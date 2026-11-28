#!/usr/bin/env python3
"""HMD-S09 · arc_live.py — the live page: play five ARC puzzles with a timer, see the grid as the model gets it,
then see how five models did. Standard library only.

    python3 -I arc_live.py                     # build arc_live.html (works opened from disk, no server)
    python3 -I arc_live.py --serve             # build + serve http://127.0.0.1:8770/  (R R in the page = mock run, live)
    python3 -I arc_live.py --serve --replay run-ab12cd34   # replay a real run's events into the page, labelled REPLAY
    python3 -I arc_live.py --selftest          # offline, keys unset, < 20 s

Page keys: ⇧1-5 or ← → puzzle · 0-9 colour · P paint · F fill · C copy input · X clear · Enter submit (2 tries) ·
A show answer · T restart timer · N next test input · M / R / L side panels · H clean frame for recording.
URL: arc_live.html?p=2&panel=model&clean=1
Server-sent events: the same Hub pattern as HMD-K01 konkur_live.py (ThreadingHTTPServer + EventSource).
"""
import argparse
import base64
import hashlib
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arc_core as core  # noqa: E402
import arc_run  # noqa: E402
import solve_fractal  # noqa: E402

TEMPLATE, PAGE = HERE / 'arc_page.html', HERE / 'arc_live.html'
FONTS = core.ROOT / 'brand' / 'fonts'
PORT = 8770
RULES = {  # our own one-line description of each rule, shown only after "Show answer"
    '1e0a9b12': 'every coloured cell falls straight down its column, as far as it can.',
    '007bbfb7': 'a 3×3 grid of copies of the shape: a copy wherever the shape itself has a coloured cell.',
    'a5313dff': 'cells fully enclosed by the red outline become blue; open regions stay black.',
    '3aa6fb7a': 'each light-blue L of three cells gets a blue cell in its missing corner.',
    '1ae2feb7': 'a run of length k left of the wall repeats its colour every k cells right of the wall; '
                'where two runs collide, the run touching the wall wins.',
}
CONTEXT_CHECKED = '28 Nov 2026'
CONTEXT = [  # published numbers only; every row is in ../sources.md
    dict(what='o3-preview, ARC-AGI-1 semi-private, Dec 2024 · lower compute', value='75.7% · $26/task',
         src='R05 arcprize.org/blog/oai-o3-pub-breakthrough (costs revised in 2025)'),
    dict(what='o3-preview, same, 172× compute', value='87.5% · $4,560/task', src='R05'),
    dict(what='a person, ARC-AGI-1 (ARC Prize estimate)', value='~$5/task', src='R05'),
    dict(what='ARC-AGI-2 public eval: average person in the test sample', value='66%', src='R03 ARC-AGI-2 readme'),
    dict(what='o3 (medium), ARC-AGI-2 semi-private, May 2025', value='3.0%', src='R04 arXiv 2505.11831, Table 1'),
    dict(what='ARC Prize 2025 winner (NVARC), ARC-AGI-2 private, offline Kaggle', value='24.03% · $0.20/task',
         src='R08 arcprize.org/blog/arc-prize-2025-results-analysis'),
    dict(what='Claude Opus 4.5, ARC-AGI-2 semi-private, Nov 2025', value='37.6% · $2.20/task', src='R08'),
    dict(what='ARC-AGI-3 at launch, best frontier model, Mar 2026', value='0.51%', src='R10 arcprize.org/blog/arc-agi-3-launch'),
    dict(what='GPT-6.2 Astra, ARC-AGI-2 semi-private (leaderboard 17 Nov 2026)', value='95.8%', src='R12 arcprize.org/leaderboard'),
    dict(what='Claude Fable 5.2, ARC-AGI-3 · Standard / Provider Adapter harness', value='81.2% / 97.7%', src='R12'),
    dict(what='GPT-6.2 Astra, ARC-AGI-3 · Standard / Provider Adapter harness', value='70.3% / 100.0%', src='R12'),
]


# ── build ──────────────────────────────────────────────────────────────────────────────────────
def font_css():
    out = []
    for w in (400, 700):
        f = FONTS / f'vazirmatn-arabic-{w}-normal.woff2'
        if f.exists():
            data = base64.b64encode(f.read_bytes()).decode()
            out.append(f'@font-face{{font-family:"Vazirmatn";font-weight:{w};font-display:block;'
                       f'src:url(data:font/woff2;base64,{data}) format("woff2");unicode-range:U+0600-06FF,U+200C-200E,U+FB50-FDFF,U+FE70-FEFC}}')
    return '\n'.join(out)


def latest_summary():
    files = sorted((HERE / 'results').glob('*/summary.json'), key=lambda p: p.stat().st_mtime)
    real = [f for f in files if f.parent.name != 'mock']   # a mock summary is never baked into the page
    pick = (real or [None])[-1]
    return json.loads(pick.read_text(encoding='utf-8')) if pick else None


def page_data(summary='auto'):
    pz = [{k: p[k] for k in ('n', 'id', 'set', 'prior', 'fa', 'en')} | {'task': p['task'], 'rule': RULES[p['id']]}
          for p in core.puzzles()]
    chars = {p['id']: [len(core.prompt_for(p['task'], i)) for i in range(len(p['task']['test']))] for p in pz}
    return {'puzzles': pz, 'prompt_chars': chars, 'context': CONTEXT, 'context_checked': CONTEXT_CHECKED,
            'summary': latest_summary() if summary == 'auto' else summary, 'built': time.strftime('%Y-%m-%d %H:%M')}


def build(summary='auto'):
    html = TEMPLATE.read_text(encoding='utf-8')
    html = html.replace('/*FONT*/', font_css()).replace('/*DATA*/null', json.dumps(page_data(summary), ensure_ascii=False))
    PAGE.write_text(html, encoding='utf-8')
    return html


# ── live board over SSE ────────────────────────────────────────────────────────────────────────
class Hub:
    def __init__(self):
        self.qs, self.lock, self.last = [], threading.Lock(), None

    def join(self):
        q = queue.Queue()
        with self.lock:
            self.qs.append(q)
            if self.last:
                q.put(self.last)
        return q

    def leave(self, q):
        with self.lock:
            self.qs.remove(q)

    def send(self, ev):
        with self.lock:
            if ev.get('type') == 'board':
                self.last = ev
            for q in self.qs:
                q.put(ev)


class Board:
    """Turns run events into the same shape as arc_run.summarize(), one update per answer."""

    def __init__(self, hub, label=None):
        self.hub, self.label, self.b, self.tests, self.pr = hub, label, None, {}, arc_run.prices()

    def __call__(self, ev):
        if ev['type'] == 'start':
            self.items = ev['items']
            self.b = {'run': self.label or ('mock' if ev['mock'] else 'live'), 'started': ev['wall'], 'mock': ev['mock'],
                      'replay': bool(self.label and not ev['mock']),
                      'models': [{'slot': s['slot'], 'label': s['label'], 'model': s['model'], 'puzzles': {},
                                  'puzzles_solved': 0, 'latency_total_s': 0.0, 'input_tokens': 0, 'output_tokens': 0,
                                  'usd': 0.0, 'usd_upper_bound': 0.0} for s in ev['slots']]}
        elif ev['type'] == 'answer' and self.b:
            m = next(x for x in self.b['models'] if x['slot'] == ev['slot'])
            self.tests.setdefault((ev['slot'], ev['n']), {})[ev['test_index']] = ev['correct']
            need = sum(1 for it in self.items if it['n'] == ev['n'])
            got = self.tests[(ev['slot'], ev['n'])]
            m['puzzles'][str(ev['n'])] = False if False in got.values() else (True if len(got) == need else None)
            m['puzzles_solved'] = sum(1 for v in m['puzzles'].values() if v)
            m['latency_total_s'] += ev['latency_s']
            m['input_tokens'] += ev['input_tokens']
            m['output_tokens'] += ev['output_tokens']
            usd, kind = arc_run.row_usd(ev, self.pr)
            m['usd_upper_bound'] = round(m['usd_upper_bound'] + usd, 4)
            if kind == 'UPPER BOUND' or m['usd'] is None:
                m['usd'] = None
            else:
                m['usd'] = round(m['usd'] + usd, 4)
        else:
            return
        self.hub.send({'type': 'board', 'board': self.b})


HUB = Hub()


def mock_run(delay=0.35):
    out = Path(tempfile.mkdtemp(prefix='hmd-s09-mock-'))
    args = argparse.Namespace(model=None, mock=True)
    arc_run.run_all(arc_run.slots(args), out, on_event=Board(HUB), delay=delay)


def replay(name, speed=1.0):
    path = arc_run.RUNS / name / 'events.jsonl'
    if not path.exists():
        sys.exit(f'no events for run {name!r} in {arc_run.RUNS}')
    board, prev = Board(HUB, label=name), 0.0
    for line in path.read_text(encoding='utf-8').splitlines():
        ev = json.loads(line)
        time.sleep(max(0.0, (ev.get('t', 0) - prev) / speed))
        prev = ev.get('t', 0)
        board(ev)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, body, ctype='text/html; charset=utf-8', code=200):
        data = body.encode('utf-8') if isinstance(body, str) else body
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/arc_live.html'):
            return self.reply(PAGE.read_text(encoding='utf-8'))
        if path == '/state':
            return self.reply(json.dumps({'summary': latest_summary(), 'live': HUB.last}), 'application/json')
        if path == '/events':
            return self.events()
        return self.reply('not found', 'text/plain', 404)

    def do_POST(self):
        if self.path.split('?')[0] == '/run-mock':
            delay = 0.0 if 'fast' in self.path else 0.35
            threading.Thread(target=mock_run, args=(delay,), daemon=True).start()
            return self.reply('{"started": "mock"}', 'application/json')
        return self.reply('not found', 'text/plain', 404)

    def events(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        q = HUB.join()
        try:
            self.wfile.write(b'data: {"type": "hello"}\n\n')
            self.wfile.flush()
            while True:
                try:
                    ev = q.get(timeout=15)
                    self.wfile.write(('data: ' + json.dumps(ev, ensure_ascii=False) + '\n\n').encode('utf-8'))
                except queue.Empty:
                    self.wfile.write(b': keep-alive\n\n')
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            HUB.leave(q)


def serve(port):
    srv = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


# ── self-test ────────────────────────────────────────────────────────────────────────────────────
def selftest():
    for k in ('GEMINI_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'OPENROUTER_API_KEY', 'HOMODYNE_MODEL'):
        os.environ.pop(k, None)
    t0 = time.time()
    src = (HERE / 'data' / 'SOURCE.txt').read_text(encoding='utf-8')
    for p in core.PUZZLES:
        f = core.DATA / f'{p["id"]}.json'
        assert hashlib.sha256(f.read_bytes()).hexdigest() in src, f'{f.name}: sha256 not in data/SOURCE.txt'
    for lic in ('LICENSE-ARC-AGI-1.txt', 'LICENSE-ARC-AGI-2.txt'):
        assert 'Apache License' in (HERE / 'data' / lic).read_text(encoding='utf-8'), lic
    tasks = {p['id']: p['task'] for p in core.puzzles()}
    assert len(tasks) == 5 and len(core.test_items()) == 7
    t = tasks['007bbfb7']
    assert all(solve_fractal.solve(pr['input']) == pr['output'] for pr in t['train'] + t['test'])
    assert not any(solve_fractal.solve(pr['input']) == pr['output'] for pr in tasks['1e0a9b12']['train']), \
        'the hand-written solver must not "solve" a different task'
    g = [[0, 4], [1, 0]]
    assert core.grid_text(g) == '0 4\n1 0' and core.column_gap(g) == 4
    assert core.exact(g, [[0, 4], [1, 0]]) and not core.exact(g, [[0, 4]]) and not core.exact(g, [[0, 4], [1, 1]])
    assert core.cells_right(g, [[0, 4], [1, 1]]) == 3
    grids, flag = core.parse_reply('```json\n{"attempt_1": [[0,4],[1,0]], "attempt_2": [[9]]}\n```')
    assert flag == 'ok' and grids[0] == g and grids[1] == [[9]]
    assert core.parse_reply('no idea')[1] == 'unparsed' and core.parse_reply('{"attempt_1": [[10]]}')[0] == [None, None]
    assert core.parse_reply('answer: [[0, 4], [1, 0]]')[0][0] == g
    assert core.solved([None, g], g) and not core.solved([[[1]], None], g)
    pr = core.prompt_for(tasks['1ae2feb7'], 2)
    assert pr.startswith(core.PROMPT_HEAD) and pr.count('Demonstration') == 6 and 'Test input (8x15)' in pr
    # plan: no key, refuses an empty slot, labels the bound
    try:
        arc_run.slots(argparse.Namespace(model=None, mock=False))
        raise AssertionError('empty slots must refuse')
    except SystemExit as e:
        assert 'no model ID' in str(e)
    fake = arc_run.slots(argparse.Namespace(model=[f'{s}=openrouter:x/{s}' for s in ('gemini', 'claude', 'gpt', 'open1', 'open2')], mock=False))
    lines, total = arc_run.plan(fake)
    assert 'NOT AN OFFICIAL PRICE' in '\n'.join(lines) and total > 0 and '35 calls' in lines[0]
    # mock run through the engine, the cost cap, the summary
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'mock'
        sl = arc_run.slots(argparse.Namespace(model=None, mock=True))
        evs = []
        board = Board(Hub())
        spent, capped = arc_run.run_all(sl, out, on_event=lambda e: (evs.append(e), board(e)))
        assert spent == 0 and not capped and evs[0]['type'] == 'start' and evs[-1]['type'] == 'end'
        assert sum(e['type'] == 'answer' for e in evs) == 35 and not any(e['type'] == 'error' for e in evs)
        (out / 'meta.json').write_text(json.dumps({'slots': sl, 'started': 'test', 'mock': True}), encoding='utf-8')
        rep = arc_run.summarize(out)
        assert rep['mock'] and len(rep['models']) == 5 and all(m['usd'] == 0 for m in rep['models'])
        for m, b in zip(rep['models'], board.b['models']):
            assert m['puzzles_solved'] == b['puzzles_solved'], 'live board and report disagree'
        rep2 = arc_run.summarize(out)
        assert rep == rep2
        # the cap: pretend every mock call cost $1, cap at $3 → calls stop
        pr = arc_run.prices()
        old = arc_run.row_usd
        arc_run.row_usd = lambda r, p: (1.0, 'price')
        try:
            spent, capped = arc_run.run_all(sl, Path(td) / 'cap', cap_usd=3.0, pr=pr)
        finally:
            arc_run.row_usd = old
        rows = (Path(td) / 'cap' / 'rows.jsonl').read_text().splitlines()
        assert capped and len(rows) < 35, f'cap did not stop the run ({len(rows)} rows)'
    # page and server
    html = build(summary=None)
    assert '/*DATA*/' not in html and '"1ae2feb7"' in html and 'NOT RUN YET' in html
    node = shutil.which('node')
    if node:                                   # the page script must parse (a syntax error = a blank page on the day)
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(re.findall(r'<script>(.*?)</script>', html, re.S)[0])
        r = subprocess.run([node, '--check', f.name], capture_output=True, text=True)
        os.unlink(f.name)
        assert r.returncode == 0, 'page script does not parse: ' + r.stderr[:300]
    srv = serve(0)
    port = srv.server_address[1]
    try:
        base = f'http://127.0.0.1:{port}'
        assert 'ARC Puzzle Lab' in urllib.request.urlopen(base + '/', timeout=5).read().decode()
        json.loads(urllib.request.urlopen(base + '/state', timeout=5).read())
        es = urllib.request.urlopen(base + '/events', timeout=10)
        assert b'hello' in es.readline()
        urllib.request.urlopen(urllib.request.Request(base + '/run-mock?fast', method='POST'), timeout=5)
        seen = 0
        deadline = time.time() + 15
        while time.time() < deadline:
            line = es.readline()
            if line.startswith(b'data: ') and b'"board"' in line:
                seen += 1
                if seen >= 36:
                    break
        assert seen >= 36, f'only {seen} board events over SSE'
    finally:
        srv.shutdown()
    build()   # leave the page as it would be built normally
    print(f'arc_live selftest passed in {time.time() - t0:.1f} s (5 tasks + licences + sha256, solver 6/6 and not on '
          'other tasks, exact match, parser, plan bound, 35 mock calls, cost cap, page, /state, SSE)')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--serve', action='store_true')
    g.add_argument('--selftest', action='store_true')
    ap.add_argument('--replay', help='run name in runs/ to replay into the page (with --serve)')
    ap.add_argument('--speed', type=float, default=1.0)
    ap.add_argument('--port', type=int, default=PORT)
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    build()
    print(f'built {PAGE}')
    if args.serve:
        serve(args.port)
        print(f'serving http://127.0.0.1:{args.port}/  (Ctrl-C to stop)')
        if args.replay:
            threading.Thread(target=replay, args=(args.replay, args.speed), daemon=True).start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
