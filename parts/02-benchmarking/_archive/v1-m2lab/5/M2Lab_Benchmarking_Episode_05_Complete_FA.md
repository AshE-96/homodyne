# M2Lab Benchmarking Foundations — Episode 05

## Metrics That Don’t Lie

**نسخه:** 1.1 — آمادهٔ ضبط  
**زبان روایت:** فارسی  
**زبان عناصر روی تصویر:** انگلیسی  
**زمان هدف:** 19:00 تا 20:30  
**خروجی این قسمت:** `Metric Registry + Scorecard Calculator v0.1`  
**پروژهٔ فصل:** تعریف Scorecard چندبعدی، Guardrailها و تحلیل حساسیت برای Benchmark ابزارهای Deep Research

---

## 0. واژه‌های این قسمت

مرجع سریع. روی اسلاید همیشه واژهٔ انگلیسی می‌آید؛ این جدول برای گوش مخاطب است.

| واژه | به فارسی | یک‌خطی |
|---|---|---|
| `Metric` | معیار | خط‌کش. اندازه می‌گیرد، تصمیم نمی‌گیرد |
| `Primary metric` | معیار اصلی | همان چیزی که Ranking بر پایه‌اش است |
| `Diagnostic metric` | معیار تشخیصی | می‌گوید چرا و کجا تفاوت هست |
| `Guardrail` | خط قرمز | Failureای که نتیجه را Veto می‌کند، نه اینکه میانگین را کم کند |
| `False positive` | مثبت کاذب | چیزی را درست اعلام کردیم که نبود |
| `False negative` | منفی کاذب | چیز درستی بود و از دستش دادیم |
| `Precision` | دقت | از آنچه گفت، چقدرش درست بود |
| `Recall` | فراخوانی | از آنچه بود، چقدرش را پیدا کرد |
| `Tail` | دُم توزیع | بدترین درصدِ اجراها، نه اجرای معمول |
| `Confidence interval` | بازهٔ اطمینان | دامنهٔ اختلاف‌هایی که با دادهٔ فعلی سازگارند |
| `Effect size` | اندازهٔ اثر | اختلاف چقدر بزرگ است، نه اینکه هست یا نه |
| `Composite` | امتیاز ترکیبی | خلاصهٔ وزن‌دار. یک View، نه حقیقت |
| `Pareto frontier` | مرز پارتو | گزینه‌هایی که هیچ گزینهٔ دیگری از هر دو جهت بهترشان نیست |

---

## 1. قول این قسمت به مخاطب

در پایان قسمت، مخاطب باید بتواند:

- Metric را از Decision و Failure استخراج کند؛
- نقش Primary، Secondary/Diagnostic و Guardrail را جدا کند؛
- Precision، Recall و F1 را در مسئلهٔ واقعی تفسیر کند؛
- خروجی باز را با Claim-level، Rubric و Pairwise ارزیابی کند؛
- Average را با Distribution، Slice و Tail تکمیل کند؛
- اختلاف را همراه Uncertainty و Practical threshold گزارش کند؛
- Composite score را به‌عنوان خلاصه، نه حقیقت مطلق، استفاده کند؛
- با Weight sensitivity و Pareto frontier از Winner مصنوعی جلوگیری کند.

جملهٔ محوری:

> **A metric is the ruler—not the experiment.**

Hook:

> **92% — STILL UNSAFE**

---

## 2. مسئلهٔ روایی

### THE CLAIM

«هرکس Overall score بالاتری دارد، انتخاب بهتر است.»

### THE EVIDENCE

Average می‌تواند Failure کم‌تکرار اما پرهزینه، ضعف یک Slice، Tail latency یا اختلاف نامطمئن را پنهان کند. Composite نیز انتخاب‌های ارزشی دربارهٔ وزن‌ها را داخل یک عدد حل می‌کند.

### THE STRESS TEST

یک Tool با Score برابر ۹۲ را باز می‌کنیم و سه Source ساختگی می‌بینیم. سپس Weight slider را حرکت می‌دهیم و Ranking میان سه Tool برمی‌گردد. هیچ داده‌ای عوض نشده؛ فقط Preference ما تغییر کرده است.

### THE VERDICT

Metric خوب از Outcome و Failure شروع می‌شود، Distribution و Uncertainty را نشان می‌دهد، Weight را شفاف می‌کند و Guardrail را داخل Average پنهان نمی‌کند.

### THE BUILD

Metric Registry، Scorecard سه‌لایه و Calculator ساخته می‌شود. خروجی به‌جای یک «بهترین Tool»، چهار Verdict سناریومحور می‌دهد: Best quality، Best value، Fastest و Most robust.

---

## 3. تئوری علمی و تصمیم‌های طراحی

### 3.1 سه نقش Metric

| نقش | سؤال | استفاده در پروژه |
|---|---|---|
| Primary | Claim اصلی با کدام Outcome رتبه می‌گیرد؟ | Claim-level citation support |
| Secondary / Diagnostic | چرا و کجا عملکرد فرق دارد؟ | coverage، factual accuracy، actionability، time، cost، robustness |
| Guardrail | کدام Failure نتیجه را Veto می‌کند؟ | fabricated source، critical factual error |

Guardrail میانگین را بهتر نمی‌کند؛ وضعیت Eligibility یا Risk را جدا تغییر می‌دهد.

### 3.2 Cost of error

- `False positive`: چیزی را درست/مرتبط/ایمن اعلام کرده‌ایم که نیست.
- `False negative`: چیزی درست/مرتبط/لازم وجود داشته ولی از دست رفته است.

Precision و Recall فقط وقتی معنا دارند که Positive class و Unit روشن باشند.

### 3.3 فرمول‌ها

`Precision = TP / (TP + FP)`  
`Recall = TP / (TP + FN)`  
`F1 = 2PR / (P + R)`

F1 میانگین هارمونیک Precision و Recall با وزن برابر است؛ الزاماً Trade-off مناسب محصول نیست.

### 3.4 خروجی‌های باز

- `Claim-level verification`: قابل Audit و دقیق؛ هزینهٔ شکستن متن و داوری بالا.
- `Rubric-based scoring`: برای Constructهای کیفی؛ کیفیت به Anchorها وابسته است.
- `Pairwise preference`: مقایسهٔ نسبی ساده‌تر؛ تعداد Pairها و Bias ترتیب مهم است.
- `LLM-as-a-Judge`: Scale و سرعت؛ نیازمند Calibration انسانی، Position swap و Audit.

### 3.5 Aggregation

- Mean: همهٔ مقدارها را جمع می‌کند؛ به Outlier حساس.
- Median: نقطهٔ میانی؛ برای توزیع‌های کج مثل latency/cost مقاوم‌تر.
- Percentile: Tail تجربه را نشان می‌دهد؛ مثلاً p95 latency.
- Macro average: Sliceها را برابر وزن می‌دهد.
- Micro average: Unitهای بیشتر غالب می‌شوند.
- Worst-group / critical failure rate: ضعف پنهان‌شده در گروه کوچک را آشکار می‌کند.

### 3.6 Uncertainty

منابع مختلف variation باید تا حد ممکن جدا دیده شوند:

- انتخاب محدود Caseها از جهان بزرگ‌تر؛
- Non-determinism در Runهای مدل؛
- تفاوت Prompt، framing و evaluator؛
- خطای Annotation/Judge؛
- Drift زمانی و Environment.

برای مقایسهٔ دو Tool روی Caseهای یکسان، اختلاف‌های Case-level paired هستند. Paired bootstrap می‌تواند با Resampling Case indexها، توزیع اختلاف و Confidence interval را تخمین بزند. CI اختلاف باید کنار Effect size و Practical threshold دیده شود.

### 3.7 Composite و Normalization

Composite فقط یک View کمکی است:

`Composite = 0.70 Quality + 0.20 Operations + 0.10 Robustness`

برای Lower-is-better مثل Time و Cost، Target و Cap را قبل از دیدن Toolها تعریف می‌کنیم:

`score = 100 × clip((cap - x) / (cap - target), 0, 1)`

Min–max normalization روی همین Competitorها خطرناک است؛ با اضافه‌شدن یک Tool بسیار بد، بقیه بدون بهترشدن Score بیشتری می‌گیرند.

### 3.8 Weight sensitivity و Pareto

Weightها Preference هستند. تحلیل حساسیت می‌پرسد Winner در محدودهٔ وزن‌های معقول چقدر پایدار می‌ماند. Pareto frontier گزینه‌هایی را نگه می‌دارد که در Quality–Cost توسط گزینهٔ دیگری هم‌زمان شکست نمی‌خورند.

---

## 4. فلو زمانی نهایی

| زمان | Beat | هدف | Proof object |
|---|---|---|---|
| 00:00–01:10 | 92% and unsafe | شکستن Score واحد | score x-ray + fabricated sources |
| 01:10–03:10 | Metric comes from failure | تعریف نقش‌ها | primary/diagnostic/guardrail |
| 03:10–05:50 | Precision, recall, F1 | وصل فرمول به Product | competitor universe |
| 05:50–08:35 | Open outputs | ساخت Measurement چندلایه | claim/rubric/pairwise |
| 08:35–11:15 | Average hides tails | دیدن Distribution | same mean, different tail |
| 11:15–13:55 | Difference and uncertainty | جلوگیری از Rank قطعی | paired bootstrap animation |
| 13:55–16:30 | Build scorecard | تعریف Metric registry | profile + composite + guardrail |
| 16:30–18:20 | Sensitivity and Pareto | آشکارکردن Preference | weight slider + frontier |
| 18:20–19:35 | Verdict and bridge | ورود به Protocol | scorecard → fair run |

---

## 5. متن کامل آمادهٔ ضبط

### 00:00–01:10 — نودودو درصد و هنوز غیرقابل‌اعتماد

**ON SCREEN:** `THE CLAIM`  
**HEADLINE:** `92% — STILL UNSAFE.`

**تصویر:** Dashboard با Overall = 92. با کلیک X-ray، سه Source ساختگی در Caseهای بحرانی آشکار شوند. داده با برچسب `ILLUSTRATIVE`.

**متن گفتاری:**

«این Tool نودودو از صد گرفته است. سریع است. Reportهای کامل می‌نویسد. بیشتر کاربران خروجی‌اش را مفید می‌دانند.

انتخابش کنیم؟

Dashboard را باز کنیم. در سه Case، منابعی ساخته که اصلاً وجود ندارند. یکی دربارهٔ اندازهٔ بازار بوده، یکی دربارهٔ Funding یک رقیب.

حالا دقت کنید. Average چیزی را پنهان نکرد. ما سؤال اشتباه را از Average پرسیدیم.

Average می‌گوید عملکرد معمول چطور بوده. هیچ‌وقت نمی‌گوید آیا یک Failure غیرقابل‌قبول اتفاق افتاده یا نه. این دو سؤال متفاوت‌اند.

پس `Metric` (معیار) فقط عددسازی نیست. Metric تصمیم می‌گیرد چه چیزی دیده شود، چه چیزی وزن بگیرد، و چه چیزی داخل میانگین گم شود.

امروز Scorecard را می‌سازیم. ولی هدفمان یک Winner مطلق نیست. می‌خواهیم ببینیم کیفیت، هزینه، سرعت و ریسک کجا با هم معامله می‌کنند.»

**در یک جمله:** میانگین بالا و Failure غیرقابل‌قبول با هم جمع می‌شوند — چون میانگین اصلاً برای این سؤال ساخته نشده.

### 01:10–03:10 — Metric از Outcome و Failure می‌آید

**ON SCREEN:** `THE MODEL`  
**HEADLINE:** `START WITH THE COST OF BEING WRONG.`

**متن گفتاری:**

«قبل از انتخاب Metric، سه سؤال می‌پرسیم. به همین ترتیب.

اول: Outcome مطلوب چیست؟ اینجا یعنی Founder در زمان کمتر یک Report دقیق و قابل‌اقدام بسازد.

دوم: کدام Failure گران است؟ Source جعلی. قیمت اشتباه. رقیب ساختگی. توصیه‌ای که هیچ شواهدی زیرش نیست.

سوم: کدام معامله را می‌پذیریم؟ مثلاً بیست درصد هزینهٔ بیشتر، در ازای نصف‌شدن خطای Citation. این را محصول تعیین می‌کند، نه آمار.

حالا Metricها سه نقش دارند و این سه نقش نباید قاطی شوند.

`Primary metric` (معیار اصلی) پاسخ Claim اصلی است. اینجا: Citation support در سطح Claim.

`Diagnostic metric` (معیار تشخیصی) توضیح می‌دهد چرا و کجا تفاوت هست. Coverage، Factual accuracy، Actionability، Time، Cost و Robustness.

و `Guardrail` (خط قرمز) می‌گوید کدام Failure اصلاً اجازهٔ استفاده را محدود می‌کند.

اینجا یک نکتهٔ کلیدی هست. Source ساختگی و Critical error را داخل میانگین حل نمی‌کنیم. اگر Guardrail شکست، Tool می‌تواند Composite بالایی داشته باشد و باز هم برچسب "قابل استفاده بدون نظارت" نگیرد.

یک هشدار هم بدهم. آستانه‌های ما — دو درصد برای Source ساختگی، پنج درصد برای Critical error — استاندارد علمی عمومی نیستند. پیشنهاد نسخهٔ اول M2Lab‌اند و به Risk tolerance همین Use case بستگی دارند.»

**در یک جمله:** Metric را از هزینهٔ اشتباه‌کردن بیرون بکش، نه از فهرست فرمول‌های موجود.

### 03:10–05:50 — Precision، Recall و F1 با مسئلهٔ رقیب

**ON SCREEN:** `THE EVIDENCE`  
**HEADLINE:** `THE RIGHT ERROR DEPENDS ON THE DECISION.`

**تصویر:** Universe از ۲۰ شرکت. هشت رقیب واقعی. Tool ده شرکت معرفی کرده؛ شش درست، چهار نامرتبط و دو رقیب واقعی جاافتاده.

**متن گفتاری:**

«چهار Metric کلاسیک را با یک کار مشخص توضیح می‌دهم: پیداکردن رقبا.

Reference standard می‌گوید هشت رقیب واقعی وجود دارد. Tool ده شرکت معرفی می‌کند.

از آن ده تا، شش تا واقعاً رقیب‌اند. چهار تا نامرتبط‌اند. و دو رقیب واقعی هم اصلاً پیدا نشدند.

`Precision` (دقت) می‌پرسد: از آنچه Tool گفت، چقدرش درست بود؟ شش تقسیم بر ده. شصت درصد.

`Recall` (فراخوانی) می‌پرسد: از آنچه واقعاً بود، چقدرش را پیدا کرد؟ شش تقسیم بر هشت. هفتادوپنج درصد.

F1 میانگین هارمونیک این دوتاست. اینجا حدود شصت‌وشش ممیز هفت.

حالا Accuracy. اینجا Accuracy می‌تواند حسابی گمراهمان کند.

چرا؟ چون جهان شرکت‌های غیررقیب خیلی بزرگ است. اگر هزار شرکت نامرتبط را درست "غیررقیب" اعلام کنیم، Accuracy بالا می‌رود — در حالی که دو رقیب اصلی را از دست داده‌ایم.

پس کدام Metric مهم‌تر است؟ بستگی دارد اشتباه‌کردن چقدر برایتان گران است.

در مرحلهٔ Discovery، Recall مهم‌تر است. رقیب مهم نباید جا بماند. در Report نهایی برای Board، Precision مهم‌تر می‌شود. فهرست نامرتبط تصمیم را منحرف می‌کند.

و F1 پاسخ طبیعی همه‌چیز نیست. F1 یک انتخاب است: وزن برابر برای هر دو خطا.

اگر هزینهٔ از دست دادن، ده برابر هزینهٔ هشدار الکی است، وزن برابر تصمیمی است که ناخواسته گرفته‌اید.»

**در یک جمله:** Precision و Recall دو سؤال متفاوت‌اند و انتخاب بینشان، انتخاب دربارهٔ این است که کدام اشتباه گران‌تر است.

### 05:50–08:35 — Report باز را چطور اندازه بگیریم؟

**ON SCREEN:** `WHAT THE SCORE SEES`  
**HEADLINE:** `RUBRICS NEED EVIDENCE, NOT ADJECTIVES.`

**متن گفتاری:**

«یک Report تحقیق بازار Answer key ندارد. پس سه لایه را روی هم می‌گذاریم.

لایهٔ اول، Claim-level. متن را به Claimهای قابل‌بررسی می‌شکنیم. هر Claim یکی از چهار برچسب می‌گیرد: Supported، Partial، Unsupported، Contradicted.

این لایه گران است. در عوض می‌توانیم از هر عدد، به منبع و دلیلش برگردیم.

لایهٔ دوم، Rubric. برای Actionability یک Anchor رفتاری یک تا پنج داریم.

اینجا یک قاعده هست: صفت ننویسید. "ضعیف، متوسط، عالی" چیزی را اندازه نمی‌گیرد. به‌جایش بپرسید — Next step مشخص است؟ شواهد دارد؟ اولویت و Dependency روشن است؟ Risk ثبت شده؟

لایهٔ سوم، Pairwise. دو Report ناشناس را برای یک تصمیم مشخص کنار هم می‌گذاریم. Annotator می‌گوید کدام مفیدتر است و چرا.

Pairwise تفاوت‌های ظریف را ساده‌تر می‌گیرد. ولی ترتیب باید Swap شود، وگرنه خودِ جایگاه روی رأی اثر می‌گذارد.

حالا LLM-as-a-Judge. بله، هزینه را کم می‌کند. نه، Ground truth نیست.

MT-Bench و مطالعات بعدش نشان داده‌اند که Judge ماشینی به موقعیت پاسخ حساس است و پاسخ طولانی‌تر را ترجیح می‌دهد.

پس در پروژهٔ ما Judge ماشینی فقط Triage می‌کند. یک نمونهٔ تصادفی، تمام Guardrail failureها و همهٔ موارد نزدیک، دست انسان بازبینی می‌شوند.

و هرجا Judge داریم، نسخه، Prompt، ترتیب و Calibration‌اش را ثبت می‌کنیم. Judge بخشی از دستگاه اندازه‌گیری است، نه ابزار جانبی.»

**در یک جمله:** خروجی باز را با سه لایهٔ متفاوت می‌سنجیم، چون هیچ‌کدام به‌تنهایی هم صحت را می‌بیند هم فایده را.

### 08:35–11:15 — دو Average مشابه، دو تجربهٔ کاملاً متفاوت

**ON SCREEN:** `THE STRESS TEST`  
**HEADLINE:** `THE MEAN CAN HIDE THE TAIL.`

**تصویر:** دو Distribution با Mean نزدیک. Tool A tail سنگین و Tool B پایدارتر.

**متن گفتاری:**

«Mean همه‌چیز را جمع می‌کند و به Outlier حساس است. Median نقطهٔ میانی است. برای latency و cost که توزیعشان کج است، Median معمولاً بهتر می‌گوید اجرای معمول چطور بوده.

Percentile چیز دیگری را نشان می‌دهد: `Tail` (دُم توزیع).

p95 latency یعنی نودوپنج درصد اجراها در آن زمان یا سریع‌تر تمام شدند، و پنج درصد کندتر. برای تجربهٔ کاربر، همان پنج درصد گاهی مهم‌تر از میانگین است.

برای Quality هم یک عدد خلاصه کافی نیست. حداقل این‌ها را نشان می‌دهیم: Mean، Median، یک معیار Tail، نرخ Critical failure، و خود Distribution.

یک مثال ملموس.

Tool A میانگین Actionability چهار ممیز دو دارد. عالی. ولی در صنایع کم‌داده به دو ممیز یک سقوط می‌کند.

Tool B میانگین چهار دارد — پایین‌تر. اما بدترین گروهش سه ممیز شش است.

اگر بازار هدف شما کم‌داده است، Tool B تصمیم بهتری است. با وجود میانگین پایین‌تر.

یک نکتهٔ فنی هم بگویم. Macro average به هر برش وزن برابر می‌دهد. Micro average واحدها را جمع می‌کند، پس گروه بزرگ‌تر غالب می‌شود. هیچ‌کدام همیشه درست نیست؛ باید با Claim بخواند.

و حرف آخر این بخش: Leaderboard بدون Distribution نمی‌گوید Tool چطور می‌بازد. برای یک محصول، نوعِ باخت معمولاً مهم‌تر از اندازهٔ برد است.»

**در یک جمله:** میانگین می‌گوید معمولاً چه می‌شود؛ دُم توزیع می‌گوید بدترین حالت چه شکلی است — و تصمیم معمولاً با دومی گرفته می‌شود.

### 11:15–13:55 — اختلاف را همراه عدم‌قطعیت گزارش کنیم

**ON SCREEN:** `MEASURED, NOT ASSUMED`  
**HEADLINE:** `RANK IS NOT A CONFIDENCE INTERVAL.`

**تصویر:** Tool A = 78.4، Tool B = 77.8؛ سپس اختلاف Case-level و Bootstrap distribution.

**متن گفتاری:**

«Tool A هفتادوهشت ممیز چهار. Tool B هفتادوهفت ممیز هشت.

Leaderboard یک برنده می‌خواهد. ولی شش‌دهم امتیاز، به‌تنهایی هیچ چیزی ثابت نمی‌کند.

خوشبختانه یک مزیت داریم: هر دو Tool روی Caseهای یکسان اجرا شده‌اند. پس برای هر Case، یک اختلاف مشخص داریم.

Paired bootstrap از همین استفاده می‌کند. مرحله به مرحله:

از همان Caseها با جایگذاری دوباره نمونه می‌گیریم. امتیاز هر دو Tool را روی همان نمونه حساب می‌کنیم. اختلاف را ذخیره می‌کنیم. و این کار را هزاران بار تکرار می‌کنیم.

نتیجه یک توزیع از اختلاف‌هاست، و از رویش `Confidence interval` (بازهٔ اطمینان).

حالا تفسیر. اگر بازه صفر را در بر بگیرد، نتیجه این نیست که دو Tool برابرند. نتیجه این است: دادهٔ فعلی برتری روشنی نشان نمی‌دهد. این دو حرف یکی نیستند.

و اگر صفر بیرون بازه باشد؟ باز هم کار تمام نشده. اندازهٔ اثر و آستانهٔ عملی می‌مانند. یک اختلاف می‌تواند آماری واقعی باشد و آن‌قدر کوچک که تعویض ابزار نیارزد.

یک تذکر دربارهٔ خود بازه. نمی‌گوییم "نودوپنج درصد احتمال دارد مقدار واقعی داخلش باشد". می‌گوییم این بازه، دامنه‌ای از اختلاف‌ها را نشان می‌دهد که با دادهٔ فعلی سازگارند.

NIST AI 800-2 روی همین تأکید دارد: منابع عدم‌قطعیت، فرض‌ها و ادعای مشروط باید گزارش شوند.

در Pilot چهل‌وهشت‌تایی ما، این بازه احتمالاً پهن خواهد بود. آن پهنا را پنهان نمی‌کنیم. خودش یافته است: یعنی نتیجه را باید تشخیصی و محدود گزارش کنیم.»

**در یک جمله:** «A از B جلوتر است» بدون بازهٔ اطمینان و آستانهٔ عملی، یک جملهٔ ناتمام است.

### 13:55–16:30 — ساخت Scorecard سه‌لایه

**ON SCREEN:** `THE BUILD`  
**HEADLINE:** `PROFILE FIRST. COMPOSITE SECOND. GUARDRAILS ALWAYS.`

**متن گفتاری:**

«Scorecard سه لایه دارد. ترتیبشان هم مهم است.

لایهٔ اول، Profile خام. Citation support، Fact coverage، Factual accuracy، Actionability، افشای عدم‌قطعیت، Time، Cost و Robustness — همه جدا از هم دیده می‌شوند.

این لایه برای تصمیم، از Composite مهم‌تر است.

لایهٔ دوم، Composite کمکی. Quality هفتاد امتیاز می‌گیرد. Operations بیست. Robustness ده.

داخل Quality: Citation support بیست، Fact coverage پانزده، Factual accuracy پانزده، Actionability پانزده، افشای عدم‌قطعیت پنج. داخل Operations: Time ده و Cost ده.

باز هم تأکید می‌کنم — این وزن‌ها استاندارد علمی نیستند. ترجیح نسخهٔ اول M2Lab هستند و قبل از Main run فریز می‌شوند.

حالا یک ریزه‌کاری مهم دربارهٔ Time و Cost.

از Target و Cap ثابت استفاده می‌کنیم. زیر Target صد می‌گیرد. بالای Cap صفر. وسطش خطی.

چرا Min–max بین همین ابزارها را به کار نمی‌بریم؟ چون اگر فردا یک ابزار خیلی بد اضافه شود، امتیاز بقیه بالا می‌رود — بدون اینکه هیچ‌کدام بهتر شده باشند.

لایهٔ سوم، Guardrail. Source ساختگی و Critical factual error یک Badge جدا دارند و وارد میانگین نمی‌شوند.

یعنی یک Tool می‌تواند در Composite اول باشد و Guardrail را رد کند. برچسب نهایی‌اش می‌شود "High quality with supervision required". نه "Winner".

و آخرین قاعده: Missing data را خودکار صفر نمی‌کنیم. دلیلش ثبت می‌شود — Tool failure، timeout، source unavailable یا annotation pending.

فقط Failureای که واقعاً به خود Tool مربوط است جریمه می‌گیرد، آن هم طبق قاعده‌ای که از قبل نوشته‌ایم.»

**در یک جمله:** اول Profile، بعد Composite، و Guardrail هیچ‌وقت داخل میانگین نمی‌رود.

### 16:30–18:20 — Weight slider و Rank flip

**ON SCREEN:** `WHAT IT MISSES`  
**HEADLINE:** `A WEIGHT IS A PREFERENCE IN DISGUISE.`

**تصویر:** سه Tool فرضی، Weight slider و نمودار Quality–Cost. همهٔ داده‌ها `ILLUSTRATIVE`.

**متن گفتاری:**

«حالا وزن‌ها را حرکت می‌دهیم. تماشا کنید.

Citation از بیست به سی‌وپنج می‌رود. Tool A اول می‌شود.

Cost را دو برابر مهم می‌کنیم. Tool B اول می‌شود.

Robustness را برای بازارهای کم‌داده بالا می‌بریم. Tool C جلو می‌آید.

هیچ عددی در داده تکان نخورد. فقط ترجیح تصمیم‌گیرنده عوض شد.

Sensitivity analysis همین وابستگی را قابل‌دیدن می‌کند. هزار ترکیب وزن را در محدوده‌های معقول نمونه می‌گیریم و می‌شماریم هر Tool در چند درصد سناریوها اول شده.

اگر Tool A فقط در یک نوار باریک برنده است، Ranking شکننده است. اگر در بیشتر وزن‌های معقول اول می‌ماند، نتیجه ارزش دارد.

بعد نوبت `Pareto frontier` (مرز پارتو) است.

یک Tool وقتی حذف‌شدنی است که ابزار دیگری هم کیفیت بالاتری داشته باشد هم هزینهٔ کمتر. آن‌وقت راحت کنارش می‌گذاریم.

اما اگر Tool A کیفیت بالاتر دارد و Tool B هزینهٔ کمتر؟ برندهٔ مطلق نداریم. دو جواب داریم، برای دو ترجیح.

پس به‌جای یک عنوان کلی، چهار Verdict می‌دهیم: Best quality، Best value، Fastest و Most robust.

Composite هنوز دیده می‌شود. فقط دیگر تصمیم را نمی‌بلعد.»

**در یک جمله:** وزن یک ترجیح است با لباس عدد — و اگر برنده با جابه‌جایی وزن عوض شود، اصلاً برنده‌ای وجود نداشته.

### 18:20–19:35 — Verdict و ورود به Protocol

**ON SCREEN:** `THE VERDICT`

**متن گفتاری:**

«Metric خوب پنج کار می‌کند.

از تصمیم و Failure شروع می‌شود. نقش Primary، Diagnostic و Guardrail را جدا نگه می‌دارد. میانگین را با Distribution و Tail کامل می‌کند. اختلاف را همراه عدم‌قطعیت و آستانهٔ عملی گزارش می‌دهد. و وزن را پنهان نمی‌کند.

قاعدهٔ این قسمت ساده است. اگر یک Overall score دارید، باید بتوانید با یک کلیک Profile، Failureها، برش‌ها و روش ساختش را باز کنید.

اگر نمی‌توانید، آن عدد برای تصمیم بیش‌ازحد فشرده شده است.

حالا سه چیز داریم: Specification، Dataset و Metric Registry. ولی یک مشکل باقی است.

حتی بهترین Metric، زیر یک اجرای ناعادلانه جواب بد می‌دهد.

یک Tool Prompt بهینه بگیرد و دیگری Prompt خام. نسخه‌ها ثبت نشوند. یا داور نام Tool را ببیند. در هر سه حالت، عدد دیگر مقایسهٔ منصفانه نیست.

قسمت بعد دربارهٔ Protocol است: Prompt، Temperature، تکرار، تصادفی‌سازی، داوری کور، Logging و مدیریت انحراف.

در کامنت بنویسید در محصول شما کدام Failure هیچ‌وقت نباید پشت میانگین پنهان شود.»

**در یک جمله:** خط‌کش را ساختیم؛ حالا باید مطمئن شویم همه با یک شرایط اندازه گرفته می‌شوند.

---

## 6. Scorecard نسخهٔ v0.1

| بُعد | وزن Composite | Metric اصلی | Unit | Role |
|---|---:|---|---|---|
| Citation support | 20 | supported cited claims / cited claims | Claim–source pair | Primary |
| Fact coverage | 15 | required facts found / required facts | Fact | Diagnostic |
| Factual accuracy | 15 | correct checked facts / checked facts | Fact | Diagnostic |
| Actionability | 15 | blind human rubric 1–5 | Report | Diagnostic |
| Uncertainty disclosure | 5 | anchored rubric | Report | Diagnostic |
| Time | 10 | median + p95 per successful Case | Run | Diagnostic |
| Cost | 10 | total cost / successful Case | Run | Diagnostic |
| Robustness | 10 | retained performance across paired challenge slices | Case pair | Diagnostic |
| Fabricated source | Veto/label | fabricated sources / checked sources | Source | Guardrail |
| Critical factual error | Veto/label | critical errors / Case | Case | Guardrail |

### Thresholdهای پیشنهادی پروژه — نه استاندارد عمومی

- Fabricated source rate > 2%: `SUPERVISION REQUIRED`.
- Critical factual error rate > 5%: `NOT ELIGIBLE FOR UNATTENDED USE`.
- Practical difference threshold برای Composite: حداقل ۳ امتیاز، همراه بررسی Dimensionها.
- CI شامل صفر: `NO CLEAR DIFFERENCE IN CURRENT EVIDENCE`.

این Thresholdها قبل از Main run با Reviewer بازبینی و Freeze می‌شوند.

---

## 7. Metric Registry Template

| فیلد | توضیح |
|---|---|
| `metric_id` | شناسهٔ پایدار و Version |
| `construct` | سازه‌ای که Metric مدعی اندازه‌گیری آن است |
| `role` | Primary، Diagnostic یا Guardrail |
| `unit` | Case، Claim، Citation، Report یا Run |
| `formula` | فرمول و جهت بهتر بودن |
| `scale` | Range، Anchor و Normalization |
| `missing_rule` | رفتار با Missing، Timeout و Failure |
| `aggregation` | Mean، Median، Macro، Worst-group یا rate |
| `uncertainty` | CI، bootstrap یا روش دیگر |
| `practical_threshold` | حداقل اختلاف مهم برای تصمیم |
| `guardrail` | Veto/flag rule در صورت وجود |
| `limitations` | Bias، Proxy risk و موارد خارج از تفسیر |
| `freeze_version` | نسخه و تاریخ قفل‌شدن |

---

## 8. طراحی تجربهٔ بصری

### صحنهٔ اصلی: Score X-Ray

- Leaderboard در مرکز؛ هر ردیف Tool قابل‌کلیک.
- Tabهای `PROFILE / DISTRIBUTION / FAILURES / UNCERTAINTY / COST`.
- Overall score با کلیک به Dimensionهای خام باز شود.
- Guardrail failure باید به‌صورت Badge بیرون Composite بماند.
- Weight slider Winner را زنده تغییر دهد.
- Toggle `SHOW RANKING STABILITY` درصد First-place در weight scenarios را نشان دهد.
- Scatter `QUALITY × COST` با Pareto frontier.
- تمام داده‌های نمایشی تا اجرای واقعی فصل با `ILLUSTRATIVE DATA` علامت بخورند.

### Proof objectهای اصلی

1. Score 92 و Sourceهای ساختگی.
2. Confusion matrix رقبای واقعی/پیشنهادی.
3. Rubric anchor 1/3/5.
4. دو Distribution با Mean مشابه.
5. Bootstrap از paired differences.
6. Profile + Composite + Guardrail.
7. Weight slider و Rank flip.
8. Pareto frontier.

---

## 9. سایت‌هایی که باید نمایش داده شوند

| زمان | سایت | بخش | جملهٔ همراه | زمان |
|---|---|---|---|---:|
| 03:35 | [Scikit-learn Precision–Recall](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html) | تعریف و Trade-off | «Precision و Recall فقط بعد از تعریف Positive class معنا دارند.» | 15 ثانیه |
| 04:55 | [Scikit-learn F1](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html) | harmonic mean و فرمول | «F1 میانگین ساده نیست و وزن برابر می‌دهد.» | 10 ثانیه |
| 07:20 | [MT-Bench / LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) | Bias discussion | «Judge مقیاس می‌دهد، اما Instrument بی‌خطا نیست.» | 15 ثانیه |
| 07:50 | [Position Bias study](https://arxiv.org/abs/2406.07791) | position consistency | «Order swap یک کنترل ارزان و ضروری است.» | 12 ثانیه |
| 11:55 | [Quantifying Variance in Evaluation Benchmarks](https://arxiv.org/abs/2406.10229) | Abstract و منابع Variance | «Prompt و framing می‌توانند Rank را جابه‌جا کنند.» | 15 ثانیه |
| 12:35 | [Bootstrap CI for NLP comparisons](https://aclanthology.org/2022.lrec-1.640/) | Figure/Abstract | «Difference و Interval از Rank تنها مفیدترند.» | 12 ثانیه |
| 13:10 | [NIST AI 800-2 IPD](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf) | Practice 3.1، صفحات ۲۸ تا ۳۰ | «Uncertainty، assumptions و qualified claims باید گزارش شوند.» | 18 ثانیه |
| 17:45 | [MLCommons Benchmarks](https://mlcommons.org/benchmarks/) | Quality/performance principles | «Cost و performance بدون شرایط ثابت قابل‌مقایسه نیستند.» | 12 ثانیه |

---

## 10. چک‌لیست علمی قبل از ضبط

- F1 را میانگین ساده نگو؛ harmonic mean است.
- Precision/Recall را بدون تعریف Unit و Positive class ارائه نکن.
- Accuracy را بدون تعریف Negative universe استفاده نکن.
- p95 را «۵ درصد سریع‌تر» تفسیر نکن؛ ۹۵ درصد در آن مقدار یا کمترند.
- LLM-as-a-Judge را Ground truth بی‌خطا معرفی نکن.
- CI را احتمال مستقیم برای یک Interval ثابت تفسیر نکن.
- CI شامل صفر را اثبات برابری معرفی نکن.
- Statistical significance را معادل اهمیت محصولی نگو.
- Caseهای paired را در Bootstrap به‌صورت مستقل برای دو Tool Resample نکن.
- Min–max normalization روی Competitorهای فعلی را بدون هشدار استفاده نکن.
- Weightهای Scorecard و Guardrail thresholdها را استاندارد علمی معرفی نکن.
- Composite را جای Profile و Failure report ننشان.
- رتبهٔ زنده را داخل Narration ماندگار Hard-code نکن.

---

## 11. بستهٔ ضبط

### A-roll حذف‌ناپذیر

- Hook 92%.
- Primary/Diagnostic/Guardrail.
- مثال کامل Precision/Recall/F1.
- سه لایهٔ Open-output evaluation.
- Mean vs Tail.
- Paired bootstrap به زبان ساده.
- Profile/Composite/Guardrail.
- Weight slider و Pareto.

### B-roll

- X-ray Score و Source failure.
- Universe رقیب‌ها و Confusion matrix.
- Rubric anchor inspector.
- Distribution comparison.
- Bootstrap animation.
- Calculator با Target/Cap.
- Weight scenarios و Pareto chart.

### نقاط مناسب Pattern interrupt

- 00:32: بازشدن سه Source ساختگی.
- 03:50: شش TP، چهار FP، دو FN.
- 06:40: Rubric adjective به Anchor رفتاری تبدیل شود.
- 09:25: دو Mean نزدیک، Tail متفاوت.
- 12:15: CI روی صفر قرار گیرد.
- 15:55: Guardrail، Winner را Flag کند.
- 17:10: Rank با Slider عوض شود.

---

## 12. CTA نهایی

> Metric Registry را برای یک تصمیم واقعی پر کنید. فقط یک Primary metric، دو Diagnostic و یک Guardrail انتخاب کنید. اگر برای هرکدام نمی‌توانید Unit، Failure و Practical threshold بنویسید، هنوز Metric آمادهٔ Ranking نیست.

---

## 13. منابع اصلی این قسمت

1. NIST, [Practices for Automated Benchmark Evaluations of Language Models — AI 800-2 Initial Public Draft](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf), January 2026.
2. Scikit-learn, [Precision–Recall](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html) و [F1 score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html).
3. Zheng et al., [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685).
4. Shi et al., [Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge](https://arxiv.org/abs/2406.07791).
5. Madaan et al., [Quantifying Variance in Evaluation Benchmarks](https://arxiv.org/abs/2406.10229).
6. Bestgen, [Please, Don’t Forget the Difference and the Confidence Interval](https://aclanthology.org/2022.lrec-1.640/).
7. [MLCommons Benchmark Work](https://mlcommons.org/benchmarks/).

