#!/usr/bin/env python3
"""HMD-022 · Model Routing Simulator: a small model, a big model and the routers between them.

    python3 routing_lab.py plan                 # no network: calls, tokens, $ (real or UPPER BOUND), fingerprints
    HOMODYNE_NO_FALLBACK=1 python3 routing_lab.py run --limit 5   # API: $ bound, then [y/N]; 5 DEV items only
    HOMODYNE_NO_FALLBACK=1 python3 routing_lab.py run             # API: all 200 items x 4 calls (3 small + 1 big)
    python3 routing_lab.py report               # prices.json -> tables, curve.png/.csv, spoken [RUN] lines
    python3 routing_lab.py simulate --table t.csv   # any per-item table, no model calls
    HOMODYNE_MODEL=mock:echo python3 routing_lab.py --selftest     # no key, no network, < 60 s

Models come from tools/llm.py: role 'main' is the big model, role 'small' the small one (HOMODYNE_MODEL,
HOMODYNE_MODEL_SMALL, or the provider defaults). Answers are cached, so a re-run costs nothing; the latency of the
first, uncached call is the one kept.

Run with HOMODYNE_NO_FALLBACK=1: a refusal is then recorded as a refusal (and graded apart from a wrong answer),
instead of being answered silently by Claude's server-side fallback model. Set it before the first run: the answer
cache does not know about it.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path[:0] = [str(HERE), str(ROOT / 'tools')]

import grade      # noqa: E402
import runmeta    # noqa: E402
import routers    # noqa: E402
import spoken     # noqa: E402
import taskset    # noqa: E402

RUNS = HERE / 'runs'
RESULTS = HERE / 'results'
PRICES = HERE / 'prices.json'
SAMPLES = 3
MAX_TOKENS = 2000
SYSTEM = ('You answer short requests. Reply with JSON only, no other text: {"answer": "<the final answer only: a number '
          'in digits without units, or a short phrase; for a yes/no question, yes or no>", "confidence": <integer 0-100: '
          'your estimate of the probability that your answer is correct>}. If a text is given, answer from that text only.')
CHARS_PER_TOKEN = {'fa': 2.5, 'en': 4.0}


def prompt_for(item, sample):
    """Sample 1 is the plain prompt; samples 2 and 3 add a marker so the cache keeps them as separate attempts."""
    return item['prompt'] if sample == 1 else f'{item["prompt"]}\n\n(independent attempt {sample})'


def calls_for(item):
    return [('small', s) for s in range(1, SAMPLES + 1)] + [('main', 1)]


# ── mock model, self-test only ──────────────────────────────────────────────────────────────────
MOCK_P = {'small': {'lookup': .9, 'convert': .85, 'extract': .8, 'multistep': .55, 'highrisk': .6},
          'main': {'lookup': .97, 'convert': .95, 'extract': .93, 'multistep': .88, 'highrisk': .9}}


def _u(*parts):
    return int(hashlib.sha256('|'.join(map(str, parts)).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def truth_text(t, lang):
    if t['type'] == 'number':
        v = t['value']
        return str(int(v)) if float(v).is_integer() else str(v)
    if t['type'] == 'text':
        return t['aliases'][0]
    return ('بله' if t['value'] else 'خیر') if lang == 'fa' else ('yes' if t['value'] else 'no')


def wrong_text(t, k):
    if t['type'] == 'number':
        return str(round(t['value'] * (1.1 + 0.07 * k) + 1, 2))
    if t['type'] == 'yesno':
        return 'no' if t['value'] else 'yes'
    return f'unknown-{k}'


def mock_answer(item, role, sample):
    """A fake model with a known skill per category, so every router branch has something to do. MOCK, not data."""
    right = _u(item['id'], role) < MOCK_P[role][item['category']]
    if sample > 1:                         # later samples: agree with the first answer more often when it was right
        same = _u(item['id'], role, sample) < (0.88 if right else 0.35)
        ans = mock_answer(item, role, 1)['answer'] if same else wrong_text(item['truth'], sample)
        return {'answer': ans, 'confidence': 80}
    conf = 70 + 29 * _u(item['id'], 'c') if right else 40 + 55 * _u(item['id'], 'c')
    return {'answer': truth_text(item['truth'], item['lang']) if right else wrong_text(item['truth'], 0),
            'confidence': round(conf)}


def mock_latency(item, role):
    base = 0.6 if role == 'small' else 2.2
    return round(base + item['chars'] / (900 if role == 'small' else 300) + 3 * _u(item['id'], role, 'lat') ** 6, 3)


# ── models ──────────────────────────────────────────────────────────────────────────────────────
def models():
    import llm
    if os.environ.get('HOMODYNE_MODEL', '').startswith('mock:') and not os.environ.get('HOMODYNE_MODEL_SMALL'):
        os.environ['HOMODYNE_MODEL_SMALL'] = 'mock:small'
    return '%s:%s' % llm.resolve('main'), '%s:%s' % llm.resolve('small')


def slug(big, small):
    return re.sub(r'[^A-Za-z0-9._-]+', '-', f'{small}__{big}')


def pick_items(args):
    """--limit N looks at DEV items only, so a trial run never shows anyone a frozen test answer."""
    if getattr(args, 'limit', 0):
        return taskset.load('dev')[:args.limit]
    return taskset.load(getattr(args, 'split', 'all') or 'all')


def estimate(items):
    """Calls and rough input tokens, per role ('small' x3 samples, 'main' x1)."""
    calls, tok = {'small': 0, 'main': 0}, {'small': 0.0, 'main': 0.0}
    for x in items:
        per = len(SYSTEM) / 4 + len(x['prompt']) / CHARS_PER_TOKEN[x['lang']]
        for role, _ in calls_for(x):
            calls[role] += 1
            tok[role] += per
    return calls, tok


def money_lines(calls, tok):
    prices = json.loads(PRICES.read_text(encoding='utf-8')) if PRICES.exists() else {}
    try:
        big, small = models()
        note = []
    except Exception:  # noqa: BLE001  no key yet: still show the bound, at the default fallback price
        big, small = 'unset:big-model', 'unset:small-model'
        note = ['dollars (models not set yet, so the default fallback price is used for both):']
    return note + runmeta.dollar_lines(tok, calls, {'main': big, 'small': small}, prices, MAX_TOKENS)


def cmd_plan(args, write=True):
    items = pick_items(args)
    calls, tok = estimate(items)
    try:
        big, small = models()
        who = f'big = {big} · small = {small}'
    except Exception as e:  # noqa: BLE001  (no key is fine for a plan)
        who = f'models not set yet ({str(e)[:80]}...)'
    text = '\n'.join([
        'HMD-022 · plan (no network, nothing spent)',
        who,
        taskset.stats(items),
        f'calls: {len(items)} items x {SAMPLES} small samples + 1 big = {sum(calls.values())}',
        f'rough input tokens: small {tok["small"] / 1e3:.0f} k, big {tok["main"] / 1e3:.0f} k (characters / 2.5 for Persian, '
        f'/ 4 for English; measure with run --limit 5)',
        f'output cap: {MAX_TOKENS} tokens per call; expected replies are a short JSON',
        *money_lines(calls, tok),
        'design fingerprints (stored by run, checked by report):',
        *runmeta.fingerprint_lines(runmeta.fingerprints()),
        'run with HOMODYNE_NO_FALLBACK=1 so refusals are recorded, not answered by a fallback model',
        'routers: ' + ', '.join(routers.FAMILIES),
        f'selection: thresholds chosen on dev (non-risk), quality budget {routers.QUALITY_BUDGET_PP:g} points vs always-big; '
        f'reported on the frozen test set; risk category always big model + human check',
    ])
    print(text)
    if write and not getattr(args, 'limit', 0):
        RESULTS.mkdir(exist_ok=True)
        text = re.sub(r'big = .*|models not set yet.*', '[models: set at run time]', text)
        (RESULTS / 'plan.txt').write_text(text + '\n', encoding='utf-8')
    return 0


def cmd_run(args, out_root=RUNS):
    import llm
    big, small = models()
    items = pick_items(args)
    calls, tok = estimate(items)
    out = out_root / slug(big, small)
    print(f'{llm.describe()}\n{len(items)} items{" (dev only: --limit)" if args.limit else ""} -> {sum(calls.values())} calls, '
          f'~{sum(tok.values()) / 1e3:.0f} k input tokens (rough) -> {out}')
    print('\n'.join(money_lines(calls, tok)))
    mock = big.startswith('mock:')
    if not mock and not os.environ.get('HOMODYNE_NO_FALLBACK'):
        print('note: HOMODYNE_NO_FALLBACK is not set; Claude refusals may be answered by a fallback model. '
              'Recommended: HOMODYNE_NO_FALLBACK=1 (see artifact/README.md).')
    if not mock and not args.yes and input('This spends API money. Continue? [y/N] ').strip().lower() != 'y':
        print('stopped')
        return 1
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'items.jsonl'
    old = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            r = json.loads(line)
            old[r['id']] = r
    meta = {'big': big, 'small': small, 'started': time.strftime('%Y-%m-%d %H:%M'), 'samples': SAMPLES,
            'max_tokens': MAX_TOKENS, 'effort': os.environ.get('HOMODYNE_EFFORT', 'medium'), 'system': SYSTEM,
            'mock': mock, 'no_fallback': bool(os.environ.get('HOMODYNE_NO_FALLBACK')), 'limit_dev_only': args.limit}
    prev_meta = json.loads((out / 'meta.json').read_text()) if (out / 'meta.json').exists() else {}
    meta['first_started'] = prev_meta.get('first_started', meta['started'])
    meta['fingerprints'] = prev_meta.get('fingerprints') or runmeta.fingerprints()
    changed = runmeta.mismatches(meta['fingerprints'], runmeta.fingerprints())
    if changed:
        print('WARNING: registered files changed since this run folder started: ' + ', '.join(changed))
        meta['fingerprint_mismatch_at_resume'] = changed
    (out / 'meta.json').write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding='utf-8')
    fell_back = 0
    for n, item in enumerate(items, 1):
        rec = old.get(item['id'], {'id': item['id'], 'calls': {}})
        for role, sample in calls_for(item):
            key = f'{role}{sample}'
            res = llm.call(prompt_for(item, sample), system=SYSTEM, role=role, max_tokens=MAX_TOKENS,
                           cache_dir=out / 'cache', mock=lambda p, i=item, r=role, s=sample: json.dumps(mock_answer(i, r, s), ensure_ascii=False))
            parsed = grade.parse_reply(res.text)
            prev = rec['calls'].get(key)
            lat = mock_latency(item, role) if mock else res.latency_s
            if prev:                                   # keep the first measurement; a cached reply has no new latency
                lat = prev['latency_s']
            rec['calls'][key] = {'role': role, 'sample': sample, 'model_served': res.model_served, 'fell_back': res.fell_back,
                                 'input_tokens': res.input_tokens, 'output_tokens': res.output_tokens, 'latency_s': round(lat, 3),
                                 'cached': prev['cached'] if prev else res.cached, 'stop_reason': res.stop_reason, 'reply': res.text,
                                 'refusal_category': (res.extra or {}).get('refusal_category'),
                                 'answer': parsed['answer'], 'confidence': parsed['confidence'],
                                 'conf_flag': parsed['conf_flag'], 'json_ok': parsed['ok'],
                                 'correct': grade.correct(item['truth'], parsed['answer'])}
            fell_back += bool(res.fell_back)
        old[item['id']] = rec
        if n % 25 == 0 or n == len(items):
            print(f'  {n}/{len(items)}')
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in old.values()), encoding='utf-8')
    if fell_back:
        print(f'  note: {fell_back} replies came from a fallback model (see model_served)')
    print(f'\nNext: fill prices.json, then: python3 {Path(__file__).name} report')
    return 0


# ── report ──────────────────────────────────────────────────────────────────────────────────────
def load_prices(path, big, small):
    d = json.loads(Path(path).read_text(encoding='utf-8')) if Path(path).exists() else {}
    p = d.get('models') or {}
    for m in (big, small):
        if (p.get(m) or {}).get('input_per_mtok') is None or (p.get(m) or {}).get('output_per_mtok') is None:
            return None, d
    return p, d


def cost(c, price):
    return (c['input_tokens'] * price['input_per_mtok'] + c['output_tokens'] * price['output_per_mtok']) / 1e6


def table_from_run(out, prices):
    meta = json.loads((out / 'meta.json').read_text(encoding='utf-8'))
    items = {x['id']: x for x in taskset.load()}
    rows = []
    for line in (out / 'items.jsonl').read_text(encoding='utf-8').splitlines():
        r = json.loads(line)
        c = r['calls']
        if not all(f'{role}{s}' in c for role, s in calls_for(items[r['id']])):
            continue
        it = items[r['id']]
        ps, pb = prices[meta['small']], prices[meta['big']]
        agree = sum(grade.same_answer(c['small1']['answer'], c[f'small{s}']['answer']) for s in range(1, SAMPLES + 1))
        rows.append({'id': it['id'], 'split': it['split'], 'category': it['category'], 'lang': it['lang'], 'risk': it['risk'],
                     'chars': it['chars'], 's1_correct': c['small1']['correct'], 's1_conf': c['small1']['confidence'],
                     's1_cost': cost(c['small1'], ps), 's1_lat': c['small1']['latency_s'],
                     's1_in': c['small1']['input_tokens'], 's1_out': c['small1']['output_tokens'],
                     's2_cost': cost(c['small2'], ps), 's2_lat': c['small2']['latency_s'],
                     's3_cost': cost(c['small3'], ps), 's3_lat': c['small3']['latency_s'], 'agree': agree,
                     'b_correct': c['main1']['correct'], 'b_cost': cost(c['main1'], pb), 'b_lat': c['main1']['latency_s'],
                     'b_in': c['main1']['input_tokens'], 'b_out': c['main1']['output_tokens'],
                     's1_refused': runmeta.classify(c['small1'])['refused'],
                     'b_refused': runmeta.classify(c['main1'])['refused']})
    fb = sum(v.get('fell_back', False) for line in (out / 'items.jsonl').read_text(encoding='utf-8').splitlines()
             for v in json.loads(line)['calls'].values())
    return rows, meta, fb


def render(result, meta, label, health=None, changed=None):
    t = result['test']
    out = [f'HMD-022 · report · {label}', f'big = {meta.get("big")} · small = {meta.get("small")} · prices checked '
           f'{meta.get("prices_checked_on")} · run {meta.get("first_started", meta.get("started"))} · '
           f'HOMODYNE_NO_FALLBACK {"on" if meta.get("no_fallback") else "off"}']
    if changed is not None:
        out.append('FINGERPRINT MISMATCH: these registered files changed after the run started: ' + ', '.join(changed)
                   if changed else 'fingerprints: graders, routers, task set and protocol match the run')
    out += ['',
           f'test set, non-risk categories (n = {result["n_test_nonrisk"]}); thresholds picked on dev; quality budget '
           f'{result["budget_pp"]:g} points below always-big on dev', '',
           f'{"router":14} {"thr":>5} {"correct":>9} {"acc":>6} {"$/1k tasks":>11} {"$/1k success":>13} {"escal":>6} '
           f'{"p95 s":>6} {"missed":>7} {"wasted":>7}']
    for f in routers.FAMILIES:
        p = result['picks'][f]
        if f not in t:
            out.append(f'{f:14}   no threshold met the quality budget on dev')
            continue
        x = t[f]
        out.append(f'{f:14} {str(p["threshold"]):>5} {x["correct"]:4}/{x["n"]:<4} {x["accuracy"]:6.3f} {1000 * x["cost_per_task"]:11.4f} '
                   f'{1000 * (x["cost_per_success"] or 0):13.4f} {x["escalation_rate"]:6.2f} {x["p95_latency"]:6.2f} '
                   f'{x["missed_escalations"]:7} {x["wasted_escalations"]:7}')
    out += ['', 'paired bootstrap vs always-big (test, non-risk, 2,000 resamples, 95% interval):']
    for f, c in result['ci'].items():
        z = ' (interval includes zero)' if c['acc_diff_ci'][0] <= 0 <= c['acc_diff_ci'][1] else ''
        out.append(f'  {f:14} accuracy {c["acc_diff_pp"]:+.1f} pts [{c["acc_diff_ci"][0]:+.1f}, {c["acc_diff_ci"][1]:+.1f}]{z} · '
                   f'cost per success x{c["cps_ratio"]:.2f} [{c["cps_ratio_ci"][0]:.2f}, {c["cps_ratio_ci"][1]:.2f}]')
    out += ['', f'by category (test): small / big / either correct · near = small at most {result["budget_pp"]:g} points '
            '(in whole items) behind big']
    for c, v in result['by_category'].items():
        out.append(f'  {c:10} {v["small"]:3}/{v["n"]}  {v["big"]:3}/{v["n"]}  {v["either"]:3}/{v["n"]}  '
                   f'{"near" if v["near"] else "behind"}{"  (small ahead)" if v["small"] > v["big"] else ""}')
    rf = result.get('refusals', {})
    b, rk = t['always-big'], result['risk_test'].get('always-big')
    out.append(f'big-model errors, non-risk test: {b["n"] - b["correct"]} = {rf.get("nonrisk_big", 0)} refused + '
               f'{b["n"] - b["correct"] - rf.get("nonrisk_big", 0)} wrong answers')
    if rk:
        out.append(f'big-model errors, risk test: {rk["n"] - rk["correct"]} = {rf.get("risk_big", 0)} refused + '
                   f'{rk["n"] - rk["correct"] - rf.get("risk_big", 0)} wrong answers')
    out += ['', f'risk category (test, n = {result["n_test_risk"]}), NOT routed in the policy; what each router would have done:']
    for f, x in result['risk_test'].items():
        out.append(f'  {f:14} correct {x["correct"]}/{x["n"]} · escalated {x["escalation_rate"]:.2f} · missed {x["missed_escalations"]}')
    if health:
        out += [''] + runmeta.health_lines(health)
    out += ['', 'missed = kept on the small model, small wrong, big right · wasted = escalated although small was right',
            '', '# Spoken lines for the [RUN] beats 11-13 (paste into script-fa.md, keep one branch, drop [bracketed] notes)', '']
    out += spoken.lines(result, meta)
    return '\n'.join(out)


def cmd_report(args, root=RUNS, prices_path=PRICES, results_dir=None, label=None):
    runs = [p for p in root.glob('*/items.jsonl')] if root.exists() else []
    if args.model:
        runs = [root / args.model / 'items.jsonl']
    if not runs:
        raise SystemExit('No run yet: routing_lab.py run   (or --selftest for a mock run)')
    if len(runs) > 1:
        raise SystemExit('Several runs: pass --model ' + ' | '.join(p.parent.name for p in runs))
    out = runs[0].parent
    meta = json.loads((out / 'meta.json').read_text(encoding='utf-8'))
    prices, pmeta = load_prices(prices_path, meta['big'], meta['small'])
    if prices is None:
        raise SystemExit(f'prices.json has no price for {meta["big"]} and {meta["small"]}: fill it (USD per million tokens '
                         'and checked_on) from the provider\'s pricing page, then run report again.')
    rows, meta, fb = table_from_run(out, prices)
    meta['prices_checked_on'] = pmeta.get('checked_on')
    result = routers.simulate(rows)
    records = [json.loads(line) for line in (out / 'items.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    health = runmeta.call_health(records)
    changed = runmeta.mismatches(meta.get('fingerprints', {}), runmeta.fingerprints()) if meta.get('fingerprints') else None
    result['health'], result['fingerprint_mismatch'] = health, changed
    label = label or ('MOCK DATA · selftest · not a result' if meta.get('mock') else
                      f'REAL RUN · {meta["small"]} vs {meta["big"]} · run {meta.get("first_started")} · prices {pmeta.get("checked_on")}')
    if changed:
        label += ' · FINGERPRINT MISMATCH'
    text = render(result, meta, label, health, changed if meta.get('fingerprints') else None)
    text += f'\n\nnote: {fb} replies came from a fallback model' if fb else ''
    print(text)
    dest = results_dir or (RESULTS / out.name)
    dest.mkdir(parents=True, exist_ok=True)
    routers.write_table(rows, dest / 'per-item.csv')
    import plot
    plot.write_csv(result, dest / 'curve.csv')
    plot.plot(result, dest / 'curve.png', f'HMD-022 · {meta["small"]} vs {meta["big"]}', label)
    (dest / 'report.txt').write_text(text + '\n', encoding='utf-8')
    (dest / 'summary.json').write_text(json.dumps({k: v for k, v in result.items() if not k.startswith('curve')},
                                                  ensure_ascii=False, indent=1, default=str), encoding='utf-8')
    return 0


def cmd_simulate(args):
    rows = routers.read_table(args.table)
    result = routers.simulate(rows, args.budget)
    meta = {'big': 'big (from table)', 'small': 'small (from table)', 'prices_checked_on': None}
    print(render(result, meta, f'SIMULATION from {args.table}'))
    return 0


# ── self-test ───────────────────────────────────────────────────────────────────────────────────
def selftest():
    if not os.environ.get('HOMODYNE_MODEL', '').startswith('mock:'):
        print('selftest needs HOMODYNE_MODEL=mock:echo (no key, no network, no cost)')
        return 2
    t0 = time.time()
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(('  ok    ' if cond else '  FAIL  ') + name)

    bad = [c for c in grade.selfcheck() if c[2] != c[3]]
    check(f'grader: {len(grade.selfcheck())} cases (Persian digits, scale words, hedges, aliases, yes/no)', not bad)
    for c in bad:
        print('        ', c)
    items = taskset.build()
    check('task set: 200 items, 80 dev / 120 test, 40 per category', len(items) == 200 and sum(x['split'] == 'dev' for x in items) == 80
          and all(sum(x['category'] == c for x in items) == 40 for c in taskset.CATEGORIES))
    check('task set: ids unique, no prompt in both dev and test', len({x['id'] for x in items}) == 200 and
          not ({x['prompt'] for x in items if x['split'] == 'dev'} & {x['prompt'] for x in items if x['split'] == 'test'}))
    check('task set: committed tasks.json equals a fresh build (seed 22)', taskset.load() == items)
    check('run --limit takes dev items only', all(x['split'] == 'dev' for x in pick_items(argparse.Namespace(limit=5, split='all'))))
    fp = runmeta.fingerprints()
    check('fingerprints: sha256 of grade.py, routers.py, tasks.json, protocol.md + commit field',
          all(len(fp[k]) == 64 for k in runmeta.REGISTERED) and 'commit' in fp)
    check('fingerprints: a changed file is flagged', runmeta.mismatches(dict(fp, **{'grade.py': '0' * 64}), fp) == ['grade.py'])
    pr = json.loads(PRICES.read_text(encoding='utf-8'))
    dl = runmeta.dollar_lines({'small': 1e5, 'main': 3e4}, {'small': 600, 'main': 200},
                              {'main': 'anthropic:big-x', 'small': 'anthropic:small-x'}, pr, MAX_TOKENS)
    check('plan/run print a CONSERVATIVE UPPER BOUND in dollars while prices are empty',
          any('TOTAL UPPER BOUND ≤ $' in l and 'NOT AN OFFICIAL PRICE' in l for l in dl))
    check('refusal, truncation and fallback are classified apart from wrong answers',
          runmeta.classify({'stop_reason': 'refusal'})['refused'] and runmeta.classify({'stop_reason': 'MAX_TOKENS'})['truncated']
          and runmeta.classify({'fell_back': True})['fallback'] and not runmeta.classify({'stop_reason': 'end_turn'})['refused'])
    check('leaflets: every dose question carries the FICTIONAL label', all(('FICTIONAL' in x['prompt']) or ('ساختگی' in x['prompt'])
                                                                            for x in items if x['category'] == 'highrisk'))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        args = argparse.Namespace(split='all', limit=0, yes=True, model=None)
        cmd_run(args, out_root=root)
        pfile = root / 'prices.json'
        big, small = models()
        pfile.write_text(json.dumps({'checked_on': '2027-04-10', 'models': {
            big: {'input_per_mtok': 5.0, 'output_per_mtok': 25.0}, small: {'input_per_mtok': 1.0, 'output_per_mtok': 5.0}}}))
        out = next(root.glob('*/items.jsonl')).parent
        rows, meta, _ = table_from_run(out, load_prices(pfile, big, small)[0])
        check('mock run: 200 items x 4 calls recorded', len(rows) == 200)
        test = routers.subset(rows, 'test', 'nonrisk')
        s, b, o = (routers.evaluate(test, f) for f in ('always-small', 'always-big', 'oracle'))
        check('oracle: at least as right as either model, never dearer than always-big',
              o['correct'] >= max(s['correct'], b['correct']) and o['cost'] <= b['cost'] + 1e-12)
        check('confidence 101 = always escalate: same correct as always-big',
              routers.evaluate(test, 'confidence', 101)['correct'] == b['correct'])
        check('cascade m=1 = never escalate: same correct as always-small',
              routers.evaluate(test, 'cascade', 1)['correct'] == s['correct'])
        picks = routers.choose(rows)
        flipped = [dict(r, s1_correct=not r['s1_correct'], b_correct=not r['b_correct']) if r['split'] == 'test' else r for r in rows]
        check('thresholds depend on dev only (scrambling test leaves every pick unchanged)',
              all(picks[f]['threshold'] == routers.choose(flipped)[f]['threshold'] for f in routers.FAMILIES))
        result = routers.simulate(rows)
        check('every router has a test result or is reported as outside the budget', set(result['picks']) == set(routers.FAMILIES))
        meta['prices_checked_on'] = '2027-04-10'
        said = spoken.lines(result, meta)
        prose = [l for l in said if not l.startswith('[') and not l.startswith('—')]
        check('spoken lines: numbers as words (no digits outside [notes])', not any(re.search(r'[0-9۰-۹]', l) for l in prose))
        crowded = [sent for l in prose for sent in re.split(r'[.؟!:؛]', l) if spoken.numbers_in(sent) > 2]
        check(f'spoken lines: at most two numbers per sentence ({len(crowded)} over)', not crowded)
        for sent in crowded[:3]:
            print('        ', sent.strip()[:90])
        health = runmeta.call_health([json.loads(l) for l in (out / 'items.jsonl').read_text(encoding='utf-8').splitlines()])
        check('call health: confidence formats and unparsed share are reported', health['confidence']['n'] == 200
              and 'unparsed_share' in health['confidence'])
        mock_dir = RESULTS / 'MOCK-selftest'
        cmd_report(argparse.Namespace(model=None), root=root, prices_path=pfile, results_dir=mock_dir,
                   label='MOCK DATA · selftest · fake model and fake prices · not a result')
        check('report wrote curve.png, curve.csv, per-item.csv, report.txt',
              all((mock_dir / f).exists() for f in ('curve.png', 'curve.csv', 'per-item.csv', 'report.txt')))
    took = time.time() - t0
    check(f'under 60 seconds ({took:.1f} s)', took < 60)
    print('selftest ' + ('passed' if ok else 'FAILED'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description='HMD-022 · Model Routing Simulator')
    ap.add_argument('--selftest', action='store_true')
    sub = ap.add_subparsers(dest='cmd')
    for name in ('plan', 'run'):
        p = sub.add_parser(name)
        p.add_argument('--split', default='all', choices=['all', 'dev', 'test'])
        p.add_argument('--limit', type=int, default=0, help='first N items only (try 5 first)')
        if name == 'run':
            p.add_argument('--yes', action='store_true', help='skip the [y/N] question')
    rp = sub.add_parser('report')
    rp.add_argument('--model', help='folder under runs/ when there are several')
    sp = sub.add_parser('simulate')
    sp.add_argument('--table', required=True, help='per-item CSV with the columns in routers.COLUMNS')
    sp.add_argument('--budget', type=float, default=routers.QUALITY_BUDGET_PP)
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.cmd == 'plan':
        return cmd_plan(args)
    if args.cmd == 'run':
        return cmd_run(args)
    if args.cmd == 'report':
        return cmd_report(args)
    if args.cmd == 'simulate':
        return cmd_simulate(args)
    ap.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
