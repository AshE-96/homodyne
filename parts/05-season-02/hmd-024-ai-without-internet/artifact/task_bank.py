"""HMD-024 · the 30 fixed tasks (15 Persian, 15 English), with their answer keys.

Every text here is synthetic: written for this episode by Homodyne, about invented people, shops and
parcels. No outside text is used, so there is nothing to license. Names, prices and dates are made up.

Six categories, five tasks each; the language of a task is the language of its input text:

    summarise  3 fa + 2 en   N bullet points; graded by format + required key points (auto)
    extract    2 fa + 3 en   JSON fields (dates, amounts, names); field match (auto)  — the HMD-020 link
    qa         3 fa + 2 en   answer from a passage; 2 of 5 have NO answer in the passage (auto)
    translate  2 fa→en + 3 en→fa   owner's blind checklist is the main grade; required-terms check is auto
    classify   3 fa + 2 en   one label from a fixed list (auto)
    nogo       2 fa + 3 en   multi-step reasoning and long context, where small models are expected to struggle

The tasks were written before any model was run, to look like everyday requests. The no-go category is
hard on purpose. Do not edit tasks after a run: results are keyed by task id and prompt hash.

    python3 task_bank.py            # print a table of the tasks
"""
import hashlib
import random

SYSTEM = ('You are a careful assistant. Follow the instructions exactly. '
          'Use only the text you are given. Do not add explanations unless asked.')
NOT_IN_TEXT = 'NOT_IN_TEXT'


def _sum_fa(n, text):
    return (f'متن زیر را در دقیقاً {n} نکتهٔ کوتاه خلاصه کن. هر نکته را در یک خط جدا و با «- » شروع کن. '
            f'چیزی جز همین {n} خط ننویس.\n\nمتن:\n{text}')


def _sum_en(n, text):
    return (f'Summarise the text below in exactly {n} short points. Put each point on its own line starting '
            f'with "- ". Write nothing except those {n} lines.\n\nText:\n{text}')


def _ext_fa(fields, text):
    return (f'از متن زیر این فیلدها را بیرون بکش و فقط یک شیء JSON بنویس، بدون توضیح و بدون ``` : {fields}\n\n'
            f'متن:\n{text}')


def _ext_en(fields, text):
    return f'Extract these fields from the text below and write only one JSON object, no explanation, no ```: {fields}\n\nText:\n{text}'


def _qa_fa(text, q):
    return (f'فقط با تکیه بر متن زیر جواب بده. فقط جواب کوتاه را بنویس. اگر جواب در متن نیست، دقیقاً بنویس: '
            f'{NOT_IN_TEXT}\n\nمتن:\n{text}\n\nپرسش: {q}')


def _qa_en(text, q):
    return (f'Answer using only the text below. Write only the short answer. If the answer is not in the text, '
            f'write exactly: {NOT_IN_TEXT}\n\nText:\n{text}\n\nQuestion: {q}')


def _tr_fa_en(text):
    return f'این بند را به انگلیسی روان ترجمه کن. فقط ترجمه را بنویس.\n\n{text}'


def _tr_en_fa(text):
    return f'Translate this paragraph into natural Persian (Farsi). Write only the translation.\n\n{text}'


def _cls_fa(labels, text):
    return f'فقط یکی از این برچسب‌ها را بنویس و هیچ چیز دیگر: {"، ".join(labels)}\n\nپیام:\n{text}'


def _cls_en(labels, text):
    return f'Write only one of these labels and nothing else: {", ".join(labels)}\n\nMessage:\n{text}'


def _nogo_fa(text):
    return f'{text}\n\nقدم‌به‌قدم فکر کن، بعد در خط آخر فقط بنویس: ANSWER: <جواب>'


def _nogo_en(text):
    return f'{text}\n\nThink step by step, then on the last line write only: ANSWER: <answer>'


# ── long-context generators (deterministic) ──────────────────────────────────────────────────
CITIES = [('تبریز', 'Tabriz'), ('شیراز', 'Shiraz'), ('مشهد', 'Mashhad'), ('اصفهان', 'Isfahan'), ('رشت', 'Rasht'),
          ('کرمان', 'Kerman'), ('یزد', 'Yazd'), ('اهواز', 'Ahvaz'), ('همدان', 'Hamedan'), ('ساری', 'Sari'),
          ('زنجان', 'Zanjan'), ('قزوین', 'Qazvin'), ('کاشان', 'Kashan'), ('ارومیه', 'Urmia'), ('بندرعباس', 'Bandar Abbas')]
STATUS_FA = ['تحویل شد', 'در راه است', 'در انبار است', 'برگشت خورد']
STATUS_EN = ['delivered', 'in transit', 'in the warehouse', 'returned']
FA_DIGITS = str.maketrans('0123456789.', '۰۱۲۳۴۵۶۷۸۹٫')


def logbook(lang, n, needles, seed):
    """n lines of a parcel log. `needles` maps line index -> (code, city_index, weight). Codes are unique."""
    rnd = random.Random(seed)
    codes = rnd.sample(range(1000, 9999), n)
    used = {c for c, _, _ in needles.values()}
    lines = []
    for i in range(n):
        if i in needles:
            code, ci, w = needles[i]
        else:
            code = codes[i]
            while code in used:
                code += 1
            ci, w = rnd.randrange(len(CITIES)), round(rnd.uniform(0.4, 9.8), 1)
        if lang == 'fa':
            st = STATUS_FA[rnd.randrange(4)]
            lines.append(f'ردیف {i + 1}: بستهٔ {code} به {CITIES[ci][0]} فرستاده شد؛ وزن {w} کیلو؛ وضعیت: {st}.'
                         .translate(FA_DIGITS))
        else:
            st = STATUS_EN[rnd.randrange(4)]
            lines.append(f'Line {i + 1}: parcel {code} sent to {CITIES[ci][1]}; weight {w} kg; status: {st}.')
    return '\n'.join(lines)


LONG_FA = logbook('fa', 160, {88: (7318, 9, 4.6)}, seed=24)                      # needle: 7318 -> Sari
LONG_EN = logbook('en', 220, {61: (2051, 3, 3.7), 157: (6604, 12, 4.2)}, seed=2024)  # 3.7 + 4.2 = 7.9

# ── the 30 tasks ──────────────────────────────────────────────────────────────────────────────
# grader kinds: points · fields · short · absent · terms · label · final
TASKS = [
    # summarise ───────────────────────────────────────────────────────────────────────────
    dict(id='sum-1', cat='summarise', lang='fa', grader='points', n=3,
         keypoints=[[['آب'], ['سه‌شنبه', 'سه شنبه']], [['شارژ'], ['۴۵۰', '450', 'چهارصد و پنجاه']], [['جلسه', 'نشست'], ['جمعه']]],
         prompt=_sum_fa(3, 'همسایه‌های عزیز، سلام. به اطلاع می‌رسانیم که روز سه‌شنبه از ساعت ۹ تا ۱۳ آب ساختمان '
                           'برای تعویض لولهٔ اصلی قطع می‌شود؛ لطفاً از قبل آب ذخیره کنید. از ماه آینده، به‌خاطر '
                           'قرارداد تازهٔ سرویس آسانسور، شارژ ماهانهٔ هر واحد به ۴۵۰ هزار تومان می‌رسد. برای '
                           'گفت‌وگو دربارهٔ رنگ‌آمیزی راه‌پله هم جمعه ساعت ۱۸ در لابی جلسه داریم. حضور یک نفر از '
                           'هر واحد کافی است. با تشکر، هیئت‌مدیرهٔ ساختمان یاس.')),
    dict(id='sum-2', cat='summarise', lang='fa', grader='points', n=3,
         keypoints=[[['ساعت', 'تا'], ['۲۲', '22', 'ده شب']], [['کتاب'], ['الکترونیک', 'دیجیتال', 'آنلاین']], [['دانشجو', 'دانش‌آموز'], ['رایگان', 'حق عضویت', 'هزینه']]],
         prompt=_sum_fa(3, 'کتابخانهٔ عمومی محلهٔ نارون از اول خرداد ساعت کارش را تغییر می‌دهد و هر روز تا ساعت ۲۲ '
                           'باز است. از همین ماه، اعضا می‌توانند با همان کارت عضویت، کتاب الکترونیک هم امانت بگیرند. '
                           'حق عضویت سالانه برای دانشجوها و دانش‌آموزها رایگان شده است. ساختمان کتابخانه تغییری '
                           'نکرده و ورودی همچنان از خیابان شقایق است.')),
    dict(id='sum-3', cat='summarise', lang='fa', grader='points', n=3,
         keypoints=[[['عرضه', 'انتشار', 'راه‌اندازی'], ['دو هفته', '۲ هفته', '2 هفته', '۲۵', '25']], [['بودجه'], ['۱۰', '10', 'ده درصد']], [['سارا'], ['آزمون', 'تست']]],
         prompt=_sum_fa(3, 'خلاصهٔ جلسهٔ تیم اپلیکیشن نوبت‌دهی: تاریخ عرضهٔ نسخهٔ تازه دو هفته عقب افتاد و حالا ۲۵ خرداد '
                           'است، چون بخش پرداخت هنوز با بانک آزموده نشده. بودجهٔ تبلیغات این فصل ده درصد کم شد. '
                           'مسئولیت آزمون نهایی با سارا است و تا پنجشنبه گزارشش را می‌فرستد. جلسهٔ بعد شنبه ساعت ۱۰.')),
    dict(id='sum-4', cat='summarise', lang='en', grader='points', n=3,
         keypoints=[[['battery']], [['$49', '49']], [['june 3', '3 june', 'june']]],
         prompt=_sum_en(3, 'Hello from the Lumo team! The new Lumo 2 desk lamp keeps the same price as before, $49, '
                           'but its battery now lasts about twice as long on a single charge. We also replaced the '
                           'touch button with a simple dial after many of you asked for it. Pre-orders are open today '
                           'and shipping starts on June 3. Thank you for sticking with a small company.')),
    dict(id='sum-5', cat='summarise', lang='en', grader='points', n=3,
         keypoints=[[['museum']], [['lunch']], [['monday'], ['form', 'slip', 'permission', 'consent']]],
         prompt=_sum_en(3, 'Dear parents, Year 5 will visit the City Science Museum next Thursday. The bus leaves the '
                           'school at 8:30 and returns by 15:00. Children should bring a packed lunch and a water '
                           'bottle, because the museum cafe will be closed. Please return the signed permission form '
                           'to the class teacher by Monday; children without a form cannot join the trip.')),
    # extract ─────────────────────────────────────────────────────────────────────────────
    dict(id='ext-1', cat='extract', lang='fa', grader='fields',
         fields={'seller': ('str', ['نیلوفر']), 'date': ('date', '1406/02/12'), 'total_toman': ('int', 1285000),
                 'buyer': ('str', ['کامران صدری'])},
         prompt=_ext_fa('seller (نام فروشگاه)، date (تاریخ به شکل YYYY/MM/DD همان‌طور که در متن آمده)، '
                        'total_toman (مبلغ کل، عدد صحیح بدون جداکننده)، buyer (نام خریدار)',
                        'فاکتور فروش · فروشگاه لوازم‌التحریر نیلوفر\nتاریخ: ۱۴۰۶/۰۲/۱۲\nخریدار: آقای کامران صدری\n'
                        'دفتر ۸۰ برگ × ۴: ۳۲۰٬۰۰۰ تومان\nخودکار آبی × ۱۰: ۲۵۰٬۰۰۰ تومان\nکیف مدرسه × ۱: ۷۱۵٬۰۰۰ تومان\n'
                        'مبلغ کل: ۱٬۲۸۵٬۰۰۰ تومان\nپرداخت: کارت‌خوان')),
    dict(id='ext-2', cat='extract', lang='fa', grader='fields',
         fields={'landlord': ('str', ['مهتاب رحیمی']), 'start_date': ('date', '1406/03/01'),
                 'deposit_toman': ('int', 300000000), 'rent_toman': ('int', 12000000)},
         prompt=_ext_fa('landlord (نام موجر)، start_date (تاریخ شروع به شکل YYYY/MM/DD)، deposit_toman (ودیعه به '
                        'تومان، عدد صحیح کامل)، rent_toman (اجارهٔ ماهانه به تومان، عدد صحیح کامل)',
                        'این قرارداد میان خانم مهتاب رحیمی (موجر) و آقای بهزاد کیانی (مستأجر) برای یک واحد '
                        'شصت‌متری در طبقهٔ دوم بسته می‌شود. مدت اجاره یک سال است و از ۱۴۰۶/۰۳/۰۱ شروع می‌شود. '
                        'مستأجر ۳۰۰ میلیون تومان ودیعه می‌پردازد و اجارهٔ ماهانه ۱۲ میلیون تومان است که تا پنجم '
                        'هر ماه واریز می‌شود.')),
    dict(id='ext-3', cat='extract', lang='en', grader='fields',
         fields={'passenger': ('str', ['Leila Navabi']), 'flight': ('code', 'HM482'), 'date': ('date', '2027-04-18'),
                 'fare_eur': ('num', 312.40)},
         prompt=_ext_en('passenger, flight (code), date (YYYY-MM-DD), fare_eur (number)',
                        'Booking confirmed. Passenger: Ms Leila Navabi. Flight HM 482 from Vienna to Lisbon departs '
                        'on 18 April 2027 at 07:15. Seat 14C. Total fare paid: EUR 312.40, including one checked bag. '
                        'Please arrive at the airport two hours before departure.')),
    dict(id='ext-4', cat='extract', lang='en', grader='fields',
         fields={'organiser': ('str', ['Tomas Berg']), 'date': ('date', '2027-03-09'), 'time': ('time', '14:30'),
                 'room': ('code', 'B2')},
         prompt=_ext_en('organiser, date (YYYY-MM-DD), time (HH:MM, 24-hour), room',
                        'Hi all, Tomas Berg here. I have booked room B2 for our quarterly review on Tuesday, 9 March '
                        '2027, starting at 2:30 pm. It should take about an hour. Please bring last quarter\'s numbers. '
                        'If you cannot come, send me a note by Monday.')),
    dict(id='ext-5', cat='extract', lang='en', grader='fields',
         fields={'customer': ('str', ['Nadia Farrokh']), 'device': ('str', ['washing machine']),
                 'total_usd': ('num', 1240), 'valid_until': ('date', '2027-06-30')},
         prompt=_ext_en('customer, device, total_usd (number), valid_until (YYYY-MM-DD)',
                        'Repair quote for Nadia Farrokh. Device: washing machine (front loader, 8 kg). Parts: new drum '
                        'bearing and door seal. Labour: 3 hours. Total: USD 1,240 including tax. This quote is valid '
                        'until June 30, 2027. Reply YES to book a technician.')),
    # qa ──────────────────────────────────────────────────────────────────────────────────
    dict(id='qa-1', cat='qa', lang='fa', grader='short', accept=['7', 'هفت'],
         prompt=_qa_fa('نانوایی سنگکی گلستان شنبه تا پنجشنبه ساعت ۶ صبح باز می‌کند و تا ۲ بعدازظهر کار می‌کند. '
                       'جمعه‌ها یک ساعت دیرتر، ساعت ۷، باز می‌کند و تا ظهر نان می‌پزد. سفارش بیش از بیست نان را '
                       'باید یک روز زودتر تلفنی ثبت کرد.', 'نانوایی جمعه‌ها ساعت چند باز می‌کند؟')),
    dict(id='qa-2', cat='qa', lang='fa', grader='short', accept=['26', 'بیست و شش', 'بیست‌وشش'],
         prompt=_qa_fa('در شرکت طراحی آبنوس، هر کارمند تمام‌وقت سالی ۲۶ روز مرخصی با حقوق دارد. کارمندهای پاره‌وقت '
                       'به نسبت ساعت کارشان مرخصی می‌گیرند. مرخصی استفاده‌نشده تا ۹ روز به سال بعد منتقل می‌شود.',
                       'کارمند تمام‌وقت سالی چند روز مرخصی با حقوق دارد؟')),
    dict(id='qa-3', cat='qa', lang='fa', grader='absent',
         prompt=_qa_fa('پارک تازهٔ کنار رودخانه از اول تیر باز می‌شود. پارک یک مسیر دوچرخه‌سواری سه‌کیلومتری، یک '
                       'زمین بازی برای کودکان و دو آب‌خوری دارد. ساعت کار پارک از ۶ صبح تا ۱۱ شب است و '
                       'نگهبان شب هم دارد.', 'هزینهٔ ورودی پارک چقدر است؟')),
    dict(id='qa-4', cat='qa', lang='en', grader='short', accept=['30', 'thirty'],
         prompt=_qa_en('With CityCycle, the first 30 minutes of every ride are free for members. After that, each '
                       'extra 15 minutes costs 50 cents. Bikes must be returned to any CityCycle dock; leaving a '
                       'bike elsewhere adds a 10-dollar fee.', 'How many minutes of each ride are free for members?')),
    dict(id='qa-5', cat='qa', lang='en', grader='absent',
         prompt=_qa_en('From 1 May, bus route 14 will no longer stop at Market Square, because of road works. '
                       'Passengers can use the temporary stop on Mill Lane, about 200 metres away. The timetable '
                       'stays the same, and the change is expected to last eight weeks.',
                       'Who is the head of the city transport department?')),
    # translate ─────────────────────────────────────────────────────────────────────────────
    dict(id='tr-1', cat='translate', lang='fa', grader='terms', direction='fa→en',
         terms=[['8'], ['22', '10 pm', '10 p.m', '10:00 pm', 'ten'], ['friday']],
         prompt=_tr_fa_en('داروخانهٔ شبانه‌روزی نیست، ولی از این هفته از ساعت ۸ صبح تا ۲۲ باز است. جمعه‌ها تعطیل '
                          'است. برای داروهای یخچالی، لطفاً پیش از آمدن تماس بگیرید.')),
    dict(id='tr-2', cat='translate', lang='fa', grader='terms', direction='fa→en',
         terms=[['rice'], ['two hours', '2 hours'], ['salt']],
         prompt=_tr_fa_en('برنج را دو ساعت در آب خیس کن. بعد آبش را بریز، دو لیوان آب تازه و یک قاشق نمک اضافه کن '
                          'و روی حرارت ملایم بگذار تا دم بکشد.')),
    dict(id='tr-3', cat='translate', lang='en', grader='terms', direction='en→fa',
         terms=[['23', '۲۳', 'یازده'], ['15', '۱۵', 'پانزده', 'یک ربع'], ['سرور']],
         prompt=_tr_en_fa('The server will restart at 23:00 tonight. Please save your work before then. The update '
                          'takes about 15 minutes, and you do not need to do anything afterwards.')),
    dict(id='tr-4', cat='translate', lang='en', grader='terms', direction='en→fa',
         terms=[['14', '۱۴', 'چهارده'], ['کتاب'], ['تمدید']],
         prompt=_tr_en_fa('Books can be borrowed for 14 days. You can renew a loan once, online or at the desk, as '
                          'long as nobody else has reserved the book.')),
    dict(id='tr-5', cat='translate', lang='en', grader='terms', direction='en→fa',
         terms=[['5', '۵', 'پنج'], ['دلار'], ['سه روز', '۳ روز', '3 روز']],
         prompt=_tr_en_fa('We are sorry your order arrived late. We will refund the shipping fee of 5 dollars to your '
                          'card within three days.')),
    # classify ──────────────────────────────────────────────────────────────────────────────
    dict(id='cls-1', cat='classify', lang='fa', grader='label', labels=['مثبت', 'منفی', 'خنثی'], answer='منفی',
         synonyms={'منفی': ['negative'], 'مثبت': ['positive'], 'خنثی': ['neutral']},
         prompt=_cls_fa(['مثبت', 'منفی', 'خنثی'], 'سلام، سفارشم سه هفته است نرسیده و هر بار تماس می‌گیرم کسی '
                        'جواب نمی‌دهد. واقعاً ناامید شده‌ام.')),
    dict(id='cls-2', cat='classify', lang='fa', grader='label', labels=['مالی', 'سلامت', 'آموزش', 'فناوری'],
         answer='مالی', synonyms={'مالی': ['finance', 'financial']},
         prompt=_cls_fa(['مالی', 'سلامت', 'آموزش', 'فناوری'], 'قسط این ماه وام شما در تاریخ ۵ خرداد از حسابتان '
                        'برداشت می‌شود. لطفاً موجودی کافی داشته باشید تا جریمهٔ دیرکرد نخورید.')),
    dict(id='cls-3', cat='classify', lang='fa', grader='label', labels=['مثبت', 'منفی', 'خنثی'], answer='خنثی',
         synonyms={'منفی': ['negative'], 'مثبت': ['positive'], 'خنثی': ['neutral']},
         prompt=_cls_fa(['مثبت', 'منفی', 'خنثی'], 'جلسهٔ فردا ساعت ۱۰ در اتاق ۳ برگزار می‌شود. دستور جلسه پیوست است.')),
    dict(id='cls-4', cat='classify', lang='en', grader='label', labels=['positive', 'negative', 'neutral'],
         answer='positive',
         prompt=_cls_en(['positive', 'negative', 'neutral'], 'Thanks so much! The repair was quick and the price '
                        'was fair. I will come back next time.')),
    dict(id='cls-5', cat='classify', lang='en', grader='label', labels=['finance', 'health', 'education', 'technology'],
         answer='education',
         prompt=_cls_en(['finance', 'health', 'education', 'technology'], 'The school has moved the maths exam from '
                        'Monday to Wednesday, and the revision class will now be on Tuesday afternoon.')),
    # nogo ──────────────────────────────────────────────────────────────────────────────────
    dict(id='nogo-1', cat='nogo', lang='fa', grader='final', kind='reasoning', accept=['25', 'بیست و پنج', 'بیست‌وپنج'],
         prompt=_nogo_fa('علی ۴ جعبه مداد دارد و در هر جعبه ۱۲ مداد است. ۸ مداد به دوستش می‌دهد. بعد نصف مدادهای '
                         'باقی‌مانده را به خواهرش می‌دهد. آخر هفته ۵ مداد تازه می‌خرد. حالا علی چند مداد دارد؟')),
    dict(id='nogo-2', cat='nogo', lang='fa', grader='final', kind='long', accept=['ساری', 'sari'],
         prompt=_nogo_fa(f'این دفتر ثبت بسته‌های یک شرکت پست است:\n\n{LONG_FA}\n\nپرسش: بستهٔ ۷۳۱۸ به کدام شهر '
                         f'فرستاده شد؟ فقط نام شهر را بنویس.')),
    dict(id='nogo-3', cat='nogo', lang='en', grader='final', kind='reasoning', accept=['11:40'],
         prompt=_nogo_en('A train is scheduled to leave at 08:40. The trip takes 2 hours and 35 minutes. Today it '
                         'leaves 25 minutes late and loses another 10 minutes on the way, then makes up 10 minutes '
                         'before arriving. At what time does it arrive? Give the time as HH:MM.')),
    dict(id='nogo-4', cat='nogo', lang='en', grader='final', kind='reasoning', accept=['ana'],
         prompt=_nogo_en('Ana, Ben, Cyrus and Dara stand in a line, numbered 1 to 4 from the left. Ben stands directly '
                         'to the right of Dara. Ana does not stand next to Ben. Cyrus stands at the left end. Dara '
                         'does not stand at either end. Who is second from the left?')),
    dict(id='nogo-5', cat='nogo', lang='en', grader='final', kind='long', accept=['7.9'],
         prompt=_nogo_en(f'This is a courier company log:\n\n{LONG_EN}\n\nQuestion: what is the total weight in kg '
                         f'of parcel 2051 and parcel 6604 together? Give one number.')),
]

CATS = ['summarise', 'extract', 'qa', 'translate', 'classify', 'nogo']
CAT_FA = {'summarise': 'خلاصه در چند نکته', 'extract': 'بیرون‌کشیدن فیلد به JSON', 'qa': 'جواب از روی متن',
          'translate': 'ترجمهٔ فارسی/انگلیسی', 'classify': 'دسته‌بندی لحن یا موضوع', 'nogo': 'استدلال چندمرحله‌ای و متن بلند'}
CAT_EN = {'summarise': 'Summarise to N points', 'extract': 'Extract fields to JSON', 'qa': 'Answer from a passage',
          'translate': 'Translate fa↔en', 'classify': 'Classify tone or topic', 'nogo': 'No-go: multi-step / long text'}


def prompt_hash(t):
    return hashlib.sha256((SYSTEM + '\n' + t['prompt']).encode()).hexdigest()[:12]


def check_bank():
    assert len(TASKS) == 30 and len({t['id'] for t in TASKS}) == 30
    for c in CATS:
        assert sum(t['cat'] == c for t in TASKS) == 5, c
    assert sum(t['lang'] == 'fa' for t in TASKS) == 15
    assert LONG_FA.count('۷۳۱۸') == 1 and LONG_EN.count('parcel 2051 ') == 1 and LONG_EN.count('parcel 6604 ') == 1
    return True


if __name__ == '__main__':
    check_bank()
    for t in TASKS:
        print(f'{t["id"]:7} {t["cat"]:10} {t["lang"]}  {len(t["prompt"]):6} chars  {prompt_hash(t)}')
