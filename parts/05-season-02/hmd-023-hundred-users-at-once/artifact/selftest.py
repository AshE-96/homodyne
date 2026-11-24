"""selftest.py — checks the whole lab against the fake service only (no model, no network, under 60 s).

    python3 load_lab.py --selftest
"""
import asyncio
import socket
import sys
import tempfile
import time
from pathlib import Path

import charts
import experiments
import loadgen
import spoken
from metrics import pct, summarize, INF

K = 0.1   # ten times faster than real time
results = []


def check(name, ok, detail=''):
    results.append(ok)
    print(f'{"PASS" if ok else "FAIL"}  {name}' + (f'  ({detail})' if detail else ''))


def cfg_for(s, **kw):
    return experiments.base_cfg(s.host, s.port, True, **{**experiments.LOAD, 'no_dash': True, 'slots': s.params['slots'], **kw})


async def main_async():
    clock = loadgen.Clock(K)
    # cold vs warm
    with experiments.FakeServer(K) as s:
        check('fake server binds 127.0.0.1 only', s.host == '127.0.0.1', f'{s.host}:{s.port}')
        cfg = cfg_for(s)
        live = loadgen.Live('fake', True, 3.0, 30.0)
        c, w = await experiments.warm_once(cfg, clock, live, 2)
        tc, tw = c['t_first'] - c['t_send'], w['t_first'] - w['t_send']
        check('cold request waits for the model load (4 s simulated)', tc >= 3.9, f'cold {tc:.2f}s')
        check('warm request starts fast', tw < 1.0, f'warm {tw:.2f}s')
        proc, port = s.proc, s.port
    check('fake server process stopped', proc.poll() is not None)
    sock = socket.socket()
    sock.settimeout(0.5)
    check('port closed after stop', sock.connect_ex(('127.0.0.1', port)) != 0)
    sock.close()

    # closed loop: 1 user vs 40 users
    with experiments.FakeServer(K) as s:
        cfg = cfg_for(s, duration=40.0)
        live = loadgen.Live('fake', True, 3.0, 30.0)
        await experiments.warm_once(cfg, clock, live)
        rows, tl, recs = await experiments.staged(cfg, clock, live, [('1 user', 1, None, 1), ('40 users', 40, None, 40)], slots=4)
    r1, r40 = rows
    check('1 user keeps the SLO', r1['slo_met'], f'n={r1["sent"]}, p95 {r1["ttft_p95"]:.2f}s')
    check('40 users break the SLO (more arrivals than 4 slots can serve)', not r40['slo_met'],
          f'n={r40["sent"]}, within SLO {r40["slo_good_share"]:.0%}')
    check('p95 first-word time grows with users', r40['ttft_p95'] > r1['ttft_p95'])
    L, lw = r40['little_L_measured'], r40['little_lambda_W']
    check("Little's law holds over the stage window (L = lambda x W, within 15%)", abs(L - lw) / L < 0.15, f'L {L:.1f} vs {lw:.1f}')
    check('denominator counts every sent request', r40['sent'] == r40['ok'] + r40['timeout'] + r40['rejected'] + r40['error'])
    check('observed concurrency from the timeline equals the 4 slots', r40.get('max_streaming') == 4, f'max streaming {r40.get("max_streaming")}')
    check('throughput uses the real span (arrivals + drain)', r40['span_s'] > 40.0 and abs(r40['throughput_rps'] - r40['ok'] / r40['span_s']) < 1e-9)

    # bounded queue answers 503 at once
    with experiments.FakeServer(K, max_queue=2) as s:
        cfg = cfg_for(s, duration=20.0)
        live = loadgen.Live('fake', True, 3.0, 30.0)
        await experiments.warm_once(cfg, clock, live)
        rows, _, recs = await experiments.staged(cfg, clock, live, [('3 req/s', None, 3.0, 7)], slots=4)
    rej = [r for r in recs if r['status'] == 'rejected']
    check('bounded queue rejects with 503 when full', len(rej) > 0, f'{len(rej)} of {len(recs)}')
    check('a rejection is fast (no waiting in line)', bool(rej) and max(r['t_end'] - r['t_send'] for r in rej) < 0.5)

    # a client that gives up frees its place
    with experiments.FakeServer(K) as s:
        cfg = cfg_for(s, duration=10.0, timeout=2.0)
        live = loadgen.Live('fake', True, 3.0, 2.0)
        await experiments.warm_once(cfg, clock, live)
        rows, _, recs = await experiments.staged(cfg, clock, live, [('2 req/s', None, 2.0, 9)], slots=4)
        await clock.sleep(1.0)
        m = await loadgen.fetch_metrics(s.host, s.port)
    check('timeouts are recorded', rows[0]['timeout'] > 0, f'{rows[0]["timeout"]} timeouts')
    check('server drops abandoned requests (queue and slots empty after)', m.get('cancelled', 0) > 0 and m.get('active') == 0
          and m.get('queue') == 0, f'cancelled {m.get("cancelled")}, wasted slot-s {m.get("wasted_slot_s")}')
    return r1, r40, tl, tc, tw


def main():
    t0 = time.time()
    check('number words', spoken.fa_int(24) == 'بیست‌وچهار' and spoken.fa_int(125) == 'صد و بیست‌وپنج'
          and spoken.fa_dec(2.5) == 'دو و نیم' and spoken.fa_dec(0.4) == 'چهار دهم' and spoken.fa_int(1000) == 'هزار')
    check('nearest-rank p95 (n=20 -> 19th value; inf stays inf)',
          pct(list(range(1, 21)), 95) == 19 and pct([1, INF, 2], 95) == INF)
    try:
        loadgen.check_local('example.com')
        check('refuses a non-local target', False)
    except SystemExit:
        check('refuses a non-local target', True)
    for bad in ('0.0.0.0:11434', 'http://192.168.1.5:11434', 'example.com'):
        try:
            loadgen.parse_ollama_host(bad)
            check(f'OLLAMA_HOST {bad} refused', False)
        except SystemExit:
            check(f'OLLAMA_HOST {bad} refused', True)
    check('OLLAMA_HOST loopback forms accepted', loadgen.parse_ollama_host(None) == ('127.0.0.1', 11434)
          and loadgen.parse_ollama_host('[::1]:11500') == ('::1', 11500)
          and loadgen.parse_ollama_host('http://localhost:11434/') == ('localhost', 11434))
    runs = experiments.RESULTS / 'runs'
    before = sorted(p.name for p in runs.iterdir()) if runs.exists() else None
    r1, r40, tl, tc, tw = asyncio.run(main_async())
    meta = {'model': 'fake', 'ollama_version': 'homodyne-fake-1', 'num_parallel': 4,
            'hardware': {'chip': 'Apple M1', 'ram_gb': 8}}
    lines, broke = spoken.run_lines(meta, {'cold_ttft': tc, 'warm_ttft': tw}, [(1, r1), (40, r40)])
    check('report builds the spoken [RUN] lines', bool(lines['10']) and bool(lines['11']) and broke == 40)
    print('   sample (SIMULATED, rehearsal only):', lines['11'][-2])
    # report: end to end on a temporary run folder (never results/runs/)
    import io, json, contextlib, load_lab
    with tempfile.TemporaryDirectory() as d:
        run = Path(d) / '20990101-0000-ollama-selftest'
        run.mkdir()
        locked = dict(experiments.RUN_PROTOCOL)
        rows = []
        for u, r in zip(locked['users'], [r1, r1, r40, r40]):
            rows.append({**r, 'users': u})
        meta = {**meta, 'label': 'SELFTEST', 'locked': locked, 'locked_sha256': experiments.sha(locked),
                'prompts_sha256': experiments.sha(loadgen.PROMPTS_FA), 'load': {'timeout': 30},
                'protocol_sha256': experiments.sha(experiments.RUN_PROTOCOL)}
        meta['hardware'].update(power='selftest')
        (run / 'meta.json').write_text(json.dumps(meta, default=str))
        (run / 'results.json').write_text(json.dumps({'cold': {'cold_ttft': tc, 'warm_ttft': tw}, 'ramp': rows}))
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            ok_code = load_lab.main(['report', '--run', str(run)])
        check('report prints spoken lines for a run that matches the locked protocol',
              ok_code == 0 and 'قاب 11' in buf.getvalue() and 'MATCHES' in buf.getvalue())
        meta['locked']['users'] = [1, 10, 20]
        (run / 'meta.json').write_text(json.dumps(meta, default=str))
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            bad_code = load_lab.main(['report', '--run', str(run)])
        check('report refuses a run whose locked protocol was edited (hash mismatch)',
              bad_code == 2 and 'REFUSED' in buf.getvalue())
    check('protocol.json (committed) equals experiments.RUN_PROTOCOL', experiments.protocol_file_ok())
    after = sorted(p.name for p in runs.iterdir()) if runs.exists() else None
    check('selftest left results/runs/ untouched', before == after)
    with tempfile.TemporaryDirectory() as d:
        made = charts.charts(d, 'SELFTEST · SIMULATED', ramp=[{**r1, 'users': 1}, {**r40, 'users': 40}], timeline=tl)
        check('charts render (or are skipped without matplotlib)', all((Path(d) / m).exists() for m in made if m.endswith('.png')),
              ', '.join(made))
    dt_ = time.time() - t0
    check('selftest under 60 s', dt_ < 60, f'{dt_:.1f}s')
    ok = all(results)
    print(f'\n{"SELFTEST PASSED" if ok else "SELFTEST FAILED"} · {sum(results)}/{len(results)} checks · fake service only, '
          f'SIMULATED SERVICE (ILLUSTRATIVE)')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
