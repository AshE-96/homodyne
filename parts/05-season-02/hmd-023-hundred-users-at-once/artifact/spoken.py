"""spoken.py — numbers as spoken Tehrani Persian, and the [RUN] lines of the HMD-023 script.

    fa_int(24) -> 'بیست‌وچهار'      fa_secs(2.5) -> 'دو و نیم'      fa_pct(0.42) -> 'چهل‌ودو درصد'
"""
ONES = ['صفر', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه']
TEENS = ['ده', 'یازده', 'دوازده', 'سیزده', 'چهارده', 'پونزده', 'شونزده', 'هفده', 'هجده', 'نوزده']
TENS = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود']
HUNDREDS = ['', 'صد', 'دویست', 'سیصد', 'چهارصد', 'پونصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد']
J = '‌و'   # «‌و» joined with a zero-width non-joiner: بیست‌وچهار


def _below_100(n):
    if n < 10:
        return ONES[n]
    if n < 20:
        return TEENS[n - 10]
    t, o = divmod(n, 10)
    return TENS[t] + (J + ONES[o] if o else '')


def _below_1000(n):
    h, r = divmod(n, 100)
    if not h:
        return _below_100(r)
    return HUNDREDS[h] + (' و ' + _below_100(r) if r else '')


def fa_int(n):
    n = int(round(n))
    if n < 0:
        return 'منفی ' + fa_int(-n)
    if n < 1000:
        return _below_1000(n)
    th, r = divmod(n, 1000)
    head = 'هزار' if th == 1 else _below_1000(th) + ' هزار'
    return head + (' و ' + _below_1000(r) if r else '')


def fa_dec(x):
    """One decimal, as spoken: 2.5 -> دو و نیم, 1.8 -> یک و هشت دهم, 0.4 -> چهار دهم."""
    x = round(x + 1e-9, 1)
    whole, tenth = int(x), int(round((x - int(x)) * 10))
    if tenth == 0:
        return fa_int(whole)
    frac = 'نیم' if tenth == 5 else ONES[tenth] + ' دهم'
    return frac if whole == 0 else f'{fa_int(whole)} و {frac}'


def fa_secs(s):
    """Seconds as spoken: one decimal under 10 s, whole seconds above."""
    if s is None:
        return '⟨ثانیه⟩'
    if s == float('inf'):
        return 'بیشتر از سقف انتظار'
    return fa_dec(s) if s < 10 else fa_int(s)


def fa_pct(share):
    if share is None:
        return '⟨درصد⟩'
    p = share * 100
    if 0 < p < 1:
        return 'کمتر از یک درصد'
    return fa_int(p) + ' درصد'


def fa_digits(x):
    return str(x).translate(str.maketrans('0123456789.', '۰۱۲۳۴۵۶۷۸۹٫'))


def secs_phrase(x, timeout=30):
    """'⟨n⟩ ثانیه', or past the timeout: 'بیش از سی ثانیه، یعنی سقف انتظار'."""
    if x is None:
        return '⟨ثانیه⟩ ثانیه'
    if x == float('inf'):
        return f'بیش از {fa_int(timeout)} ثانیه، یعنی سقف انتظار'
    return f'{fa_secs(x)} ثانیه'


def run_lines(meta, cold, rows, slo_ttft=3.0):
    """The spoken [RUN] lines of beats 10 and 11 (script-fa.md), from one real run.
    rows: list of (users, summary row), in stage order. Returns ({'10': [...], '11': [...]}, first users that broke the SLO)."""
    hw = meta.get('hardware', {})
    to = (meta.get('load') or {}).get('timeout', 30)
    out = {'10': [], '11': []}
    obs = meta.get('observed_max_streaming')      # measured, not the --num-parallel the owner typed
    out['10'].append(f'توی این اجرا، بیشترین تعداد جوابی که هم‌زمان نوشته شد، {fa_int(obs) if obs else "⟨عدد⟩"} تا بود؛ '
                     f'روی {hw.get("chip", "⟨تراشه⟩")} با {fa_int(hw["ram_gb"]) if hw.get("ram_gb") else "⟨عدد⟩"} گیگ حافظه.')
    if cold:
        out['10'].append(f'بار اول، اولین کلمه {secs_phrase(cold.get("cold_ttft"), to)} طول کشید. '
                         f'بار دوم، با مدل گرم: {secs_phrase(cold.get("warm_ttft"), to)}.')
    p95 = {u: r['ttft_p95'] for u, r in rows}
    us = [u for u, _ in rows]
    for a, b in zip(us[0::2], us[1::2]):
        first = 'صدک نود و پنجم زمان تا اولین کلمه، ' if a == us[0] else ''
        out['11'].append(f'{first}با {fa_int(a) if a != 1 else "یه"} کاربر {secs_phrase(p95[a], to)} بود؛ '
                         f'با {fa_int(b)} کاربر {secs_phrase(p95[b], to)}.')
    if len(us) % 2:
        out['11'].append(f'با {fa_int(us[-1])} کاربر {secs_phrase(p95[us[-1]], to)}.')
    last_u, last = rows[-1]
    out['11'].append(f'توی مرحلهٔ {fa_int(last_u)}\u200cنفره، {fa_pct(last["fail_rate"])} درخواست‌ها اصلاً جواب کامل نگرفتن.'
                     if last['fail_rate'] else f'توی مرحلهٔ {fa_int(last_u)}\u200cنفره، هیچ درخواستی بی‌جواب نموند.')
    broke = next((u for u, r in rows if not r['slo_met']), None)
    if broke is None:
        out['11'].append(f'پس قول سه‌ثانیه‌ای ما روی این لپ‌تاپ، تا {fa_int(us[-1])} کاربر هم نشکست.')
    elif broke == us[0]:
        out['11'].append('پس قول سه‌ثانیه‌ای ما روی این لپ‌تاپ، از همون مرحلهٔ اول نگه داشته نشد.')
    else:
        out['11'].append(f'پس قول سه‌ثانیه‌ای ما روی این لپ‌تاپ، اولین بار با {fa_int(broke)} کاربر شکست.')
    best = max(rows, key=lambda ur: ur[1]['throughput_rps'] or 0)[1]
    per_min = fa_int((best['throughput_rps'] or 0) * 60)
    cost = best.get('machine_s_per_success')
    out['11'].append(f'بیشترین چیزی که درآوردیم، حدود {per_min} جواب کامل در دقیقه بود؛ '
                     f'هر جواب موفق، حدود {secs_phrase(cost, to)} از وقت کل لپ‌تاپ.')
    return out, broke
