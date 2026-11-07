# M2Lab Benchmarking Foundations — Episode 07

## Why Most AI Benchmarks Mislead Us

**نسخه:** 1.1 — آمادهٔ ضبط با بازبینی صفحات زنده در روز ضبط  
**زبان روایت:** فارسی  
**زبان عناصر روی تصویر:** انگلیسی  
**زمان هدف:** 20:00 تا 21:30  
**خروجی این قسمت:** `15-Point Benchmark Risk Audit + Evidence Status Profile`  
**پروژهٔ فصل:** حملهٔ پیش از اجرا به Claim، Dataset، Protocol، Metric و Publication پروژهٔ M2Lab

---

## 0. واژه‌های این قسمت

مرجع سریع. روی اسلاید همیشه واژهٔ انگلیسی می‌آید؛ این جدول برای گوش مخاطب است.

| واژه | به فارسی | یک‌خطی |
|---|---|---|
| `Validity` | روایی | آیا واقعاً همان چیزی را می‌سنجد که ادعا می‌کند |
| `Goodhart` | قانون گودهارت | وقتی معیار هدف شود، دیگر معیار خوبی نیست |
| `Leakage` | نشت | پاسخ از مسیر ارزیابی وارد سیستم شده |
| `Contamination` | آلودگی | خود Benchmark در Training دیده شده |
| `Saturation` | اشباع | همه نزدیک سقف‌اند و اختلاف‌ها بی‌معنا می‌شوند |
| `Cherry-picking` | گلچین‌کردن | فقط نتیجهٔ دلخواه منتشر می‌شود |
| `Harness` | بستر اجرا | Prompt، Retry، Parser، Judge — همهٔ چیزهای دور مدل |
| `Rank spread` | بازهٔ رتبه | با عدم‌قطعیت فعلی، چه رتبه‌هایی قابل‌دفاع‌اند |
| `External validity` | روایی بیرونی | آیا این آزمون به تصمیم واقعی ما شبیه است |
| `Claim boundary` | مرز ادعا | نتیجه اجازهٔ گفتن چه چیزی را می‌دهد و چه چیزی را نه |
| `Residual risk` | ریسک باقی‌مانده | چیزی که با وجود همهٔ اقدامات هنوز سر جایش است |

---

## 1. قول این قسمت به مخاطب

در پایان قسمت، مخاطب باید بتواند:

- ظاهر حرفه‌ای Leaderboard را از Validity روش جدا کند؛
- Goodhart-style gaming را بدون متهم‌کردن بی‌دلیل تشخیص دهد؛
- Leakage، Contamination و Evaluation awareness را تفکیک کند؛
- Cherry-picking، Selective disclosure و Post-hoc analysis را پیدا کند؛
- Prompt، Harness، Judge و Implementation bias را Audit کند؛
- Saturation، Aggregation و Rank instability را در Score ببیند؛
- فاصلهٔ Benchmark تا Product outcome را با Claim boundary محدود کند؛
- بین `No evidence`, `Conflicting evidence` و `Evidence of failure` فرق بگذارد؛
- یک Benchmark عمومی را با چک‌لیست ۱۵ موردی بررسی کند؛
- بفهمد چرا Trust با یک Score دوم حل نمی‌شود.

جملهٔ محوری:

> **A precise ranking can still be an imprecise claim.**

Hook:

> **RANK #1. EVIDENCE: UNKNOWN.**

---

## 2. مسئلهٔ روایی

### THE CLAIM

«اگر Benchmark عمومی، تعداد نمونهٔ زیاد، Methodology و Confidence interval دارد، نتیجه قابل اعتماد است.»

### THE EVIDENCE

هرکدام از این اجزا لازم یا مفیدند، اما هیچ‌کدام به‌تنهایی Validity را تضمین نمی‌کند. Benchmark می‌تواند دقیقاً چیزی را اندازه بگیرد که برای Decision ما بی‌ربط است؛ Dataset می‌تواند آلوده یا Saturated باشد؛ Protocol و Judge می‌توانند Rank را تغییر دهند؛ و انتشار می‌تواند فقط نتیجهٔ مطلوب را نشان دهد.

### THE STRESS TEST

یک Leaderboard تمیز را X-Ray می‌کنیم. سپس فقط چند لایهٔ پنهان را آشکار می‌کنیم: Variantهای ثبت‌نشده، Promptهای متفاوت، Rank spread، Distribution کاربران و Claim بزرگ‌تر از Dataset. عدد تغییر نمی‌کند، اما حق تفسیر آن کوچک‌تر می‌شود.

### THE VERDICT

Benchmark گمراه‌کننده همیشه Fraud نیست. بیشتر اوقات ترکیبی از Proxy ضعیف، Incentive، انتخاب‌های پنهان و Claim بیش‌ازحد بزرگ است. Audit خوب قصد سازنده را حدس نمی‌زند؛ مسیر Evidence را بررسی می‌کند.

### THE BUILD

چک‌لیست ۱۵ موردی روی LMArena به‌عنوان Case study اجرا می‌شود و سپس روی پروژهٔ خود M2Lab. خروجی یک Profile سبز/زرد/قرمز/Unknown است، نه Trust Score واحد.

---

## 3. تئوری علمی و Taxonomy ریسک

### 3.1 Validity risk: Benchmark چیز دیگری را می‌سنجد

ممکن است Metric دقیق باشد ولی Construct اشتباه انتخاب شده باشد. Human preference در گفت‌وگوی ناشناس، Predictor مستقیمی برای Citation accuracy، Cost، latency یا موفقیت Workflow نیست. سؤال Audit:

> این Benchmark چه چیزی را مستقیماً مشاهده می‌کند و برای چه Claim بزرگ‌تری فقط Proxy است؟

### 3.2 Incentive risk: وقتی Score هدف می‌شود

Goodhart’s Law را به‌عنوان هشدار تحلیلی به کار می‌بریم: وقتی یک Measure به Target رقابتی تبدیل می‌شود، بازیگران برای همان Measure بهینه می‌شوند. این Optimization لزوماً تقلب نیست. ریسک زمانی بالا می‌رود که:

- Test distribution شناخته‌شده و ثابت باشد؛
- Variantهای متعدد بدون Disclosure تست شوند؛
- فقط بهترین Result عمومی شود؛
- Benchmark data برای Training یا Prompt tuning در دسترس باشد؛
- Incentive رتبه از Intended use بزرگ‌تر شود.

### 3.3 Data risk: Leakage، Contamination و Saturation

- `Leakage`: اطلاعات Test یا Answer وارد Pipeline ارزیابی می‌شود.
- `Contamination`: Itemهای Benchmark یا نزدیک‌های آنها در Training دیده شده‌اند.
- `Evaluation awareness`: System تشخیص می‌دهد در Test است و رفتار متفاوتی نشان می‌دهد.
- `Saturation`: Benchmark بین سیستم‌های قوی تمایز کافی ندارد؛ تفاوت کوچک با Noise، Prompt یا Contamination هم‌اندازه می‌شود.

تازگی به‌تنهایی درمان نیست. Benchmark زنده می‌تواند Fresh باشد اما Ground truth ضعیف یا Task نامربوط داشته باشد.

### 3.4 Publication risk: چند حقیقت، فقط یکی منتشر می‌شود

Selective reporting می‌تواند در چند سطح رخ دهد:

- بهترین Model variant؛
- بهترین Prompt؛
- بهترین Run؛
- بهترین Slice؛
- بهترین Metric؛
- بهترین Date window؛
- حذف Errorها و Refusalها؛
- تیتر Winner وقتی CI یا Rank spread هم‌پوشان است.

مقالهٔ *The Leaderboard Illusion* دربارهٔ Chatbot Arena ادعا کرد تست Variantهای خصوصی و امکان Selective disclosure، میدان را نامتقارن می‌کند. LMArena در پاسخ، بخشی از تفسیرها را رد کرد، بر overlap در Confidence intervalها تأکید کرد و بعداً Methodology رتبه‌بندی و Rank spread را شفاف‌تر و کد Arena-Rank را عمومی کرد. این Case برای M2Lab ارزشمند است چون نشان می‌دهد Audit پایان بحث نیست؛ Evidence، پاسخ و اصلاح روش نیز باید ثبت شوند.

### 3.5 Protocol risk: Harness می‌تواند Winner بسازد

مواردی که باید دیده شوند:

- Prompt format و few-shot examples؛
- Tool/scaffolding access؛
- Model settings و reasoning budget؛
- Retry و Timeout؛
- Parser و output schema؛
- Interface/API؛
- Date، Region و Service load؛
- Development set در برابر Test set؛
- Implementation bug و unsolvable item.

NIST AI 800-2 یادآوری می‌کند که Anomalous result می‌تواند Finding واقعی یا نشانهٔ Contamination/Implementation problem باشد. نتیجهٔ عجیب قبل از تیتر باید Debug شود.

### 3.6 Judge risk: Measuring preference with another model

LLM judge به Position، Verbosity، Style، Authority cue و Self-preference حساس است. `More data` نیز لزوماً Bias مدل Judge را از بین نمی‌برد؛ ممکن است با اطمینان بیشتری همان Bias را Aggregation کند.

Audit حداقل باید اینها را ببیند:

- Swap consistency؛
- Agreement با Human به تفکیک Dimension؛
- Rubric anchors؛
- Judge family و رابطه‌اش با evaluated systems؛
- Tie/Unknown behavior؛
- Sensitivity به Prompt معادل؛
- Human verification برای Critical unitها.

### 3.7 Ranking risk: رتبه یک Point estimate است

سه نوع ناپایداری مهم:

1. `Sampling uncertainty`: با رأی یا Case دیگری Rank عوض می‌شود.
2. `Protocol sensitivity`: با Prompt، Judge یا Weight دیگری Rank عوض می‌شود.
3. `Composition sensitivity`: با اضافه/حذف Competitor یا Segment، Aggregate تغییر می‌کند.

پژوهش ۲۰۲۶ دربارهٔ Ranking uncertainty توصیه می‌کند Rank interval یا Rank confidence دیده شود. پژوهش Huang و همکاران نیز نشان داد در Leaderboardهای Preference، حذف بخش بسیار کوچکی از رأی‌ها می‌تواند Top rank را برگرداند. این نتیجه دربارهٔ Robustness رتبه است، نه اینکه تمام Preference data بی‌ارزش باشد.

### 3.8 External validity: Lab winner لزوماً Product winner نیست

Benchmark می‌تواند روی Task خودش معتبر باشد و برای Product decision ما نامعتبر. فاصله‌ها:

- User متفاوت؛
- Data distribution متفاوت؛
- Human-in-the-loop متفاوت؛
- Cost/latency نادیده‌گرفته‌شده؛
- Language/geography متفاوت؛
- Risk tolerance متفاوت؛
- Workflow چندمرحله‌ای در برابر پاسخ تک‌مرحله‌ای.

Claim boundary باید دقیق بگوید نتیجه به کدام محیط منتقل نمی‌شود.

---

## 4. چک‌لیست ۱۵ موردی Benchmark Risk Audit

وضعیت‌ها:

- `GREEN`: Evidence عمومی کافی و هم‌راستا؛
- `YELLOW`: Evidence محدود یا فرض مهم؛
- `RED`: شواهد مشخص از Risk مؤثر؛
- `UNKNOWN`: Evidence عمومی پیدا نشده؛ نه صفر و نه Failure.

| لایه | سؤال Audit |
|---|---|
| Validity | 1. Claim محدود و قابل falsify است؟ |
| Validity | 2. Task/Metric همان Construct را می‌سنجد؟ |
| Validity | 3. User، Operator و Population با Intended use هم‌راستاست؟ |
| Data | 4. Sampling/Coverage روشن است؟ |
| Data | 5. Ground truth، Annotation و Agreement قابل بررسی‌اند؟ |
| Data | 6. Leakage، Contamination، Freshness و Holdout مدیریت شده‌اند؟ |
| Protocol | 7. Tool/model/version، Prompt، Budget و Environment ثبت شده‌اند؟ |
| Protocol | 8. Replication، Randomization و Order effect کنترل شده‌اند؟ |
| Protocol | 9. Error، Refusal، Timeout و Missing در Result باقی مانده‌اند؟ |
| Protocol | 10. Score تا Raw run/Evidence trace می‌شود؟ |
| Metrics | 11. Primary metric به Decision و Failure متصل است؟ |
| Metrics | 12. N، Distribution، Slice و Uncertainty گزارش شده‌اند؟ |
| Metrics | 13. Ranking به Weight، Judge یا Sample چقدر حساس است؟ |
| Governance | 14. Submission، Funding، Conflict و Correction روشن‌اند؟ |
| Governance | 15. Update cadence، Versioning و Retirement condition وجود دارد؟ |

قانون:

> `UNKNOWN ≠ SAFE` و `UNKNOWN ≠ FAILED`؛ فقط یعنی هنوز حق نتیجه‌گیری نداریم.

---

## 5. فلو زمانی نهایی

| زمان | Beat | هدف | Proof object |
|---|---|---|---|
| 00:00–01:15 | Rank #1, evidence unknown | شکستن اعتماد به ظاهر | clean leaderboard x-ray |
| 01:15–03:10 | The score became the target | Incentive و Goodhart | optimization loop |
| 03:10–05:50 | The test may already be known | Leakage/contamination/saturation | data lineage scan |
| 05:50–08:20 | Only the winning run survived | Selective reporting | result funnel |
| 08:20–10:50 | The harness moved the score | Prompt/Judge/implementation | protocol diff |
| 10:50–13:30 | Rank is less stable than it looks | CI، rank spread، sensitivity | rank interval animation |
| 13:30–15:25 | Lab is not deployment | External validity | lab-to-product gap |
| 15:25–18:45 | Live audit: LMArena | بررسی منصفانهٔ Evidence | 15-point audit inspector |
| 18:45–20:00 | Audit M2Lab before the run | Red-team پروژهٔ خودمان | risk register |
| 20:00–20:45 | Verdict and bridge | آماده‌سازی اجرای واقعی | unresolved risks → run |

---

## 6. متن کامل آمادهٔ ضبط

### 00:00–01:15 — رتبهٔ اول، Evidence نامعلوم

**تصویر:** Leaderboard بسیار تمیز؛ Rank 1 با اختلاف ۰٫۳. کاربر X-Ray را روشن می‌کند: Dataset قدیمی، Variant count نامعلوم، Prompt متفاوت، CI هم‌پوشان و Claim عمومی‌تر از Task.

**متن گفتاری:**

«این مدل رتبهٔ اول است. اختلافش با دومی سه‌دهم امتیاز.

صفحه مرتب است. نمونه بزرگ است. عدد اعشار هم دارد.

و یک سؤال هنوز بی‌جواب مانده: این رتبه اجازهٔ چه ادعایی به ما می‌دهد؟

سه حالت را در نظر بگیرید. ممکن است روش محاسبه دقیق باشد و ادعای ما غلط. ممکن است Dataset مشهور باشد و برای محصول ما بی‌ربط. ممکن است Score واقعی باشد و انتخاب برنده نامطمئن.

پس Benchmark گمراه‌کننده همیشه عدد ساختگی ندارد. اغلب عدد درست است — و جمله‌ای که دورش ساخته‌ایم بیشتر از شواهد ادعا می‌کند.

امروز دنبال "Benchmark بد" نمی‌گردیم. دنبال نقطه‌ای می‌گردیم که شواهد تمام می‌شوند و حرف ادامه پیدا می‌کند.»

**در یک جمله:** عدد می‌تواند دقیق باشد و جمله‌ای که رویش ساخته‌ایم بی‌اعتبار.

**روی تصویر:**

`THE SCORE MAY BE RIGHT. THE CLAIM MAY STILL BE WRONG.`

### 01:15–03:10 — وقتی Measure به Target تبدیل می‌شود

**تصویر:** Loop: `Measure → Optimize → Publish → Train toward measure → Measure again`.

**متن گفتاری:**

«Benchmark فقط اندازه نمی‌گیرد. رفتار بازار را شکل می‌دهد.

وقتی رتبه روی خرید، سرمایه، شهرت و زمان Launch اثر بگذارد، تیم‌ها برای همان رتبه بهینه می‌شوند. کاملاً طبیعی است.

این همان هشدار `Goodhart` (قانون گودهارت) است: وقتی یک معیار به هدف تبدیل شود، رابطه‌اش با هدف اصلی ضعیف می‌شود.

حالا یک نکتهٔ مهم. بهینه‌سازی به‌خودی‌خود تقلب نیست.

اگر Benchmark واقعاً نمایندهٔ کار مهم باشد، بهترشدن رویش دقیقاً همان چیزی است که می‌خواهیم.

خطر جای دیگری است: وقتی توزیع شناخته‌شده، ثابت و باریک باشد — ولی ادعا همچنان "هوش عمومی" یا "بهترین مدل" بماند.

پس Audit باید انگیزه‌ها را ببیند. چهار سؤال:

آیا سازنده می‌تواند چند Variant را تست کند؟ آیا فقط بهترین Score عمومی می‌شود؟ آیا Prompt روی خود Test تنظیم شده؟ آیا دادهٔ Benchmark وارد Training شده؟

و یک قاعده که تا آخر قسمت نگهش می‌داریم: ما نیت کسی را حدس نمی‌زنیم. ساختار را بررسی می‌کنیم.»

**در یک جمله:** وقتی رتبه به پول تبدیل می‌شود، بهینه‌سازی برای رتبه اجتناب‌ناپذیر است — پس ساختار را باید بازرسی کرد، نه نیت را.

### 03:10–05:50 — شاید سیستم سؤال‌ها را قبلاً دیده باشد

**تصویر:** Data lineage: Training → Benchmark items → near duplicates → Test. سپس Gauge `CONTAMINATION RISK`.

**متن گفتاری:**

«سه ریسک هست که خیلی شبیه هم‌اند و مدام قاطی می‌شوند. جدایشان کنیم.

`Leakage` (نشت): پاسخ یا اطلاعات تست، از مسیر خود ارزیابی وارد سیستم شده.

`Contamination` (آلودگی): آیتم‌های Benchmark — یا نسخه‌های خیلی نزدیکشان — در Training دیده شده‌اند.

`Evaluation awareness` (آگاهی از ارزیابی): سیستم می‌فهمد در حال تست است و رفتارش عوض می‌شود.

برای مدل بسته، معمولاً نمی‌توانیم Training data را بازرسی کنیم. پس با اعتماد کاذب نمی‌نویسیم "contamination-free".

به‌جایش این‌ها را گزارش می‌کنیم: سطح ریسک، تاریخ Caseها، Holdout، جست‌وجوی تطابق دقیق، و اقدامات کاهش.

ریسک چهارم اسمش `Saturation` (اشباع) است.

وقتی همهٔ سیستم‌های قوی نزدیک سقف‌اند، اختلاف یک امتیاز ممکن است هم‌اندازهٔ نویز باشد. یا هم‌اندازهٔ حساسیت به Prompt. یا هم‌اندازهٔ آلودگی.

Benchmark هنوز برای سیستم‌های ضعیف‌تر مفید است. اما برای رتبهٔ اول، قدرت تفکیکش را از دست داده.

یک تصور غلط هم رفع کنم. تازه‌بودن به‌تنهایی کافی نیست.

سؤال دیروز شاید نشت را کم کند. ولی اگر Ground truth مبهم باشد، یا فقط توان جست‌وجوی زنده را بسنجد، ما یک سازهٔ دیگر ساخته‌ایم — نه همان چیزی که می‌خواستیم.»

**در یک جمله:** نمی‌توانیم پاک‌بودن را اثبات کنیم، پس ریسک را نام می‌بریم و اندازه‌اش را گزارش می‌کنیم.

### 05:50–08:20 — Funnel انتشار فقط یک Winner نشان می‌دهد

**تصویر:** ۲۰ Variant → ۸ Prompt → ۳ Run → ۵ Metric → یک تصویر تبلیغاتی. سپس `SHOW DISCARDED RESULTS`.

**متن گفتاری:**

«فرض کنید بیست Variant، هشت Prompt و سه Run آزمایش شده. چند نتیجهٔ ممکن وجود دارد؟

خیلی بیشتر از یک Score.

حالا اگر فقط بهترین Variant، بهترین Prompt و بهترین Run منتشر شود، آن عدد شاید واقعاً اندازه‌گیری شده باشد. ولی عملکرد معمول را نشان نمی‌دهد.

و `Cherry-picking` (گلچین‌کردن) فقط پنهان‌کردن شکست نیست. انتخاب برش، انتخاب تاریخ، انتخاب Metric و انتخاب رقیب — هرکدام به‌تنهایی روایت را عوض می‌کند.

یک نمونهٔ واقعی. مقالهٔ *The Leaderboard Illusion* همین ریسک را در Chatbot Arena بررسی کرد و دربارهٔ تست خصوصی Variantها و دسترسی نامتقارن به داده هشدار داد.

LMArena بخشی از نتیجه‌گیری‌ها را رد کرد. گفت Scoreهای مورد اشاره داخل بازهٔ اطمینان معقول بوده‌اند و سیاست تست هم عمومی بوده است.

اینجا کار ما اعلام پیروزی برای یک طرف نیست.

کار ما این است: صفحهٔ یک Benchmark باید پنج چیز را نشان دهد. تعداد Variant. سیاست ارسال. بازهٔ اطمینان. دادهٔ کنارگذاشته‌شده. و پاسخ به اعتراض‌ها.

و یک Audit وقتی کامل‌تر است که پاسخ سازمان و تغییرات بعدی روش را هم ثبت کند — نه فقط انتقاد اولیه را.»

**در یک جمله:** اگر ندانیم چند نتیجه دور ریخته شده، عددی که منتشر شده را نمی‌توانیم تفسیر کنیم.

### 08:20–10:50 — Harness می‌تواند Rank را حرکت دهد

**تصویر:** دو Protocol diff؛ فقط Prompt، Reasoning budget، Retry و Tool access متفاوت. Rank flip.

**متن گفتاری:**

«یک مدل، بدون اینکه یک وزنش عوض شود، می‌تواند زیر یک `Harness` (بستر اجرا) دیگر امتیاز متفاوتی بگیرد.

چون این‌ها همه بخشی از سیستم ارزیابی‌اند: قالب Prompt، few-shot، سقف توکن، دسترسی به ابزار، بودجهٔ استدلال، Retry و Parser.

یک مثال حساس. اگر یک مدل با دسترسی وب اجرا شود و دیگری بدون آن، چه اتفاقی افتاده؟

بستگی دارد. ممکن است این یک قابلیت واقعی محصول باشد. ممکن است یک مزیت پنهان Protocol باشد. تفسیرش کاملاً به هدف آزمایش بستگی دارد.

Judge هم بخشی از Harness است. پژوهش‌های LLM-as-a-Judge نشان داده‌اند داور به جایگاه و طول پاسخ حساس است.

پس اگر Judge همان پاسخ را در جایگاه A بیشتر از جایگاه B بپسندد، آن رأی به مدل نیست. رأی به جایگاه است.

و یک مورد که راحت از قلم می‌افتد: باگ پیاده‌سازی.

باگ هم یک عدد واقعی تولید می‌کند — فقط دربارهٔ چیزی غیر از ادعای ما. NIST پیشنهاد می‌کند برای Debug از آیتم‌های حل‌شدنی، Baseline، بررسی ناهنجاری و مقایسه با نتایج قبلی استفاده کنیم.

برای همین هر نتیجهٔ غیرمنتظره دو برچسب می‌گیرد: مشاهده و فرضیه.

"Model X شکست خورد" مشاهده نیست. تفسیر است.

مشاهده این است: در هفت Case، Parser خروجی را خالی ثبت کرده.»

**در یک جمله:** خیلی از تفاوت‌هایی که به مدل نسبت می‌دهیم، مال چیزهایی است که دور مدل چیده‌ایم.

### 10:50–13:30 — رتبه کمتر از چیزی که می‌بینیم پایدار است

**تصویر:** Rank 1 به Rank spread `1–4` باز می‌شود. سپس یک Slider تعداد Vote/Case را کم می‌کند و Top rank جابه‌جا می‌شود.

**متن گفتاری:**

«رتبه یک برآورد نقطه‌ای است. یک عدد، بدون هیچ پهنایی.

اگر امتیازها نزدیک باشند و عدم‌قطعیت بزرگ، آن ترتیب دقیق بیشتر از داده حرف می‌زند.

LMArena الان کنار Score، بازهٔ اطمینان و `Rank spread` (بازهٔ رتبه) نشان می‌دهد.

Rank spread یعنی: با عدم‌قطعیت فعلی، این مدل چه رتبه‌هایی را می‌تواند قابل‌دفاع داشته باشد. این خیلی بهتر از یک رتبهٔ قطعی است — هرچند همهٔ سوگیری‌ها را حل نمی‌کند.

پژوهش Huang و همکاران چیز جالبی نشان داد. رتبهٔ اول در Rankingهای مبتنی بر ترجیح، می‌تواند به حذف بخش بسیار کوچکی از رأی‌ها حساس باشد.

نتیجه این نیست که رأی انسانی بی‌ارزش است. نتیجه این است که پایداری رتبه خودش باید تست شود.

پس سه سؤال بپرسید. اگر نمونه کمی عوض شود، برنده می‌ماند؟ اگر Judge یا Prompt عوض شود چه؟ اگر وزن بخش‌ها عوض شود چه؟

اگر جواب هرکدام "نه" است، به‌جای جدول مدال، یک Tier یا فهرست مدعیان منتشر کنید.

رتبه‌بندی دقیق روی شواهدی که تابش را ندارند، اسم دارد: دقت کاذب.»

**در یک جمله:** وقتی رتبه با حذف چند رأی جابه‌جا می‌شود، آن رتبه یک یافته نیست.

### 13:30–15:25 — فاصلهٔ Lab تا Product

**تصویر:** یک Model در Lab رتبه ۱؛ در Product scenario به دلیل Cost، latency و failure rate گزینهٔ سوم.

**متن گفتاری:**

«فرض کنیم یک Benchmark از نظر روش عالی است. بی‌نقص.

هنوز یک سؤال مانده: آیا کاری که می‌سنجد شبیه تصمیم ماست؟

ترجیح انسان در گفت‌وگوی آزاد، برای تجربهٔ Chat مهم است. اما درستی Citation، هزینه یا تکمیل یک Workflow را مستقیم نمی‌سنجد.

MMLU دانش را روی یک قالب سؤال مشخص می‌سنجد. اما یک تیکت پشتیبانی واقعی نیست. گزارش تحقیق بازار هم نیست.

`External validity` (روایی بیرونی) به شباهت اسم کار ربطی ندارد. این‌ها باید نزدیک باشند: کاربر، اپراتور، داده، محدودیت، ریسک و میزان بازبینی انسانی.

پس یک Benchmark می‌تواند کاملاً معتبر باشد و برای Use case شما بی‌ربط. این تناقض نیست.

روایی همیشه برای یک تفسیر و یک کاربرد مشخص است. نه به‌طور مطلق.

برای همین کنار هر Score دو فیلد می‌گذاریم: `SUPPORTS` و `DOES NOT PROVE`.

و اگر دومی خالی باشد، بازاریابی جای روش‌شناسی نشسته است.»

**در یک جمله:** یک Benchmark می‌تواند بی‌نقص باشد و برای تصمیم شما هیچ حرفی نداشته باشد.

### 15:25–18:45 — Audit زندهٔ LMArena، بدون دادگاه نمایشی

**تصویر:** صفحهٔ LMArena، Methodology ranking، changelog، مقالهٔ Leaderboard Illusion و پاسخ LMArena در چهار Tab. Inspector ۱۵ موردی در راست.

**متن گفتاری:**

«حالا یک Benchmark واقعی را Audit کنیم: LMArena. پنج زاویه.

اول، Scope. Arena ترجیح انسان میان دو پاسخ ناشناس را می‌سنجد — روی توزیع کاربران و Promptهای خودش.

این شواهد برای ترجیح در گفت‌وگو ارزشمند است. برای صحت، ایمنی، هزینه یا Workflow محصول، به‌تنهایی کافی نیست.

پس روایی‌اش برای ادعای محدود سبز است. برای "بهترین مدل در همه‌چیز" قرمز.

دوم، Method. Arena روش Ranking، بازهٔ اطمینان و Rank spread را توضیح داده و Arena-Rank را Open source کرده. این شواهد قوی برای شفافیت محاسبه است.

سوم، Data و انگیزه. اینجا اختلاف هست.

مقالهٔ Leaderboard Illusion دربارهٔ تست Variantها و دسترسی نامتقارن هشدار می‌دهد. Arena پاسخ داده و بخشی از تحلیل را رد کرده.

ما اینجا سبز یا قرمز قطعی نمی‌زنیم. برچسب `CONFLICTING EVIDENCE` می‌گذاریم و هر دو منبع را باز نگه می‌داریم.

چهارم، Drift. Changelog نشان می‌دهد منبع رأی، تصحیح سوگیری و روش محاسبهٔ بازه عوض شده‌اند.

این ضعف پنهان نیست. نشانهٔ یک Benchmark زنده است. ولی هر تغییر باید یک Badge روی مقایسه‌پذیری تاریخی داشته باشد.

پنجم، Rank. Arena امتیاز، بازه و Rank spread دارد. بهتر از جدول مدال ساده است.

ولی پژوهش‌های پایداری رتبه یادآوری می‌کنند: بازهٔ اطمینان همهٔ حساسیت‌ها را پوشش نمی‌دهد — مثلاً حساسیت به حذف رأی یا به ترکیب مدل‌ها.

نتیجهٔ Audit: Arena برای سؤال خودش شواهد ارزشمندی دارد. اما هر رتبه‌اش باید همراه با تاریخ، دسته، Rank spread و مرز ادعا خوانده شود.

این نه حمله است نه تأیید کامل. مرز استفاده است.»

**در یک جمله:** Audit خوب حکم صادر نمی‌کند؛ می‌گوید این شواهد تا کجا اعتبار دارند و از کجا به بعد ندارند.

**کادر اجباری:**

`CASE STUDY STATUS MUST BE RECHECKED ON RECORDING DAY`

### 18:45–20:00 — حالا Benchmark خودمان را Red-team کنیم

**تصویر:** Risk register M2Lab با چهار ستون `RISK / EVIDENCE / MITIGATION / RESIDUAL`.

**متن گفتاری:**

«اگر Audit فقط برای دیگران باشد، تبدیل به محتوای ارزان می‌شود. پس همان پانزده سؤال را روی خودمان اجرا می‌کنیم.

چهل‌وهشت Case نمونهٔ احتمالی از تمام تحقیقات بازار نیست. زرد.

ابزارهای بسته Training data شفاف ندارند. ریسک آلودگی: نامعلوم.

Ground truth برای Actionability انسانی و محدود است. زرد.

یک Main run نوسان کامل را نمی‌سنجد. زرد.

نسخهٔ ابزار ممکن است وسط بازهٔ اجرا عوض شود. `Residual risk` (ریسک باقی‌مانده).

اقدامات کاهش داریم: Snapshot، Holdout، Run log، زیرنمونهٔ تکرارشونده، برچسب‌گذاری کور و Change log.

ولی رک بگویم — این اقدامات ریسک را جادویی پاک نمی‌کنند. فقط اندازه‌اش را کم می‌کنند و قابل‌دیدنش می‌کنند.

و مهم‌ترین تصمیم: ما یک Trust Score واحد منتشر نمی‌کنیم.

چرا؟ چون یک میانگین دیگر، دقیقاً همان ریسک‌هایی را پنهان می‌کند که در امتیاز مدل‌ها نقد کردیم.

به‌جایش: Profile لایه‌ای، یادداشت شواهد، و حق Veto برای Red flagهای بحرانی.

Risk register هم قبل از Main run فریز می‌شود. بعد از دیدن نتایج، دیگر نمی‌شود یک ریسک ناخوشایند را از صفحه پاک کرد.»

**در یک جمله:** همان چک‌لیستی که روی دیگران بردیم را روی خودمان می‌بریم — و نتیجه‌اش یک نمرهٔ اعتماد نیست، یک فهرست ریسک است.

### 20:00–20:45 — Verdict و ورود به اجرای واقعی

**تصویر:** پنج لایه `VALIDITY / DATA / PROTOCOL / METRICS / GOVERNANCE` و وضعیت‌های باز. سپس دکمه `START MAIN RUN`.

**متن گفتاری:**

«ظاهر علمی، اعتبار علمی نیست.

Dataset مشهور، نمونهٔ بزرگ، کد باز و بازهٔ اطمینان — هرکدام بخشی از شواهدند. هیچ‌کدام کل آن نیستند.

Audit خوب سه کار می‌کند. ادعا را کوچک می‌کند. ناشناخته‌ها را آشکار می‌کند. و مسیر اصلاح می‌سازد.

دو کاری هم که نمی‌کند: نیت کسی را حدس نمی‌زند، و همه‌چیز را دوباره در یک نمرهٔ اعتماد فشرده نمی‌کند.

حالا سؤال، Dataset، Metric، Protocol و Risk register ما فریز شده‌اند.

قسمت بعد دیگر تئوری نیست. Main run را اجرا می‌کنیم. خطاها را نگه می‌داریم. Claimها و Citationها را برچسب می‌زنیم.

و می‌بینیم داده واقعاً اجازهٔ گفتن چه چیزی را می‌دهد.»

**در یک جمله:** این قسمت هیچ جزء تازه‌ای اضافه نکرد — به چهار جزء موجود حمله کرد و آنچه سالم ماند را نوشت.

**پایان روی تصویر:**

`NEXT: THE REAL RUN`

---

## 7. Evidence Status Profile برای Case study

این جدول در روز ضبط با لینک و تاریخ به‌روزرسانی شود؛ Status زیر نتیجهٔ نهایی از پیش‌ساخته نیست.

| سؤال | Evidence مورد نیاز | Status مجاز |
|---|---|---|
| Scope دقیق چیست؟ | How-it-works + methodology | Green/Yellow |
| Prompt population چگونه شکل می‌گیرد؟ | public data/method note | Green/Yellow/Unknown |
| Variant submission policy چیست؟ | policy + independent audit + response | Conflicting evidence |
| Ranking چگونه محاسبه می‌شود؟ | open method/code | Green/Yellow |
| CI و rank spread وجود دارد؟ | current leaderboard | Green/Red |
| Bias position/style کنترل می‌شود؟ | method/changelog | Green/Yellow/Unknown |
| Version و Date روشن‌اند؟ | model row/changelog | Green/Yellow |
| Correction/appeal وجود دارد؟ | governance page | Green/Yellow/Unknown |
| Claim خارج از Scope محدود شده؟ | product copy + reporting | Green/Yellow/Red |

---

## 8. طراحی تجربهٔ بصری

### صحنهٔ اصلی: Leaderboard X-Ray

- حالت اول: Leaderboard تمیز و وسوسه‌کننده؛
- کلیک روی هر Rank: Score، CI، Rank spread، N، Date و Category؛
- X-Ray: Data، Protocol، Judge، Incentive و Claim boundary پشت ردیف باز شوند؛
- Audit inspector در راست: Green/Yellow/Red/Unknown؛
- Source drawer: Claim، منبع موافق، منبع مخالف و پاسخ Method owner؛
- دکمه `SHOW WHAT THIS DOES NOT PROVE` باید قاب را تغییر دهد.

### Interactionهای امضادار

1. `REMOVE 0.1%`: Rank robustness را با دادهٔ نمایشی نشان دهد؛ عدد واقعی فقط از Paper.
2. `CHANGE PROMPT POLICY`: Rank sensitivity نمایش داده شود.
3. `OPEN DISCARDED RUNS`: Result funnel آشکار شود.
4. `AUDIT THIS CLAIM`: مسیر ۱۵ سؤال باز شود.
5. `CONFLICTING EVIDENCE`: دو Source کنار هم، بدون Verdict مصنوعی.

### قاعدهٔ اخلاقی تصویر

از لوگو، تصویر یا تیتر LMArena برای القای Fraud استفاده نشود. Case study دربارهٔ Methodology و Evidence dispute است؛ پاسخ LMArena باید همان‌قدر قابل مشاهده باشد که مقالهٔ انتقادی.

---

## 9. سایت‌هایی که باید نمایش داده شوند

| زمان | سایت | نمایش | نکته |
|---|---|---|---|
| 06:40 | The Leaderboard Illusion | Abstract + claimهای اصلی | یک مطالعهٔ انتقادی، نه حکم نهایی |
| 07:25 | LMArena response | پاسخ دربارهٔ CI و submission policy | اختلاف Evidence را صادقانه نشان بده |
| 11:15 | LMArena Ranking Method | Rank spread و CI | روش جاری را روز ضبط دوباره چک کن |
| 12:10 | Arena-Rank | کد/روش Open source | Transparency محاسبه را نشان بده |
| 12:45 | Quantifying Ranking Uncertainty | Rank CI concept | اختلاف Score با قطعیت Rank یکی نیست |
| 15:25 | LMArena leaderboard/changelog | Category، Date، Votes، method changes | عدد زنده Hard-code نشود |
| 18:45 | NIST AI 800-2 | qualified claims/reporting | مرز Interpretation را وصل کن |

---

## 10. چک‌لیست علمی قبل از ضبط

- [ ] همهٔ وضعیت‌های زندهٔ LMArena در روز ضبط بازبینی شده‌اند.
- [ ] مقالهٔ انتقادی و پاسخ LMArena هر دو نمایش داده می‌شوند.
- [ ] Goodhart به‌عنوان هشدار تحلیلی است، نه اثبات Manipulation.
- [ ] Contamination، Leakage و Awareness قاطی نشده‌اند.
- [ ] Saturation با «همه مدل‌ها کامل‌اند» یکی نشده است.
- [ ] Rank instability به «Leaderboard بی‌ارزش است» تعمیم داده نشده است.
- [ ] CI، Rank spread و Robustness test از هم تفکیک شده‌اند.
- [ ] Unknown به Red یا Score صفر تبدیل نشده است.
- [ ] Trust Score جای Evidence profile را نگرفته است.
- [ ] Riskهای خود M2Lab قبل از نقد دیگران نشان داده شده‌اند.
- [ ] هیچ Rank زنده‌ای داخل متن Hard-code نشده است.
- [ ] نام Tool/سازمان برای Thumbnail اتهامی استفاده نشده است.

---

## 11. بستهٔ ضبط

### A-roll حذف‌ناپذیر

- Score درست / Claim غلط؛
- Incentive و Goodhart؛
- Riskهای Data، Protocol، Judge و Ranking؛
- تحلیل دوطرفهٔ LMArena؛
- Audit خود M2Lab؛
- Unknown و Conflicting evidence.

### B-roll و Screen recording

- Leaderboard X-Ray؛
- Variant/result funnel؛
- Data lineage؛
- Rank spread؛
- مقاله، پاسخ و changelog؛
- ۱۵-point audit؛
- Risk register پروژه.

### Pattern interrupt

- 00:30: X-Ray؛
- 05:50: Result funnel؛
- 10:50: Rank spread؛
- 15:25: Audit mode؛
- 18:45: Self-audit.

---

## 12. CTA نهایی

> «یک Benchmark مورداعتماد خودتان را باز کنید و فقط پنج سؤال را جواب دهید: Claim چیست؟ Data از کجا آمده؟ Protocol چیست؟ Rank چقدر نامطمئن است؟ و Result چه چیزی را ثابت نمی‌کند؟ هرجا Evidence پیدا نکردید، Unknown بنویسید—نه صفر و نه حدس.»

**Comment prompt:**

> کدام علامت هشدار اعتماد شما را سریع‌تر متوقف می‌کند: Data نامشخص، Prompt پنهان، Judge بدون Audit، Rank بدون Uncertainty یا نبود Change Log؟

---

## 13. منابع اصلی این قسمت

1. Singh et al., [The Leaderboard Illusion](https://arxiv.org/abs/2504.20879), 2025.
2. LMArena, [Our Response to “The Leaderboard Illusion”](https://lmarena.ai/blog/our-response/), 2025.
3. LMArena, [Arena’s Ranking Method](https://news.lmarena.ai/ranking-method/), current methodology page.
4. LMArena, [Arena-Rank: Open Sourcing the Leaderboard Methodology](https://news.lmarena.ai/arena-rank/), 2025.
5. LMArena, [Leaderboard Changelog](https://news.lmarena.ai/leaderboard-changelog/), accessed August 2026.
6. Huang et al., [Dropping Just a Handful of Preferences Can Change Top Large Language Model Rankings](https://arxiv.org/abs/2508.11847), 2025/2026.
7. Neuhof and Benjamini, [Quantifying Ranking Uncertainty in LLM Benchmarks](https://arxiv.org/abs/2607.16259), 2026.
8. Zheng et al., [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685), 2023.
9. NIST, [Practices for Automated Benchmark Evaluations of Language Models — NIST AI 800-2 IPD](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf), January 2026.
10. Madaan et al., [Quantifying Variance in Evaluation Benchmarks](https://arxiv.org/abs/2406.10229), 2024.

---

## 14. خطاهای ممنوع

- متهم‌کردن سازمان یا Vendor به دستکاری بدون Evidence مستقیم؛
- حذف پاسخ یا اصلاحات Method owner؛
- استفاده از Rank زنده بدون Date/Category/Version؛
- تبدیل اختلاف علمی به Drama شخصی؛
- معرفی Open source methodology به‌عنوان تضمین Validity؛
- معرفی Sample بزرگ به‌عنوان درمان Bias؛
- ساخت Trust Score واحد بدون Evidence page؛
- پنهان‌کردن Riskهای خود پروژهٔ M2Lab.

