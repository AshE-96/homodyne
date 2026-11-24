#!/usr/bin/env python3
"""
HMD-020 · Structured Output Testbench: the form is tidy, so why is the answer wrong?

Chat messages to an invented neighbourhood grocery («سبد محله», ILLUSTRATIVE) become order records for its API.
Three lights per record: STRUCTURE (parses + fits schema.json), RULE (business rules), MEANING (answer key, lab only).

Arms (same 100 frozen messages, same instructions, same model; they differ only in how the format is asked for):
    free           "reply with JSON with these keys"
    schema_prompt  the JSON Schema is pasted into the prompt
    native         the same prompt + the provider's own schema-constrained decoding (tools/llm.py schema=)
    native_rules   native + the rule layer: record automatically, repair once, or send to a person

Commands (run from anywhere; standard library + tools/llm.py):
    python3 testbench.py generate        # writes data/ (refuses to change the frozen test set)
    python3 testbench.py local           # LOCAL, free: answer key + fault injection + demo extractor → results/
    python3 testbench.py plan            # no network: number of calls, token estimate, cost if prices.json is filled
    python3 testbench.py run [--limit 5] # API: prints the estimate and asks y/N before spending; answers cached
    python3 testbench.py report          # table + the Persian spoken lines for the [RUN] beats
    HOMODYNE_MODEL=mock:echo python3 testbench.py --selftest   # no key, no network, no cost, < 60 s
"""

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3] / 'tools'))

import checks  # noqa: E402
import demo_extractor  # noqa: E402
import world  # noqa: E402

DATA, RESULTS, RUNS, PRICES = HERE / 'data', HERE / 'results', HERE / 'runs', HERE / 'prices.json'
CALL_ARMS = ('free', 'schema_prompt', 'native')
MAX_TOKENS = 8000          # room for the model's own reasoning; a cut-off reply would look like a format failure
CHARS_PER_TOKEN = 2.5      # rough, for Persian-heavy prompts; `run --limit 3` shows the real count


# ── data ─────────────────────────────────────────────────────────────────────────────────────────
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cmd_generate(args):
    DATA.mkdir(exist_ok=True)
    lock = DATA / 'FROZEN.json'
    out = {}
    for split in ('test', 'dev'):
        rows = world.make_split(split)
        text = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
        path = DATA / f'{split}.jsonl'
        if split == 'test' and lock.exists() and not args.force:
            want = json.loads(lock.read_text())['test.jsonl']
            if hashlib.sha256(text.encode()).hexdigest() != want:
                raise SystemExit('The frozen test set would change. It is locked (data/FROZEN.json); use --force only '
                                 'before any model run, and say so in protocol.md.')
        path.write_text(text, encoding='utf-8')
        out[f'{split}.jsonl'] = sha(path)
        print(f'{split}: {len(rows)} messages → {path.relative_to(HERE)}  {Counter(r["group"] for r in rows)}')
    cat = {p: {'name_fa': v[0], 'allowed_units': v[2], 'base_unit': v[3], 'toman_per_base_unit': v[4],
               'household_cap': v[5]} for p, v in world.CATALOG.items()}
    (DATA / 'catalog.json').write_text(json.dumps(cat, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    if not lock.exists() or args.force:
        lock.write_text(json.dumps({**out, 'frozen_on': dt.date.today().isoformat(),
                                    'note': FROZEN_NOTE},
                                   indent=1) + '\n')
    return 0


FROZEN_NOTE = ('test.jsonl is frozen. Prompts and rules 1-4 were written on dev.jsonl only. Rule 5 was added on '
               '2026-11-24 after seeing the demo extractor (not a model) on test.jsonl; dev.jsonl shows the same hole '
               '(3/28 auto-recorded and wrong without rule 5, 0/28 with it). No model output had been produced.')


def verify_frozen(data_dir=None):
    """The SHA-256 of data/test.jsonl, after checking it against data/FROZEN.json. Aborts on a mismatch."""
    data_dir = data_dir or DATA
    want = json.loads((data_dir / 'FROZEN.json').read_text())['test.jsonl']
    got = sha(data_dir / 'test.jsonl')
    if got != want:
        raise SystemExit(f'data/test.jsonl does not match data/FROZEN.json (sha256 {got[:12]}… ≠ {want[:12]}…). '
                         'The frozen test set was changed; restore it before running or reporting.')
    return got


def load(split='test'):
    path = DATA / f'{split}.jsonl'
    if not path.exists():
        raise SystemExit('No data yet: python3 testbench.py generate')
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


# ── prompts (fixed before any model call; written on the dev split) ──────────────────────────────
def catalog_table():
    lines = ['id | Persian name | units it is sold in | price (toman per base unit) ']
    for p, (name, _, allowed, base, price, _cap) in world.CATALOG.items():
        extra = ' (1 pack = 30 eggs)' if p == 'eggs' else ''
        lines.append(f'{p} | {name} | {", ".join(allowed)}{extra} | {price:,} per {base}')
    return '\n'.join(lines)


SYSTEM = f"""You turn one customer chat message to the neighbourhood grocery «سبد محله» into one order record for the
shop's order API. Today is {world.TODAY.strftime('%A')} {world.TODAY.isoformat()} ({world.TODAY_FA}). The Iranian week
starts on Saturday.

Catalog:
{catalog_table()}

Fields:
- product: the catalog id.
- quantity and unit: the amount the customer ordered, in the unit they used (kg, g, piece, pack, liter). A size such
  as «۳ تا ۵ کیلویی» describes each item, it is not the quantity. If the quantity is missing or given only as a range,
  quantity is null (unit as stated, or null if no unit is stated).
- paid_toman: the amount the customer says they have already paid, in toman (1 toman = 10 rial). People often drop
  «هزار» («۴۵۰ تومن» = 450,000 toman) or write millions in words. null if they will pay on delivery.
- delivery_date: the requested delivery day in the Gregorian calendar, YYYY-MM-DD. Convert Persian (Jalali) dates and
  relative days. null if no day is given.
Never guess a value that is not in the message: use null."""

FORMAT_FREE = 'Reply with the order as JSON with the keys product, quantity, unit, paid_toman, delivery_date.'
FORMAT_SCHEMA = 'Reply with only one JSON object that validates against this JSON Schema:\n' + \
    json.dumps(checks.SCHEMA, ensure_ascii=False)


def prompt_for(arm, message):
    fmt = FORMAT_FREE if arm == 'free' else FORMAT_SCHEMA
    return f'Customer message:\n<<<\n{message}\n>>>\n\n{fmt}'


def repair_prompt(message, reply_record, hints):
    """One repair call. It names the broken rule in words (checks.REPAIR_HINTS) and never the catalog total."""
    found = '\n'.join(f'- {m}' for m in hints)
    return (f'Customer message:\n<<<\n{message}\n>>>\n\nYour record:\n{json.dumps(reply_record, ensure_ascii=False)}\n\n'
            f'Our business checks found:\n{found}\n\nRe-read the customer message and return the corrected record. '
            f'Change a value only if the message supports the change; if the message really says this, return the '
            f'record unchanged.\n\n{FORMAT_SCHEMA}')


# ── self-test model (mock:echo only; never used for results) ─────────────────────────────────────
def _h(s):
    return int(hashlib.sha256(s.encode()).hexdigest(), 16) % 100


def mock_model(prompt, schema=None):
    """Imitates the plumbing, not a real model: the demo extractor's values, plus arm-shaped format noise."""
    msg = prompt.split('<<<\n', 1)[1].split('\n>>>', 1)[0]
    rec = json.loads(demo_extractor.extract(msg))
    if rec['product'] is None:
        rec['product'] = 'rice'
    if 'Our business checks found' in prompt:
        if 'its currency' in prompt and rec['paid_toman'] and 'ریال' in msg:
            rec['paid_toman'] //= 10
        return json.dumps(rec, ensure_ascii=False)
    h = _h(msg + ('S' if schema else '') + ('P' if 'JSON Schema' in prompt else ''))
    if schema is not None:                                   # constrained decoding: always fits the schema
        rec['quantity'] = None if rec['quantity'] is None else float(rec['quantity'])
        return json.dumps(rec, ensure_ascii=False)
    if 'JSON Schema' in prompt:
        if h < 5:
            return 'Here is the record:\n' + json.dumps(rec, ensure_ascii=False)
        if h < 10:
            rec['paid_toman'] = str(rec['paid_toman'])
        return '```json\n' + json.dumps(rec, ensure_ascii=False) + '\n```' if h % 3 == 0 else json.dumps(rec)
    if h < 15:
        return 'Sure! The order is: ' + json.dumps(rec, ensure_ascii=False)
    if h < 25:
        rec['paid_toman'] = f'{rec["paid_toman"]:,} toman' if rec['paid_toman'] else None
    if h < 30:
        rec['price'] = rec.pop('paid_toman')
    return json.dumps(rec, ensure_ascii=False)


from local_stage import cmd_local, faults  # noqa: E402,F401  (the local stage lives in local_stage.py)


# ── model stage ──────────────────────────────────────────────────────────────────────────────────
def model_id():
    import llm
    provider, name = llm.resolve('main')
    return f'{provider}:{name}', f'{provider}-{name}'.replace('/', '_').replace(':', '_')


def load_prices(path=PRICES):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'models': {}}


def plan_numbers(rows, arms, out_tokens):
    sys_t = len(SYSTEM) / CHARS_PER_TOKEN
    calls, tin = 0, 0
    for arm in arms:
        for r in rows:
            calls += 1
            tin += sys_t + len(prompt_for(arm, r['message'])) / CHARS_PER_TOKEN
    repairs = len(rows) if 'native' in arms else 0       # upper bound: every native record repaired once
    tin += repairs * (sys_t + len(repair_prompt('x' * 120, {'a': 1}, ['x' * 120])) / CHARS_PER_TOKEN + 900 / CHARS_PER_TOKEN)
    return calls, repairs, int(tin), int((calls + repairs) * out_tokens)


def price_lines(mid, tin, tout, calls_total):
    """Dollar lines for plan/run: the owner's price if filled, else an UPPER BOUND from the dated conservative
    fallback in prices.json, using MAX_TOKENS output for every call (HMD-021 convention)."""
    prices = load_prices()
    provider = mid.split(':', 1)[0] if ':' in mid else None
    p = prices.get('models', {}).get(mid, {})
    upper_out = calls_total * MAX_TOKENS
    if provider in ('mock', 'ollama'):
        return [f'model {mid}: no API cost']
    if p.get('input_per_mtok') is not None and p.get('output_per_mtok') is not None:
        usd = tin / 1e6 * p['input_per_mtok'] + tout / 1e6 * p['output_per_mtok']
        top = tin / 1e6 * p['input_per_mtok'] + upper_out / 1e6 * p['output_per_mtok']
        return [f'estimated cost ≈ ${usd:,.2f}; upper bound ≤ ${top:,.2f} if every call used all {MAX_TOKENS} output '
                f'tokens (prices.json, read {prices.get("date_read")})']
    fb = prices.get('fallback', {})
    fp = fb.get(provider) or fb.get('default') or {}
    if fp.get('input_per_mtok') is None or provider is None:
        return ['cost: no price for this model in prices.json; fill it in, with the date you read it']
    top = tin / 1e6 * fp['input_per_mtok'] + upper_out / 1e6 * fp['output_per_mtok']
    return [f'model {mid}: UPPER BOUND ≤ ${top:,.2f} using the conservative fallback price in prices.json '
            f'(${fp["input_per_mtok"]}/${fp["output_per_mtok"]} per M tokens, set {fb.get("set_on")}; NOT an official '
            f'price) and {calls_total} calls × {MAX_TOKENS} output tokens = {upper_out:,} (worst case). '
            f'Fill prices.json for a real figure.']


def cmd_plan(args, quiet=False):
    rows = load(args.split)[:args.limit or None]
    calls, repairs, tin, tout = plan_numbers(rows, args.arms, args.out_tokens)
    try:
        mid, _ = model_id()
    except Exception as e:  # noqa: BLE001
        mid = f'(no model configured: {e})'
    lines = [f'model: {mid} · split {args.split} · {len(rows)} messages · arms {", ".join(args.arms)}',
             f'calls: {calls} + at most {repairs} repair calls (only records the rules reject)',
             f'input ≈ {tin:,} tokens (characters ÷ {CHARS_PER_TOKEN}) · output ≈ {tout:,} tokens '
             f'(assumes {args.out_tokens} per call, reasoning included)']
    lines += price_lines(mid, tin, tout, calls + repairs)
    if not quiet:
        print('\n'.join(lines))
    return calls + repairs


def cmd_run(args, out_root=RUNS, ask=True):
    import llm
    mid, slug = model_id()
    test_sha = verify_frozen()
    rows = load(args.split)[:args.limit or None]
    cmd_plan(args)
    if ask and not mid.startswith(('mock:', 'ollama:')):
        if input('Spend money on these calls? [y/N] ').strip().lower() != 'y':
            print('Nothing sent.')
            return 1
    out = out_root / slug
    out.mkdir(parents=True, exist_ok=True)
    path = out / f'rows-{args.split}.jsonl'
    done = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            x = json.loads(line)
            done[(x['arm'], x['id'])] = x
    print(llm.describe())

    def ask_model(prompt, native):
        return llm.call(prompt, system=SYSTEM, max_tokens=MAX_TOKENS, cache_dir=out / 'cache', mock=mock_model,
                        schema=checks.SCHEMA if native else None)

    def row(arm, r, res, L):
        return {'id': r['id'], 'split': r['split'], 'group': r['group'], 'category': r['category'], 'arm': arm,
                'model': mid, 'model_served': res.model_served, 'fell_back': res.fell_back,
                'stop_reason': res.stop_reason, 'input_tokens': res.input_tokens, 'output_tokens': res.output_tokens,
                'latency_s': round(res.latency_s, 3), 'cached': res.cached, 'reply': res.text,
                'effort': os.environ.get('HOMODYNE_EFFORT', 'medium'), 'test_sha256': test_sha,
                **{k: L[k] for k in ('parse_ok', 'schema_ok', 'rule_ok', 'rule_violations', 'rule_messages', 'repair_hints',
                                     'missing', 'fields', 'correct', 'silent_error', 'record')}}
    for arm in args.arms:
        for i, r in enumerate(rows, 1):
            res = ask_model(prompt_for(arm, r['message']), arm == 'native')
            done[(arm, r['id'])] = row(arm, r, res, checks.lights(res.text, r['truth'], r['message']))
            if i % 20 == 0 or i == len(rows):
                print(f'  {arm}: {i}/{len(rows)}')
    if 'native' in args.arms:                            # arm 4: one repair call for records the rules reject
        n = 0
        for r in rows:
            first = done[('native', r['id'])]
            if first['schema_ok'] and not first['missing'] and not first['rule_ok']:
                res = ask_model(repair_prompt(r['message'], first['record'], first['repair_hints']), True)
                done[('repair', r['id'])] = row('repair', r, res, checks.lights(res.text, r['truth'], r['message']))
                n += 1
        print(f'  repair calls: {n}')
    path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in done.values()), encoding='utf-8')
    fb = sum(x['fell_back'] for x in done.values())
    print(f'wrote {path}' + (f' · {fb} replies came from a fallback model (see model_served)' if fb else ''))
    return 0


# ── self-test ────────────────────────────────────────────────────────────────────────────────────
def selftest():
    import time
    t0 = time.time()
    if not os.environ.get('HOMODYNE_MODEL', '').startswith('mock:'):
        print('selftest needs HOMODYNE_MODEL=mock:echo (no key, no network, no cost)')
        return 2
    import llm
    import report
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(('  ok    ' if cond else '  FAIL  ') + name)
    check('Jalali: 1 Farvardin 1406 = 2027-03-21; 18 Farvardin = today; 1 Ordibehesht = today + 14',
          world.jalali_to_gregorian(1406, 1, 1) == dt.date(2027, 3, 21) and world.gregorian_to_jalali(world.TODAY) ==
          (1406, 1, 18) and world.jalali_to_gregorian(1406, 2, 1) == world.TODAY + dt.timedelta(days=14))
    check('Jalali: leap years 1399 (30 Esfand = 2021-03-20) and 1403 (1 Farvardin = 2024-03-20)',
          world.jalali_to_gregorian(1399, 12, 30) == dt.date(2021, 3, 20) and
          world.jalali_to_gregorian(1403, 1, 1) == dt.date(2024, 3, 20))
    check('generator is deterministic and matches the frozen test file',
          ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in world.make_split('test')) ==
          (DATA / 'test.jsonl').read_text(encoding='utf-8'))
    rows = load('test')
    check('test split: 100 messages, 11 groups; dev split is separate', len(rows) == 100 and
          len({r['group'] for r in rows}) == 11 and not {r['message'] for r in rows} & {r['message'] for r in load('dev')})
    check('every answer key passes the schema', all(not checks.validate_schema(r['truth']) for r in rows))
    good = {'product': 'rice', 'quantity': 5, 'unit': 'kg', 'paid_toman': 1500000, 'delivery_date': '2027-04-08'}
    check('schema: amount as text fails; Jalali-in-ISO passes the schema but breaks the date rule',
          checks.validate_schema({**good, 'paid_toman': '1,500,000'}) and
          not checks.validate_schema({**good, 'delivery_date': '1406-01-19'}) and
          checks.check_rules({**good, 'delivery_date': '1406-01-19'})[0][0] == 'date')
    check('rules: ×10 amount is a price violation; 750 g cheese = 0.75 kg passes',
          checks.check_rules({**good, 'paid_toman': 15000000})[0][0] == 'price' and
          not checks.check_rules({'product': 'cheese', 'quantity': 750, 'unit': 'g', 'paid_toman': 300000,
                                  'delivery_date': '2027-04-08'}))
    check('grader: 750 g = 0.75 kg; a null in the key must stay null',
          checks.grade({'product': 'cheese', 'quantity': 0.75, 'unit': 'kg', 'paid_toman': 1, 'delivery_date': 'x'},
                       {'product': 'cheese', 'quantity': 750, 'unit': 'g', 'paid_toman': 1,
                        'delivery_date': 'x'})['quantity'] and
          not checks.grade({**good}, {**good, 'quantity': None})['quantity'])
    check('parse: a code fence is tolerated, words around the object are not',
          checks.parse_reply('```json\n{"a": 1}\n```')[0] == {'a': 1} and checks.parse_reply('Sure: {"a": 1}')[0] is None)
    seen = []
    llm.call('x <<<\nسلام\n>>>', model='mock:echo', mock=lambda p, schema=None: seen.append(schema) or '{}',
             schema=checks.SCHEMA)
    check('tools/llm.py passes schema= through to the mock', seen and seen[0] == checks.SCHEMA)
    import llm as _llm
    check('tools/llm.py strips $comment before sending a schema', '$comment' not in _llm.clean_schema(checks.SCHEMA)
          and '$comment' in checks.SCHEMA)
    loc = cmd_local(argparse.Namespace(), write=False)
    fm = {m['fault']: m for m in loc['faults']}
    check('fault injection: amount ×10 and Jalali-in-ISO are never silent; text amount and cut-off are structure',
          fm['rial_read_as_toman']['silent'] == 0 and fm['jalali_in_iso']['silent'] == 0 and
          fm['amount_as_text']['structure'] == fm['amount_as_text']['n'] and
          fm['cut_off']['structure'] == fm['cut_off']['n'])
    check('fault injection: a date one day early is mostly silent', fm['one_day_early']['silent'] > fm['one_day_early']['n'] / 2)
    r5 = loc['rule5_effect']
    check('rule 5 on the demo: test 23 → 2 and dev 3 → 0 auto-recorded and wrong (the numbers spoken in beat 9)',
          (r5['test']['without_rule5']['auto_wrong'], r5['test']['with_rule5']['auto_wrong'],
           r5['dev']['without_rule5']['auto_wrong'], r5['dev']['with_rule5']['auto_wrong']) == (23, 2, 3, 0))
    check('the answer key: every record correct; only boundary and missing records leave the automatic path',
          loc['answer_key']['correct'] == 100 and all(i for i in loc['answer_key']['flagged_ids']))
    with tempfile.TemporaryDirectory() as tmp:
        args = argparse.Namespace(split='test', limit=0, arms=list(CALL_ARMS), out_tokens=800)
        cmd_run(args, out_root=Path(tmp), ask=False)
        rows_run = report.load_rows(Path(tmp), 'test')
        check('run: 300 first replies + one repair per rule-rejected native record',
              sum(x['arm'] != 'repair' for x in rows_run) == 300 and
              sum(x['arm'] == 'repair' for x in rows_run) == sum(x['arm'] == 'native' and x['schema_ok'] and
                                                                 not x['missing'] and not x['rule_ok'] for x in rows_run))
        s = report.summarise(rows_run, {'input_per_mtok': 4.0, 'output_per_mtok': 20.0}, report.truth_routes('test'))
        check('every row carries the frozen test-set hash', all(x['test_sha256'] == verify_frozen() for x in rows_run))
        bad = Path(tmp) / 'baddata'
        bad.mkdir()
        (bad / 'FROZEN.json').write_text((DATA / 'FROZEN.json').read_text())
        (bad / 'test.jsonl').write_text((DATA / 'test.jsonl').read_text().replace('T001', 'T00X', 1))
        try:
            verify_frozen(bad)
            check('run aborts when test.jsonl differs from FROZEN.json', False)
        except SystemExit:
            check('run aborts when test.jsonl differs from FROZEN.json', True)
        (Path(tmp) / 'mock-echo' / 'rows-test.jsonl').write_text(''.join(
            json.dumps({**x, 'test_sha256': 'f' * 64}) + '\n' for x in rows_run))
        try:
            report.load_rows(Path(tmp), 'test')
            check('report aborts on rows made from another test set', False)
        except SystemExit:
            check('report aborts on rows made from another test set', True)
        wrong = {'product': 'rice', 'quantity': 5, 'unit': 'kg', 'paid_toman': 15000000, 'delivery_date': '2027-04-08'}
        rp = repair_prompt('x', wrong, checks.lights(json.dumps(wrong), wrong)['repair_hints'])
        check('repair prompt names the rule, never the catalog total',
              'catalog total' not in rp and '1,500,000' not in rp and 'ratio' not in rp)
        check('false alarms exclude orders the answer key itself sends to a person',
              s['native']['false_alarm'] <= sum(x['correct'] and x['arm'] == 'native' for x in rows_run))
        check('mock native arm: every reply parses and fits the schema', s['native']['parse'] == 100 and
              s['native']['schema'] == 100)
        check('mock free arm: some replies fail to parse (prose around JSON)', s['free']['parse'] < 100)
        check('routing adds up to 100', sum(s['native_rules']['routes'].values()) == 100)
        check('silent errors = schema-valid and wrong', all(s[a]['silent'] == s[a]['schema'] - s[a]['correct_valid']
                                                             for a in CALL_ARMS))
        try:
            txt = report.render(s, {'date_read': '2027-01-01'}, 'mock:echo', 'test')
            check('report renders, with spoken lines for beats 10–12', '[10]' in txt and '[12]' in txt)
        except Exception as e:  # noqa: BLE001
            check(f'report renders ({e!r})', False)
    took = time.time() - t0
    check(f'under 60 seconds ({took:.1f} s)', took < 60)
    print('SELFTEST ' + ('PASSED' if ok else 'FAILED'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description='HMD-020 · Structured Output Testbench')
    ap.add_argument('--selftest', action='store_true')
    sub = ap.add_subparsers(dest='cmd')
    g = sub.add_parser('generate')
    g.add_argument('--force', action='store_true')
    sub.add_parser('local', help='LOCAL, free: answer key, fault injection, demo extractor → results/')
    for name in ('plan', 'run'):
        p = sub.add_parser(name)
        p.add_argument('--split', default='test', choices=['test', 'dev'])
        p.add_argument('--limit', type=int, default=0, help='first N messages only (try 3 first)')
        p.add_argument('--arms', nargs='+', default=list(CALL_ARMS), choices=CALL_ARMS)
        p.add_argument('--out-tokens', type=int, default=800, help='assumed output tokens per call, for the estimate')
        if name == 'run':
            p.add_argument('--yes', action='store_true', help='do not ask before spending')
    r = sub.add_parser('report')
    r.add_argument('--split', default='test', choices=['test', 'dev'])
    r.add_argument('--model', help='folder under runs/ when several models were run')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.cmd == 'generate':
        return cmd_generate(args)
    if args.cmd == 'local':
        cmd_local(args)
        return 0
    if args.cmd == 'plan':
        cmd_plan(args)
        return 0
    if args.cmd == 'run':
        return cmd_run(args, ask=not args.yes)
    if args.cmd == 'report':
        import report
        return report.cmd_report(args)
    ap.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
