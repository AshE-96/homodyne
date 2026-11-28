# HMD-S11 · منابع

> همهٔ منابع ۲۸ نوامبر ۲۰۲۶ (۷ آذر ۱۴۰۵) باز و خوانده یا آزموده شدند، مگر جایی که نوشته شده. هیچ API پولی، ورود یا دیوار پرداختی استفاده نشد. Open-Meteo در این قسمت **اصلاً** استفاده نشد.
> برچسب‌ها: ✅ از متن منبع خوانده یا با دادهٔ خودش آزموده شد · 🔁 از دانستهٔ عمومی یا منبع دیگر (متن اصلی باز نشد) · ⚠️ اختلاف یا ابهام · `[VERIFY]` پیش از ضبط دوباره ببین.

## داده و مجوز

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| S01 | ECMWF, «Open data» — https://www.ecmwf.int/en/forecasts/datasets/open-data ؛ مجوز: https://apps.ecmwf.int/datasets/licences/general/ | IFS و AIFS Single در ۰٫۲۵ درجه، CC BY 4.0 با ذکر منبع و اعلام تغییر («پردازش هومودین»)؛ data.ecmwf.int فقط چند روز آخر را نگه می‌دارد (در HMD-S06 خوانده شد) | ✅ (از HMD-S06، همان روز) |
| S01b | آینه‌های ابری همان داده: `storage.googleapis.com/ecmwf-open-data/…` و `ecmwf-forecasts.s3.eu-central-1.amazonaws.com/…` (AWS Open Data، فهرست AWS: «CC-BY-4.0»، بی‌حساب) | **بایگانی** اجراهای آوریل ۲۰۲۵ با همان نام فایل و `.index`. آزمون ما: GCS پاسخ داد (فقط یک بازهٔ بایت در هر درخواست)؛ AWS بیشتر درخواست‌ها را با 503 SlowDown رد کرد. بخش‌های موجود ۲۰۲۵: IFS با `10fg`، `mucape`، `2t`، `2d`، `10u/10v` و سطح‌های ۱۰۰۰ تا ۵۰ hPa؛ AIFS بی‌تندباد و بی‌CAPE | ✅ دسترسی و محتوا · ✅ صفحهٔ Open data خود ECMWF (۲۸ نوامبر ۲۰۲۶) می‌گوید زیرمجموعهٔ open data روی AWS، Azure و Google Cloud «replicated» است |
| S02 | ECMWF IFS و AIFS، اجرای 00Z ۲۸ نوامبر ۲۰۲۶، data.ecmwf.int | زمین مدل زیر سکو (IFS ۱٬۸۳۷، AIFS ۱٬۸۹۴ متر) و زیر مهرآباد (۱٬۴۴۳، ۱٬۵۶۰)؛ نمای «فردا» | ✅ `artifact/derived/SOURCE.txt` |
| S03 | Iowa Environmental Mesonet, ASOS/METAR archive — https://mesonet.agron.iastate.edu/request/download.phtml ؛ disclaimer: https://mesonet.agron.iastate.edu/disclaimer.php | METAR مهرآباد آوریل ۲۰۲۵ (۶۰ مقایسه)؛ متن خام ۱۷ آوریل؛ تعداد ماهانهٔ گزارش‌ها: ۲۰۲۵ کامل (~۱٬۴۰۰ تا ۱٬۵۰۰ در ماه)، **اسفند ۱۴۰۴ تا اردیبهشت ۱۴۰۵ (مارس و آوریل ۲۰۲۶) تقریباً خالی** (۲ و ۱۹۷ گزارش برای OIII)، آخرین گزارش OIII: ۱۴ نوامبر ۲۰۲۶، ۱۵:۳۰ UTC. مجوز: «in the public domain… may be used freely by anyone for any lawful purpose» | ✅ |
| S04 | NOAA/NCEP NOMADS, GFS 0.25° grib filter — https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl ؛ مالکیت عمومی: https://www.weather.gov/disclaimer | GFS ساعتی برای سکو: باد ۱۰ متری، سطح‌های ۹۰۰ تا ۵۰۰ hPa، GUST، CAPE، HPBL، SHTFL؛ زمین مدل ۱٬۸۴۸ (سکو) و ۱٬۴۵۵ (مهرآباد) | ✅ |
| S05 | Open-Meteo, Terms — https://open-meteo.com/en/terms | **استفاده نشد.** API رایگان فقط غیرتجاری؛ تصمیم مجوز با محمد (کارت ایده). نسخهٔ «پیش‌بینی گذشته» Open-Meteo راه ساده‌تری بود؛ به‌جایش بایگانی خود ECMWF را خواندیم | ✅ (از HMD-S06) |
| S06 | HMD-S06، `parts/03-standalone/hmd-s06-damavand-summit-weather/artifact/grib2_point.py` و `summit_fetch.py` | رمزگشای GRIB2 (CCSDS) کپی شد با سرآیند اعتبار؛ `get` و `get_ranges` اقتباس شد | ✅ داخلی |
| S10 | aviationweather.gov Data API — `https://aviationweather.gov/api/data/metar?ids=OIII,OIIE&hours=48` | ۲۸ نوامبر ۲۰۲۶: HTTP 204 (خالی) برای مهرآباد و امام | ✅ آزمون دسترسی |
| S11 | NOAA ISD (global-hourly) روی AWS | کارت ایده: مهرآباد فقط تا ۲۴ اوت ۲۰۲۵ | 🔁 (کارت ایده، ۲۷ نوامبر؛ دوباره آزموده نشد، لازم هم نشد) |
| S12 | سازمان هواشناسی کشور — irimo.ir | کارت ایده: از بیرون ایران وصل نشد | 🔁 `[VERIFY]` از داخل ایران |

## مکان‌ها

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| S13 | SRTM از طریق OpenTopoData — `api.opentopodata.org/v1/srtm30m` و `srtm90m` (دادهٔ NASA، مالکیت عمومی) | ارتفاع سکو ۲٬۳۲۵ متر (۳۰ متری)؛ نقطهٔ OSM ۲٬۳۲۰ (۹۰ متری)؛ نیم‌رخ ۲۴ نقطه دور سکو: زمین به شرق، جنوب‌شرق، جنوب، غرب و شمال‌غرب پایین می‌رود (چند سکو ممکن است)؛ مهرآباد ۱٬۱۸۳ | ✅ `[VERIFY]` با باشگاه |
| S14 | OpenStreetMap (Overpass، ۲۸ نوامبر ۲۰۲۶؛ © OpenStreetMap contributors، ODbL) | node 10207682763 «سایت پرواز گلایدر شهران» 35.80701 N، 51.28557 E؛ node 6120597767 «سایت پرواز پاراگلایدر شهران» 35.77715 N، 51.30077 E (ارتفاع ۱٬۵۶۱، احتمالاً پایین‌تر/فرود)؛ node 9196055606 آبیک قزوین | ✅ |
| S15 | FlyAPPI, «Shahran (Peak)» — https://flyappi.org/take_off/16923/ و https://flyappi.org/flysite/9771 | سکو حدود 35.8076 N، 51.2851 E (از پیوند XContest)؛ «Good for learning»؛ جهت‌ها به‌صورت رشتهٔ مبهم؛ متن ۲۰۱۱ و هشدار «قوانین هر سال عوض می‌شود» | ✅ ⚠️ قدیمی |
| S16 | Mehrabad International Airport — Wikipedia و SkyVector (OIII) | ارتفاع فرودگاه ۱٬۲۰۸ متر (۳٬۹۶۲ پا؛ SkyVector ۳٬۹۶۵) | 🔁 (AIP رسمی باز نشد) |
| S17 | IANA tz mailing list؛ Wikipedia «Iran Standard Time» | ایران از ۲۰۲۲ ساعت تابستانی ندارد؛ UTC+3:30 تمام سال (برای آوریل ۲۰۲۵ و ۲۰۲۷ هم) | ✅ |

## پرواز، باد و گزارش

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| S20 | USHPA, *Pilot Proficiency System*, SOP 12-02, «Last Amended September, 2023» (نسخهٔ PDF میزبانی‌شده نزد یک مدرسهٔ پرواز: https://cdn.shopify.com/s/files/1/2630/5424/files/SOP-12-02_4.pdf) | خلبان مبتدی پاراگلایدر (P2): «Maximum base wind of 12 MPH»، «Maximum peak gusts to 15 MPH»، «Maximum gust rate of 5 MPH in 5 seconds»، «Should not fly in thermal lift where peak climb rates exceed 200 fpm»، پرتاب پیاده فقط وقتی باد «within 25º of being straight up the slope». متوسط (P3): ۱۵ و ۱۸ مایل، و «thermals where peak climb rates exceed 500 fpm or where significant vertical cloud development exists» | ✅ متن خوانده شد و ۲۸ نوامبر ۲۰۲۶ دوباره با pdftotext وارسی شد (همهٔ عددها و «Last Amended September, 2023») · `[VERIFY]` با نسخهٔ ushpa.org (کتابخانهٔ SOP در بخش اعضاست) |
| S21 | باشگاه یا فدراسیون پرواز ایران | قاعدهٔ محلی، جهت و ارتفاع دقیق سکو، اجازهٔ فیلم‌برداری | ⛔ هنوز گرفته نشده (`prep-fa.md` §۱) |
| S22 | WMO-No. 306 *Manual on Codes* / ICAO Annex 3 (خلاصهٔ Skybrary: https://skybrary.aero/articles/wind-velocity-reporting) | METAR: باد میانگین ۱۰ دقیقهٔ پیش از گزارش؛ تندباد سه‌ثانیه‌ای فقط وقتی دست‌کم ۱۰ گره (۵ m/s) بالاتر از میانگین باشد؛ TEMPO یعنی تغییر موقت پیش‌بینی‌شده، نه مشاهده | 🔁 (از خلاصه‌ها؛ متن کامل Annex 3 باز نشد) `[VERIFY]` |
| S23 | Whiteman, C. D., *Mountain Meteorology: Fundamentals and Applications*, Oxford University Press, 2000 | باد شیب (روز بالارو، شب پایین‌رو)، باد دره، گرداب پشت ستیغ، فون | 🔁 (کتاب درسی؛ باز نشد) |
| S24 | Stull, R., *Practical Meteorology: An Algebra-based Survey of Atmospheric Science*, UBC, 2017 (باز، CC BY-NC-SA)؛ Stull, R., *An Introduction to Boundary Layer Meteorology*, Kluwer, 1988 | ارتفاع تراز میعان صعودی ≈ ۱۲۵ متر × (T − Td)؛ افت دمای خشک ۹٫۸ K/km؛ رشد روزانهٔ لایهٔ مرزی و آمیختگی تکانه | 🔁 `[VERIFY]` شمارهٔ معادله |
| S25 | Deardorff, J. W. (1970), «Convective velocity and temperature scales for the unstable planetary boundary layer and for Rayleigh convection», *J. Atmos. Sci.* 27, 1211–1213 | w* = (g/T · H/(ρ cp) · zi)^(1/3) | 🔁 |
| S26 | ECMWF Parameter Database — `10fg` (10 metre wind gust)، `mucape` | تعریف تندباد ۱۰ متری (بیشینه در بازهٔ پیش از گام) و CAPE ناپایدارترین بسته | ✅ طول بازه از خود فایل: بخش ۴ GRIB2 (template 4.8) برای اجرای ۱۶ آوریل ۲۰۲۵ گام ۳۰ و ۳۶ = **بیشینهٔ ۱ ساعت** پیش از گام؛ گام ۱۵۰ = ۶ ساعت (وارسی ۲۸ نوامبر ۲۰۲۶) |
| S27 | NCEP GFS، متغیر `SHTFL` | علامت: در اجرای ما روز مثبت (تا ۷۰ W/m²) و شب منفی بود؛ پس «مثبت = رو به بالا» | ✅ از داده · `[VERIFY]` از مستند NCEP |

## زنجیره

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| S30 | `parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/README.md` (HMD-012) | فقط موضوع تیزر: «چند سؤال تا اعتماد به نمره». هیچ عددی از آن در این قسمت نیامده | ✅ داخلی |
| S31 | HMD-011 «طوفان خورشیدی بعدی را می‌شود پیش‌بینی کرد؟» | فقط پل روایی قاب ۲ | ✅ داخلی (عنوان از manifest) |

## هر عدد از کجا

| عدد در متن یا دک | مقدار | از کجا |
|---|---|---|
| ۱۷ آوریل ۲۰۲۵، ۱۵:۳۰: پیش‌بینی روز قبل، تندباد، CAPE | ۱٫۵ km/h · ۲۸٫۲ · ۰ | `case-2025-04-17.json` (IFS 16 Apr 00Z، گام ۳۶) |
| همان، پیش‌بینی همان صبح · AIFS روز قبل | ۷٫۹ · ۱۰٫۶ km/h | همان فایل |
| همان، مشاهده | `27024KT` = ۴۴٫۴ km/h، `FEW040CB`، `TEMPO 27034KT 3000 SA/DU` | S03، متن خام در همان فایل |
| ارزیابی: میانگین مشاهده · میانگین IFS · AIFS | ۱۶٫۲ · ۸٫۴ · ۸٫۰ km/h | `eval-2025-04.json` (۶۰ جفت) |
| bias · MAE | IFS −۷٫۸ و ۸٫۵ · AIFS −۸٫۱ و ۸٫۴ | همان، `stats.all` |
| جهت: میانه · بیش از ۴۵° | IFS ۲۲° و ۱۴ از ۴۹ · AIFS ۳۱° و ۱۵ از ۴۹ (فقط باد مشاهده ≥ ۵ گره) | همان |
| ۱۹ km/h و بیشتر | مشاهده ۱۸ بار · IFS ۱ · AIFS ۱ | همان، `over_novice_line` |
| تندباد IFS بالای اوج مشاهده · گزارش تندباد METAR | ۵۶ از ۶۰ · ۱ بار در ۶۰ بازهٔ سه‌ساعته | همان، `ifs_gust_above_obs_peak` و `obs.gust_reports` |
| فرق خطای مطلق دو مدل · n مؤثر | ۰٫۱۷ ± ۰٫۴۱ km/h (یک خطای معیار) · ۳۸ (از سری خود فرق، r = ۰٫۲۲)؛ n مؤثر خطای IFS ۴۴ | همان، `ifs_minus_aifs_abs_error` |
| ارتفاع سکو · مهرآباد | ۲٬۳۲۵ · ۱٬۲۰۸ متر | S13، S16 |
| زمین مدل (سکو · مهرآباد) | IFS ۱٬۸۳۷ · ۱٬۴۴۳ · AIFS ۱٬۸۹۴ · ۱٬۵۶۰ · GFS ۱٬۸۴۸ · ۱٬۴۵۵ | S02، S04؛ `replay-2026-11-28.json` |
| روز تمرین ۰۸:۳۰: ۱۰ متری · سکو | ۰٫۸ · ۱۰٫۶ km/h (GFS) | `replay-2026-11-28.json` |
| روز تمرین ۱۴:۳۰: سقف گرمیک · بالای سکو · پایهٔ ابر · لایهٔ مرزی · w* | ۲٬۶۶۳ · ۳۳۸ · ۴٬۰۹۶ · ۲٬۸۰۳ متر · ۱٫۳ m/s | همان (GFS) |
| اولین سطح ECMWF بالای زمین مدل | ۷۰۰ hPa در حدود ۳٬۱۳۰ متر، ~۱٬۳۰۰ متر بالای زمین مدل | همان (IFS) |
| آستانه‌ها | ۱۹ / ۲۴ km/h باد، ۲۴ / ۲۹ تندباد، ۲۵° جهت، ۱٫۰ / ۲٫۵ m/s گرمیک | S20 (تبدیل در `--selftest`) |
| METAR: میانگین ۱۰ دقیقه، تندباد ۱۰ گره | — | S22 |
| پایهٔ ابر ۱۲۵ متر برای هر درجه · ۹٫۸ K/km | — | S24 |

## آنچه بیرون ماند

- **Open-Meteo** (پیش‌بینی، پیش‌بینی‌های گذشته، ERA5): مجوز API رایگان برای کانال درآمدزا مبهم است؛ لازم هم نشد.
- **ارزیابی بهار ۱۴۰۵ (آوریل ۲۰۲۶):** METAR ایران در IEM برای اسفند تا اوایل اردیبهشت ۱۴۰۵ تقریباً خالی است؛ علت را نمی‌دانیم و حدس نمی‌زنیم.
- **GFS در ارزیابی گذشته:** فایل‌های بایگانی GFS روی AWS بستهٔ پیچیده (template 5.3) دارند که رمزگشای ما ندارد؛ برای ارزیابی فقط IFS و AIFS آمد.
- **سایت‌های دیگر (توچال، کلکچال، شیراز، اصفهان):** مختصات سکوی تأییدشده پیدا نشد؛ ایستگاه ۷ توچال پیست اسکی است، نه سکوی ثبت‌شده. با باشگاه، در قسمت پیگیری.
- **آمار حادثهٔ پاراگلایدر در ایران:** منبع معتبر نداشتیم؛ در متن هیچ آمار حادثه نیست.
