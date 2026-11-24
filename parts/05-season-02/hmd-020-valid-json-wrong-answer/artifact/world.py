"""
HMD-020 · the invented shop «سبد محله» (Sabad-e Mahalleh) and its order messages. ILLUSTRATIVE.

Everything here is synthetic. Each order is created as a structured record first (the answer key), then written
as a Persian chat message from templates, so the right answer is known by construction.

    catalog       12 products, allowed units, an invented price per base unit (toman) and a household cap
    jalali        Solar Hijri <-> Gregorian (the arithmetic algorithm used by jalaali-js, Borkowski breaks)
    make_split()  the frozen test set (100) and the dev set (28), seeded
"""

import datetime as dt
import random

TODAY = dt.date(2027, 4, 7)          # Wednesday, 18 Farvardin 1406 (one day before release)
TODAY_FA = 'چهارشنبه ۱۸ فروردین ۱۴۰۶'
WINDOW_DAYS = 14                    # the shop delivers today .. today + 14 days
SEED = {'test': 20, 'dev': 2020}

# id: (Persian name, aliases used in messages, allowed units, base unit, toman per base unit, max base qty)
CATALOG = {
    'rice':       ('برنج طارم', ['برنج طارم', 'برنج'], ['kg', 'g'], 'kg', 300_000, 30),
    'chicken':    ('مرغ', ['مرغ'], ['kg', 'g'], 'kg', 150_000, 10),
    'potato':     ('سیب‌زمینی', ['سیب‌زمینی', 'سیب زمینی'], ['kg', 'g'], 'kg', 50_000, 20),
    'tomato':     ('گوجه‌فرنگی', ['گوجه‌فرنگی', 'گوجه'], ['kg', 'g'], 'kg', 60_000, 20),
    'cheese':     ('پنیر لیقوان', ['پنیر لیقوان', 'پنیر'], ['kg', 'g'], 'kg', 400_000, 5),
    'saffron':    ('زعفران', ['زعفران', 'زعفرون'], ['g'], 'g', 150_000, 20),
    'tea':        ('چای (بستهٔ ۵۰۰ گرمی)', ['چای'], ['pack'], 'pack', 450_000, 10),
    'oil':        ('روغن مایع (بطری ۱٫۵ لیتری)', ['روغن مایع', 'روغن'], ['piece'], 'piece', 250_000, 6),
    'eggs':       ('تخم‌مرغ (هر شانه ۳۰ عدد)', ['تخم‌مرغ', 'تخم مرغ'], ['piece', 'pack'], 'piece', 8_000, 90),
    'watermelon': ('هندوانه', ['هندونه', 'هندوانه'], ['piece'], 'piece', 200_000, 4),
    'melon':      ('خربزه', ['خربزه'], ['piece'], 'piece', 180_000, 4),
    'milk':       ('شیر', ['شیر'], ['liter'], 'liter', 80_000, 10),
}
UNITS = ['kg', 'g', 'piece', 'pack', 'liter']
PACK_SIZE = {'eggs': 30}            # one «شانه» = 30 eggs; tea is sold only by the pack


def to_base(product, quantity, unit):
    """Quantity in the product's base unit, or None if the unit cannot be converted."""
    base = CATALOG[product][3]
    if quantity is None or unit is None:
        return None
    if unit == base:
        return quantity
    if base == 'kg' and unit == 'g':
        return quantity / 1000
    if base == 'piece' and unit == 'pack' and product in PACK_SIZE:
        return quantity * PACK_SIZE[product]
    return None


def order_total(product, quantity, unit):
    q = to_base(product, quantity, unit)
    return None if q is None else round(q * CATALOG[product][4])


# ── Solar Hijri (Jalali) calendar ───────────────────────────────────────────────────────────────
BREAKS = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394,
          2456, 3178]


def _march_day(jy):
    """Day of March (Gregorian year jy + 621) on which 1 Farvardin of jy falls."""
    gy = jy + 621
    leap_j, jp, jump = -14, BREAKS[0], 0
    for jm in BREAKS[1:]:
        jump = jm - jp
        if jy < jm:
            break
        leap_j += (jump // 33) * 8 + (jump % 33) // 4
        jp = jm
    n = jy - jp
    leap_j += (n // 33) * 8 + ((n % 33) + 3) // 4
    if jump % 33 == 4 and jump - n == 4:
        leap_j += 1
    leap_g = gy // 4 - ((gy // 100 + 1) * 3) // 4 - 150
    return 20 + leap_j - leap_g


def jalali_to_gregorian(jy, jm, jd):
    start = dt.date(jy + 621, 3, _march_day(jy))
    offset = (jm - 1) * 31 if jm <= 7 else 6 * 31 + (jm - 7) * 30
    return start + dt.timedelta(days=offset + jd - 1)


def gregorian_to_jalali(d):
    jy = d.year - 621
    if d < dt.date(d.year, 3, _march_day(jy)):
        jy -= 1
    days = (d - dt.date(jy + 621, 3, _march_day(jy))).days
    if days < 186:
        return jy, days // 31 + 1, days % 31 + 1
    days -= 186
    return jy, days // 30 + 7, days % 30 + 1


# ── Persian text helpers ────────────────────────────────────────────────────────────────────────
FA_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
AR_DIGITS = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
JALALI_MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن',
                 'اسفند']
ONES = ['صفر', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه', 'ده', 'یازده', 'دوازده', 'سیزده',
        'چهارده', 'پانزده', 'شانزده', 'هفده', 'هجده', 'نوزده']
TENS = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود']
HUNDREDS = ['', 'صد', 'دویست', 'سیصد', 'چهارصد', 'پونصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد']


def fa(n):
    return str(n).translate(FA_DIGITS)


def sep(n, mark='٬'):
    return f'{n:,}'.replace(',', mark)


def words_small(n):
    """0..999 as colloquial spoken Persian (پونصد, not پانصد)."""
    if n < 20:
        return ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        return TENS[t] + (' و ' + ONES[o] if o else '')
    h, r = divmod(n, 100)
    return HUNDREDS[h] + (' و ' + words_small(r) if r else '')


def spoken_toman(amount, rng):
    """How people say an amount in chat: «دو و نیم میلیون», «یه میلیون و دویست», «چهارصد و پنجاه هزار»."""
    m, rest = divmod(amount, 1_000_000)
    k = rest // 1000
    if m == 0:
        return words_small(k) + ' هزار تومن'
    head = 'یه' if m == 1 else words_small(m)
    if k == 0:
        return f'{head} میلیون تومن'
    if k == 500 and rng.random() < 0.7:
        return ('یه میلیون و نیم تومن' if m == 1 else f'{head} و نیم میلیون تومن')
    return f'{head} میلیون و {words_small(k)} تومن'      # «هزار» is left out, as people say it


# ── message pieces ──────────────────────────────────────────────────────────────────────────────
def qty_phrase(product, quantity, unit, rng):
    q = fa(quantity)
    if unit == 'kg':
        if quantity == 0.5:
            return 'نیم کیلو'
        if quantity == 1.5:
            return 'یه کیلو و نیم'
        return f'{q} کیلو' if quantity != 1 else rng.choice(['یه کیلو', '۱ کیلو'])
    if unit == 'g':
        return f'{q} گرم' if product != 'saffron' or quantity != 1 else 'یه گرم'
    if unit == 'pack':
        word = 'شونه' if product == 'eggs' else 'بسته'
        return f'یه {word}' if quantity == 1 else f'{q} {word}'
    if unit == 'liter':
        return f'{q} لیتر'
    return 'یه دونه' if quantity == 1 else f'{q} تا'


def amount_phrase(amount, style, rng):
    if amount is None:
        return rng.choice(['پولش رو موقع تحویل می‌دم.', 'حساب رو موقع تحویل کارتخوان می‌کشم.'])
    verb = rng.choice(['کارت به کارت کردم', 'واریز کردم', 'ریختم به کارتتون'])
    if style == 'plain':
        money = f'{sep(amount).translate(FA_DIGITS)} {rng.choice(["تومان", "تومن"])}'
    elif style == 'arabic':
        money = f'{str(amount).translate(AR_DIGITS)} تومان'
    elif style == 'dot':
        money = f'{sep(amount, ".")} تومان'
    elif style == 'slash':
        money = f'{fa(amount // 1_000_000)}/{fa(amount % 1_000_000 // 100_000)} میلیون تومن'
    elif style == 'rial':
        r, roll = amount * 10, rng.random()
        if r >= 1_000_000 and r % 500_000 == 0 and roll < 0.35:
            money = spoken_toman(r, rng).replace('تومن', 'ریال')
        elif r % 1_000_000 == 0 and roll < 0.65:
            money = f'{fa(r // 1_000_000)} میلیون ریال'
        else:
            money = f'{sep(r).translate(FA_DIGITS)} ریال'
    elif style == 'colloquial':
        k = amount // 1000
        money = f'{fa(k)} تومن' if rng.random() < 0.6 else f'{words_small(k)} تومن'
    elif style == 'spoken':
        money = spoken_toman(amount, rng)
    else:
        raise ValueError(style)
    return f'{money} {verb}.'


def date_phrase(kind, rng):
    """Returns (Persian phrase, delivery date) for a date style."""
    w = TODAY.weekday()  # Monday = 0; TODAY is a Wednesday

    def next_weekday(target):  # Python weekday numbers; the next one strictly after today
        return TODAY + dt.timedelta(days=(target - w - 1) % 7 + 1)
    if kind == 'easy':
        return rng.choice(['برای فردا', 'فردا صبح', 'فردا عصر']), TODAY + dt.timedelta(days=1)
    if kind == 'relative':
        options = [('پس‌فردا', TODAY + dt.timedelta(days=2)),
                   ('سه روز دیگه', TODAY + dt.timedelta(days=3)),
                   ('برای شنبه', next_weekday(5)),
                   ('دوشنبه عصر', next_weekday(0)),
                   ('همین جمعه', next_weekday(4)),
                   ('هفتهٔ بعد همین روز', TODAY + dt.timedelta(days=7))]
        return rng.choice(options)
    if kind == 'jalali':
        d = TODAY + dt.timedelta(days=rng.randint(2, WINDOW_DAYS))
        jy, jm, jd = gregorian_to_jalali(d)
        style = rng.choice(['day_month', 'numeric', 'ordinal'])
        if style == 'numeric':
            return f'برای {fa(jy)}/{fa(jm).zfill(2).replace("0", "۰")}/{fa(jd).zfill(2).replace("0", "۰")}', d
        if style == 'ordinal' and jd == 1:
            return f'اول {JALALI_MONTHS[jm - 1]}', d
        return f'{fa(jd)} {JALALI_MONTHS[jm - 1]}', d
    if kind == 'edge':
        return 'دو هفته دیگه همین روز', TODAY + dt.timedelta(days=WINDOW_DAYS)
    if kind == 'missing':
        return None, None
    raise ValueError(kind)


GREET = ['سلام', 'سلام وقت بخیر', 'سلام خسته نباشید', 'سلام آقا رضا', '']
THANKS = ['ممنون', 'مرسی', 'دستتون درد نکنه', '']


def render(product, qp, dp, ap, rng, extra=''):
    name = rng.choice(CATALOG[product][1])
    want = rng.choice(['می‌خواستم', 'لطفاً بفرستید', 'می‌خوام'])
    parts = [rng.choice(GREET)]
    if dp:
        parts.append(f'{qp} {name} {want} {dp}.' if rng.random() < 0.5 else f'{dp} {qp} {name} {want}.')
    else:
        parts.append(f'{qp} {name} {want}.')
    if extra:
        parts.append(extra)
    parts.append(ap)
    parts.append(rng.choice(THANKS))
    return ' '.join(p for p in parts if p).replace(' .', '.')


# ── categories (one main trap per message; the rest of the message is kept easy) ─────────────────
# name: (count in test, amount style, date style, quantity style)
CATEGORIES = [
    ('clean', 12, 'plain', 'easy', 'normal'),
    ('digits_arabic', 4, 'arabic', 'easy', 'normal'),
    ('digits_dot', 3, 'dot', 'easy', 'normal'),
    ('digits_slash', 3, 'slash', 'easy', 'normal'),
    ('rial', 12, 'rial', 'easy', 'normal'),
    ('colloquial_thousand', 8, 'colloquial', 'easy', 'normal'),
    ('spoken_number', 10, 'spoken', 'easy', 'normal'),
    ('relative_date', 12, 'plain', 'relative', 'normal'),
    ('jalali_date', 10, 'plain', 'jalali', 'normal'),
    ('size_not_quantity', 3, 'plain', 'easy', 'size_spec'),
    ('quantity_range', 3, None, 'easy', 'range'),
    ('units', 6, 'plain', 'easy', 'units'),
    ('missing_quantity', 3, None, 'easy', 'missing'),
    ('missing_date', 3, 'plain', 'missing', 'normal'),
    ('bulk_over_cap', 2, 'plain', 'easy', 'bulk'),
    ('partial_payment', 2, 'partial', 'easy', 'normal'),
    ('edge_valid', 4, 'plain', 'edge', 'at_cap'),
]
TRAP_GROUP = {  # categories grouped for the report and the deck
    'clean': 'clean', 'digits_arabic': 'digits', 'digits_dot': 'digits', 'digits_slash': 'digits',
    'rial': 'rial', 'colloquial_thousand': 'colloquial', 'spoken_number': 'spoken',
    'relative_date': 'relative_date', 'jalali_date': 'jalali_date', 'size_not_quantity': 'ranges',
    'quantity_range': 'ranges', 'units': 'units', 'missing_quantity': 'missing', 'missing_date': 'missing',
    'bulk_over_cap': 'boundary', 'partial_payment': 'boundary', 'edge_valid': 'boundary'}

NORMAL_QTY = {'rice': [1, 2, 3, 5, 10], 'chicken': [1, 2, 3, 4], 'potato': [2, 3, 5, 10], 'tomato': [1, 2, 3, 4],
              'cheese': [1, 2, 3], 'saffron': [1, 2, 3, 5, 10], 'tea': [1, 2, 4], 'oil': [1, 2, 3, 4],
              'milk': [1, 2, 3, 5], 'watermelon': [1, 2], 'melon': [1, 2], 'eggs': None}


def amount_ok(style, total):
    if style == 'slash':
        return total >= 1_000_000 and total % 100_000 == 0 and total % 1_000_000 != 0
    if style == 'colloquial':
        return total < 1_000_000 and total % 1000 == 0
    if style == 'spoken':
        return total >= 1_000_000 and total % 100_000 == 0
    return True


def make_record(cat, amount_style, date_style, qty_style, rng):
    for _ in range(500):
        extra = ''
        if qty_style == 'size_spec':
            product = rng.choice(['watermelon', 'melon'])
            quantity, unit = rng.choice([1, 2]), 'piece'
            lo = rng.choice([2, 3, 4])
            size = f'{fa(lo)} تا {fa(lo + 2)} کیلویی'
            qp = f'یه {CATALOG[product][1][0]}ٔ {size}' if quantity == 1 else f'{fa(quantity)} تا {CATALOG[product][1][0]}ٔ {size}'
            text_name = False
        elif qty_style == 'range':
            product = rng.choice(['potato', 'tomato', 'chicken'])
            lo = rng.choice([2, 3])
            quantity, unit = None, 'kg'
            qp = f'{fa(lo)} تا {fa(lo + 2)} کیلو'
            text_name = True
        elif qty_style == 'units':
            product, quantity, unit, qp = rng.choice([
                ('cheese', 0.5, 'kg', 'نیم کیلو'), ('cheese', 750, 'g', '۷۵۰ گرم'), ('rice', 1.5, 'kg', 'یه کیلو و نیم'),
                ('chicken', 1500, 'g', '۱۵۰۰ گرم'), ('eggs', 2, 'pack', 'دو شونه'), ('eggs', 1, 'pack', 'یه شونه')])
            text_name = True
        elif qty_style == 'missing':
            product = rng.choice(['rice', 'cheese', 'chicken', 'potato'])
            quantity, unit, qp = None, None, ''
            text_name = True
        elif qty_style == 'bulk':
            product = rng.choice(['rice', 'potato'])
            quantity, unit = rng.choice([40, 50]), 'kg'
            qp = f'{fa(quantity)} کیلو'
            extra = rng.choice(['برای نذریه.', 'برای رستوران می‌خوام.'])
            text_name = True
        elif qty_style == 'at_cap':
            product = rng.choice(['rice', 'oil', 'saffron', 'milk'])
            quantity, unit = CATALOG[product][5], CATALOG[product][3]
            qp = qty_phrase(product, quantity, unit, rng)
            text_name = True
        else:
            product = rng.choice([p for p in CATALOG if p not in ('watermelon', 'melon')] + ['watermelon'])
            if product == 'eggs':
                quantity, unit = rng.choice([(10, 'piece'), (15, 'piece'), (20, 'piece'), (1, 'pack'), (2, 'pack')])
            else:
                quantity, unit = rng.choice(NORMAL_QTY[product]), CATALOG[product][3]
            qp = qty_phrase(product, quantity, unit, rng)
            text_name = True
        total = order_total(product, quantity, unit) if quantity is not None else None
        if amount_style is None:
            paid, style = None, None
        elif amount_style == 'partial':
            paid = rng.choice([200_000, 300_000, 500_000])
            if total is None or paid >= total * 0.8:
                continue
            style = 'plain'
            extra = 'بیعانه‌ست، بقیه‌ش موقع تحویل.'
        else:
            if total is None:
                continue
            paid, style = total, amount_style
            if not amount_ok(style, total):
                continue
        dp, date = date_phrase(date_style, rng)
        ap = amount_phrase(paid, style, rng) if style or paid is None else ''
        if qty_style == 'missing':
            msg = render(product, '', dp, ap, rng, extra).replace('  ', ' ')
        else:
            msg = render(product, qp, dp, ap, rng, extra) if text_name else \
                ' '.join(x for x in [rng.choice(GREET), f'{qp} می‌خواستم {dp}.', ap, rng.choice(THANKS)] if x)
        if amount_style == 'partial':
            msg = msg.replace(f'{extra} ', '')
            msg = msg.replace(ap, f'{ap[:-1]}؛ {extra}')
        truth = {'product': product, 'quantity': quantity, 'unit': unit, 'paid_toman': paid,
                 'delivery_date': date.isoformat() if date else None}
        return msg, truth
    raise RuntimeError(f'could not build a record for {cat}')


def make_split(split):
    rng = random.Random(SEED[split])
    rows, n = [], 0
    for cat, count, a, d, q in CATEGORIES:
        k = count if split == 'test' else 3 if cat in ('clean', 'rial', 'relative_date', 'jalali_date') else \
            (1 if count <= 4 else 2)
        for _ in range(k):
            n += 1
            msg, truth = make_record(cat, a, d, q, rng)
            rows.append({'id': f'{split[0].upper()}{n:03d}', 'split': split, 'category': cat,
                         'group': TRAP_GROUP[cat], 'message': msg, 'truth': truth})
    rng.shuffle(rows)
    return rows
