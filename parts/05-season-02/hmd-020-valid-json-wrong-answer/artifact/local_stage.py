"""HMD-020 · local stage: no model at all. The answer key, fault injection and the demo extractor through the lights."""

import copy
import datetime as dt
import json
from collections import Counter
from pathlib import Path

import checks
import demo_extractor
import world

HERE = Path(__file__).resolve().parent
RESULTS = HERE / 'results'


def load(split):
    return [json.loads(x) for x in (HERE / 'data' / f'{split}.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]


def _dump(rec):
    return json.dumps(rec, ensure_ascii=False)


def faults():
    """Known corruptions applied to the answer key: which light catches each? (name, applies?, corrupt → text)"""
    def change(field, fn):
        def f(t):
            r = copy.deepcopy(t)
            r[field] = fn(r)
            return _dump(r)
        return f

    def jalali_iso(r):
        jy, jm, jd = world.gregorian_to_jalali(dt.date.fromisoformat(r['delivery_date']))
        return f'{jy:04d}-{jm:02d}-{jd:02d}'

    def day_before(r):
        return (dt.date.fromisoformat(r['delivery_date']) - dt.timedelta(days=1)).isoformat()

    def invent(t):
        r = copy.deepcopy(t)
        if r['quantity'] is None:
            r['quantity'], r['unit'] = 1, r['unit'] or world.CATALOG[r['product']][3]
        if r['delivery_date'] is None:
            r['delivery_date'] = (world.TODAY + dt.timedelta(days=1)).isoformat()
        return _dump(r)

    def unit_swap(t):
        r = copy.deepcopy(t)
        r['unit'] = 'g'
        return _dump(r)

    def size_as_qty(t):
        r = copy.deepcopy(t)
        r['quantity'] = r['quantity'] + 2
        return _dump(r)

    def renamed(t):
        r = copy.deepcopy(t)
        r['price'] = r.pop('paid_toman')
        return _dump(r)
    return [
        ('rial_read_as_toman', 'amount ×10 (ریال read as تومن)', lambda t: t['paid_toman'] is not None,
         change('paid_toman', lambda r: r['paid_toman'] * 10)),
        ('thousand_dropped', 'amount ÷1000 («۴۵۰ تومن» read literally)', lambda t: t['paid_toman'] is not None,
         change('paid_toman', lambda r: r['paid_toman'] // 1000)),
        ('jalali_in_iso', 'Jalali date written as YYYY-MM-DD (1406-01-25)', lambda t: t['delivery_date'] is not None,
         change('delivery_date', jalali_iso)),
        ('one_day_early', 'date one day early («پس‌فردا» read as «فردا»)', lambda t: t['delivery_date'] is not None,
         change('delivery_date', day_before)),
        ('kg_written_as_g', 'unit g, number unchanged (5 kg → 5 g)', lambda t: t['unit'] == 'kg' and t['quantity'],
         unit_swap),
        ('size_as_quantity', 'item size read as quantity (+2 pieces)', lambda t: t['unit'] == 'piece', size_as_qty),
        ('invented_missing', 'missing value invented (quantity 1 / tomorrow)',
         lambda t: t['quantity'] is None or t['delivery_date'] is None, invent),
        ('amount_as_text', 'amount as text "1,500,000"', lambda t: t['paid_toman'] is not None,
         change('paid_toman', lambda r: f'{r["paid_toman"]:,}')),
        ('cut_off', 'reply cut off before the last bracket', lambda t: True, lambda t: _dump(t)[:-1]),
        ('renamed_field', 'field renamed (price instead of paid_toman)', lambda t: True, renamed),
    ]


def first_catch(L):
    if not L['parse_ok']:
        return 'structure'
    if not L['schema_ok']:
        return 'structure'
    if L['missing'] or not L['rule_ok']:
        return 'rule'
    return 'none'


def cmd_local(args, write=True):
    rows = load('test')
    out = {'date_run': dt.date.today().isoformat(), 'n': len(rows)}
    # 1. the answer key itself through the lights: what do perfect records cost?
    truth_l = [checks.lights(_dump(r['truth']), r['truth'], r['message']) for r in rows]
    truth_route = {r['id']: checks.route(L) for r, L in zip(rows, truth_l)}
    routes = Counter(checks.route(L) for L in truth_l)
    out['answer_key'] = {'schema_ok': sum(L['schema_ok'] for L in truth_l), 'correct': sum(L['correct'] for L in truth_l),
                         'routes': dict(routes),
                         'rule_flags': dict(Counter(v for L in truth_l for v in L['rule_violations'])),
                         'flagged_ids': [r['id'] for r, L in zip(rows, truth_l) if checks.route(L) != 'auto']}
    # 2. fault injection
    matrix = []
    for name, label, applies, corrupt in faults():
        # only records whose correct version is recorded automatically, so a catch is caused by the fault itself
        # (the missing-value fault is the exception: it applies exactly to the records with nothing to record)
        hit = [r for r in rows if applies(r['truth']) and
               (truth_route[r['id']] == 'auto') != (name == 'invented_missing')]
        caught = Counter(first_catch(checks.lights(corrupt(r['truth']), r['truth'], r['message'])) for r in hit)
        matrix.append({'fault': name, 'label': label, 'n': len(hit), 'structure': caught['structure'],
                       'rule': caught['rule'], 'silent': caught['none']})
    out['faults'] = matrix
    # 3. the demo extractor (a regex program, not AI), with rule 5 (message given) and without it (message=None)
    def demo_summary(split):
        res = {}
        for label, use_msg in (('with_rule5', True), ('without_rule5', False)):
            auto_wrong, auto, groups = 0, 0, Counter()
            data = load(split)
            for r in data:
                L = checks.lights(demo_extractor.extract(r['message']), r['truth'], r['message'] if use_msg else None)
                if checks.route(L) == 'auto':
                    auto += 1
                    if not L['correct']:
                        auto_wrong += 1
                        groups[r['group']] += 1
            res[label] = {'n': len(data), 'auto': auto, 'auto_wrong': auto_wrong, 'by_group': dict(groups)}
        return res
    out['rule5_effect'] = {'test': demo_summary('test'), 'dev': demo_summary('dev')}
    demo = []
    for r in rows:
        text = demo_extractor.extract(r['message'])
        L = checks.lights(text, r['truth'], r['message'])
        demo.append({'id': r['id'], 'group': r['group'], 'reply': text, **{k: L[k] for k in (
            'parse_ok', 'schema_ok', 'rule_ok', 'missing', 'correct', 'silent_error', 'rule_violations')},
            'route': checks.route(L)})
    n = len(demo)
    auto = [d for d in demo if d['route'] == 'auto']
    out['demo'] = {'parse_ok': sum(d['parse_ok'] for d in demo), 'schema_ok': sum(d['schema_ok'] for d in demo),
                   'correct': sum(d['correct'] for d in demo), 'silent': sum(d['silent_error'] for d in demo),
                   'wrong_and_flagged': sum(d['silent_error'] and d['route'] != 'auto' for d in demo),
                   'auto': len(auto), 'auto_wrong': sum(not d['correct'] for d in auto),
                   'silent_by_group': dict(Counter(d['group'] for d in auto if not d['correct'])), 'n': n}
    text = local_text(out)
    print(text)
    if write:
        RESULTS.mkdir(exist_ok=True)
        (RESULTS / 'local.txt').write_text(text + '\n', encoding='utf-8')
        (RESULTS / 'local.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        (RESULTS / 'demo-per-record.jsonl').write_text(''.join(json.dumps(d, ensure_ascii=False) + '\n' for d in demo),
                                                       encoding='utf-8')
    return out


def local_text(o):
    from stats import words_fa
    a, d = o['answer_key'], o['demo']
    L = [f'HMD-020 · LOCAL RUN · {o["date_run"]} · no model called · ILLUSTRATIVE data · test split n={o["n"]}', '',
         '1. The answer key itself, through the lights (what a PERFECT extractor would get)',
         f'   schema ok {a["schema_ok"]}/{o["n"]} · correct {a["correct"]}/{o["n"]} · routes {a["routes"]}',
         f'   rule flags on correct records: {a["rule_flags"]}', '',
         '2. Fault injection: one known error put into each applicable correct record. First light that catches it:',
         f'   {"fault":<20}{"n":>4}{"structure":>11}{"rule":>6}{"silent":>8}   what']
    for m in o['faults']:
        L.append(f'   {m["fault"]:<20}{m["n"]:>4}{m["structure"]:>11}{m["rule"]:>6}{m["silent"]:>8}   {m["label"]}')
    L += ['', '3. DEMO extractor (a deliberately simple regex program, NOT an AI model)',
          f'   valid JSON {d["parse_ok"]}/{d["n"]} · schema ok {d["schema_ok"]}/{d["n"]} · fully correct '
          f'{d["correct"]}/{d["n"]} · schema-valid but wrong {d["silent"]}/{d["n"]}',
          f'   of those, stopped by rules or missing-value check: {d["wrong_and_flagged"]} · recorded automatically: '
          f'{d["auto"]}, of which wrong: {d["auto_wrong"]} {d["silent_by_group"]}', '',
          '4. Rule 5 (an amount or payment the message mentions may not come back null), added after seeing (3):']
    for split, v in o['rule5_effect'].items():
        w, wo = v['with_rule5'], v['without_rule5']
        L.append(f'   {split:<5} recorded automatically and wrong: without rule 5 {wo["auto_wrong"]}/{wo["n"]} '
                 f'{wo["by_group"]} · with rule 5 {w["auto_wrong"]}/{w["n"]} {w["by_group"]}')
    L += ['',
          'Spoken lines (local, real numbers):']
    fm = {m['fault']: m for m in o['faults']}
    r10, early = fm['rial_read_as_toman'], fm['one_day_early']
    L.append(f'  [8] وقتی مبلغ رو ده برابر کردم، قانون قیمت از {words_fa(r10["n"])} مورد، '
             f'{words_fa(r10["rule"])} تاش رو گرفت.')
    L.append(f'  [8] یه روز جابه‌جایی تاریخ: از {words_fa(early["n"])} مورد، {words_fa(early["silent"])} تاش از هر سه '
             f'قالب و قانون رد شد.')
    L.append(f'  [9] برنامهٔ ساده: {words_fa(d["parse_ok"])} از صد فرم مرتب؛ {words_fa(d["correct"])} تا کاملاً درست.')
    t5 = o['rule5_effect']['test']
    L.append(f'  [9] قبل از این قانون، {words_fa(t5["without_rule5"]["auto_wrong"])} سفارش غلط خودکار ثبت می‌شد؛ '
             f'بعدش {words_fa(t5["with_rule5"]["auto_wrong"])} تا.')
    L.append(f'  [9] حتی جواب‌نامهٔ بی‌نقص هم {words_fa(o["n"] - a["routes"].get("auto", 0))} سفارش از صد رو '
             f'می‌فرسته پیش آدم.')
    return '\n'.join(L)
