"""HMD-024 · build the report and the Persian spoken lines for the [RUN] beats (9 to 13 of script-fa.md)."""
import json
from pathlib import Path

import report as R
from spoken import dec_fa, fa_num, smart_fa, words_fa
from task_bank import CAT_FA, CATS

HERE = Path(__file__).resolve().parent
SYM_FA = {'✓': 'تیک', '~': 'موج', '✗': 'ضربدر'}


def _money_fa(x, currency):
    if currency == 'toman':
        return f'حدود {words_fa(round(x, -1) if x >= 100 else round(x))} تومن'
    return f'حدود {smart_fa(x)} {currency}'


def _usd_fa(usd):
    return f'حدود {words_fa(max(1, round(usd * 100)))} سنت' if usd < 1 else f'حدود {dec_fa(usd)} دلار'


def spoken(summ, chosen, online, cost_cfg, prices_meta):
    bad = [s for s in summ if s['arm'] == 'local' and not s['offline_verified']]
    local = [s for s in summ if s['arm'] == 'local' and s['offline_verified']]
    L = []
    for s in bad:
        L.append(f'!!! BLOCKING: {s["model"]} was NOT verified offline (network reachable before, during or after the run). '
                 'Its numbers are left out below. Re-run it offline before recording. !!!')
    L.append('— قاب ۹ · کیفیت [RUN] —')
    for i, s in enumerate(local):
        L.append((f'از سی کار، روی همین لپ‌تاپ، {s["spoken_fa"]} {words_fa(s["passed"])} تا رو درست انجام داد.' if i == 0
                  else f'{s["spoken_fa"]} {words_fa(s["passed"])} تا.'))
    L.append(f'سرویس آنلاین، همون سی کار: {words_fa(online["passed"])} تا.' if online else '(اجرای آنلاین هنوز انجام نشده.)')
    if chosen:
        L.append(f'{chosen["spoken_fa"]} از پونزده کار فارسی {words_fa(chosen["fa"])} تا رو درست کرد. '
                 f'از پونزده کار انگلیسی، {words_fa(chosen["en"])} تا.')
        # compare within categories: the two languages do not have the same mix of tasks
        worse = sum(c['fa'][1] and c['en'][1] and c['fa'][0] / c['fa'][1] < c['en'][0] / c['en'][1] for c in chosen['cats'].values())
        better = sum(c['fa'][1] and c['en'][1] and c['fa'][0] / c['fa'][1] > c['en'][0] / c['en'][1] for c in chosen['cats'].values())
        if worse >= 4:
            L.append(f'دسته‌به‌دسته نگاه کنیم: توی {words_fa(worse)} دسته از شش، فارسی ضعیف‌تر بود.')
        elif better >= 4:
            L.append(f'دسته‌به‌دسته نگاه کنیم: توی {words_fa(better)} دسته از شش، فارسی حتی بهتر بود.')
        else:
            L.append(f'دسته‌به‌دسته نگاه کنیم: فارسی توی {words_fa(worse)} دسته ضعیف‌تر بود، توی {words_fa(better)} دسته بهتر.')
        inv = chosen['invented']
        L.append(f'از {words_fa(chosen["absent_n"])} سؤالی که جوابش توی متن نبود، ' +
                 ('برای هیچ‌کدوم از خودش جواب نساخت.' if inv == 0 else
                  ('برای یکی‌ش از خودش جواب ساخت.' if inv == 1 else f'برای {words_fa(inv)} تاش از خودش جواب ساخت.')))
    if online and chosen:
        worst = max(CATS, key=lambda c: online['cats'][c]['n'] - chosen['cats'][c]['n'])
        d = online['cats'][worst]['n'] - chosen['cats'][worst]['n']
        if d >= 2:
            L.append(f'بیشترین فاصله با سرویس آنلاین توی «{CAT_FA[worst]}» بود: {words_fa(chosen["cats"][worst]["n"])} '
                     f'از پنج، در برابر {words_fa(online["cats"][worst]["n"])} از پنج.')
        else:
            L.append('توی هیچ دسته‌ای، فاصله با سرویس آنلاین بیشتر از یه کار نبود.')
    if any(s['truncated'] for s in local):
        L.append('[هشدار: دست‌کم یه ورودی بلند ممکنه بریده شده باشه؛ results.jsonl را ببین، possibly_truncated]')

    L.append('— قاب ۱۰ · سرعت و حافظه [RUN] —')
    for s in local:
        L.append(f'{s["spoken_fa"]}: اولین کلمه {smart_fa(s["ttft_med"])} ثانیه، کل جواب {smart_fa(s["total_med"])} ثانیه.')
        L.append(f'سرعتش حدود {words_fa(s["tps_med"] or 0)} توکن در ثانیه، و حافظه‌ش حدود {dec_fa((s["ps_size"] or 0) / R.GB)} گیگ.')
    if online:
        L.append(f'سرویس آنلاین، با رفت‌وبرگشت اینترنت، کل جواب رو میانه {smart_fa(online["total_med"])} ثانیه‌ای داد.')
    if chosen and chosen['cold_load_s'] is not None:
        L.append(f'بار اولِ {chosen["spoken_fa"]}، فقط بالا اومدن مدل {smart_fa(chosen["cold_load_s"])} ثانیه طول کشید.')
    big = [s for s in local if s['swap_growth'] and s['swap_growth'] > 0.25 * R.GB]
    if big:
        s = max(big, key=lambda x: x['swap_growth'])
        L.append(f'و برای {s["spoken_fa"]}، لپ‌تاپ حدود {dec_fa(s["swap_growth"] / R.GB)} گیگابایت از حافظه رو روی دیسک جابه‌جا کرد؛ '
                 'یعنی حافظه کم آورد و از دیسک قرض گرفت.')
    else:
        L.append('و توی هیچ اجرایی، لپ‌تاپ مجبور نشد حافظهٔ قابل‌توجهی رو روی دیسک جابه‌جا کنه.')

    L.append('— قاب ۱۱ · هزینه [RUN] —')
    cur = cost_cfg.get('currency', 'toman')
    if chosen:
        c = R.costs(chosen, cost_cfg, None, {})
        b = chosen['busy_s']
        dur = f'{words_fa(b / 60)} دقیقه' if b >= 90 else f'{words_fa(b)} ثانیه'
        L.append(f'سی کار، روی {chosen["spoken_fa"]}، روی هم حدود {dur} لپ‌تاپ رو مشغول کرد.')
        if 'energy_cost' in c:
            L.append(f'با فرض {words_fa(cost_cfg["power_watts_under_load"])} وات مصرف، برق همهٔ این سی کار {_money_fa(c["energy_cost"], cur)} شد.')
        else:
            L.append('[هزینهٔ برق: cost.json را پر کن (وات و قیمت برق)؛ تا آن موقع عدد نگو]')
        if 'depreciation_cost' in c:
            L.append(f'اگه سهم استهلاک لپ‌تاپ رو هم حساب کنیم، {_money_fa(c["depreciation_cost"], cur)} دیگه.')
        else:
            L.append('[سهم استهلاک: قیمت لپ‌تاپ را در cost.json بگذار]')
    if online:
        c = R.costs(online, cost_cfg, (prices_meta or {}).get('models'), prices_meta or {})
        if 'usd' in c:
            L.append(f'همین سی کار روی سرویس آنلاین، با قیمت‌هایی که {fa_num(c["checked_on"] or "[تاریخ]")} خوندیم، {_usd_fa(c["usd"])} شد.')
        else:
            L.append(f'سرویس آنلاین: حدود {words_fa(round((online["tokens_in"] + online["tokens_out"]) / 1000))} هزار توکن. [قیمت را در prices.json بگذار]')

    L.append('— قاب ۱۲ · کارت توانایی آفلاین [RUN] —')
    if chosen:
        n = {k: sum(c['sym'] == k for c in chosen['cats'].values()) for k in '✓~✗'}
        L.append(f'مدلی که با قانون ما انتخاب شد: {chosen["spoken_fa"]}.')
        cnt = lambda k: 'یکی' if n[k] == 1 else ('هیچ‌کدوم' if n[k] == 0 else words_fa(n[k]) + ' تا')
        L.append(f'از شش دسته، {cnt("✓")} تیک گرفت و {cnt("~")} موج.')
        L.append(f'{cnt("✗")} هم ضربدر.')
        slow = [c for c in CATS if chosen['cats'][c]['slow']]
        if slow:
            L.append(f'«{CAT_FA[slow[0]]}» درست بود ولی کند؛ برای همین موج گرفت، نه تیک.')
    unfit = [s for s in local if not s['fits']]
    for s in unfit:
        L.append(f'{s["spoken_fa"]} روی این لپ‌تاپ راحت جا نشد؛ پس انتخاب نشد.')

    L.append('— قاب ۱۳ · تصمیم [RUN] —')
    if chosen:
        groups = {k: [CAT_FA[c] for c in CATS if chosen['cats'][c]['sym'] == k] for k in '✓~✗'}
        if groups['✓']:
            L.append('آفلاین می‌مونه: ' + '، '.join(groups['✓']) + '.')
        if groups['~']:
            L.append('آفلاین، ولی یه آدم جواب رو چک می‌کنه: ' + '، '.join(groups['~']) + '.')
        if groups['✗']:
            both = [CAT_FA[c] for c in CATS if chosen['cats'][c]['sym'] == '✗' and online and online['cats'][c]['n'] <= 2]
            rest = [g for g in groups['✗'] if g not in both]
            if rest:
                L.append('می‌ره سراغ مدل قوی‌تر: ' + '، '.join(rest) + '؛ مگه اینکه متن محرمانه باشه.')
            if both:
                L.append('برای ' + '، '.join(both) + ' حتی سرویس آنلاین هم خوب نبود؛ اینجا کار با خود آدمه.')
    if online:
        L.append(f'[روی صفحه، قاب ۹ و ۱۰: مدل آنلاین = {online["model"]}، max_tokens {online["max_tokens"]}، effort {online["effort"]}]')
    L.append(f'[{", ".join(s["model"] for s in summ)} · سی کار ساختگی · یک لپ‌تاپ · همین تاریخ]')
    return L


def build(runs_dir, out_dir, demo=False, allow_changed=False):
    import locks
    runs = R.load_runs(runs_dir)
    if not runs:
        raise SystemExit(f'No runs in {runs_dir}. Run: python3 offline_lab.py run --local   (or --selftest)')
    lock_issues = locks.problems(runs)
    if lock_issues and not allow_changed:
        raise SystemExit('Refusing to build the card: the locked files differ from what the runs used.\n  '
                         + '\n  '.join(lock_issues) + '\nRe-run, restore the files, or pass --allow-changed-rules '
                         '(the card will say so).')
    rules = json.loads((HERE / 'rules.json').read_text(encoding='utf-8'))
    cost_cfg = json.loads((HERE / 'cost.json').read_text(encoding='utf-8'))
    prices_meta = json.loads((HERE / 'prices.json').read_text(encoding='utf-8'))
    if demo:
        cost_cfg.update(power_watts_under_load=15, electricity_price_per_kwh=1000, laptop_price=60_000_000)
    blind = R.load_blind(runs_dir)
    summ = R.summarise(runs, rules, blind)
    chosen = R.choose(summ, rules)
    online = next((s for s in summ if s['arm'] == 'online'), None)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    meta = next(r['meta'] for r in runs if r['meta']['arm'] == 'local') if any(r['meta']['arm'] == 'local' for r in runs) else runs[0]['meta']
    head, rows = R.card_rows(summ, chosen, online, rules)
    R.write_md(out / 'capability-card.md', head, rows, meta, summ, demo, rules, lock_issues)
    pngs = R.write_pngs(out, head, rows, summ, demo)
    for s in summ:
        s['costs'] = R.costs(s, cost_cfg, prices_meta.get('models'), prices_meta)
    (out / 'summary.json').write_text(json.dumps({'demo': demo, 'chosen': chosen and chosen['model'], 'models': summ},
                                                 ensure_ascii=False, indent=1, default=str), encoding='utf-8')
    lines = spoken(summ, chosen, online, cost_cfg, prices_meta)
    if lock_issues:
        lines.insert(0, '!!! BLOCKING: rules/tasks/graders changed since a run (built with --allow-changed-rules). !!!')
    (out / 'spoken-fa.txt').write_text(('DEMO — NOT A RESULT\n' if demo else '') + '\n'.join(lines) + '\n', encoding='utf-8')
    return {'summ': summ, 'chosen': chosen, 'online': online, 'head': head, 'rows': rows, 'lines': lines, 'pngs': pngs,
            'out': out, 'lock_issues': lock_issues}
