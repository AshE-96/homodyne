---
title: "جدول درست و گمراه‌کننده: سیمپسون، best-of-N و ممیزی"
description: "وزن زیرمجموعه‌ها در پارادوکس سیمپسون، نقطهٔ برابری جریمه، تورم best-of-N، holdout، فاصلهٔ Wilson و وضعیت UNKNOWN، و بازتولید با mislead_lab.py."
lang: fa
translationKey: hmd-014-deep-dive
hmd: HMD-014
kind: deep-dive
date: 2027-02-26
tags: ["پارادوکس سیمپسون", "انتشار گزینشی", "best-of-N", "holdout", "فاصلهٔ Wilson", "آلودگی داده", "بنچمارک"]
sources:
  - title: "Singh و همکاران (2025). The Leaderboard Illusion. arXiv 2504.20879 (v1، ۲۹ آوریل ۲۰۲۵؛ v2، ۱۲ مه ۲۰۲۵)"
    url: "https://arxiv.org/abs/2504.20879"
  - title: "BetaKit (۲ مه ۲۰۲۵). Cohere Labs head calls \"unreliable\" AI leaderboard rankings a \"crisis\" in the field (منبع ثانویه)"
    url: "https://betakit.com/cohere-labs-head-calls-unreliable-ai-leaderboard-rankings-a-crisis-in-the-field/"
  - title: "Bickel, Hammel, O'Connell (1975). Sex Bias in Graduate Admissions: Data from Berkeley. Science 187(4175):398–404"
    url: "https://www.science.org/doi/10.1126/science.187.4175.398"
  - title: "Wikipedia، Simpson's paradox (بخش UC Berkeley gender bias؛ منبع ثانویه)"
    url: "https://en.wikipedia.org/wiki/Simpson%27s_paradox"
  - title: "Zhang و همکاران (2024). A Careful Examination of Large Language Model Performance on Grade School Arithmetic. arXiv 2405.00332 v4"
    url: "https://arxiv.org/html/2405.00332v4"
  - title: "Reuel و همکاران (2024). BetterBench. NeurIPS 2024, arXiv 2411.12990"
    url: "https://arxiv.org/abs/2411.12990"
  - title: "Miller (2024). Adding Error Bars to Evals. arXiv 2411.00640"
    url: "https://arxiv.org/abs/2411.00640"
datasets:
  - title: "mislead_lab.py: جدول درست با چهار تیتر، جریمهٔ k، best-of-N، holdout و ممیزی PASS/BREACH/UNKNOWN (فقط کتابخانهٔ استاندارد Python؛ ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py"
    license: "MIT (LICENSE.md مخزن)"
  - title: "bluff_lab.py: نمره‌دهی و وضعیت ممیزی سؤال‌های بی‌جواب"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff_lab.py"
    license: "MIT (LICENSE.md مخزن)"
  - title: "bluff-demo.csv: ۲۰ ردیف ساختگی برچسب‌خورده (ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff-demo.csv"
    license: "MIT (LICENSE.md مخزن)"
  - title: "GSM8K (OpenAI): حدود ۷٫۵ هزار مسئلهٔ آموزشی و ۱ هزار مسئلهٔ آزمون"
    url: "https://github.com/openai/grade-school-math"
    license: "MIT"
  - title: "GSM1k (Scale AI)، نسخهٔ Hugging Face: ۱۲۰۵ ردیف آزمون"
    url: "https://huggingface.co/datasets/ScaleAI/gsm1k"
    license: "در کارت داده ذکر نشده (بازبینی ۷ نوامبر ۲۰۲۶)"
---

یک جدول با عددهای درست سه راه برای گمراه‌کردن دارد: وزن نابرابر زیرمجموعه‌ها هنگام جمع‌زدن (پارادوکس سیمپسون)، انتخاب سنجه یا جریمه‌ای که برنده را تعیین می‌کند، و گزارش گزینشی بهترین تلاش. این نوشته هر سه را با فرمول باز می‌کند، نشان می‌دهد holdout و ممیزی با فاصلهٔ Wilson کجا کمک می‌کنند و کجا نه، و همهٔ عددهای قسمت را با `mislead_lab.py` (seed 7) بازتولید می‌کند. هیچ مدلی فراخوانده نشده است.

> **خلاصه**
> - دقت کل میانگین وزن‌دار دقت زیرمجموعه‌هاست و وزن‌ها را خود سامانه با انتخاب سؤال‌هایی که جواب می‌دهد تعیین می‌کند. با وزن یکسان، برتری A برمی‌گردد.
> - نقطهٔ برابری جریمه k* = (C_A − C_B)/(W_A − W_B) است؛ در جدول ما 216/124 ≈ 1.74.
> - از ده نسخهٔ هم‌مهارت (۷۰٪)، بهترین به‌طور میانگین ۷۴٫۹٪ می‌گیرد؛ با بیست نسخه ۷۶٫۰٪. روی holdout میانگین به حدود ۷۰٪ برمی‌گردد (ILLUSTRATIVE).
> - با صفر خطا، کران بالای Wilson برابر z²/(n + z²) است؛ برای رسیدن به ۵٪ دست‌کم ۷۳ نمونه لازم است.
> - Bluff اجرا نشده و هیچ عددی در این نوشته به مدل واقعی تعلق ندارد.

این لایهٔ فنی [قسمت HMD-014](/fa/episodes/hmd-014/) است. اگر ویدیو را ندیده‌ای، از [نوشتهٔ همراه](/fa/blog/hmd-014-correct-table-misleads/) شروع کن.

## پارادوکس سیمپسون در جدول بنچمارک دقیقاً از کجا می‌آید؟

از وزن‌ها. «دقت روی جواب‌ها» برای کل جدول میانگین وزن‌دار دقت زیرمجموعه‌هاست:

```text
acc_all = Σ_s w_s · acc_s        w_s = answered_s / answered_all
```

در جدول آموزشی (بخش ۱ خروجی، **ILLUSTRATIVE**)، A در سؤال‌های آسان ۹۵٫۰٪ و در سخت ۶۰٫۰٪ دقت دارد، B به ترتیب ۹۴٫۱٪ و ۵۵٫۰٪. ولی وزن سؤال سخت برای A برابر 390/990 (۳۹٪) و برای B برابر 60/650 (۹٪) است. B بیشتر وزنش را روی گروهی گذاشته که در آن همه دقت بالایی دارند؛ پس دقت کلش ۹۰٫۵٪ می‌شود، در برابر ۸۱٫۲٪ برای A.

شرط وارونگی همین است: یک طرف در هر گروه بهتر باشد، ولی سهم گروه آسان در طرف دیگر به اندازهٔ کافی بیشتر باشد. راه رایج اصلاح، استانداردسازی است: دقت هر گروه را با وزن‌های **یکسان** برای هر دو سامانه ترکیب کن، مثلاً سهم هر گروه از کل سؤال‌ها (۶۰۰ و ۴۰۰ از ۱۰۰۰). با همین عددهای جدول، حساب ما: A برابر 0.6 × 570/600 + 0.4 × 234/390 = 81.0٪ و B برابر 0.6 × 555/590 + 0.4 × 33/60 ≈ 78.4٪. برتری A برمی‌گردد. ولی این هم کامل نیست: دقت ۵۵٫۰٪ B در سؤال‌های سخت فقط از ۶۰ جواب آمده و برای ۳۴۰ سؤالی که جواب نداده هیچ اطلاعی نداریم. به همین دلیل، گزارش صادقانه پوشش (سهم سؤال‌هایی که جواب داده شده) را برای هر زیرمجموعه کنار دقت می‌گذارد.

### برکلی ۱۹۷۳

در پاییز ۱۹۷۳، از ۱۲٬۷۶۳ متقاضی تحصیلات تکمیلی برکلی، ۸٬۴۴۲ مرد (حدود ۴۴٪ پذیرش) و ۴٬۳۲۱ زن (حدود ۳۵٪) بودند ([Wikipedia](https://en.wikipedia.org/wiki/Simpson%27s_paradox)). Bickel و همکاران (Science، ۱۹۷۵) نشان دادند که زنان بیشتر برای رشته‌های سخت‌گیرتر درخواست داده بودند و داده‌های تجمیع‌شده با وزن رشته‌ها «a small but statistically significant bias in favor of women» نشان می‌داد. همان‌جا هم چهار رشته به ضرر زنان و شش رشته به ضرر مردان سوگیری معنی‌دار داشتند؛ Wikipedia یادآوری می‌کند که نتیجه‌گیری اصلی بر این شمارش‌ها تکیه نداشت. ما صفحهٔ Science را نتوانستیم بخوانیم و عددها از منبع ثانویه‌اند.

## نقطه‌ای که جریمه برنده را عوض می‌کند چطور حساب می‌شود؟

با قانون +۱ برای درست، صفر برای «نمی‌دانم» و −k برای غلط، امتیاز هر سامانه در N سؤال:

```text
S(k) = (C − k · W) / N
```

C تعداد درست‌ها و W تعداد غلط‌هاست. دو خط S_A(k) و S_B(k) در نقطهٔ زیر به هم می‌رسند:

```text
k* = (C_A − C_B) / (W_A − W_B) = (804 − 588) / (186 − 62) = 216 / 124 ≈ 1.74
```

A درست‌های بیشتری دارد و غلط‌های بیشتری هم. زیر k* درست‌های اضافه می‌ارزند، بالای آن غلط‌های اضافه گران‌اند. منطق انتخاب k در [نوشتهٔ عمیق HMD-010](/fa/blog/hmd-010-silence-line-calibration/) آمده است؛ این‌جا فقط نکته این است که k* را هر کسی با دو عدد از جدول می‌تواند حساب کند و ببیند انتخاب جریمه چقدر به برنده نزدیک است.

<figure>
<svg viewBox="0 0 640 300" role="img" aria-labelledby="hmd014fa-title hmd014fa-desc" style="max-width:100%;height:auto;direction:ltr" font-family="system-ui, sans-serif" font-size="12" fill="currentColor">
<title id="hmd014fa-title">امتیاز A و B در هر ۱۰۰ سؤال بر حسب جریمهٔ k؛ برنده در k = 1.74 عوض می‌شود؛ ILLUSTRATIVE</title>
<desc id="hmd014fa-desc">A: ۸۰٫۴، ۶۱٫۸، ۴۳٫۲ و ۲۴٫۶ برای k از ۰ تا ۳. B: ۵۸٫۸، ۵۲٫۶، ۴۶٫۴ و ۴۰٫۲. دو خط در k = 1.74 به هم می‌رسند.</desc>
<text x="80" y="22" opacity="0.7">ILLUSTRATIVE · mislead_lab.py section 3 · points per 100 questions</text>
<g stroke="currentColor" stroke-opacity="0.15"><line x1="80" y1="63.3" x2="580" y2="63.3"/><line x1="80" y1="110" x2="580" y2="110"/><line x1="80" y1="156.7" x2="580" y2="156.7"/><line x1="80" y1="203.3" x2="580" y2="203.3"/><line x1="80" y1="250" x2="580" y2="250" stroke-opacity="0.6"/></g>
<g font-size="11" text-anchor="end" opacity="0.7"><text x="70" y="67.3">80</text><text x="70" y="114">60</text><text x="70" y="160.7">40</text><text x="70" y="207.3">20</text><text x="70" y="254">0</text></g>
<line x1="370" y1="40" x2="370" y2="250" stroke="currentColor" stroke-opacity="0.5" stroke-dasharray="4 3"/>
<text x="376" y="48" font-size="11">k = 1.74</text>
<polyline points="80,62.4 246.7,105.8 413.3,149.2 580,192.6" fill="none" stroke="#E8A33D" stroke-width="3"/>
<polyline points="80,112.8 246.7,127.3 413.3,141.7 580,156.2" fill="none" stroke="currentColor" stroke-width="2"/>
<g fill="#E8A33D"><circle cx="80" cy="62.4" r="4"/><circle cx="246.7" cy="105.8" r="4"/><circle cx="413.3" cy="149.2" r="4"/><circle cx="580" cy="192.6" r="4"/></g>
<g><circle cx="80" cy="112.8" r="3.5"/><circle cx="246.7" cy="127.3" r="3.5"/><circle cx="413.3" cy="141.7" r="3.5"/><circle cx="580" cy="156.2" r="3.5"/></g>
<g font-size="11" font-weight="bold"><text x="88" y="56" fill="#E8A33D">A 80.4</text><text x="88" y="132">B 58.8</text><text x="586" y="196" fill="#E8A33D">24.6</text><text x="586" y="160">40.2</text></g>
<g text-anchor="middle" font-size="11"><text x="80" y="270">k = 0</text><text x="246.7" y="270">1</text><text x="413.3" y="270">2</text><text x="580" y="270">3</text></g>
<text x="330" y="292" text-anchor="middle" font-size="11" opacity="0.7">penalty k per wrong answer</text>
</svg>
<figcaption>امتیاز در هر ۱۰۰ سؤال با قانون +۱ / ۰ / −k؛ خط کهربایی A و خط دیگر B. ILLUSTRATIVE؛ داده از بخش ۳ خروجی mislead_lab.py.</figcaption>
</figure>

## انتشار گزینشی نمره را چقدر بالا می‌برد؟

نمرهٔ هر نسخه روی n سؤال یک برآورد پرنویز از مهارت واقعی p است، با انحراف معیار √(p(1 − p)/n). با p = 0.70 و n = 200 این حدود ۳٫۲ امتیاز است. اگر N نسخه آزموده و فقط بیشینه منتشر شود، عدد منتشرشده بیشینهٔ N متغیر تصادفی است و میانگینش با بزرگ‌شدن N و نویز هر نسخه بالا می‌رود، هرچند مهارت هیچ نسخه‌ای عوض نشده است.

خروجی بخش ۴ و ۵ (**ILLUSTRATIVE**):

| تنظیم | نمرهٔ منتشرشده در این اجرا | میانگین بهترین در ۲۰۰۰ تکرار | holdout در ۲۰۰۰ تکرار |
|---|---|---|---|
| ۱۰ نسخه، seed 7 | ۷۴٫۵٪ | ۷۴٫۹٪ | ۶۹٫۹٪ |
| ۱۰ نسخه، seed 11 | ۷۸٫۵٪ | ۷۴٫۹٪ | ۷۰٫۰٪ |
| ۲۰ نسخه، seed 7 | ۷۴٫۵٪ | ۷۶٫۰٪ | ۷۰٫۰٪ |

holdout کار می‌کند چون سؤال‌های تازه با انتخاب نسخه هم‌بسته نیستند: شانسی که نسخه را برنده کرد، روی آن‌ها تکرار نمی‌شود. ولی holdout تنها هم یک نمونهٔ ۲۰۰ سؤالی با همان نویز است. در seed 7 نسخهٔ منتخب روی holdout ۷۴٫۰٪ گرفت و با ۲۰ نسخه ۷۶٫۰٪؛ با seed 11 از ۷۸٫۵٪ به ۶۹٫۵٪ رسید. درس در میانگین است، نه در یک اجرا. این همان نکتهٔ [قسمت HMD-012](/fa/episodes/hmd-012/) است: هر نمره، حتی نمرهٔ holdout، حاشیهٔ خطا دارد ([Miller، arXiv 2411.00640](https://arxiv.org/abs/2411.00640)).

### The Leaderboard Illusion چه چیزی را اندازه گرفت؟

چکیدهٔ مقاله (v2) می‌گوید آزمون‌های خصوصی اعلام‌نشده به چند ارائه‌دهنده امکان داده است چند نسخه را پیش از انتشار بیازمایند و توانایی آن‌ها برای «choose the best score» به نمره‌های سوگیرانهٔ Arena انجامیده است. نویسندگان ۲۷ نسخهٔ خصوصی از Meta را در آستانهٔ انتشار Llama 4 شناسایی کرده‌اند. چکیده عدم‌تقارن داده را هم گزارش می‌کند: برآورد سهم Google و OpenAI از کل دادهٔ Arena به ترتیب ۱۹٫۲٪ و ۲۰٫۴٪، در برابر ۲۹٫۷٪ برای ۸۳ مدل open-weight روی هم؛ و می‌گوید حتی دادهٔ اضافی محدود می‌تواند تا ۱۱۲٪ بهبود نسبی روی توزیع Arena بدهد ([arXiv 2504.20879](https://arxiv.org/abs/2504.20879)). LMArena رفتار ناعادلانه را رد کرد، فهرستی از «factual errors» مقاله داد و گفت سیاست آزمون پیش از انتشارش عمومی بوده است ([BetaKit](https://betakit.com/cohere-labs-head-calls-unreliable-ai-leaderboard-rankings-a-crisis-in-the-field/)). پست اصلی LMArena را مستقیم نخوانده‌ایم.

### آلودگی و GSM1k

نسخهٔ ۴ مقالهٔ Zhang و همکاران (۲۲ نوامبر ۲۰۲۴) می‌گوید GSM1k از ۱۲۰۵ مسئله تشکیل شده، با نویسندگان انسانی و بدون استفاده از مدل زبانی ساخته شده، و برای پیشگیری از آلودگی منتشر نشده است؛ نویسندگان قرار گذاشته بودند آن را وقتی سه مدل open-source از تبارهای متفاوت به دقت ۹۵٪ برسند یا در ژوئن ۲۰۲۵، هر کدام زودتر، منتشر کنند. یافته‌ها: افت دقت تا ۸٪، نشانهٔ بیش‌برازش نظام‌مند در خانواده‌هایی مثل Phi و Mistral، و نشانهٔ کم در بسیاری از مدل‌های پیشرو ([arXiv 2405.00332v4](https://arxiv.org/html/2405.00332v4)). نسخه‌ای با ۱۲۰۵ ردیف آزمون اکنون در Hugging Face زیر نام ScaleAI/gsm1k هست، ولی کارت داده‌اش خالی است و مجوزی ذکر نمی‌کند. نسخه‌های قبلی مقاله عدد دیگری برای افت داشتند؛ ما فقط عدد v4 را آورده‌ایم.

## ممیزی کوچک کِی می‌تواند «قبول» بگوید؟

وقتی کران بالای فاصلهٔ اطمینان از سقف مجاز پایین‌تر باشد. `mislead_lab.py` و `bluff_lab.py` هر دو فاصلهٔ دوطرفهٔ ۹۵٪ Wilson را برای x خطا در n نمونه حساب می‌کنند:

```text
p̂ = x/n
center = (p̂ + z²/2n) / (1 + z²/n)
half   = z · √(p̂(1 − p̂)/n + z²/4n²) / (1 + z²/n)
```

و سه وضعیت می‌دهند: اگر کران بالا ≤ سقف، PASS؛ اگر کران پایین > سقف، BREACH؛ وگرنه UNKNOWN. با x = 0 کران بالا ساده می‌شود به z²/(n + z²). با سقف ۵٪ (انتخاب طراحی، نه استاندارد)، کوچک‌ترین n با صفر خطا که PASS می‌گیرد ۷۳ است. خروجی بخش ۶:

| خطا / نمونه | فاصلهٔ ۹۵٪ | وضعیت |
|---|---|---|
| 0 / 2 | 0.0٪ تا 65.8٪ | UNKNOWN |
| 0 / 20 | 0.0٪ تا 16.1٪ | UNKNOWN |
| 0 / 100 | 0.0٪ تا 3.7٪ | PASS |
| 3 / 20 | 5.2٪ تا 36.0٪ | BREACH |

`bluff_lab.py score` روی دادهٔ نمونه با شرط t75 برای هر دو مدل ساختگی `n_u_completed` برابر ۲، `fabrication_count` برابر صفر و `ci95_wilson` برابر [0.0, 0.6576] گزارش می‌کند: UNKNOWN. این کار عمداً از سبزکردن نتیجه‌ای که شاهد کافی ندارد جلوگیری می‌کند.

## BetterBench دربارهٔ کیفیت بنچمارک‌ها چه می‌گوید؟

Reuel و همکاران (NeurIPS 2024) چارچوبی از ۴۶ بهترین‌روش در چرخهٔ عمر بنچمارک ساختند و ۲۴ بنچمارک هوش مصنوعی را با آن سنجیدند. یافته‌ها: تفاوت‌های کیفی بزرگ و اینکه بیشتر بنچمارک‌ها معنی‌داری آماری نتایجشان را گزارش نمی‌کنند یا تکرارپذیری را آسان نمی‌کنند ([arXiv 2411.12990](https://arxiv.org/abs/2411.12990)). این تنها ادعای کمّی ما دربارهٔ کیفیت بنچمارک‌های واقعی است.

## چطور همه‌چیز را خودت بازتولید کنی؟

از ریشهٔ مخزن، فقط با کتابخانهٔ استاندارد Python (۳٫۸ یا جدیدتر):

```bash
python3 parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py --selftest
python3 parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py               # seed 7، عددهای این نوشته
python3 parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py --seed 11     # پایداری
python3 parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py --variants 20  # تلاش‌های خصوصی بیشتر
python3 tools/bluff_lab.py score tools/bluff-demo.csv --condition t75 --max-fabrication 0.05
```

`--selftest` باید `selftest: OK (reversal, metric flip, penalty flip, best-of-N inflation, Wilson, audit states)` برگرداند. گزینه‌های دیگر: `--n-test` و `--n-holdout` (اندازهٔ آزمون و holdout)، `--true-acc` (مهارت واقعی)، `--reps` (تعداد تکرار) و `--limit` (سقف ممیزی). ما همهٔ این فرمان‌ها را در ۷ نوامبر ۲۰۲۶ اجرا کردیم و خروجی seed 7 با عددهای قسمت یکی بود. seed 7 پیش از اجرا انتخاب شد و پس از دیدن نتیجهٔ holdout عوض نشد.

## محدودیت‌ها و آنچه این نشان نمی‌دهد

- جدول A و B دستی ساخته شده تا وارونگی رخ دهد. نشان می‌دهد این وارونگی **ممکن** است، نه اینکه در جدول‌های واقعی چقدر رایج است.
- استانداردسازی با وزن یکسان برتری A را برمی‌گرداند، ولی دربارهٔ سؤال‌هایی که B جواب نداده چیزی نمی‌داند. هیچ وزن‌دهی‌ای جای پوشش کامل را نمی‌گیرد.
- شبیه‌سازی best-of-N نسخه‌های مستقل با مهارت یکسان فرض می‌کند. در واقعیت نسخه‌ها مهارت متفاوت و همبسته دارند و تورم می‌تواند کمتر یا بیشتر باشد.
- دربارهٔ Chatbot Arena فقط یافته‌های نویسندگان مقاله و پاسخ LMArena را، از طریق یک گزارش خبری، آورده‌ایم؛ نه تقلب کسی را نشان می‌دهیم، نه درستی یکی از دو طرف را.
- فاصلهٔ Wilson فرض می‌کند نمونه‌ها مستقل‌اند. اگر سؤال‌های بی‌جواب خوشه‌ای باشند، فاصلهٔ واقعی پهن‌تر است. سقف ۵٪ یک انتخاب طراحی است.
- Bluff اجرا نشده است. پیوندهای GitHub پرونده‌های `artifact/` این قسمت پس از انتشار مخزن فعال می‌شوند.

## مطالعهٔ بیشتر

- Singh و همکاران، *The Leaderboard Illusion*، [arXiv 2504.20879](https://arxiv.org/abs/2504.20879).
- Zhang و همکاران، *A Careful Examination of Large Language Model Performance on Grade School Arithmetic*، [arXiv 2405.00332](https://arxiv.org/abs/2405.00332).
- Reuel و همکاران، *BetterBench*، [arXiv 2411.12990](https://arxiv.org/abs/2411.12990).
- [نوشتهٔ عمیق HMD-012](/fa/blog/hmd-012-power-paired-clusters/) دربارهٔ توان آماری و خطای خوشه‌ای.

*نسخهٔ انگلیسی: [A correct table that misleads: Simpson, best-of-N, audits](/en/blog/hmd-014-mislead-lab-methods/)*
