"""HMD-020 · report: per-arm metrics with denominators, intervals, and the Persian spoken lines for the [RUN] beats."""

import json
from collections import Counter
from pathlib import Path

import checks
from stats import mcnemar_exact, paired_bootstrap, pct_words, wilson, words_fa

HERE = Path(__file__).resolve().parent
ARMS = ('free', 'schema_prompt', 'native')
ARM_FA = {'free': 'آزاد', 'schema_prompt': 'قالب توی متن', 'native': 'قالب اجباری'}
GROUP_FA = {'clean': 'پیام‌های ساده', 'digits': 'رقم و جداکننده', 'rial': 'مبلغ به ریال',
            'colloquial': 'تومنِ بی‌هزار', 'spoken': 'مبلغ با حروف', 'relative_date': 'روزهای نسبی مثل پس‌فردا',
            'jalali_date': 'تاریخ شمسی', 'ranges': 'بازه و اندازه', 'units': 'گرم و کیلو و شونه',
            'missing': 'مقدارِ گفته‌نشده', 'boundary': 'سفارش‌های مرزی'}
MAX_AUTO_WRONG = 2      # locked before the run: auto-recording is accepted only if ≤ 2 of 100 orders are auto and wrong


def frozen_sha(data_dir=HERE / 'data'):
    import hashlib
    want = json.loads((data_dir / 'FROZEN.json').read_text())['test.jsonl']
    got = hashlib.sha256((data_dir / 'test.jsonl').read_bytes()).hexdigest()
    if got != want:
        raise SystemExit('data/test.jsonl does not match data/FROZEN.json; the frozen test set was changed.')
    return got


def truth_routes(split, data_dir=HERE / 'data'):
    """Where the ANSWER KEY itself goes (auto / human_*): flags on these are by design, not false alarms."""
    out = {}
    for line in (data_dir / f'{split}.jsonl').read_text(encoding='utf-8').splitlines():
        if line.strip():
            r = json.loads(line)
            out[r['id']] = checks.route(checks.lights(json.dumps(r['truth'], ensure_ascii=False), r['truth'], r['message']))
    return out


def load_rows(root, split, slug=None, data_dir=HERE / 'data'):
    files = sorted(root.glob(f'*/rows-{split}.jsonl')) if root.exists() else []
    if slug:
        files = [root / slug / f'rows-{split}.jsonl']
    if not files:
        raise SystemExit('No run yet. python3 testbench.py run   (or --selftest for a dry run)')
    if len(files) > 1:
        raise SystemExit('Several models in runs/: pass --model ' + ' | '.join(f.parent.name for f in files))
    rows = [json.loads(x) for x in files[0].read_text(encoding='utf-8').splitlines() if x.strip()]
    if split == 'test':
        sha = frozen_sha(data_dir)
        bad = sum(r.get('test_sha256') != sha for r in rows)
        if bad:
            raise SystemExit(f'{bad} rows were produced on a different test.jsonl than data/FROZEN.json; re-run.')
    return rows


def cost(rows, price):
    tin, tout = sum(r['input_tokens'] for r in rows), sum(r['output_tokens'] for r in rows)
    usd = None
    if price and price.get('input_per_mtok') is not None and price.get('output_per_mtok') is not None:
        usd = tin / 1e6 * price['input_per_mtok'] + tout / 1e6 * price['output_per_mtok']
    return tin, tout, usd


def summarise(rows, price, truth_route=None):
    by = {a: sorted([r for r in rows if r['arm'] == a], key=lambda r: r['id']) for a in ARMS}
    rep = {r['id']: r for r in rows if r['arm'] == 'repair'}
    s = {}
    for a, rs in by.items():
        n = len(rs)
        flagged = [r['schema_ok'] and (bool(r['missing']) or not r['rule_ok']) for r in rs]
        silent = [r['silent_error'] for r in rs]
        tin, tout, usd = cost(rs, price)
        correct = sum(r['correct'] for r in rs)
        s[a] = {'n': n, 'parse': sum(r['parse_ok'] for r in rs), 'schema': sum(r['schema_ok'] for r in rs),
                'correct': correct, 'correct_ci': wilson(correct, n),
                'correct_valid': sum(r['correct'] and r['schema_ok'] for r in rs),
                'field_correct': {f: sum(r['fields'][f] for r in rs) for f in checks.FIELDS},
                'silent': sum(silent), 'silent_ci': wilson(sum(silent), n),
                'caught': sum(x and f for x, f in zip(silent, flagged)),
                'slipped': sum(x and not f for x, f in zip(silent, flagged)),
                # correct records the rules stopped, minus the ones the answer key itself sends to a person
                'false_alarm': sum(r['correct'] and f and (truth_route or {}).get(r['id'], 'auto') == 'auto'
                                   for r, f in zip(rs, flagged)),
                'caught_by_group': dict(Counter(r['group'] for r, f in zip(rs, flagged) if r['silent_error'] and f)),
                'slipped_by_group': dict(Counter(r['group'] for r, f in zip(rs, flagged) if r['silent_error'] and not f)),
                'tokens_in': tin, 'tokens_out': tout, 'usd': usd,
                'fell_back': sum(r['fell_back'] for r in rs), 'model': rs[0]['model'] if rs else '',
                'vec_correct': [int(r['correct']) for r in rs], 'vec_silent': [int(r['silent_error']) for r in rs]}
        s[a]['field_acc'] = sum(s[a]['field_correct'].values()) / (len(checks.FIELDS) * n) if n else 0
    nat = by['native']
    routes, auto_ok, auto_bad, rep_ok, rep_bad, groups_bad = Counter(), 0, 0, 0, 0, Counter()
    for r in nat:
        rr = rep.get(r['id'])
        route = checks.route(r, rr)
        routes[route] += 1
        final = rr if route == 'auto_repaired' else r
        if route.startswith('auto'):
            auto_ok += final['correct']
            auto_bad += not final['correct']
            if not final['correct']:
                groups_bad[r['group']] += 1
        if route == 'auto_repaired':
            rep_ok += final['correct']
            rep_bad += not final['correct']
    tin, tout, usd = cost(nat + list(rep.values()), price)
    auto = auto_ok + auto_bad
    s['native_rules'] = {'n': len(nat), 'routes': dict(routes), 'auto': auto, 'auto_correct': auto_ok,
                         'auto_wrong': auto_bad, 'auto_wrong_ci': wilson(auto_bad, len(nat)),   # out of all 100
                         'auto_wrong_by_group': dict(groups_bad), 'repair_calls': len(rep),
                         'repaired_correct': rep_ok, 'repaired_still_wrong': rep_bad,
                         'human': sum(v for k, v in routes.items() if k.startswith('human')),
                         'tokens_in': tin, 'tokens_out': tout, 'usd': usd}
    pairs = {}
    for a, b in (('free', 'native'), ('schema_prompt', 'native'), ('free', 'schema_prompt')):
        if by[a] and by[b] and [r['id'] for r in by[a]] == [r['id'] for r in by[b]]:
            pairs[f'{a}-{b}'] = {'correct': paired_bootstrap(s[b]['vec_correct'], s[a]['vec_correct']),
                                 'correct_mcnemar': mcnemar_exact(s[b]['vec_correct'], s[a]['vec_correct']),
                                 'silent': paired_bootstrap(s[b]['vec_silent'], s[a]['vec_silent'])}
    s['pairs'] = pairs
    return s


def money_fa(usd):
    if usd is None:
        return None
    cents = round(usd * 100)
    if cents < 100:
        return f'حدود {words_fa(max(cents, 1))} سنت'
    return f'حدود {words_fa(round(usd))} دلار' if usd >= 10 else f'حدود {words_fa(int(usd))} دلار و {words_fa(cents % 100)} سنت'


def top(d):
    return max(d.items(), key=lambda kv: kv[1])[0] if d else None


def spoken(s, meta, model, split):
    """The exact Persian lines of script-fa.md beats 10–12, with this run's numbers written as words."""
    f, p, nat, nr = s['free'], s['schema_prompt'], s['native'], s['native_rules']
    n, w = nat['n'], words_fa
    L = [f'[10] همون {w(n)} پیام، یه مدل: {model}.',
         f'[10] روش آزاد: {w(f["parse"])} فرم خونده شد، {w(f["schema"])} تا توی قالب هم جا شد.',
         f'[10] قالب توی متن: {w(p["parse"])} و {w(p["schema"])}. قالب اجباری: {w(nat["parse"])} و {w(nat["schema"])}؛ همه از {w(n)}.',
         f'[10] حالا معنی. سفارش کاملاً درست: آزاد {w(f["correct"])}، قالب توی متن {w(p["correct"])}. قالب اجباری {w(nat["correct"])}.',
         f'[10] و ستارهٔ امروز، فرم بی‌نقص با جواب غلط: آزاد {w(f["silent"])}، قالب توی متن {w(p["silent"])}. قالب اجباری {w(nat["silent"])}؛ از {w(n)}.']
    lo, hi = nat['correct_ci']
    L.append(f'[10] بازهٔ اطمینانِ درستیِ قالب اجباری از {w(round(100 * lo))} درصد تا {w(round(100 * hi))} درصده؛ '
             f'یعنی با {w(n)} پیام، عدد واقعی احتمالاً همین وسطه.')
    pr = s['pairs'].get('free-native')
    if pr:
        d, lo, hi = pr['correct']
        pts = w(abs(round(100 * d)))
        if lo > 0 or hi < 0:
            L.append(f'[10] شاخهٔ الف · فرق درستیِ قالب اجباری و روش آزاد {pts} واحد درصده، و بازه‌ش صفر رو شامل نمی‌شه.')
        else:
            L.append(f'[10] شاخهٔ ب · فرقشون {pts} واحد درصده، ولی بازه‌ش صفر رو هم شامل می‌شه؛ پس نمی‌تونم بگم قالب '
                     f'اجباری جواب‌ها رو درست‌تر کرد.')
        _, slo, _ = pr['silent']
        loud_dropped = nat['schema'] > f['schema']
        if slo > 0 and loud_dropped:
            L.append('[11] شاخهٔ الف · قالب اجباری خطای پرسروصدا رو کم کرد؛ یعنی فرمی که سیستم همون اول ردش می‌کنه. '
                     'ولی بخشی از همون خطاها فقط بی‌صدا شدن.')
        else:
            L.append('[11] شاخهٔ ب · این بار نمی‌تونم بگم قالب اجباری خطای بی‌صدا رو بیشتر کرد.')
    g = top(nat['caught_by_group'])
    L.append(f'[11] حالا چراغ قانون. از {w(nat["silent"])} خطای بی‌صدای قالب اجباری، قانون‌ها {w(nat["caught"])} تا رو نگه '
             f'داشتن' + (f'؛ بیشترشون از گروه «{GROUP_FA[g]}».' if g else '.'))
    if nat['slipped']:
        L.append(f'[11] شاخهٔ الف · {w(nat["slipped"])} تا از قالب و قانون رد شدن؛ بیشترشون از گروه '
                 f'«{GROUP_FA[top(nat["slipped_by_group"])]}».')
    else:
        L.append('[11] شاخهٔ ب · هیچ خطای بی‌صدایی از قالب و قانون رد نشد.')
    tail = (f'{w(nr["repaired_still_wrong"])} تا از قانون رد شدن ولی هنوز غلط بودن.' if nr['repaired_still_wrong']
            else 'هیچ‌کدوم با اصلاحِ ظاهری از قانون رد نشد.')
    L.append(f'[11] برای {w(nr["repair_calls"])} سفارش یه بار اصلاح خواستیم و {w(nr["repaired_correct"])} تا درست شدن. ' + tail)
    L.append(f'[11] قانون‌ها {w(nat["false_alarm"])} سفارشِ کاملاً درست رو هم بی‌دلیل نگه داشتن؛ این هزینهٔ احتیاطه.')
    L.append(f'[11] یادت باشه: یه مدل، یه دستور، یه روز، {w(n)} پیام ساختگی.')
    L.append(f'[12] با این اجرا، {w(nr["auto"])} سفارش از {w(n)} خودکار ثبت می‌شه و {w(nr["human"])} تا می‌ره پیش آدم.')
    L.append(f'[12] از {w(nr["auto"])} سفارش خودکار، {w(nr["auto_wrong"])} تا غلط بودن.')
    L.append(f'[12] با {w(n)} پیام، عدد واقعی ممکنه تا حدود {w(round(100 * nr["auto_wrong_ci"][1]))} درصد باشه.')
    money = money_fa(nr['usd'] / nr['auto_correct']) if nr['usd'] is not None and nr['auto_correct'] else None
    L.append(f'[12] هزینهٔ هر سفارش درستِ خودکار: {money}.' if money else
             f'[12] هزینهٔ هر سفارش درستِ خودکار حدود {w((nr["tokens_in"] + nr["tokens_out"]) // max(nr["auto_correct"], 1))} '
             f'توکنه؛ قیمت مدل رو هنوز وارد نکردم.')
    if nr['auto_wrong'] <= MAX_AUTO_WRONG:
        L.append(f'[12] شاخهٔ الف · {w(nr["auto_wrong"])} از {w(n)}، زیر سقف. پس ثبت خودکار، به شرط تکرار تاریخ و مبلغ '
                 f'برای مشتری.')
    else:
        L.append(f'[12] شاخهٔ ب · {w(nr["auto_wrong"])} از {w(n)}، بالای سقف. پس فعلاً «{GROUP_FA[top(nr["auto_wrong_by_group"])]}» '
                 f'خودکار ثبت نمی‌شه و می‌ره پیش آدم.')
    fb = sum(s[a]['fell_back'] for a in ARMS)
    if fb:
        L.append(f'[10] (روی صفحه: {fb} جواب از مدل جایگزین آمد؛ model_served را ببین.)')
    if meta.get('date_read'):
        L.append(f'[12] (روی صفحه: قیمت‌ها از prices.json، خوانده‌شده در {meta["date_read"]}.)')
    return L


def pct(k, n):
    return f'{k}/{n} ({100 * k / n:.0f}%)' if n else '–'


def render(s, meta, model, split):
    n = s['native']['n']
    out = [f'HMD-020 · {model} · split {split} · n = {n} messages per arm · ILLUSTRATIVE data · prices read '
           f'{meta.get("date_read")}', '',
           f'{"":<26}' + ''.join(f'{a:>18}' for a in ARMS)]

    def line(label, fn):
        out.append(f'{label:<26}' + ''.join(f'{fn(s[a]):>18}' for a in ARMS))
    line('parses as JSON', lambda x: pct(x['parse'], x['n']))
    line('fits the schema', lambda x: pct(x['schema'], x['n']))
    line('field accuracy (4 fields)', lambda x: f'{100 * x["field_acc"]:.0f}% of {4 * x["n"]}')
    for f in checks.FIELDS:
        line(f'  {f}', lambda x, f=f: pct(x['field_correct'][f], x['n']))
    line('full record correct', lambda x: pct(x['correct'], x['n']))
    line('  95% Wilson', lambda x: f'{100 * x["correct_ci"][0]:.0f}–{100 * x["correct_ci"][1]:.0f}%')
    line('SILENT: schema ok, wrong', lambda x: pct(x['silent'], x['n']))
    line('  caught by rules', lambda x: f'{x["caught"]}/{x["silent"]}')
    line('  slipped past rules', lambda x: str(x['slipped']))
    line('correct but stopped*', lambda x: str(x['false_alarm']))
    line('tokens in / out', lambda x: f'{x["tokens_in"]:,}/{x["tokens_out"]:,}')
    line('cost per correct record', lambda x: f'${x["usd"] / x["correct"]:.4f}' if x['usd'] is not None and x['correct']
         else 'no price')
    nr = s['native_rules']
    out += ['', f'native_rules (arm 4): routes {nr["routes"]}',
            f'  recorded automatically {nr["auto"]}/{nr["n"]} · of which wrong {nr["auto_wrong"]} '
            f'(95% Wilson {100 * nr["auto_wrong_ci"][0]:.1f}–{100 * nr["auto_wrong_ci"][1]:.1f}% of all {nr["n"]} orders) '
            f'{nr["auto_wrong_by_group"]}',
            f'  repair calls {nr["repair_calls"]}: now pass and correct {nr["repaired_correct"]}, pass but still wrong '
            f'{nr["repaired_still_wrong"]} · human review {nr["human"]}/{nr["n"]}',
            f'  cost per correct auto-recorded order: ' + (f'${nr["usd"] / nr["auto_correct"]:.4f}'
                                                         if nr['usd'] is not None and nr['auto_correct'] else
                                                         f'{(nr["tokens_in"] + nr["tokens_out"]) // max(nr["auto_correct"], 1):,} tokens'),
            f'  locked acceptance rule: at most {MAX_AUTO_WRONG} of {nr["n"]} orders recorded automatically and wrong '
            f'(even {MAX_AUTO_WRONG}/{nr["n"]} has a 95% Wilson interval of '
            f'{100 * wilson(MAX_AUTO_WRONG, nr["n"])[0]:.1f}–{100 * wilson(MAX_AUTO_WRONG, nr["n"])[1]:.1f}%)',
            '  * excludes the orders the answer key itself sends to a person (missing values, over the cap, deposits)', '',
            'paired differences (same messages; bootstrap 95% over messages):']
    for k, v in s['pairs'].items():
        a, b = k.split('-')
        d, lo, hi = v['correct']
        oa, ob, p = v['correct_mcnemar']
        out.append(f'  full correct, {b} − {a}: {100 * d:+.0f} pts [{100 * lo:+.0f}, {100 * hi:+.0f}]'
                   f'{"  (interval includes zero)" if lo <= 0 <= hi else ""} · only {b} right {oa}, only {a} right {ob}, '
                   f'exact McNemar p = {p:.3f}')
        d, lo, hi = v['silent']
        out.append(f'  silent errors, {b} − {a}: {100 * d:+.0f} pts [{100 * lo:+.0f}, {100 * hi:+.0f}]'
                   f'{"  (interval includes zero)" if lo <= 0 <= hi else ""}')
    out += ['', 'silent errors that slipped past the rules, by group (native): ' + str(s['native']['slipped_by_group']),
            '', 'Spoken lines for the [RUN] beats (read verbatim; keep one branch):']
    out += ['  ' + x for x in spoken(s, meta, model, split)]
    return '\n'.join(out)


def cmd_report(args):
    rows = load_rows(HERE / 'runs', args.split, args.model)
    meta = json.loads((HERE / 'prices.json').read_text(encoding='utf-8'))
    model = rows[0]['model']
    price = meta.get('models', {}).get(model)
    s = summarise(rows, price, truth_routes(args.split))
    txt = render(s, meta, model, args.split)
    print(txt)
    out = HERE / 'results' / f'report-{args.split}-{model.replace(":", "_").replace("/", "_")}.txt'
    out.parent.mkdir(exist_ok=True)
    out.write_text(txt + '\n', encoding='utf-8')
    return 0
