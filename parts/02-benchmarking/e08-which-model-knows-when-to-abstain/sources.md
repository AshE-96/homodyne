# منابع · HMD-016 · Benchmark E08

تاریخ بازبینی: ۷ نوامبر ۲۰۲۶ (۱۶ آبان ۱۴۰۵). شناسه‌های Rxx از `private/planning/production-v3/references.json`؛ شناسه‌های X منبع تازهٔ این قسمت‌اند و هنوز در آن فایل نیستند.

| شناسه | منبع | چه چیزی از آن استفاده شد | کجا |
|---|---|---|---|
| R09 (اصلی) | [AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions — arXiv 2506.09038 (v1، ۱۰ ژوئن ۲۰۲۵)](https://arxiv.org/abs/2506.09038) · Kirichenko, Ibrahim, Chaudhuri, Bell · FAIR at Meta · کد: [github.com/facebookresearch/AbstentionBench](https://github.com/facebookresearch/AbstentionBench) | چکیده: ۲۰ مجموعه داده (سؤال با جواب نامعلوم، ناقص، فرض غلط، ذهنی، اطلاعات کهنه)؛ ۲۰ مدل پیشرفته؛ «abstention is an unsolved problem»؛ بزرگ‌کردن مدل کمک کمی کرده؛ تنظیم برای استدلال خودداری را «by 24% on average» بدتر کرده؛ system prompt دقیق در عمل کمک کرده ولی مشکل بنیادی استدلال دربارهٔ عدم‌قطعیت را حل نکرده. وابستگی سازمانی و جزئیات ۲۴٪ از متن HTML v1 (بخش 4.3: میانگین افت برای DeepSeek R1 Distill Llama 70B و s1 نسبت به همتای غیراستدلالی؛ سنجه abstention recall). **نکته:** متن روشن نمی‌کند ۲۴٪ نسبی است یا واحد درصد؛ در گفتار فقط «طبق چکیده، به‌طور میانگین ۲۴ درصد بدتر» و «در اون مطالعه» گفته می‌شود. | قاب ۳، هوک ۵ |
| X1 | [El-Yaniv & Wiener, *On the Foundations of Noise-free Selective Classification*, JMLR 11(53):1605–1641, 2010](https://www.jmlr.org/papers/v11/el-yaniv10a.html) | چکیده: «selective classification» = «classification with a reject option»؛ «We term this trade-off the risk-coverage (RC) trade-off.» فقط نام و ایدهٔ بده‌بستان؛ هیچ عددی نقل نشده. | قاب ۳ |
| R07 | [Miller, *Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations* — arXiv 2411.00640 (۱ نوامبر ۲۰۲۴)](https://arxiv.org/abs/2411.00640) | بخش 4.2 «Paired analysis»: «We therefore recommend using the paired version of the standard error estimate wherever practicable.» بخش 2.2 «Clustered questions» (مثل ترجمه‌های یک سؤال). **دقت:** میلر بوت‌استرپ را برای خطای معیار «unnecessary unless a complicated sampling scheme or estimator is being used» می‌داند؛ ما از بوت‌استرپ خوشه‌ای `bluff_lab.py` استفاده می‌کنیم (برآوردگر نسبتی با خوشه‌های نامساوی)؛ در گفتار بوت‌استرپ به میلر نسبت داده نمی‌شود، فقط «تحلیل جفتی». | قاب ۸ |
| X2 | [Nosek, Ebersole, DeHaven, Mellor, *The preregistration revolution*, PNAS 115(11):2600–2606, 2018 (PMC5856500)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/) · DOI 10.1073/pnas.1708274114 | تعریف: «Preregistration of an analysis plan is committing to analytic steps without advance knowledge of the research outcomes.»؛ تمایز پیش‌بینی (prediction) از توضیح پس از دیدن داده (postdiction). صفحهٔ pnas.org برای ابزار ما 403 داد؛ متن از PMC. | قاب ۵ |
| R01 | [Kalai, Nachum, Vempala, Zhang, *Why Language Models Hallucinate* — arXiv 2509.04664 (v1، ۴ سپتامبر ۲۰۲۵)](https://arxiv.org/abs/2509.04664) | پیش‌زمینه: نمره‌دهی رایج حدس‌زدن را بر اعتراف به عدم‌قطعیت ترجیح می‌دهد؛ پیشنهاد تغییر نمره‌دهی بنچمارک‌ها. قانون +۱ / ۰ / −k و خط سکوت t = k/(k+1) از HMD-010 (E05). | قاب ۴ |
| — | [Geifman & El-Yaniv, *Selective Classification for Deep Neural Networks* — arXiv 1705.08500 (2017)](https://arxiv.org/abs/1705.08500) | پیش‌زمینه برای منحنی ریسک–پوشش در شبکه‌های عمیق؛ در گفتار نقل نشده. | — |

## محاسبه‌های خودمان (بدون منبع بیرونی لازم)

- **خط صفر:** با +۱ / ۰ / −۳، دستیاری که همیشه «نمی‌دانم» می‌گوید دقیقاً ۰ می‌گیرد. خطای فنی (`api_error`) و خروجی نامعتبر (`invalid`) هم −k (قاعدهٔ اعلام‌شدهٔ `tools/bluff_lab.py`).
- **خط سکوت k = 3:** t = 3/4 = ۷۵٪ (E05).
- **چند مقایسه:** با m مدل، m(m−1)/2 جفت؛ ۶ مدل ⇒ ۱۵. اگر هیچ تفاوت واقعی نباشد و آزمون‌ها مستقل باشند، احتمال دست‌کم یک «هشدار کاذب» با بازه‌های ۹۵٪: ۱ − ۰٫۹۵^۱۵ ≈ ۰٫۵۳۷ (۵۴٪)؛ برای ۳ جفت ≈ ۱۴٪. مقایسه‌های جفتی روی یک مجموعه سؤال مستقل نیستند؛ عدد فقط برای شهود است و در گفتار «اگه مستقل باشن» گفته می‌شود.
- **بازهٔ Wilson برای ۰ از ۵۰:** [۰٪، ۷٫۱٪] (۹۵٪، دوطرفه)؛ بالاتر از سقف ۵٪ ⇒ UNKNOWN (قاعدهٔ `bluff_lab.py`: PASS فقط وقتی کران بالا ≤ سقف).

## دادهٔ آموزشی و ابزار (ILLUSTRATIVE)

`artifact/abstain_report.py --demo` (اجرا ۷ نوامبر ۲۰۲۶، Python 3.11.7). سه مدل خیالی، ۱۵۰ سؤال پایه × ۲ زبان (en/fa، با `cluster_id` مشترک) + ۵۰ سؤال بی‌جواب مستقل؛ هر مدل ۳۵۰ سؤال، شرط t75. پارامترهای مولد در `DEMO_MODELS` (مهارت، افت فارسی، احتمال خودداری وقتی نمی‌داند، احتمال خودداری روی سؤال بی‌جواب). seed ثابت ۱۶ برای داده، ۴۲ برای بوت‌استرپ (۲٬۰۰۰ تکرار). **هیچ مدلی صدا زده نشده.** خروجی کامل:

```
wrote abstain-demo-ILLUSTRATIVE.csv (ILLUSTRATIVE: fictional models and questions, no model was called)

HMD-016 abstain report · ILLUSTRATIVE · condition t75 (right +1, "I don't know" 0, wrong -3)
data lock  input sha256 a39e3469b7ca0e03e41a074a5f0790dde11c9d770d8c16e4f0e67e951e267f7a
           plan  sha256 e1f87007f3198289946cbdacd0713d3ee97838cb28aecb0fc03865b9308388d9

1. Per model (all answerable + unanswerable prompts, equal weight per prompt)
model      prompts  coverage   risk  abstain   score
Model-A        350       96%    34%       4%  -0.331
Model-B        350       67%    17%      33%  +0.203
Model-C        350       52%     7%      48%  +0.383
   coverage = answered / completed · risk = wrong among answered · score in points per prompt, not %
   always silent scores exactly 0

2. Guardrail on unanswerable questions (first repeat, Wilson 95%)
   Model-A    made up an answer 37 / 50  CI [60%, 84%]  vs 5% -> BREACH
   Model-B    made up an answer  3 / 50  CI [2%, 16%]   vs 5% -> UNKNOWN
   Model-C    made up an answer  0 / 50  CI [0%, 7%]    vs 5% -> UNKNOWN

3. CONFIRMATORY (preregistered): Model-B minus Model-A
   paired difference +0.534 points/prompt, pointwise 95% CI [+0.330, +0.738]
   350 prompts in 200 base clusters, cluster bootstrap x2000, seed 42
   CI excludes 0; practical delta set in advance: +0.10

4. EXPLORATORY (not preregistered; read as leads, not findings). 3 possible pairs for 3 models; 6 models would give 15.
   Model-A minus Model-C: -0.714 [-0.926, -0.497]
   Model-B minus Model-C: -0.180 [-0.343, -0.020]
   Model-A English minus Persian: +0.273 [-0.127, +0.620] (150 pairs)
   Model-B English minus Persian: +0.227 [-0.040, +0.507] (150 pairs)
   Model-C English minus Persian: +0.067 [-0.127, +0.247] (150 pairs)
   If every true difference were 0 and the 3 tests were independent, the chance that at least
   one 95% interval still excludes 0 would be 1 - 0.95^3 = 14% (for 15 pairs: 54%).

A hash proves the file did not change after hashing. It does not prove the answers were judged correctly.

Tamper test: change ONE label in line 7 (wrong -> correct), hash again:
           input sha256 2ce360be929623121dc70f570da91417f81b914f44e9808c0f073ecb933f3fa6
```

- `shasum -a 256 artifact/abstain-demo-ILLUSTRATIVE.csv` همان `a39e3469…` را داد.
- مقایسهٔ B − A با `python3 tools/bluff_lab.py compare artifact/abstain-demo-ILLUSTRATIVE.csv --a Model-B --b Model-A --iterations 2000` یکسان درآمد (+0.534، [+0.330، +0.738]).
- با seed بوت‌استرپ ۷: B − A همان +0.534، بازه [+0.332، +0.736].
- `--selftest`: قطعی بودن داده، شکستن هش با تغییر یک برچسب، برابری میانگین جفتی با محاسبهٔ دستی، اتحاد امتیاز = درست − ۳×غلط، و بی‌اثر بودن ترتیب کلیدها در هش طرح.
- پوشش و ریسک در خروجی، سؤال‌های بی‌جواب را هم شامل می‌شوند (تعریف `bluff_lab.py`)؛ برای همین ریسک A (۳۴٪) جواب‌های ساختگی روی سؤال‌های بی‌جواب را هم دارد.

## چیزی که نمی‌گوییم

- هیچ نتیجه‌ای از اجرای مدل واقعی تا این تاریخ وجود ندارد؛ Bluff اجرا و قفل نشده است. قاب ۱۱ و ۱۲ [RUN] تا قفل داده خالی‌اند.
- مدل‌های A، B و C وجود ندارند؛ هیچ عدد آموزشی به مدل واقعی نسبت داده نمی‌شود.
- هیچ رتبه‌ای از AbstentionBench نقل نمی‌شود؛ فقط یافته‌های کلی چکیده با قید «در همان مطالعه».
- سقف ۵٪ برای ساختن جواب یک انتخاب طراحی است، نه استاندارد ایمنی.
- پیوندهای `artifact/handoff-v3.md` به `examples/bluff-v1/production-v3/` در این مخزن وجود ندارند (آن پوشه پس از جدا شدن مخزن کانال منتقل نشده است)؛ به آن پیش‌نیازها در این بسته استناد نشده.
