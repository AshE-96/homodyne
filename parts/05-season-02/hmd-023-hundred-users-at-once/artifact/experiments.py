"""experiments.py — the HMD-023 experiments: simulate (fake service, runs now) and run (Ollama on this laptop).

Results land in artifact/results/:
    simulated/                     committed; every file says SIMULATED SERVICE (ILLUSTRATIVE)
    runs/<date>-<target>-<model>/  one folder per real run ([RUN] in the script until it exists)
"""
import asyncio
import datetime as dt
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import urllib.request
from pathlib import Path

import charts
import dashboard
import loadgen
from metrics import summarize, capacity_from_open

HERE = Path(__file__).resolve().parent
RESULTS = HERE / 'results'

SIM = dict(slots=4, prefill_tps=600.0, decode_tps=80.0, contention=0.10, cold_load=4.0, max_queue=512,
           degrade_at=0, degrade_tokens=40)
LOAD = dict(in_range=(80, 240), out_range=(40, 200), think=20.0, duration=120.0, ramp=10.0, timeout=30.0,
            slo_ttft=3.0, sample_every=0.5)
RAMP_USERS = [1, 10, 25, 50, 100]
OPEN_RATES = [0.5, 1.0, 1.25, 1.5, 1.75, 2.0]
POLICIES = [('baseline', {}),
            ('bounded queue (4)', {'max_queue': 4}),
            ('bounded queue + short answers', {'max_queue': 4, 'degrade_at': 2}),
            ('double slots, same hardware (sim)', {'slots': 8})]
LABEL_SIM = 'SIMULATED SERVICE (ILLUSTRATIVE)'

# The protocol the script's [RUN] lines (beats 10 and 11) were written for. Locked before any real run;
# its SHA-256 goes into meta.json, and `report` refuses to print spoken lines for a run that differs.
RUN_PROTOCOL = {'slo_first_word_s': 3.0, 'slo_share': 0.95, 'slo_max_fail': 0.01, 'no_think': False,
                'prompt_template': loadgen.PROMPT_TEMPLATE, 'prompts_sha256': None,
                'percentile': 'nearest-rank p95 over every sent request; timeouts and 503 count as misses',
                'users': [1, 10, 50, 100], 'duration_s': 120.0, 'think_mean_s': 20.0, 'ramp_s': 10.0,
                'timeout_s': 30.0, 'max_tokens': 160, 'cold_tries': 3, 'model': 'qwen2.5:1.5b'}


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def run_locked(a, users, model):
    """The protocol this run actually used, in RUN_PROTOCOL's shape, plus the prompts' hash."""
    return {'slo_first_word_s': LOAD['slo_ttft'], 'slo_share': 0.95, 'slo_max_fail': 0.01,
            'percentile': RUN_PROTOCOL['percentile'], 'users': users, 'duration_s': a.duration,
            'think_mean_s': a.think, 'ramp_s': LOAD['ramp'], 'timeout_s': a.timeout, 'max_tokens': a.max_tokens,
            'cold_tries': a.cold_tries, 'model': model, 'no_think': a.no_think,
            'prompt_template': loadgen.PROMPT_TEMPLATE, 'prompts_sha256': sha(loadgen.PROMPTS_FA)}


RUN_PROTOCOL['prompts_sha256'] = sha(loadgen.PROMPTS_FA)
PROTOCOL_FILE = HERE / 'protocol.json'


def protocol_file_ok():
    """protocol.json (committed before the real run) must equal RUN_PROTOCOL."""
    try:
        return json.loads(PROTOCOL_FILE.read_text(encoding='utf-8')).get('protocol') == RUN_PROTOCOL
    except (OSError, ValueError):
        return False


def protocol_diff(locked):
    return {k: (locked.get(k), v) for k, v in RUN_PROTOCOL.items() if locked.get(k) != v}


# ── fake server process ───────────────────────────────────────────────────
class FakeServer:
    """Start fake_server.py on 127.0.0.1 in its own process; always stopped on exit."""

    def __init__(self, timescale, **params):
        self.params = {**SIM, **params}
        self.timescale = timescale

    def __enter__(self):
        args = [sys.executable, '-I', str(HERE / 'fake_server.py'), '--port', '0', '--timescale', str(self.timescale)]
        for k, v in self.params.items():
            args += ['--' + k.replace('_', '-'), str(v)]
        self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, text=True)
        line = self.proc.stdout.readline().split()
        if len(line) != 3 or line[0] != 'LISTENING':
            self.__exit__()
            raise RuntimeError('fake server did not start')
        self.host, self.port = line[1], int(line[2])
        return self

    def __exit__(self, *exc):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        return False


# ── helpers ───────────────────────────────────────────────────────────────
def hardware():
    def sysctl(k):
        try:
            return subprocess.run(['sysctl', '-n', k], capture_output=True, text=True, timeout=3).stdout.strip()
        except Exception:
            return ''
    ram = sysctl('hw.memsize')
    power = ''
    try:
        power = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=3).stdout.split('\n')[0]
    except Exception:
        pass
    return {'chip': sysctl('machdep.cpu.brand_string') or platform.processor(), 'ram_gb': round(int(ram) / 2**30) if ram else None,
            'os': platform.platform(), 'python': platform.python_version(), 'power': power.strip()}


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str), encoding='utf-8')


async def staged(cfg, clock, live, stages, slots=None):
    """stages: list of (label, users, rate, seed). Runs them back to back with the dashboard on."""
    stop = asyncio.Event()
    dash = asyncio.ensure_future(dashboard.run(live, cfg, stop))
    rows, timeline, allrecs = [], [], []
    try:
        for label, users, rate, seed in stages:
            recs, samples, window = await loadgen.run_stage(cfg, clock, live, label, users=users, rate=rate, seed=seed)
            row = summarize(recs, cfg['duration'], cfg['slo_ttft'], slots=slots, samples=samples,
                            timeout=cfg['timeout'], window=window)
            row.update({'stage': label, 'users': users, 'rate': rate})
            row['machine_s_per_success'] = window / row['ok'] if row['ok'] else None
            live.history.append((label, row))
            rows.append(row)
            timeline.append((label, samples))
            allrecs += recs
            await clock.sleep(5)
    finally:
        stop.set()
        await dash
    return rows, timeline, allrecs


async def warm_once(cfg, clock, live, n=1):
    """One request whose numbers are not kept (load the model / connection before measuring)."""
    recs = []
    for _ in range(n):
        cfg['_rid'] = cfg.get('_rid', 0) + 1
        recs.append(await loadgen.one_request(cfg, clock, live, cfg['_rid'], None, 'warmup', random.Random(1)))
    return recs


def timeline_rows(timeline):
    return [{'stage': st, **s} for st, samples in timeline for s in samples]


def write_summary_md(path, title, label, meta, cold, ramp, open_rows=None, policies=None, capacity=None):
    f = lambda x: '-' if x is None else ('>timeout' if x == float('inf') else f'{x:.2f}')
    pc = lambda x: '-' if x is None else f'{x:.0%}'
    L = [f'# {title}', '', f'**{label}**', '',
         f'- date: {meta["date"]}', f'- target: {meta["target"]}', f'- hardware: {meta["hardware"]}',
         f'- load pattern: {json.dumps(meta["load"], ensure_ascii=False)}', '']
    if meta.get('service'):
        L += [f'- simulated service parameters: {json.dumps(meta["service"])}', f'- timescale: {meta.get("timescale")}', '']
    if cold:
        L += ['## Cold vs warm (first word, seconds)', '', '| try | cold | warm |', '|---|---|---|']
        L += [f'| {i + 1} | {f(c)} | {f(w)} |' for i, (c, w) in enumerate(zip(cold['cold_all'], cold['warm_all']))]
        L += ['', f'cold (try 1) {f(cold["cold_ttft"])} s · median warm {f(cold["warm_ttft"])} s · '
              'on a real laptop only try 1 is truly cold from disk; tries 2-3 may hit the OS file cache', '']
    head = ('| load | sent | ok | timeout (of which first word seen) | busy 503 | first word p50 | p95 | full answer p50 | p95 | '
            'within SLO | SLO | answers/s (real span) | span s | mean waiting | max streaming |')
    rule = '|' + '---|' * 15

    def line(lbl, r):
        return (f'| {lbl} | {r["sent"]} | {r["ok"]} | {r["timeout"]} ({r["timeout_after_first_word"]}) | {r["rejected"]} | '
                f'{f(r["ttft_p50"])} | {f(r["ttft_p95"])} | {f(r["e2e_p50"])} | {f(r["e2e_p95"])} | {pc(r["slo_good_share"])} | '
                f'{"kept" if r["slo_met"] else "broken"} | {f(r["throughput_rps"])} | {f(r.get("span_s"))} | '
                f'{f(r.get("mean_waiting"))} | {r.get("max_streaming", "-")} |')
    L += ['## Closed loop: virtual users', '', head, rule] + [line(f'{r["users"]} users', r) for r in ramp] + ['']
    if open_rows:
        L += ['## Open loop: requests per second', '', head, rule] + [line(f'{r["rate"]:g} req/s', r) for r in open_rows]
        L += ['', f'Highest arrival rate that kept the SLO: {capacity} req/s', '']
        L += ['Little\'s law check (L = lambda x W, over each stage window):', '',
              '| load | L measured | lambda x W |', '|---|---|---|']
        L += [f'| {r["rate"]:g} req/s | {f(r.get("little_L_measured"))} | {f(r.get("little_lambda_W"))} |' for r in open_rows]
        L += ['']
    if policies:
        L += ['## 100 users, four policies (chosen by us; the fake service and its slot contention are a model, not a measurement)', '',
              '| policy | sent | ok | busy 503 | timeout (of which first word seen) | within SLO | first word p95 | first word p95, answered only | '
              'answers/s (real span) | mean answer tokens | shortened | slot-seconds per success |',
              '|---|---|---|---|---|---|---|---|---|---|---|---|']
        L += [f'| {p["policy"]} | {p["sent"]} | {p["ok"]} | {p["rejected"]} | {p["timeout"]} ({p["timeout_after_first_word"]}) | '
              f'{pc(p["slo_good_share"])} | {f(p["ttft_p95"])} | {f(p["ttft_p95_ok_only"])} | {f(p["throughput_rps"])} | '
              f'{f(p["mean_out_tokens"])} | {pc(p["degraded_share"])} | {f(p.get("slot_s_per_success"))} |' for p in policies]
    path.write_text('\n'.join(L) + '\n', encoding='utf-8')


def base_cfg(host, port, simulated, **kw):
    return {**LOAD, 'host': host, 'port': port, 'simulated': simulated, **kw}


# ── simulate: the fake service, runs now ─────────────────────────────────
async def _simulate(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    k = a.timescale
    clock = loadgen.Clock(k)
    users = a.users or RAMP_USERS
    rates = a.rates or OPEN_RATES
    load = {**LOAD, 'duration': a.duration}
    meta = {'label': LABEL_SIM, 'date': dt.datetime.now().isoformat(timespec='seconds'), 'target': 'fake_server.py on 127.0.0.1',
            'hardware': hardware(), 'service': SIM, 'timescale': k, 'load': load, 'ramp_users': users, 'open_rates': rates,
            'policies': POLICIES, 'slo': 'first word within 3 s for 95% of requests, fewer than 1% failed'}
    meta['config_sha256'] = sha({'service': SIM, 'load': load, 'users': users, 'rates': rates, 'policies': POLICIES})
    # 1. cold vs warm: a fresh server each try
    cold_all, warm_all = [], []
    for i in range(3):
        with FakeServer(k) as s:
            cfg = base_cfg(s.host, s.port, True, **load, slots=SIM['slots'], no_dash=True)
            live = loadgen.Live('fake', True, cfg['slo_ttft'], cfg['timeout'])
            c, w = await warm_once(cfg, clock, live, 2)
            cold_all.append(c['t_first'] - c['t_send'])
            warm_all.append(w['t_first'] - w['t_send'])
    cold = {'cold_all': cold_all, 'warm_all': warm_all, 'cold_ttft': cold_all[0], 'warm_ttft': sorted(warm_all)[1],
            'note': 'cold_ttft = try 1; every try restarts the fake server'}
    # 2. closed loop ramp, one warm server
    with FakeServer(k) as s:
        cfg = base_cfg(s.host, s.port, True, **load, slots=SIM['slots'], no_dash=a.no_dash)
        live = loadgen.Live('fake', True, cfg['slo_ttft'], cfg['timeout'])
        await warm_once(cfg, clock, live)
        ramp, tl_ramp, recs_ramp = await staged(cfg, clock, live, [(f'{u} users', u, None, u) for u in users], slots=SIM['slots'])
    # 3. open loop sweep
    with FakeServer(k) as s:
        cfg = base_cfg(s.host, s.port, True, **load, slots=SIM['slots'], no_dash=a.no_dash)
        live = loadgen.Live('fake', True, cfg['slo_ttft'], cfg['timeout'])
        await warm_once(cfg, clock, live)
        open_rows, tl_open, recs_open = await staged(cfg, clock, live, [(f'{r:g} req/s', None, r, 42) for r in rates],
                                                     slots=SIM['slots'])
    capacity = capacity_from_open(open_rows, LOAD['slo_ttft'])
    # 4. policies at 100 users
    policies, recs_pol = [], []
    for name, params in ([] if a.skip_policies else POLICIES):
        with FakeServer(k, **params) as s:
            slots = params.get('slots', SIM['slots'])
            cfg = base_cfg(s.host, s.port, True, **load, slots=slots, no_dash=a.no_dash)
            live = loadgen.Live('fake', True, cfg['slo_ttft'], cfg['timeout'])
            await warm_once(cfg, clock, live)
            rows, _, recs = await staged(cfg, clock, live, [(name, 100, None, 100)], slots=slots)
            rows[0]['policy'] = name
            policies += rows
            recs_pol += [{**r, 'stage': name} for r in recs]
    # write
    charts.write_csv(out / 'stages.csv', [{'experiment': 'closed', **r} for r in ramp] + [{'experiment': 'open', **r} for r in open_rows])
    charts.write_csv(out / 'policies.csv', policies)
    charts.write_csv(out / 'timeline.csv', timeline_rows(tl_ramp) + timeline_rows(tl_open))
    charts.write_csv(out / 'requests.csv', recs_ramp + recs_open + recs_pol)
    charts.write_csv(out / 'cold.csv', [{'try': i + 1, 'cold_ttft_s': c, 'warm_ttft_s': w} for i, (c, w) in enumerate(zip(cold_all, warm_all))])
    meta['capacity_rps_within_slo'] = capacity
    dump(out / 'meta.json', meta)
    dump(out / 'results.json', {'label': LABEL_SIM, 'cold': cold, 'ramp': ramp, 'open': open_rows, 'policies': policies,
                                'capacity_rps_within_slo': capacity})
    made = charts.charts(out, LABEL_SIM, ramp=ramp, timeline=tl_ramp, open_rows=open_rows, policies=policies,
                         slo=LOAD['slo_ttft'], timeout=LOAD['timeout'])
    write_summary_md(out / 'summary.md', 'HMD-023 · simulated service results', LABEL_SIM, meta, cold, ramp, open_rows, policies, capacity)
    return out, made


def replot(out):
    """Redraw the charts of an existing simulate folder from results.json and timeline.csv (no new run)."""
    import csv
    res = json.loads((out / 'results.json').read_text(encoding='utf-8'))
    tl = {}
    with open(out / 'timeline.csv', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['stage'].endswith('users'):
                tl.setdefault(r['stage'], []).append({'t': float(r['t']), 'waiting': int(r['waiting'])})
    return charts.charts(out, res['label'], ramp=res['ramp'], timeline=list(tl.items()), open_rows=res['open'],
                         policies=res['policies'], slo=LOAD['slo_ttft'], timeout=LOAD['timeout'])


def simulate(a):
    if a.replot:
        print('charts:', ', '.join(replot(Path(a.out))))
        return
    out, made = asyncio.run(_simulate(a))
    print((out / 'summary.md').read_text(encoding='utf-8'))
    print('charts:', ', '.join(made))
    print(f'written to {out}')


# ── run: a real Ollama on this computer ([RUN]) ───────────────────────────
SETUP = """Ollama is not reachable at {url}. Nothing was loaded.

Set it up once (the owner does this; about 1 GB download in step 3):
  1. Install Ollama for macOS from https://ollama.com/download and open the app once.
  2. Choose how many requests it serves at the same time, and write the number down:
       launchctl setenv OLLAMA_NUM_PARALLEL 4
     then quit Ollama from the menu bar and open it again.
     (Or, in a terminal instead of the app:  OLLAMA_NUM_PARALLEL=4 ollama serve)
  3. Pull the small model (qwen2.5:1.5b · 986 MB · Apache 2.0 · checked on ollama.com 23 Nov 2026):
       ollama pull qwen2.5:1.5b
  4. Check it answers:   ollama run qwen2.5:1.5b "سلام"      then   ollama ps
  5. Plug in the charger, close heavy apps, then run again:
       python3 {me} run --target ollama --num-parallel 4
"""


def _get(url, timeout=3):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _post(url, obj, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def default_model():
    sys.path.insert(0, str(HERE.parents[3] / 'tools'))
    try:
        import llm                                   # HOMODYNE_MODEL=ollama:<model> picks the model
        prov, model = llm.resolve('main')
        return model if prov == 'ollama' else None
    except Exception:
        return None


async def _run(a):
    k = 1.0
    clock = loadgen.Clock(k)
    users = a.users or [1, 10, 50, 100]
    load = {**LOAD, 'duration': a.duration, 'think': a.think, 'timeout': a.timeout,
            'out_range': (a.max_tokens, a.max_tokens)}   # fake target: same answer cap as the real run
    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M')
    hw = hardware()
    if a.target == 'fake':
        server = FakeServer(k)
        server.__enter__()
        host, port, model, version = server.host, server.port, 'fake', 'homodyne-fake-1'
    else:
        server = None
        host, port = loadgen.parse_ollama_host(os.environ.get('OLLAMA_HOST'))   # refuses anything but loopback
        hh = f'[{host}]' if ':' in host else host
        url = f'http://{hh}:{port}'
        me = Path(sys.argv[0]).as_posix()
        try:
            version = _get(f'{url}/api/version')['version']
            tags = _get(f'{url}/api/tags')
        except Exception:
            print(SETUP.format(url=url, me=me))
            return None
        model = a.model or default_model() or 'qwen2.5:1.5b'
        found = [m for m in tags.get('models', []) if m.get('name') == model or m.get('model') == model]
        if not found:
            print(f'Ollama {version} is running, but {model} is not pulled. Run:  ollama pull {model}\n'
                  f'Pulled models: {[m.get("name") for m in tags.get("models", [])]}')
            return None
        if a.num_parallel is None:
            print('Warning: --num-parallel not given. Pass the OLLAMA_NUM_PARALLEL value you set, so the run records it.')
        minutes = len(users) * (a.duration + a.timeout + 5) / 60 + 1.5
        print(f'This loads Ollama {version} on {host}:{port} with {model}: stages {users} users, '
              f'{a.duration:.0f}s each, about {minutes:.0f} minutes. Fans may spin up.\n'
              f'Cost estimate (upper bound): $0.00 in API fees: no API is called, only 127.0.0.1. '
              f'Electricity and wear are not counted.')
        if not a.yes and input('Continue? [y/N] ').strip().lower() != 'y':
            return None
    try:
        cfg = base_cfg(host, port, a.target == 'fake', **load, model=model, max_tokens=a.max_tokens,
                       num_parallel=a.num_parallel, no_dash=a.no_dash, no_think=a.no_think,
                       slots=SIM['slots'] if a.target == 'fake' else None)
        live = loadgen.Live(a.target, a.target == 'fake', cfg['slo_ttft'], cfg['timeout'])
        meta = {'label': LABEL_SIM if a.target == 'fake' else 'REAL RUN', 'date': dt.datetime.now().isoformat(timespec='seconds'),
                'target': f'{a.target} {host}:{port}', 'model': model, 'ollama_version': version,
                'num_parallel': a.num_parallel, 'no_think': a.no_think, 'hardware': hw, 'load': {**load, 'max_tokens': a.max_tokens}, 'users': users,
                'prompts': 'loadgen.PROMPTS_FA, request number first (no shared prefix)',
                'prompts_sha256': sha(loadgen.PROMPTS_FA)}
        meta['locked'] = run_locked(a, users, model)
        meta['locked_sha256'] = sha(meta['locked'])
        meta['protocol_sha256'] = sha(RUN_PROTOCOL)
        meta['protocol_diff'] = {k: list(v) for k, v in protocol_diff(meta['locked']).items()}
        if meta['protocol_diff'] and a.target == 'ollama':
            print(f'Note: this run differs from the locked protocol {meta["protocol_diff"]}; '
                  'report will not print spoken lines for it.')
        if server is None:
            digest = [m.get('digest', '')[:12] for m in tags.get('models', []) if m.get('name') == model]
            meta['model_digest'] = digest[0] if digest else ''
        # cold vs warm: unload, then one request (cold) and one more (warm); three times
        cold_all, warm_all, loads = [], [], []
        for _ in range(a.cold_tries):
            if server is None:
                _post(f'{url}/api/generate', {'model': model, 'keep_alive': 0})
                await asyncio.sleep(3)
            else:
                server.__exit__()
                server = FakeServer(k)
                server.__enter__()
                cfg['port'] = server.port
            c, w = await warm_once(cfg, clock, live, 2)
            cold_all.append(c['t_first'] - c['t_send'] if c['t_first'] else float('inf'))
            warm_all.append(w['t_first'] - w['t_send'] if w['t_first'] else float('inf'))
            loads.append(c.get('load_s'))
        cold = {'cold_all': cold_all, 'warm_all': warm_all, 'load_s_reported': loads,
                'cold_ttft': cold_all[0], 'warm_ttft': sorted(warm_all)[len(warm_all) // 2],
                'note': 'cold_ttft = try 1, the only one truly cold from disk; tries 2-3 may hit the OS file cache'}
        ramp, tl, recs = await staged(cfg, clock, live, [(f'{u} users', u, None, u) for u in users], slots=cfg.get('slots'))
    finally:
        if server is not None:
            server.__exit__()
    out = RESULTS / 'runs' / f'{stamp}-{a.target}-{model.replace(":", "_").replace("/", "_")}'
    out.mkdir(parents=True, exist_ok=True)
    dump(out / 'meta.json', meta)
    meta['observed_max_streaming'] = max((r.get('max_streaming') or 0) for r in ramp)
    if a.num_parallel and meta['observed_max_streaming'] != a.num_parallel:
        meta['concurrency_warning'] = (f'--num-parallel {a.num_parallel} but at most {meta["observed_max_streaming"]} '
                                       'answers streamed at once; the server setting may differ')
        print('WARNING:', meta['concurrency_warning'])
    dump(out / 'meta.json', meta)
    dump(out / 'results.json', {'label': meta['label'], 'cold': cold, 'ramp': ramp})
    charts.write_csv(out / 'stages.csv', ramp)
    charts.write_csv(out / 'timeline.csv', timeline_rows(tl))
    charts.write_csv(out / 'requests.csv', recs)
    label = meta['label'] if a.target == 'fake' else f'REAL RUN · {model} · {hw.get("chip")} {hw.get("ram_gb")} GB'
    charts.charts(out, label, ramp=ramp, timeline=tl, slo=LOAD['slo_ttft'], timeout=a.timeout)
    write_summary_md(out / 'summary.md', f'HMD-023 · run {stamp}', label, meta, cold, ramp)
    return out


def run(a):
    out = asyncio.run(_run(a))
    if not out:
        return 1
    if out:
        print((out / 'summary.md').read_text(encoding='utf-8'))
        print(f'written to {out}\nnext:  python3 {Path(sys.argv[0]).as_posix()} report')
