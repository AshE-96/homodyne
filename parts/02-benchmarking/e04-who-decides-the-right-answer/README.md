# HMD-008 · Benchmark E04 · v7

## اگر جواب‌نامه غلط باشد، کدام AI می‌بازد؟

**وضعیت:** آمادهٔ ضبط (۲۶ نوامبر ۲۰۲۶). حالا داده و ماجرای واقعی دارد: سؤال واقعی MMLU با کلید غلط («بومی» به‌جای «همه‌گیری»)، شمارش خطا از دادهٔ عمومی MMLU-Redux (CC BY 4.0)، جابه‌جایی واقعی رتبه در ویروس‌شناسی (جدول ۲ Gema و همکاران)، ماجرای مستند SWE-bench Verified (OpenAI، ۲۰۲۴ و ۲۰۲۶) و دو عکس واقعی کنکور ۱۴۰۴ (مهر، CC BY 4.0). آزمایش K/P ساختگی فقط در قاب ۱، ۵ و ۶ مانده، چون سازوکار را تمیزتر نشان می‌دهد. شاخهٔ B: ممیزی پایلوت هنوز اجرا نشده.
**قالب:** Benchmark Lab · **زنجیره:** HMD-S04 (AI و پیش‌بینی طوفان) ← **HMD-008** → HMD-S05 (AI در المپیاد ریاضی)
**زمان:** حدود ۱۲:۳۰ (۱۲ تا ۱۴ دقیقه) · ۱۶۹۴ واژهٔ گفتاری · ۱۴ قاب · هوک: Shock/Contradiction

**جملهٔ مرکزی:** جواب‌نامهٔ غلط فقط از کسی نمره کم می‌کند که درست جواب داده؛ پس خطای کلید نویز بی‌طرف نیست و می‌تواند برنده را عوض کند، مگر اینکه کلید را با مخرج روشن ممیزی و با شاهد داوری کنیم.

**مرز ادعا:** آزمایش K/P ساختگی است. شمارش‌های MMLU-Redux کار ما روی دادهٔ منتشرشده‌اند (۱۰۰ سؤال تصادفی در هر موضوع). جابه‌جایی رتبه فقط در یک موضوع و با فاصله‌های چندسؤالی است و رتبه‌ها همان‌اند که مقاله گزارش کرده. نشان نمی‌دهیم رتبه‌بندی امروزِ مدل خاصی غلط است.

## فایل‌ها

| فایل | محتوا |
|---|---|
| [script-fa.md](script-fa.md) | متن ضبط v7 (۱۴ قاب، Pattern Interrupt Log، Retention Risk Map، کنترل پیش از ضبط) |
| [hooks-fa.md](hooks-fa.md) | پنج هوک ۳۰ ثانیه‌ای + توصیه |
| [package-fa.md](package-fa.md) | عنوان‌ها، تامبنیل، توضیحات، فصل‌ها، تگ، کامنت پین، end screen، دو Short، پست کامیونیتی |
| [`deck-fa.html`](deck-fa.html) · [`deck-en.html`](deck-en.html) | دک ضبط، فارسی راست‌به‌چپ و انگلیسی؛ کاور + ۱۴ قاب (→ ← · F · H · N). قاب ۲ عکس `media/` را نشان می‌دهد؛ پوشهٔ `media/` کنار دک بماند |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ هر دو دک؛ بعد از ویرایش `python3 scripts/build-decks.py --only hmd-008` |
| [sources.md](sources.md) | منابع با لینک، نقل عین متن، تاریخ بازبینی و محدودیت‌ها |
| [artifact/mmlu_redux_audit.py](artifact/mmlu_redux_audit.py) | **دادهٔ واقعی**: شمارش خطای MMLU-Redux، مخرج، سؤال‌های واقعی با کلید غلط (فقط stdlib؛ `--selftest`؛ `--build` با pyarrow) |
| [artifact/derived/](artifact/derived/SOURCE.txt) | `mmlu_redux_subject_counts.csv`، `mmlu_redux_wrong_key_items.json`، `mmlu_redux_raw_sha256.txt`؛ منبع، مجوز، sha256 و فرمان در `SOURCE.txt` |
| [artifact/key_audit_demo.py](artifact/key_audit_demo.py) · `key-v1.csv` · `key-v2.csv` | دموی **ساختگی** K/P (stdlib) و همان پاسخ‌ها در قالب `tools/bluff_lab.py` |
| [media/CREDITS.md](media/CREDITS.md) | دو عکس کنکور ۱۴۰۴ (مهر) و شکل ۱ مقاله، با مجوز و متن اعتبار؛ فهرست «دانلود نشد» |
| [artifact/handoff-v3.md](artifact/handoff-v3.md) | پیوند به پیش‌نیازهای اجرای واقعی Bluff (دست‌نخورده) |

دادهٔ خام (۲٫۸ مگابایت) در `artifact/data/` است و در git نمی‌رود (`artifact/.gitignore`).

## اجرا (از ریشهٔ مخزن)

```bash
python3 parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/mmlu_redux_audit.py --selftest
python3 parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/mmlu_redux_audit.py
python3 parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/key_audit_demo.py
python3 tools/bluff_lab.py score parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/key-v2.csv --condition plain
```

خروجی مورد انتظار — واقعی: 370/5700 = 6.49٪؛ ویروس‌شناسی 57/100 (Wilson ۴۷٪–۶۶٪)، 33 کلید غلط، 27 از «Human Virology 5e»؛ پنج موضوع بدتر 145/500 = 29٪؛ 32 «expert». ساختگی: K 73 / P 80 با کلید v1؛ K 80 / P 76 با کلید v2؛ typo: K 73 / P 74.

بازسازی دادهٔ مشتق از خام (فقط اگر `artifact/data/` را دوباره دانلود کردی؛ نشانی‌ها در `SOURCE.txt`):
`python3 -I parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/mmlu_redux_audit.py --build parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/data/mmlu-redux-2.0`

## موقع ضبط چه بگیری

- **ترمینال قاب ۶:** `key_audit_demo.py` (لحظهٔ `leader=K`) و `bluff_lab.py score … key-v2.csv`.
- **ترمینال قاب ۹ (و اختیاری قاب ۳):** `mmlu_redux_audit.py`، بخش ۳ (و بخش ۲)؛ بخش ۴ سه سؤال واقعی با کلید غلط را هم نشان می‌دهد.
- **مرورگر (اختیاری، خودت ضبط کن):** کارت دادهٔ MMLU-Redux در Hugging Face با Dataset Viewer روی `virology`؛ دو پست OpenAI دربارهٔ SWE-bench Verified؛ labelerrors.com. جزئیات در `media/CREDITS.md`.

## باید پیش از ضبط حل شود

| برچسب | مورد | کجا | اقدام |
|---|---|---|---|
| ✔ | ممیزی پایلوت ۶۰ پرسشی Bluff | قاب ۱۱ | شاخهٔ B: «هنوز اجرا نشده»؛ نتیجهٔ واقعی جدا منتشر می‌شود. |
| ✔ | روند کلید اولیه ← اعتراض ← کلید نهایی | قاب ۲ و ۱۰ | با منبع رسمی‌تر تطبیق شد (۷ نوامبر ۲۰۲۶)؛ هیچ عدد کنکوری گفته نمی‌شود. |
| ✔ | عددهای واقعی | قاب ۱، ۳، ۷–۱۱ | همه با منبع اصلی و دادهٔ خام تطبیق شد (۲۶ نوامبر ۲۰۲۶). |
| — | منابع تازه شناسهٔ R ندارند | sources.md | پیشنهاد R37 تا R41 در references.json. |
| — | `make teleprompter` | recording/ | برگهٔ ضبط و تله‌پرامپتر هنوز نسخهٔ قبلی‌اند؛ باید دوباره ساخته شوند. |
