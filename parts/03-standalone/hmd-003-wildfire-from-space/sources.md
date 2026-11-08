# HMD-003 · منابع

بازبینی: ۲ نوامبر ۲۰۲۶. شناسه‌های Rxx از `private/planning/production-v3/references.json`؛ منابع W از جست‌وجوی همین نوبت.

| شناسه | منبع | لینک | بازبینی | در این قسمت برای |
|---|---|---|---|---|
| R13 | NASA FIRMS | https://firms.modaps.eosdis.nasa.gov/ | references.json؛ صفحهٔ API در ۲ نوامبر ۲۰۲۶ خوانده شد | منبع اصلی داده؛ VIIRS 375 m و MODIS 1 km · قاب ۳، ۴، ۸، ۹ |
| R13-api | FIRMS area API | https://firms.modaps.eosdis.nasa.gov/api/area/ | ۲ نوامبر ۲۰۲۶ | الگوی URL `/api/area/csv/[MAP_KEY]/[SOURCE]/[W,S,E,N]/[DAY_RANGE]/[DATE]`؛ DAY_RANGE 1..5؛ منابع `VIIRS_SNPP_SP/NRT`، `VIIRS_NOAA20_*`، `VIIRS_NOAA21_*`، `MODIS_*`؛ MAP_KEY رایگان؛ ۵٬۰۰۰ تراکنش در ۱۰ دقیقه · artifact |
| R13-notes | FIRMS Fire Alerts: Important Notes | https://firms.modaps.eosdis.nasa.gov/alerts/notes.php | ۲ نوامبر ۲۰۲۶ | دلایل ندیده‌شدن آتش: «started and ended between satellite overpasses»، «cloud cover, heavy smoke, or tree canopy»؛ VIIRS 375 m پاسخ بهتر به آتش کوچک نسبت به MODIS 1 km · قاب ۹ |
| R13-attr | FIRMS VIIRS attribute descriptions (از راه آینه‌ها و راهنمای کاربر) | https://www.earthdata.nasa.gov/sites/default/files/imported/VIIRS_activefire_User_Guide.pdf | ۲ نوامبر ۲۰۲۶ (صفحهٔ اصلی Earthdata به ابزار خودکار 403 داد) | مختصات = مرکز پیکسل؛ confidence l/n/h؛ نقطه‌های کم‌اطمینان روزانه معمولاً با بازتاب خورشید (sun glint)؛ ستون type (0 گیاهی، 1 آتشفشان، 2 منبع ثابت خشکی، 3 دریایی)؛ FRP به مگاوات · قاب ۴، ۶، ۷. ✔ ۷ نوامبر ۲۰۲۶ با صفحهٔ محصول NASA MODAPS تأیید شد (پایین) |
| R12 | Earth Fire Alliance & Muon Space · first light and first active fire images from operational FireSat | https://earthfirealliance.org/news-article/earth-fire-alliance-and-muon-space-release-first-light-and-first-active-fire-images-from-operational-firesat-constellation/ | ۲ نوامبر ۲۰۲۶ | ۱۶ سپتامبر ۲۰۲۶؛ سه ماهواره، رسیدن به مدار ۷ ژوئیهٔ ۲۰۲۶؛ first light حدود سه هفته بعد بر فراز Dubbo؛ یک hotspot در Porto؛ Big Grass Fire (اورگان–آیداهو) پنج بار در سه شب و دو روز؛ MWIR تا ۵×۵ متر («دو جای پارک»)؛ دادهٔ عملیاتی دست‌کم دو بار در روز تا پایان ۲۰۲۶؛ دسترسی جهانی ۲۰۲۸؛ بازدید ساعتی ۲۰۲۹؛ ۲۰ دقیقه اوایل دههٔ ۲۰۳۰ · قاب ۱۰، ۱۲. این صفحه از AI نام نمی‌برد. |
| W1 | Google · *A breakthrough in wildfire detection* · 16 Sep 2024 | https://blog.google/outreach-initiatives/sustainability/google-ai-wildfire-detection/ | ۲ نوامبر ۲۰۲۶ | نقش AI: «rapidly compare any 5x5 meter spot on earth with previous imagery» + زیرساخت اطراف و هوای محلی؛ تصاویر فعلی «low resolution or only updated a few times a day» · قاب ۳، ۱۱ |
| W2 | Iran International · Hyrcanian forest fires · 17 Nov 2025 | https://www.iranintl.com/en/202511174535 | ۲ نوامبر ۲۰۲۶ | منطقهٔ الیت نزدیک مرزن‌آباد، چالوس؛ «for over two weeks» تا ۱۷ نوامبر؛ شعله‌ورشدن دوباره پس از مهار (این گزارش ۱۷ نوامبر منتشر شده؛ تاریخِ ملاکِ شعله‌ورشدن دوباره ۲۴ آبان = ۱۵ نوامبر است، طبق بازبینی ۷ نوامبر ۲۰۲۶ در همین فایل)؛ شیب تند و صخره‌ای · قاب ۱، ۸ |
| W3 | IQAir · Wildfire Map Spotlight: Hyrcanian Forest Fire, Iran | https://www.iqair.com/newsroom/wildfire-map-spotlight-hyrcanian-forest-fire-iran | ۲ نوامبر ۲۰۲۶ | UNESCO-listed؛ «By November 25, 2025, Iranian authorities confirmed the fire was fully contained» · دک قاب ۱ |

## محاسبه‌شده توسط ما

- ۳۷۵ × ۳۷۵ = ۱۴۰٬۶۲۵ مترمربع ≈ ۱۴ هکتار؛ یک زمین فوتبال استاندارد حدود ۱۰۵ × ۶۸ = ۷٬۱۴۰ مترمربع ⇒ حدود ۲۰ زمین (قاب ۳). اندازهٔ پیکسل با کوچک‌ترین آتش قابل‌تشخیص یکی نیست؛ متن این را می‌گوید.
- خروجی `firms_timeline.py --demo` (۲ نوامبر ۲۰۲۶) روی دادهٔ ILLUSTRATIVE: ۱۸ ردیف؛ آستانهٔ low/nominal/high → ۱۸/۱۵/۷؛ اولین نقطهٔ نگه‌داشته = SITE-A (علامت‌خورده)؛ در حالت low، نقطهٔ ضعیف محل آتش حدود ۱۲ ساعت پیش از اولین نقطهٔ nominal (قاب ۵، ۷).
- برآوردهای مساحت الیت: ۱۵۰ تا ۱۸۰ ÷ ۸ ≈ ۱۹ تا ۲۲ ⇒ «حدود بیست برابر» (قاب ۸، دک `~20×`).
- تبدیل تاریخ: ۱۷ نوامبر ۲۰۲۵ = ۲۶ آبان ۱۴۰۴؛ ۲۸ اکتبر ۲۰۲۵ = ۶ آبان؛ ۲۷ نوامبر ۲۰۲۵ = ۶ آذر.

## اجرا نشده / نیازمند تأیید

- **اجرای FIRMS:** اختیاری، برای ویدیوی کوتاه پیگیری. عددی از آن در متن نیست.
- **تاریخ آتش (تأیید ۷ نوامبر ۲۰۲۶):** ۱۰ آبان ۱۴۰۴ (۱ نوامبر ۲۰۲۵)، شعله‌ورشدن دوباره ۲۴ آبان (۱۵ نوامبر). [ایران‌اینترنشنال، ۶ آذر ۱۴۰۴](https://www.iranintl.com/fa/202511276713): آتش «در ۱۰ و ۲۴ آبان». تاریخ ۳۱ اکتبر فقط در چند منبع انگلیسی ثانویه است.
- **محدودهٔ `elit`:** اصلاح‌شده به (50.95, 36.20, 51.45, 36.55). روستای الیت 36.3228N، 51.1119E، دهستان کوهستان، بخش مرزن‌آباد، شهرستان چالوس ([Wikipedia](https://en.wikipedia.org/wiki/Elit,_Iran)). کجور (~36.38N، 51.72E) بیرون محدوده است.
- **مساحت سوخته (قاب ۸):** برآوردهای رسمی ناهمخوان‌اند: معاون وزیر جهاد کشاورزی و استاندار حدود ۸ هکتار؛ منابع طبیعی حدود ۱۰ هکتار (انتخاب، ایران‌اینترنشنال)؛ معاون سازمان حفاظت محیط زیست ۱۵۰ تا ۱۸۰ هکتار (به نقل snn.ir و انتخاب). IFRC DREF: «دست‌کم ۱۰ تا ۱۵ هکتار». ادعای «بیش از ۶۰۰ هکتار» (fireriskheritage.net) بی‌منبع است و در متن نیامده.
- **ستون‌های FIRMS:** [NASA MODAPS، VNP14IMGTDL_NRT](https://modaps.modaps.eosdis.nasa.gov/services/about/products/viirs-land-c2-nrt/vnp14imgtdl_nrt.html): مختصات = «Center of nominal 375 m fire pixel»؛ نقطه‌های کم‌اطمینان روزانه «typically associated with areas of Sun glint»؛ ستون type (۰ آتش گیاهی، ۱ آتشفشان، ۲ منبع ثابت، ۳ دریا) فقط در محصول استاندارد.

## آنچه عمداً استفاده نشد

- عبارت «پیش از آنکه کسی متوجه شود» (و نسخهٔ intro کانال)؛ ادعایی است که دادهٔ ما ثابت نمی‌کند.
- «۵۰+ ماهواره» و «۱۳ میلیون دلار» از گزارش‌های ثانویهٔ ۲۰۲۴؛ صفحهٔ R12 تعداد نهایی را نمی‌گوید.
- precision/recall یا هر درصد دقتی برای VIIRS در ایران.
