# HMD-002 · منابع

بازبینی: ۲ نوامبر ۲۰۲۶. شناسه‌های Rxx از `private/planning/production-v3/references.json`.

| شناسه | منبع | لینک | بازبینی | در این قسمت برای |
|---|---|---|---|---|
| R01 | OpenAI · *Why Language Models Hallucinate* · 5 Sep 2025 | https://openai.com/index/why-language-models-hallucinate/ | جدول از مرجع تأییدشدهٔ پروژه (references.json، ۳۱ اکتبر ۲۰۲۶)؛ صفحه در این نوبت به ابزار خودکار 403 داد | جدول SimpleQA: gpt-5-thinking-mini 52/22/26، OpenAI o4-mini 1/24/75 (خودداری/درست/غلط) · قاب ۱، ۶، ۸، ۱۳ |
| R01-paper | Kalai, Nachum, Vempala, Zhang · arXiv 2509.04664 | https://arxiv.org/abs/2509.04664 | ۲ نوامبر ۲۰۲۶ (نسخهٔ HTML خوانده شد) | مثال تاریخ تولد؛ Table 2: ده ارزیابی (GPQA، MMLU-Pro، IFEval، Omni-MATH، WildBench، BBH، MATH L5، MuSR، SWE-bench، HLE) که فقط WildBench اعتبار جزئی برای IDK می‌دهد؛ جملهٔ «the vast majority of popular evaluations have binary grading»؛ §4.2 k = t/(1−t) · قاب ۷، ۱۰ |
| R07 | *Adding Error Bars to Evals* | https://arxiv.org/abs/2411.00640 | references.json | مبنای آماری دوره؛ یادآوری اینکه اختلاف دو مدل را باید با عدم‌قطعیتش سنجید (یادداشت تدوین/مرز ادعا) |

## محاسبه‌شده توسط ما (اجرا در ۲ نوامبر ۲۰۲۶ از ریشهٔ مخزن)

- `python3 parts/02-benchmarking/e01-is-a-higher-score-better/artifact/two_scores.py` — بازنمره‌دهی جدول R01: در k = 1/3 → −1.0 و 13.3؛ k = 1 → −51.0 و −4.0؛ نقطهٔ جابه‌جایی k = 0.0408 (t = 3.9٪)، «1/24.5». **بازنمره‌دهی، نه اجرای دوباره.**
- `python3 tools/bluff_lab.py demo` — داده‌های ILLUSTRATIVE A (60/30/10) و B (50/5/45)؛ امتیاز در صد سؤال برای k = 0, 1, 3, 9 → (60,50)، (30,45)، (−30,35)، (−210,5).
- نقطهٔ جابه‌جایی دستیارهای آموزشی: (60−50)/(30−5) = 0.4 (حساب دستی، قاب ۴).
- حساب حدس کور در تست چهارگزینه‌ای با منفی یک‌سوم: ¼×1 − ¾×⅓ = 0 (قاب ۱۰).

## نیازمند تأیید پیش از ضبط

- ✔ قانون کنکور (+۳ برای درست، −۱ برای غلط؛ هر غلط = منفی یک‌سوم) در ۷ نوامبر ۲۰۲۶ با چند منبع ثانویهٔ هم‌خوانِ ۱۴۰۵ تأیید شد (راهنمای کارنامهٔ ۱۴۰۵ در arkamoshavere.com، فرمول درصد در bahareman.com). sanjesh.org برای ابزار ما 403 داد؛ یک بار دفترچه را در مرورگر خودت ببین.

## آنچه عمداً استفاده نشد

- رتبه‌های زندهٔ مدل‌ها، AA-Omniscience (R08) و درصدهای امروز؛ این قسمت دربارهٔ قانون نمره است، نه رتبهٔ روز.
- هیچ نتیجه‌ای از Bluff؛ آزمایش هنوز اجرا نشده (بخش ۶ بایبل).
