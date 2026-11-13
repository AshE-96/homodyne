<div dir="rtl">

# HMD-015 · AI in Production · فصل ۲ · v1

## جواب داخل فایل است؛ چرا AI باز هم اشتباه می‌کند؟

**وضعیت:** قاب ۱ تا ۹ و ۱۳ تا ۱۵ آمادهٔ ضبط؛ عددهای قاب ۷ تا ۹ و «حدود ۲۹ برابر» قاب ۱۲ از اجرای واقعی محلی ۱۳ نوامبر ۲۰۲۶‌اند. قاب ۱۰، ۱۱ و جملهٔ [RUN] قاب ۱۲ منتظر اجرای API‌اند (NOT RUN YET). منبع‌ها ۱۳ نوامبر ۲۰۲۶ روی وب بازبینی شدند.
**قالب:** AI in Production · ایدهٔ ۹ فایل «۲۳ آزمایش» · **انتشار:** ۲۰۲۷-۰۳-۰۴ (پنجشنبه) · **زمان برآوردی:** حدود ۱۴:۱۶ · **واژهٔ گفتاری:** 1749 (همهٔ شاخه‌ها؛ ضبط حدود ۱۶۵۰) · **قاب:** ۱۵
**هوک:** Curiosity-Gap — «جواب کلمه به کلمه توی فایله… دو تا مظنون داریم.»

**جملهٔ مرکزی:** جواب داخل فایل دو بار باید سالم برسد: جست‌وجو باید بند درست را بیاورد و مدل باید نسخهٔ درست را درست بخواند؛ و انتخاب معماری با «هزینه به‌ازای هر جواب درست» است.

**مرز ادعا:** هیچ روشی همه‌جا برنده نیست؛ هر نتیجه فقط مال همین پروندهٔ ساختگی، همین ۵۰ سؤال، همین مدل و همین تاریخ است. «جست‌وجوی ترکیبی» ما بدون مدل معنایی است. Lost in the Middle (مدل‌های ۲۰۲۳) انگیزهٔ آزمون است، نه پیش‌بینی رفتار مدل‌های امروز.

**زنجیره:** از HMD-014 / E07 («پیدا نکرده، یا پیدا کرده و بد فهمیده؟») ← این قسمت ← HMD-016 / E08 («وقتی جواب هیچ‌جا نیست؛ نه توی فایل، نه توی حافظهٔ مدل: کدوم AI به‌موقع می‌گه «نمی‌دونم»؟»؛ ۸ سؤال بی‌جواب همین قسمت پل آن‌اند).

**تصمیم مدیر محصول:** برای این اندازهٔ سند و این نوع سؤال، کدام معماری کمترین هزینه را به‌ازای هر جواب درست دارد؟ و اگر اشتباه می‌کند، پول را خرج جست‌وجو کنیم یا خواندن؟

## فایل‌ها

| فایل | چیست |
|---|---|
| [script-fa.md](script-fa.md) | متن ضبط، ۱۵ قاب، Pattern Interrupt Log، Retention Risk Map، یادداشت تدوین، کنترل پیش از ضبط |
| [hooks-fa.md](hooks-fa.md) | پنج هوک ۳۰ ثانیه‌ای + توصیه |
| [package-fa.md](package-fa.md) | عنوان‌ها، تامبنیل A/B/C، توضیحات، chapterها، تگ، کامنت پین، end screen، دو Short، پست Community |
| [`deck-fa.html`](deck-fa.html) | دک ضبط فارسی: کاور + ۱۵ قاب (→ ← · F · H · N) |
| [`deck-en.html`](deck-en.html) | همان دک به انگلیسی |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ دک؛ بعد از ویرایش `python3 scripts/build-decks.py --only hmd-015` |
| [sources.md](sources.md) | منابع R01 تا R07 با لینک و تاریخ بازبینی، و عددهای محاسبه‌شده |
| [artifact/README.md](artifact/README.md) | راهنمای artifact (انگلیسی). نسخهٔ عمومی: https://github.com/AshE-96/homodyne/tree/main/parts/05-season-02/hmd-015-answer-in-the-file/artifact |
| [artifact/answer_in_file.py](artifact/answer_in_file.py) | `retrieval` (محلی)، `estimate`، `run` و `report` (API)، `--selftest` |
| [artifact/protocol.md](artifact/protocol.md) | طرح ثابت آزمایش پیش از هر فراخوانی مدل، و ضعف‌های شناخته‌شده |
| [artifact/pack/](artifact/pack/questions.json) | ۷ سند ساختگی + فایل قدیمی FAQ، ۵۰ سؤال آزمون + ۱۰ سؤال dev، و دو پروندهٔ متنی آماده برای امتحان بیننده |
| [artifact/results/retrieval-local.txt](artifact/results/retrieval-local.txt) | خروجی اجرای محلی (و `.json`، `per-question.csv`) |
| [artifact/prices.json](artifact/prices.json) | **صاحب کانال پر می‌کند:** قیمت هر میلیون توکن و تاریخ |

## نتیجهٔ محلی (اجرا شده، ۱۳ نوامبر ۲۰۲۶، بدون مدل زبانی)

- بند درست بین ۵ نتیجهٔ اول BM25: پروندهٔ کوتاه ۴۰ از ۴۲، پروندهٔ بلند ۳۴ از ۴۲؛ ترکیبی ۴۰ و ۳۸.
- همهٔ جاافتاده‌ها سؤال‌های محاوره‌ای یا هم‌معنا بودند: در پروندهٔ بلند BM25 ۴ از ۱۲، ترکیبی ۸ از ۱۲؛ بقیه ۳۰ از ۳۰.
- نسخهٔ قدیمی بالاتر از نسخهٔ معتبر: ۱۰ از ۱۴ سؤال نسخه‌دار (BM25، پروندهٔ بلند). سؤال عینک: رتبهٔ ۱ و ۲ قدیمی، رتبهٔ ۳ معتبر.
- به‌هم‌ریختن ترتیب پرونده نتیجهٔ جست‌وجو را عوض نمی‌کند؛ پس اثر جای بند در API فقط مال مدل خواننده است.

## اجرای API (طراحی شده، اجرا نشده)

```bash
HOMODYNE_MODEL=mock:echo python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py --selftest
python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py estimate
python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py run --limit 3
python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py run
python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py report
```

`run` ۴۶۸ فراخوانی دارد (حدود ۳٫۹ میلیون توکن ورودی، برآورد تقریبی از نویسه؛ بیشترش «کل پرونده» روی پروندهٔ بلند). `report` جدول کامل و جمله‌های گفتاری قاب ۱۰، ۱۱، ۱۲ و خط اختیاری ۱۵ را با عدد واقعی و به حروف چاپ می‌کند.

## پیش از ضبط

- [x] ✔ اجرای محلی `retrieval` و تطبیق قاب ۷ تا ۹ دک با `artifact/results/retrieval-local.txt` (۱۳ نوامبر ۲۰۲۶).
- [x] ✔ `--selftest` با `HOMODYNE_MODEL=mock:echo` سبز (۱۳ نوامبر ۲۰۲۶).
- [ ] [RUN] `prices.json` (قیمت رسمی + تاریخ)، بعد `run` و `report`؛ پر کردن قاب ۱۰ تا ۱۲ در متن و دک، فقط یک شاخه در هر قاب.
- [ ] تصویرسازی ساده: میز (قاب ۳)، کتابدار (قاب ۴)، سه برگهٔ ۱۴۰۲/۱۴۰۴/۱۴۰۵ (قاب ۹)؛ صحنهٔ بازسازی‌شدهٔ قاب ۱ با برچسب.
- [ ] برچسب ILLUSTRATIVE روی همهٔ نماهای اسناد «دایره»؛ `REAL LOCAL RUN` روی قاب ۷ تا ۹؛ `NOT RUN YET` روی قاب ۱۰ تا ۱۲ تا اجرا.
- [ ] `python3 scripts/check-season-01.py channel/season-02/manifest.json` برای HMD-015 بدون خطا.

</div>
