# HMD-007 · منابع

بازبینی: ۲ نوامبر ۲۰۲۶ (۱۱ آبان ۱۴۰۵).

## منبع اصلی (روی کارت قسمت)

### R33 · Mitigating the risk of prompt injections in browser use (Anthropic)
- **پیوند:** https://www.anthropic.com/research/prompt-injection-defenses · تاریخ انتشار: ۲۴ نوامبر ۲۰۲۵ (بازبینی ۲ نوامبر ۲۰۲۶)
- **محتوا:** تعریف تزریق دستور به‌عنوان دستورهای خصمانهٔ پنهان در محتوایی که مدل پردازش می‌کند؛ سه دفاع (آموزش با یادگیری تقویتی روی محتوای دارای تزریق، طبقه‌بندهای محتوای نامطمئن، red teaming)؛ نرخ موفقیت حمله با حمله‌کنندهٔ تطبیقی Best-of-N (۱۰۰ تلاش در هر محیط): مثلاً Opus 4.5 ۸٫۰٪ بدون محافظ، ۱٫۴٪ با محافظ‌های بهبودیافته.
- **استفاده:** قاب ۱۱ — ۱٫۴٪ برای Opus 4.5 با محافظ‌های بهبودیافته و جملهٔ «far from a solved problem»؛ هوک ۵.
- **احتیاط:** عددها مال آزمون‌های مرورگرِ همان شرکت، در همان تاریخ‌اند؛ با دموی ما قابل‌مقایسه نیستند. طبق `references.json`: «مقاومت کامل ادعا نشده». ✔ ۷ نوامبر ۲۰۲۶ تأیید شد: نمودار ۸٫۰٪ / ۷٫۶٪ / ۱٫۴٪؛ متن مقاله «A 1% attack success rate».

## چارچوب

### OWASP LLM01:2025 Prompt Injection
- **پیوند:** https://genai.owasp.org/llmrisk/llm01-prompt-injection/ (بازبینی ۲ نوامبر ۲۰۲۶)
- **استفاده:** قاب ۲ (مورد اول فهرست، تعریف مستقیم/غیرمستقیم)، قاب ۹ (حداقل دسترسی، تأیید انسانی)، قاب ۸ (جداسازی و برچسب‌گذاری محتوای نامطمئن).
- **جملهٔ تعریف:** «A Prompt Injection Vulnerability occurs when user prompts alter the LLM's behavior or output in unintended ways.»

## پژوهش‌های پشتیبان

### Hines و همکاران ۲۰۲۴ · Defending Against Indirect Prompt Injection Attacks With Spotlighting
- **پیوند:** https://arxiv.org/abs/2403.14720 (ثبت ۲۰ مارس ۲۰۲۴)
- **استفاده:** قاب ۸ — «از بیش از ۵۰٪ به کمتر از ۲٪» در آزمایش‌های خودشان روی مدل‌های خانوادهٔ GPT (از چکیده). روش datamarking دموی ما از این مقاله الهام گرفته، ولی پیاده‌سازی دقیق آن نیست.

### Greshake و همکاران ۲۰۲۳ · Not what you've signed up for
- **پیوند:** https://arxiv.org/abs/2302.12173 (پیش‌چاپ arXiv)
- **استفاده:** قاب ۴ — معرفی و بررسی تزریق غیرمستقیم در برنامه‌های مبتنی بر LLM.

## آزمایش خودمان

- **کد:** [`artifact/injection_lab.py`](artifact/injection_lab.py) — Python 3.10+، فقط کتابخانهٔ استاندارد، بدون هیچ import شبکه‌ای. **داده:** [`artifact/cases.json`](artifact/cases.json) — ۲۰ سند ساختگی (۱۲ حمله: ۷ با ابزار، ۵ فقط تغییر جواب؛ ۸ سالم)، فایل‌های ساختگی، نشانی‌های `.invalid`.
- **مدل‌های جایگزین (ILLUSTRATIVE):** `naive` (از هر خط دستورمانند اطاعت می‌کند) و `boundary` (درون نشانگرهای spotlight را نادیده می‌گیرد؛ پس spotlight روی آن «طبق ساخت» کار می‌کند). خروجی: [`artifact/results-illustrative-2026-11-02.md`](artifact/results-illustrative-2026-11-02.md) و [`artifact/trace-A01-illustrative-2026-11-02.txt`](artifact/trace-A01-illustrative-2026-11-02.txt). این عددها رفتار قاعده‌های خودمان‌اند، نه یافته دربارهٔ AI.
- **مدل واقعی:** هنوز اجرا نشده؛ برای ویدیوی پیگیری با [`artifact/adapter_template.py`](artifact/adapter_template.py). هیچ نرخی از پیش نوشته نشده.

## ایمنی

- هیچ هدف واقعی، محصول واقعی، حساب یا داده‌ای استفاده نشده. خط‌های حمله جمله‌های سادهٔ زبان طبیعی‌اند که فقط ابزارهای قلابی همین فایل را هدف می‌گیرند؛ هیچ ترفند پنهان‌سازی، کدگذاری یا دورزدن محصول خاصی در آن‌ها نیست.
