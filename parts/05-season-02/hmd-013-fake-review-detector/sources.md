<div dir="rtl">

# منابع · HMD-013 · AI in Production

تاریخ بازبینی: ۱۳ نوامبر ۲۰۲۶ (۲۲ آبان ۱۴۰۵). PDFها با `pdftotext` خوانده شدند؛ عددها از متن خودِ منبع، نه از خلاصه‌های ثانویه. صفحه‌هایی که به ابزار خودکار 403 دادند از نسخهٔ Internet Archive خوانده شدند و این در ستون بازبینی آمده است.

| شناسه | منبع | لینک | بازبینی | چه چیزی استفاده شد · کجا |
|---|---|---|---|---|
| R01 | Ott, Choi, Cardie, Hancock · *Finding Deceptive Opinion Spam by Any Stretch of the Imagination* · ACL-HLT 2011 · arXiv 1107.4557 | https://arxiv.org/abs/1107.4557 | ۱۳ نوامبر ۲۰۲۶، PDF کامل | ساخت داده: ۴۰۰ نظر فریبنده از Mechanical Turk (هر کارگر یک نظر؛ دستور: «برای بخش بازاریابی هتل، نظر قانع‌کننده بنویس»)، ۴۰۰ نظر پنج‌ستارهٔ TripAdvisor که «فرض» شده راست‌اند (پالایش‌شده، نه تأییدشده). جدول ۲: سه داور دانشجو روی ۱۶۰ نظر (fold 1، مثبت): درستی ۶۱٫۹٪، ۵۶٫۹٪، ۵۳٫۱٪؛ پوشش فریبندهٔ داور ۲ = ۱۸٫۸٪؛ «truth-bias». جدول ۳: BIGRAMS NB ۸۸٫۹٪، LIWC+BIGRAMS SVM ۸۹٫۸٪. بخش ۵: نظرهای راست جزئیات مکانی بیشتر دارند (small، bathroom، location)؛ نظرهای فریبنده «من» بیشتر و تمرکز بر چیزهای بیرون از هتل (husband، vacation). · قاب ۲، ۴، ۵، ۶، ۱۴ |
| R02 | Deceptive Opinion Spam Corpus v1.4 (Myle Ott) | https://myleott.com/op_spam_v1.4.zip · صفحهٔ توضیح: https://web.archive.org/web/20240228122920/https://myleott.com/op-spam.html | ۱۳ نوامبر ۲۰۲۶. صفحهٔ اصلی `op-spam.html` امروز 404 است؛ متن آن از نسخهٔ Wayback ۲۸ فوریهٔ ۲۰۲۴ خوانده شد. فایل zip از آدرس اصلی ناقص برگشت؛ نسخهٔ Wayback با SHA-256 `e3a61b37…6724fa` دانلود شد و فایل‌های `LICENSE` و `README.md` داخل آن خوانده شدند. | ۱٬۶۰۰ نظر، ۲۰ هتل شیکاگو، ۴۰۰ در هر دسته (مثبت/منفی × راست/فریبنده)؛ پوشه‌های fold1 تا fold5، هر کدام ۴ هتل (تقسیم به تفکیک هتل). **مجوز: Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported**؛ درخواست ارجاع به دو مقاله. داده در مخزن کامیت نمی‌شود؛ `artifact/fetch_data.py` آن را دانلود می‌کند. · همهٔ قاب‌های آزمایش |
| R03 | Ott, Cardie, Hancock · *Negative Deceptive Opinion Spam* · NAACL-HLT 2013, pp. 497–501 | https://aclanthology.org/N13-1053/ | ۱۳ نوامبر ۲۰۲۶ (صفحهٔ Anthology؛ PDF برای ابزار ما ناقص دانلود شد) | منشأ ۸۰۰ نظر منفی پیکره (راست: Expedia، Hotels.com، Orbitz، Priceline، TripAdvisor، Yelp؛ فریبنده: Mechanical Turk، طبق README پیکره). هیچ عددی از این مقاله نقل نشده. · قاب ۴ («بعدها نسخهٔ منفی») |
| R04 | Liang, Yuksekgonul, Mao, Wu, Zou · *GPT detectors are biased against non-native English writers* · Patterns 4(7), 100779, July 2023 · arXiv 2304.02819v3 | https://doi.org/10.1016/j.patter.2023.100779 · https://arxiv.org/abs/2304.02819 | ۱۳ نوامبر ۲۰۲۶ (متن arXiv v3؛ مشخصات انتشار از Crossref؛ صفحهٔ cell.com به ابزار 403 داد) | هفت آشکارساز پرکاربرد؛ ۹۱ انشای TOEFL (از یک انجمن آموزشی چینی) و ۸۸ انشای کلاس هشتم آمریکا (ASAP). روی انشاهای آمریکایی «near-perfect accuracy»؛ روی TOEFL میانگین مثبت کاذب ۶۱٫۲۲٪؛ ۱۸ از ۹۱ (۱۹٫۷۸٪) را هر هفت آشکارساز AI دانستند؛ ۸۹ از ۹۱ (۹۷٫۸۰٪) را دست‌کم یکی. توضیح: perplexity پایین‌تر (کلمه‌های ساده‌تر). بازنویسی با ChatGPT («Enhance the word choices…») مثبت کاذب را از ۶۱٫۲۲٪ به ۱۱٫۷۷٪ رساند. محدودیت خود مقاله: نمونهٔ کوچک، بیشتر آشکارسازها بر پایهٔ GPT-2. · قاب ۱۱، Short 2 |
| R05 | OpenAI · *New AI classifier for indicating AI-written text* · ۳۱ ژانویهٔ ۲۰۲۳؛ یادداشت بالای صفحه: از ۲۰ ژوئیهٔ ۲۰۲۳ «no longer available due to its low rate of accuracy» | https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/ · نسخهٔ خوانده‌شده: https://web.archive.org/web/20230802023548/https://openai.com/blog/new-ai-classifier-for-indicating-ai-written-text/ | ۱۳ نوامبر ۲۰۲۶ (صفحهٔ اصلی 403 به ابزار؛ Wayback ۲ اوت ۲۰۲۳) | روی «challenge set» انگلیسی: ۲۶٪ متن‌های AI را درست گرفت، ۹٪ متن آدم را AI خواند؛ «reliability typically improves as the length of the input text increases»؛ «very unreliable on short texts (below 1,000 characters)»؛ در زبان‌های دیگر به‌مراتب بدتر. فاصلهٔ ۳۱ ژانویه تا ۲۰ ژوئیه کمتر از شش ماه است. · قاب ۸، کارت تصمیم |
| R06 | Turnitin · Annie Chechitelli (Chief Product Officer) · *AI writing detection update from Turnitin's Chief Product Officer* · ۲۳ مه ۲۰۲۳ | https://www.turnitin.com/blog/ai-writing-detection-update-from-turnitins-chief-product-officer | ۱۳ نوامبر ۲۰۲۶ | حداقل متن از ۱۵۰ به ۳۰۰ کلمه: «our accuracy increases with a little more text»؛ مثبت کاذب بیشتر در «first few or last few sentences»؛ زیر ۲۰٪ AI، ستاره کنار درصد (کمتر قابل‌اعتماد). · قاب ۸ |
| R07 | Turnitin · Annie Chechitelli · *Understanding the false positive rate for sentences of our AI writing detection capability* · ۱۴ ژوئن ۲۰۲۳ | https://www.turnitin.com/blog/understanding-the-false-positive-rate-for-sentences-of-our-ai-writing-detection-capability | ۱۳ نوامبر ۲۰۲۶ | ادعای فروشنده: مثبت کاذب سند «less than 1%» برای اسنادی با ۲۰٪ یا بیشتر متن AI؛ مثبت کاذب سطح جمله «around 4%». ادعای خود فروشنده است، نه سنجش مستقل. · فقط در توضیحات و کامنت پین (در گفتار نیامده) |
| R08 | Tripadvisor · *Tripadvisor report reveals strong growth in review submissions and improvement in fraud detection rates* (Review Transparency Report) · ۱۱ آوریل ۲۰۲۳ | https://tripadvisor.mediaroom.com/2023-04-11-Tripadvisor-report-reveals-strong-growth-in-review-submissions-and-improvement-in-fraud-detection-rates | ۱۳ نوامبر ۲۰۲۶ | سال ۲۰۲۲: ۳۰٫۲ میلیون نظر ارسالی؛ ۴٫۴٪ «fake or fraudulent» (کمی بیش از ۱٫۳ میلیون)؛ ۷۲٪ پیش از انتشار گرفته شد. این نرخِ «تشخیص‌داده‌شده با سیستم خودشان» است، نه نرخ واقعی جعل. · قاب ۱۲، ۱۳ |

## محاسبه‌های خودمان (`artifact/review_lab.py`، اجرا ۱۳ نوامبر ۲۰۲۶، Python 3.11.7، stdlib، seed 13)

خروجی کامل: [`artifact/results/local-output.txt`](artifact/results/local-output.txt) و [`local-results.json`](artifact/results/local-results.json). همه روی هتل‌هایی که آشکارساز در آموزش ندیده (۵ بخش پیکره، هر بار ۴ هتل). «جعلی» = کلاس مثبت. بازهٔ ۹۵٪ Wilson در فایل خروجی.

- **قانون ساده** (I/me/my بیشتر از آستانه **یا** کمتر از حدود ۱٫۵ تا ۲٫۱ واژهٔ مکانی در هر ۱۰۰ واژه؛ آستانه‌ها روی ۱۶ هتل آموزشی): درستی ۶۹٫۴٪، دقت اتهام ۶۸٫۹٪، پوشش ۷۰٫۸٪، اتهام به نظر صادق ۳۲٫۰٪. روی همان ۱۶۰ نظر داورهای Ott (fold 1، مثبت): درستی ۷۱٫۲٪، اتهام ۲۵٫۰٪ (افزوده پس از بازبینی؛ اجرای دوباره ۱۳ نوامبر ۲۰۲۶، بقیهٔ عددها بی‌تغییر).
- **Naive Bayes** (واژه + جفت واژه، Laplace): درستی ۸۷٫۸٪، دقت اتهام ۸۴٫۳٪، پوشش ۹۲٫۹٪، اتهام به نظر صادق ۱۷٫۲٪. روی همان ۱۶۰ نظر داورهای Ott (fold 1، مثبت): درستی ۸۲٫۵٪، اتهام ۲۳٫۸٪. کنترل با sklearn 1.7.2 (LogisticRegression): درستی ۸۶٫۲٪، اتهام ۱۲٫۸٪.
- **طول متن** (مدل با نظر کامل آموزش دیده، فقط k جملهٔ اول را می‌بیند): اتهام به نظر صادق ۱ جمله ۳۸٫۶٪ · ۳ جمله ۲۵٫۴٪ · ۵ جمله ۲۱٫۲٪ · کل نظر ۱۷٫۲٪؛ درستی ۷۲٫۶ / ۸۱٫۰ / ۸۴٫۲ / ۸۷٫۸٪. روی ۵۸۴ نظرِ دست‌کم ده‌جمله‌ای: اتهام ۴۱٫۲٪ / ۲۸٫۸٪ / ۱۶٫۴٪ برای ۱ / ۳ / ۱۰ جمله.
- **حالت حذف خودکار** (آستانه روی امتیازهای خارج از بخش هتل‌های آموزشی، طوری که حداکثر ۱٪ نظر صادق علامت بخورد): کل نظر: اتهام ۰٫۹٪، پوشش ۳۵٫۴٪، دقت اتهام ۹۷٫۶٪؛ ۳ جمله: پوشش ۲۶٫۶٪.
- **دامنهٔ ندیده:** آموزش روی مثبت، آزمون روی منفی (هتل‌های ندیده): پوشش ۶۵٫۵٪ (در برابر ۹۴٫۵٪ روی مثبت)، درستی ۷۵٫۴٪. برعکس: پوشش ۷۳٫۸٪.
- **پیش‌بینی ده‌هزارتایی (حساب، نه اندازه‌گیری):** با ۴٫۴٪ جعلی (R08): حالت علامت، کل نظر ⇒ ۴۰۹ از ۴۴۰ جعلی گرفته، ۱٬۶۴۹ صادق علامت‌خورده، دقت اتهام ۱۹٫۹٪ («از هر پنج علامت، حدود چهار تا صادق»). حالت حذف، کل نظر ⇒ ۱۵۶ جعلی، ۸۴ صادق، دقت ۶۵٫۰٪. فرض: نرخ خطای پیکره در آن سایت هم برقرار است؛ که لزوماً نیست.
- **آزمونک ده‌نظره** (fold 1، مثبت، ۶۰ تا ۱۱۰ واژه، ۵ جعلی + ۵ صادق، seed 13): مدل ۷ از ۱۰؛ هر ۵ جعلی را گرفت، ۳ از ۵ صادق را متهم کرد. ده نمونه شاهد آماری نیست.
- `--selftest`: ۱۰ از ۱۰.

## بخش API (`artifact/ai_text_lab.py`) — اجرا نشده

طرح و دستورها در [`artifact/README.md`](artifact/README.md). خودآزمایی با مدل ساختگی (`HOMODYNE_MODEL=mock:echo`): ۱۶ از ۱۶. هیچ عددی از این بخش در متن، دک یا بستهٔ انتشار نیامده است.

## نقل‌قول‌های کوتاه روی صفحه

- R05: «very unreliable on short texts (below 1,000 characters)» (قاب ۸).
- R01، R04: فقط عدد، بدون نقل جمله.

## آنچه عمداً استفاده نشد

- عدد دقت هیچ آشکارساز تجاری امروز؛ ادعاهای R07 فقط به‌عنوان «ادعای فروشنده» در توضیحات.
- Li et al. 2014 (*Towards a General Rule for Identifying Deceptive Opinion Spam*، ACL، doi 10.3115/v1/P14-1147) برای مجموعهٔ انتقال: مجوز داده‌اش را نتوانستیم تأیید کنیم؛ به‌جایش انتقال مثبت ← منفی درون پیکرهٔ R02 و نویسندهٔ ماشینی (بخش API) آمد.
- نظرهای بی‌برچسب اینترنت: مرجع حقیقت نیستند و در هیچ عددی به کار نرفتند.

</div>
