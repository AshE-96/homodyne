# HMD-014 · Benchmark E07 · v5

## این جدول درست است؛ چرا گمراه‌کننده است؟

**وضعیت:** آمادهٔ تمرین و ضبط. همهٔ عددهای آموزشی از اجرای واقعی `artifact/mislead_lab.py` (seed 7، ۷ نوامبر ۲۰۲۶) آمده‌اند؛ منبع‌ها ۷ نوامبر ۲۰۲۶ بازبینی شدند. هیچ نتیجهٔ اجرانشده یا عدد تأییدنشده‌ای در متن نیست.
**قالب:** Benchmark Lab · **زنجیره:** HMD-013 (رد متن AI) ← **HMD-014** → HMD-015 (جواب داخل فایل)
**زمان:** حدود ۱۴ تا ۱۶ دقیقه · ۱۵ قاب · ۱۷۲۴ واژهٔ گفتاری · هوک: Shock/Contradiction («این جدول حتی یه عدد غلط هم نداره…»)

**جملهٔ مرکزی:** یک جدول با عددهای کاملاً درست می‌تواند برندهٔ اشتباه را نشان دهد، چون سازنده‌اش سه چیز را انتخاب کرده: کدام تکه از داده، کدام سنجه، و کدام تلاش‌ها گزارش شوند؛ و جایی که شاهد کم است، «نامعلوم» صادقانه‌تر از سبز است.

**مرز ادعا:** عددهای A و B آموزشی‌اند و به هیچ مدل واقعی تعلق ندارند؛ مکانیزم گمراه‌شدن نشان داده می‌شود، نه تقلب هیچ جدول یا شرکت مشخص؛ دربارهٔ Chatbot Arena فقط یافته‌های نویسندگان مقاله و اعتراض LMArena گزارش می‌شود؛ ممیزی کوچک بی‌خطا، سلامت را ثابت نمی‌کند.

## فایل‌ها

| فایل | محتوا |
|---|---|
| [script-fa.md](script-fa.md) | متن ضبط v5 (۱۵ قاب، MID-CTA در قاب ۵، RE-HOOK در قاب ۹) |
| [hooks-fa.md](hooks-fa.md) | پنج هوک + توصیه (Shock/Contradiction) |
| [package-fa.md](package-fa.md) | بستهٔ انتشار کامل، با metadata انگلیسی |
| [deck.html](deck.html) | دک ضبط v5 (۱۵ section، بدون منبع بیرونی) |
| [sources.md](sources.md) | منابع، تاریخ بازبینی، اعداد اجرا، آنچه نمی‌گوییم |
| [artifact/mislead_lab.py](artifact/mislead_lab.py) | جدول درست با چهار تیتر و دو برنده، جریمهٔ k، best-of-N، holdout، ممیزی PASS/BREACH/UNKNOWN (stdlib، `--selftest`) |
| [artifact/handoff-v3.md](artifact/handoff-v3.md) | پیوند به پیش‌نیازهای اجرای واقعی Bluff (از نسخهٔ قبل، دست‌نخورده) |

نسخهٔ قبلی (v4، ۱۰ قاب): `../_archive/v4-november-2026/e07-where-does-this-benchmark-mislead-you/`.

## اجرا (از ریشهٔ مخزن)

```bash
python3 parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py --selftest
python3 parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py            # seed 7 (عددهای متن)
python3 parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py --seed 11  # پایداری
python3 tools/bluff_lab.py score tools/bluff-demo.csv --condition t75 --max-fabrication 0.05            # "status": "UNKNOWN" در قاب ۱۱
```

### خروجی واقعی (ILLUSTRATIVE، seed 7، اجرا ۷ نوامبر ۲۰۲۶)

```text
ILLUSTRATIVE - teaching numbers, no model was called.

1) ONE TABLE. Every cell is correct.
system subset  questions  answered  correct  wrong  acc_answered
A      easy          600       600      570     30         95.0%
A      hard          400       390      234    156         60.0%
A      ALL          1000       990      804    186         81.2%
B      easy          600       590      555     35         94.1%
B      hard          400        60       33     27         55.0%
B      ALL          1000       650      588     62         90.5%

2) FOUR TRUE HEADLINES, SAME TABLE
  Accuracy on answered questions (all)       A  81.2%  B  90.5%  -> winner B
  Accuracy on answered questions (easy only) A  95.0%  B  94.1%  -> winner A
  Accuracy on answered questions (hard only) A  60.0%  B  55.0%  -> winner A
  Correct out of ALL 1,000 questions         A  80.4%  B  58.8%  -> winner A
  Why: B answered 60 of 400 hard questions, A answered 390. Hard share of answered: A 39%, B 9%.

3) PENALTY CHOICE (+1 right, 0 abstain, -k wrong), points per 100 questions
  k=0:  A   80.4   B   58.8   -> winner A
  k=1:  A   61.8   B   52.6   -> winner A
  k=2:  A   43.2   B   46.4   -> winner B
  k=3:  A   24.6   B   40.2   -> winner B
  Winner flips at k = 1.74

4) SELECTIVE DISCLOSURE: 10 private variants, identical true accuracy 70%, 200 test questions each (seed 7)
  private scores: 74.5 70.0 70.5 69.0 74.0 68.0 70.5 71.0 65.0 66.5
  mean of all variants: 69.9%   published (best only): variant #1 74.5%
  over 2000 repeats of this game, the published best averages 74.9% (true 70%)

5) HOLDOUT: re-test variant #1 on 200 fresh questions
  this run: published 74.5%  ->  holdout 74.0%  (true 70%)
  over 2000 repeats: published best 74.9%  ->  holdout 69.9%
  one holdout of this size is noisy too; the average is the lesson.

6) AUDIT: invented answers on unanswerable questions, limit 5% (design choice)
  0 errors in   2 checked -> 95% interval  0.0%.. 65.8%  UNKNOWN
  0 errors in  20 checked -> 95% interval  0.0%.. 16.1%  UNKNOWN
  0 errors in 100 checked -> 95% interval  0.0%..  3.7%  PASS
  3 errors in  20 checked -> 95% interval  5.2%.. 36.0%  BREACH
  zero errors needs n >= 73 checked questions before PASS at 5%
```

با `--seed 11`: نمرهٔ منتشرشده 78.5% → holdout 69.5%؛ میانگین ۲۰۰۰ تکرار 74.9% → 70.0% (همان جهت). `--selftest`: `selftest: OK (reversal, metric flip, penalty flip, best-of-N inflation, Wilson, audit states)`.

## باید پیش از ضبط حل شود

| برچسب | مورد | کجا | اقدام |
|---|---|---|---|
| ✔ | عددهای R10 (۲۷ نسخه، نقل «choose the best score») | قاب ۸، هوک ۵ | ۷ نوامبر ۲۰۲۶ با چکیدهٔ v2 تأیید شد. |
| ✔ | اعتراض LMArena | قاب ۸ | از گزارش BetaKit (۲ مه ۲۰۲۵)؛ پست اصلی X مستقیم خوانده نشد، پس فقط «رد کرد و گفت خطای واقعی دارد». |
| ✔ | برکلی ۱۹۷۳ (۸۴۴۲ / ۴۴٪، ۴۳۲۱ / ۳۵٪) | قاب ۴ | با دو منبع ثانویهٔ هم‌خوان تأیید شد؛ صفحهٔ Science برای ابزار 403 داد. اگر دسترسی داری، جدول ۱ خود مقاله را یک بار ببین. |
| ✔ | GSM1k (۱۲۰۵ سؤال، افت تا ۸٪، Phi و Mistral) | قاب ۱۰ | با متن v4 (۲۲ نوامبر ۲۰۲۴) تأیید شد. |
| باز | خوانش آزمایشی | کل متن | اگر بیش از ۱۶ دقیقه شد، کوتاه‌کردن قاب ۴ و ۱۰ (پیشنهاد در `script-fa.md`). |
| باز | `private/planning/production-v3/script-manifest.json` | خارج از این پوشه | ردیف E07 هنوز `beats: 10` و `REHEARSAL_READY` است؛ برای اینکه `check-production-v3.py` این قسمت را به `check-season-01.py` بسپارد، وضعیت باید `MOVED_TO_SEASON_01` شود (مثل E01–E05). عمداً دست نخورد. |
