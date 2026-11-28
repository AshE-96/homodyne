"""HMD-S02 · offline self-test: keys unset, temp folder, MOCK players only. Stockfish parts run only if installed.

    python3 chess_live.py --selftest        (or chess_run.py --selftest)
"""
import json
import os
import tempfile
import time
import urllib.request
from pathlib import Path

import chess_core as cc
from chess_core import chess

KEYS = ('ANTHROPIC_API_KEY', 'GEMINI_API_KEY', 'OPENAI_API_KEY', 'OPENROUTER_API_KEY')


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def core():
    b = chess.Board('4k3/8/8/8/8/8/4r3/4K2R w K - 0 1')          # White king in check from the rook on e2
    want = {'{"move": "Kd1"}': None, '{"move":"O-O"}': 'castling_illegal', 'Qd4': 'ghost_piece',
            'Rh8+': 'leaves_king_in_check', '12. Kf2': 'leaves_king_in_check', 'e9': 'bad_notation',
            '{"move": "h1h8"}': 'leaves_king_in_check', 'e1g1': 'castling_illegal', '': 'no_answer',
            '{"move": "a2a4"}': 'ghost_piece', 'Kxe2': None, 'Rh3': 'leaves_king_in_check'}
    for text, kind in want.items():
        mv, info = cc.judge(b, text)
        check((mv is not None) == (kind is None) and info.get('kind') == kind, f'judge({text!r}) → {info}')
    b = chess.Board('k7/8/8/8/8/8/1N3N2/K7 w - - 0 1')
    check(cc.judge(b, 'Nd3')[1]['kind'] == 'ambiguous' and cc.judge(b, 'Nbd3')[0], 'ambiguous SAN')
    b = chess.Board('k7/8/8/8/8/8/8/K6R w - - 0 1')
    check(cc.judge(b, 'Rh9')[1]['kind'] == 'bad_notation' and cc.judge(b, 'Ra2')[1]['kind'] == 'unreachable'
          and cc.judge(b, 'Rxh8+!')[0] is not None and cc.judge(b, 'Rh8+!')[0] is not None
          and cc.judge(b, 'h1h5')[0] is not None, 'unreachable / UCI')
    b = chess.Board()
    for m in 'e4 e5 Nf3 Nc6 Bb5'.split():
        b.push_san(m)
    check(cc.book_info(b) == (True, ('C60', 'Ruy Lopez')), f'book {cc.book_info(b)}')
    for m in 'a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O h3 Na5 Bc2 c5 d4 Qc7 Kh2 Kh8'.split():
        b.push_san(m)
    check(not cc.book_info(b)[0], 'a deep sideline is out of book')
    check(round(cc.win_pct(100), 1) == 59.1 and round(cc.win_pct(18), 1) == 51.7, 'Lichess win%')
    check(round(cc.win_pct(5000), 2) == round(cc.win_pct(1000), 2), 'eval ceiling ±1000')
    check(cc.accuracy(50, 80) == 100.0 and round(cc.accuracy(0, -100), 1) == 67.2, 'Lichess accuracy')
    check(cc.judgement(0, -300) == 'blunder' and cc.judgement(0, -20) is None and cc.judgement(0, -60) == 'inaccuracy' and cc.judgement(0, -150) == 'mistake',
          'judgement thresholds')
    check(round(cc.expected_score(1700, 1500), 2) == 0.76, 'Elo expected score')
    p = cc.prompt_for(chess.Board(), [], 'G01')
    check('Position (FEN): rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' in p and 'You play White' in p, p)
    b = chess.Board()
    b.push_san('e4')
    p = cc.prompt_for(b, ['e4'], 'G01', retry_text='Qh5')
    check('Moves so far: 1. e4' in p and 'last chance' in p and 'You play Black' in p, p)
    r = json.loads(cc.mock_reply('gemini', p, 'G01'))
    check(r == json.loads(cc.mock_reply('gemini', p, 'G01')), 'mock is deterministic')


def engine():
    e, note = cc.open_engine(10)
    if not e:
        print('  skip engine checks: ' + note)
        return False
    try:
        cp, mate = e.eval(chess.Board())
        check(-80 < cp < 120 and mate is None, f'start position eval {cp}')
        cp, mate = e.eval(chess.Board('6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1'))
        check(mate == 1 and cp == cc.CP_CEIL, f'mate in 1 → {cp}, {mate}')
    finally:
        e.close()
    print('  engine ok: ' + note)
    return True


def tournament(tmp):
    import chess_run
    cc.DATA, cc.RESULTS = tmp / 'data', tmp / 'results'
    sl = [{'slot': s, 'label': s, 'model': 'mock:' + s, 'no_schema': False}
          for s in ('gemini', 'claude', 'gpt', 'open1', 'open2')]
    games = chess_run.schedule(sl)
    check(len(games) == 20, 'round-robin size')
    for s in sl:
        w = sum(g['white'] == s['slot'] for g in games)
        bl = sum(g['black'] == s['slot'] for g in games)
        check(w == 4 and bl == 4, f'colours balanced for {s["slot"]}: {w}/{bl}')
    check(len({frozenset((g['white'], g['black'])) for g in games}) == 10, 'every pair meets')
    t = time.monotonic()
    assert chess_run.main(['run', '--mock', '--run', 'mock-x', '--max-plies', '40', '--delay', '0', '--parallel',
                           '4', '--no-engine']) == 0
    check(time.monotonic() - t < 60, 'mock tournament is fast')
    assert chess_run.main(['report', '--run', 'mock-x']) == 0
    res = cc.RESULTS / 'mock-x'
    summ = json.loads((res / 'summary.json').read_text(encoding='utf-8'))
    check(sum(v['points'] for v in summ['models'].values()) == 20, 'points add up to the number of games')
    check('MOCK' in (res / 'report.md').read_text(encoding='utf-8'), 'report labelled MOCK')
    check((res / 'spoken-fa.txt').read_text(encoding='utf-8').startswith('[MOCK]'), 'spoken lines labelled MOCK')
    check((res / 'games.pgn').read_text(encoding='utf-8').count('[Event ') == 20, 'PGN has 20 games')
    assert chess_run.main(['run', '--mock', '--run', 'mock-x', '--max-plies', '40', '--delay', '0', '--no-engine']) == 0
    lines = (cc.DATA / 'runs/mock-x/games.jsonl').read_text(encoding='utf-8').splitlines()
    check(len(lines) == 20, f'resume skipped finished games ({len(lines)} records)')
    # retry rule: a player that is always illegal forfeits on its first decision, after exactly two replies
    sl2 = [{'slot': 'gpt', 'label': 'gpt', 'model': 'mock:gpt', 'no_schema': False},
           {'slot': 'always_illegal', 'label': 'bad', 'model': 'mock:always_illegal', 'no_schema': False}]
    evs = []
    chess_run.run_tournament(sl2, chess_run.schedule(sl2), cc.DATA / 'runs/forfeit', on_event=evs.append,
                             max_plies=20, want_engine=False)
    ends = [e for e in evs if e['type'] == 'game_end']
    check(len(ends) == 2 and all(e['reason'] == 'forfeit: two illegal moves' for e in ends), ends)
    check(sorted(e['result'] for e in ends) == ['0-1', '1-0'] and
          sorted(e['plies'] for e in ends) == [0, 1], f'forfeit results and ply count {ends}')
    bad = [e for e in evs if e['type'] == 'illegal' and e['slot'] == 'always_illegal']
    check(len(bad) == 4 and {e['attempt'] for e in bad} == {1, 2}, 'one retry, then forfeit')
    # cost cap: a tiny cap stops the run and marks games aborted
    evs = []
    chess_run.run_tournament(sl[:2], chess_run.schedule(sl[:2]), cc.DATA / 'runs/cap', on_event=evs.append,
                             max_plies=40, cap=0.01, parallel=1, want_engine=False)
    check(any(e['type'] == 'game_end' and 'cost cap' in (e['reason'] or '') for e in evs), 'cost cap stops calls')
    return res / 'events.jsonl'


def live(events_path):
    import chess_live
    hub = chess_live.Hub()
    chess_live.replay(events_path, chess_live.Board(hub, 'replay', 1e6), 1e6)
    kinds = [e['type'] for e in hub.history]
    check(kinds[0] == 'start' and kinds[-1] == 'end' and kinds.count('game_end') >= 20, kinds[-5:])
    check(hub.history[0]['mode'] == 'mock', 'a replayed MOCK run stays MOCK')
    check(all(e['usd'] is None for e in hub.history if e['type'] == 'reply'), 'MOCK never shows exact $')
    chess_live.HUB = hub
    srv = chess_live.serve(0)
    port = srv.server_address[1]
    try:
        html = urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=5).read().decode()
        check('dir="rtl"' in html and 'MOCK' in html and 'EventSource' in html and 'Vazirmatn' in html, 'page')
        st = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{port}/state', timeout=5).read())
        check(len(st) == len(hub.history), '/state')
        r = urllib.request.urlopen(f'http://127.0.0.1:{port}/events', timeout=5)
        first = [r.readline() for _ in range(4)]
        check(any(b'"type": "start"' in x for x in first), first)
        r.close()
    finally:
        srv.shutdown()


def run():
    saved = {k: os.environ.pop(k) for k in KEYS if k in os.environ}
    data, results = cc.DATA, cc.RESULTS
    try:
        core()
        print('  core ok: parsing, 7 illegal kinds, opening book, Lichess win%/accuracy/judgement, Elo, prompt')
        eng = engine()
        with tempfile.TemporaryDirectory() as tmp:
            ev = tournament(Path(tmp))
            print('  tournament ok: 20 games, colours balanced, report/PGN/spoken MOCK-labelled, resume, '
                  'retry→forfeit, cost cap')
            live(ev)
            print('  live ok: replay, MOCK label kept, no invented $, page, /state, SSE')
    finally:
        cc.DATA, cc.RESULTS = data, results
        os.environ.update(saved)
    print('selftest ok' + ('' if eng else ' (Stockfish not installed: engine checks skipped)'))
    return 0
