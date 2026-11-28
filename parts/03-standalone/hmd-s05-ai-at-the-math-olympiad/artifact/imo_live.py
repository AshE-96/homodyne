#!/usr/bin/env python3
"""HMD-S05 · imo_live.py — official IMO statistics + a live session where five models attempt IMO 2025 problems.

    python3 imo_live.py --build                 # write imo_live.html (statistics views, opens from disk)
    python3 imo_live.py --serve                 # statistics only, http://127.0.0.1:8765
    python3 imo_live.py --mock                  # rehearsal: five MOCK lanes, no key, no network, watermarked
    python3 imo_live.py --fetch-problems        # official English PDF -> artifact/data/problems/ (not committed)
    python3 imo_live.py --live --problem P1     # [RUN] the real session; spends money; asks [y/N] first
    python3 imo_live.py --replay RUN            # replay artifact/data/runs/RUN with its true timing
    python3 imo_live.py --grade-sheet RUN       # blind sheet + grades.json template for the HUMAN grader
    python3 imo_live.py --rebuild               # re-derive derived/imo-stats.json from imo-official.org
    python3 imo_live.py --selftest              # offline, keys unset
Views: 1 difficulty · 2 medal cut-offs · 3 Iran history · 4 live session · 5 who graded + rubric.
URL: ?view=4&year=2025&p=P1. Record at 1600×900. The page never says "solved": a person grades later.
"""
import argparse
import base64
import json
import os
import queue
import random
import re
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # works under python3 -I too
import imo_core as core  # noqa: E402

sys.path.insert(0, str(core.ROOT / 'tools'))
import llm  # noqa: E402

TEMPLATE = core.HERE / 'imo_page.html'
BUILT = core.HERE / 'imo_live.html'
RUNS = core.DATA / 'runs'
FONTS = core.ROOT / 'brand' / 'fonts'


def font_css():
    out = []
    for w in (400, 700):
        for script in ('arabic', 'latin'):
            f = FONTS / f'vazirmatn-{script}-{w}-normal.woff2'
            if f.exists():
                b64 = base64.b64encode(f.read_bytes()).decode()
                out.append(f'@font-face{{font-family:Vazirmatn;font-weight:{w};src:url(data:font/woff2;base64,{b64}) '
                           'format("woff2")}')
    return '\n'.join(out)


def page():
    rub = {p: core.rubric(p) for p in core.PROBLEMS}
    return (TEMPLATE.read_text(encoding='utf-8').replace('/*FONTS*/', font_css())
            .replace('/*STATS*/null', json.dumps(core.load_stats(), ensure_ascii=False))
            .replace('/*RUBRICS*/null', json.dumps(rub, ensure_ascii=False)))


class Hub:
    """Fan-out of events to every open page; history for late joiners (same pattern as HMD-K01)."""

    def __init__(self):
        self.lock, self.subs, self.history = threading.Lock(), set(), []

    def join(self):
        q = queue.Queue()
        with self.lock:
            self.subs.add(q)
            for ev in self.history:
                q.put(ev)
        return q

    def leave(self, q):
        with self.lock:
            self.subs.discard(q)

    def send(self, ev):
        with self.lock:
            self.history.append(ev)
            targets = list(self.subs)
        for q in targets:
            q.put(ev)


HUB = Hub()


# ── one session: every slot gets the same prompt once, all in parallel ───────────────────────────
def slots_from(models_file, mock):
    if mock:
        return core.MOCK_SLOTS
    m = json.loads(Path(models_file).read_text(encoding='utf-8'))
    empty = [s['slot'] for s in m['slots'] if not s.get('model')]
    if empty:
        sys.exit(f'models.json: fill the model id for {", ".join(empty)} first (see its _how)')
    return [{'slot': s['slot'], 'label': s['label'], 'model': s['model']} for s in m['slots']]


def run_session(slots, pids, out, emit, mode, delay=0.0, prices=None):
    """Ask each slot each problem once (no retries beyond transport errors, no best-of-n). Logs events.jsonl."""
    prices = prices or json.loads((core.HERE / 'prices.json').read_text(encoding='utf-8'))
    out.mkdir(parents=True, exist_ok=True)
    log, lock, t0 = (out / 'events.jsonl').open('w', encoding='utf-8'), threading.Lock(), time.monotonic()
    texts = {}
    for p in pids:
        try:
            texts[p] = core.statement(p)
        except FileNotFoundError:
            if mode != 'mock':
                raise
            texts[p] = f'[statement of IMO 2025 {p} not bundled: IMO copyright; MOCK run]'

    def send(ev):
        ev['t'] = round(time.monotonic() - t0, 2) if mode != 'mock' else ev.get('t', 0)
        with lock:
            log.write(json.dumps(ev, ensure_ascii=False) + '\n')
            log.flush()
        emit(ev)

    send({'type': 'start', 'mode': mode, 'run': out.name, 'date': time.strftime('%Y-%m-%d %H:%M'), 'slots': slots,
          'problems': pids, 'system': core.SYSTEM, 'max_tokens': core.MAX_TOKENS,
          'speed': 1 / delay if mode == 'mock' and delay > 0 else 1.0})
    ends = []

    def lane(s):
        clock = 0.0
        for p in pids:
            send({'type': 'ask', 'slot': s['slot'], 'problem': p, 't': clock})
            try:
                if mode == 'mock':
                    secs = core.MOCK_SECONDS[s['slot']] * (1 if p == 'P1' else 3)
                    time.sleep(secs * delay)
                    clock += secs
                    res = llm.call(core.prompt_for(p, texts[p]), system=core.SYSTEM, model=s['model'],
                                   mock=lambda _p, s=s, p=p: core.mock_answer(s['slot'], p))
                    res.latency_s = float(secs)
                else:
                    res = llm.call(core.prompt_for(p, texts[p]), system=core.SYSTEM, model=s['model'],
                                   max_tokens=core.MAX_TOKENS, cache_dir=out / 'cache')
            except Exception as e:      # recorded, shown on the lane, never retried silently
                send({'type': 'error', 'slot': s['slot'], 'problem': p, 'error': str(e)[:300], 't': clock})
                continue
            ev = {'type': 'answer', 'slot': s['slot'], 'problem': p, 'model': s['model'],
                  'model_served': res.model_served, 'fell_back': res.fell_back, 'text': res.text,
                  'input_tokens': res.input_tokens, 'output_tokens': res.output_tokens,
                  'reasoning_tokens': res.extra.get('reasoning_tokens') or res.extra.get('thoughts_tokens') or 0,
                  'latency_s': round(res.latency_s, 1), 'stop_reason': res.stop_reason,
                  'cost_usd': res.extra.get('cost_usd'), 'grade': None, 't': clock, 'mock': mode == 'mock'}
            ev['usd'] = None if mode == 'mock' else core.usd(ev, prices)
            ev['usd_bound'] = round(core.upper_bound_usd(ev, prices), 2) if mode == 'mock' else None
            send(ev)
        ends.append(clock)
        send({'type': 'done', 'slot': s['slot'], 't': clock})

    threads = [threading.Thread(target=lane, args=(s,)) for s in slots]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    send({'type': 'end', 't': max([0.0] + ends)})
    log.close()
    return out


def load_grades(run_dir):
    """grades.json (filled by a person) mapped back from blind IDs to (slot, problem)."""
    g, k = run_dir / 'grades.json', run_dir / 'blind-key.json'
    if not (g.exists() and k.exists()):
        return {}
    grades, key = json.loads(g.read_text(encoding='utf-8')), json.loads(k.read_text(encoding='utf-8'))
    return {tuple(key[b]): v for b, v in grades.items() if v.get('score') is not None and v.get('grader')}


def replay(run_dir, emit, speed=1.0):
    grades = load_grades(run_dir)
    evs = [json.loads(x) for x in (run_dir / 'events.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    t0 = time.monotonic()
    for ev in evs:
        wait = ev.get('t', 0) / speed - (time.monotonic() - t0)
        if wait > 0:
            time.sleep(wait)
        if ev['type'] == 'start':
            ev = {**ev, 'mode': 'replay' if ev['mode'] != 'mock' else 'mock', 'speed': speed}
        if ev['type'] == 'answer':
            ev = {**ev, 'grade': grades.get((ev['slot'], ev['problem']))}
        emit(ev)


VENDORS = ('Gemini', 'Google', 'DeepMind', 'Claude', 'Anthropic', 'OpenAI', 'ChatGPT', 'GPT', 'Qwen', 'DeepSeek',
           'Llama', 'Meta', 'Mistral', 'Kimi', 'Moonshot', 'Grok', 'xAI', 'GLM', 'Nemotron')


def grade_sheet(run_dir):
    """Write a blind grading sheet: answers under random IDs, the rubric, and an empty grades.json."""
    evs = [json.loads(x) for x in (run_dir / 'events.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    ans = [e for e in evs if e['type'] == 'answer']
    rng = random.Random(run_dir.name)
    rng.shuffle(ans)
    key, md = {}, [f'# Blind grading sheet · {run_dir.name}', '',
                   'Grade each answer with the rubric only. Model names are hidden. Write scores into grades.json '
                   '(score 0–7, your name as grader, rubric items awarded, notes). Do not open blind-key.json first.', '']
    names = {w for e in ans for w in (e['slot'], e['model'], e['model'].split(':')[-1], e.get('model_served') or '')}
    names |= set(VENDORS)
    hide = re.compile('|'.join(re.escape(n) for n in sorted(names, key=len, reverse=True) if len(n) > 2), re.I)
    for i, e in enumerate(ans):
        bid = f'{e["problem"]}-{chr(65 + i)}'
        key[bid] = [e['slot'], e['problem']]
        md += [f'## {bid}', '', '```', hide.sub('[model]', e['text']), '```', '']
    for p in sorted({e['problem'] for e in ans}):
        r = core.rubric(p)
        md += [f'## Rubric {p} — {r["status"]}', ''] + [f'- **{i["points"]}** · {i["en"]}' for i in r['items']]
        md += [''] + [f'- deduction: {d["en"]}' for d in r['deductions']] + ['']
    (run_dir / 'grade-sheet.md').write_text('\n'.join(md), encoding='utf-8')
    (run_dir / 'blind-key.json').write_text(json.dumps(key, indent=1), encoding='utf-8')
    g = run_dir / 'grades.json'
    if not g.exists():
        g.write_text(json.dumps({b: {'score': None, 'grader': None, 'items': [], 'notes': ''} for b in key},
                                indent=1), encoding='utf-8')
    return run_dir / 'grade-sheet.md'


# ── server ───────────────────────────────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, body, ctype='text/html; charset=utf-8', code=200):
        data = body.encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/imo_live.html'):
            return self.reply(page())
        if path == '/state':
            with HUB.lock:
                return self.reply(json.dumps(HUB.history, ensure_ascii=False), 'application/json; charset=utf-8')
        if path != '/events':
            return self.reply('not found', 'text/plain', 404)
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        q = HUB.join()
        try:
            self.wfile.write(b'retry: 1000\n\n')
            self.wfile.flush()
            while True:
                try:
                    self.wfile.write(f'data: {json.dumps(q.get(timeout=15), ensure_ascii=False)}\n\n'.encode())
                except queue.Empty:
                    self.wfile.write(b': ping\n\n')
                self.wfile.flush()
        except OSError:
            pass
        finally:
            HUB.leave(q)


def serve(port):
    srv = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    g = ap.add_mutually_exclusive_group()
    for a in ('--build', '--serve', '--mock', '--live', '--fetch-problems', '--rebuild', '--selftest'):
        g.add_argument(a, action='store_true')
    g.add_argument('--replay', metavar='RUN')
    g.add_argument('--grade-sheet', metavar='RUN')
    ap.add_argument('--problem', action='append', choices=sorted(core.PROBLEMS), help='default: P1')
    ap.add_argument('--models', default=str(core.HERE / 'models.json'))
    ap.add_argument('--run', help='run folder name under artifact/data/runs/')
    ap.add_argument('--speed', type=float, default=1.0)
    ap.add_argument('--delay', type=float, default=0.1, help='mock: wall seconds per simulated second')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--yes', action='store_true')
    ap.add_argument('--no-browser', action='store_true')
    ap.add_argument('--hold', type=float, default=None, help='exit this many seconds after the end')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.build:
        BUILT.write_text(page(), encoding='utf-8')
        print('wrote', BUILT)
        return 0
    if a.rebuild:
        s = core.rebuild()
        print('wrote', core.STATS, {y: v['n_rows'] for y, v in s['years'].items()})
        return 0
    if a.fetch_problems:
        print(core.fetch_statements())
        return 0
    if a.grade_sheet:
        print('wrote', grade_sheet(RUNS / a.grade_sheet))
        return 0
    pids = a.problem or ['P1']
    job = None
    if a.replay:
        job = lambda: replay(RUNS / a.replay, HUB.send, a.speed)
    elif a.mock or a.live:
        slots = slots_from(a.models, a.mock)
        name = a.run or ('mock-' if a.mock else 'live-') + time.strftime('%Y%m%d-%H%M')
        if a.live:
            print(f'[RUN] {len(slots)} models × {len(pids)} problem(s), one attempt each, max {core.MAX_TOKENS} '
                  'output tokens per answer. This spends API money.')
            for s in slots:
                print('   ', s['slot'], s['model'])
            if not a.yes and input('Continue? [y/N] ').strip().lower() != 'y':
                return 1
        job = lambda: run_session(slots, pids, RUNS / name, HUB.send, 'mock' if a.mock else 'live', a.delay)
    srv = serve(a.port)
    url = f'http://127.0.0.1:{a.port}/?view={4 if job else 1}'
    print('page:', url)
    if not a.no_browser:
        webbrowser.open(url)
        time.sleep(1.5)
    if job:
        job()
        print('session finished')
    try:
        if a.hold is not None:
            time.sleep(a.hold)
        else:
            while True:
                time.sleep(3600)
    except KeyboardInterrupt:
        pass
    srv.shutdown()
    return 0


def selftest():
    import tempfile
    import urllib.request
    for k in llm.KEYS.values():
        assert not os.environ.get(k), f'{k} is set: unset it for the selftest'
    s = core.load_stats()
    y = s['years']['2025']
    assert y['cutoffs'] == {'gold': 35, 'silver': 28, 'bronze': 19} and y['contestants'] == 630 == y['n_rows']
    assert all(sum(p['hist']) == 630 for p in y['problems']) and sum(y['total_hist']) == 630
    assert y['problems'][5]['full'] == 6 and abs(y['problems'][5]['mean'] - 0.184) < 1e-3
    assert y['counts']['gold'] == sum(y['total_hist'][35:]) == 72, 'gold count must match the histogram'
    ir = y['iran']
    assert (ir['rank'], ir['points'], ir['gold'], ir['silver'], ir['bronze']) == (12, 183, 2, 3, 1)
    assert sum(ir['problems']) == ir['points'] and ir['problems'][5] == 0
    assert s['years']['2024']['cutoffs']['gold'] == 29 and s['years']['2026']['iran']['points'] == 147
    assert [r for r in s['iran_history'] if r['rank'] == 1] and min(r['year'] for r in s['iran_history']) == 1985
    blob = json.dumps(s, ensure_ascii=False)
    assert 'data-name' not in blob and 'contestant/' not in blob, 'no individual records may be stored'
    for n in (3, 4, 5, 6):
        assert core.sunny_ks(n) == [0, 1, 3], n
    for p in core.PROBLEMS:
        r = core.rubric(p)
        assert sum(i['points'] for i in r['items']) == r['max'] == 7 and 'NOT the official' in r['status']
    assert 'solved' not in TEMPLATE.read_text(encoding='utf-8').lower(), 'the page must not claim a solve'
    with tempfile.TemporaryDirectory() as tmp:
        out = run_session(core.MOCK_SLOTS, ['P1', 'P6'], Path(tmp) / 'mock-x', lambda e: None, 'mock', delay=0)
        evs = [json.loads(x) for x in (out / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
        ans = [e for e in evs if e['type'] == 'answer']
        assert len(ans) == 10 and all(e['grade'] is None and e['usd'] is None and e['mock'] for e in ans)
        assert all(e['text'].startswith('[MOCK ANSWER') for e in ans) and evs[-1]['type'] == 'end'
        sheet = grade_sheet(out)
        assert 'gemini' not in sheet.read_text(encoding='utf-8'), 'the grading sheet must be blind'
        gr = json.loads((out / 'grades.json').read_text())
        bid = sorted(gr)[0]
        gr[bid].update(score=3, grader='selftest')
        (out / 'grades.json').write_text(json.dumps(gr))
        seen = []
        replay(out, seen.append, speed=1e6)
        graded = [e for e in seen if e['type'] == 'answer' and e['grade']]
        assert len(graded) == 1 and graded[0]['grade']['score'] == 3, 'only human-entered grades appear'
        global HUB
        HUB = Hub()
        for e in seen:
            HUB.send(e)
        srv = serve(0)
        port = srv.server_address[1]
        html = urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=5).read().decode()
        assert 'dir="rtl"' in html and 'NOT RUN YET' in html and '"cutoffs"' in html and 'Vazirmatn' in html
        r = urllib.request.urlopen(f'http://127.0.0.1:{port}/events', timeout=5)
        first = [r.readline() for _ in range(4)]
        assert any(b'"type": "start"' in x for x in first), first
        r.close()
        srv.shutdown()
    print('imo_live selftest ok: 2025 stats (630 rows, cut-offs 35/28/19, P6 6 full scores, Iran 12th/183), '
          'no names stored, sunny_ks(3..6) = [0, 1, 3], rubrics sum to 7, mock session 10 ungraded answers, '
          'blind sheet, human grade only via grades.json, page + SSE')
    return 0


if __name__ == '__main__':
    sys.exit(main())
