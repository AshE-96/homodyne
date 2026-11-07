# HMD-018 · Benchmark E09 · v5 (قسمت آخر دورهٔ بنچمارک)

## این نمرهٔ AI از کجا آمده؟ خودت بررسی کن

**وضعیت:** آمادهٔ ضبط. همهٔ خروجی‌های دمو در ۷ نوامبر ۲۰۲۶ اجرا و با متن و دک تطبیق شدند؛ منبع‌ها همان روز بازبینی شدند. پیش از ضبط: جمله‌های E06 تا E08 در قاب ۱۵ را با نسخهٔ نهایی آن قسمت‌ها تطبیق بده.
**قالب:** Benchmark Lab · **زنجیره:** HMD-017 (یوتیوب چرا این ویدیو را پیشنهاد داد؟) ← **HMD-018** → HMD-019 (مقاله را به AI دادیم؛ می‌تواند آزمایشش را تکرار کند؟)
**زمان:** حدود ۱۴ دقیقه · واژهٔ گفتاری: ببین `make episodes` · ۱۶ قاب · هوک: Problem-Agitation («خودشون گفتن»)

**جملهٔ مرکزی:** یک نمره وقتی «نتیجه» است که یک غریبه بتواند بدون ناشرش آن را دوباره حساب کند: جواب‌های برچسب‌خورده، روش، کد و دفتر اصلاحیه، به‌علاوهٔ مانیفستی از اثرانگشت‌ها که لنگرش بیرون از بسته و با تاریخ منتشر شده.

**مرز ادعا:** بررسی‌پذیری درستیِ حساب را نشان می‌دهد، نه درستی برچسب‌ها یا تکرار رفتار مدل در اجرای دوباره؛ لنگر تعویض بی‌صدا را سخت می‌کند، نه ناممکن؛ بستهٔ دمو آموزشی است.

## فایل‌ها

| فایل | محتوا |
|---|---|
| [script-fa.md](script-fa.md) | متن ضبط v5 (۱۶ قاب؛ MID-CTA قاب ۵ حدود ۲۵٪؛ RE-HOOK قاب ۱۰ حدود ۵۸٪؛ قاب ۱۵ کل دوره E01 تا E09) |
| [hooks-fa.md](hooks-fa.md) | پنج هوک + توصیه (Problem-Agitation) |
| [package-fa.md](package-fa.md) | بستهٔ انتشار کامل + متادیتای انگلیسی |
| [`deck-fa.html`](deck-fa.html) | دک ضبط v6، فارسی و راست‌به‌چپ: کاور + ۱۶ قاب (→ ← · F · H · N) |
| [`deck-en.html`](deck-en.html) | همان دک به انگلیسی، با همان قاب‌ها و همان ترتیب |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ هر دو دک؛ بعد از ویرایش `make decks` |
| [sources.md](sources.md) | منابع R40–R44، R03، خروجی واقعی artifact |
| [artifact/recompute_check.py](artifact/recompute_check.py) | چک‌کنندهٔ خواننده: مانیفست SHA-256، لنگر، دفتر اصلاحیه، محاسبهٔ دوبارهٔ نمره با `tools/bluff_lab.py` (stdlib) |
| [artifact/handoff-v3.md](artifact/handoff-v3.md) | پیوند به پیش‌نیازهای اجرای واقعی Bluff (از نسخهٔ قبل، دست‌نخورده) |

نسخهٔ قبلی: `../_archive/v4-november-2026/e09-how-do-you-publish-a-refutable-result/`.

## اجرا (از ریشهٔ مخزن)

```bash
A=parts/02-benchmarking/e09-how-do-you-publish-a-refutable-result/artifact
python3 $A/recompute_check.py --selftest                           # پنج بسته، هر کدام بی‌لنگر و با لنگر
python3 $A/recompute_check.py --demo /tmp/b                         # بستهٔ آموزشی v0.1 + چاپ لنگر
python3 $A/recompute_check.py /tmp/b --anchor <sha256>              # PASS
python3 $A/recompute_check.py --demo /tmp/t --variant tamper-all    # تقلب تمیز
python3 $A/recompute_check.py /tmp/t                                # PASS بدون لنگر (!)
python3 $A/recompute_check.py /tmp/t --anchor <لنگر v0.1>           # FAIL
python3 $A/recompute_check.py /tmp/b --claim A=0.3                  # عددی که روی اسکرین‌شات دیدی
```

`--variant`: `original`، `tamper-csv`، `tamper-csv-manifest`، `tamper-all`، `correction`. کد خروج: 0 = PASS، 1 = FAIL.

## خروجی واقعی `--selftest` (۷ نوامبر ۲۰۲۶) · ILLUSTRATIVE

```
# ILLUSTRATIVE (teaching bundle; no model was called)
# selftest: one original bundle, three tampered ones, one public correction
# every bundle is checked twice: without and with the anchor published outside it

anchor v0.1 = sha256(MANIFEST.sha256) = e6db5cb88679bd980353f1188a716a1a34b6d07eb03f3ccc2e6206677eb0ad2b

[original           ] no anchor   -> PASS
[original           ] anchor e6db5cb8 -> PASS
  ok    manifest matches the published anchor e6db5cb88679...
  ok    results.csv     35ceaaf427d7...
  ok    published.json  9f7fb21f0017...
  ok    METHOD.md       53c632aa8884...
  ok    CHANGELOG.md    833d23ee3f61...
  ok    version v0.1 is the newest of 1 log entry
  ok    A: published -0.100 == recomputed -0.100
  ok    B: published +0.100 == recomputed +0.100

[tamper-csv         ] no anchor   -> FAIL  first mismatch: hash mismatch in results.csv: manifest 35ceaaf427d7..., file 0fb34f0c362b...
[tamper-csv         ] anchor e6db5cb8 -> FAIL  first mismatch: hash mismatch in results.csv: manifest 35ceaaf427d7..., file 0fb34f0c362b...

[tamper-csv-manifest] no anchor   -> FAIL  first mismatch: score of A: published -0.100, recomputed +0.300
[tamper-csv-manifest] anchor e6db5cb8 -> FAIL  first mismatch: manifest anchor: published e6db5cb88679..., bundle has 55734e42755b...

[tamper-all         ] no anchor   -> PASS
[tamper-all         ] anchor e6db5cb8 -> FAIL  first mismatch: manifest anchor: published e6db5cb88679..., bundle has 3013a118e3d7...

[correction         ] no anchor   -> PASS
[correction         ] anchor 57772828 -> PASS
  ok    manifest matches the published anchor 577728283b70...
  ok    results.csv     0fb34f0c362b...
  ok    published.json  93e133b7daa7...
  ok    METHOD.md       53c632aa8884...
  ok    CHANGELOG.md    9659319087d5...
  ok    version v0.2 is the newest of 2 log entries
  ok    A: published +0.300 == recomputed +0.300
  ok    B: published +0.100 == recomputed +0.100

[original, viewer types A=+0.300 from a screenshot] -> FAIL  first mismatch: score of A: claimed +0.300, recomputed -0.100

selftest: all expectations met
```

## باید پیش از ضبط حل شود

| برچسب | مورد | کجا | اقدام |
|---|---|---|---|
| ✔ | خروجی artifact | قاب ۶، ۸–۱۲، دک | اجرا و تطبیق شد (بالا). اگر `tools/bluff-demo.csv` عوض شد، دوباره اجرا و هش‌ها را در متن و دک به‌روز کن. |
| ✔ | SWE-bench Verified (۲۳ فوریهٔ ۲۰۲۶؛ ۱۳۸؛ ۵۹٫۴٪) | قاب ۱۳ | با منابع ثانویهٔ هم‌خوان و R03 تأیید شد؛ openai.com برای ابزار ما 403 داد؛ یک بار در مرورگر ببین. |
| ☐ | خط‌های E06–E08 در مرور دوره | قاب ۱۵، دک beat-15 | آن قسمت‌ها هم‌زمان بازنویسی می‌شوند؛ با جملهٔ مرکزی نهایی‌شان تطبیق بده. |
| ☐ | لنگر و لینک واقعی بستهٔ قسمت | package-fa §۳ و §۶ | روز انتشار؛ URL ساختگی ممنوع. |
| ☐ | Makefile | `make selftest` | پیشنهاد: سطر `$(PY) parts/02-benchmarking/e09-how-do-you-publish-a-refutable-result/artifact/recompute_check.py --selftest > /dev/null` اضافه شود (این بسته جز کپی بایگانی v4 در `_archive/` چیزی بیرون از پوشه‌اش را عوض نکرده است). |
