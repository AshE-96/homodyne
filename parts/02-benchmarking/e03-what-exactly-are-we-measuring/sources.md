# HMD-006 · E03 · منابع

بازبینی: **۲۶ نوامبر ۲۰۲۶** (۵ آذر ۱۴۰۵) برای همهٔ منابع زیر، مستقیم از منبع اصلی (قبلی: ۲ و ۷ نوامبر ۲۰۲۶). نسخه‌های قبلی: `../_archive/v4-november-2026/e03-what-exactly-are-we-measuring/` و `../_archive/v2-september-2026/e03-what-exactly-are-we-measuring/`.

## منبع اصلی

### R01 · Why Language Models Hallucinate (OpenAI, سپتامبر ۲۰۲۵)
- **پیوند:** https://openai.com/index/why-language-models-hallucinate/ · مقاله: Kalai و همکاران، arXiv 2509.04664 (https://arxiv.org/abs/2509.04664)
- **استفاده:** قاب ۵ و ۶ — جدول SimpleQA: gpt-5-thinking-mini «نمی‌دانم» ۵۲٪، دقت ۲۲٪، خطا ۲۶٪؛ OpenAI o4-mini «نمی‌دانم» ۱٪، دقت ۲۴٪، خطا ۷۵٪. قاب ۶ — ایدهٔ «نمره‌دهی دودویی، حدس‌زدن را بهینه می‌کند» (بخش ۴٫۱ مقاله: «Under binary grading, abstaining is strictly sub-optimal»).
- **وضعیت تأیید:** ✔ ۷ نوامبر ۲۰۲۶ و دوباره ✔ ۲۶ نوامبر ۲۰۲۶ از خود صفحهٔ OpenAI (جدول با عنوان «from the GPT-5 System Card»؛ هر ستون جمعش ۱۰۰). این جدول فقط در وبلاگ است، نه در متن arXiv.
- **حساب خودمان (قاب ۶):** خطا ÷ جواب‌های داده‌شده = ۲۶/(۲۲+۲۶) ≈ ۵۴٪ و ۷۵/(۲۴+۷۵) ≈ ۷۶٪. با برچسب «حساب ما روی عددهای R01» نمایش داده می‌شود.
- **احتیاط:** «عددها دربارهٔ همان آزمون‌اند، نه رتبهٔ امروز».

## دادهٔ واقعی و رویدادهای مستند (تازه در v6.1)

### Vectara Hallucination Leaderboard (HHEM-2.3)
- **پیوند:** https://github.com/vectara/hallucination-leaderboard · README خام: https://raw.githubusercontent.com/vectara/hallucination-leaderboard/main/README.md · دریافت ۲۶ نوامبر ۲۰۲۶ · «Last updated on November 24, 2026» · ۱۱۷ مدل.
- **مجوز:** Apache License 2.0 (فایل LICENSE مخزن؛ API گیت‌هاب هم `apache-2.0`). داده با ذکر منبع آزاد است.
- **استفاده:** قاب ۹ — ردیف `openai/gpt-5-high-2025-08-07`: نرخ توهم **۱۵٫۱٪**، سازگاری ۸۴٫۹٪، نرخ پاسخ ۹۹٫۹٪. تگ قاب ۹ — `anthropic/claude-haiku-4-5-20251001`: ۹٫۸٪. بازهٔ جدول: کمترین ۱٫۸٪ (`antgroup/finix_s1_32b`)، بیشترین ۲۴٫۲٪ (`mistralai/ministral-3-3b-2512`).
- **تعریف (از README):** به هر مدل سند داده و گفته‌اند فقط با اطلاعات همان سند خلاصه کند؛ «hallucination rate (100 - accuracy)»؛ ستون Answer Rate سهم سندهایی است که مدل خلاصه کرده؛ ارزیابی نهایی فقط روی سندهایی است که همهٔ مدل‌ها خلاصه کرده‌اند.
- **قاب ۱۰ (از FAQ همان README):** پرسش «خلاصه‌سازی که فقط متن را کپی کند ۱۰۰٪ (صفر توهم) نمی‌گیرد؟» ← جواب «Absolutely»؛ و «we do not recommend using this as a standalone metric». در دک: نقل کوتاه انگلیسی (۹ واژه) + ترجمهٔ فارسی.
- **داده:** `artifact/derived/vectara_leaderboard_2026-11-24.csv` و `artifact/derived/same_model_two_definitions.csv` (`artifact/derived/SOURCE.txt`).
- **احتیاط:** جدول زنده است؛ روز ضبط دوباره ببین.

### R08 · AA-Omniscience (Artificial Analysis, نوامبر ۲۰۲۵)
- **پیوند:** https://arxiv.org/abs/2511.13029 (نسخهٔ HTML v1 خوانده شد، ۲۶ نوامبر ۲۰۲۶) · **مجوز مقاله:** CC BY 4.0 (صفحهٔ abs).
- **استفاده:**
  - قاب ۴ (فرمول سوم) و قاب ۹ — بخش ۲٫۴٫۳: hallucination rate = i/(p+i+a).
  - قاب ۹ — بخش ۳٫۱: «Grok 4 and GPT-5 (high) record the highest accuracy at 39%, their hallucination rates of 64% and 81%»؛ «Claude 4.5 Haiku … 16% accuracy but a 26% hallucination rate».
  - **قاب ۱ و ۸ (تازه)** — بخش ۲٫۴٫۱: «a model that abstains from every question would be given a score of 0, which would place it 4th out of the 36 models that were tested»؛ جریمهٔ هر غلط p = 1. بخش ۳٫۱: «only three frontier models at launch able to achieve an Omniscience Index score of above 0».
  - تصویرها: شکل ۱ (قاب ۸) و شکل ۷ (B-roll قاب ۹) — `media/CREDITS.md`.
- **«یک مدل» در قاب ۹ — مرز ادعا:** Vectara ردیف `gpt-5-high-2025-08-07` را دارد؛ AA نام «GPT-5 (high)» را چاپ کرده ولی تاریخ نسخه را نه. پس می‌گوییم «یه مدل، با یه اسم»، نه «دقیقاً همان نسخه». «high» در هر دو نام به سطح استدلال اشاره دارد.
- **احتیاط:** فقط برای مقایسهٔ فلسفهٔ سنجش، نه رتبهٔ زنده.

### Mata v. Avianca, Inc. (S.D.N.Y.، ۲۲ ژوئن ۲۰۲۳)
- **سند:** Opinion and Order on Sanctions، پروندهٔ 22-cv-1461 (PKC)، Document 54، قاضی P. Kevin Castel. نسخهٔ دریافت‌شده: https://www.nhd.uscourts.gov/sites/default/files/pdf/Mata-v-Avianca-sanctions-order.PDF (۲۶ نوامبر ۲۰۲۶؛ sha256 `4417953d…2025d`). نسخهٔ RECAP: https://storage.courtlistener.com/recap/gov.uscourts.nysd.575368/gov.uscourts.nysd.575368.54.0_8.pdf
- **مجوز:** سند دادگاه فدرال آمریکا، مالکیت عمومی.
- **استفاده (قاب ۲، ۱۱، ۱۲):** از متن رأی:
  - وکیل‌ها (LoDuca و Schwartz) و دفتر Levidow «submitted non-existent judicial opinions with fake quotes and citations created by the artificial intelligence tool ChatGPT» (ص ۱).
  - شش رأی ساختگی: Varghese، Shaboon، Petersen، Martinez، Durden، Miller (ص ۳۴، بند b).
  - پیوست B: پرسش «Is varghese a real case» و جواب «Yes, Varghese v. China Southern Airlines Co Ltd, 925 F.3d 1339 (11th Cir. 2019) is a real case.» (ص ۴۱)؛ بند ۴۵: ChatGPT گفته بود منابع «real» و در Westlaw و LexisNexis پیداشدنی‌اند.
  - «A penalty of $5,000 is jointly and severally imposed on Respondents» (ص ۳۴، بند d).
- **احتیاط:** زمان آن پرسش در رأی روشن نیست (بند ۴۶ و ۴۷: دو روایت متناقض Schwartz)؛ در متن نگفته‌ایم «قبل از» تحویل پرسید. پرونده مال ۲۰۲۳ و ChatGPT آن زمان است؛ دربارهٔ مدل‌های امروز چیزی نمی‌گوید (قاب ۱۲).

### AI Hallucination Cases Database (Damien Charlotin)
- **پیوند:** https://www.damiencharlotin.com/hallucinations/ · CSV: https://www.damiencharlotin.com/hallucinations/hallucinations/download.csv (۲۶ نوامبر ۲۰۲۶؛ sha256 `04555084…3abb`).
- **مجوز:** CC BY 4.0 (روی صفحه). اعتبار: «AI Hallucination Cases Database, Damien Charlotin».
- **استفاده (قاب ۱۱):** صفحه: «2338 cases identified so far»، «Last updated: 25 November 2026». CSV هم ۲۳۳۸ ردیف دارد؛ Mata v. Avianca ردیف `case_id = 1` است. نمودار فصلی دک = **شمارش ما** بر اساس تاریخ رأی (از ۶ پرونده در فصل دوم ۲۰۲۳ تا اوج ۴۶۳ در فصل اول ۲۰۲۶؛ فصل چهارم ۲۰۲۶ ناقص).
- **دامنه (به گفتهٔ خود سایت):** رأی‌هایی که دادگاه صریحاً یا ضمنی یافته طرفی به محتوای توهمی تکیه کرده؛ «does not track the (necessarily wider) universe of all fake citations or use of AI in court filings»؛ «work in progress».
- **احتیاط (همان درس قسمت):** این عدد صورت بدون مخرج است: نه نرخ خطای AI، نه نرخ استفاده. افت ۲۰۲۶ ممکن است فقط عقب‌ماندن ثبت باشد؛ دربارهٔ روند چیزی نمی‌گوییم جز «تند بالا رفته» (۲۰۲۳ تا اوایل ۲۰۲۶). ۱۳۳۸ ردیف «Pro Se Litigant» و ۹۲۲ ردیف «Lawyer» است (در متن گفته نمی‌شود).

## منابع پشتیبان

### R02 · Measuring what Matters (NeurIPS 2025 D&B)
- **پیوند:** https://arxiv.org/abs/2511.04703 (چکیده بازبینی شد، ۲۶ نوامبر ۲۰۲۶)
- **استفاده:** قاب ۱۰ — ۴۴۵ بنچمارک، ۲۹ داور متخصص، هشت توصیه؛ الگوهای تعریف پدیده و نمره‌دهی اعتبار ادعاها را سست می‌کنند (از چکیده).
- **احتیاط:** درصدهای داخلی مقاله (مثلاً ۴۷٫۸٪، ۵۳٫۴٪، ۱۶٪ در نسخهٔ v2) دوباره تأیید نشدند و در متن گفته نمی‌شوند.

### R09 · AbstentionBench (Kirichenko و همکاران، ژوئن ۲۰۲۵)
- **پیوند:** https://arxiv.org/abs/2506.09038 (چکیده بازبینی شد، ۲۶ نوامبر ۲۰۲۶)
- **استفاده:** قاب ۸ — ۲۰ مجموعه، ۲۰ مدل؛ «reasoning fine-tuning degrades abstention (by 24% on average)».
- **احتیاط:** یافتهٔ همان مطالعه، نه قانون همهٔ مدل‌ها.

## بررسی‌شده ولی استفاده‌نشده

- **Moffatt v. Air Canada** (BC Civil Resolution Tribunal، فوریهٔ ۲۰۲۴): مسئولیت شرکت برای جواب غلط چت‌بات. داستان خوبی است، ولی دربارهٔ «چه چیزی شمرده می‌شود» نیست و داستان دوم دادگاهی وقت قسمت را می‌گرفت. هیچ عددی از آن در متن نیست، پس جزئیاتش تأیید نشد.
- **«۱٫۸٪ در برابر ۸۱٪» (قلاب v2 و v6):** جای خودش را به «یک مدل، ۱۵٫۱٪ در برابر ۸۱٪» داد. دلیل: `scientific-corrections-fa.md` هشدار داده بود از دو درصد مدل‌های متفاوت «معما» نسازیم؛ حالا هر دو عدد برای یک مدل‌اند و تنها فرقشان کار و فرمول است، یعنی دقیقاً درس قسمت. ۱٫۸٪ فقط در کارت سازه به‌عنوان بازهٔ جدول مانده.
- **ادعای «بعضی جدول‌ها به‌جای تعریف‌نشده صفر می‌گذارند» (قاب ۸ و Short 1 نسخهٔ قبلی):** منبع مشخصی نداشت؛ حذف شد و جایش جملهٔ تأییدشدهٔ AA («چهارم از ۳۶») آمد.

## دادهٔ آموزشی و ابزار

- **ده کارت (۵/۲/۳)** و مدل‌های A/B: ILLUSTRATIVE؛ A و B همان دو مدل `tools/bluff-demo.csv`.
- **ابزار:** `tools/bluff_lab.py score tools/bluff-demo.csv --condition t75` → A: accuracy 0.5، coverage 0.7، risk ≈ 0.286، score −0.1؛ B: 0.4، 0.5، 0.2، +0.1 (اجرا ۲ نوامبر ۲۰۲۶).
- **دادهٔ واقعی:** `artifact/real_data.py` (stdlib، `--selftest` آفلاین) از دو دانلود بالا `artifact/derived/*` را می‌سازد؛ فرمان دقیق و sha256 در `artifact/derived/SOURCE.txt`.
- **کارت سازه:** `artifact/construct-card.md` (ردیف Vectara به ۲۴ نوامبر ۲۰۲۶ و ردیف «یک مدل، دو تعریف» به‌روز شد؛ نمونهٔ پرشدهٔ شارلوتن اضافه شد).
- **کنکور:** فقط تشبیه کیفی («کنکوری که نمرهٔ منفی نداشته باشد»)؛ هیچ عددی دربارهٔ کنکور گفته نمی‌شود.
