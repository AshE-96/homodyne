# HMD-008 · Benchmark E04 · v5

## اگر جواب‌نامه غلط باشد، کدام AI می‌بازد؟

**وضعیت:** متن، دک و بستهٔ انتشار آمادهٔ تمرین. شاخهٔ B انتخاب شد (پایلوت هنوز اجرا نشده). منبع‌ها ۷ نوامبر ۲۰۲۶ بازبینی شدند.
**قالب:** Benchmark Lab · **زنجیره:** HMD-007 (prompt injection) ← **HMD-008** → HMD-009 (گوگل‌مپس)
**زمان:** حدود ۱۴ تا ۱۵ دقیقه · ۱۷۴۰ واژهٔ گفتاری · ۱۴ قاب · هوک: Shock/Contradiction

**جملهٔ مرکزی:** جواب‌نامهٔ غلط فقط از کسی نمره کم می‌کند که درست جواب داده؛ پس خطای کلید نویز بی‌طرف نیست و می‌تواند برنده را عوض کند، مگر اینکه کلید را با مخرج روشن ممیزی و با شاهد داوری کنیم.

**مرز ادعا:** آزمایش ما ILLUSTRATIVE است (مدل‌های خیالی، خطای کاشته‌شده)؛ نشان نمی‌دهد رتبه‌بندی واقعیِ یک مدل خاص غلط است یا یک بنچمارک مشخص امروز چند درصد خطا دارد. نداشتن منبع در جست‌وجو به معنای نبودِ جواب نیست.

## فایل‌ها

| فایل | محتوا |
|---|---|
| [script-fa.md](script-fa.md) | متن ضبط v5 (۱۴ قاب، Pattern Interrupt Log، Retention Risk Map، کنترل پیش از ضبط) |
| [hooks-fa.md](hooks-fa.md) | پنج هوک ۳۰ ثانیه‌ای + توصیه |
| [package-fa.md](package-fa.md) | عنوان‌ها، تامبنیل A/B/C، توضیحات، فصل‌ها، تگ، کامنت پین، end screen، دو Short، پست کامیونیتی |
| [deck.html](deck.html) | دک ضبط v5 (۱۴ section، `data-start` هم‌زمان با متن) |
| [sources.md](sources.md) | منابع با شناسه، لینک و تاریخ بازبینی |
| [artifact/key_audit_demo.py](artifact/key_audit_demo.py) | دموی قابل اجرا (stdlib)؛ ILLUSTRATIVE |
| `artifact/key-v1.csv`، `artifact/key-v2.csv` | همان پاسخ‌ها در قالب `tools/bluff_lab.py` |
| [artifact/handoff-v3.md](artifact/handoff-v3.md) | پیوند به پیش‌نیازهای اجرای واقعی Bluff (از نسخهٔ قبل، دست‌نخورده) |

نسخهٔ قبلی: `../_archive/v4-november-2026/e04-who-decides-the-right-answer/` و `../_archive/v3-before-plain-language/…`.

## اجرا (از ریشهٔ مخزن)

```bash
python3 parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/key_audit_demo.py --write-csv
python3 tools/bluff_lab.py score parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/key-v1.csv --condition plain
python3 tools/bluff_lab.py score parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/key-v2.csv --condition plain
```

خروجی مورد انتظار: K 73 / P 80 با کلید v1؛ K 80 / P 76 با کلید v2؛ typo: K 73 / P 74؛ ممیزی مشکوک‌ها 8/36 = 22٪؛ ممیزی تصادفی 3/30 (Wilson 95٪: ۳٪ تا ۲۶٪)؛ توافق داوران 11/12.

## باید پیش از ضبط حل شود

| برچسب | مورد | کجا | اقدام |
|---|---|---|---|
| ✔ | ممیزی پایلوت ۶۰ پرسشی Bluff | قاب ۱۱، دک beat-11 | شاخهٔ B (۷ نوامبر ۲۰۲۶): «هنوز اجرا نشده»؛ نتیجهٔ واقعی جدا منتشر می‌شود. |
| ✔ | روند «کلید اولیه ← اعتراض ← کلید نهایی (اصلاح یا حذف سؤال)» در کنکور سراسری | قاب ۲ و ۱۰ | با اطلاعیهٔ رسمی sanjesh.org تطبیق؛ فعلاً فقط منبع ثانویه. هیچ تاریخ/عددی از کنکور گفته نمی‌شود. | (تأیید ۷ نوامبر ۲۰۲۶)
| — | منابع MMLU-Redux و Northcutt شناسهٔ R ندارند | sources.md | پیشنهاد افزودن به references.json به‌عنوان R37 و R38. |
| — | تامبنیل و تصویر پاسخ‌برگ | package-fa.md | بازسازی‌شده، بدون لوگو یا سند واقعی. |
