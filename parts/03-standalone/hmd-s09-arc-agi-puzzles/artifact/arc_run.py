#!/usr/bin/env python3
"""HMD-S09 · arc_run.py — five models try the episode's five ARC puzzles under one locked protocol.

    python3 arc_run.py plan                      # calls, input size, $ UPPER BOUND per model; no network, no key
    python3 arc_run.py run                       # paid: plan, cost cap check, then [y/N]
    python3 arc_run.py run --max-usd 10          # refuse/stop when the running cost bound passes $10 (default 25)
    python3 arc_run.py run --mock                # no key, no network: mock models (rehearsal; labelled MOCK everywhere)
    python3 arc_run.py report [--run NAME]       # per-model table → results/<run>/summary.json (+ spoken lines)

Protocol (protocol.md): one call per test input (7 calls per model: puzzles 1-4 have one test input, puzzle 5 has
three); the same English prompt for every model (arc_core.PROMPT_HEAD + demonstrations + test input as text grids);
two attempts in one JSON reply, like ARC Prize's pass@2; exact match only; a puzzle counts only if every one of its
test inputs is solved. Provider default sampling; Claude effort medium (tools/llm.py default). All five models start
at the same instant (a barrier), each in puzzle order. Raw replies and events go to runs/<run>/ (git-ignored).
"""
import argparse
import hashlib
import json
import os
import random
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3] / 'tools'))
import arc_core as core  # noqa: E402
import llm  # noqa: E402

MODELS_FILE, PRICES_FILE = HERE / 'models.json', HERE / 'prices.json'
RUNS, RESULTS = HERE / 'runs', HERE / 'results'
REGISTERED = ('arc_core.py', 'arc_run.py', 'protocol.md', 'models.json')
os.environ.setdefault('HOMODYNE_HTTP_TIMEOUT', '900')   # long reasoning replies
GRID = {'type': 'array', 'items': {'type': 'array', 'items': {'type': 'integer'}}}
SCHEMA = {'type': 'object', 'properties': {'attempt_1': GRID, 'attempt_2': GRID},
          'required': ['attempt_1', 'attempt_2'], 'additionalProperties': False}
# mock only: chance of an exact answer on puzzles 1..5, and seconds per call. Invented for rehearsal, never shown as data.
MOCK_STYLE = {'gemini': ((.95, .9, .9, .8, .5), 14), 'claude': ((.95, .9, .9, .85, .55), 16),
              'gpt': ((.95, .95, .9, .8, .6), 19), 'open1': ((.8, .6, .5, .4, .1), 8),
              'open2': ((.85, .5, .6, .3, .1), 9)}


# ── setup ──────────────────────────────────────────────────────────────────────────────────────
def slots(args):
    cfg = json.loads(MODELS_FILE.read_text(encoding='utf-8'))['slots']
    over = dict(m.split('=', 1) for m in (args.model or []))
    out = [{'slot': s['slot'], 'label': s['label'], 'no_schema': bool(s.get('no_schema')),
            'model': 'mock:' + s['slot'] if args.mock else over.get(s['slot'], s.get('model'))} for s in cfg]
    missing = [s['slot'] for s in out if not s['model']]
    if missing:
        sys.exit(f'no model ID for slot(s) {missing}: fill models.json or pass --model SLOT=provider:model '
                 '(protocol.md §1: the current flagship of each provider on run day, written down with the date)')
    return out


def fingerprints():
    out = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in REGISTERED}
    try:
        r = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=HERE, capture_output=True, text=True, timeout=10)
        out['commit'] = r.stdout.strip() or 'not a git checkout'
    except (OSError, subprocess.SubprocessError):
        out['commit'] = 'unknown'
    return out


def prices():
    return json.loads(PRICES_FILE.read_text(encoding='utf-8'))


def bound_usd(model, tin, tout, pr):
    """(usd, kind): real price if prices.json has it, else the fallback UPPER BOUND; mock/ollama cost nothing."""
    provider = model.split(':', 1)[0]
    if provider in ('mock', 'ollama'):
        return 0.0, 'free'
    p = pr.get('models', {}).get(model, {})
    if p.get('input_per_mtok') is not None and p.get('output_per_mtok') is not None:
        return (tin * p['input_per_mtok'] + tout * p['output_per_mtok']) / 1e6, 'price'
    fb = pr['fallback'].get(provider) or pr['fallback']['default']
    return (tin * fb['input_per_mtok'] + tout * fb['output_per_mtok']) / 1e6, 'UPPER BOUND'


def plan(sl, pr=None):
    pr = pr or prices()
    items = core.test_items()
    chars = sum(len(core.prompt_for(core.load_task(t), i)) for _, t, i in items)
    tin = int(chars / 1.5)                       # deliberately high: a digit grid is roughly one token per cell
    lines = [f'{len(items)} test inputs (5 puzzles) × {len(sl)} models = {len(items) * len(sl)} calls · '
             f'{chars:,} prompt characters per model · ≤ ~{tin:,} input tokens per model (rough, high)']
    total = 0.0
    for s in sl:
        usd, kind = bound_usd(s['model'], tin, len(items) * core.MAX_TOKENS, pr)
        total += usd
        lines.append(f'  {s["slot"]:6} {s["model"]}: ' + ('no API cost' if kind == 'free' else
                     f'≤ ${usd:,.2f} ({kind}; every call at its {core.MAX_TOKENS}-token output cap'
                     + (', CONSERVATIVE UPPER BOUND, NOT AN OFFICIAL PRICE' if kind == 'UPPER BOUND' else '') + ')'))
    lines.append(f'TOTAL ≤ ${total:,.2f}' + (' (includes UPPER BOUNDS, not official prices)'
                                            if any(bound_usd(s['model'], 1, 1, pr)[1] == 'UPPER BOUND' for s in sl) else ''))
    return lines, total


# ── one call ─────────────────────────────────────────────────────────────────────────────────
def mock_text(slot, n, task, ti):
    p_right, _ = MOCK_STYLE.get(slot, ((.5,) * 5, 10))
    truth = task['test'][ti]['output']
    r = random.Random(f'{slot}|{n}|{ti}').random()
    wrong = [row[:] for row in truth]
    wrong[0][0] = (wrong[0][0] + 1) % 10
    if r < p_right[n - 1] * 0.8:
        return json.dumps({'attempt_1': truth, 'attempt_2': wrong})
    if r < p_right[n - 1]:
        return json.dumps({'attempt_1': wrong, 'attempt_2': truth})
    return json.dumps({'attempt_1': task['test'][ti]['input'], 'attempt_2': wrong})


def answer_one(s, n, tid, ti, out, delay=0.0):
    task = core.load_task(tid)
    prompt = core.prompt_for(task, ti)
    mock = s['model'].startswith('mock:')
    t0 = time.monotonic()
    res = llm.call(prompt, model=s['model'], max_tokens=core.MAX_TOKENS, cache_dir=out / 'cache' / s['slot'],
                   schema=None if s.get('no_schema') else SCHEMA, mock=lambda p, schema=None: mock_text(s['slot'], n, task, ti))
    grids, flag = core.parse_reply(res.text)
    ex = res.extra or {}
    row = {'n': n, 'task': tid, 'test_index': ti, 'slot': s['slot'], 'model': s['model'],
           'model_served': res.model_served, 'attempts': grids, 'flag': flag,
           'correct': core.solved(grids, task['test'][ti]['output']),
           'latency_s': round(res.latency_s, 3), 'input_tokens': res.input_tokens, 'output_tokens': res.output_tokens,
           'reasoning_tokens': ex.get('reasoning_tokens', ex.get('thoughts_tokens')), 'usd_reported': ex.get('cost_usd'),
           'stop_reason': res.stop_reason, 'fell_back': res.fell_back, 'cached': res.cached, 'mock': mock,
           'prompt_chars': len(prompt), 'reply': (res.text or '')[:2000]}
    if mock:
        _, sec = MOCK_STYLE.get(s['slot'], (None, 10))
        lat = sec * random.Random(f'lat|{s["slot"]}|{n}|{ti}').lognormvariate(0, 0.4)
        row.update(latency_s=round(lat, 2), input_tokens=len(prompt) // 2, output_tokens=int(lat * 120))
        if delay:
            time.sleep(max(0.0, lat * delay - (time.monotonic() - t0)))
    return row


def row_usd(r, pr):
    if r.get('usd_reported') is not None:
        return r['usd_reported'], 'reported'
    return bound_usd(r['model'], r['input_tokens'], r['output_tokens'], pr)


# ── the engine (also used by arc_live.py for the on-camera mock run) ──────────────────────────────
def run_all(sl, out, on_event=None, cap_usd=25.0, delay=0.0, pr=None):
    pr = pr or prices()
    out.mkdir(parents=True, exist_ok=True)
    items = core.test_items()
    lock, barrier, stop = threading.Lock(), threading.Barrier(len(sl)), threading.Event()
    t0 = time.monotonic()

    def emit(ev):
        with lock:
            ev['t'] = round(time.monotonic() - t0, 3)
            with (out / 'events.jsonl').open('a', encoding='utf-8') as f:
                f.write(json.dumps(ev, ensure_ascii=False) + '\n')
        if on_event:
            on_event(ev)

    emit({'type': 'start', 'wall': time.strftime('%Y-%m-%d %H:%M:%S'), 'cap_usd': cap_usd,
          'slots': [{k: s[k] for k in ('slot', 'label', 'model')} for s in sl],
          'items': [{'n': n, 'task': t, 'test_index': i} for n, t, i in items],
          'mock': all(s['model'].startswith('mock:') for s in sl)})
    done_path = out / 'rows.jsonl'
    done = {}
    if done_path.exists():
        for ln in done_path.read_text(encoding='utf-8').splitlines():
            r = json.loads(ln)
            done[(r['slot'], r['task'], r['test_index'])] = r
    spent = [sum(row_usd(r, pr)[0] for r in done.values())]   # a resumed run keeps counting what it already spent
    if spent[0] >= cap_usd:
        stop.set()

    def worker(s):
        barrier.wait()
        for n, tid, ti in items:
            if (s['slot'], tid, ti) in done:
                emit({'type': 'answer', 'resumed': True, **{k: v for k, v in done[(s['slot'], tid, ti)].items()
                                                           if k not in ('reply', 'attempts')}})
                continue
            if stop.is_set():
                emit({'type': 'capped', 'slot': s['slot'], 'n': n, 'task': tid, 'test_index': ti})
                continue
            emit({'type': 'ask', 'slot': s['slot'], 'n': n, 'task': tid, 'test_index': ti})
            try:
                r = answer_one(s, n, tid, ti, out, delay)
            except Exception as e:                 # never let one slot's thread die silently
                emit({'type': 'error', 'slot': s['slot'], 'n': n, 'task': tid, 'test_index': ti, 'error': str(e)[:300]})
                continue
            with lock:
                with done_path.open('a', encoding='utf-8') as f:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')
                spent[0] += row_usd(r, pr)[0]
                if spent[0] >= cap_usd:
                    stop.set()
            emit({'type': 'answer', **{k: v for k, v in r.items() if k not in ('reply', 'attempts')},
                  'spent_bound_usd': round(spent[0], 4)})
        emit({'type': 'done', 'slot': s['slot']})

    threads = [threading.Thread(target=worker, args=(s,), daemon=True) for s in sl]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    emit({'type': 'end', 'spent_bound_usd': round(spent[0], 4), 'capped': stop.is_set()})
    return spent[0], stop.is_set()


def run_name(sl, mock):
    if mock:
        return 'mock'
    return 'run-' + hashlib.sha256('|'.join(s['model'] for s in sl).encode()).hexdigest()[:8]


def cmd_run(args):
    sl = slots(args)
    lines, total = plan(sl)
    out = RUNS / (args.run or run_name(sl, args.mock))
    print('\n'.join(lines) + f'\ncost cap --max-usd {args.max_usd} · → {out}')
    if not args.mock:
        if total > args.max_usd:
            print(f'the bound (${total:,.2f}) is above the cap: the run stops once spending passes ${args.max_usd}; '
                  'puzzles not reached are marked "capped". Raise --max-usd to allow more.')
        if not args.yes and input('This spends API money. Continue? [y/N] ').strip().lower() != 'y':
            print('stopped')
            return 1
    if args.mock and out.exists():               # a rehearsal starts clean; a paid run resumes
        import shutil
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {'slots': sl, 'started': time.strftime('%Y-%m-%d %H:%M'), 'fingerprints': fingerprints(),
            'prompt_head': core.PROMPT_HEAD, 'schema': SCHEMA, 'max_tokens': core.MAX_TOKENS, 'cap_usd': args.max_usd,
            'effort': os.environ.get('HOMODYNE_EFFORT', 'medium'), 'mock': args.mock}
    (out / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    spent, capped = run_all(sl, out, cap_usd=args.max_usd, delay=args.delay,
                            on_event=lambda e: e['type'] == 'done' and print(f'  {e["slot"]} finished at {e["t"]:.0f} s'))
    print(f'cost bound spent ≈ ${spent:,.2f}' + (' · CAPPED' if capped else ''))
    print(f'next: python3 {Path(__file__).name} report --run {out.name}')
    return 0


# ── report ───────────────────────────────────────────────────────────────────────────────────────
def summarize(out, pr=None):
    pr = pr or prices()
    meta = json.loads((out / 'meta.json').read_text(encoding='utf-8'))
    rows = [json.loads(ln) for ln in (out / 'rows.jsonl').read_text(encoding='utf-8').splitlines() if ln.strip()]
    items = core.test_items()
    rep = {'run': out.name, 'started': meta['started'], 'mock': meta['mock'], 'prices_checked_on': pr.get('checked_on'),
           'protocol': 'pass@2 in one reply, exact match, one call per test input', 'models': []}
    for s in meta['slots']:
        mine = {(r['task'], r['test_index']): r for r in rows if r['slot'] == s['slot']}
        per = {}
        for n, tid, ti in items:
            r = mine.get((tid, ti))
            per.setdefault(n, []).append(None if r is None else r['correct'])
        costs = [row_usd(r, pr) for r in mine.values()]
        lat = [r['latency_s'] for r in mine.values() if not r.get('cached')] or [r['latency_s'] for r in mine.values()]
        rep['models'].append({
            'slot': s['slot'], 'label': s['label'], 'model': s['model'],
            'served': sorted({r['model_served'] for r in mine.values()}),
            'puzzles': {str(n): (None if None in v else all(v)) for n, v in per.items()},
            'puzzles_solved': sum(1 for v in per.values() if None not in v and all(v)),
            'tests_solved': sum(bool(r['correct']) for r in mine.values()), 'tests_answered': len(mine),
            'latency_total_s': round(sum(r['latency_s'] for r in mine.values()), 1),
            'latency_median_s': round(statistics.median(lat), 1) if lat else None,
            'input_tokens': sum(r['input_tokens'] for r in mine.values()),
            'output_tokens': sum(r['output_tokens'] for r in mine.values()),
            'usd': None if any(k == 'UPPER BOUND' for _, k in costs) else round(sum(u for u, _ in costs), 4),
            'usd_upper_bound': round(sum(u for u, _ in costs), 4),
            'unparsed': sum(r['flag'] == 'unparsed' for r in mine.values()),
            'truncated': sum(str(r.get('stop_reason')).lower() in ('max_tokens', 'length') for r in mine.values()),
            'fell_back': sum(bool(r.get('fell_back')) for r in mine.values())})
    return rep


def cmd_report(args):
    runs = sorted(RUNS.glob('*/meta.json'), key=lambda p: p.stat().st_mtime)
    out = RUNS / args.run if args.run else (runs[-1].parent if runs else None)
    if not out or not (out / 'rows.jsonl').exists():
        sys.exit('no run yet: python3 arc_run.py run [--mock]')
    rep = summarize(out)
    dest = RESULTS / out.name
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'summary.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    tag = 'MOCK (invented numbers, rehearsal only) · ' if rep['mock'] else ''
    print(f'{tag}run {rep["run"]} · started {rep["started"]} · {rep["protocol"]}')
    for m in rep['models']:
        usd = f'${m["usd"]:.2f}' if m['usd'] is not None else f'≤ ${m["usd_upper_bound"]:.2f} (bound; fill prices.json)'
        marks = ' '.join(f'{n}:{"✓" if v else ("–" if v is None else "✗")}' for n, v in m['puzzles'].items())
        print(f'  {m["label"]:13} {m["puzzles_solved"]}/5 puzzles · {marks} · {m["latency_total_s"]:.0f} s · '
              f'{m["input_tokens"] + m["output_tokens"]:,} tokens · {usd}')
    print(f'→ {dest / "summary.json"} (arc_live.py shows the newest summary)')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('cmd', choices=['plan', 'run', 'report'])
    ap.add_argument('--model', action='append', help='SLOT=provider:model (repeatable)')
    ap.add_argument('--mock', action='store_true')
    ap.add_argument('--yes', action='store_true', help='skip the [y/N] question (paid run)')
    ap.add_argument('--max-usd', type=float, default=25.0)
    ap.add_argument('--delay', type=float, default=0.0, help='mock only: sleep this × the mock latency')
    ap.add_argument('--run')
    args = ap.parse_args(argv)
    if args.cmd == 'plan':
        print('\n'.join(plan(slots(args))[0]))
        return 0
    return cmd_run(args) if args.cmd == 'run' else cmd_report(args)


if __name__ == '__main__':
    sys.exit(main())
