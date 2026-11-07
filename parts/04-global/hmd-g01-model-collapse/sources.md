# HMD-G01 · منابع

بازبینی: ۳ نوامبر ۲۰۲۶ (۱۲ آبان ۱۴۰۵). هر عدد ویدیو یا از اجرای خودمان است، یا از منبع زیر با شناسه.

## منبع اصلی

### R-G01 · AI models collapse when trained on recursively generated data
- **پیوند:** https://www.nature.com/articles/s41586-024-07566-y · پیش‌انتشار: https://arxiv.org/abs/2305.17493 (*The Curse of Recursion*، نسخهٔ ۳، آوریل ۲۰۲۴؛ چکیده بازبینی شد ۳ نوامبر ۲۰۲۶)
- **نویسندگان:** Ilia Shumailov, Zakhar Shumaylov, Yiren Zhao, Nicolas Papernot, Ross Anderson, Yarin Gal · *Nature* 631, 755–759، ژوئیهٔ ۲۰۲۴
- **استفاده در ویدیو:**
  - قاب ۵: نام پدیده (model collapse).
  - «دنباله‌های توزیع ناپدید می‌شوند» (از چکیدهٔ پیش‌انتشار: *tails of the original content distribution disappear*).
  - دو مرحلهٔ زودهنگام و دیرهنگام.
  - آزمایش روی Gaussian mixture، VAE و یک مدل زبانی.
- **✔ (۷ نوامبر ۲۰۲۶، نسخهٔ [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11269175/)):** مدل زبانی «OPT-125m» روی wikitext2؛ حالت «ده epoch، ۱۰٪ دادهٔ اصلی نگه داشته شد» به «تنها افت جزئی» رسید؛ سه خانوادهٔ مدل: LLM، VAE و GMM. پیش از نقل مستقیم روی صفحه، جمله را با PDF یکی کن.

## منابع پشتیبان

### R-G02 · Is Model Collapse Inevitable? Breaking the Curse of Recursion by Accumulating Real and Synthetic Data
- **پیوند:** https://arxiv.org/abs/2404.01413 (v2، ۲۹ آوریل ۲۰۲۴؛ چکیده بازبینی شد)
- **نویسندگان:** Gerstgrasser, Schaeffer, Dey, Rafailov, … Donoho, Koyejo (Stanford و دیگران)
- **استفاده در ویدیو:** قاب ۹. جایگزینی داده به فروریزی می‌رسد. انباشت دادهٔ واقعی و مصنوعی از آن جلوگیری می‌کند، و در مدل خطی خطا کران بالای محدود دارد. آزمایش accumulate در فایل همراه از همین ایده آمده است.

### R-G03 · Will we run out of data? Limits of LLM scaling based on human-generated data
- **پیوند:** https://epoch.ai/blog/will-we-run-out-of-data-limits-of-llm-scaling-based-on-human-generated-data · arXiv 2211.04325
- **نویسندگان:** Villalobos, Ho, Sevilla, Besiroglu, Heim, Hobbhahn (Epoch AI) · ۶ ژوئن ۲۰۲۴
- **استفاده در ویدیو:** قاب ۴.
  - حدود ۳۰۰ تریلیون توکن (بازهٔ ۹۰٪: ۱۰۰ تا ۱۰۰۰ تریلیون).
  - مصرف کامل بین ۲۰۲۶ و ۲۰۳۲ (بازهٔ ۸۰٪)، «اگر روند فعلی ادامه یابد».
- **احتیاط:** فقط متن عمومی است و تصویر، ویدیو و دادهٔ خصوصی را شامل نمی‌شود. با overtraining زودتر می‌رسد. نسخهٔ تازه‌تری از Epoch پیدا نشد.

### R-G04 · Graphite: سهم مقاله‌های ماشینی در وب
- **گزارش ۲۰۲۵:** https://graphite.io/five-percent/more-articles-are-now-created-by-ai-than-humans (۱۴ اکتبر ۲۰۲۵)
  - ۴۳ هزار URL از Common Crawl.
  - آشکارساز Surfer، با مثبت کاذب ۴٫۲٪.
  - عبور از انسان در نوامبر ۲۰۲۴ و ثابت‌ماندن از مه ۲۰۲۴.
  - خود صفحه می‌گوید با گزارش تازه جایگزین شده است.
- **گزارش تازه (داده تا Q1 2026، میانگین سه آشکارساز Pangram، GPTZero و Copyleaks):** به نقل [Axios، ۱۵ مه ۲۰۲۶](https://axios.com/2026/05/15/human-vs-ai-written-articles).
  - حدود ۳۶٪ یک سال پس از ChatGPT.
  - حدود ۴۸٪ پس از دو سال.
  - از آن پس نزدیک ۵۰٪.
- **مطالعهٔ جدا (اکتبر ۲۰۲۵):** [Graphite، AI Content in Search and LLMs](https://graphite.io/research/ai-content-in-search-and-llms)؛ خبر آن: [Axios، ۱۴ اکتبر ۲۰۲۵](https://www.axios.com/2025/10/14/ai-generated-writing-humans).
  - حدود ۸۶٪ مقاله‌های رتبه‌دار در گوگل را آدم‌ها نوشته‌اند.
  - حدود ۸۲٪ مقاله‌های ارجاع‌شده در ChatGPT و Perplexity را آدم‌ها نوشته‌اند.
- **✔ (۷ نوامبر ۲۰۲۶):** گزارش تازه: [Graphite، «AI Now Writes as Many Online Articles as Humans»، ۱۵ مه ۲۰۲۶](https://graphite.io/research/ai-now-writes-as-many-online-articles-as-humans-do)؛ ۵۵٫۴ هزار URL از Common Crawl، میانگین سه آشکارساز. «۳۵٫۹٪» پس از ۱۲ ماه، «۴۸٪» پس از ۲۴ ماه، نزدیک ۵۰٪ از Q1 2025 (۵۰٫۹٪ در Q4 2025، ۴۹٫۹٪ در Q1 2026). **اصلاح:** عددهای ۸۶٪ (گوگل) و ۸۲٪ (ChatGPT/Perplexity) از مطالعهٔ جدای [Graphite، «AI Content in Search and LLMs»، ۱۴ اکتبر ۲۰۲۵](https://graphite.io/research/ai-content-in-search-and-llms) با آشکارساز Surfer‌اند و خبر Axios آن [۲۰۲۵](https://www.axios.com/2025/10/14/ai-generated-writing-humans) است، نه ۲۰۲۶. در ویدیو فقط «حدود نصف» و «حدود یک‌سوم» گفته می‌شود.

### R-G06 · How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits
- **پیوند:** https://arxiv.org/abs/1905.09749 · Gidney و Ekerå، ۲۰۱۹ (Quantum، ۲۰۲۱)
- **استفاده در ویدیو:** قاب ۱۴ (تیزر قسمت بعد): «سال ۲۰۱۹ حدود بیست میلیون کیوبیت». جملهٔ «حالا برآوردها خیلی پایین‌تر اومدن» به Gidney، [arXiv 2505.15917](https://arxiv.org/abs/2505.15917) (۲۰۲۵، کمتر از یک میلیون کیوبیت) تکیه دارد و عددی از آن گفته نمی‌شود. مرجع: `channel/season-01/idea-bank-global-fa.md`.

### R-G05 · Low-background steel
- **پیوند:** https://en.wikipedia.org/wiki/Low-background_steel
- **استفاده در ویدیو:** قاب ۱۱، به‌عنوان تشبیه. فولاد ساخته‌شده پیش از آزمایش‌های هسته‌ای (پیش از ۱۹۴۵)، که بخشی از آن از کشتی‌های غرق‌شده بازیابی شد، در آشکارسازهای حساس تابش به کار رفته است. این تشبیه در بحث‌های عمومی دادهٔ پیش از ۲۰۲۲ رایج است و در ویدیو به «بعضی‌ها می‌گن» نسبت داده می‌شود، نه به یک پژوهش.

## اجرای خودمان (اصلی‌ترین شاهد شبیه‌سازی)

- **فایل نتیجه:** [`artifact/results-seed2026.md`](artifact/results-seed2026.md) · داده‌های کامل: [`artifact/results-seed2026.json`](artifact/results-seed2026.json)
- **اسکریپت:** [`artifact/collapse_lab.py`](artifact/collapse_lab.py). فقط کتابخانهٔ استاندارد Python. seed 2026، اجرا ۳ نوامبر ۲۰۲۶، حدود ۹۰ ثانیه.
- **آزمایش ۱:** Gaussian، ۱۰۰ نمونه در هر نسل، ۲۰۰ اجرا، ۱۰۰۰ نسل، سه رژیم replace / keep10 / accumulate.
- **آزمایش ۲:** پیکرهٔ Zipf ساختگی، ۵۰۰۰ واژهٔ ممکن، ۲۰٬۰۰۰ توکن (۳۱۷۲ واژهٔ متمایز)، ۲۰ اجرا، ۱۰۰ نسل.
- **کنترل:** `--quick --seed 7` همان الگو را داد: پهنای نسل ۱۰۰ برابر ۰٫۳۷، واژه‌های نسل ۱۰۰ برابر ۲۲۸.
- **عددهای استفاده‌شده در متن:**
  - پهنا: ۱ ← ۰٫۶۰ (نسل ۵۰) ← ۰٫۳۷ (نسل ۱۰۰) ← ۰ (نسل ۱۰۰۰).
  - دنباله: ۴٫۷۱٪ ← ۰٫۳۷٪ ← ۰٪.
  - accumulate حدود ۰٫۹۸۵ و keep10 حدود ۰٫۹۳.
  - واژه‌ها: ۳۱۷۲ ← ۲۵۵۰ ← ۱۰۷۶ ← ۲۲۰؛ نیمهٔ نادر ۱۵۸۶ ← ۳۶.
  - keep10 روی ۱۷۷۴ واژه و ۵۷۳ واژهٔ نادر.

## پیوند به ژنتیک جمعیت

- مدل Wright–Fisher (نمونه‌گیری دوجمله‌ای یا چندجمله‌ای هر نسل از فراوانی‌های نسل قبل) همان سازوکار آزمایش ۲ است: واژه‌ای که شمارش‌اش صفر شد، جذب می‌شود و برنمی‌گردد. منبع درسی عمومی، مثلاً Hartl و Clark، *Principles of Population Genetics*. در ویدیو فقط شباهت ریاضی گفته می‌شود.

## منابعی که عمداً استفاده نشدند

- ادعاهای «مدل X فروریخته است» در شبکه‌های اجتماعی: بدون شاهد منتشرشده.
- آمار سهم دادهٔ مصنوعی در آموزش مدل‌های تجاری: منبع رسمی و مقایسه‌پذیر پیدا نشد.
