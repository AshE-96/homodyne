<div dir="rtl">

# HMD-019 · منابع

بازبینی: ۱۳ نوامبر ۲۰۲۶ (۲۲ آبان ۱۴۰۵). هر لینک همان روز باز و خوانده شد. شناسه‌ها برای این قسمت تازه‌اند (R01 تا R05 در محدودهٔ HMD-019).

| شناسه | منبع | لینک | بازبینی | در این قسمت برای |
|---|---|---|---|---|
| R01 (منبع اصلی) | Starace, Jaffe, Sherburn, Aung و همکاران (OpenAI) · *PaperBench: Evaluating AI's Ability to Replicate AI Research* · arXiv 2504.01848 (v1 ۲ آوریل ۲۰۲۵؛ v3 ۷ آوریل ۲۰۲۵) | https://arxiv.org/abs/2504.01848 (متن کامل: https://arxiv.org/html/2504.01848v3) | ۱۳ نوامبر ۲۰۲۶، چکیده و متن HTML | چکیده: ۲۰ مقالهٔ Spotlight و Oral در ICML 2024؛ ۸٬۳۱۶ کار قابل‌نمره‌دهی؛ بهترین ایجنت «Claude 3.5 Sonnet (New) with open-source scaffolding» با میانگین امتیاز بازسازی ۲۱٫۰٪. متن: «our human baseline of ML PhDs (best of 3 attempts) achieved 41.4% after 48 hours of effort» روی زیرمجموعهٔ ۳ مقاله، «compared to 26.6% achieved by o1 on the same subset». ایجنت‌ها کد نویسندگان را نمی‌بینند («we disallow agents from using or viewing paper authors' original codebases»). داور: SimpleJudge با o3-mini. · قاب ۳، ۱۳؛ هوک ۱ |
| R02 | Yao, Shinn, Razavi, Narasimhan · *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains* · arXiv 2406.12045 (۱۷ ژوئن ۲۰۲۴) | https://arxiv.org/abs/2406.12045 (متن کامل: https://arxiv.org/html/2406.12045) | ۱۳ نوامبر ۲۰۲۶، چکیده و متن HTML | تعریف pass^k: «the chance that all k i.i.d. task trials are successful, averaged across tasks»؛ برآورد C(c,k)/C(n,k) (همان فرمول `metrics.pass_hat_k`). چکیده: gpt-4o «succeed on <50% of the tasks» و «pass^8 <25% in retail»؛ جدول ۲: gpt-4o در retail، pass^1 = ۶۱٫۲. · قاب ۶؛ هوک ۵؛ Short 1 |
| R03 | Siegel, Kapoor, Nadgir, Stroebl, Narayanan · *CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark* · arXiv 2409.11363 (v1 ۱۷ سپتامبر ۲۰۲۴) | https://arxiv.org/abs/2409.11363 | ۱۳ نوامبر ۲۰۲۶، چکیده | ۲۷۰ کار از ۹۰ مقاله (علوم کامپیوتر، علوم اجتماعی، پزشکی)؛ بهترین ایجنت روی سخت‌ترین سطح ۲۱٪. در گفتار نقل نشده؛ فقط در توضیحات و یادداشت دک به‌عنوان «آزمون هم‌خانواده». |
| R04 | Stripe API Reference · *Idempotent requests* | https://docs.stripe.com/api/idempotent_requests | ۱۳ نوامبر ۲۰۲۶ | «safely retrying requests without accidentally performing the same operation twice … if a connection error occurs, you can safely repeat the request without risk of creating a second object». مبنای «کلید یکتا» در قاب ۱۲ و قانون دفتر مشترک. |
| R05 | HMD-018 · Benchmark E09 · `parts/02-benchmarking/e09-how-do-you-publish-a-refutable-result/` | (مخزن) | ۱۳ نوامبر ۲۰۲۶ | تمایز recompute / rerun و مثال فاکتور رستوران (قاب ۴ آن قسمت)؛ تیزر پایان آن قسمت که قاب ۱ و ۲ این قسمت جوابش را می‌دهد. |

## محاسبه‌شده یا ساخته‌شده توسط ما

- **جواب‌نامه (`artifact/reference.py`)** — اجرا ۱۳ نوامبر ۲۰۲۶ با Python 3.11.7:
  `p1a 0.040816 · p1b −1.0 · p1c 145.0 · p2a 28.571 · p2b 0.100 · p2c 60.0 · p3a 0.130 · p3b 86.5 · p3c −0.385`.
  تطبیق با قسمت‌های اصلی: HMD-002 `two_scores.py` (نقطهٔ جابه‌جایی 0.0408، کنکور −1.0، و −56.0 در برابر −201.0 در t = 0.75)، HMD-006 `bluff_lab.py` (A منفی ۰٫۱، B مثبت ۰٫۱)، HMD-010 `penalty_threshold.py` (0.130، 86%، −0.385). selftest همین تطبیق را تکرار می‌کند.
- **حساب آشپز (قاب ۶):** 0.9³ = 0.729 ≈ ۷۳٪، با فرض استقلال بارها. ILLUSTRATIVE.
- **حساب هشت مرحله (قاب ۷):** 0.95⁸ = 0.6634 ≈ ۶۶٪، با فرض استقلال مرحله‌ها. ILLUSTRATIVE.
- **خروجی selftest (`artifact/selftest-output.txt`، ۱۳ نوامبر ۲۰۲۶):** ایجنت ساختگی (mock، بدون مدل)؛ ۱۳۵ اجرا همه درست نمره گرفتند؛ حذف کلید از خروجی و ردکردن macos-sandbox با کلید در محیط آزموده شد. پروب macos-sandbox: شبکه، نوشتن بیرون و خواندن مخزن مسدود، حلقهٔ بی‌پایان کشته شد، ولی `key_leak: FOUND via sysctl` (دلیل اختیاری‌بودن این حالت). پروب Docker رد شد چون daemon روشن نبود؛ پیش از `run` با `agent_lab.py plan` اجرا شود. **عددهای mock هیچ‌جا در ویدیو نمی‌آیند.**

## نیازمند اجرا پیش از ضبط [RUN]

- قاب ۹ تا ۱۲: همهٔ عددها از `python3 parts/05-season-02/hmd-019-agent-repeats-a-paper/artifact/agent_lab.py report` پس از `run` با کلید مالک. نام مدل، تاریخ اجرا و تاریخ قیمت (`prices.json`) روی دک و در این فایل ثبت شود.

## آنچه عمداً استفاده نشد

- عدد PaperBench برای مدل‌های تازه‌تر یا لیدربورد زنده؛ این قسمت دربارهٔ روش سنجش است، نه رتبهٔ امروز ایجنت‌ها.
- عدد «۲۶٪» دیگرِ PaperBench (o1 با IterativeAgent، ۲۴٫۴٪ و ۲۶٫۰٪ با ۳۶ ساعت) تا با ۲۶٫۶٪ زیرمجموعهٔ انسانی قاطی نشود.
- هر ادعای «ایجنت فلان شرکت قابل‌اعتماد است/نیست».

</div>
