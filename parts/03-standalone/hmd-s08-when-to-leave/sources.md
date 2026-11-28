# HMD-S08 · منابع

> همهٔ منابع ۲۸ نوامبر ۲۰۲۶ (۷ آذر ۱۴۰۵) باز و خوانده شدند، مگر جایی که نوشته شده. نقل‌قول‌ها کوتاه‌اند و فقط برای نقد و گزارش.
> برچسب‌ها: ✅ از متن منبع خوانده شد · 🔁 از منبع دست‌دوم (منبع اصلی باز نشد) · ⚠️ ابهام.

## منابع

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| S1 | NYC Taxi & Limousine Commission, *TLC Trip Record Data*, Yellow Taxi Trip Records, مارس و آوریل ۲۰۲۶ — https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page · فرهنگ داده (۱۸ مارس ۲۰۲۵): https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf | هر سفر: زمان روشن/خاموش شدن کنتور («when the meter was engaged/disengaged»)، منطقهٔ TLC، مسافت. فایل‌ها برای HMD-009 در ۲۶ نوامبر ۲۰۲۶ گرفته شدند؛ sha256 هر دو ۲۸ نوامبر دوباره وارسی شد (`artifact/derived/SOURCE.txt`). مجوز: دادهٔ عمومی شهر نیویورک (قانون دادهٔ باز NYC: بدون محدودیت استفاده؛ ذکر منبع). TLC: «makes no representations as to the accuracy of these data». | ✅ (از طریق HMD-009؛ هش‌ها امروز وارسی شد) |
| S2 | FHWA (Office of Operations; تهیه: Texas Transportation Institute با Cambridge Systematics), *Travel Time Reliability: Making It There On Time, All The Time*, دسامبر ۲۰۰۵ — https://ops.fhwa.dot.gov/publications/tt_reliability/TTR_Report.htm · بروشور FHWA-HOP-06-070: https://ops.fhwa.dot.gov/publications/tt_reliability/brochure/index.htm | شاخص بافر: «computed as the difference between the 95th percentile travel time and average travel time» تقسیم بر میانگین؛ شاخص زمان برنامه‌ریزی: «95th percentile travel time divided by the free-flow travel time»؛ مثال بروشور: میانگین ۲۰ دقیقه، بافر ۴۰٪ ← ۲۸ دقیقه؛ جریان آزاد ۱۵ و PTI ۱٫۶۰ ← ۲۴ دقیقه؛ «The one or two bad days each month mark the 95th or 90th percentile». فرمول‌ها در گزارش تصویرند؛ متن بالا از نثر خود گزارش است. | ✅ ⚠️ «زمان جریان آزاد» تعریف عددی ندارد (در مثال گزارش: سرعت ۶۰ مایل). جانشین ما: صدک ۵ همهٔ سفرهای آموزشی مسیر (۳۴٫۳ دقیقه برای JFK)؛ روی دک با ستاره. |
| S3 | Google Maps Platform, *Routes API · REST v2 · TrafficModel* — https://developers.google.com/maps/documentation/routes/reference/rest/v2/TrafficModel | BEST_GUESS: «the best estimate of travel time given what is known about both historical traffic conditions and live traffic»؛ «Live traffic becomes more important the closer the departureTime is to now»؛ PESSIMISTIC: «longer than the actual travel time on most days, though occasional days with particularly bad traffic conditions may exceed this value»؛ OPTIMISTIC: «shorter than the actual travel time on most days…»؛ فقط با `TRAFFIC_AWARE_OPTIMAL` و `DRIVE`. **صدک نام برده نشده.** | ✅ |
| S4 | Elena Kelareva (Product Manager, Google Maps APIs), «Predicting Future Travel Times with the Google Maps APIs», *Google Cloud Blog*, ۱۰ نوامبر ۲۰۱۵ — https://cloud.googleblog.com/2015/11/predicting-future-travel-times-with-the-Google-Maps-APIs.html | «Predictive travel time uses historical time-of-day and day-of-week traffic data to estimate travel times at a future date»؛ مثال‌ها: زمان‌بندی تحویل بار ← pessimistic؛ ترموستات خانه ← optimistic؛ best_guess «the most likely travel time considering both current traffic conditions and historical averages». | ✅ (HTML صفحه خوانده شد؛ کارت ایده تاریخ را ۱۱ نوامبر نوشته بود، صفحه ۱۰ نوامبر می‌گوید) ⚠️ بلاگ دربارهٔ پارامتر `traffic_model` در Directions/Distance Matrix API قدیمی است، نه Routes API؛ روی دوربین «یه بلاگ گوگل» گفته می‌شود، نه «مستند Routes API». |
| S5 | Google Maps Help, «Discover helpful features in Google Maps» — https://support.google.com/maps/answer/6291839 | «Set depart or arrive time»، «Depart at» / «Arrive by»؛ فقط برای یک مقصد و برای Driving و Transit؛ برآورد «is based on traffic and transit schedules for the planned travel time». **دربارهٔ بازهٔ «typically X–Y min» چیزی نمی‌گوید.** | ✅ |
| S6 | NYC Public Schools, *2025–2026 School Year Calendar* — https://schools.nyc.gov/calendar/2025-2026-school-year-calendar | «April 2–10 (Thursday–Friday): Spring Recess schools closed»؛ ۲۰ مارس: عید فطر، تعطیل. | ✅ |
| S7 | K. A. Small, «The Scheduling of Consumer Activities: Work Trips», *American Economic Review* 72(3) (1982) 467–479 | مدل «تأخیر زمان‌بندی»: هزینهٔ زود رسیدن و دیر رسیدن جدا و خطی، به‌اضافهٔ احتمالاً یک جریمهٔ ثابت برای دیر رسیدن. فقط در study-fa (فصل ۴). | 🔁 (از مدخل «Schedule delay» ویکی‌پدیا و چکیده‌ها؛ متن اصلی باز نشد) |
| S8 | مسئلهٔ روزنامه‌فروش و «کسر بحرانی» q* = c_u/(c_u + c_o) — نتیجهٔ استاندارد کتاب‌های پژوهش عملیاتی؛ صورت‌بندی کلاسیک: K. J. Arrow, T. Harris, J. Marschak, «Optimal Inventory Policy», *Econometrica* 19(3) (1951) | فرمول قاب ۸. ما به منبع تکیه نمی‌کنیم: `leave_live.py --selftest` روی ۹۹۷ عدد ساختگی و روی ۳۵۷ سفر واقعی ±۱۵ دقیقهٔ ۱۶:۴۵ نشان می‌دهد کمینهٔ هزینهٔ تجربی همان صدک q است (۴ نسبت). | 🔁 (مقالهٔ ۱۹۵۱ باز نشد) |
| S9 | HMD-009 (همین مخزن)، `parts/03-standalone/hmd-009-maps-eta/` | همان دادهٔ خام و همان پالایش مسیر JFK؛ جداسازی ۱۳ آوریل. `--selftest` وارسی می‌کند سطرهای JFK ما دقیقاً سطرهای روز کاری فایل HMD-009 است. | ✅ |

## چیزی که دنبالش گشتیم و پیدا نکردیم

- **معنای بازهٔ «typically X–Y min» در اپ Google Maps:** در راهنمای رسمی (S5) و مستند API (S3) چیزی نیست. فقط یک مقالهٔ دست‌دوم (How-To Geek، بازنشر در Yahoo) می‌گوید اپ «how long it typically takes» را نشان می‌دهد. **پس در قسمت هیچ ادعایی دربارهٔ صدکِ این بازه نمی‌کنیم.** اگر محمد روی گوشی‌اش آن را دید، فقط نشانش می‌دهد.
- **صدکی که Google برای «pessimistic» به کار می‌برد:** منتشر نشده.

## دادهٔ واقعی و محاسبهٔ خودمان (`artifact/leave_live.py --report`، ۲۸ نوامبر ۲۰۲۶)

همهٔ عددهای زیر در `artifact/derived/episode_numbers.json` هستند و `--selftest` آن‌ها را دوباره می‌سازد.

- **داده:** ۳۰٬۷۵۰ سفر روز کاری، ۲ مارس تا ۳۰ آوریل ۲۰۲۶: JFK ۸٬۵۰۹ · لاگواردیا ۱۵٬۰۵۴ · نیوآرک ۳٬۴۳۷ · آپر ایست ساید ← محلهٔ مالی ۳٬۷۵۰ (پالایش: `SOURCE.txt`).
- **جداسازی:** آموزش ۳۰ روز کاری (۲ مارس تا ۱۰ آوریل)؛ آزمون ۱۴ روز کاری (۱۳ تا ۳۰ آوریل)؛ همان روز جداسازی HMD-009.
- **مدل:** «سفر تو» = سفرهای روزهای آموزش که ±۱۵ دقیقه از ساعت حرکت تو راه افتادند. صدک با درون‌یابی خطی (روش inclusive، همان numpy/Excel). ساعت پیشنهادی = دیرترین زمان روی شبکهٔ ۵ دقیقه‌ای که «زمان + صدک c» از مهلت نگذرد (حداکثر ۴ ساعت عقب؛ دست‌کم ۲۰ سفر در پنجره).
- **قهرمان (JFK، مهلت ۱۸:۰۰):**

| چیز | عدد |
|---|---:|
| سفرهای ±۱۵ دقیقهٔ ۱۶:۴۵ (آموزش) | ۲۳۴ |
| میانگین / میانه / صدک ۵ / صدک ۹۵ (دقیقه) | ۷۴٫۸ / ۷۴٫۲ / ۵۲٫۱ / ۹۹٫۷ |
| سهم به‌موقع با حرکت ۱۶:۰۰ / ۱۶:۱۵ / ۱۶:۲۰ / ۱۶:۳۰ / ۱۶:۴۵ (آموزش) | ۱۰۰٪ / ۹۹٫۳٪ / ۹۶٫۸٪ / ۸۶٫۹٪ / ۵۲٫۱٪ |
| ساعت حرکت: قاعدهٔ میانگین / ۵۰٪ / ۹۰٪ / ۹۵٪ | ۱۶:۴۵ / ۱۶:۴۵ / ۱۶:۲۵ / ۱۶:۲۰ |
| بک‌تست (±۱۰ دقیقه، ۱۴ روز آزمون): قاعدهٔ میانگین | ۷۲٫۷٪ دیر (۵۶ از ۷۷)، هر ۱۴ روز دست‌کم یک سفر دیر |
| بک‌تست: قاعدهٔ ۹۵٪ | ۸٫۳٪ دیر (۹ از ۱۰۸)، ۵ روز از ۱۴ |
| میانهٔ ساعت ۱۳:۰۰ | ۵۹٫۶ |
| صدک ۹۵: حرکت ۱۶:۰۰ ← ۹۲٫۸ (رسیدن ۱۷:۳۳)؛ ۱۶:۳۰ ← ۹۹٫۴ (۱۸:۰۹)؛ ۱۷:۳۰ ← رسیدن ۱۹:۰۳؛ ۱۸:۳۰ ← ۱۹:۴۰ | |
| شاخص بافر ۱۶:۴۵ / شاخص زمان برنامه‌ریزی / جانشین جریان آزاد | ۰٫۳۳ / ۲٫۹۱ / ۳۴٫۳ دقیقه |

- **کالیبراسیون (۳۱ مهلت، ۰۷:۰۰ تا ۲۲:۰۰ هر نیم ساعت؛ سهم سفرهای دیر روی همهٔ مهلت‌ها با هم):**

| مسیر | قاعدهٔ ۹۵٪ | قاعدهٔ میانگین |
|---|---:|---:|
| JFK | ۱۱٫۰٪ | ۶۴٫۹٪ |
| لاگواردیا | ۳٫۷٪ | ۳۲٫۸٪ |
| نیوآرک | ۵٫۱٪ | ۳۳٫۱٪ |
| محلهٔ مالی | ۶٫۱٪ | ۳۵٫۹٪ |

  سفرها بین مهلت‌های نزدیک هم‌پوشانی دارند؛ این ۳۱ آزمون مستقل نیستند. قاعدهٔ میانگین زیر ۵۰٪ است به دو دلیل (بازبینی مستقل، ۲۸ نوامبر): (۱) گرد شدن به سمت زودتر روی شبکهٔ ۵ دقیقه‌ای، به‌اضافهٔ پنجره‌های کم‌سفر (کمتر از ۲۰) که رد می‌شوند، به‌طور میانگین ۲ تا ۱۱ دقیقه حاشیهٔ اضافه روی میانگین می‌گذارد (JFK ۲٫۰، محلهٔ مالی ۲٫۵، لاگواردیا ۷٫۲، نیوآرک ۱۰٫۷)؛ (۲) توزیع کمی چوله به راست است: در پنجره‌های انتخاب‌شده فقط ۴۲ تا ۴۷٪ سفرها از میانگین بلندترند. این دو عدد در `episode_numbers.json` نیستند و `--selftest` آن‌ها را نمی‌سازد.
- **چرا JFK لغزید؟** میانهٔ سفرهای حرکت ۱۵:۰۰ تا ۱۸:۰۰: آموزش ۷۱٫۲، آزمون ۸۳٫۲. میانهٔ هفتگی (دوشنبهٔ هفته): ۲ مارس ۷۹٫۱ · ۹ مارس ۷۹٫۴ · ۱۶ مارس ۷۴٫۹ · ۲۳ مارس ۷۰٫۸ · **۳۰ مارس ۶۳٫۳ · ۶ آوریل ۵۶٫۲** · ۱۳ آوریل ۸۵٫۹ · ۲۰ آوریل ۸۱٫۹ · ۲۷ آوریل ۷۹٫۲. دو هفتهٔ خلوت با تعطیلی بهارهٔ مدرسه‌ها (S6، ۲ تا ۱۰ آوریل) هم‌زمان است؛ ولی وقتی روزهای ۲ تا ۱۰ آوریل را از آموزش برداشتیم، دیرِ قاعدهٔ ۹۵٪ فقط از ۱۱٫۰٪ به ۱۰٫۳٪ رسید. **علت را ثابت نکرده‌ایم.** این حذف بعد از دیدن آزمون انتخاب شد؛ آزمون منصفانه نیست و فقط برای فهم است.
