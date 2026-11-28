#!/usr/bin/env python3
"""HMD-S02 · chess_run.py — a round-robin among five models, every move checked, every illegal move diagnosed.

    python3 chess_run.py plan                              # games, calls, tokens, $ UPPER BOUND; no network
    python3 chess_run.py run --pilot --max-usd 3           # paid pilot (2 games, 20 plies): plan, then [y/N]
    python3 chess_run.py run --max-usd 40                  # full round-robin (resumable: run again after a crash)
    python3 chess_run.py run --mock                        # no key, no network: MOCK players
    python3 chess_run.py report [--run NAME]               # tables, PGN, events for replay → results/NAME/
    python3 chess_run.py --selftest                        # keys unset, temp folder, no Stockfish needed

Protocol: protocol.md (locked). Prompt, parsing and metrics: chess_core.py. Model calls: tools/llm.py.
Raw run data (events, per-game answer caches) go to artifact/data/runs/NAME/ (git-ignored); `report` writes
aggregates, a PGN and a copy of the events (moves only, no keys) to artifact/results/NAME/.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import chess_core as cc
from chess_core import chess
import llm

MODELS_FILE = cc.HERE / 'models.json'
PRICES_FILE = cc.HERE / 'prices.json'
REGISTERED = ('chess_core.py', 'chess_run.py', 'protocol.md', 'models.json')
os.environ.setdefault('HOMODYNE_HTTP_TIMEOUT', '900')


class CapReached(Exception):
    pass


# ── setup ────────────────────────────────────────────────────────────────────────────────────────
def slots(args):
    cfg = json.loads(MODELS_FILE.read_text(encoding='utf-8'))['slots']
    over = dict(m.split('=', 1) for m in (args.model or []))
    out = [{'slot': s['slot'], 'label': s['label'], 'model': ('mock:' + s['slot']) if args.mock
            else over.get(s['slot'], s.get('model')), 'no_schema': bool(s.get('no_schema'))} for s in cfg]
    if getattr(args, 'extra_mock', None):
        out += [{'slot': x, 'label': x, 'model': 'mock:' + x, 'no_schema': False} for x in args.extra_mock]
    missing = [s['slot'] for s in out if not s['model']]
    if missing:
        sys.exit(f'no model ID for slot(s) {missing}: fill models.json or pass --model SLOT=provider:model '
                 f'(protocol.md §1)')
    return out


def schedule(sl, pilot=False):
    """Circle-method rounds; every pair plays twice, once with each colour (protocol.md §4)."""
    names = [s['slot'] for s in sl] + ([None] if len(sl) % 2 else [])
    n, rounds = len(names), []
    arr = names[:]
    for _ in range(n - 1):
        rounds.append([(arr[i], arr[n - 1 - i]) for i in range(n // 2)])
        arr = [arr[0]] + [arr[-1]] + arr[1:-1]
    legs = [[(a, b) for a, b in r if a and b] for r in rounds]
    pairs = [p for r in legs for p in r] + [(b, a) for r in legs for (a, b) in r]
    games = [{'gid': f'G{i + 1:02d}', 'white': w, 'black': b} for i, (w, b) in enumerate(pairs)]
    return games[:2] if pilot else games


def run_dir(args, sl):
    name = args.run or ('mock-' + time.strftime('%Y%m%d-%H%M%S') if args.mock else hashlib.sha256(
        '|'.join(s['model'] for s in sl).encode()).hexdigest()[:8])
    return cc.DATA / 'runs' / name


def fingerprints():
    out = {n: hashlib.sha256((cc.HERE / n).read_bytes()).hexdigest()[:16] for n in REGISTERED}
    try:
        r = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=cc.HERE, capture_output=True, text=True, timeout=10)
        out['commit'] = r.stdout.strip() or 'unknown'
    except (OSError, subprocess.SubprocessError):
        out['commit'] = 'unknown'
    return out


def prices():
    return json.loads(PRICES_FILE.read_text(encoding='utf-8'))


def usd(model, tin, tout, extra, pr):
    """(dollars, exact?) for one call: OpenRouter's reported cost, else prices.json, else the fallback bound."""
    if extra and extra.get('cost_usd') is not None:
        return float(extra['cost_usd']), True
    p = pr['models'].get(model)
    if p and p.get('input_per_mtok') is not None:
        return (tin * p['input_per_mtok'] + tout * p['output_per_mtok']) / 1e6, True
    fb = pr['fallback'].get(model.split(':')[0], pr['fallback']['default'])
    return (tin * fb['input_per_mtok'] + tout * fb['output_per_mtok']) / 1e6, False


def plan_lines(sl, games, max_plies, cap):
    pr = prices()
    per = {s['slot']: sum(g['white'] == s['slot'] or g['black'] == s['slot'] for g in games) for s in sl}
    lines = [f'{len(games)} games · {len(sl)} models · ≤ {max_plies} plies per game · one retry per illegal move',
             f'cost cap (--max-usd): {cap if cap is not None else "NOT SET (required for a paid run)"} USD total; '
             f'new calls stop once the running total (exact $ or the fallback bound) reaches it']
    tin = int((len(cc.SYSTEM) + 420 + 7 * max_plies / 2) / 3.2)       # FEN + history; ~3.2 chars/token
    tot_typ = tot_top = 0.0
    for s in sl:
        calls = int(per[s['slot']] * max_plies / 2 * 1.2)            # +20% for retries
        typ, _ = usd(s['model'], calls * tin, calls * 3000, None, pr)
        top, exact = usd(s['model'], calls * tin, calls * cc.MAX_TOKENS, None, pr)
        lines.append(f'  {s["slot"]:7} {s["model"]:42} {per[s["slot"]]} games · ≤ {calls} calls · ~{tin} in-tokens/call'
                     f' · typical ${typ:,.2f} (3000 out/call) · worst ${top:,.2f} ({cc.MAX_TOKENS} out/call)'
                     + ('' if exact else ' · FALLBACK BOUND, prices.json empty'))
        tot_typ, tot_top = tot_typ + typ, tot_top + top
    lines.append(f'  TOTAL   typical ${tot_typ:,.2f} · worst ${tot_top:,.2f} (all {len(sl)} models; the cap is for this '
                 f'total, counted over every session of the run)')
    return lines


# ── one game ─────────────────────────────────────────────────────────────────────────────────────
class Spend:
    def __init__(self, cap, already=0.0, bound=False):
        self.cap, self.total, self.bound, self.lock = cap, already, bound, threading.Lock()

    def check(self):
        if self.cap is not None and self.total >= self.cap:
            raise CapReached(f'cost cap {self.cap} USD reached')

    def add(self, d, exact):
        with self.lock:
            self.total += d
            self.bound |= not exact


def ask(slot, game, board, sans, retry_text, cache, emit, spend, use_schema, delay):
    spec = slot['model']
    prompt = cc.prompt_for(board, sans, game['gid'], retry_text)
    ply, attempt = len(sans) + 1, 1 if retry_text is None else 2
    emit({'type': 'ask', 'gid': game['gid'], 'slot': slot['slot'], 'ply': ply, 'attempt': attempt, 'prompt': prompt})
    spend.check()
    err = None
    for tries in range(3):
        try:
            res = llm.call(prompt, system=cc.SYSTEM, model=spec, cache_dir=cache, max_tokens=cc.MAX_TOKENS,
                           schema=None if (slot['no_schema'] or not use_schema) else cc.SCHEMA,
                           mock=lambda p, schema=None: cc.mock_reply(slot['slot'], p, game['gid']))
            break
        except Exception as e:      # API failure after llm.py's own retries: not the model's fault
            err = f'{type(e).__name__}: {str(e)[:200]}'
            emit({'type': 'error', 'gid': game['gid'], 'slot': slot['slot'], 'error': err})
            time.sleep(0 if spec.startswith('mock:') else 10 * (tries + 1))
    else:
        raise RuntimeError(err)
    lat, tin, tout = res.latency_s, res.input_tokens, res.output_tokens
    if res.provider == 'mock':
        lat, tin, tout = cc.mock_cost(slot['slot'], prompt)
        time.sleep(lat * delay)
    d, exact = usd(spec, tin, tout, res.extra, prices())
    if not res.cached:
        spend.add(d, exact)
    ev = {'type': 'reply', 'gid': game['gid'], 'slot': slot['slot'], 'ply': ply, 'attempt': attempt,
          'text': (res.text or '')[:300], 'latency_s': round(lat, 2), 'input_tokens': tin, 'output_tokens': tout,
          'reasoning_tokens': res.extra.get('reasoning_tokens') or res.extra.get('thoughts_tokens'),
          'usd': round(d, 5) if exact else None, 'cached': res.cached, 'served': res.model_served,
          'stop': res.stop_reason, 'spent': round(spend.total, 4), 'spent_is_bound': spend.bound}
    emit(ev)
    return res.text, ev


def play_game(game, smap, engine, emit, root, max_plies, spend, use_schema=True, delay=0.0, stop=None):
    board, sans, plies = chess.Board(), [], []
    cache = root / 'cache' / game['gid']
    emit({'type': 'game_start', **game})
    ev_now = engine.eval(board) if engine else (None, None)
    result = reason = None
    while result is None:
        if stop is not None and stop.is_set():
            result, reason = 'aborted', 'run stopped'
            break
        if len(sans) >= max_plies:
            cp = ev_now[0]
            if cp is not None and abs(cp) >= 400:
                result, reason = ('1-0' if cp > 0 else '0-1'), 'adjudicated: move cap, engine ≥ 4 pawns'
            else:
                result, reason = '1/2-1/2', 'adjudicated: move cap'
            break
        mover = smap[game['white'] if board.turn == chess.WHITE else game['black']]
        in_book_before = cc.book_info(board)[0]
        rec = {'ply': len(sans) + 1, 'slot': mover['slot'], 'attempts': [], 'in_book_before': in_book_before}
        move, retry_text = None, None
        try:
            for attempt in (1, 2):
                text, rep = ask(mover, game, board, sans, retry_text, cache, emit, spend, use_schema, delay)
                move, info = cc.judge(board, text)
                rec['attempts'].append({k: rep[k] for k in ('latency_s', 'input_tokens', 'output_tokens', 'usd',
                                                            'cached', 'reasoning_tokens', 'stop')} | info
                                       | {'text': text[:200]})
                if move:
                    break
                emit({'type': 'illegal', 'gid': game['gid'], 'slot': mover['slot'], 'ply': rec['ply'],
                      'attempt': attempt, 'proposed': info.get('proposed'), 'kind': info['kind'], 'fen': board.fen()})
                retry_text = info.get('proposed') or text[:60]
        except CapReached as e:
            result, reason = 'aborted', str(e)
            if stop is not None:
                stop.set()
            break
        except RuntimeError as e:
            result, reason = 'aborted', 'API error: ' + str(e)
            break
        if not move:
            plies.append(rec)
            result = '0-1' if board.turn == chess.WHITE else '1-0'
            reason = 'forfeit: two illegal moves'
            break
        san = board.san(move)
        white_moved = board.turn == chess.WHITE
        board.push(move)
        sans.append(san)
        in_book, opening = cc.book_info(board)
        rec.update(san=san, uci=move.uci(), in_book_after=in_book, opening=opening)
        if engine:
            before = ev_now[0]
            ev_now = engine.eval(board)
            sgn = 1 if white_moved else -1
            b, a = sgn * before, sgn * ev_now[0]
            rec.update(eval_before=before, eval_after=ev_now[0], mate=ev_now[1], cpl=max(0, b - a),
                       accuracy=round(cc.accuracy(b, a), 1), judgement=cc.judgement(b, a))
        plies.append(rec)
        emit({'type': 'move', 'gid': game['gid'], 'slot': mover['slot'], 'ply': rec['ply'], 'san': san,
              'uci': move.uci(), 'fen': board.fen(), 'in_book': in_book, 'opening': opening,
              'eval_cp': ev_now[0], 'mate': ev_now[1], 'cpl': rec.get('cpl'), 'accuracy': rec.get('accuracy'),
              'judgement': rec.get('judgement'), 'retried': len(rec['attempts']) > 1})
        out = board.outcome(claim_draw=True)
        if out:
            result, reason = out.result(), out.termination.name.lower().replace('_', ' ')
    rec = {**game, 'result': result, 'reason': reason, 'sans': sans, 'plies': plies, 'final_fen': board.fen()}
    emit({'type': 'game_end', 'gid': game['gid'], 'result': result, 'reason': reason, 'plies': len(sans)})
    return rec


# ── the tournament ───────────────────────────────────────────────────────────────────────────────
def run_tournament(sl, games, out, on_event=None, max_plies=100, cap=None, parallel=4, engine_depth=12,
                   want_engine=True, use_schema=True, delay=0.0, mode='live'):
    out.mkdir(parents=True, exist_ok=True)
    done_path = out / 'games.jsonl'
    done = {}
    if done_path.exists():
        for line in done_path.read_text(encoding='utf-8').splitlines():
            g = json.loads(line)
            # a game cut at a lower ply cap (the pilot's 20) is not finished: it is replayed from its cache and goes on
            short = g['reason'] == 'adjudicated: move cap' or g['reason'].startswith('adjudicated: move cap,')
            if g['result'] != 'aborted' and not (short and len(g['sans']) < max_plies):
                done[g['gid']] = g
            else:
                done.pop(g['gid'], None)
    session = len(list(out.glob('events-*.jsonl'))) + 1
    already, already_bound = 0.0, False      # the cap counts money spent in earlier sessions of this run too
    for f in out.glob('events-*.jsonl'):
        for line in f.read_text(encoding='utf-8').splitlines():
            e = json.loads(line)
            if e.get('spent') is not None and e['spent'] >= already:
                already, already_bound = e['spent'], already_bound or bool(e.get('spent_is_bound'))
    lock, t0 = threading.Lock(), time.monotonic()
    evf = (out / f'events-{session}.jsonl').open('a', encoding='utf-8')
    engine, engine_note = cc.open_engine(engine_depth, want_engine)

    def emit(ev):
        with lock:
            ev = {'t': round(time.monotonic() - t0, 3), **ev}
            evf.write(json.dumps(ev, ensure_ascii=False) + '\n')
            evf.flush()
            if on_event:
                on_event(ev)

    meta = {'slots': sl, 'games': games, 'max_plies': max_plies, 'cap_usd': cap, 'engine': engine_note,
            'schema': use_schema, 'effort': os.environ.get('HOMODYNE_EFFORT', 'medium'), 'mode': mode,
            'started': time.strftime('%Y-%m-%d %H:%M:%S %z'), 'fingerprints': fingerprints(), 'session': session}
    (out / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    emit({'type': 'start', 'slots': sl, 'games': games, 'max_plies': max_plies, 'cap_usd': cap, 'mode': mode,
          'engine': engine_note, 'engine_on': engine is not None, 'date': time.strftime('%Y-%m-%d'),
          'resumed': sorted(done)})
    for g in done.values():
        emit({'type': 'game_end', 'gid': g['gid'], 'result': g['result'], 'reason': g['reason'],
              'plies': len(g['sans']), 'resumed': True})
    spend, stop = Spend(cap, already, already_bound), threading.Event()
    smap = {s['slot']: s for s in sl}
    todo = [g for g in games if g['gid'] not in done]

    def one(g):
        rec = play_game(g, smap, engine, emit, out, max_plies, spend, use_schema, delay, stop)
        with lock:
            with done_path.open('a', encoding='utf-8') as f:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        return rec
    try:
        with ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
            list(ex.map(one, todo))
    finally:
        emit({'type': 'end', 'spent': round(spend.total, 4), 'spent_is_bound': spend.bound})
        evf.close()
        if engine:
            engine.close()
    return 0


# ── CLI ──────────────────────────────────────────────────────────────────────────────────────────
def parser():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', nargs='?', choices=['plan', 'run', 'report'])
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--mock', action='store_true')
    ap.add_argument('--model', action='append', help='SLOT=provider:model (overrides models.json)')
    ap.add_argument('--extra-mock', action='append', help=argparse.SUPPRESS)
    ap.add_argument('--pilot', action='store_true', help='2 games, 20 plies')
    ap.add_argument('--max-plies', type=int, default=80)
    ap.add_argument('--max-usd', type=float)
    ap.add_argument('--parallel', type=int, default=4)
    ap.add_argument('--engine-depth', type=int, default=12)
    ap.add_argument('--no-engine', action='store_true')
    ap.add_argument('--no-schema', action='store_true', help='debug only (protocol.md §3)')
    ap.add_argument('--delay', type=float, default=0.02, help='mock: wall seconds per simulated second')
    ap.add_argument('--run')
    ap.add_argument('--yes', action='store_true')
    return ap


def paid_guard(args):
    """Checks before any paid run (protocol.md §4)."""
    if args.max_usd is None:
        sys.exit('a paid run needs --max-usd (protocol.md §4)')
    if not args.pilot and not args.no_engine and cc.find_stockfish() is None:
        sys.exit('the full paid run needs Stockfish: without it a game that hits the move cap is always a draw '
                 '(brew install stockfish; prep-fa.md §2). Override only with --no-engine.')


def prepare(args):
    sl = slots(args)
    games = schedule(sl, args.pilot)
    plies = 20 if args.pilot else args.max_plies
    return sl, games, plies


def main(argv=None):
    args = parser().parse_args(argv)
    if args.selftest:
        import chess_selftest
        return chess_selftest.run()
    if args.cmd == 'report':
        import chess_report
        return chess_report.report(args)
    if args.cmd not in ('plan', 'run'):
        parser().print_help()
        return 0
    sl, games, plies = prepare(args)
    print('\n'.join(plan_lines(sl, games, plies, args.max_usd)))
    if args.cmd == 'plan':
        return 0
    if not args.mock:
        paid_guard(args)
        if not args.yes and input('This spends API money. Continue? [y/N] ').strip().lower() != 'y':
            return 1
    out = run_dir(args, sl)
    rc = run_tournament(sl, games, out, max_plies=plies, cap=args.max_usd, parallel=args.parallel,
                        engine_depth=args.engine_depth, want_engine=not args.no_engine,
                        use_schema=not args.no_schema, delay=args.delay, mode='mock' if args.mock else 'live')
    print(f'run finished · {out}\nnext: python3 chess_run.py report --run {out.name}')
    return rc


if __name__ == '__main__':
    sys.exit(main())
