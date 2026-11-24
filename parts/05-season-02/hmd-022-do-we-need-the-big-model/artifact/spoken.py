"""HMD-022 · the Persian lines for the [RUN] beats 11, 12 and 13, with real numbers written as the narrator says them.

Every line names its denominator and keeps the hedges (this task set, these two models, this date, prices change).
The owner keeps one branch per beat and deletes the bracketed notes before recording.
"""
ONES = ['صفر', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه', 'ده', 'یازده', 'دوازده', 'سیزده',
        'چهارده', 'پونزده', 'شونزده', 'هفده', 'هیجده', 'نوزده']
TENS = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود']
HUNDREDS = ['', 'صد', 'دویست', 'سیصد', 'چهارصد', 'پونصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد']
CAT_FA = {'lookup': 'سؤال‌های ساده', 'convert': 'تبدیل واحد', 'extract': 'بیرون کشیدن از متن',
          'multistep': 'مسئله‌های چندمرحله‌ای', 'highrisk': 'سؤال‌های دارو'}
ROUTER_FA = {'always-small': 'همیشه کوچیک', 'always-big': 'همیشه بزرگ', 'rule-category': 'قانون نوع سؤال',
             'rule-length': 'قانون طول سؤال', 'confidence': '«چقدر مطمئنی؟»', 'cascade': 'نظر دوم',
             'oracle': 'پیشگو'}
# protocol.md: a router is worth switching on only if it cuts the cost per successful task by at least this much
# (and stays within the quality budget). The same measure is used in the script, the deck and the report.
MIN_SAVING = 0.30
RULE_ROUTERS = ('rule-category', 'rule-length')


def words_fa(n):
    n = int(round(n))
    if n < 0:
        return 'منفی ' + words_fa(-n)
    if n < 20:
        return ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        return TENS[t] + ('‌و' + ONES[o] if o else '')
    if n < 1000:
        h, r = divmod(n, 100)
        return HUNDREDS[h] + (' و ' + words_fa(r) if r else '')
    for size, name in ((10 ** 9, 'میلیارد'), (10 ** 6, 'میلیون'), (1000, 'هزار')):
        if n >= size:
            h, r = divmod(n, size)
            return (words_fa(h) + ' ' if (h > 1 or size > 1000) else '') + name + (' و ' + words_fa(r) if r else '')
    return str(n)


def dec_fa(x, places=1):
    neg = x < 0
    x = round(abs(x), places)
    whole = int(x)
    frac = round((x - whole) * 10 ** places)
    s = words_fa(whole) + (f' ممیز {words_fa(frac)}' if frac else '')
    return ('منفی ' if neg and (whole or frac) else '') + s


def pct(x):
    return words_fa(round(100 * x)) + ' درصد'


def money_fa(usd):
    """Dollars as spoken: under one dollar in cents, otherwise dollars with one decimal."""
    if usd < 1:
        return f'{words_fa(max(1, round(usd * 100)))} سنت'
    return f'{dec_fa(usd, 1)} دلار'


MONTHS = ['ژانویه', 'فوریه', 'مارس', 'آوریل', 'مه', 'ژوئن', 'ژوئیه', 'اوت', 'سپتامبر', 'اکتبر', 'نوامبر', 'دسامبر']


def date_fa(iso):
    """'2027-04-10' -> 'ده آوریل دو هزار و بیست‌وهفت' (as said aloud)."""
    try:
        y, m, d = (int(x) for x in str(iso)[:10].split('-'))
        return f'{words_fa(d)} {MONTHS[m - 1]} {words_fa(y)}'
    except (ValueError, IndexError):
        return '[تاریخ قیمت]'


NUMBER_WORDS = set(ONES + TENS[2:] + HUNDREDS[1:] + ['هزار', 'میلیون', 'میلیارد'])


def numbers_in(sentence):
    """Count spoken numbers in a sentence: a run of number words joined by «و» or «ممیز» is one number."""
    toks, n, inside = sentence.split(), 0, False
    for tok in toks:
        parts = tok.replace('\u200c', ' ').replace('‌و', ' ').split()
        is_num = bool(parts) and any(p in NUMBER_WORDS for p in parts) and all(p in NUMBER_WORDS or p == 'و' for p in parts)
        if is_num and not inside:
            n += 1
        inside = is_num or (inside and tok in ('و', 'ممیز'))
    return n


def branch(result):
    """Which of the three beat-13 branches the data supports, by the rule fixed in protocol.md."""
    t, picks = result['test'], result['picks']
    big = t['always-big']
    budget = result['budget_pp']
    within = lambda f: 100 * (t[f]['accuracy'] - big['accuracy']) >= -budget
    if picks['always-small']['feasible'] and within('always-small'):
        return 'C', 'always-small'
    # the candidate is chosen on dev (lowest dev cost per success), never on test
    cands = [f for f in ('rule-category', 'rule-length', 'confidence', 'cascade') if picks[f]['feasible'] and f in t]
    best = min(cands, key=lambda f: picks[f]['dev']['cost_per_success']) if cands else None
    if best and 1 - result['ci'][best]['cps_ratio'] >= MIN_SAVING and within(best):
        return 'A', best
    return 'B', best


def curve_branch(cats):
    """Beat 11: are the non-risk categories 'near' the big model (within the quality budget, in whole items)?"""
    kinds = [c for c in cats if c != 'highrisk']
    close = [c for c in kinds if cats[c]['near']]
    if len(close) == len(kinds):
        return 'A', close
    if not close:
        return 'B', close
    return 'C', close


def lines(result, meta):
    t, ci, cats = result['test'], result['ci'], result['by_category']
    n = result['n_test_nonrisk']
    out = ['— قاب ۱۱ · کوچیک، بزرگ، پیشگو —']
    s, b, o = t['always-small'], t['always-big'], t['oracle']
    out.append(f'روی {words_fa(n)} سؤال آزمون، بیرون از دستهٔ دارو.')
    out.append(f'مدل کوچیک {words_fa(s["correct"])} تا رو درست جواب داد، مدل بزرگ {words_fa(b["correct"])} تا.')
    out.append(f'پیشگو {words_fa(o["correct"])} تا رو درست می‌گرفت، با {pct(o["cost"] / b["cost"])} خرج مدل بزرگ.')
    for c in (c for c in cats if c != 'highrisk'):
        x = cats[c]
        out.append(f'{CAT_FA[c]}: کوچیک {words_fa(x["small"])} از {words_fa(x["n"])}.')
        out.append(f'بزرگ {words_fa(x["big"])} از {words_fa(x["n"])}.')
    which, close = curve_branch(cats)
    if which == 'A':
        out.append('**شاخهٔ الف** · پس کوچیک توی همهٔ دسته‌های کم‌خطر نزدیک بزرگه؛ جای صرفه‌جویی هست.')
    elif which == 'B':
        out.append('**شاخهٔ ب** · پس کوچیک حتی توی دسته‌های ساده عقبه؛ با این جفت مدل، جای زیادی برای صرفه‌جویی نمونده.')
    else:
        out.append('**شاخهٔ ج** · بعضی دسته‌ها نزدیک، بعضی عقب: پس صرفه‌جویی فقط توی همون دسته‌ها ممکنه؛ یعنی '
                   + '، '.join(CAT_FA[c] for c in close) + '.')
    if any(cats[c]['small'] > cats[c]['big'] for c in cats if c != 'highrisk'):
        out.append('[یادداشت: توی دست‌کم یه دسته، کوچیک از بزرگ بهتر بود؛ اگه نگهش می‌داری، بگو که با این تعداد سؤال ممکنه شانسی باشه.]')

    out.append('— قاب ۱۲ · خطای مسیریاب و کندترین جواب‌ها —')
    for f in ('confidence', 'cascade'):
        if f not in t:
            out.append(f'[{ROUTER_FA[f]}: هیچ آستانه‌ای روی دستهٔ تنظیم توی بودجهٔ کیفیت نبود.]')
            continue
        x = t[f]
        th = result['picks'][f]['threshold']
        th_fa = f'آستانهٔ {words_fa(th)}' if f == 'confidence' else f'شرط {words_fa(th)} جواب یکسان'
        out.append(f'{ROUTER_FA[f]}، با {th_fa}، {pct(x["escalation_rate"])} سؤال‌ها رو فرستاد پیش بزرگ.')
        out.append(f'{words_fa(x["missed_escalations"])} ارجاع جاافتاده داشت، و {words_fa(x["wasted_escalations"])} ارجاع بی‌خود.')
    for f in ('always-small', 'always-big', 'confidence', 'cascade'):
        if f in t:
            out.append(f'کندترین جواب از هر بیست تا، {ROUTER_FA[f]}: {dec_fa(t[f]["p95_latency"])} ثانیه.')
    rk = result['risk_test']
    for f in ('confidence', 'cascade'):
        if f in rk:
            out.append(f'توی دستهٔ دارو، اگه {ROUTER_FA[f]} تصمیم می‌گرفت، {words_fa(rk[f]["n"] - rk[f]["correct"])} جواب غلط '
                       f'از {words_fa(rk[f]["n"])} می‌رفت بیرون.')
    if 'always-big' in rk:
        wrong = rk['always-big']['n'] - rk['always-big']['correct']
        refused = result.get('refusals', {}).get('risk_big', 0)
        if refused:
            out.append(f'خود مدل بزرگ هم اونجا {words_fa(wrong - refused)} جواب غلط داد، و {words_fa(refused)} بار اصلاً جواب نداد.')
        else:
            out.append(f'خود مدل بزرگ هم اونجا {words_fa(wrong)} تا غلط داشت.')
        out.append('برای همینه که یه آدم هم نگاه می‌کنه.')

    out.append('— قاب ۱۳ · تصمیم —')
    which, f = branch(result)
    out.append(f'قیمت‌ها رو {date_fa(meta.get("prices_checked_on"))} خوندم.')
    if f and f in t:
        x, c = t[f], ci[f]
        out.append(f'هر هزار کار موفق، مدل بزرگ: {money_fa(1000 * b["cost_per_success"])}.')
        out.append(f'{ROUTER_FA[f]}: {money_fa(1000 * x["cost_per_success"])}.')
        lo_, hi_ = c['acc_diff_ci']
        out.append(f'فرق درستیش با مدل بزرگ {dec_fa(c["acc_diff_pp"])} واحد درصده.')
        out.append(f'بازه‌اش از {dec_fa(lo_)} تا {dec_fa(hi_)}.')
        if lo_ <= 0 <= hi_:
            out.append('صفر داخل بازه‌ست؛ یعنی این آزمون نمی‌تونه بگه افتی بوده یا نه.')
        elif hi_ < 0:
            out.append('کل بازه زیر صفره؛ این آزمون افت رو نشون می‌ده.')
        r_lo, r_hi = c['cps_ratio_ci']
        out.append(f'هر کار موفقش حدود {pct(c["cps_ratio"])} مدل بزرگ خرج داشت.')
        out.append(f'بازه‌اش از {pct(r_lo)} تا {pct(r_hi)}.')
    if which == 'A':
        out.append(f'**شاخهٔ الف** · پس برای چهار دستهٔ کم‌خطر، {ROUTER_FA[f]} رو روشن می‌کنم.')
        if f in RULE_ROUTERS:
            out.append('ولی توی محصول واقعی، اول باید یه چیزی نوع سؤال رو تشخیص بده؛ اون هنوز آزمایش نشده.')
    elif which == 'C':
        out.append('**شاخهٔ ج** · پس برای این چهار دسته، مدل کوچیک تنها توی بودجهٔ کیفیت بود؛ مسیریاب لازم نیست.')
    else:
        out.append('**شاخهٔ ب** · پس فعلاً همه پیش مدل بزرگ؛ این صرفه‌جویی دردسر دو مدل رو نمی‌خره.')
    out.append('در هر سه حالت، دستهٔ دارو همیشه مدل بزرگ و یه آدم.')
    out.append(f'[فقط همین {words_fa(n + result["n_test_risk"])} سؤال آزمون، همین دو مدل: {meta.get("small")} و {meta.get("big")}، '
               f'همین تاریخ؛ قیمت‌ها عوض می‌شن.]')
    return out
