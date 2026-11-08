# HMD-003 · Silent Breakthrough · v5

## می‌شود آتش جنگل را وقتی هنوز کوچک است پیدا کرد؟

**وضعیت:** آمادهٔ ضبط (۷ نوامبر ۲۰۲۶). قاب ۸ با عددهای تأییدشدهٔ خبری بازنویسی شد؛ اجرای FIRMS اختیاری است و اگر کلید نرسید، ویدیوی کوتاه پیگیری.
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

## پیش از ضبط (همهٔ موارد باز)

- [ ] (اختیاری) MAP_KEY رایگان FIRMS (راهنما در `artifact/README.md`) و اجرای
  `python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --fetch --region elit --start 2025-10-28 --end 2025-11-27 --save data/elit_2025-11.csv`؛
  اگر انجام شد، متن جایگزین زیر قاب ۸ را بخوان و قاب ۸ دک را با خروجی عوض کن. اگر نه، قاب ۸ فعلی ضبط می‌شود.
- [x] محدودهٔ `elit` اصلاح شد: (50.95, 36.20, 51.45, 36.55). منبع: مختصات روستای الیت 36.32N 51.11E.
- [x] تاریخ آتش تأیید شد: ۱۰ آبان ۱۴۰۴ (۱ نوامبر ۲۰۲۵) و شعله‌ورشدن دوباره ۲۴ آبان (۱۵ نوامبر). متن هر دو را می‌گوید.
- [x] تعریف ستون‌ها از صفحهٔ محصول NASA MODAPS تأیید شد (مرکز پیکسل ۳۷۵ متری، sun glint، type). نکته: ستون type فقط در محصول استاندارد (SP) هست، نه NRT.
- [ ] فیلم/عکس آرشیوی آتش الیت فقط با مجوز، تاریخ و منبع؛ تصاویر FireSat فقط از صفحهٔ رسمی EFA.
- [ ] `python3 parts/03-standalone/hmd-003-wildfire-from-space/artifact/firms_timeline.py --demo` و `--demo --min-confidence low --quiet` اجرا و با قاب ۵ و ۷ دک تطبیق شود (۲ نوامبر ۲۰۲۶ تطبیق داده شد).
- [ ] `python3 scripts/check-season-01.py` بدون خطا برای HMD-003.
