# HMD-S04 · منابع

> همهٔ منابع ۲۸ نوامبر ۲۰۲۶ (۷ آذر ۱۴۰۵) باز و خوانده شدند، مگر جایی که نوشته شده. نقل‌قول‌ها کوتاه‌اند و فقط برای گزارش و نقد.
> برچسب‌ها: ✅ از متن منبع خوانده شد · 🔁 از متن یک منبع دیگر یا خلاصهٔ جست‌وجو (منبع اصلی کامل باز نشد) · 🟡 دانستهٔ درسی/استاندارد · ⚠️ اختلاف یا ابهام · [VERIFY] پیش از استفادهٔ بیشتر بازبینی شود.

## منبع اصلی و داده

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| R01 | J. P. Cangialosi, J. Martinez, B. Reinhart, P. Papin, «National Hurricane Center Forecast Verification Report, 2025 Hurricane Season», NHC، ۳۰ مارس ۲۰۲۶ — https://www.nhc.noaa.gov/verification/pdfs/Verification_2025.pdf (۲۲٫۸ مگابایت؛ متن با `pdftotext -layout`) | چکیده: «Official forecasts generally outperformed most dynamical and consensus models, though the Google DeepMind ensemble mean (GDMI) showed slightly better short-range performance.» · §۱: قاعدهٔ راستی‌آزمایی (فقط وقتی سامانه در best track در لحظهٔ شروع **و** لحظهٔ اعتبار حاره‌ای/نیمه‌حاره‌ای است)؛ خطای مسیر = فاصلهٔ دایرهٔ عظیمه؛ خطای شدت = قدرمطلق اختلاف؛ مدل‌های «زودهنگام/interpolated» (اجرای قبلی، صاف و جابه‌جا شده تا با موقعیت مشاهده‌شده جور شود؛ «no distinction between 6- and 12-h interpolated models»)؛ CLIPER5 به‌عنوان مبنای بی‌مهارت · ص ۷: «2025 season marked the first time that NHC incorporated AI-based models into real-time operations» · §۲الف: ۲۴۰ پیش‌بینی؛ «the 24−72-h track forecast errors have been drastically reduced by about 75%» در «couple of decades»؛ GDMI «slightly outperformed NHC at the shorter lead times from 12 to 72 h»؛ «GDMI was not available during the early part of the season… does not include the first two storms» · **جدول ۲** (خطای مسیر، مایل دریایی، ۱۴ مدل؛ تعداد ۱۹۳/۱۷۰/۱۵۵/۱۳۵/۱۱۷/۱۰۳/۷۸/۵۹)؛ **جدول ۴** (شدت، گره؛ ۱۹۵…۵۹)؛ **جدول ۹** (شعاع مخروط ۲۰۲۶ و تغییر نسبت به ۲۰۲۵) · اقیانوس آرام شرقی جدول ۶ (GDMI ۸۷٫۳ در برابر OFCL ۱۱۱٫۹ در ۱۲۰ ساعت؛ فقط در study) · داده‌ها «taken from the ATCF on 11 February 2026» | ✅ |
| R02 | NHC ATCF archive 2025 — https://ftp.nhc.noaa.gov/atcf/archive/2025/ ؛ `aal01…13 2025.dat.gz` (پیش‌بینی‌ها) و `bal01…13 2025.dat.gz` (best track) | دادهٔ خام بازسازی؛ ۲۶ فایل، ۲۸ نوامبر ۲۰۲۶؛ sha256 در `artifact/data/SHA256SUMS` و خلاصه در `artifact/derived/SOURCE.txt`. نام‌ها: OFCL (رسمی)، GDMI/GDM2 (Google DeepMind، ۶ و ۱۲ ساعته)، EMXI/EMX2 (ECMWF IFS)، AVNI/AVN2 (GFS؛ در گزارش «GFSI»)، HFAI/HFBI (HAFS)، HWFI (HWRF)، HMNI (HMON)، CMCI (کانادا)، AEMI (میانگین GEFS)، HCCA/FSSE/TVCA (اجماع‌ها)، OCD5 (CLIPER5/DSHIFOR5)، DSHP/LGEM/NNIC/IVCN (شدت) | ✅ دانلود و پردازش شد. مالکیت عمومی (کار دولت آمریکا)؛ خطوط GDMI ← R06 |
| R03 | قالب ATCF a-deck/b-deck (NRL؛ نشانی قدیمی `nrlmry.navy.mil/atcf_web/docs/database/new/abrdeck.html` حالا به صفحهٔ عمومی NRL هدایت می‌شود) | ستون‌ها: BASIN, CY, YYYYMMDDHH, TECHNUM, TECH, TAU, Lat, Lon, VMAX, MSLP, TY, RAD… | 🟡 صفحه باز نشد. **درستی خوانش ما با بازتولید دقیق تعداد پیش‌بینی‌های جدول ۲ و ۴ R01 در هر هشت افق آزموده شد** (`--selftest`). |
| R04 | NOAA/NWS, «AI Hurricane Forecasting» — https://www.weather.gov/news/261102-AI-Hurricane-Forecasting | «NHC has partnered directly with Google DeepMind to develop a new AI hurricane forecast model»؛ «Last season was all about experimentation»؛ در طول فصل «NHC began using these AI systems as guidance in operational forecasts»؛ ملیسا: مدل‌های AI مسیر و شدت را زود دیدند، و در موردهای دیگر مدل‌های سنتی بهتر بودند؛ «official NHC forecast was the most skillful and consistent overall» | ✅ (خلاصهٔ WebFetch؛ جمله‌ها کوتاه نقل شدند) |
| R05 | Google DeepMind, «How we're supporting better tropical cyclone prediction with AI» (Weather Lab)، ۱۲ ژوئن ۲۰۲۵ — https://deepmind.google/blog/how-were-supporting-better-tropical-cyclone-prediction-with-ai/ | «50 possible scenarios, up to 15 days ahead»؛ پایگاه دادهٔ طوفان «past 45 years»؛ مسیر ۵ روزه به‌طور میانگین «140 km closer… than ENS» در آزمون ۲۰۲۳–۲۰۲۴ (ادعای خود شرکت)؛ شدت بهتر از HAFS (ادعای شرکت)؛ «not official warnings» | ✅ |
| R06 | Google, WeatherNext developer guide: Weather Lab — https://developers.google.com/weathernext/guides/weatherlab ؛ و Disclaimers — https://developers.google.com/weathernext/guides/disclaimers | پیش‌بینی‌های طوفان Weather Lab در CSV و ATCF قابل دانلودند؛ دادهٔ مربوط به زمانی بیش از یک ساعت پیش «Creative Commons Attribution 4.0 International (CC BY 4.0)»؛ دادهٔ بلادرنگ تابع «GDM Real-Time Weather Forecasting Experimental Data Terms of Use»؛ «Data is available from approximately 2023 to present»؛ عدد ۶۴ عضو فقط برای پیش‌بینی جهانی WeatherNext 2/3 آمده، نه مدل طوفان (بازبین، ۲۸ نوامبر ۲۰۲۶) | ✅ ⚠️ [VERIFY] که همین مجوز رونوشت‌های GDMI درون بایگانی NOAA را هم پوشش می‌دهد (منطقی است؛ صریح ننوشته). |
| R06b | تیترهای رسانه‌ای «AI بهتر از NHC/ابرکامپیوتر» (برای جملهٔ قاب ۱ «تیترها…»)، مثلاً Gizmodo «This AI aced hurricane season in 2025…» — https://gizmodo.com/this-ai-aced-hurricane-season-in-2025-heres-what-that-means-2000682445 ؛ TechSpot — https://www.techspot.com/news/110152-google-ai-weather-model-outperforming-us-supercomputer-forecasts.html | وجود چنین تیترهایی | 🔁 فقط عنوان از نتیجهٔ جست‌وجوی بازبین (۲۸ نوامبر ۲۰۲۶)؛ متن باز نشد. [VERIFY] پیش از ضبط یکی را باز کن و تاریخش را ثبت کن. |
| R07 | Google DeepMind / Nature، مقالهٔ مدل‌های WeatherNext (پیوندشده در R06): https://www.nature.com/articles/s41586-026-10953-2 | — | ⚠️ باز نشد (هدایت به صفحهٔ ورود). در متن استفاده نشده. [VERIFY] |
| R08 | IBTrACS v04r01, North Indian list — https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NI.list.v04r01.csv (۲۷٫۹ مگابایت) · ارجاع: Knapp و همکاران (۲۰۱۰)، BAMS 91، ۳۶۳–۳۷۶؛ Gahtan و همکاران (۲۰۲۴)، doi:10.25921/82ty-9e16 🟡 | گونو `2007151N14072` (۶۳ نقطهٔ سه‌ساعته، ۳۱ مه تا ۸ ژوئن ۲۰۰۷): اوج JTWC ۱۴۵ گره (۱ دقیقه‌ای، ۴ ژوئن ۱۲ گرینویچ)؛ اوج IMD ۱۲۷ گره (۳ دقیقه‌ای) با درجهٔ SUCS؛ شاهین `2021267N18094`، نام «GULAB:SHAHEEN-GU» (۸۵ نقطه، ۲۳ سپتامبر تا ۴ اکتبر ۲۰۲۱): اوج JTWC ۷۰ گره، IMD ۶۰ گره با درجهٔ SCS. فاصله‌ها حساب ما (`north-indian.json`): گونو ۸ کیلومتری راس‌الحد، ۲۴ جاسک، ۷۸ مسقط، ۱۸۷ چابهار؛ شاهین ۱۰۰ چابهار، ۵۵ مسقط، ۱۸۲ جاسک. | ✅ دانلود و پردازش شد. مالکیت عمومی (NOAA NCEI). |
| R09 | Natural Earth 1:50m land v5.1.2 — https://github.com/nvkelso/natural-earth-vector | زمینهٔ نقشهٔ دمو | ✅ مالکیت عمومی |

## مدل‌های AI هواشناسی (زمینه، study و قاب ۱۲)

| شناسه | منبع | چه چیزی | وضعیت |
|---|---|---|---|
| R10 | R. Lam و همکاران، «Learning skillful medium-range global weather forecasting» (GraphCast)، *Science* 382 (2023)، doi:10.1126/science.adi2336؛ و پست DeepMind ۱۴ نوامبر ۲۰۲۳ | آموزش روی ERA5 ۱۹۷۹ تا ۲۰۱۷ (۳۹ سال)؛ ردیاب طوفان روی خروجی GraphCast از HRES دقیق‌تر | 🔁 (خلاصهٔ جست‌وجو از پست DeepMind و چکیده؛ متن کامل مقاله باز نشد) |
| R11 | I. Price و همکاران، «Probabilistic weather forecasting with machine learning» (GenCast)، *Nature* (انتشار برخط دسامبر ۲۰۲۴)؛ arXiv 2312.15796 | ensemble؛ آموزش تا ۲۰۱۸، آزمون ۲۰۱۹؛ بهتر از ENS در ۹۷٫۲٪ هدف‌ها؛ وزن‌ها CC BY-NC-SA (کارت ایده) | 🔁 ⚠️ شمارهٔ جلد را از خلاصهٔ جست‌وجو نمی‌شود مطمئن بود؛ [VERIFY] |
| R12 | ECMWF, «ECMWF's AI forecasts become operational»، ۲۵ فوریه ۲۰۲۵ — https://www.ecmwf.int/node/29308 ؛ و صفحهٔ «Implementation of AIFS Single v1» | AIFS Single از ۲۵ فوریه ۲۰۲۵، اجرای ۰۶ گرینویچ، عملیاتی شد؛ نخستین مدل یادگیری ماشینی کاملاً عملیاتی ECMWF | 🔁 (خلاصهٔ جست‌وجو از صفحه‌های ECMWF) |
| R13 | F. Alet و همکاران، «Skillful joint probabilistic weather forecasting from marginals» (FGN)، arXiv 2506.10772، ۱۲ ژوئن ۲۰۲۵ | مدل ensemble گوگل که با CRPS آموزش دیده؛ ردیابی طوفان بهتر از پیشینیان | 🔁 (چکیده از جست‌وجو). ⚠️ اینکه GDMI دقیقاً کدام نسخه است را R05/R06 صریح نمی‌گویند؛ در متن فقط «مدل Weather Lab گوگل دیپ‌مایند». |
| R14 | ECMWF Open Data (AIFS، IFS) — https://data.ecmwf.int/forecasts/ | دسترس‌پذیری بی‌کلید (کارت ایده، ۲۷ نوامبر ۲۰۲۶)؛ مجوز CC BY 4.0 [VERIFY] | 🔁 (کارت ۲ بانک ایده؛ دوباره آزموده نشد چون در دمو استفاده نشد) |

## منطقهٔ ما

| شناسه | منبع | چه چیزی | وضعیت |
|---|---|---|---|
| R15 | IMD/RSMC New Delhi، توصیه‌نامه‌ها و اطلاعیه‌های شاهین (۱ تا ۳ اکتبر ۲۰۲۱)، `rsmcnewdelhi.imd.gov.in/uploads/archive/…` | اطلاعیهٔ ۳ اکتبر: عبور از ساحل عمان «between Long. 56°E & 58°E, around 57°E, by early hours of 4th October» | 🔁 ⚠️ سایت IMD از اینجا باز نشد (timeout)؛ متن از خلاصهٔ جست‌وجو. **روی دوربین استفاده نشده.** [VERIFY] |
| R16 | مختصات شهرها (GeoNames، گرد به ۰٫۰۱ درجه): چابهار ۲۵٫۲۹ش ۶۰٫۶۴ق، جاسک ۲۵٫۶۴ش ۵۷٫۷۷ق، مسقط ۲۳٫۵۹ش ۵۸٫۴۱ق، راس‌الحد ۲۲٫۵۳ش ۵۹٫۸۰ق | فقط برای فاصلهٔ نزدیک‌ترین عبور | 🟡 (خطای چند صدم درجه = کمتر از ۵ کیلومتر) |
| R17 | RSMC New Delhi مسئول پیش‌بینی طوفان در اقیانوس هند شمالی (دریای عرب و خلیج بنگال) است؛ NHC فقط اطلس و آرام شرقی | قاب ۲ و ۱۲ | 🟡 دانستهٔ استاندارد (WMO Tropical Cyclone Programme)؛ R01 §۱ حوزهٔ NHC را صریح می‌گوید. |

## عددهای ما (همه از `artifact/derived/verify-2025.json`، ۲۸ نوامبر ۲۰۲۶)

| عدد | تعریف |
|---|---|
| ۵۸/۹۱/۱۵۱/۳۱۲ کیلومتر (OFCL) و ۴۸/۷۶/۱۲۰/۳۱۶ (GDMI) | میانگین خطای مسیر در ۲۴/۴۸/۷۲/۱۲۰ ساعت، نمونهٔ هم‌گن جدول ۲ (۱۴ مدل) |
| ۶۴٫۹ و ۸۱٫۵ مایل دریایی | همان در ۷۲ ساعت به یکای NHC (NHC: ۶۶٫۵ و ۸۱٫۴) |
| ۱۰۳ و ۵۹ | تعداد پیش‌بینی در ۷۲ و ۱۲۰ ساعت؛ برابر جدول ۲ |
| ۷ و ۴ طوفان | تعداد طوفان‌های پشت ۷۲ و ۱۲۰ ساعت |
| منفی ۳۰٫۷ کیلومتر، بازهٔ منفی ۷۵ تا منفی ۱ | GDMI منهای OFCL در ۷۲ ساعت؛ bootstrap طوفانی، ۲۰۰۰ بار، seed 1 |
| منفی ۹٫۸، بازهٔ منفی ۱۹ تا مثبت ۲ | همان در ۲۴ ساعت |
| منفی ۲۷ تا منفی ۵ | bootstrap تک‌پیش‌بینی (نادرست) در ۴۸ ساعت، برای مقایسه |
| ۱۴٫۶ و ۱۴٫۲ گره | شدت ۷۲ ساعت، OFCL و GDMI، نمونهٔ جدول ۴ (NHC: ۱۴٫۶ و ۱۴٫۶) |
| ۵ از ۷ | طوفان‌هایی که در ۷۲ ساعت میانگین GDMI کمتر بود؛ OFCL در AL07 گابریل (۱۴۶ در برابر ۱۷۱) و AL10 جری (۹۱ در برابر ۱۵۰) |
| ملیسا، ۲۵ اکتبر ۲۰۲۵، ۰۰ گرینویچ | ۷۲ ساعت: GDMI ۱۰۸، OFCL ۱۴۶، EMXI ۱۱۱، AVNI ۴۳۰؛ ۱۲۰ ساعت: OFCL ۱۱۷، GDMI ۱۳۴ کیلومتر. رسیدن به جامائیکا در best track: ۲۸ اکتبر ۱۷ گرینویچ، ۱۶۰ گره. |
| ۱۸۵ کیلومتر | شعاع مخروط ۷۲ ساعت ۲۰۲۵ = ۱۰۰ مایل دریایی (R01 جدول ۹: ۹۵ + ۵) |

## چیزهایی که بیرون ماندند

| ادعا | چرا |
|---|---|
| «AI از متخصص‌ها بهتر است» (بی‌قید) | R01 فقط «slightly better short-range» می‌گوید؛ در ۱۲۰ ساعت و در شدت نه؛ و متخصص‌ها از GDMI استفاده می‌کردند (R04). |
| «هواشناسی ایران از این مدل‌ها استفاده می‌کند / نمی‌کند» | منبعی نداریم (کارت ایده هم صریحاً منع کرده). |
| «AI گونو یا شاهین را بهتر پیش‌بینی می‌کرد» | هیچ پیش‌بینی AI زنده‌ای برای این دو در بایگانی عمومی پیدا نکردیم؛ ساختن hindcast با GraphCast/GenCast هم (الف) مجوز وزن‌ها CC BY-NC-SA است و (ب) گونو در دادهٔ آموزشی است. |
| خطای پیش‌بینی IMD برای شاهین (کیلومتر) | گزارش IMD باز نشد (R15). اگر محمد آن را گرفت، می‌تواند در study بیاید، نه در این نسخهٔ متن. |
| تعداد قربانیان و خسارت گونو و شاهین | منبع اصلی بازبینی‌شده نداریم؛ لازم هم نیست. |
| «۱۴۰ کیلومتر بهتر از ENS» (R05) | ادعای خود شرکت روی ۲۰۲۳–۲۰۲۴، نه راستی‌آزمایی مستقل؛ فقط در study با همین برچسب. |
