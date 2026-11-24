<div dir="rtl">

# HMD-022 · AI in Production · فصل ۲ · v1

## برای هر سؤال، گران‌ترین AI لازم است؟

**وضعیت:** قاب ۱ تا ۱۰ و ۱۴ تا ۱۶ آمادهٔ ضبط. قاب ۱۱، ۱۲ و ۱۳ منتظر اجرای API‌اند (NOT RUN YET). مجموعهٔ ۲۰۰ سؤال، طرح آزمون (`artifact/protocol.md`)، `plan` و self-test با مدل ساختگی ۲۴ نوامبر ۲۰۲۶ اجرا شدند؛ هیچ مدل زبانی هنوز صدا زده نشده. منبع‌ها همان روز روی وب بازبینی شدند.
**قالب:** AI in Production · ایدهٔ ۱۱ فایل «۲۳ آزمایش» · **انتشار:** پنجشنبه ۲۰۲۷-۰۴-۲۲، ۱۸:۰۰ تهران · **زمان برآوردی:** حدود ۱۴:۱۷ · **واژهٔ گفتاری:** ۱۷۹۲ به شمارش voice-lint، ۱۸۴۴ به شمارش check-season (همهٔ شاخه‌ها و یادداشت‌های کروشه‌ای؛ ضبط با یک شاخه حدود ۱۷۴۰) · **قاب:** ۱۶
**هوک:** Curiosity-Gap — «دو تا سؤال… اولی هم واقعاً لازمه بره پیش گرون‌ترین هوش مصنوعی؟»
**تصویر واحد قسمت:** درمانگاه محل: پزشک عمومی = مدل کوچک، متخصص = مدل بزرگ، ارجاع‌دهنده = مسیریاب، «نظر دوم» = آبشار، صف نوبت ساعت ۹ = تیزر HMD-023.

**جملهٔ مرکزی:** همهٔ سؤال‌ها متخصص لازم ندارند، ولی اینکه کدام‌ها با حدس معلوم نمی‌شود: آستانه را روی یک دسته انتخاب کن، روی دستهٔ قفل بسنج، و با «هزینهٔ هر کار موفق» تصمیم بگیر؛ سؤال‌هایی که خطایشان گران است اصلاً به مدل ارزان نمی‌روند.

**مرز ادعا:** فقط همین ۲۰۰ سؤال ساختگی، همین دو مدل، همین تاریخ و همین قیمت‌ها؛ قیمت‌ها عوض می‌شوند. ترکیب سؤال‌های واقعی فرق دارد و صرفه‌جویی را همان تعیین می‌کند. عدد RouteLLM و FrugalGPT نتیجهٔ آن‌ها روی آزمون‌ها و مدل‌های خودشان است.

**زنجیره:** از HMD-021 («آزمایش رزومه یعنی هزاران بار یه جور سؤال از مدل گرون؛ بیشترش ساده؛ همه‌اش بزرگ‌ترین مدل لازم داشت؟»؛ قاب ۱ و ۲ جوابش‌اند؛ هیچ عددی از هزینهٔ HMD-021 گفته نمی‌شود) ← این قسمت ← HMD-023 («امروز یکی‌یکی سنجیدیم… ساعت نه صبح صد نفر هم‌زمان… انتظار چی می‌شه؟ قسمت بعد: صد کاربر هم‌زمان»، قاب ۱۶).

**تصمیم مدیر محصول:** آیا صرفه‌جویی مسیریاب هم افت کیفیت را جبران می‌کند و هم دردسر نگه‌داشتن دو مدل را؟ قاعده پیش از اجرا نوشته شد: بودجهٔ کیفیت ۲ واحد درصد زیر مدل بزرگ (روی دستهٔ تنظیم)، و مسیریاب فقط اگر هزینهٔ هر کار موفق را دست‌کم ۳۰٪ کم کند. دستهٔ دارو در هر حال: مدل بزرگ و یک آدم.

## فایل‌ها

| فایل | چیست |
|---|---|
| [script-fa.md](script-fa.md) | متن ضبط، ۱۶ قاب، Pattern Interrupt Log، Retention Risk Map، یادداشت تدوین، کنترل پیش از ضبط |
| [hooks-fa.md](hooks-fa.md) | پنج هوک ۳۰ ثانیه‌ای + توصیه |
| [package-fa.md](package-fa.md) | عنوان‌های A/B/C، تامبنیل A/B/C، توضیحات فارسی و انگلیسی، chapterها، تگ، کامنت پین، کارت‌ها و end screen، دو Short، پست Community، چک‌لیست انتشار |
| [`deck-fa.html`](deck-fa.html) | دک ضبط فارسی: کاور + ۱۶ قاب (→ ← · F · H · N) |
| [`deck-en.html`](deck-en.html) | همان دک به انگلیسی |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ دک؛ بعد از ویرایش `python3 scripts/build-decks.py --only hmd-022` |
| [sources.md](sources.md) | منابع R01، R01b و R02 با لینک و تاریخ بازبینی، مجوزها، و آنچه عمداً استفاده نشد |
| [artifact/README.md](artifact/README.md) | راهنمای artifact (انگلیسی): Model Routing Simulator |
| [artifact/routing_lab.py](artifact/routing_lab.py) | `plan` (بدون شبکه)، `run` (برآورد و [y/N]، `--limit`)، `report` (جمله‌های گفتاری [RUN] به حروف)، `simulate`، `--selftest` |
| [artifact/protocol.md](artifact/protocol.md) | طرح ثابت آزمایش پیش از هر فراخوانی مدل، و ضعف‌های شناخته‌شده |
| [artifact/tasks/tasks.json](artifact/tasks/tasks.json) | ۲۰۰ سؤال با جواب مرجع (۸۰ تنظیم، ۱۲۰ آزمون) |
| [artifact/prices.json](artifact/prices.json) | **صاحب کانال پر می‌کند:** قیمت هر میلیون توکن برای هر دو مدل و تاریخ خواندن |
| [artifact/results/MOCK-selftest/](artifact/results/MOCK-selftest/report.txt) | خروجی self-test با مدل و قیمت **ساختگی**؛ فقط شکل گزارش و نمودار؛ نتیجه نیست |

## اجرا

```bash
HOMODYNE_MODEL=mock:echo python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py --selftest
python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py plan
python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py run --limit 5
python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py run
python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py report
```

`run` ۸۰۰ فراخوانی دارد (برای هر سؤال سه نمونه از مدل کوچک و یکی از مدل بزرگ)، حدود ۱۱۰ هزار توکن ورودی به برآورد تقریبی. جواب‌ها cache می‌شوند و زمان اولین فراخوانی نگه داشته می‌شود. `report` نمودار `curve.png` و `curve.csv` را برای دک و جمله‌های قاب ۱۱ تا ۱۳ را با عدد واقعی و به حروف چاپ می‌کند.

## پیش از ضبط

- [x] ✔ `--selftest` با `HOMODYNE_MODEL=mock:echo` سبز (۲۴ نوامبر ۲۰۲۶، حدود ۵ ثانیه).
- [x] ✔ `plan` بدون کلید اجرا شد (`artifact/results/plan.txt`).
- [ ] [RUN] کلید در `private/keys.env`؛ `python3 tools/llm.py check`؛ `run --limit 5` و نگاه به پنج جواب؛ بعد `run` کامل.
- [ ] [RUN] `prices.json` با قیمت رسمی هر دو مدل و تاریخ خواندن؛ بعد `report`؛ پر کردن قاب ۱۱ تا ۱۳ در متن و دک (فقط یک شاخه)، و گذاشتن `curve.png` در قاب ۱۱.
- [ ] تصویرسازی ساده: درمانگاه و دو در (قاب ۲، ۴، ۱۰)، سه کارت جواب (قاب ۷)، صف نوبت ساعت ۹ (قاب ۱۶).
- [ ] برچسب `FICTIONAL LEAFLET · not medical advice` روی هر نمای بروشور؛ `THEIR RESULT` روی قاب ۵ و ۷؛ `NOT RUN YET` روی قاب ۱۱ تا ۱۳ تا اجرا.
- [ ] `python3 scripts/check-season-01.py channel/season-02/manifest.json` برای HMD-022 بدون خطا.

</div>
