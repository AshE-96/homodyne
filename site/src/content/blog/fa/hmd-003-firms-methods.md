---
title: "دادهٔ آتش FIRMS را چطور بخوانیم و خودمان اجرا کنیم؟"
description: "هر ردیف FIRMS مرکز یک پیکسل ۳۷۵ متری VIIRS است. ستون‌ها، API با MAP_KEY رایگان، اسکریپت firms_timeline.py و مرزهای کار بدون حقیقت زمینی."
lang: fa
translationKey: hmd-003-deep-dive
hmd: HMD-003
kind: deep-dive
date: 2026-12-04
tags: ["NASA FIRMS", "VIIRS", "MODIS", "سنجش از دور", "بازتولیدپذیری", "آتش جنگل"]
sources:
  - title: "NASA FIRMS (Fire Information for Resource Management System)"
    url: "https://firms.modaps.eosdis.nasa.gov/"
  - title: "NASA FIRMS · Area API"
    url: "https://firms.modaps.eosdis.nasa.gov/api/area/"
  - title: "NASA MODAPS · VNP14IMGTDL_NRT product page (VIIRS 375 m active fire)"
    url: "https://modaps.modaps.eosdis.nasa.gov/services/about/products/viirs-land-c2-nrt/vnp14imgtdl_nrt.html"
  - title: "NASA Earthdata · VIIRS Active Fire User Guide (PDF)"
    url: "https://www.earthdata.nasa.gov/sites/default/files/imported/VIIRS_activefire_User_Guide.pdf"
  - title: "NASA FIRMS · Fire Alerts: Important Notes"
    url: "https://firms.modaps.eosdis.nasa.gov/alerts/notes.php"
  - title: "Earth Fire Alliance & Muon Space · First light and first active fire images from operational FireSat (16 Sep 2026)"
    url: "https://earthfirealliance.org/news-article/earth-fire-alliance-and-muon-space-release-first-light-and-first-active-fire-images-from-operational-firesat-constellation/"
  - title: "Google · A breakthrough in wildfire detection (16 Sep 2024)"
    url: "https://blog.google/outreach-initiatives/sustainability/google-ai-wildfire-detection/"
  - title: "ایران‌اینترنشنال · گزارش آتش جنگل‌های الیت (۶ آذر ۱۴۰۴)"
    url: "https://www.iranintl.com/fa/202511276713"
  - title: "Wikipedia · Elit, Iran"
    url: "https://en.wikipedia.org/wiki/Elit,_Iran"
  - title: "Google Earth Engine catalog · FIRMS terms of use (NASA data policy, LANCE citation and disclaimer)"
    url: "https://developers.google.com/earth-engine/datasets/catalog/FIRMS"
datasets:
  - title: "NASA FIRMS · VIIRS 375 m active fire (S-NPP, NOAA-20, NOAA-21; SP و NRT)"
    url: "https://firms.modaps.eosdis.nasa.gov/"
    license: "دادهٔ باز ناسا (اشتراک کامل و آزاد)؛ ذکر LANCE FIRMS و پیوند به سلب مسئولیت آن"
  - title: "NASA FIRMS · MODIS 1 km active fire (برای مقایسه؛ اسکریپت از آن پشتیبانی می‌کند)"
    url: "https://firms.modaps.eosdis.nasa.gov/"
    license: "دادهٔ باز ناسا (اشتراک کامل و آزاد)؛ ذکر LANCE FIRMS و پیوند به سلب مسئولیت آن"
  - title: "HMD-003 artifact · firms_timeline.py و دو فایل ILLUSTRATIVE (۱۸ ردیف ساختگی، یک محل فرضی)"
    url: "https://github.com/AshE-96/homodyne/tree/main/parts/03-standalone/hmd-003-wildfire-from-space/artifact"
    license: "ساختگی (ILLUSTRATIVE)؛ ببینید LICENSE.md هومودین (کد: MIT)"
---

برای خواندن دادهٔ آتش FIRMS باید هر ردیف را «مرکز یک پیکسل حدود ۳۷۵ متری که در لحظهٔ عبور ماهواره داغ‌تر از اطراف بود» دید، نه محل دقیق یک آتش تأییدشده. برای اجرای آن کافی است با یک MAP_KEY رایگان از API ناحیه‌ای FIRMS دانلود کنید و اسکریپت `firms_timeline.py` را، که فقط به کتابخانهٔ استاندارد پایتون نیاز دارد، روی آن بزنید. خط زمانی آتش الیت با این روش هنوز اجرا نشده است؛ این نوشته نشان می‌دهد شما چطور می‌توانید اجرایش کنید.

> **نکته‌های اصلی**
> - محصول اصلی، نقطه‌های داغ VIIRS با پیکسل ۳۷۵ متری روی ماهواره‌های S-NPP، NOAA-20 و NOAA-21 است؛ MODIS با پیکسل حدود ۱ کیلومتری قدیمی‌تر و درشت‌تر است.
> - API ناحیه‌ای در هر درخواست حداکثر ۵ روز می‌دهد و با MAP_KEY رایگان ۵٬۰۰۰ تراکنش در هر ۱۰ دقیقه مجاز است.
> - ستون `type` (منبع ثابت، آتشفشان و غیره) فقط در محصول استاندارد SP هست، نه در NRT.
> - اسکریپت سه کار می‌کند: فیلتر اطمینان، علامت نزدیکی به محل صنعتی، و علامت تکرار در چند روز. هیچ precision یا recallی گزارش نمی‌کند.
> - دادهٔ نمونهٔ همراه ILLUSTRATIVE است و هیچ عددی از آن دربارهٔ آتش الیت نیست.

## کدام دیتاست‌ها و با چه شرایطی؟

همهٔ دادهٔ واقعی این قسمت از [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/) می‌آید؛ سامانه‌ای که نقطه‌های داغ دو خانوادهٔ حسگر را منتشر می‌کند.

| دیتاست | اندازهٔ پیکسل | نام منبع در API | دسترسی |
|---|---|---|---|
| VIIRS روی S-NPP | حدود ۳۷۵ متر | `VIIRS_SNPP_SP` و `VIIRS_SNPP_NRT` | MAP_KEY رایگان |
| VIIRS روی NOAA-20 | حدود ۳۷۵ متر | `VIIRS_NOAA20_SP` و `VIIRS_NOAA20_NRT` | MAP_KEY رایگان |
| VIIRS روی NOAA-21 | حدود ۳۷۵ متر | `VIIRS_NOAA21_*` | MAP_KEY رایگان |
| MODIS | حدود ۱ کیلومتر | `MODIS_*` | MAP_KEY رایگان |

دو نسخه از هر منبع وجود دارد. **NRT** دادهٔ تقریباً بی‌درنگ است و برای چند ماه اخیر به کار می‌آید. **SP** آرشیو پردازش استاندارد است که دیرتر منتشر می‌شود و ستون `type` را هم دارد. اگر یک منبع برای تاریخی داده نداشته باشد، FIRMS جدول خالی یا یک پیام برمی‌گرداند و اسکریپت همان پیام را چاپ می‌کند؛ در آن حالت نسخهٔ دیگر یا بخش Archive Download سایت FIRMS را امتحان کنید.

قاعده‌های API ناحیه‌ای (بازبینی ۲ نوامبر ۲۰۲۶):

- الگوی نشانی: `/api/area/csv/[MAP_KEY]/[SOURCE]/[W,S,E,N]/[DAY_RANGE]/[DATE]`
- `DAY_RANGE` بین ۱ و ۵ است؛ پس بازهٔ یک‌ماهه باید به تکه‌های ۵ روزه تقسیم شود و اسکریپت این کار را خودش می‌کند.
- MAP_KEY رایگان است و ۵٬۰۰۰ تراکنش در هر بازهٔ ۱۰ دقیقه‌ای اجازه می‌دهد. درخواست چندروزه ممکن است بیش از یک تراکنش حساب شود؛ دکمهٔ «Check status» در همان صفحه باقی‌مانده را نشان می‌دهد.

دربارهٔ شرایط استفاده: ناسا از اشتراک کامل و آزاد داده‌هایش پشتیبانی می‌کند. اگر دادهٔ FIRMS را در اختیار دیگران می‌گذارید، ناسا می‌خواهد از راهنمای ارجاع، قدردانی و سلب مسئولیت LANCE پیروی کنید و متن سلب مسئولیت را بیاورید یا به آن پیوند بدهید (خلاصهٔ این شرایط در [صفحهٔ FIRMS در کاتالوگ Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/FIRMS) آمده است). پیش از بازنشر ردیف‌های خام، همین شرایط را بخوانید.

کنار این‌ها دو فایل ساختگی در پوشهٔ artifact هست: `sample_firms_ILLUSTRATIVE.csv` با ۱۸ ردیف در قالب ستون‌های VIIRS، و `sites_ILLUSTRATIVE.csv` با یک محل صنعتی فرضی به نام SITE-A. هر دو با دست و برای آموزش نوشته شده‌اند؛ دادهٔ FIRMS نیستند و رویداد واقعی را توصیف نمی‌کنند.

## هر ستون یک ردیف FIRMS چه می‌گوید؟

تعریف ستون‌ها از [صفحهٔ محصول VIIRS در NASA MODAPS](https://modaps.modaps.eosdis.nasa.gov/services/about/products/viirs-land-c2-nrt/vnp14imgtdl_nrt.html) و [راهنمای کاربر VIIRS](https://www.earthdata.nasa.gov/sites/default/files/imported/VIIRS_activefire_User_Guide.pdf) است:

- **`latitude`، `longitude`:** «Center of nominal 375 m fire pixel»؛ مرکز پیکسل، نه محل دقیق آتش.
- **`acq_date`، `acq_time`:** تاریخ و ساعت عبور، به وقت هماهنگ جهانی (UTC) و به شکل HHMM. برای تهران سه ساعت و نیم اضافه کنید؛ ایران از ۲۰۲۳ ساعت تابستانی ندارد.
- **`satellite`:** ماهواره‌ای که نقطه را دیده، مثلاً `N` برای S-NPP و `N20` برای NOAA-20.
- **`confidence`:** در VIIRS یکی از `l`، `n`، `h` (کم، معمولی، زیاد). نقطه‌های کم‌اطمینانِ روزانه «typically associated with areas of Sun glint». در MODIS این ستون عددی بین ۰ و ۱۰۰ است و اسکریپت آن را این‌طور نگاشت می‌کند: کمتر از ۳۰ کم، ۳۰ تا ۷۹ معمولی، ۸۰ و بیشتر زیاد.
- **`frp`:** توان تابشی آتش به مگاوات؛ تقریبی از شدت گرمای آن پیکسل.
- **`daynight`:** `D` برای روز و `N` برای شب.
- **`type`:** فقط در محصول SP: ۰ آتش گیاهی احتمالی، ۱ آتشفشان، ۲ منبع ثابت دیگر روی خشکی، ۳ منبع روی آب.

ستون‌هایی مثل `bright_ti4` و `bright_ti5` هم در فایل هستند، ولی اسکریپت این قسمت از آن‌ها استفاده نمی‌کند.

## اسکریپت دقیقاً چه می‌کند؟

`firms_timeline.py` فقط کتابخانهٔ استاندارد Python 3.9 یا بالاتر را لازم دارد و تا وقتی `--fetch` ندهید، به شبکه وصل نمی‌شود. مراحلش:

1. **خواندن:** CSV را می‌خواند. خط‌هایی که با `#` شروع شوند توضیح‌اند؛ اگر در آن‌ها واژهٔ ILLUSTRATIVE باشد، بنر هشدار چاپ می‌شود.
2. **محدوده و تاریخ:** فقط ردیف‌های داخل جعبهٔ W,S,E,N و بازهٔ تاریخ می‌مانند.
3. **آستانهٔ اطمینان:** ردیف‌های پایین‌تر از `--min-confidence` (پیش‌فرض `nominal`) کنار می‌روند. خروجی همیشه نشان می‌دهد با هر سه آستانه چند ردیف می‌ماند.
4. **نزدیکی به محل صنعتی:** فاصلهٔ هر نقطه تا نزدیک‌ترین محل فهرست شما با فرمول haversine حساب می‌شود؛ اگر کمتر از `--near-km` (پیش‌فرض ۲) باشد، علامت می‌خورد.
5. **تکرار:** اگر نقطه‌هایی در شعاع `--repeat-km` (پیش‌فرض ۰٫۵) در `--repeat-days` (پیش‌فرض ۳) روز مختلف یا بیشتر دیده شده باشند، علامت «recurring» می‌خورند. روز خودِ نقطه هم شمرده می‌شود.
6. **ستون type:** اگر ستون وجود داشته باشد و مقدارش ۲ باشد، علامت منبع ثابت می‌خورد.
7. **گزارش:** خط زمانی روزبه‌روز (تعداد، تعداد علامت‌خورده، بیشترین FRP)، جدول نقطه‌ها با ساعت UTC و تهران، و خلاصه‌ای با اولین نقطهٔ بدون علامت.

اسکریپت هیچ مدل یادگیری ماشینی ندارد و تصمیم نمی‌گیرد که نقطه آتش است. فقط می‌گوید چه چیزی، کی و با چه علامتی دیده شد.

## چطور خودتان اجرا کنید؟

همهٔ دستورها از ریشهٔ مخزن اجرا می‌شوند.

**۱. اجرای آفلاین روی دادهٔ ILLUSTRATIVE (بدون کلید):**

```bash
python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --demo --region mazandaran
python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --demo --region mazandaran --min-confidence low --quiet
python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --demo --region mazandaran --min-confidence high --quiet
```

با جعبهٔ بزرگ‌تر `mazandaran`، روی این دادهٔ ساختگی باید ببینید: ۱۸ ردیف در جعبه؛ با آستانهٔ کم، معمولی و زیاد به‌ترتیب ۱۸، ۱۵ و ۷ ردیف می‌ماند؛ اولین نقطهٔ نگه‌داشته کنار SITE-A است و علامت تکرار پنج‌روزه دارد. در حالت `low`، یک نقطهٔ ضعیف در محل آتش نمونه حدود ۱۲ ساعت پیش از اولین نقطهٔ `nominal` همان‌جا پیدا می‌شود. اگر با `--demo` منطقه ندهید، اسکریپت همین جعبهٔ `mazandaran` را به کار می‌برد، چون ردیف‌های نمونه همین ناحیه را پوشش می‌دهند؛ با `--region elit` فقط ۱۲ ردیف از ۱۸ ردیف می‌ماند (۱۲، ۱۰ و ۵) و SITE-A بیرون جعبه است، پس هیچ نقطه‌ای علامت نمی‌خورد. این عددها فقط برای آزمودن درستی اجرای شماست و دربارهٔ هیچ آتش واقعی چیزی نمی‌گوید.

**۲. گرفتن MAP_KEY:** صفحهٔ [API ناحیه‌ای FIRMS](https://firms.modaps.eosdis.nasa.gov/api/area/) را باز کنید، گزینهٔ Get MAP_KEY را بزنید، ایمیلتان را وارد و کلید رسیده را تأیید کنید. کلید را فقط در پوستهٔ خودتان نگه دارید و هرگز در مخزن نگذارید:

```bash
export FIRMS_MAP_KEY=your_key_here
```

**۳. دانلود بازهٔ آتش الیت:**

```bash
mkdir -p data
python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --fetch --region elit \
    --start 2025-10-28 --end 2025-11-27 \
    --sources VIIRS_SNPP_SP,VIIRS_NOAA20_SP \
    --save data/elit_2025-11.csv
```

بازهٔ ۲۸ اکتبر تا ۲۷ نوامبر ۲۰۲۵ (۶ آبان تا ۶ آذر ۱۴۰۴) هر دو تاریخ شروع و شعله‌ورشدن دوباره را در بر می‌گیرد. اگر نسخهٔ SP برای این ماه‌ها داده نداد، `--sources VIIRS_SNPP_NRT,VIIRS_NOAA20_NRT,VIIRS_NOAA21_NRT` یا Archive Download را امتحان کنید.

**۴. اجرای دوباره بدون شبکه، تا عددهایتان بازتولیدپذیر بمانند:**

```bash
python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --csv data/elit_2025-11.csv --region elit --min-confidence low
```

**۵. فهرست محل‌های صنعتی شما:** یک CSV با ستون‌های `name,lat,lon,kind` بسازید و با `--sites my_sites.csv` بدهید. اسکریپت هیچ مختصات واقعی‌ای همراه خودش ندارد. هر سطر را از منبعی که خودتان بررسی کرده‌اید (OpenStreetMap یا نقشهٔ رسمی) بسازید و منبع را کنار سطر بنویسید.

## محدودهٔ «الیت» چطور تعریف شده است؟

در اسکریپت، `--region elit` جعبهٔ (W, S, E, N) = (50.95, 36.20, 51.45, 36.55) است. مبنای آن مختصات روستای الیت است: حدود 36.32 شمالی و 51.11 شرقی، در دهستان کوهستان، بخش مرزن‌آباد، شهرستان چالوس. کجور، حدود 36.38 شمالی و 51.72 شرقی، بیرون این جعبه می‌ماند. جعبه تقریبی است؛ پیش از انتشار هر نتیجه آن را روی نقشه بررسی کنید یا با `--bbox` جعبهٔ خودتان را بدهید. اگر در جدول `artifact/README.md` عدد دیگری دیدید، مقدار داخل خود اسکریپت همان است که اجرا می‌شود.

## چرا precision و recall گزارش نمی‌شود؟

precision یعنی چه سهمی از هشدارها آتش واقعی بودند، و recall یعنی چه سهمی از آتش‌های واقعی دیده شدند. هر دو به یک فهرست مستقل از زمین نیاز دارند: محل، زمان و وسعت هر آتش. برای شمال ایران چنین فهرست معتبری در اختیار ما نیست، و حتی دربارهٔ مساحت سوختهٔ یک آتش مشهور مثل الیت، برآوردهای رسمی از حدود ۸ هکتار (معاون وزیر جهاد کشاورزی و استاندار) و حدود ۱۰ هکتار (منابع طبیعی) تا ۱۵۰ تا ۱۸۰ هکتار (معاون سازمان حفاظت محیط زیست) فرق دارند.

برای یک ارزیابی واقعی، دست‌کم این‌ها لازم است: فهرست زمینی مستقل با زمان و مختصات، قاعدهٔ تطبیق از پیش اعلام‌شده (چه فاصله‌ای و چه بازهٔ زمانی «همان آتش» حساب شود)، و جدا کردن آتش‌هایی که اصلاً قابل‌دیدن نبودند. FIRMS دلیل‌های ندیده‌شدن را صریح گفته: آتشی که «started and ended between satellite overpasses»، یا آتشی زیر «cloud cover, heavy smoke, or tree canopy». بدون این‌ها هر درصد دقتی، عددی بی‌پشتوانه است.

## محدودیت‌های این روش

- **مختصات تقریبی است:** مرکز پیکسل حدود ۱۴ هکتاری، نه جای آتش.
- **نمونه‌برداری گسسته است:** فقط لحظه‌های عبور ماهواره دیده می‌شوند؛ اولین نقطه، اولین لحظهٔ آتش نیست.
- **تاج درختان:** در جنگل انبوه هیرکانی، آتش زیرِ تاج ممکن است کم‌رنگ دیده شود یا اصلاً دیده نشود.
- **علامت‌ها اکتشافی‌اند:** نزدیکی و تکرار هر دو می‌توانند آتش واقعی را علامت بزنند یا منبع ثابت را از قلم بیندازند، و کیفیتشان به کامل‌بودن فهرست محل‌های شما بستگی دارد.
- **ستون type در NRT نیست:** برای داده‌های اخیر، این کمک را ندارید.
- **این FireSat نیست:** طبق اعلام Earth Fire Alliance در ۱۶ سپتامبر ۲۰۲۶، باندهای فروسرخ FireSat می‌توانند آتشی به کوچکی ۵ در ۵ متر را تشخیص دهند و دسترسی جهانی‌اش برای ۲۰۲۸ برنامه‌ریزی شده است. اسکریپت ما با دادهٔ VIIRS کار می‌کند و هیچ مدل FireSat یا گوگل را بازسازی نمی‌کند.

## این چه چیزی را نشان نمی‌دهد

- عددی دربارهٔ آتش الیت از FIRMS نشان نمی‌دهد؛ آن اجرا هنوز انجام نشده است.
- نشان نمی‌دهد VIIRS در شمال ایران چقدر دقیق است.
- نشان نمی‌دهد ماهواره آتش الیت را زودتر از مردم روی زمین دید.
- خروجی دادهٔ ILLUSTRATIVE را نباید دربارهٔ هیچ مکان یا آتش واقعی خواند.

## برای مطالعهٔ بیشتر

- [راهنمای کاربر محصول آتش فعال VIIRS](https://www.earthdata.nasa.gov/sites/default/files/imported/VIIRS_activefire_User_Guide.pdf)، برای الگوریتم و معنای ستون‌ها.
- [یادداشت‌های مهم هشدارهای FIRMS](https://firms.modaps.eosdis.nasa.gov/alerts/notes.php)، برای دلیل‌های ندیده‌شدن آتش.
- [اعلامیهٔ Earth Fire Alliance دربارهٔ FireSat](https://earthfirealliance.org/news-article/earth-fire-alliance-and-muon-space-release-first-light-and-first-active-fire-images-from-operational-firesat-constellation/) و [توضیح گوگل از نقش هوش مصنوعی](https://blog.google/outreach-initiatives/sustainability/google-ai-wildfire-detection/).
- نسخهٔ خلاصه برای خوانندهٔ عمومی: [آیا می‌توان آتش کوچک جنگل را از فضا دید؟](/fa/blog/hmd-003-small-fires-from-space/)
- ویدیو و دک: [صفحهٔ HMD-003](/fa/episodes/hmd-003/)؛ قسمت بعد: [HMD-004](/fa/episodes/hmd-004/)
- نسخهٔ انگلیسی: [How to read and rerun NASA FIRMS fire data](/en/blog/hmd-003-firms-methods/)
