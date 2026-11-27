<div dir="rtl">

# اعتبار تصاویر · HMD-006

سه تصویر `beat02_*` از **یک سند دادگاه فدرال آمریکا** برداشته شده‌اند. متن رأی (صفحهٔ ۱) اثر دادگاه فدرال و مالکیت عمومی است؛ پیوست‌های A و B **محتوای شخص ثالث‌اند** که به‌عنوان ضمیمه در پروندهٔ عمومی دادگاه آمده‌اند (اثر دولت آمریکا نیستند)، پس اعتبارشان «ضمیمه در پروندهٔ عمومی» است، نه «مالکیت عمومی». دو تصویر `beat08_*` و `beat09_*` شکل‌های مقالهٔ AA-Omniscience با مجوز **CC BY 4.0** هستند و **ذکر نام الزامی است**. متن اعتبار را هم روی تصویر (زیرنویس کوچک؛ در دک هست) و هم در توضیحات ویدیو بیاور. تاریخ دریافت همه: ۲۶ نوامبر ۲۰۲۶.

**سند:** *Mata v. Avianca, Inc.*، پروندهٔ 22-cv-1461 (PKC)، دادگاه فدرال ناحیهٔ جنوبی نیویورک، **Opinion and Order on Sanctions**، قاضی P. Kevin Castel، ۲۲ ژوئن ۲۰۲۳، Document 54 (۴۳ صفحه).
**نسخهٔ دریافت‌شده:** https://www.nhd.uscourts.gov/sites/default/files/pdf/Mata-v-Avianca-sanctions-order.PDF (سایت یک دادگاه فدرال آمریکا) · sha256 `4417953d96b89502678ad95c2a8af7c1d1e0b66b8030408aec2c95ee1c2b025d` · نسخهٔ خام در `artifact/data/mata-v-avianca-doc54/` (git-ignored).
**ساخت تصویرهای شکل AA:** `magick <png> -background white -alpha remove -resize 1600x -quality 88` (پهن و کوتاه‌اند؛ ۱۶۰۰ پیکسل تا متن نمودار خوانا بماند). محتوا دست نخورده.
**ساخت تصویرهای دادگاه:** `pdftoppm -r 150 -png` روی صفحه‌های ۱، ۳۶ و ۴۱؛ صفحهٔ ۴۱ با `magick -rotate -90` صاف شد؛ بعد `magick -resize 1280x (یا x1280) -quality 85`. صفحهٔ ۱ فقط تا ارتفاع ۹۰۰ پیکسل برش خورد. هیچ چیز دیگری عوض نشد.

| فایل | قاب | چیست | منبع | مجوز | متن اعتبار |
|---|---|---|---|---|---|
| `beat02_mata_chatgpt_appendixB_court-exhibit.jpg` (۱۲۸۰×۹۸۹) | ۲ (در دک) | پیوست B رأی: اسکرین‌شات گوشی وکیل از ChatGPT؛ «Is varghese a real case» ← «Yes, … is a real case.» | صفحهٔ ۴۱ از ۴۳ همان سند | ضمیمه در پروندهٔ عمومی دادگاه؛ محتوای شخص ثالث (اسکرین‌شات وکیل از خروجی ChatGPT)، نه اثر دولت آمریکا؛ استفادهٔ مستند و آموزشی | `Mata v. Avianca, 22-cv-1461 (S.D.N.Y.), Opinion and Order on Sanctions, 22 June 2023, Appendix B (exhibit in the public court record)` |
| `beat02_mata_fake_opinion_appendixA_court-exhibit.jpg` (۹۸۹×۱۲۸۰) | ۲ (B-roll) | پیوست A: رأی ساختگی «Varghese v. China Southern Airlines» با مهر «DO NOT CITE OR QUOTE AS LEGAL AUTHORITY» | صفحهٔ ۳۶ از ۴۳ همان سند | ضمیمه در پروندهٔ عمومی دادگاه؛ محتوای شخص ثالث (متنی که وکیل‌ها تحویل دادند)، نه اثر دولت آمریکا | `Mata v. Avianca, 22-cv-1461 (S.D.N.Y.), Opinion and Order on Sanctions, 22 June 2023, Appendix A (exhibit in the public court record)` |
| `beat02_mata_order_page1_PD.jpg` (۱۲۸۰×۹۰۴) | ۲ (B-roll) | صفحهٔ اول رأی: «OPINION AND ORDER ON SANCTIONS» و بند اول قاضی دربارهٔ ChatGPT | صفحهٔ ۱ از ۴۳ همان سند | مالکیت عمومی | `Mata v. Avianca, 22-cv-1461 (S.D.N.Y.), 22 June 2023 · public domain` |
| `beat08_aa_omniscience_index_fig1_CC-BY-4.0.jpg` (۱۶۰۰×۵۴۳) | ۸ (در دک) | شکل ۱ مقاله: Omniscience Index مدل‌ها؛ خط‌چین صفر = دستیار همیشه ساکت؛ فقط سه ستون بالای صفر | [arXiv 2511.13029 v1، شکل ۱](https://arxiv.org/html/2511.13029v1) · فایل: `https://arxiv.org/html/2511.13029v1/resources/Artificial_Analysis_Omniscience_Index.png` (sha256 `fd5ac0bb…a750f`) | CC BY 4.0 (صفحهٔ abs مقاله) | `Figure: Artificial Analysis, AA-Omniscience (arXiv 2511.13029), CC BY 4.0` |
| `beat09_aa_hallucination_rate_fig7_CC-BY-4.0.jpg` (۱۶۰۰×۴۶۷) | ۹ (B-roll) | شکل ۷ مقاله: نرخ توهم مدل‌ها در AA-Omniscience؛ ستون GPT-5 (high) = ۸۱٪ و Claude 4.5 Haiku = ۲۶٪ | [arXiv 2511.13029 v1، شکل ۷](https://arxiv.org/html/2511.13029v1) · فایل: `…/resources/Artificial_Analysis_Omniscience_Hallucination_Rate.png` (sha256 `082b8c01…a080`) | CC BY 4.0 | `Figure: Artificial Analysis, AA-Omniscience (arXiv 2511.13029), CC BY 4.0` |

**نکته‌ها**

- شکل‌های AA لوگوی شرکت‌ها را زیر ستون‌ها دارند (همان‌طور که منتشر شده)؛ در ویدیو به‌عنوان سند نشان بده، **در تامبنیل نیاور**. شکل ۱ گزیده‌ای از مدل‌هاست، نه هر ۳۶ مدل؛ رتبهٔ «چهارم از ۳۶» از متن مقاله است، نه از شمردن ستون‌های شکل.
- نشان ChatGPT داخل اسکرین‌شات پیوست B بخشی از سند دادگاه است؛ در قاب ۲ به‌عنوان سند نشانش بده، ولی **در تامبنیل نیاور** (بستهٔ انتشار لوگوی شرکت‌ها را ممنوع کرده).
- اسکرین‌شات‌ها را خود وکیل (Schwartz) گرفته و دادگاه ضمیمه کرده. متن رأی قطعاً مالکیت عمومی است؛ ضمیمه‌ها محتوای شخص ثالث در پروندهٔ عمومی‌اند (برای همین اعتبارشان «exhibit in the public court record» است، نه «public domain»). محتوا خروجی ماشین است و ریسک حقوقی بسیار کم است، ولی اگر نخواستی هیچ ریسکی کنی، فقط `beat02_mata_order_page1_PD.jpg` را نگه دار و پیوست‌ها را بردار.
- زمان پرسش «Is varghese a real case» در خود رأی مبهم است (بند ۴۶ و ۴۷). در متن گفتاری عمداً نگفته‌ایم «قبل از» تحویل لایحه پرسید.
- نمودار فصلی قاب ۱۱ تصویر نیست؛ SVG خود دک است که از `artifact/derived/charlotin_cases_by_quarter.csv` ساخته شده (منبع: AI Hallucination Cases Database، Damien Charlotin، CC BY 4.0). متن اعتبار در توضیحات: `Data: AI Hallucination Cases Database, Damien Charlotin, https://www.damiencharlotin.com/hallucinations/ (CC BY 4.0); quarterly counts by Homodyne`.

## دانلود نشد

- **جدول SimpleQA در صفحهٔ OpenAI** (قاب ۵): https://openai.com/index/why-language-models-hallucinate/ — حق نشر صفحه با OpenAI است و مجوز آزادِ بازنشر ندارد. راه: خودت صفحه را در مرورگر باز کن و هنگام ضبط از صفحهٔ باز ضبط صفحه بگیر (نمایش مستقیم برای نقد و آموزش)، یا فقط به جدول دک بسنده کن.
- **نمودار رسمی Vectara** (`img/top25_hallucination_rates_2026-11-24.png` در مخزن گیت‌هاب): مخزن Apache-2.0 است و بازنشر مجاز است، ولی لازم نبود؛ قاب ۹ عددها را مستقیم از جدول README نشان می‌دهد و نمودار ۲۵ مدل اول ردیف GPT-5 را ندارد. اگر خواستی B-roll داشته باشی، صفحهٔ گیت‌هاب را خودت باز کن و اسکرول کن تا ردیف `openai/gpt-5-high-2025-08-07`.
- **صفحهٔ پایگاه دادهٔ شارلوتن** (قاب ۱۱): محتوای سایت CC BY 4.0 است، ولی عدد زنده‌اش هر روز عوض می‌شود. راه: روز ضبط خودت https://www.damiencharlotin.com/hallucinations/ را باز کن و عدد «cases identified» و «Last updated» را ضبط صفحه کن.
- **عکس‌های خبری وکیل‌ها و جلسهٔ دادگاه Mata** (Reuters، AP، NYT و…): حق نشر دارند؛ دانلود نشد و جایگزین لازم نیست.
- **پروندهٔ Moffatt v. Air Canada** (دادگاه حل اختلاف بریتیش کلمبیا، ۲۰۲۴): برای این قسمت استفاده نشد (دربارهٔ مسئولیت جواب غلط چت‌بات است، نه دربارهٔ «چه چیزی شمرده می‌شود»)؛ تصویری هم دانلود نشد.

</div>
