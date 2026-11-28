# HMD-S06 · منابع

> همهٔ منابع ۲۸ نوامبر ۲۰۲۶ (۷ آذر ۱۴۰۵) باز و خوانده یا آزموده شدند، مگر جایی که نوشته شده. هیچ API پولی، ورود یا دیوار پرداختی استفاده نشد.
> برچسب‌ها: ✅ از متن منبع خوانده یا با دادهٔ خودش آزموده شد · 🔁 از منبع دیگری نقل شده (منبع اصلی باز نشد) · ⚠️ اختلاف یا ابهام · `[VERIFY]` پیش از ضبط دوباره ببین.

## داده و مجوز

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| S01 | ECMWF, «Open data» — https://www.ecmwf.int/en/forecasts/datasets/open-data | مجوز CC BY 4.0 و اجازهٔ استفادهٔ تجاری با ذکر منبع؛ IFS (۰٫۲۵ درجه و از ۲۰ اکتبر ۲۰۲۶ ۰٫۱ درجه)، AIFS Single و AIFS ENS؛ نگه‌داری فقط ۱۲ اجرای آخر (۲ تا ۳ روز)؛ محدودیت اتصال هم‌زمان | ✅ |
| S01b | ECMWF, Terms of use / licence — https://apps.ecmwf.int/datasets/licences/general/ | متن اعتبار لازم: «© 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)»، منبع www.ecmwf.int، جملهٔ مجوز CC BY 4.0، سلب مسئولیت، و **اعلام تغییر** («پردازش هومودین») | ✅ |
| S02 | ECMWF IFS 0.25° oper، اجرای 00Z ۲۸ نوامبر ۲۰۲۶، فایل‌های `20261128000000-<step>h-oper-fc.grib2` و `.index` در data.ecmwf.int | ارتفاع زمین مدل زیر قله ۲٬۸۰۶ متر (بارگاه سوم ۲٬۷۷۵)؛ همهٔ عددهای IFS متن؛ بستهٔ CCSDS (template 5.42)، پشتیبانی از چند بازهٔ بایت در یک درخواست | ✅ (آزمون مستقیم؛ `artifact/derived/SOURCE.txt`) |
| S03 | ECMWF AIFS Single 0.25°، همان اجرا، `aifs-single/0p25/oper` | زمین مدل ۲٬۷۲۷ متر؛ عددهای AIFS؛ `tp` به kg m⁻² (نه متر) | ✅ |
| S04 | NOAA/NCEP NOMADS, GFS 0.25° grib filter — https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl ؛ مالکیت عمومی: https://www.weather.gov/disclaimer («in the public domain… may be used without charge for any lawful purpose») | زمین مدل ۲٬۷۳۳ متر؛ عددهای GFS؛ زیرناحیهٔ ۲×۲ درجه با بستهٔ ساده (template 5.0) | ✅ |
| S05 | Open-Meteo, Terms — https://open-meteo.com/en/terms ؛ Docs — https://open-meteo.com/en/docs | «You may only use the free API services for non-commercial purposes»؛ فهرست غیرتجاری شامل «Use in educational content» است و فهرست تجاری شامل «Websites or apps that have subscriptions or display advertisements»؛ از YouTube نام نمی‌برد، پس کانال درآمدزا **مبهم** است (ما محتاطانه تجاری فرض کردیم)؛ دادهٔ رایگان CC BY 4.0؛ ۱۰٬۰۰۰ فراخوان در روز. Docs: `elevation` برای «statistical downscaling»، پیش‌فرض DEM نود متری، `elevation=nan` یعنی ارتفاع میانگین خانه؛ نمی‌گوید کدام متغیرها پایین‌مقیاس می‌شوند (آزمون ما: فقط دمای ۲ متری، با ۶٫۵ K/km؛ باد و تندباد دست‌نخورده؛ `study-fa.md` فصل ۴) | ✅ ⚠️ **تصمیم مجوز با محمد** |
| S06 | Open-Meteo forecast و ensemble API، ۲۸ نوامبر ۲۰۲۶ ساعت 08:50Z (فرمان‌ها در `artifact/summit_fetch.py`) | تندباد ۱۰ متری بیشینهٔ ۷۲ ساعت با elevation=5610: GFS ۱۴٫۴، IFS ۵۶٫۵، ICON ۹۹٫۴ km/h (نسبت ۶٫۹)؛ ارتفاع خانه ۳٬۳۵۴ متر؛ ECMWF ENS پنجاه‌ویک عضو؛ GEFS و ICON-EPS در سطح‌های فشار تهی | ✅ (`artifact/derived/openmeteo-summary-2026-11-28.json`) |
| S06b | کارت ۳ بانک ایده (۲۷ نوامبر ۲۰۲۶)، همان درخواست Open-Meteo | آن روز: ۳۵٫۶، ۱۲٫۶، ۶۸٫۴ km/h (نسبت حدود ۵٫۴) | 🔁 (داخلی؛ فقط برای مقایسه) |

## فیزیک و آستانه‌ها

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| S07 | Environment and Climate Change Canada, «Wind chill and the Wind Chill Index» — https://www.canada.ca/en/services/environment/weather/severeweather/wind-chill-index.html | چارت: −۲۰ °C در ۲۰/۴۰/۶۰ km/h ← −۳۰/−۳۴/−۳۶؛ −۳۰ °C ← −۴۳/−۴۸/−۵۰. نوارها: −۲۸ تا −۳۹ «خطر بالا، ۱۰ تا ۳۰ دقیقه»؛ −۴۰ تا −۴۷ «۵ تا ۱۰ دقیقه»؛ −۴۸ تا −۵۴ «۲ تا ۵»؛ ≤ −۵۵ «کمتر از ۲». باد بالای ۵۰ km/h یخ‌زدگی را سریع‌تر می‌کند. شرط: دما ≤ ۰ و باد ≥ ۵ km/h | ✅ (فرمول در این صفحه نیست) |
| S08 | NWS, «Wind Chill Chart» — https://www.weather.gov/safety/cold-wind-chill-chart | «Wind chill (ºF) = 35.74 + 0.6215T − 35.75(V^0.16) + 0.4275T(V^0.16)»؛ باد در ارتفاع ۳۳ فوت اندازه‌گیری و به ارتفاع صورت (۵ فوت) برده می‌شود | ✅ (سال ۲۰۰۱ در این صفحه نیامده) |
| S09 | Osczevski, R. & Bluestein, M., «The new wind chill equivalent temperature chart», *BAMS* 86 (2005) 1453–1458 | منشأ فرمول ۲۰۰۱ (کانادا و آمریکا) و شکل متریک `13.12 + 0.6215T − 11.37V^0.16 + 0.3965TV^0.16` | 🔁 `[VERIFY]` (متن مقاله باز نشد؛ شکل متریک با S07 و S08 در `--selftest` وارسی شد) |
| S12 | ICAO, *Manual of the ICAO Standard Atmosphere* (Doc 7488) | T₀ = 288.15 K، p₀ = 1013.25 hPa، افت ۶٫۵ K/km؛ ارتفاع ۵۰۰/۶۰۰/۷۰۰ hPa = ۵٬۵۷۴/۴٬۲۰۶/۳٬۰۱۲ متر (حساب خودمان، `--selftest`) | 🔁 (ثابت‌های استاندارد) |
| S15 | Asiri, Almazroui & Awad, «Synoptic features associated with the winter variability of the subtropical jet stream over Africa and the Middle East», *Meteorol. Atmos. Phys.* (2020) — https://link.springer.com/10.1007/s00703-019-00722-4 | جت جنب‌حاره‌ای زمستان بیش از ۸۷٪ مواقع در ۲۰۰ هکتوپاسکال، بیشتر بین ۲۰ و ۳۵ درجهٔ شمالی | 🔁 (فقط چکیده از طریق جست‌وجو) `[VERIFY]` |

## مکان‌ها

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| S10 | Wikipedia, «Mount Damavand» — https://en.wikipedia.org/wiki/Mount_Damavand | ۵٬۶۱۰ متر (با برچسب «disputed»؛ نقشه‌های دیگر ۵٬۵۹۸، ۵٬۶۲۶ و ۵٬۶۲۸)؛ مختصات 35°57′04″N 52°06′32″E؛ «Bargah Sevom Camp/Shelter» ۴٬۲۲۰ متر | ✅ ⚠️ ارتفاع مورد اختلاف است؛ ما ۵٬۶۱۰ را (رقم رایج ایرانی) به کار می‌بریم |
| S11 | damawand.de (سایت یک گروه راهنمای تجاری), «Damavand GPS Waypoints» — https://www.damawand.de/Info-Tech/GPS.html | قله 35-57-19 N، 52-06-37 E (GPS ۵٬۶۲۱ تا ۵٬۶۴۵)؛ پناهگاه قدیم بارگاه سوم 35-55-54 N، 52-06-30 E، ۴٬۲۲۰ متر؛ پناهگاه نو ۴٬۲۵۰ متر؛ خودش می‌گوید GPS دستی دقیق نیست | ✅ مختصات دمو (35.9553, 52.1100 و 35.9317, 52.1083) از همین‌جاست؛ با S11b چک شد |
| S11b | OpenStreetMap (Overpass API، ۲۸ نوامبر ۲۰۲۶؛ © OpenStreetMap contributors، ODbL) | قله: node 25944923 «دماوند»، 35.95437 N، 52.11034 E، ele 5609 (حدود ۱۰۰ متر جنوب نقطهٔ دمو)؛ بارگاه سوم پناهگاه نو: way 307642862، 35.93141 N، 52.10894 E، ele 4240؛ پناهگاه قدیم: way 355536739، 35.93047 N، 52.10852 E، ele 4200 (نقطهٔ دمو حدود ۶۰ متر با پناهگاه نو فاصله دارد) | ✅ اختلاف‌ها در برابر خانهٔ ۲۵ کیلومتری بی‌اثرند؛ GPS گروه اختیاری |

## دادهٔ مشاهده‌ای (آنچه نیست)

| شناسه | منبع | نتیجهٔ آزمون ۲۸ نوامبر ۲۰۲۶ | وضعیت |
|---|---|---|---|
| S13 | Iowa Environmental Mesonet, ASOS/METAR archive — `mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=OIII…` ؛ aviationweather.gov `api/data/metar?ids=OIII,OIIE,OINR,OINZ,OIFM` | آخرین METAR مهرآباد در بایگانی: **۱۴ نوامبر ۲۰۲۶، 15:30 UTC**؛ API زندهٔ aviationweather برای پنج فرودگاه ایران: HTTP 204 (خالی) | ✅ |
| S14 | سازمان هواشناسی کشور — https://www.irimo.ir و https://data.irimo.ir | از بیرون ایران: اتصال پس از ۲۰ ثانیه قطع شد (۲۸ نوامبر، همان نتیجهٔ کارت ۲۷ نوامبر) | ✅ (آزمون دسترسی) — **از داخل ایران آزموده نشد** |
| — | ایستگاه عمومی روی قله یا در بارگاه سوم | در منابع بالا و کارت ایده پیدا نشد | ⚠️ «پیدا نکردیم»، نه «وجود ندارد» |

## روش و کد

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| S16 | CCSDS 121.0-B, «Lossless Data Compression» (Blue Book) — https://public.ccsds.org/Pubs/121x0b3.pdf ؛ libaec (DKRZ) — https://gitlab.dkrz.de/k202009/libaec | الگوریتم رمزگشای `artifact/grib2_point.py`: گزینه‌های zero-block، second-extension، split-sample و uncompressed، پیش‌پردازندهٔ تأخیر واحد | 🔁 (از دانستهٔ عمومی پیاده شد؛ درستی با رفت‌وبرگشت مصنوعی و توافق IFS–GFS در `--selftest` وارسی شد) |
| S17 | WMO, *Manual on Codes*, GRIB2 templates 3.0, 4.0, 5.0, 5.42 | ساختار بخش‌ها | 🔁 |

## عددهای متن و جایشان

| عدد در متن | مقدار | از کجا |
|---|---|---|
| تندباد سه مدل (قاب ۱) | ۱۴ / ۵۷ / ۹۹ km/h، حدود ۷ برابر | S06 |
| سطح ۵۰۰ hPa: جو استاندارد / بالای دماوند | ۵٬۵۷۴ / ۵٬۷۵۸ متر (شنبه 15:30 تهران، IFS) | S12، S02 |
| زمین مدل زیر قله | IFS ۲٬۸۰۶، AIFS ۲٬۷۲۷، GFS ۲٬۷۳۳ متر | S02–S04 |
| سه دما، شنبه 15:30 تهران (IFS) | +۵٫۶ / −۱۲٫۶ / −۱۵٫۰ °C | S02، `artifact` |
| باد زمین مدل / هوای آزاد، همان ساعت | ۳ / ۴۶ km/h | S02 |
| سرمای باد قله، همان ساعت | −۲۸٫۱ °C | S02 + فرمول S07–S09 |
| مثال سرمای باد | −۲۰ °C و ۴۰ km/h ← −۳۴ | S07 |
| بیشینهٔ باد هوای آزاد ۷۲ ساعت | GFS ۵۴٫۷، AIFS ۶۴٫۳، ICON ۶۵٫۴، IFS ۶۷٫۷ km/h؛ نسبت ۱٫۲۴ | S02–S04، S06 |
| یکشنبه 03:30 تهران | IFS ۳۹٫۶، AIFS ۳۹٫۱، GFS ۳۴٫۷، ICON ۴۲٫۴؛ ENS ۲۸ از ۵۱ ≥ ۴۰ (۵۵٪) | S02–S04، S06 |
| دوشنبه 15:30 تهران | سه مدل از چهار ≥ ۶۰ km/h؛ ENS ۳۰ از ۵۱ ≥ ۶۰ | همان |
| پنجرهٔ آرام‌تر بارگاه سوم | شنبه 03:30 تا یکشنبه 21:30 تهران؛ قله: هیچ | `artifact` |
| بارگاه سوم پایین‌تر از قله | حدود ۱٬۴۰۰ متر (۵٬۶۱۰ − ۴٬۲۲۰) | S10، S11 |
| جت جنب‌حاره‌ای | حدود ۲۰۰ hPa، یعنی حدود ۱۲ کیلومتر (جو استاندارد: ۱۱٫۸) | S15، S12 |

## بیرون ماند

- «هر سال هزاران کوهنورد» (کارت ایده): منبع شمارش رسمی پیدا نکردیم؛ در متن «خیلی از کوهنوردها» آمده.
- «ERA5 قلهٔ دماوند را ۵٬۴۷۳ متر می‌بیند» (`docs/host-study-standard.md` §۷، نمونهٔ فصل ۶): با دادهٔ ما نمی‌خواند؛ هر مدل ۰٫۲۵ درجه‌ای که آزمودیم زمین زیر قله را حدود ۲٬۷۰۰ تا ۲٬۸۰۰ متر می‌بیند. ERA5 را نیازمودیم (حساب CDS لازم است)؛ این جمله را به کار نبرید تا آزموده شود.
- مقایسه با سرویس‌های تجاری قله (Mountain-Forecast و…): روششان را از منبع اصلی نخواندیم؛ نام برده نمی‌شوند.
- ECMWF ENS مستقیم از open data: هر گام حدود ۶۰ مگابایت فقط برای باد ۵۰۰ هکتوپاسکال؛ برای دمو سنگین است. در طرح سرویس هست، اجرا نشد.
