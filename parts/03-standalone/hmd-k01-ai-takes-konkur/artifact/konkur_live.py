#!/usr/bin/env python3
"""HMD-K01 · konkur_live.py — the live scoreboard: five lanes, a clock, tokens and $, then a کارنامه per model.

    python3 konkur_live.py --mock                     # MOCK models on synthetic questions, watermark, no key
    python3 konkur_live.py --live [run options]       # the real run (same options as konkur_run.py run), [y/N] first
    python3 konkur_live.py --replay RUN               # replay private/konkur/runs/RUN with its true timing
    python3 konkur_live.py --replay RUN --speed 20    # 20× faster, labelled «×۲۰» on screen
    python3 konkur_live.py --selftest
Then open http://127.0.0.1:8765 (the script opens it unless --no-browser). Record at 1600×900, dark, Persian RTL.

Server-sent events over the standard library (ThreadingHTTPServer + EventSource + a fan-out Hub: the same pattern as
scripts/prompter-remote.py, rewritten here, not imported). Every event is kept, so a reloaded page catches up.
"""
import argparse
import base64
import json
import queue
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import kcore
import konkur_run
import rank_estimate

FONTS = kcore.ROOT / 'brand' / 'fonts'


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
    """Adds $ and the end-of-run کارنامه to the raw exam events, then publishes them."""

    def __init__(self, hub, mode, speed=1.0, prices=None, tscale=1.0):
        self.hub, self.mode, self.speed, self.tscale = hub, mode, speed, tscale   # mock: clock in simulated seconds
        self.prices = prices or json.loads(konkur_run.PRICES_FILE.read_text(encoding='utf-8'))
        self.rows, self.slots, self.lock = {}, [], threading.Lock()

    def usd(self, ev):
        d = konkur_run.usd(ev, self.prices)
        if d is None and self.mode == 'mock':           # MOCK only: the fallback upper-bound prices, labelled
            fb = self.prices['fallback']['default']
            d = (ev['input_tokens'] * fb['input_per_mtok'] + ev['output_tokens'] * fb['output_per_mtok']) / 1e6
        return d

    def __call__(self, ev):
        ev = dict(ev)
        if 't' in ev and self.tscale != 1.0:
            ev['t'] = round(ev['t'] * self.tscale, 3)
        if ev['type'] == 'start':
            self.slots = ev['slots']
            ev.update(mode=self.mode, speed=self.speed, prices_checked_on=self.prices.get('checked_on'))
        if ev['type'] == 'answer':
            ev['usd'] = self.usd(ev)
            ev['value'] = kcore.item_value(ev['label'])
            with self.lock:
                self.rows.setdefault(ev['slot'], []).append(ev)
        self.hub.send(ev)
        if ev['type'] == 'done':
            self.hub.send(self.karnameh(ev['slot'], ev['t']))

    def karnameh(self, slot, t):
        with self.lock:
            rows = list(self.rows.get(slot, []))
        exams = []
        for y, g in sorted({(r['year'], r['group']) for r in rows}):
            ex = [r for r in rows if (r['year'], r['group']) == (y, g)]
            pcts = {s: kcore.konkur_percent([r['label'] for r in ex if r['subject'] == s])
                    for s in sorted({r['subject'] for r in ex})}
            est = rank_estimate.estimate(g, y, pcts)
            exams.append({'year': y, 'group': g, 'percents': pcts, 'weighted': est['weighted_exam_percent'],
                          'estimate_fa': est['summary_fa'], 'range_fa': est['range_fa'], 'n': len(ex)})
        dollars = [r['usd'] for r in rows]
        return {'type': 'karnameh', 'slot': slot, 't': t, 'exams': exams,
                'total_s': round(sum(r['latency_s'] for r in rows), 1),
                'tokens': sum(r['input_tokens'] + r['output_tokens'] for r in rows),
                'usd': None if any(d is None for d in dollars) else round(sum(dollars), 2),
                'percent': kcore.konkur_percent([r['label'] for r in rows])}


def replay(path, board, speed):
    events = [json.loads(x) for x in Path(path).read_text(encoding='utf-8').splitlines() if x.strip()]
    t0 = time.monotonic()
    for ev in events:
        wait = ev.get('t', 0) / speed - (time.monotonic() - t0)
        if wait > 0:
            time.sleep(wait)
        board(ev)


# ── the page ─────────────────────────────────────────────────────────────────────────────────────
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


PAGE = """<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>کنکور هوش مصنوعی · هومودین</title><style>
%FONTS%
:root{--night:#111214;--panel:#181A1D;--line:#2A2C30;--ink:#F3F1EC;--muted:#A9A69D;--amber:#E8A33D;--ok:#6FBF73;--bad:#E06C5B}
*{box-sizing:border-box;margin:0}body{background:var(--night);color:var(--ink);font-family:Vazirmatn,system-ui,sans-serif;
height:100vh;overflow:hidden;display:flex;flex-direction:column;padding:22px 28px;gap:14px;font-variant-numeric:tabular-nums}
header{display:flex;align-items:center;gap:20px}header h1{font-size:30px;font-weight:700}header h1 em{color:var(--amber);font-style:normal}
.badge{border:1px solid var(--amber);color:var(--amber);border-radius:6px;padding:3px 12px;font-size:18px}
#clock{margin-inline-start:auto;font-size:34px;font-weight:700;direction:ltr}
#lanes{display:flex;flex-direction:column;gap:10px;flex:1}
.lane{flex:1;display:grid;grid-template-columns:230px 150px 1fr 230px 330px;gap:18px;align-items:center;background:var(--panel);
border:1px solid var(--line);border-radius:10px;padding:10px 18px;position:relative;transition:border-color .3s}
.lane.flash-ok{border-color:var(--ok)}.lane.flash-bad{border-color:var(--bad)}.lane.done{border-color:var(--amber)}
.name b{display:block;font-size:26px}.name small{color:var(--muted);font-size:14px;direction:ltr;display:block;text-align:right;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.timer b{font-size:32px;direction:ltr;display:block}.timer small,.q small,.tok small{color:var(--muted);font-size:15px}
.q b{font-size:21px;display:block}.bar{height:6px;background:var(--line);border-radius:3px;margin-top:8px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--amber);width:0;transition:width .4s}
.tok div{font-size:17px;direction:ltr;text-align:right}.tok div span{color:var(--muted)}
.subj{display:flex;gap:8px;flex-wrap:wrap}.subj i{font-style:normal;background:#202226;border-radius:6px;padding:4px 9px;font-size:17px}
.subj i b{color:var(--amber)}.place{position:absolute;left:14px;top:8px;color:var(--amber);font-size:22px;font-weight:700}
#cards{position:fixed;inset:0;background:rgba(17,18,20,.96);display:none;grid-template-columns:repeat(5,1fr);gap:14px;padding:40px 28px}
#cards.on{display:grid}.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:10px;font-size:16px}
.card h2{font-size:26px}.card .big{font-size:40px;color:var(--amber);font-weight:700}.card table{width:100%;border-collapse:collapse}
.card td{padding:5px 0;border-bottom:1px solid var(--line);font-size:19px}.card td b{color:var(--ink)}.card .est b{color:var(--ink)}.card .est{color:var(--muted);font-size:16px;line-height:1.55}
.est-tag{color:var(--night);background:var(--amber);border-radius:4px;padding:0 6px;font-size:13px;font-weight:700}
#wm{position:fixed;inset:0;display:none;align-items:center;justify-content:center;pointer-events:none;font-size:220px;font-weight:700;
color:rgba(232,163,61,.10);transform:rotate(-14deg);direction:ltr}#wm.on{display:flex}
footer{color:var(--muted);font-size:14px;display:flex;gap:18px}
</style></head><body>
<header><h1>کنکورِ <em>هوش مصنوعی</em> · هومودین</h1><span class="badge" id="mode">…</span><span id="clock">00:00</span></header>
<div id="lanes"></div>
<footer><span>درصد با نمرهٔ منفیِ یک‌سوم · هر مدل یک سؤال در هر درخواست، همه هم‌زمان</span><span id="pricenote"></span><span id="link">● …</span></footer>
<div id="cards"></div><div id="wm">MOCK</div>
<script>
const P=p=>p===null||p===undefined?'—':(p<0?'منفی '+F(Math.abs(p).toFixed(0)):F(p.toFixed(0)))+'٪';
const F=n=>String(n).replace(/[0-9]/g,d=>'۰۱۲۳۴۵۶۷۸۹'[d]).replace(/\\./g,'٫'),$=s=>document.querySelector(s);
const SUBJ={bio:'زیست',chem:'شیمی',phys:'فیزیک',math:'ریاضی',geo:'زمین',other:'سایر'},GRP={tajrobi:'گروه تجربی',riazi:'گروه ریاضی'},CARDS_NOW=location.search.includes('cards');
let S={},slots=[],speed=1,clockT=0,clockAt=performance.now(),ended=false,place=0,nq=0;
const mmss=s=>{s=Math.max(0,s);const m=Math.floor(s/60),x=Math.floor(s%60);return String(m).padStart(2,'0')+':'+String(x).padStart(2,'0')};
const pct=l=>{const sc=l.filter(x=>x!==null);if(!sc.length)return null;let v=0;for(const x of sc)v+=x==='correct'?1:x==='wrong'?-1/3:0;return 100*v/sc.length};
function lane(s){const d=document.createElement('div');d.className='lane';d.id='L'+s.slot;
d.innerHTML=`<div class="name"><b>${s.label}</b><small>${s.model}</small></div><div class="timer"><b>00.0</b><small>کل: <span class="tot">00:00</span></small></div>
<div class="q"><b>آماده</b><small class="qs"></small><div class="bar"><i></i></div></div>
<div class="tok"><div><span>in</span> <span class="ti">0</span></div><div><span>out</span> <span class="to">0</span> <span>· think</span> <span class="tr">0</span></div><div class="usd">$ —</div></div>
<div class="subj"></div><span class="place"></span>`;return d}
function tick(){const now=performance.now();const t=clockT+(now-clockAt)/1000*speed;if(!ended)$('#clock').textContent=mmss(t);
for(const k in S){const x=S[k];if(x.askT!==null&&!x.done){const e=Math.max(0,t-x.askT);x.el.querySelector('.timer b').textContent=e.toFixed(1)}}
for(const k in S){const x=S[k];for(const f of ['ti','to','tr','usd']){const c=x.shown[f],g=x.tot[f];if(c!==g){const n=c+(g-c)*0.18;x.shown[f]=Math.abs(g-n)<(f==='usd'?0.0005:1)?g:n;
const el=x.el.querySelector(f==='usd'?'.usd':'.'+f);el.textContent=f==='usd'?(x.usdKnown?'$'+x.shown.usd.toFixed(3):'$ —'):Math.round(x.shown[f]).toLocaleString('en')}}}
requestAnimationFrame(tick)}
function subjects(x){const ex=x.cur;if(!ex)return;const by={};for(const r of x.rows)if(r.year===ex.year&&r.group===ex.group)(by[r.subject]=by[r.subject]||[]).push(r.label);
x.el.querySelector('.subj').innerHTML=Object.entries(by).map(([s,l])=>{const p=pct(l);return `<i>${SUBJ[s]} <b>${P(p)}</b></i>`}).join('')}
function on(ev){if(ev.t!==undefined){clockT=ev.t;clockAt=performance.now()}
if(ev.type==='start'){slots=ev.slots;speed=ev.speed||1;nq=ev.questions.length;$('#lanes').innerHTML='';S={};place=0;ended=false;$('#cards').classList.remove('on');$('#cards').innerHTML='';
const m=ev.mode;$('#mode').textContent=m==='mock'?'MOCK · ساختگی':m==='replay'?(speed===1?'بازپخش · زمان واقعی':'بازپخش · ×'+F(speed)):'زنده';
$('#wm').classList.toggle('on',m==='mock'||slots.some(s=>s.model.startsWith('mock:')));$('#pricenote').textContent=ev.prices_checked_on?('قیمت‌ها: '+ev.prices_checked_on):(m==='mock'?'$ = سقف ساختگی (MOCK)':'$ فقط برای OpenRouter؛ prices.json خالی است');
for(const s of slots){const el=lane(s);$('#lanes').appendChild(el);S[s.slot]={el,askT:null,rows:[],tot:{ti:0,to:0,tr:0,usd:0},shown:{ti:0,to:0,tr:0,usd:0},usdKnown:true,cur:null,done:false}}}
if(ev.type==='end'){ended=true;$('#clock').textContent=mmss(ev.t);setTimeout(()=>$('#cards').classList.add('on'),CARDS_NOW?0:1500);return}
const x=S[ev.slot];if(!x)return;
if(ev.type==='ask'){x.askT=ev.t;x.cur={year:ev.year,group:ev.group};x.el.querySelector('.q b').textContent=`${F(ev.year)} · ${GRP[ev.group]} · ${SUBJ[ev.subject]} · سؤال ${F(ev.number)}`;
x.el.querySelector('.qs').textContent=`${F(ev.i+1)} از ${F(nq)}`;x.el.querySelector('.bar i').style.width=(100*ev.i/nq)+'%';subjects(x)}
if(ev.type==='answer'){x.rows.push(ev);x.cur={year:ev.year,group:ev.group};x.tot.ti+=ev.input_tokens;x.tot.to+=ev.output_tokens;x.tot.tr+=ev.reasoning_tokens||0;
if(ev.usd===null||ev.usd===undefined)x.usdKnown=false;else x.tot.usd+=ev.usd;let tot=0;for(const r of x.rows)tot+=r.latency_s;x.el.querySelector('.tot').textContent=mmss(tot);
x.el.querySelector('.bar i').style.width=(100*(ev.i+1)/nq)+'%';x.el.querySelector('.timer b').textContent=ev.latency_s.toFixed(1);x.askT=null;
const c=ev.label==='correct'?'flash-ok':ev.label==='wrong'?'flash-bad':'';if(c&&!ev.resumed){x.el.classList.add(c);setTimeout(()=>x.el.classList.remove(c),450)}subjects(x)}
if(ev.type==='error'){x.el.querySelector('.qs').textContent='خطای API · بعداً دوباره'}
if(ev.type==='done'){x.done=true;place++;x.el.classList.add('done');x.el.querySelector('.place').textContent=F(place);x.el.querySelector('.q b').textContent='تمام شد'}
if(ev.type==='karnameh')card(ev)}
function card(k){const s=slots.find(s=>s.slot===k.slot);const d=document.createElement('div');d.className='card';d.id='C'+k.slot;
const ys=[...new Set(k.exams.map(e=>e.year))].sort(),gs=['tajrobi','riazi'].filter(g=>k.exams.some(e=>e.group===g));
const cell=(y,g)=>{const e=k.exams.find(e=>e.year===y&&e.group===g);return e?P(e.weighted):'—'};
const tbl=`<table><tr><td></td>${gs.map(g=>`<td>${GRP[g]}</td>`).join('')}</tr>${ys.map(y=>`<tr><td>${F(y)}</td>${gs.map(g=>`<td><b>${cell(y,g)}</b></td>`).join('')}</tr>`).join('')}</table>`;
const last=k.exams.filter(e=>e.year===Math.max(...ys));
d.innerHTML=`<h2>${s.label}</h2><div class="big">${P(k.percent)}</div><small>درصد کل با منفی · ${mmss(k.total_s)} · ${k.tokens.toLocaleString('en')} توکن · ${k.usd===null?'$ —':'$'+F(k.usd)}</small>${tbl}
<small>درصد هر آزمون با ضریب درس‌ها</small>${last.map(e=>`<div class="est"><span class="est-tag">تخمین · ESTIMATE</span> ${F(e.year)} ${GRP[e.group]}: <b>${e.range_fa}</b></div>`).join('')}
<div class="est">فقط اگر سوابق تحصیلی نزدیک کامل باشد؛ با معدل متوسط بازه‌ای نمی‌شود گفت. منبع رتبه‌ها کم‌اعتبار است؛ هیچ قبولی‌ای ادعا نمی‌شود.</div>`;
$('#cards').appendChild(d)}
function connect(){const es=new EventSource('/events');es.onopen=()=>$('#link').textContent='● وصل';es.onerror=()=>$('#link').textContent='○ قطع';es.onmessage=e=>{try{on(JSON.parse(e.data))}catch(err){console.error(err)}}}
connect();requestAnimationFrame(tick);addEventListener('keydown',e=>{if(e.key==='k')$('#cards').classList.toggle('on')});
</script></body></html>"""


def page():
    return PAGE.replace('%FONTS%', font_css())


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
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--mock', action='store_true')
    g.add_argument('--live', action='store_true')
    g.add_argument('--replay', metavar='RUN')
    g.add_argument('--selftest', action='store_true')
    ap.add_argument('--speed', type=float, default=1.0, help='replay speed (1 = true timing)')
    ap.add_argument('--session', type=int, help='replay: which events-N.jsonl (default: the longest)')
    ap.add_argument('--delay', type=float, default=0.25, help='mock: seconds of wall time per simulated second')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--no-browser', action='store_true')
    ap.add_argument('--hold', type=float, default=None, help='exit this many seconds after the end (default: stay)')
    for a in ('--model', '--exam'):
        ap.add_argument(a, action='append')
    ap.add_argument('--limit', type=int)
    ap.add_argument('--run')
    ap.add_argument('--yes', action='store_true')
    ap.add_argument('--no-schema', action='store_true')
    ap.add_argument('--per-subject', type=int, default=4)
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.mock or args.live or args.replay):
        ap.print_help()
        return 0
    if args.replay:
        out = kcore.private_dir() / 'runs' / args.replay
        evs = sorted(out.glob('events-*.jsonl'), key=lambda p: p.stat().st_size)
        if not evs:
            sys.exit(f'no events in {out}')
        path = out / f'events-{args.session}.jsonl' if args.session else evs[-1]
        board, job = Board(HUB, 'replay', args.speed), None
        job = lambda: replay(path, board, args.speed)
    else:
        args.mock, args.synthetic = bool(args.mock), bool(args.mock)
        sl, qs = konkur_run.slots(args), konkur_run.questions(args)
        out = konkur_run.run_dir(args, sl) if args.live else kcore.private_dir() / 'runs' / f'live-mock-{time.strftime("%H%M%S")}'
        if args.live:
            print('\n'.join(konkur_run.plan_lines(sl, qs)))
            if not args.yes and input('This spends API money. Continue? [y/N] ').strip().lower() != 'y':
                return 1
        board = Board(HUB, 'mock', 1 / args.delay, tscale=1 / args.delay) if args.mock else Board(HUB, 'live')
        job = lambda: konkur_run.run_exam(sl, qs, out, on_event=board, use_schema=not args.no_schema,
                                          delay=args.delay if args.mock else 0.0)
    srv = serve(args.port)
    url = f'http://127.0.0.1:{args.port}/'
    print(f'scoreboard: {url}  (record at 1600×900; key K toggles the کارنامه cards; {url}?cards opens them at once)')
    if not args.no_browser:
        webbrowser.open(url)
        time.sleep(1.5)
    job()
    print('run finished' + (f'; events in {out}' if not args.replay else ''))
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


def selftest():
    import os
    import tempfile
    import urllib.request
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['KONKUR_PRIVATE'] = tmp
        try:
            assert konkur_run.main(['run', '--mock', '--synthetic', '--per-subject', '2', '--yes', '--run', 'synthetic-x']) == 0
            hub = Hub()
            board = Board(hub, 'replay', 1000.0)
            replay(Path(tmp) / 'runs/synthetic-x/events-1.jsonl', board, 1000.0)
            kinds = [e['type'] for e in hub.history]
            assert kinds[0] == 'start' and kinds[-1] == 'end' and kinds.count('karnameh') == 5, kinds[-8:]
            k = next(e for e in hub.history if e['type'] == 'karnameh')
            assert k['exams'] and all('تخمین' in e['estimate_fa'] for e in k['exams'])
            assert all(e['usd'] is None for e in hub.history if e['type'] == 'answer'), 'replay must not invent $'
            mock = Board(Hub(), 'mock')
            mock({'type': 'answer', 'slot': 'a', 'label': 'correct', 'input_tokens': 1000, 'output_tokens': 1000,
                  'model': 'mock:a', 'latency_s': 1, 'year': 1405, 'group': 'riazi', 'subject': 'math'})
            assert mock.hub.history[0]['usd'] > 0, 'mock shows a labelled bound'
            global HUB
            HUB = hub
            srv = serve(0)
            port = srv.server_address[1]
            html = urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=5).read().decode()
            assert 'dir="rtl"' in html and 'MOCK' in html and 'EventSource' in html and 'Vazirmatn' in html
            st = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{port}/state', timeout=5).read())
            assert len(st) == len(hub.history)
            r = urllib.request.urlopen(f'http://127.0.0.1:{port}/events', timeout=5)
            first = [r.readline() for _ in range(4)]
            assert any(b'"type": "start"' in x for x in first), first
            r.close()
            srv.shutdown()
        finally:
            os.environ.pop('KONKUR_PRIVATE', None)
    print('konkur_live selftest passed (replay, کارنامه events, no invented $, page, /state, SSE)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
