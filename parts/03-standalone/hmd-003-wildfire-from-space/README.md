# HMD-003 · Silent Breakthrough · v5

## می‌شود آتش جنگل را وقتی هنوز کوچک است پیدا کرد؟

**وضعیت:** آمادهٔ ضبط (۲۳ نوامبر ۲۰۲۶). قاب ۸ حالا خط زمانی واقعی ماهواره‌ای آتش الیت را دارد (دادهٔ سالانهٔ FIRMS، بی‌نیاز به کلید). عکس‌ها و فیلم حرارتی واقعی آتش الیت (مهر، CC BY 4.0) و دو عکس آزاد برای قاب ۶ در `media/` هستند.
**قالب:** Silent Breakthrough (مستقل) · **زمان برآوردی:** ۱۳ تا ۱۴ دقیقه · **واژهٔ گفتاری:** ۱۶۴۸ · **قاب:** ۱۵
**هوک:** Story-Open — «آبان پارسال، جنگل‌های الیت، نزدیک مرزن‌آباد…»

**جملهٔ مرکزی:** یک نقطهٔ داغ از فضا سرنخ است، نه حکم؛ پیدا کردن آتش کوچک یعنی حسگر ریزتر، نگاه مکرر، و جدا کردن داغی‌هایی که آتش نیستند.

**مرز ادعا:** نقشهٔ ما دادهٔ VIIRS از NASA FIRMS است، نه FireSat. نقطهٔ داغ همیشه آتش جنگل نیست. بدون فهرست زمینی معتبر، precision/recall اعلام نمی‌شود. نمی‌گوییم ماهواره آتش الیت را زودتر از مردم دید، و نمی‌گوییم FireSat امروز بالای ایران کار می‌کند.

**زنجیره:** از HMD-002 («از نمرهٔ مدل‌ها به یک تشخیص واقعی») ← این قسمت ← HMD-004 («تشخیص درست به سنجه بستگی دارد؛ جدول رتبه‌بندی هم»).

## فایل‌ها

| فایل | چیست |
|---|---|
| [script-fa.md](script-fa.md) | متن ضبط v5، ۱۵ قاب، شاخهٔ B برای قاب ۸، لاگ و نقشهٔ ریسک |
| [hooks-fa.md](hooks-fa.md) | پنج هوک + توصیه |
| [package-fa.md](package-fa.md) | بستهٔ انتشار کامل |
| [`deck-fa.html`](deck-fa.html) | دک ضبط v6، فارسی و راست‌به‌چپ: کاور + ۱۵ قاب (→ ← · F · H · N) |
| [`deck-en.html`](deck-en.html) | همان دک به انگلیسی، با همان قاب‌ها و همان ترتیب |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ هر دو دک؛ بعد از ویرایش `make decks` |
| [sources.md](sources.md) | منابع، تاریخ بازبینی، محاسبه‌ها |
| [artifact/firms_timeline.py](artifact/firms_timeline.py) | خواندن/دانلود FIRMS، فیلتر اطمینان، علامت نزدیکی به محل صنعتی و تکرار، خط زمانی (فقط stdlib) |
| [artifact/README.md](artifact/README.md) | اجرای آفلاین، گرفتن MAP_KEY، منطقه‌ها، معنی علامت‌ها |
| [artifact/sample_firms_ILLUSTRATIVE.csv](artifact/sample_firms_ILLUSTRATIVE.csv) | ۱۸ ردیف ساختگی با ستون‌های FIRMS VIIRS |
| [artifact/sites_ILLUSTRATIVE.csv](artifact/sites_ILLUSTRATIVE.csv) | یک محل صنعتی فرضی (SITE-A) |
| [artifact/derived/elit_viirs_2025.csv](artifact/derived/elit_viirs_2025.csv) | همهٔ ۸۳ نقطهٔ داغ VIIRS سال ۲۰۲۵ در محدودهٔ الیت (FIRMS، پردازش استاندارد)؛ منبع و SHA-256 در `SOURCE.txt` |
| [media/CREDITS.md](media/CREDITS.md) | عکس و فیلم آماده برای تدوین، با مجوز و متن اعتبار هر کدام |

## پیش از ضبط (همهٔ موارد باز)

- [x] خط زمانی واقعی FIRMS برای الیت اجرا شد (۲۳ نوامبر ۲۰۲۶) و در قاب ۸ متن و دک نشست. ضبط ترمینال قاب ۸:
  `python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --csv parts/03-standalone/hmd-003-wildfire-from-space/artifact/derived/elit_viirs_2025.csv --region elit --start 2025-10-28 --end 2025-11-27 --quiet`
- [x] محدودهٔ `elit` اصلاح شد: (50.95, 36.20, 51.45, 36.55). منبع: مختصات روستای الیت 36.32N 51.11E.
- [x] تاریخ آتش تأیید شد: ۱۰ آبان ۱۴۰۴ (۱ نوامبر ۲۰۲۵) و شعله‌ورشدن دوباره ۲۴ آبان (۱۵ نوامبر). متن هر دو را می‌گوید.
- [x] تعریف ستون‌ها از صفحهٔ محصول NASA MODAPS تأیید شد (مرکز پیکسل ۳۷۵ متری، sun glint، type). نکته: ستون type فقط در محصول استاندارد (SP) هست، نه NRT.
- [x] عکس و فیلم آرشیوی آتش الیت: مهر، CC BY 4.0، در `media/` (اعتبار روی تصویر و در توضیحات الزامی است).
- [ ] تصاویر FireSat (قاب ۱۰): شرایط سایت Earth Fire Alliance محتوا را مالکیت خودش می‌داند و برداشت خودکار را ممنوع کرده؛ دانلود نشد. یا از press@earthfirealliance.org اجازه بگیر، یا قاب ۱۰ را با کارت منبع و نمودار خودمان (۳۷۵ متر در برابر ۵ متر) بساز.
- [ ] `python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --demo` و `--demo --min-confidence low --quiet` اجرا و با قاب ۵ و ۷ دک تطبیق شود (۲ نوامبر ۲۰۲۶ تطبیق داده شد).
- [ ] `python3 scripts/check-season-01.py` بدون خطا برای HMD-003.
