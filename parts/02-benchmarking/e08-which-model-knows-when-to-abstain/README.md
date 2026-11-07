# HMD-016 · Benchmark E08 · v5

## کدام AI به‌موقع می‌گوید «نمی‌دانم»؟ نتیجهٔ آزمون ما

**وضعیت:** recordable except the result beats [RUN]; the result beats wait for the Bluff data lock. — قاب ۱ تا ۱۰ و ۱۳ تا ۱۵ همین حالا قابل ضبط‌اند (عددهای قاب ۶ تا ۱۰ ILLUSTRATIVE از `artifact/abstain_report.py --demo`). قاب ۱۱ و ۱۲ [RUN] با شاخه‌های آماده، فقط پس از قفل دادهٔ Bluff ضبط می‌شوند. ویدیو پیش از آن منتشر نمی‌شود. منبع‌ها ۷ نوامبر ۲۰۲۶ بازبینی شدند.
**قالب:** Benchmark Lab · **زنجیره:** HMD-015 (جواب داخل فایل است؛ چرا AI باز هم اشتباه می‌کند؟) ← **HMD-016** → HMD-017 (یوتیوب چرا این ویدیو را به تو پیشنهاد داد؟)
**زمان:** حدود ۱۴:۳۰ · ۱۵ قاب · واژهٔ گفتاری ۱۷۰۷ با همهٔ شاخه‌ها (حدود ۱۶۰۰ با یک شاخه) · هوک: Story-Open «کتاب سوم»

**جملهٔ مرکزی:** «به‌موقع نمی‌دانم گفتن» یعنی پوشش و ریسک را با هم ببینی، با قانونی که هزینهٔ اشتباه را نشان دهد؛ و مقایسهٔ مدل‌ها فقط وقتی «یافته» است که داده پیش از تحلیل قفل و مقایسه پیش از دیدن نتیجه ثبت شده باشد.

**مرز ادعا:** نتیجه فقط دربارهٔ همین سؤال‌های کوتاه، نسخه‌ها و تاریخ است؛ خروجی را می‌سنجیم نه «دانستن» درونی؛ عدم تشخیص تفاوت یعنی برابری نیست؛ هش تغییرنکردن فایل را ثابت می‌کند، نه درستی داوری.

## فایل‌ها

| فایل | محتوا |
|---|---|
| [script-fa.md](script-fa.md) | متن ضبط v5 (۱۵ قاب؛ قاب ۱۱ و ۱۲ [RUN] با سه شاخه) |
| [hooks-fa.md](hooks-fa.md) | پنج هوک + توصیه (Story-Open)؛ هیچ هوکی نتیجه نمی‌گوید |
| [package-fa.md](package-fa.md) | بستهٔ انتشار کامل + English metadata؛ موارد وابسته به نتیجه «پس از قفل داده» |
| [deck.html](deck.html) | دک ضبط v5 (۱۵ section؛ beat-11 و beat-12 کارت `[RUN] · NOT RUN YET`) |
| [sources.md](sources.md) | منابع با تاریخ بازبینی، محاسبه‌ها، خروجی کامل دمو |
| [artifact/abstain_report.py](artifact/abstain_report.py) | گزارش پوشش/ریسک/خودداری/امتیاز، نگهبان سؤال‌های بی‌جواب، اختلاف جفتی تأییدی با بازهٔ بوت‌استرپ خوشه‌ای، مقایسه‌های اکتشافی، هش قفل داده و طرح (stdlib؛ امتیازدهی از `tools/bluff_lab.py`) |
| [artifact/abstain-demo-ILLUSTRATIVE.csv](artifact/abstain-demo-ILLUSTRATIVE.csv) | دادهٔ آموزشی تولیدشده با `--demo` (سه مدل خیالی؛ sha256 `a39e3469…`) |
| [artifact/handoff-v3.md](artifact/handoff-v3.md) | پیوند به پیش‌نیازهای اجرای واقعی (از نسخهٔ قبل، دست‌نخورده؛ پیوندهای `examples/` در این مخزن نیستند) |

## اجرا (از ریشهٔ مخزن)

```bash
python3 parts/02-benchmarking/e08-which-model-knows-when-to-abstain/artifact/abstain_report.py --selftest
python3 parts/02-benchmarking/e08-which-model-knows-when-to-abstain/artifact/abstain_report.py --demo        # عددهای قاب ۶ تا ۱۰
# پس از قفل داده [RUN]:
python3 parts/02-benchmarking/e08-which-model-knows-when-to-abstain/artifact/abstain_report.py locked.csv --plan plan.json
```

`plan.json` همان کلیدهای `DEMO_PLAN` را دارد: `primary_condition`، `confirmatory_pair`، `practical_delta_points_per_prompt`، `max_fabrication_design_choice`.

## باید پیش از ضبط حل شود

| برچسب | مورد | کجا | اقدام |
|---|---|---|---|
| [RUN] | قفل دادهٔ Bluff: پاسخ‌ها، داوری نهایی، manifest اجرای مورد انتظار، طرح تحلیل ثبت‌شده و هش‌ها | قاب ۱۱ و ۱۲، دک beat-11/12، بخش‌های «پس از قفل داده» در `package-fa.md` | پس از قفل: `abstain_report.py locked.csv --plan plan.json`؛ پر کردن کروشه‌ها؛ نگه داشتن فقط یک شاخه در هر قاب؛ به‌روز کردن دک. |
| ✔ | عددهای آموزشی قاب ۶ تا ۱۰ | قاب ۶–۱۰، دک | ۷ نوامبر ۲۰۲۶ با خروجی `--demo` و با `bluff_lab.py compare` تطبیق داده شد. |
| ✔ | یافته‌های AbstentionBench (۲۰/۲۰/۲۴٪) | قاب ۳ | ۷ نوامبر ۲۰۲۶ با arXiv v1 تطبیق شد؛ «۲۴٪» فقط با قید «طبق چکیده، در اون مطالعه». |
