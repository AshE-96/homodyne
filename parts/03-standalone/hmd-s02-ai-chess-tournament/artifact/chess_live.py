#!/usr/bin/env python3
"""HMD-S02 · chess_live.py — the live page: board, move list, eval bar, illegal-move counter, per-call latency/tokens/$.

    python3 chess_live.py --mock                      # MOCK players, watermark, no key, no network
    python3 chess_live.py --live --max-usd 40 [...]   # the real round-robin (owner only): plan, then [y/N]
    python3 chess_live.py --replay RUN                # replay a run with its true timing
    python3 chess_live.py --replay RUN --speed 20     # 20× faster, labelled «×۲۰» on screen
    python3 chess_live.py --selftest                  # same as chess_run.py --selftest
Then open http://127.0.0.1:8766 (opened automatically unless --no-browser). Record at 1600×900.
URL: ?game=G07 features one game. Keys: ← → previous / next game · A follow the latest move.

Server-sent events over the standard library (ThreadingHTTPServer + EventSource + a fan-out Hub, the same pattern as
HMD-K01's konkur_live.py, rewritten here). Every event is kept, so a reloaded page catches up.
"""
import base64
import json
import queue
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import chess_core as cc
import chess_run

FONTS = cc.ROOT / 'brand' / 'fonts'
PAGE = cc.HERE / 'chess_page.html'


class Hub:
    """Fan-out of events to every open page; history for late joiners."""

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


class Board:
    """Labels every event stream with its mode (live / mock / replay ×N) before publishing it."""

    def __init__(self, hub, mode, speed=1.0):
        self.hub, self.mode, self.speed = hub, mode, speed

    def __call__(self, ev):
        ev = dict(ev)
        if ev['type'] == 'start':
            ev['orig_mode'] = ev.get('mode')
            ev.update(mode=self.mode, speed=self.speed)
            if self.mode == 'replay' and ev['orig_mode'] == 'mock':
                ev['mode'] = 'mock'          # a replayed MOCK run stays MOCK on screen
        self.hub.send(ev)


def find_events(run):
    for d in (cc.RESULTS / run, cc.DATA / 'runs' / run):
        if (d / 'events.jsonl').exists():
            return d / 'events.jsonl'
        evs = sorted(d.glob('events-*.jsonl'), key=lambda p: p.stat().st_size) if d.exists() else []
        if evs:
            return evs[-1]
    return None


def replay(path, board, speed):
    events = [json.loads(x) for x in Path(path).read_text(encoding='utf-8').splitlines() if x.strip()]
    t0 = time.monotonic()
    for ev in events:
        wait = ev.get('t', 0) / speed - (time.monotonic() - t0)
        if wait > 0:
            time.sleep(wait)
        board(ev)


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
    return PAGE.read_text(encoding='utf-8').replace('%FONTS%', font_css())


HUB = Hub()


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
        if path == '/':
            return self.reply(page())
        if path == '/state':
            with HUB.lock:
                return self.reply(json.dumps(HUB.history, ensure_ascii=False), 'application/json; charset=utf-8')
        if path == '/events':
            return self.events()
        self.reply('not found', 'text/plain', 404)

    def events(self):
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
    ap = chess_run.parser()
    ap.description = __doc__.split('\n')[0]
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--live', action='store_true')
    g.add_argument('--replay', metavar='RUN')
    ap.add_argument('--speed', type=float, default=1.0, help='replay speed (1 = true timing)')
    ap.add_argument('--port', type=int, default=8766)
    ap.add_argument('--no-browser', action='store_true')
    ap.add_argument('--hold', type=float, default=None, help='exit this many seconds after the end (default: stay)')
    args = ap.parse_args(argv)
    if args.selftest:
        import chess_selftest
        return chess_selftest.run()
    if not (args.mock or args.live or args.replay):
        ap.print_help()
        return 0
    if args.replay:
        path = find_events(args.replay)
        if not path:
            sys.exit(f'no events for run {args.replay!r} in results/ or data/runs/')
        board = Board(HUB, 'replay', args.speed)
        job = lambda: replay(path, board, args.speed)
    else:
        if args.mock and args.delay == 0.02:
            args.delay = 0.25                      # live mock: watchable pace (simulated seconds × 0.25)
        sl, games, plies = chess_run.prepare(args)
        print('\n'.join(chess_run.plan_lines(sl, games, plies, args.max_usd)))
        if args.live:
            chess_run.paid_guard(args)
            if not args.yes and input('This spends API money. Continue? [y/N] ').strip().lower() != 'y':
                return 1
        out = chess_run.run_dir(args, sl)
        board = Board(HUB, 'mock' if args.mock else 'live')
        job = lambda: chess_run.run_tournament(sl, games, out, on_event=board, max_plies=plies, cap=args.max_usd,
                                               parallel=args.parallel, engine_depth=args.engine_depth,
                                               want_engine=not args.no_engine, use_schema=not args.no_schema,
                                               delay=args.delay, mode='mock' if args.mock else 'live')
    srv = serve(args.port)
    url = f'http://127.0.0.1:{args.port}/'
    print(f'live page: {url}  (record at 1600×900; ?game=G07 features a game; ← → switch games, A follows)')
    if not args.no_browser:
        webbrowser.open(url)
        time.sleep(1.5)
    job()
    print('finished' + ('' if args.replay else f'; next: python3 chess_run.py report --run {out.name}'))
    try:
        if args.hold is not None:
            time.sleep(args.hold)
        else:
            while True:
                time.sleep(3600)
    except KeyboardInterrupt:
        pass
    srv.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
