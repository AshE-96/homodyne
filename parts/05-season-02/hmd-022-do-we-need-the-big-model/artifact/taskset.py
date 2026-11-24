"""HMD-022 · task set: 200 requests with ground truth, Persian and English, five categories.

Everything is generated from code with a fixed seed, except the 40 hand-written lookups, so every truth value is
either computed (conversions, extraction, arithmetic, leaflet doses) or a stable, well-known fact. Nothing here is
judged by a model.

    python3 taskset.py            # (re)build tasks/tasks.json and print the stats

ILLUSTRATIVE: the bank messages, invoices, people and the three medicines (Zelvorin, Tamirex, Orvadin) are invented.
The leaflets are fictional and must never be read as medical advice.
"""
import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = HERE / 'tasks' / 'tasks.json'
SEED = 22
CATEGORIES = ['lookup', 'convert', 'extract', 'multistep', 'highrisk']
RISK = {'highrisk'}
PER_CAT_LANG = 20            # 5 categories x 2 languages x 20 = 200
DEV_PER_CAT_LANG = 8         # 8 dev + 12 test per category and language -> 80 dev, 120 test

FA_DIGITS = str.maketrans('0123456789.', '۰۱۲۳۴۵۶۷۸۹٫')


def fa(n, sep=True):
    """Number in Persian digits with the Persian thousands separator."""
    if isinstance(n, float) and n.is_integer():
        n = int(n)
    s = f'{n:,}' if sep else str(n)
    return s.replace(',', '٬').translate(FA_DIGITS)


def en(n):
    if isinstance(n, float) and n.is_integer():
        n = int(n)
    return f'{n:,}'


# ── number words (for the "write it in digits" conversions) ─────────────────────────────────────
FA_ONES = ['', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه', 'ده', 'یازده', 'دوازده', 'سیزده',
           'چهارده', 'پانزده', 'شانزده', 'هفده', 'هجده', 'نوزده']
FA_TENS = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود']
FA_HUN = ['', 'صد', 'دویست', 'سیصد', 'چهارصد', 'پانصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد']
EN_ONES = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve',
           'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
EN_TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']


def fa_words(n):
    if n == 0:
        return 'صفر'
    parts = []
    for size, name in ((10 ** 9, 'میلیارد'), (10 ** 6, 'میلیون'), (1000, 'هزار')):
        if n >= size:
            q, n = divmod(n, size)
            parts.append(f'{fa_words(q)} {name}' if not (q == 1 and size == 1000) else name)
    if n >= 100:
        q, n = divmod(n, 100)
        parts.append(FA_HUN[q])
    if n >= 20:
        q, n = divmod(n, 10)
        parts.append(FA_TENS[q])
    if n:
        parts.append(FA_ONES[n])
    return ' و '.join(parts)


def en_words(n):
    parts = []
    for size, name in ((10 ** 6, 'million'), (1000, 'thousand')):
        if n >= size:
            q, n = divmod(n, size)
            parts.append(f'{en_words(q)} {name}')
    if n >= 100:
        q, n = divmod(n, 100)
        parts.append(f'{EN_ONES[q]} hundred')
    rest = ''
    if n >= 20:
        q, r = divmod(n, 10)
        rest = EN_TENS[q] + (f'-{EN_ONES[r]}' if r else '')
    elif n:
        rest = EN_ONES[n]
    if rest:
        parts.append(('and ' if parts else '') + rest)
    return ' '.join(parts)


# ── truth helpers ────────────────────────────────────────────────────────────────────────────────
def num(v):
    return {'type': 'number', 'value': v}


def text(*aliases):
    return {'type': 'text', 'aliases': list(aliases)}


def yesno(v):
    return {'type': 'yesno', 'value': bool(v)}


# ── 1. lookups: hand-written, stable facts ───────────────────────────────────────────────────────
LOOKUP_FA = [
    ('پایتخت ژاپن کجاست؟', text('توکیو', 'tokyo')),
    ('نماد شیمیایی طلا چیست؟', text('au')),
    ('هر هفته چند روز دارد؟', num(7)),
    ('آب در فشار سطح دریا در چند درجهٔ سانتی‌گراد می‌جوشد؟', num(100)),
    ('بزرگ‌ترین سیارهٔ منظومهٔ شمسی کدام است؟', text('مشتری', 'برجیس', 'jupiter')),
    ('پایتخت ترکیه کدام شهر است؟', text('آنکارا', 'ankara')),
    ('نماد شیمیایی آهن چیست؟', text('fe')),
    ('عنکبوت چند پا دارد؟', num(8)),
    ('سال کبیسه در تقویم میلادی چند روز دارد؟', num(366)),
    ('سرایندهٔ شاهنامه کیست؟', text('فردوسی', 'ferdowsi', 'ferdowsi tusi')),
    ('پایتخت استرالیا کدام شهر است؟', text('کانبرا', 'canberra')),
    ('یک دوجین چند تاست؟', num(12)),
    ('نزدیک‌ترین سیاره به خورشید کدام است؟', text('عطارد', 'تیر', 'mercury')),
    ('نماد شیمیایی سدیم چیست؟', text('na')),
    ('اسفند در سال غیرکبیسهٔ شمسی چند روز دارد؟', num(29)),
    ('چند ماه از سال شمسی ۳۱ روزه است؟', num(6)),
    ('قلهٔ دماوند در کدام رشته‌کوه است؟', text('البرز', 'alborz')),
    ('پایتخت کانادا کدام شهر است؟', text('اتاوا', 'اوتاوا', 'ottawa')),
    ('فرمول شیمیایی آب چیست؟', text('h2o')),
    ('هر ساعت چند ثانیه است؟', num(3600)),
]
LOOKUP_EN = [
    ('What is the capital of Italy?', text('rome', 'roma', 'رم')),
    ('What is the chemical symbol for silver?', text('ag')),
    ('How many hours are there in two days?', num(48)),
    ('What is the largest ocean on Earth?', text('pacific', 'pacific ocean', 'آرام')),
    ('At what temperature in degrees Fahrenheit does water freeze at sea level?', num(32)),
    ("Who wrote 'Romeo and Juliet'?", text('shakespeare', 'william shakespeare')),
    ('What is the capital of Brazil?', text('brasilia', 'brasília')),
    ('What is the chemical symbol for potassium?', text('k')),
    ('How many bones does a typical adult human skeleton have?', num(206)),
    ('What is the smallest prime number?', num(2)),
    ('How many sides does an octagon have?', num(8)),
    ('Which planet is known as the Red Planet?', text('mars', 'مریخ')),
    ('What is the capital of Switzerland (the federal city)?', text('bern', 'berne')),
    ('What is the chemical symbol for lead?', text('pb')),
    ('How many minutes are in three hours?', num(180)),
    ('What is the square root of 144?', num(12)),
    ('What is the capital of New Zealand?', text('wellington')),
    ('How many players does each side have on the field in a standard football (soccer) match?', num(11)),
    ('Who painted the Mona Lisa?', text('leonardo da vinci', 'da vinci', 'leonardo')),
    ('What is the capital of Morocco?', text('rabat')),
]


def unique(make, seen):
    """Draw from a template until the prompt is new, so no request appears twice (or in both dev and test)."""
    for _ in range(200):
        out = make()
        if out[0] not in seen:
            seen.add(out[0])
            return out
    raise RuntimeError('template pool too small')


def lookups(rng):
    return [('fa', q, t) for q, t in LOOKUP_FA] + [('en', q, t) for q, t in LOOKUP_EN]


# ── 2. conversions ───────────────────────────────────────────────────────────────────────────────
def conversions(rng):
    out = []
    fa_t = [
        lambda: (lambda x: (f'{fa(x)} تومان چند ریال است؟', num(x * 10)))(rng.choice([12_500, 85_000, 340_000, 1_250_000, 7_900_000])),
        lambda: (lambda y: (f'{fa(y)} ریال چند تومان است؟', num(y // 10)))(rng.choice([45_000, 230_000, 1_800_000, 12_600_000, 95_000_000])),
        lambda: (lambda a: (f'{fa(a)} میلیون تومان چند ریال است؟', num(int(round(a * 10_000_000)))))(rng.choice([1.5, 2.5, 3.2, 0.75, 12.4])),
        lambda: (lambda k: (f'{fa(k)} کیلومتر چند متر است؟', num(int(round(k * 1000)))))(rng.choice([3.7, 12.5, 0.85, 42.195])),
        lambda: (lambda h, m: (f'{fa(h)} ساعت و {fa(m)} دقیقه روی هم چند دقیقه است؟', num(h * 60 + m)))(rng.randint(1, 9), rng.randint(5, 55)),
        lambda: (lambda n: (f'عدد «{fa_words(n)}» را با رقم بنویس.', num(n)))(rng.choice([2_340_000, 17_850, 406_000, 1_005_300, 93_070])),
        lambda: (lambda g: (f'{fa(g)} گرم چند کیلوگرم است؟', num(g / 1000)))(rng.choice([2500, 750, 12_300, 1250])),
        lambda: (lambda p, b: (f'{fa(p)} درصدِ {fa(b)} تومان چند تومان می‌شود؟', num(p * b // 100)))(rng.choice([10, 15, 20, 25, 40]), rng.choice([80_000, 360_000, 1_200_000, 2_500_000])),
    ]
    en_t = [
        lambda: (lambda k: (f'How many meters are there in {k} km?', num(int(round(k * 1000)))))(rng.choice([3.7, 12.5, 0.85, 42.195])),
        lambda: (lambda m: (f'Convert {m} minutes to hours (give a decimal number).', num(m / 60)))(rng.choice([135, 75, 210, 45, 390])),
        lambda: (lambda kg: (f'How many grams are in {kg} kg?', num(int(round(kg * 1000)))))(rng.choice([2.4, 0.35, 15.75, 1.08])),
        lambda: (lambda n: (f"Write '{en_words(n)}' in digits.", num(n)))(rng.choice([3405, 18_260, 702_015, 1_040_300, 99_009])),
        lambda: (lambda h: (f'How many seconds are there in {h} hours?', num(h * 3600)))(rng.randint(2, 30)),
        lambda: (lambda c: (f'Convert {c} °C to °F.', num(c * 9 // 5 + 32)))(rng.choice([-40, -10, 25, 35, 180, 220])),
        lambda: (lambda t: (f'How many Iranian rials are in {en(t)} tomans?', num(t * 10)))(rng.choice([45_000, 1_200_000, 380_000, 9_750])),
        lambda: (lambda p, b: (f'What is {p}% of {en(b)}?', num(p * b / 100)))(rng.choice([5, 12, 30, 45, 8]), rng.choice([250, 1_200, 640, 18_000])),
    ]
    seen = set()
    for lang, tmpl in (('fa', fa_t), ('en', en_t)):
        for i in range(PER_CAT_LANG):
            q, t = unique(tmpl[i % len(tmpl)], seen)
            out.append((lang, q, t))
    return out


# ── 3. extraction from a short text (with distractor numbers) ───────────────────────────────────
def extraction(rng):
    out = []

    def bank():
        amt, bal = rng.randrange(150, 9_000) * 1000, rng.randrange(2_000, 90_000) * 1000
        card, d, hh, mm = rng.randrange(1000, 9999), rng.randint(1, 29), rng.randint(8, 22), rng.randint(0, 59)
        msg = (f'بانک فرضی آفتاب\nبرداشت: {fa(amt)} ریال\nکارت: ۶۰۳۷****{fa(card, False)}\n'
               f'تاریخ: ۱۴۰۵/۰۳/{fa(d, False).zfill(2)}  ساعت {fa(hh, False)}:{fa(mm, False).zfill(2)}\nمانده: {fa(bal)} ریال')
        q, t = rng.choice([('مانده حساب بعد از این برداشت چند ریال است؟', num(bal)),
                           ('مبلغ برداشت چند ریال بوده؟', num(amt)),
                           ('مبلغ برداشت چند تومان می‌شود؟', num(amt // 10)),
                           ('چهار رقم آخر کارت چیست؟', num(card))])
        return msg, q, t

    def parcel():
        order, track, fee, items = rng.randrange(10_000, 99_999), rng.randrange(1_000_000, 9_999_999), rng.choice([35_000, 45_000, 60_000]), rng.randint(2, 7)
        msg = (f'فروشگاه فرضی «سبدک»: سفارش شمارهٔ {fa(order, False)} شامل {fa(items)} قلم کالا ارسال شد. '
               f'هزینهٔ ارسال {fa(fee)} تومان. کد رهگیری پست: {fa(track, False)}. تحویل حداکثر سه روز کاری.')
        q, t = rng.choice([('کد رهگیری پست چیست؟', num(track)), ('هزینهٔ ارسال چند تومان است؟', num(fee)),
                           ('سفارش چند قلم کالا دارد؟', num(items)), ('شمارهٔ سفارش چیست؟', num(order))])
        return msg, q, t

    def rent():
        rent_, dep, months = rng.randrange(8, 60) * 1_000_000, rng.randrange(100, 900) * 1_000_000, rng.choice([6, 12])
        msg = (f'آگهی فرضی: آپارتمان ۷۵ متری، طبقهٔ سوم، ودیعه {fa(dep)} تومان و اجارهٔ ماهانه {fa(rent_)} تومان، '
               f'قرارداد {fa(months)} ماهه. شارژ ماهانه جداگانه ۸۵۰٬۰۰۰ تومان.')
        q, t = rng.choice([('اجارهٔ ماهانه چند تومان است؟', num(rent_)), ('ودیعه چند تومان است؟', num(dep)),
                           ('قرارداد چند ماهه است؟', num(months)), ('شارژ ماهانه چند تومان است؟', num(850_000))])
        return msg, q, t

    def class_():
        room, cap, start = rng.randrange(101, 450), rng.randint(18, 45), rng.choice([8, 10, 14, 16])
        msg = (f'اطلاعیهٔ فرضی: کلاس جبرانی ریاضی از ساعت {fa(start, False)} به ساعت {fa(start + 2, False)} منتقل شد. '
               f'محل کلاس: اتاق {fa(room, False)}. ظرفیت {fa(cap)} نفر. کلاس قبلی در اتاق ۲۰۷ لغو شد.')
        q, t = rng.choice([('کلاس جبرانی الان در کدام اتاق است؟', num(room)), ('ظرفیت کلاس چند نفر است؟', num(cap)),
                           ('کلاس الان ساعت چند شروع می‌شود؟', num(start + 2))])
        return msg, q, t

    def invoice():
        sub = rng.randrange(120, 900) + rng.choice([0, 0.5, 0.25])
        tax = round(sub * 0.08, 2)
        inv = rng.randrange(1000, 9999)
        msg = (f'Invoice INV-{inv} (fictional)\nSubtotal: ${sub:.2f}\nSales tax (8%): ${tax:.2f}\n'
               f'Total due: ${sub + tax:.2f}\nPayment terms: 30 days. Late fee: $25.00')
        q, t = rng.choice([('What is the total amount due, in dollars?', num(round(sub + tax, 2))),
                           ('How much is the sales tax, in dollars?', num(tax)),
                           ('What is the invoice number (digits only)?', num(inv)),
                           ('What is the late fee, in dollars?', num(25))])
        return msg, q, t

    def meeting():
        room, old_h, new_h, n = rng.randrange(100, 499), rng.choice([9, 10, 11]), rng.choice([14, 15, 16]), rng.randint(4, 12)
        day = rng.choice(['Wednesday', 'Thursday', 'Friday'])
        msg = (f'Hi all, the design review is moved from Tuesday {old_h}:00 to {day} {new_h}:30, room B-{room}. '
               f'We expect {n} people; the old room A-12 is no longer booked.')
        q, t = rng.choice([('What is the new room number (digits only)?', num(room)),
                           ('On which day is the review now?', text(day.lower())),
                           ('How many people are expected?', num(n))])
        return msg, q, t

    def flight():
        fl, gate, seat_row, bag = rng.randrange(100, 999), rng.randint(2, 48), rng.randint(5, 40), rng.choice([20, 23, 30])
        msg = (f'Booking confirmation (fictional airline): flight FX{fl}, boarding at gate {gate}, '
               f'seat {seat_row}C. Checked baggage allowance {bag} kg; cabin bag 7 kg.')
        q, t = rng.choice([('What is the boarding gate number?', num(gate)),
                           ('What is the checked baggage allowance in kg?', num(bag)),
                           ('What is the flight number (digits only)?', num(fl))])
        return msg, q, t

    def payslip():
        gross, ins, net_bonus = rng.randrange(3000, 9000), rng.randrange(150, 400), rng.randrange(100, 900)
        msg = (f'Payslip, March (fictional employer). Gross salary: {gross} EUR. Health insurance: -{ins} EUR. '
               f'One-off bonus: {net_bonus} EUR. Overtime hours: 6.')
        q, t = rng.choice([('How much is the health insurance deduction, in EUR?', num(ins)),
                           ('What is the gross salary, in EUR?', num(gross)),
                           ('How many overtime hours are listed?', num(6))])
        return msg, q, t

    seen = set()
    for lang, gens in (('fa', [bank, parcel, rent, class_]), ('en', [invoice, meeting, flight, payslip])):
        for i in range(PER_CAT_LANG):
            msg, q, t = unique(lambda g=gens[i % len(gens)]: (lambda m, qq, tt: (m + qq, m, qq, tt))(*g()), seen)[1:]
            out.append((lang, (f'متن:\n{msg}\n\nپرسش: {q}' if lang == 'fa' else f'Text:\n{msg}\n\nQuestion: {q}'), t))
    return out


# ── 4. multi-step word problems ─────────────────────────────────────────────────────────────────
def multistep(rng):
    out = []

    def change():
        a, p, b, r = rng.randint(2, 6), rng.choice([12_000, 18_500, 24_000, 35_000]), rng.randint(1, 4), rng.choice([6_500, 9_000, 12_500])
        return (f'علی {fa(a)} دفتر هر کدام {fa(p)} تومان و {fa(b)} خودکار هر کدام {fa(r)} تومان خرید و '
                f'یک اسکناس {fa(500_000)} تومانی داد. چند تومان باید پس بگیرد؟', num(500_000 - a * p - b * r))

    def shoe():
        price, d = rng.choice([1_200_000, 1_850_000, 2_400_000, 3_500_000]), rng.choice([20, 25, 30, 40])
        return (f'قیمت یک کفش {fa(price)} تومان است. اول {fa(d)} درصد تخفیف می‌خورد و بعد روی قیمت تخفیف‌خورده '
                f'۱۰ درصد مالیات اضافه می‌شود. قیمت نهایی چند تومان است؟', num(round(price * (100 - d) / 100 * 1.1)))

    def taxi():
        base, per_km, km = rng.choice([13_000, 18_000, 25_000]), rng.choice([1_200, 1_850, 2_400, 3_500]), rng.randint(8, 14)
        total = base + per_km * km
        n = next(k for k in (4, 3, 5, 2) if total % k == 0)
        return (f'کرایهٔ یک تاکسی اینترنتی {fa(base)} تومان ورودی و هر کیلومتر {fa(per_km)} تومان است. مسیر {fa(km)} کیلومتر '
                f'است و {fa(n)} نفر کرایه را مساوی تقسیم می‌کنند. سهم هر نفر چند تومان است؟', num(total // n))

    def tank():
        a, b = rng.randint(2, 9), rng.randint(1, 4)
        return (f'یک مخزن {fa(a * b * 40)} لیتری با شیری پر می‌شود که دقیقه‌ای {fa(b * 5)} لیتر آب می‌دهد، ولی از سوراخ ته آن '
                f'دقیقه‌ای {fa(b)} لیتر بیرون می‌ریزد. پر شدن مخزن خالی چند دقیقه طول می‌کشد؟', num(a * 10))

    def cafe():
        a, b, p, r = rng.randint(2, 6), rng.randint(1, 4), rng.choice([2.5, 3.25, 4.0]), rng.choice([3.75, 4.5, 5.25])
        return (f'A cafe sells coffee at ${p:.2f} and cake at ${r:.2f}. Sam buys {a} coffees and {b} {"cake" if b == 1 else "cakes"} and pays with '
                f'a $50 note. How much change does he get, in dollars?', num(round(50 - a * p - b * r, 2)))

    def ages():
        k = rng.randint(6, 15)
        return (f'A mother is three times as old as her son. In {k} years she will be twice as old as him. '
                f'How old is the son now?', num(k))

    def train():
        a, v = rng.randint(2, 5), rng.choice([60, 80, 100])
        return (f'A train leaves at 08:00 and travels at {v} km/h for {a} hours, then at {v + 40} km/h for 1.5 hours. '
                f'How many kilometres does it travel in total?', num(v * a + (v + 40) * 1.5))

    def pens():
        need, pack, price = rng.randint(60, 230), rng.randint(4, 7), rng.randint(3, 6)
        return (f'Pens come in packs of {pack}. A school needs {need} pens and each pack costs ${price}. '
                f'How many dollars does the school spend if it must buy whole packs?', num(-(-need // pack) * price))

    seen = set()
    for lang, gens in (('fa', [change, shoe, taxi, tank]), ('en', [cafe, ages, train, pens])):
        for i in range(PER_CAT_LANG):
            q, t = unique(gens[i % len(gens)], seen)
            out.append((lang, q, t))
    return out


# ── 5. high-risk: dose questions answered from a fictional leaflet ──────────────────────────────
DRUGS = [
    dict(fa='زِلوَرین', en='Zelvorin', mg5=120, mgkg=6, every=8, doses=3, cap=600, min_age=2, adult=240, adult_doses=4),
    dict(fa='تامیرِکس', en='Tamirex', mg5=100, mgkg=5, every=6, doses=4, cap=500, min_age=3, adult=200, adult_doses=3),
    dict(fa='اورادین', en='Orvadin', mg5=160, mgkg=8, every=12, doses=2, cap=700, min_age=1, adult=400, adult_doses=2),
]


def leaflet(d, lang):
    if lang == 'fa':
        return (f'بروشور ساختگی، فقط برای آزمون؛ این دارو وجود ندارد و این متن توصیهٔ پزشکی نیست.\n'
                f'شربت {d["fa"]}: هر ۵ میلی‌لیتر شامل {fa(d["mg5"])} میلی‌گرم.\n'
                f'کودکان {fa(d["min_age"])} تا ۱۲ سال: هر نوبت {fa(d["mgkg"])} میلی‌گرم به ازای هر کیلوگرم وزن، '
                f'هر {fa(d["every"])} ساعت، حداکثر {fa(d["doses"])} نوبت در ۲۴ ساعت، و روی هم هرگز بیش از {fa(d["cap"])} میلی‌گرم در روز.\n'
                f'زیر {fa(d["min_age"])} سال: مصرف نشود.\n'
                f'بزرگسالان و بالای ۱۲ سال: هر نوبت {fa(d["adult"])} میلی‌گرم، حداکثر {fa(d["adult_doses"])} نوبت در روز.')
    return (f'FICTIONAL leaflet for testing only; this medicine does not exist and this is not medical advice.\n'
            f'{d["en"]} syrup: each 5 ml contains {d["mg5"]} mg.\n'
            f'Children {d["min_age"]} to 12 years: {d["mgkg"]} mg per kg of body weight per dose, every {d["every"]} hours, '
            f'at most {d["doses"]} doses in 24 hours, and never more than {d["cap"]} mg per day in total.\n'
            f'Under {d["min_age"]} years: do not use.\n'
            f'Adults and over 12: {d["adult"]} mg per dose, at most {d["adult_doses"]} doses per day.')


def highrisk(rng):
    out, seen = [], set()

    def make(i, lang):
        d = DRUGS[(i + i // 6) % 3]          # spread every question kind over all three leaflets
        kind = ['dose_mg', 'dose_ml', 'daily_cap', 'daily_cap', 'age', 'adult_daily'][i % 6]
        age = rng.randint(max(d['min_age'], 3), 11)
        w = 2 * age + 8 + rng.randint(-2, 3)          # a plausible weight for the age
        if kind == 'dose_ml':                         # keep the syrup volume on a quarter-millilitre
            w = min((x for x in range(w - 3, w + 4) if (d['mgkg'] * x * 5 / d['mg5'] * 4).is_integer()),
                    key=lambda x: abs(x - w), default=w)
        elif kind == 'daily_cap' and i % 2:           # the trap: the per-kg total passes the daily cap
            age = rng.randint(10, 11)
            w = max(2 * age + 8, d['cap'] // (d['mgkg'] * d['doses']) + rng.randint(2, 6))
        if kind == 'dose_mg':
            qf, qe, t = (f'کودکی {fa(age)} ساله و {fa(w)} کیلویی است. طبق همین بروشور، هر نوبت چند میلی‌گرم؟',
                         f'A child is {age} years old and weighs {w} kg. Per this leaflet, how many mg per dose?', num(d['mgkg'] * w))
        elif kind == 'dose_ml':
            qf, qe, t = (f'کودکی {fa(age)} ساله و {fa(w)} کیلویی است. طبق همین بروشور، هر نوبت چند میلی‌لیتر شربت؟',
                         f'A child is {age} years old and weighs {w} kg. Per this leaflet, how many ml of syrup per dose?',
                         num(round(d['mgkg'] * w * 5 / d['mg5'], 2)))
        elif kind == 'daily_cap':
            qf, qe, t = (f'کودکی {fa(age)} ساله و {fa(w)} کیلویی است. طبق همین بروشور، حداکثر چند میلی‌گرم در ۲۴ ساعت؟',
                         f'A child is {age} years old and weighs {w} kg. Per this leaflet, what is the most mg allowed in 24 hours?',
                         num(min(d['mgkg'] * w * d['doses'], d['cap'])))
        elif kind == 'age':
            young = i % 4 == 0 or d['min_age'] == 1 and i % 2 == 0
            a = rng.randint(0, d['min_age'] - 1) if young else rng.randint(d['min_age'], 11)
            months = a * 12 + rng.choice([3, 6, 9]) if young else a * 12
            ok = months >= d['min_age'] * 12
            qf, qe, t = (f'طبق همین بروشور، این شربت برای کودک {fa(months)} ماهه مجاز است؟ فقط بله یا خیر.',
                         f'Per this leaflet, may this syrup be given to a child aged {months} months? Answer yes or no.', yesno(ok))
        else:
            qf, qe, t = ('طبق همین بروشور، یک بزرگسال حداکثر چند میلی‌گرم در روز می‌تواند مصرف کند؟',
                         'Per this leaflet, what is the most mg an adult may take per day?', num(d['adult'] * d['adult_doses']))
        body = (f'متن:\n{leaflet(d, "fa")}\n\nپرسش: {qf}' if lang == 'fa' else f'Text:\n{leaflet(d, "en")}\n\nQuestion: {qe}')
        return body, t

    for lang in ('fa', 'en'):
        for i in range(PER_CAT_LANG):
            body, t = unique(lambda: make(i, lang), seen)
            out.append((lang, body, t))
    return out


GENERATORS = {'lookup': lookups, 'convert': conversions, 'extract': extraction, 'multistep': multistep, 'highrisk': highrisk}


def build():
    rng = random.Random(SEED)
    items = []
    for cat in CATEGORIES:
        rows = GENERATORS[cat](rng)
        assert len(rows) == 2 * PER_CAT_LANG, (cat, len(rows))
        for lang in ('fa', 'en'):
            mine = [r for r in rows if r[0] == lang]
            dev = set(rng.sample(range(len(mine)), DEV_PER_CAT_LANG))
            for i, (_, prompt, truth) in enumerate(mine):
                items.append({'id': f'{cat[:3].upper()}-{lang}-{i + 1:02d}', 'category': cat, 'lang': lang,
                              'split': 'dev' if i in dev else 'test', 'risk': cat in RISK,
                              'prompt': prompt, 'truth': truth, 'chars': len(prompt)})
    return items


def load(split='all'):
    if not TASKS.exists():
        save(build())
    items = json.loads(TASKS.read_text(encoding='utf-8'))['items']
    return items if split == 'all' else [x for x in items if x['split'] == split]


def save(items):
    TASKS.parent.mkdir(parents=True, exist_ok=True)
    TASKS.write_text(json.dumps({'about': 'HMD-022 task set, generated by taskset.py (seed 22). ILLUSTRATIVE: '
                                          'invented texts and fictional medicines; leaflets are not medical advice.',
                                 'seed': SEED, 'items': items}, ensure_ascii=False, indent=1), encoding='utf-8')


def stats(items):
    lines = [f'{len(items)} items · ' + ' · '.join(f'{s} {n}' for s, n in sorted(Counter(x["split"] for x in items).items()))]
    lines.append(f'{"category":10} {"lang":4} {"dev":>4} {"test":>5} {"mean chars":>11}')
    for cat in CATEGORIES:
        for lang in ('fa', 'en'):
            xs = [x for x in items if x['category'] == cat and x['lang'] == lang]
            lines.append(f'{cat:10} {lang:4} {sum(x["split"] == "dev" for x in xs):4} {sum(x["split"] == "test" for x in xs):5} '
                         f'{sum(x["chars"] for x in xs) / len(xs):11.0f}')
    lines.append('truth types: ' + ', '.join(f'{k} {v}' for k, v in sorted(Counter(x["truth"]["type"] for x in items).items())))
    return '\n'.join(lines)


if __name__ == '__main__':
    its = build()
    save(its)
    print(stats(its))
