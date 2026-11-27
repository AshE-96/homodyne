<div dir="rtl">

# HMD-K01 · Benchmark Lab · قسمت مستقل

## AI کنکور بدهد، کدام دانشگاه قبول می‌شود؟

**وضعیت (۲۷ نوامبر ۲۰۲۶):** متن، هوک‌ها، بستهٔ انتشار، دک فارسی و انگلیسی، منبع‌ها، پروتکل قفل‌شده و همهٔ ابزارها آماده‌اند. همهٔ selftestها بدون کلید و بدون شبکه گذشتند. **نیازمند اجرا [RUN]:** قاب ۷ تا ۱۲ و ۱۴ تا اجرای واقعی جای خالی و شاخه دارند و در دک `NOT RUN YET`. **هیچ سؤال واقعی هنوز رونویسی نشده**؛ منتظر PDFهای مالک است (`prep-fa.md` §۲).
**قالب:** Benchmark Lab · **زنجیره:** HMD-S01 (ریمان؛ تیزر: «ریاضیِ سخت آره؛ کنکور چی؟») ← **HMD-K01** ← HMD-005 (توکن فارسی؛ تیزر: «چرا یکی از مدل‌ها برای فارسی چند برابر توکن سوزوند؟»، شاخهٔ ب اگر فاصلهٔ توکن کم بود)
**زمان:** حدود ۱۲ دقیقه · ۱۴۸۳ واژهٔ گفتاری بدون جمله‌های [RUN] · ۱۵ قاب · هوک: **Curiosity-Gap** («ChatGPT پزشکی تهران قبول می‌شه؟»)

**جملهٔ مرکزی:** پنج مدل با قانون خود کنکور درصد می‌گیرند و زمان و خرجشان دیده می‌شود؛ ۱۴۰۵ (بعد از تاریخ برش بیشتر مدل‌ها) سرنخ آلودگی داده را می‌دهد؛ ولی قبولی را نمی‌شود ادعا کرد، چون ۶۰٪ نمرهٔ نهایی سوابق تحصیلی است.

**مرز ادعا:** یک نشستن، یک نسخه از هر مدل، یک روز؛ رتبه فقط بازهٔ تخمینی کنار چند کارنامهٔ منتشرشدهٔ کم‌اعتبار، با شرط سوابق کامل؛ افت ۱۴۰۵ اثبات آلودگی نیست؛ سرعت = سرویس در آن ساعت؛ توکن بین مدل‌ها هم‌واحد نیست.

> **دربارهٔ عنوان:** عنوان manifest «کدام دانشگاه» را می‌پرسد. شواهد عمومی (sources.md) فقط یک بازهٔ رتبهٔ پهن را پشتیبانی می‌کنند، نه نام دانشگاه. متن در قاب ۱۲ و ۱۴ صادقانه همین را می‌گوید. اگر این فاصلهٔ عنوان و جواب آزارت می‌دهد، عنوان C در `package-fa.md` بی‌خطرتر است.

## فایل‌ها

| فایل | محتوا |
|---|---|
| [prep-fa.md](prep-fa.md) | **دستورکار مالک**: کلیدها، PDFها، تمرین MOCK، پیش‌آزمون پولی، اجرای کامل، بازپخش، روز ضبط |
| [study-fa.md](study-fa.md) | **سند مطالعه** برای مالک: کنکور، ارزیابی مدل، آلودگی داده، آمار یک‌بار نشستن، چه بگو و چه نگو، خودآزمایی |
| [cheatsheet-fa.md](cheatsheet-fa.md) | **برگهٔ روز ضبط** (یک صفحه): پنج جمله، عددهای ثابت با منبع، جدول خالی عددهای اجرا، «نگو»، فرمان‌های تابلو |
| [script-fa.md](script-fa.md) | متن ضبط v6، ۱۵ قاب، شاخه‌های [RUN]، Pattern Interrupt Log، Retention Risk Map |
| [hooks-fa.md](hooks-fa.md) | پنج هوک + توصیه (Curiosity-Gap) |
| [package-fa.md](package-fa.md) | عنوان‌ها، تامبنیل، توضیحات، chapterها، تگ، کامنت پین، دو Short، Community |
| [`deck-fa.html`](deck-fa.html) · [`deck-en.html`](deck-en.html) | دک ضبط (ساخته‌شده) |
| [`deck.src.html`](deck.src.html) | منبع دوزبانه؛ بعد از ویرایش `python3 scripts/build-decks.py --only hmd-k01` |
| [sources.md](sources.md) | منابع R01 تا R13، «چه چیزی پیدا نشد»، محاسبه‌ها |
| [media/CREDITS.md](media/CREDITS.md) | تصاویر (فعلاً هیچ) و آنچه نباید روی صفحه بیاید |
| [artifact/protocol.md](artifact/protocol.md) | پروتکل قفل‌شده پیش از اجرای پولی |
| [artifact/konkur_prep.py](artifact/konkur_prep.py) | PDF ← صفحه، برش شکل، الگوی سؤال، اعتبارسنجی، diff دو رونویسی، کلید، نمونهٔ بازبینی |
| [artifact/konkur_run.py](artifact/konkur_run.py) | `plan` · `run` (نخ برای هر مدل، ازسرگیری، `--limit`، `--mock`) · `report` |
| [artifact/konkur_live.py](artifact/konkur_live.py) | تابلوی زنده: `--live` · `--replay RUN [--speed N]` · `--mock` |
| [artifact/rank_estimate.py](artifact/rank_estimate.py) | درصد ← بازهٔ رتبهٔ تخمینی (همیشه ESTIMATE) |
| [artifact/kcore.py](artifact/kcore.py) | دستور، schema، پارس جواب، درصد با منفی ⅓، بازه‌ها |
| `artifact/models.json` · `artifact/prices.json` | پنج slot (شناسه روز اجرا) · قیمت‌ها (مالک پر می‌کند؛ تا آن روز سقف «fallback») |
| `artifact/tables/` | `konkur_facts.json`، `anchors.json`، `SOURCE.txt` (جدول‌های کوچک مشتق‌شده) |
| `artifact/fixtures/synthetic-exam.json` | شش سؤال ساختگی برای selftest (هیچ سؤال واقعی در git نیست) |

**خارج از git:** `private/konkur/` (PDF، صفحه‌ها، برش‌ها، فایل سؤال‌ها، جواب خام مدل‌ها). `artifact/results/<run>/` فقط عدد و شناسهٔ سؤال دارد.

## اجرا (از ریشهٔ مخزن)

```bash
A=parts/03-standalone/hmd-k01-ai-takes-konkur/artifact
python3 $A/konkur_prep.py --selftest && python3 $A/konkur_run.py --selftest && python3 $A/konkur_live.py --selftest && python3 $A/rank_estimate.py --selftest
python3 $A/konkur_live.py --mock                      # تمرین: MOCK، بی‌کلید، واترمارک
python3 $A/konkur_run.py plan                         # پس از رونویسی: تعداد درخواست و سقف دلار
HOMODYNE_NO_FALLBACK=1 python3 $A/konkur_run.py run --limit 10   # پیش‌آزمون پولی
HOMODYNE_NO_FALLBACK=1 python3 $A/konkur_live.py --live          # اجرای کامل روی تابلو (یا konkur_run.py run)
python3 $A/konkur_run.py report                       # results/<run>/: report.md، summary.json، spoken-fa.txt
python3 $A/konkur_live.py --replay <run> --speed 20   # بازپخش برای ضبط، با برچسب ×۲۰
```

## چه اجرا شد و چه [RUN] است

- **اجرا شد (۲۷ نوامبر ۲۰۲۶، کلیدها unset):** `tools/llm.py selftest`؛ selftest هر چهار اسکریپت؛ یک اجرای کامل MOCK روی ۱۰۵ سؤال ساختگی × ۵ مدل؛ `report` روی آن (برچسب MOCK / SYNTHETIC)؛ تابلوی `--mock` و `--replay ×50` در Chrome بی‌سر در ۱۶۰۰×۹۰۰ (ردیف‌ها به‌روز می‌شوند، کارت‌های کارنامه می‌آیند)؛ `build-decks.py --only hmd-k01` و `voice-lint.py` بدون خطا.
- **[RUN]:** همهٔ عددهای مدل‌ها، تاریخ برش مدل‌ها (R10)، قیمت‌ها (R11)، مدت واقعی اجرا، شاخه‌های قاب ۸ تا ۱۱، ۱۴ و ۱۵.

## ریسک‌های باز

- **schema در مدل‌های باز:** برخی مدل‌های OpenRouter ممکن است `response_format` را نپذیرند؛ پیش‌آزمون نشان می‌دهد. راه: فقط برای همان slot در `models.json` بنویس `"no_schema": true` (پارس متن)؛ گزارش کنار نامش «(no schema)» می‌نویسد.
- **تصویر:** هر دو مدل باز باید تصویر بپذیرند (`models.json`، hint). پیش‌آزمون: سؤال شکل‌دار درست رسید؟
- **رونویسی:** خطای تایپ یک سؤال را بی‌جواب می‌کند؛ دو رونویسی + diff + ۲۵ نمونهٔ بازبینی مالک.
- **کلید نهایی:** فقط کلید اولیهٔ ۱۴۰۵ در خبر پیدا شد؛ پیش از نمره، کلید نهایی (با سؤال‌های حذف‌شده) لازم است.
- **مدت و هزینه:** چند صد سؤال × ۵ مدل (عدد دقیق را `plan` پس از رونویسی می‌دهد)؛ مدل‌های فکرکننده ممکن است ساعت‌ها طول بکشند. `plan` سقف دلار را پیش از y/N نشان می‌دهد؛ اجرا قابل ازسرگیری است.
- **رتبه:** شواهد عمومی خیلی کم است (sources.md)؛ کارت فقط بازه و همیشه «تخمین».

</div>
