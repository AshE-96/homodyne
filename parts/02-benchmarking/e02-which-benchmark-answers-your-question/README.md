# HMD-004 · Benchmark Lab E02 · v7

## مدل اول جدول، برای تو هم بهترین است؟

**وضعیت:** آمادهٔ ضبط. v7 (۲۶ نوامبر ۲۰۲۶): دادهٔ ساختگی جایش را به دادهٔ واقعی داد؛ همهٔ منبع‌ها دوباره باز و بازبینی شدند؛ هر دو دستور ترمینال دوباره اجرا و با دک تطبیق شدند. هیچ مورد اجرانشده یا تأییدنشده‌ای باز نمانده.
**قالب:** Benchmark Lab · دورهٔ بنچمارک قسمت ۲ · **زمان برآوردی:** حدود ۱۳:۳۶ · **واژهٔ گفتاری:** ۱۷۴۰ · **قاب:** ۱۵
**هوک:** Curiosity-Gap — «تابستون ۲۰۲۴، یه مدل ششم بود… اون یه چیز چی بود؟» (جواب در قاب ۳، 01:36)

**جملهٔ مرکزی:** مدل یک پروفایل دارد، نه یک رتبه؛ و هر بنچمارک تاریخ مصرف دارد. از خطایی شروع کن که نمی‌توانی هزینه‌اش را بدهی، نه از اسم مشهور.

**مرز ادعا:** خانواده‌ها و چرخهٔ عمر نقشهٔ راهنمای ما هستند، نه طبقه‌بندی رسمی یا خط زمانی اجباری؛ نمی‌گوییم هیچ جدولی بی‌فایده است یا کدام مدل امروز بهترین است؛ ابزار `m2bench families` واژه‌محور است و تصمیم نمی‌گیرد. عددهای Epoch اجرای خود Epoch‌اند؛ انتخاب جفت و شمارش‌ها کار ماست.

**زنجیره:** از HMD-003 («تشخیص درست به سنجه بستگی دارد») ← این قسمت ← HMD-005 («مدل اول جدول را برای فارسی امتحان کرده‌اند؟ اول ببینیم فارسی را چطور می‌خواند»).

## دادهٔ واقعی در این نسخه

| قاب | چه | منبع · مجوز |
|---|---|---|
| ۳ | کنترل سبک: GPT-4o-mini ۶ → ۱۱، Claude 3 Opus ۱۶ → ۱۰ (حالا دو ستون واقعی، به‌جای دو جواب ساختگی) | LMSYS، ۲۹ اوت ۲۰۲۴ |
| ۴ (تازه) | Llama 4 Maverick: نسخهٔ آزمایشی ۱۴۱۷ (ادعای Meta) در برابر نسخهٔ عمومی ۱۲۷۳، رتبهٔ ۳۵ از ۱۸۲؛ بیانیهٔ LMArena | Meta ۵ آوریل ۲۰۲۵ · LMArena ۸ آوریل ۲۰۲۵ · بایگانی LMArena (CC BY 4.0) |
| ۵ | کارنامهٔ واقعی دو مدل با GPQA یکسان (۸۹٫۶) و جابه‌جایی قاطع در سه آزمون دیگر؛ ۱۸۸ جفت از ۷۱ مدل (به‌جای مدل‌های ساختگی X و Y) | Epoch AI (CC BY 4.0) · قانون انتخاب ما |
| ۱۱ | اشباع با عدد واقعی: ۱۶ از ۶۵ مدل تازه با نمرهٔ کامل در OTIS Mock AIME | Epoch AI (CC BY 4.0) · شمارش ما |
| ۲ | B-roll: عکس واقعی یک مسابقهٔ آشپزی | Wikimedia Commons، مالکیت عمومی |

فقط تقسیم توکن قاب ۱۵ ساختگی (ILLUSTRATIVE) مانده: تیزر HMD-005 عمداً عدد نشان نمی‌دهد.

## فایل‌ها

| فایل | چیست |
|---|---|
| [script-fa.md](script-fa.md) | متن ضبط v7، ۱۵ قاب، لاگ و نقشهٔ ریسک |
| [hooks-fa.md](hooks-fa.md) | شش هوک + توصیه |
| [package-fa.md](package-fa.md) | بستهٔ انتشار کامل |
| [`deck-fa.html`](deck-fa.html) | دک ضبط، فارسی و راست‌به‌چپ: کاور + ۱۵ قاب (→ ← · F · H · N) |
| [`deck-en.html`](deck-en.html) | همان دک به انگلیسی، با همان قاب‌ها و همان ترتیب |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ هر دو دک؛ بعد از ویرایش `python3 scripts/build-decks.py --only hmd-004` |
| [sources.md](sources.md) | منابع، تاریخ بازبینی، خروجی‌های اجراشده، آنچه رد شد |
| [media/CREDITS.md](media/CREDITS.md) | اعتبار تصویر و داده‌ها؛ فهرست «دانلود نشد» |
| [artifact/real_data.py](artifact/real_data.py) | دادهٔ واقعی قاب ۴، ۵ و ۱۱ از ZIP اپوک و بایگانی LMArena؛ `--selftest` آفلاین |
| [artifact/derived/](artifact/derived/SOURCE.txt) | خروجی‌های کوچک + `SOURCE.txt` (لینک، مجوز، sha256، دستور) |
| [artifact/decision-card.md](artifact/decision-card.md) | کارت چهارخانه: کار ← خطای پرهزینه ← شاهد ← آزمون، با دو دستور نمایش‌داده‌شده |
| [artifact/landscape-card.md](artifact/landscape-card.md) | پنج سؤال، دو محور، شش وضعیت عمر (از v2) |
| [artifact/family-selection-bluff.md](artifact/family-selection-bluff.md) | زنجیرهٔ انتخاب برای bluff-v1 (از v2) |
| [artifact/handoff-v3.md](artifact/handoff-v3.md) | پیوند به پیش‌نویس‌های Bluff |

دادهٔ خام (ZIP اپوک، حدود ۲ مگابایت؛ دو فایل parquet بایگانی LMArena، حدود ۶۰ مگابایت هرکدام) در `artifact/data/` است و در git نمی‌رود (`artifact/.gitignore`). برای ساختن دوباره، دستورهای `artifact/derived/SOURCE.txt`.

نسخهٔ v4 در `../_archive/v4-november-2026/e02-which-benchmark-answers-your-question/` و v2 در `../_archive/v2-september-2026/e02-which-benchmark-answers-your-question/`.

## پیش از ضبط

- [ ] دو دستور قاب ۷ و ۸ (در `artifact/decision-card.md`) را از ریشهٔ **مخزن M2Lab** (`~/Documents/M2Lab`) اجرا کن، نه از مخزن هومودین (`m2bench` اینجا نیست)؛ اگر `framework/00-landscape/benchmark-families.yaml` تغییر کرده، خروجی جدید را در دک بگذار.
- [ ] `python3 -I artifact/real_data.py --selftest` سبز.
- [ ] پست LMArena در X (لینک در `sources.md`، W3) را یک بار خودت ببین؛ متن از نقل کامل یک منبع ثانویه تأیید شده است.
- [ ] عددهای Arena همیشه با «آگوست ۲۰۲۴» و «در آن تحلیل»؛ Llama 4: «۱۴۱۷» ادعای Meta، «حدود رتبهٔ ۳۵» از بایگانی امروز LMArena؛ هرگز «تقلب» نگو.
- [ ] SWE-bench: «دست‌کم ۵۹٫۴٪ از ۱۳۸ مسئلهٔ بازبینی‌شده؛ نمونهٔ تصادفی کل نبود»؛ Pro: «حدود ۳۰٪، برآورد خود OpenAI، ۸ ژوئیهٔ ۲۰۲۶».
- [ ] برچسب ILLUSTRATIVE روی قاب ۱۵؛ برچسب `Epoch AI · CC BY 4.0` زیر نمودار قاب ۵.
- [ ] `python3 scripts/check-season-01.py` بدون خطا برای HMD-004.

## چه چیزی را هنگام ضبط بگیری

- **ترمینال (قاب ۷ و ۸):** در `~/Documents/M2Lab` دو دستور `m2bench families` را زنده اجرا کن.
- **ترمینال (اختیاری، قاب ۵):** در پوشهٔ این قسمت `python3 -I artifact/real_data.py epoch artifact/data/epoch_2026-11-26/benchmark_data.zip` تا خروجی `deepseek-v4-pro_max` / `claude-haiku-5-5_max` و «pairs_passing_rule: 188» دیده شود.
- **ضبط صفحه در مرورگر خودت (هر کدام ۲ تا ۳ ثانیه، برای B-roll):** جدول «Ablation» در پست LMSYS (قاب ۳)؛ جملهٔ «experimental chat version… 1417» در پست Meta (قاب ۴)؛ Space نبردهای Llama 4 در Hugging Face (قاب ۴)؛ صفحهٔ epoch.ai/benchmarks (قاب ۵)؛ پست OpenAI دربارهٔ SWE-bench Verified (قاب ۱۰).
