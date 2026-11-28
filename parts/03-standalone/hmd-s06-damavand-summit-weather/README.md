# HMD-S06 · Silent Breakthrough · فردا سر دماوند چه خبر است؟

**قالب:** Silent Breakthrough · **فصل ۱، پس از HMD-009 و پیش از HMD-010** · **هوک:** Shock/Contradiction («سه مدل، یک قله، سه جواب»)
**وضعیت:** آمادهٔ تمرین (۲۸ نوامبر ۲۰۲۶) با replay واقعی. دو چیز منتظر محمد: **تصمیم مجوز Open-Meteo** و **گروه کوهنوردی برای سنجش میدانی** ([RUN]). هیچ API پولی استفاده نشد.
**زمان برآوردی:** حدود ۱۲:۱۰ · **واژهٔ گفتاری:** ۱٬۴۴۹ · **قاب:** ۱۵ · **قاب‌های دک:** ۱۵ + کاور

**جملهٔ مرکزی:** در دادهٔ باز ۰٫۲۵ درجه، زمینِ مدل زیر قلهٔ دماوند حدود ۲٬۸۰۰ متر است (IFS ۲٬۸۰۶، AIFS ۲٬۷۲۷، GFS ۲٬۷۳۳). عددهای «سطحی» مدل مال این کوه خیالی‌اند؛ برای همین بیشینهٔ تندباد ۱۰ متری سه مدل تا حدود ۷ برابر فرق داشت (۱۴ تا ۹۹ km/h). باد هوای آزاد در ارتفاع واقعی، از همان مدل‌ها، فقط حدود ۱٫۲ برابر فرق داشت (۵۵ تا ۶۸). آنچه می‌ماند، زمان‌بندی است؛ آن را با چند مدل و پیش‌بینی گروهی (۵۱ عضو) به زبان احتمال می‌گوییم، در جدولی که هیچ خانه‌اش «امن» نیست.

**مرز ادعا:** ابزار آموزشی است؛ جای هشدار رسمی، راهنمای محلی و سرپرست برنامه را نمی‌گیرد؛ آستانه‌ها انتخاب تحریریه‌اند و با هیچ اندازه‌گیری میدانی سنجیده نشده‌اند؛ عددها مال روز اجرای ما هستند.

## فایل‌ها

| فایل | چیست |
|---|---|
| [`script-fa.md`](script-fa.md) | متن ضبط v6، ۱۵ قاب |
| [`hooks-fa.md`](hooks-fa.md) | پنج هوک؛ Shock/Contradiction انتخاب شده، هوک ۲ نسخهٔ بی‌Open-Meteo |
| [`package-fa.md`](package-fa.md) | عنوان، تامبنیل، توضیحات (با متن اعتبار ECMWF)، Chapters، دو Short، پست Community |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ دک → `deck-fa.html` و `deck-en.html` (`python3 scripts/build-decks.py --only hmd-s06`) |
| [`sources.md`](sources.md) | منابع S01–S17، وضعیت هر کدام، جدول «هر عدد از کجا»، چیزهایی که بیرون ماندند |
| [`study-fa.md`](study-fa.md) | **سند مطالعه برای محمد**: فشار، افت دما، زمین مدل، باد، سرمای باد، ensemble، طرح سرویس، GRIB و مجوز؛ ۱۱ سؤال |
| [`cheatsheet-fa.md`](cheatsheet-fa.md) | یک صفحه برای روز ضبط |
| [`prep-fa.md`](prep-fa.md) | آنچه محمد باید بگیرد، تمرین، شات‌ها، چک‌لیست، ریسک‌ها |
| [`artifact/summit_live.py`](artifact/summit_live.py) | دموی زنده: گرفتن داده، ساخت صفحه، سرور محلی (`--serve`)، `--offline`، `--replay`، `--selftest` |
| [`artifact/summit_fetch.py`](artifact/summit_fetch.py) | ECMWF Open Data (چند بازهٔ بایت در یک درخواست، نیمهٔ اول هر پیام)، NOMADS GFS، Open-Meteo اختیاری |
| [`artifact/grib2_point.py`](artifact/grib2_point.py) | رمزگشای GRIB2 با پایتون خالص (CCSDS/AEC و بستهٔ ساده)، فقط چند نقطه |
| [`artifact/summit_core.py`](artifact/summit_core.py) | فیزیک و منطق هشدار: جو استاندارد، افت دما، هوای آزاد، سرمای باد، آستانه‌ها، پنجره‌ها |
| [`artifact/summit_selftest.py`](artifact/summit_selftest.py) | وارسی‌های بی‌شبکه |
| `artifact/summit_page.html` → `artifact/summit_live.html` | قالب و صفحهٔ ساخته‌شده (چهار نما: کنار هم، اصلاح ارتفاع، پنجره‌ها، منطق هشدار). نسخهٔ موجود در مخزن replay ۲۸ نوامبر **بدون** Open-Meteo است (فقط IFS، AIFS، GFS)؛ با `--offline` و کش محلی `data/`، ICON و ensemble هم می‌آیند |
| [`artifact/derived/`](artifact/derived/SOURCE.txt) | `replay-2026-11-28.json`، `latest.json`، خلاصهٔ Open-Meteo، `SOURCE.txt` (sha256، مجوز) |
| `artifact/data/` | پاسخ خام Open-Meteo (git-ignored؛ فقط تمرین) |
| [`media/CREDITS.md`](media/CREDITS.md) | هیچ تصویر بیرونی؛ فهرست «دانلود نشد» |

## وارسی‌ها (۲۸ نوامبر ۲۰۲۶)

- `python3 -I artifact/summit_live.py --selftest` (کلیدها unset، بی‌شبکه) → `selftest ok`: شش عدد چارت سرمای باد کانادا؛ نسخهٔ متریک و آمریکایی فرمول؛ ارتفاع ۵۰۰/۶۰۰/۷۰۰ در جو استاندارد؛ رفت‌وبرگشت CCSDS روی ۱۲٬۸۰۵ نمونه با هر چهار گزینهٔ کدگذاری؛ GRIB2 template 5.0 و 5.42؛ ارتفاع ۵۰۰ هکتوپاسکال IFS (CCSDS) و GFS (بستهٔ ساده) در ۱۳ زمان مشترک حداکثر ۱۷ متر اختلاف.
- `python3 scripts/voice-lint.py …/script-fa.md` → exit 0 (۱٬۴۴۹ واژه؛ همهٔ قاب‌ها ۱۱۰ تا ۱۴۱ واژه در دقیقه).
- `python3 scripts/build-decks.py --only hmd-s06` → `ok · 15 beats + cover`، بدون هشدار.
- اسکرین‌شات Chrome بی‌سر (۱۶۰۰×۹۰۰) از چهار نمای دمو و چند قاب دک (fa و en).

## پیش از ضبط باید حل شود

- [ ] **تصمیم Open-Meteo** (`prep-fa.md` §۱). اگر «نه»: هوک ۲، و نسخهٔ بی‌Open-Meteo قاب‌های ۸ تا ۱۰ (یادداشت تدوین `script-fa.md`).
- [x] مختصات قله و بارگاه سوم با OpenStreetMap چک شد (حدود ۱۰۰ و ۶۰ متر اختلاف؛ `sources.md` S11b). GPS گروه اختیاری.
- [ ] اجرای زندهٔ روز ضبط و تطبیق عددها با متن و دک.
- [ ] [RUN] گروه کوهنوردی برای سنجش میدانی (قسمت پیگیری؛ تا آن موقع قاب ۱۲ کارت NOT RUN YET).
- [ ] جملهٔ «ERA5 قله را ۵٬۴۷۳ متر می‌بیند» در `docs/host-study-standard.md` §۷ با دادهٔ ما نمی‌خواند (`sources.md`، «بیرون ماند»)؛ به هماهنگ‌کننده گزارش شد.

## چه چیزهایی سر ضبط بگیری

جدول کامل در `prep-fa.md` §۵: چهره (قاب ۱، ۹، ۱۳)، چهار نمای دمو (قاب ۴، ۵، ۸، ۹، ۱۰، ۱۱، ۱۴)، دک برای بقیه.
