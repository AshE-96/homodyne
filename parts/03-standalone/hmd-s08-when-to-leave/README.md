# HMD-S08 · Silent Breakthrough · کی راه بیفتم که به‌موقع برسم؟

**قالب:** Silent Breakthrough (دنبالهٔ HMD-009) · **زنجیره:** HMD-S07 (چالوس کی خلوت است؟) ← **HMD-S08** → HMD-010 (نمرهٔ منفی می‌تواند AI را محتاط‌تر کند؟) · **پخش:** ۲۸ اسفند ۱۴۰۵ (۱۹ مارس ۲۰۲۷) · **هوک:** Shock/Contradiction
**وضعیت:** آمادهٔ تمرین (۲۸ نوامبر ۲۰۲۶). همهٔ عددها خروجی `artifact/leave_live.py --report` روی دادهٔ واقعی TLC است؛ `--selftest` سبز. هیچ API پولی، کلید یا ورود. هیچ [RUN] یا [VERIFY] باز در متن گفتاری.
**زمان برآوردی:** حدود ۱۱:۵۵ · **واژهٔ گفتاری:** ۱۴۷۸ · **قاب:** ۱۵ · **دک:** ۱۵ قاب + کاور

**جملهٔ مرکزی:** برای «به‌موقع رسیدن» میانگین زمان سفر یعنی شیر یا خط؛ باید صدکِ توزیعِ همان ساعت حرکت را برداشت که با هزینهٔ دیر و زود رسیدنت جور است (q = هزینهٔ دیر ÷ (دیر + زود))، و بعد دید روی روزهای تازه واقعاً همان‌قدر مطمئن است یا نه.

**مرز ادعا:** حساب خودمان روی چهار مسیر تاکسی زرد نیویورک در روزهای کاری مارس و آوریل ۲۰۲۶ (زمان کنتور، بدون انتظار و بازرسی)؛ دربارهٔ تهران یا الگوریتم Google Maps چیزی ثابت نمی‌کند. «۹۵٪» در مسیر JFK روی روزهای ۱۳ تا ۳۰ آوریل حدود ۸۹٪ از آب درآمد.

## نتیجهٔ سرخط (JFK، مهلت ۱۸:۰۰)

| قاعده | ساعت حرکت | به‌موقع در روزهای آموزش | دیر در ۱۴ روز آزمون |
|---|---|---:|---:|
| اعتماد به میانگین (۷۴٫۸ دقیقه) | ۱۶:۴۵ | ۵۲٫۱٪ | ۷۲٫۷٪ (۵۶ از ۷۷) |
| اطمینان ۹۵٪ (صدک ۹۵ همان ساعت) | ۱۶:۲۰ | ۹۶٫۸٪ | ۸٫۳٪ (۹ از ۱۰۸) |

۳۱ مهلت × ۴ مسیر، دیرِ قاعدهٔ ۹۵٪: لاگواردیا ۳٫۷٪ · نیوآرک ۵٫۱٪ · محلهٔ مالی ۶٫۱٪ · JFK ۱۱٫۰٪.

## فایل‌ها

| فایل | چیست |
|---|---|
| [`script-fa.md`](script-fa.md) | متن ضبط v6، ۱۵ قاب |
| [`hooks-fa.md`](hooks-fa.md) | پنج هوک؛ Shock/Contradiction انتخاب شده (Story-Open به‌خاطر HMD-010 ممنوع) |
| [`package-fa.md`](package-fa.md) | عنوان، تامبنیل، توضیحات، Chapters، دو Short، پست Community |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ دک → `deck-fa.html` و `deck-en.html` (`python3 scripts/build-decks.py --only hmd-s08`) |
| [`sources.md`](sources.md) | منابع S1–S9، وضعیت هر کدام، جدول کامل محاسبه‌های ما |
| [`study-fa.md`](study-fa.md) | درس‌نامهٔ میزبان: توزیع، صدک، قاعدهٔ «رسیدن تا»، روزنامه‌فروش، FHWA، بک‌تست؛ ۱۲ پرسش |
| [`cheatsheet-fa.md`](cheatsheet-fa.md) | یک صفحه برای روز ضبط |
| [`prep-fa.md`](prep-fa.md) | چه چیزی بگیری (فقط ضبط صفحهٔ گوشی)، تمرین دمو، شات‌ها، چک‌لیست |
| [`artifact/leave_live.py`](artifact/leave_live.py) | دموی زنده: ساخت صفحه، `--serve`، `--report`، `--ask`، `--selftest` (stdlib) |
| [`artifact/leave_core.py`](artifact/leave_core.py) · [`leave_core.js`](artifact/leave_core.js) | ریاضی (صدک، قاعده، بک‌تست، FHWA، روزنامه‌فروش)؛ نسخهٔ JS همان، برای صفحه |
| `artifact/leave_page.html` → `artifact/leave_live.html` | قالب صفحه و صفحهٔ ساخته‌شده (یک نما، ۱۶۰۰×۹۰۰) |
| [`artifact/deck_figures.py`](artifact/deck_figures.py) | سه SVG دک از داده |
| [`artifact/leave_build.py`](artifact/leave_build.py) | بازسازی دادهٔ مشتق از parquet خام TLC (duckdb) |
| [`artifact/derived/`](artifact/derived/SOURCE.txt) | `weekday_trips.csv` (۳۰٬۷۵۰ سفر)، `episode_numbers.json`، `SOURCE.txt` (نشانی، مجوز، sha256، دستور) |
| [`media/CREDITS.md`](media/CREDITS.md) | هیچ تصویر بیرونی؛ فهرست «دانلود نشد» |

## اجرا (از پوشهٔ قسمت)

```bash
python3 -I artifact/leave_live.py --selftest                 # آفلاین، حدود ۱۰ ثانیه
python3 -I artifact/leave_live.py --serve                    # http://127.0.0.1:8768/leave_live.html?route=jfk&deadline=18:00&conf=95
python3 -I artifact/leave_live.py --ask jfk 18:00 95         # جواب ترمینالی (lga، ewr، fidi هم)
python3 -I artifact/leave_live.py --report                   # همهٔ عددهای قسمت → derived/episode_numbers.json
python3 -I artifact/deck_figures.py                          # SVGهای دک
```

## وارسی‌ها (۲۸ نوامبر ۲۰۲۶)

- `--selftest` → `selftest ok`: صدک = `statistics.quantiles(inclusive)`؛ کمینهٔ هزینهٔ تجربی = صدک q (۴ نسبت، روی داده‌ای ساختگی و ۳۵۷ سفر واقعی)؛ بک‌تست روی دادهٔ ساختگی با جواب معلوم؛ sha256 داده؛ همهٔ سطرها روز کاری؛ سطرهای JFK = سطرهای روز کاری HMD-009؛ اطمینان بالاتر هرگز حرکت دیرتر (۳۱ مهلت)؛ همهٔ عددهای متن و دک دوباره ساخته می‌شوند؛ JS صفحه = پایتون (node).
- `python3 scripts/voice-lint.py …/script-fa.md` → exit 0 (۱۴۷۸ واژه؛ همهٔ قاب‌ها ۱۱۱ تا ۱۴۶ واژه در دقیقه).
- `python3 scripts/build-decks.py --only hmd-s08` → `ok · 15 beats + cover`، بدون هشدار.
- اسکرین‌شات Chrome بی‌سر (۱۶۰۰×۹۰۰): ۳۲ قاب دک (fa و en) و سه حالت دمو.

## پیش از ضبط

- [ ] ضبط صفحهٔ «Arrive by» گوشی خودت (`prep-fa.md` §۱).
- [ ] روز ضبط صفحهٔ `TrafficModel` را دوباره باز کن.
- [ ] هماهنگی فوتیج چالوس با تدوین HMD-S07.
