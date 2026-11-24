#!/usr/bin/env python3
"""load_lab.py — AI Load Lab for HMD-023 «وقتی صد نفر هم‌زمان از AI سؤال کنند چه می‌شود؟»

    python3 load_lab.py plan                      what will run, and whether Ollama is reachable (loads nothing)
    python3 load_lab.py simulate                  fake service on 127.0.0.1, about 9 minutes, writes results/simulated/
    python3 load_lab.py simulate --timescale 1    same in real time (for filming the live dashboard)
    python3 load_lab.py run --target ollama --num-parallel 4     a real small model on this laptop ([RUN])
    python3 load_lab.py run --target fake         rehearse the real-run flow against the fake service
    python3 load_lab.py report                    the Persian spoken lines for the [RUN] beats, numbers as words
    python3 load_lab.py --selftest                fake service only, under 60 seconds

Rules built in: only 127.0.0.1/localhost targets; the fake server binds 127.0.0.1 and is always stopped;
no cloud calls; numbers from the fake service are labelled SIMULATED SERVICE (ILLUSTRATIVE) everywhere.
Python 3.9+, standard library (+ matplotlib for PNG charts, optional).
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import experiments  # noqa: E402
import spoken       # noqa: E402

PLAN = """AI Load Lab · HMD-023 · plan

SLO (the promise, in one sentence):
  95% of requests see the first word of the answer within {slo:g} s, and fewer than 1 in 100 requests fail.
  Denominator = requests sent in the stage (not users). A timeout or a 503 counts as a miss.

Tier 1 · simulate (runs now, no model)       -> results/simulated/   SIMULATED SERVICE (ILLUSTRATIVE)
  fake service: {slots} slots, prefill {prefill:g} tok/s, decode {decode:g} tok/s per slot (-{cont:.0%} per other busy slot),
                cold load {cold:g} s, queue up to {mq}
  requests:     input {inr[0]}-{inr[1]} tokens, output {outr[0]}-{outr[1]} tokens (uniform)
  closed loop:  {users} users; each sends, waits for the whole answer, thinks ~{think:g} s (exponential), repeats
  open loop:    {rates} requests/s (Poisson arrivals)
  policies:     100 users x {policies}
  each stage:   {dur:g} s of load + drain (timeout {to:g} s); cold and warm measured separately (3 tries each)

Tier 2 · run --target ollama ([RUN], the owner's laptop)   -> results/runs/<date>-ollama-<model>/
  model qwen2.5:1.5b (986 MB, Apache 2.0) unless --model or HOMODYNE_MODEL=ollama:<model>
  closed loop 1, 10, 50, 100 users · {dur:g} s each · think ~{think:g} s · max 160 output tokens · timeout {to:g} s
  records: Ollama version, model digest, OLLAMA_NUM_PARALLEL (from --num-parallel), chip, RAM, macOS, power source

Tier 3 · a cloud API: not included. tools/llm.py retries 429/5xx inside the call, so rate-limit behaviour
  would be invisible; and load-testing someone else's service is out of bounds for this episode.
"""


def plan(a):
    S, L = experiments.SIM, experiments.LOAD
    print(f'Locked real-run protocol: sha256 {experiments.sha(experiments.RUN_PROTOCOL)}  '
          f'(protocol.json {"matches" if experiments.protocol_file_ok() else "DOES NOT MATCH; run: load_lab.py plan --write-protocol"})')
    if getattr(a, 'write_protocol', False):
        experiments.PROTOCOL_FILE.write_text(json.dumps({'sha256': experiments.sha(experiments.RUN_PROTOCOL),
                                                         'protocol': experiments.RUN_PROTOCOL}, ensure_ascii=False, indent=1) + '\n',
                                             encoding='utf-8')
        print('wrote', experiments.PROTOCOL_FILE.name)
    print(PLAN.format(slo=L['slo_ttft'], slots=S['slots'], prefill=S['prefill_tps'], decode=S['decode_tps'],
                      cont=S['contention'], cold=S['cold_load'], mq=S['max_queue'], inr=L['in_range'], outr=L['out_range'],
                      users=experiments.RAMP_USERS, think=L['think'], rates=experiments.OPEN_RATES,
                      policies=[p[0] for p in experiments.POLICIES], dur=L['duration'], to=L['timeout']))
    try:
        with urllib.request.urlopen('http://127.0.0.1:11434/api/version', timeout=1) as r:
            print('Ollama: reachable on 127.0.0.1:11434, version', json.loads(r.read())['version'])
    except Exception:
        print('Ollama: not reachable on 127.0.0.1:11434 (run --target ollama prints the setup steps)')
    try:
        import matplotlib  # noqa: F401
        print('matplotlib: available (PNG charts)')
    except ImportError:
        print('matplotlib: missing (CSV only)')


def latest_run():
    runs = sorted((experiments.RESULTS / 'runs').glob('*-ollama-*'))
    return runs[-1] if runs else None


def report(a):
    d = Path(a.run) if a.run else latest_run()
    if d is None or not (d / 'results.json').exists():
        print('NOT RUN YET: no real Ollama run in results/runs/. The [RUN] beats (10 and 11) keep their placeholders.\n'
              'Run:  python3 load_lab.py run --target ollama --num-parallel 4   (setup steps are printed if Ollama is missing)')
        return 1
    meta = json.loads((d / 'meta.json').read_text(encoding='utf-8'))
    res = json.loads((d / 'results.json').read_text(encoding='utf-8'))
    locked = meta.get('locked')
    problems = []
    if not locked or experiments.sha(locked) != meta.get('locked_sha256'):
        problems.append('meta.json has no locked protocol, or its SHA-256 does not match (edited after the run?)')
    else:
        diff = experiments.protocol_diff(locked)
        if diff:
            problems.append(f'run protocol differs from the locked one the script was written for: {diff}')
        if meta.get('prompts_sha256') != experiments.sha(experiments.loadgen.PROMPTS_FA):
            problems.append('prompts changed since this run (prompts_sha256 differs)')
        if not experiments.protocol_file_ok() or meta.get('protocol_sha256') != experiments.sha(experiments.RUN_PROTOCOL):
            problems.append('protocol.json / RUN_PROTOCOL changed since this run (protocol_sha256 differs)')
    if meta.get('concurrency_warning'):
        print('WARNING: ' + meta['concurrency_warning'])
    if problems and not a.allow_mismatch:
        print('REFUSED: ' + ' · '.join(problems) +
              '\nThe [RUN] lines of beats 10 and 11 assume the locked protocol (experiments.RUN_PROTOCOL). '
              'Re-run with it, or pass --allow-mismatch and rewrite the hedges in the script by hand.')
        return 2
    rows = [(r['users'], r) for r in res['ramp']]
    meta.setdefault('observed_max_streaming', max((r.get('max_streaming') or 0) for _, r in rows) or None)
    lines, broke = spoken.run_lines(meta, res.get('cold'), rows)
    sim = meta.get('label', '').startswith('SIMULATED')
    print(f'# HMD-023 report · {d.name} · {meta.get("label")}')
    if sim:
        print('# SIMULATED: these lines are a rehearsal only and must NOT be read in the [RUN] beats.')
    print(f'# model {meta.get("model")} · Ollama {meta.get("ollama_version")} · OLLAMA_NUM_PARALLEL={meta.get("num_parallel")} · '
          f'{meta["hardware"].get("chip")} {meta["hardware"].get("ram_gb")} GB · {meta["hardware"].get("power")}')
    print(f'# load: {json.dumps(meta["load"], ensure_ascii=False)}')
    print(f'# locked protocol sha256 {meta.get("locked_sha256", "-")[:16]} · ' +
          ('MATCHES experiments.RUN_PROTOCOL' if not problems else 'MISMATCH: ' + ' · '.join(problems)) + '\n')
    print('| users | sent | ok | timeout | busy | first word p50 | p95 | full p95 | within SLO | SLO |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    f = lambda x: '-' if x is None else ('>timeout' if x == float('inf') else f'{x:.2f}')
    for u, r in rows:
        print(f'| {u} | {r["sent"]} | {r["ok"]} | {r["timeout"]} | {r["rejected"]} | {f(r["ttft_p50"])} | {f(r["ttft_p95"])} | '
              f'{f(r["e2e_p95"])} | {r["slo_good_share"]:.0%} | {"kept" if r["slo_met"] else "broken"} |')
    for beat in ('10', '11'):
        print(f'\n## قاب {beat} — جمله‌های گفتاری (عیناً به‌جای ⟨…⟩ در script-fa.md)\n')
        for ln in lines[beat]:
            print(ln)
    print(f'\n## deck (beat 11): first stage that broke the SLO = {broke if broke is not None else "none"}')
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--selftest', action='store_true', help='fake service only, under 60 s')
    sub = p.add_subparsers(dest='cmd')
    pl = sub.add_parser('plan')
    pl.add_argument('--write-protocol', action='store_true', help='(re)write protocol.json from experiments.RUN_PROTOCOL')
    s = sub.add_parser('simulate')
    s.add_argument('--timescale', type=float, default=0.25, help='0.25 = four times faster than real time (default)')
    s.add_argument('--duration', type=float, default=experiments.LOAD['duration'])
    s.add_argument('--users', type=lambda x: [int(v) for v in x.split(',')])
    s.add_argument('--rates', type=lambda x: [float(v) for v in x.split(',')])
    s.add_argument('--skip-policies', action='store_true')
    s.add_argument('--no-dash', action='store_true')
    s.add_argument('--replot', action='store_true', help='redraw charts of an existing --out folder, no new run')
    s.add_argument('--out', default=str(experiments.RESULTS / 'simulated'))
    r = sub.add_parser('run')
    r.add_argument('--target', choices=['ollama', 'fake'], required=True)
    r.add_argument('--model', help='default: HOMODYNE_MODEL=ollama:<model>, else qwen2.5:1.5b')
    r.add_argument('--num-parallel', type=int, help='the OLLAMA_NUM_PARALLEL value you set (recorded, not applied)')
    r.add_argument('--users', type=lambda x: [int(v) for v in x.split(',')])
    r.add_argument('--duration', type=float, default=120.0)
    r.add_argument('--think', type=float, default=20.0)
    r.add_argument('--max-tokens', type=int, default=160)
    r.add_argument('--timeout', type=float, default=30.0)
    r.add_argument('--cold-tries', type=int, default=3)
    r.add_argument('--no-think', action='store_true', help='send think=false (only for thinking models such as qwen3.5)')
    r.add_argument('--yes', action='store_true')
    r.add_argument('--no-dash', action='store_true')
    rp = sub.add_parser('report')
    rp.add_argument('--run', help='a folder in results/runs/ (default: the latest Ollama run)')
    rp.add_argument('--allow-mismatch', action='store_true', help='print lines even if the run differs from the locked protocol')
    a = p.parse_args(argv)
    if a.selftest:
        import selftest
        return selftest.main()
    if a.cmd == 'plan':
        return plan(a)
    if a.cmd == 'simulate':
        return experiments.simulate(a)
    if a.cmd == 'run':
        return experiments.run(a)
    if a.cmd == 'report':
        return report(a)
    p.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
