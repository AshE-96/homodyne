# M2Lab Benchmarking Foundations — Episode 03

## How to Design the Right Benchmark Task

**نسخه:** 1.0 — آمادهٔ ضبط  
**زبان روایت:** فارسی  
**زبان عناصر روی تصویر:** انگلیسی  
**زمان هدف:** 18:00 تا 19:30  
**خروجی این قسمت:** `Benchmark Specification v0.1`  
**پروژهٔ فصل:** قفل‌کردن سؤال مقایسهٔ ابزارهای Deep Research پیش از ساخت Dataset

---

## 1. قول این قسمت به مخاطب

در پایان قسمت، مخاطب می‌تواند یک سؤال مبهم مثل «بهترین ابزار AI برای تحقیق بازار کدام است؟» را به یک Specification قابل‌اجرا و قابل‌نقد تبدیل کند.

جملهٔ محوری:

> **A perfect score on the wrong task is still the wrong answer.**

قاعدهٔ عملی:

> **Decision → Construct → Task → Unit → Scope → Baseline → Claim boundary**

این قسمت باید یک «تبدیل» را جلوی چشم مخاطب انجام دهد. ابتدا سؤال باز و تبلیغاتی است؛ در پایان، سندی داریم که مشخص می‌کند چه تصمیمی پشتیبانی می‌شود، چه چیزی اندازه‌گیری می‌شود و نتیجه درباره چه چیزهایی حق ادعا ندارد.

---

## 2. مسئلهٔ روایی

### THE CLAIM

«برای ساخت Benchmark، اول باید سؤال‌ها و Dataset را جمع کنیم.»

### THE EVIDENCE

اگر Measurement target، Intended use و Construct روشن نباشند، Dataset فقط مجموعه‌ای از مثال‌هاست که ممکن است Task اشتباهی را با دقت بالا بسنجد. پیش‌نویس NIST AI 800-2 نیز فرایند را با تعریف Measurement target شروع می‌کند، سپس به اجرا و بعد تحلیل/گزارش می‌رسد.

### THE STRESS TEST

دو Benchmark را با Dataset و مدل‌های یکسان اجرا می‌کنیم؛ فقط Definition of success را تغییر می‌دهیم. در یکی ابزار پرجزئیات برنده است؛ در دیگری ابزار دقیق و مختصر. نتیجه نشان می‌دهد «بهتر» بدون تصمیم و Boundary معنای مستقل ندارد.

### THE VERDICT

Benchmark از Specification شروع می‌شود، نه Dataset. Specification جلوی تمام Biasها را نمی‌گیرد، اما تغییر پنهانی سؤال پس از دیدن نتیجه را قابل‌مشاهده می‌کند.

### THE BUILD

Specification پروژهٔ فصل را جلوی دوربین کامل و نسخهٔ `v0.1` آن را با تاریخ و Change Log Freeze می‌کنیم.

---

## 3. تئوری علمی، به زبان اجرایی

### 3.1 Intended use

نتیجه قرار است چه تصمیمی را بهتر کند؟

- انتخاب Tool برای Pilot؟
- انتخاب Model برای Production؟
- تشخیص Risk؟
- مقایسهٔ نسخهٔ جدید با Baseline؟
- ادعای عمومی دربارهٔ Capability؟

هر Intended use به Evidence متفاوت نیاز دارد. Score مفید برای Iteration داخلی الزاماً برای ادعای عمومی کافی نیست.

### 3.2 Construct

Construct مفهوم مورد اندازه‌گیری است؛ مثل «کیفیت تحقیق بازار»، «Factuality»، «توانایی حل Issue» یا «کاربردپذیری برای Founder».

Construct معمولاً مستقیماً قابل‌مشاهده نیست. آن را با Task و Metric عملیاتی می‌کنیم. خطر اصلی Construct underrepresentation و Construct-irrelevant variance است:

- `Underrepresentation`: فقط بخش کوچکی از مفهوم را سنجیده‌ایم؛ مثلاً کیفیت تحقیق را فقط با تعداد منابع.
- `Irrelevant variance`: چیز دیگری Score را تغییر می‌دهد؛ مثلاً سرعت تایپ Operator، کیفیت UI یا طول پاسخ.

### 3.3 Task

Task عملی است که سیستم باید انجام دهد. Task باید ورودی، Context، ابزار مجاز، خروجی و Success condition روشن داشته باشد.

### 3.4 Unit of evaluation

کوچک‌ترین واحدی که Score روی آن ساخته می‌شود:

- Report
- Case
- Claim
- Citation
- Action item
- Run

اگر Unit روشن نباشد، ممکن است ۲٬۰۰۰ Claim داخل ۴۸ Report را مثل ۲٬۰۰۰ مشاهدهٔ مستقل تحلیل کنیم و عدم‌قطعیت را کمتر از واقع نشان دهیم.

### 3.5 Scope و Constraints

Population، زبان، جغرافیا، صنعت، Stage شرکت، دادهٔ مجاز، زمان، بودجه، ابزار و نوع Output را محدود می‌کنند. Scope کوچک‌تر به معنی Benchmark ضعیف‌تر نیست؛ به معنی ادعای دقیق‌تر است.

### 3.6 Baseline و Comparator

Baseline باید یک جایگزین واقعی و قابل‌اجرا باشد:

- Human-only workflow
- Search + spreadsheet
- ابزار فعلی تیم
- نسخهٔ قبلی سیستم
- Rule-based یا random baseline، اگر با تصمیم مرتبط است

عبارت «روش سنتی» Baseline نیست؛ فرایند، زمان، ابزار و خروجی باید تعریف شود.

### 3.7 Claim boundary

نتیجه حداکثر چه ادعایی را پشتیبانی می‌کند و چه چیزی را ثابت نمی‌کند؟

الگوی M2Lab:

> **Useful for [decision], under [conditions]. Weak when [boundary]. Does not prove [excluded claim].**

### 3.8 Freeze و Change Log

Freeze به معنی ممنوع‌کردن یادگیری نیست. Pilot می‌تواند Specification را بهتر کند؛ اما تغییر باید با تاریخ، دلیل و اینکه قبل یا بعد از دیدن نتیجه بوده ثبت شود. Analysis اکتشافی مجاز است، به شرطی که بعداً به‌عنوان فرضیهٔ ازپیش‌تعیین‌شده معرفی نشود.

---

## 4. فلو زمانی نهایی

| زمان | Beat | هدف | Proof object |
|---|---|---|---|
| 00:00–01:10 | Wrong question, perfect score | ایجاد تنش | ترازو روی شیء اشتباه |
| 01:10–03:10 | Decision before dataset | تعریف Measurement target | NIST three-stage flow |
| 03:10–05:20 | Construct vs proxy | دیدن خطای مفهومی | evidence circle vs claim circle |
| 05:20–08:10 | User, task, unit | عملیاتی‌کردن مفهوم | report → claim → citation |
| 08:10–10:50 | Scope and constraints | محدودکردن جهان ادعا | boundary box |
| 10:50–12:50 | Baseline and comparator | جلوگیری از رقابت مصنوعی | Search + Sheet baseline |
| 12:50–16:15 | Live build | تکمیل Specification | سند زندهٔ v0.1 |
| 16:15–17:40 | Freeze and change log | جداسازی planned/exploratory | Git diff / timestamp |
| 17:40–18:40 | Verdict and bridge | ورود به Dataset | specification → sampling grid |

---

## 5. متن کامل آمادهٔ ضبط

### 00:00–01:10 — سؤال اشتباه، امتیاز بی‌نقص

**ON SCREEN:** `THE CLAIM`  
**HEADLINE:** `WRONG QUESTION. PERFECT SCORE.`

**تصویر:** یک ترازوی دقیق، وزن یک جعبه را میلی‌گرمی نشان می‌دهد؛ سپس معلوم می‌شود سؤال واقعی حجم جعبه بوده است.

**متن گفتاری:**

«این ترازو کاملاً دقیق است. عدد را بدون خطا می‌دهد. اما اگر سؤال من این باشد که این جعبه داخل قفسه جا می‌شود یا نه، این اندازه‌گیری—با تمام دقتش—جواب سؤال من نیست.

Benchmark هم می‌تواند دقیق، تکرارپذیر و از نظر فنی بی‌نقص باشد، اما Construct یا Task اشتباهی را بسنجد. آن‌وقت Score جعلی نیست؛ تفسیر ما غلط است.

سؤال اولیهٔ پروژهٔ ما این بود: بهترین ابزار Deep Research کدام است؟ این سؤال جذاب است، ولی قابل‌آزمایش نیست. بهترین برای چه کسی؟ برای چه کاری؟ با چه بودجه‌ای؟ چه چیزی باید بهتر شود؟ و اگر یک ابزار Report طولانی‌تری ساخت، آیا واقعاً بهتر تحقیق کرده یا فقط بیشتر نوشته است؟

امروز قبل از ساخت Dataset، سؤال را قفل می‌کنیم. چون اگر سؤال را قفل نکنیم، بعد از دیدن نتیجه می‌توانیم تعریف “بهتر” را طوری تغییر دهیم که داستان دلخواه‌مان برنده شود.»

### 01:10–03:10 — Benchmark برای تصمیم ساخته می‌شود

**ON SCREEN:** `THE MODEL`  
**HEADLINE:** `DEFINE THE MEASUREMENT TARGET FIRST.`

**تصویر:** سه مرحلهٔ `DEFINE → RUN → ANALYZE & REPORT`؛ کنار آن برچسب `NIST AI 800-2 / INITIAL PUBLIC DRAFT / JAN 2026`.

**متن گفتاری:**

«پیش‌نویس NIST AI 800-2 فرایند Automated benchmark evaluation را در سه مرحله می‌چیند: تعریف Measurement target؛ پیاده‌سازی و اجرای Evaluation؛ و تحلیل و گزارش نتیجه. ترتیب مهم است.

در مرحلهٔ اول باید دو سؤال را جواب بدهیم: نتیجه چگونه استفاده می‌شود، و چه مفهومی باید اندازه‌گیری شود؟

برای پروژهٔ ما Intended use این نیست که “باهوش‌ترین مدل دنیا” را اعلام کنیم. تصمیم محدودتر است: یک Founder غیرفنی برای تحقیق اولیهٔ بازار، کدام ابزار را وارد Pilot کاری خود کند؟

این تفاوت کوچک نیست. اگر هدف Research باشد، Citation support، پوشش Fact، Actionability، زمان و هزینه مهم‌اند. اگر هدف نوشتن مقاله باشد، معیارهای دیگری وارد می‌شوند. اگر هدف Due diligence مالی باشد، Risk و استاندارد شواهد شدیدتر می‌شوند.

پس Benchmark از سؤال “کدام ابزار بالاتر است؟” شروع نمی‌شود. از سؤال “این Evidence قرار است کدام تصمیم را بهتر کند؟” شروع می‌شود.»

### 03:10–05:20 — Construct را با Proxy اشتباه نگیریم

**ON SCREEN:** `WHAT THE SCORE SEES`  
**HEADLINE:** `THE METRIC SEES A PROXY—NOT THE WHOLE CONSTRUCT.`

**تصویر:** دو دایره. دایرهٔ بزرگ `MARKET RESEARCH QUALITY` و دایرهٔ کوچک‌تر `OBSERVED EVIDENCE` شامل citation، coverage، actionability، time، cost.

**متن گفتاری:**

«Construct ما “کیفیت و usefulness تحقیق بازار برای تصمیم اولیهٔ Founder” است. این مفهوم را نمی‌توان مستقیم داخل یک سلول Spreadsheet گذاشت. باید آن را با Evidence قابل‌مشاهده عملیاتی کنیم.

Citation support بخشی از Construct را می‌بیند، نه همهٔ آن را. تعداد Factها پوشش را می‌بیند، نه اولویت‌بندی را. Rubric قابلیت اقدام را می‌بیند، ولی ممکن است سلیقهٔ Annotator را وارد کند. زمان و هزینه Efficiency را می‌بینند، نه Truth را.

دو خطای رایج داریم. اول، Construct underrepresentation: بخش بزرگی از مفهوم اصلاً وارد تست نشده؛ مثلاً فقط تعداد لینک را می‌شماریم و اسمش را “کیفیت تحقیق” می‌گذاریم.

دوم، Construct-irrelevant variance: چیزهایی که جزء مفهوم نیستند Score را تکان می‌دهند. مثلاً یک Tool به‌خاطر UI بهتر سریع‌تر استفاده می‌شود، یا یک Report طولانی‌تر در Rubric کلی امتیاز بیشتر می‌گیرد.

راه‌حل، ادعای کامل‌بودن نیست. باید دقیق بگوییم چه Evidenceهایی داریم و چه بخش‌هایی بیرون مانده‌اند.»

### 05:20–08:10 — User، Operator، Task و Unit

**ON SCREEN:** `THE EVIDENCE`  
**HEADLINE:** `A TASK NEEDS AN OPERATOR, AN OUTPUT, AND A UNIT.`

**متن گفتاری:**

«حالا سؤال را عملیاتی می‌کنیم.

User هدف Founder غیرفنی است؛ کسی که می‌خواهد دربارهٔ یک بازار ناآشنا تصمیم اولیه بگیرد. Operator در Run اصلی خود من هستم، با دستورالعمل ثابت. این دو را جدا می‌نویسیم، چون مهارت Operator می‌تواند نتیجه را تغییر دهد.

Task این است: از یک Brief استاندارد، ظرف حداکثر سی دقیقه و سقف هزینهٔ ده دلار، Report انگلیسی تولید شود که تعریف بازار، بازیگران، شواهد تقاضا، ریسک‌ها، Unknownها و Next stepها را با Citation ارائه دهد.

خروجی اصلی یک Report است؛ اما Unit ارزیابی فقط Report نیست. برای Factuality، Unit یک Claim است. برای Citation support، یک Claim–source pair. برای Actionability، یک Action item. برای Cost و latency، یک Run موفق.

چرا Unit مهم است؟ چون اگر داخل ۴۸ Report دو هزار Claim داشته باشیم، دو هزار Case مستقل نداریم. Claimهای یک Report Context، Prompt و Sourceهای مشترک دارند. اگر این وابستگی را فراموش کنیم، Confidence کاذب می‌سازیم.

در صفحه این سلسله‌مراتب را می‌بینید: Benchmark شامل Caseها؛ هر Case یک Report؛ هر Report شامل Claim، Citation و Action item. Score باید بداند روی کدام لایه ساخته می‌شود.»

### 08:10–10:50 — Scope: مرزی که نتیجه را صادق نگه می‌دارد

**ON SCREEN:** `DOES NOT PROVE`  
**HEADLINE:** `A NARROW CLAIM CAN BE STRONGER.`

**متن گفتاری:**

«حالا جهان آزمایش را محدود می‌کنیم.

زبان خروجی انگلیسی است. داده فقط از وب عمومی می‌آید. Use case تحقیق اولیهٔ بازار است، نه Due diligence حقوقی یا توصیهٔ سرمایه‌گذاری. صنایع B2B و B2C را داریم، ولی بازارهای کاملاً محرمانه یا نیازمند Database پولی بیرون‌اند. ابزارها در نسخه و بازهٔ زمانی مشخص اجرا می‌شوند. هر Case سقف زمان و هزینه دارد.

این Scope شاید کوچک به نظر برسد، اما ادعای کوچک‌تر معمولاً قابل‌دفاع‌تر است. اگر خروجی فارسی را آزمایش نکرده‌ایم، دربارهٔ فارسی نتیجه نمی‌دهیم. اگر فقط Founder غیرفنی را مدل کرده‌ایم، دربارهٔ تیم حرفه‌ای Market intelligence حکم نمی‌دهیم. اگر ابزار را با حساب پولی تست کرده‌ایم، نتیجه را به Free tier تعمیم نمی‌دهیم.

Claim boundary نسخهٔ اول این است: نتیجه می‌تواند انتخاب ابزار برای Pilot تحقیق اولیهٔ بازار، در شرایط همین Dataset و Protocol، را پشتیبانی کند. نتیجه ثابت نمی‌کند یک ابزار برای تمام انواع Research، تمام زبان‌ها یا همهٔ کاربران بهترین است.

Scope disclaimer نیست که آخر ویدئو پنهان شود. بخشی از خود نتیجه است.»

### 10:50–12:50 — Baseline واقعی، نه رقیب ضعیف نمایشی

**ON SCREEN:** `THE STRESS TEST`  
**HEADLINE:** `A MODEL SHOULD BEAT THE REAL ALTERNATIVE.`

**تصویر:** فرایند `SEARCH → SHEET → VERIFY → SYNTHESIZE` با Timer و خروجی.

**متن گفتاری:**

«اگر فقط Toolهای AI را با هم مقایسه کنیم، ممکن است همه از جایگزین واقعی بدتر باشند. بنابراین Baseline لازم است.

Baseline پروژهٔ ما یک Workflow دستی Search + spreadsheet است: جست‌وجوی وب با Queryهای ازپیش‌تعریف‌شده، ثبت Fact و Source در Sheet، بررسی Claimهای بحرانی و ساخت Summary با Template ثابت. همان زمان و همان نوع خروجی را ثبت می‌کنیم.

عبارت “روش سنتی” کافی نیست. باید مشخص کنیم چه کسی، با چه تجربه‌ای، از چه ابزارهایی، چند دقیقه و با چه Templateی کار کرده است. NIST در بحث Baseline هم تأکید می‌کند که شرایط Comparator—از ابزار تا خصوصیات انسان—باید Context داشته باشد.

علاوه بر Baseline دستی، دو Track برای Toolها داریم. Track استاندارد: Prompt و Budget یکسان برای مقایسهٔ کنترل‌شده. Track بهینه‌شده: هر Tool با Workflow منطقی و قابلیت‌های خودش، اما با همان خروجی و سقف منابع. اولی Comparability بیشتری می‌دهد؛ دومی Best achievable system را بهتر منعکس می‌کند. این دو را با هم مخلوط نمی‌کنیم.»

### 12:50–16:15 — ساخت زندهٔ Specification نسخهٔ 0.1

**ON SCREEN:** `THE BUILD`  
**تعامل:** یک سند خالی در سمت راست با تکمیل هر فیلد، سؤال مبهم در سمت چپ کوتاه و دقیق شود.

**متن گفتاری:**

«حالا سند را کامل کنیم.

نام: M2Lab Deep Research for Startup Market Research Benchmark، نسخهٔ صفر ممیز یک.

Decision: انتخاب حداکثر دو Tool برای Pilot یک Founder غیرفنی.

Primary user: Founder غیرفنی در مرحلهٔ Discovery. Operator: ارزیاب آموزش‌دیده با SOP ثابت.

Construct: کیفیت شواهد و usefulness تصمیمی Report تحقیق اولیهٔ بازار، تحت زمان و هزینهٔ محدود.

Task: تولید Report انگلیسی از Brief استاندارد، با تعریف بازار، رقبا، شواهد تقاضا، ریسک، Unknown و Next step؛ فقط با دادهٔ عمومی وب.

Primary unit: Case. Nested units: Report، Claim، Citation، Action item و Run.

Candidate systems: حداکثر پنج Tool مشخص با Plan، Region، date و version ثبت‌شده.

Baseline: Workflow دستی Search + Sheet با Template ثابت.

Constraints: حداکثر سی دقیقه و ده دلار برای هر Case؛ بدون دخالت انسانی در متن خروجی بعد از Submit؛ Failure و Timeout در داده باقی می‌مانند.

Primary outcome: Citation support در سطح Claim، چون بدون شواهد قابل‌ردیابی، Report تحقیق بازار قابل اتکا نیست.

Secondary outcomes: پوشش Factهای لازم، Factual accuracy، Actionability، زمان، هزینه و Robustness روی Sliceهای سخت.

Guardrails: منبع ساختگی و Critical factual error. Threshold دقیق در قسمت Metric پیش از Main run Freeze می‌شود.

Claim boundary: مقایسه فقط برای Toolها، نسخه‌ها، Dataset، زبان، بازهٔ زمانی و Protocol ثبت‌شده معتبر است. دربارهٔ بهترین مدل پایه یا بهترین Tool برای همهٔ Researchها ادعا نمی‌کند.

این سند هنوز Dataset و Metric کامل ندارد؛ اما اکنون می‌دانیم چه Datasetی لازم است و هر Case باید کدام جهان و Failure را نمایندگی کند.»

### 16:15–17:40 — Freeze، Preregistration و Change Log

**ON SCREEN:** `MEASURED, NOT ASSUMED`  
**HEADLINE:** `FREEZE THE QUESTION BEFORE THE ANSWER.`

**تصویر:** Commit با Tag `spec-v0.1`, timestamp و یک Change Log خالی.

**متن گفتاری:**

«چرا نسخه را قبل از Run ثبت می‌کنیم؟ چون بعد از دیدن نتیجه، صدها انتخاب کوچک داریم: حذف یک Case، تغییر وزن، جابه‌جایی Threshold یا انتخاب Slice جذاب‌تر. هرکدام ممکن است منطقی به نظر برسد، اما اگر فقط بعد از دیدن Winner اتفاق بیفتد، روایت نتیجه را شکل می‌دهد.

در پروژهٔ کوچک لازم نیست Registry دانشگاهی بسازیم. یک فایل Methodology، تاریخ، Git commit و Change Log کافی است. اگر Formal preregistration بخواهیم، OSF امکان نسخهٔ timestamped و read-only از Plan را می‌دهد.

Freeze به معنی ممنوع‌کردن تغییر نیست. Pilot برای پیدا کردن مشکل است. هر تغییر را ثبت می‌کنیم: چه چیزی تغییر کرد؟ چرا؟ قبل یا بعد از دیدن کدام نتیجه؟ و چه اثری ممکن است روی Ranking داشته باشد؟

Exploratory analysis هم ارزشمند است. فقط برچسبش را عوض نمی‌کنیم. چیزی که بعد از دیدن داده کشف شده، Discovery است؛ نه Hypothesis ازپیش‌تعریف‌شده.»

### 17:40–18:40 — Verdict و ورود به Dataset

**ON SCREEN:** `THE VERDICT`

**متن گفتاری:**

«Specification خوب هفت چیز را قفل می‌کند: Decision، Construct، Task، Unit، Scope، Baseline و Claim boundary.

این سند تضمین نمی‌کند Benchmark بی‌نقص باشد. اما به دیگران اجازه می‌دهد قبل از دیدن Score بپرسند آیا سؤال درست انتخاب شده است یا نه؛ و بعد از نتیجه ببینند کدام قواعد تغییر کرده‌اند.

Rule این قسمت: اگر نمی‌توانید Decision و Claim boundary را هرکدام در یک جمله بنویسید، هنوز برای جمع‌کردن Dataset آماده نیستید.

در قسمت بعد، جهان داخل Specification را به ۴۸ Case تبدیل می‌کنیم. می‌بینیم چرا Dataset فقط انبار سؤال نیست، چگونه Sampling grid می‌سازیم، چه زمانی Synthetic data مفید است و وقتی پاسخ درست واحد نداریم، Ground truth را چگونه تعریف می‌کنیم.

در کامنت فقط این جمله را برای محصول خود کامل کنید: این Benchmark قرار است تصمیمِ ... را بهتر کند، اما دربارهٔ ... ادعا نمی‌کند.»

---

## 6. Benchmark Specification نهایی پروژه

| فیلد | نسخهٔ v0.1 |
|---|---|
| Benchmark name | M2Lab Deep Research for Startup Market Research Benchmark |
| Intended decision | انتخاب حداکثر دو Tool برای Pilot |
| Primary user | Founder غیرفنی در مرحلهٔ Discovery |
| Operator | ارزیاب آموزش‌دیده با SOP ثابت |
| Construct | Evidence quality + decision usefulness under constraints |
| Task | تولید Report انگلیسی تحقیق اولیهٔ بازار از Brief استاندارد |
| Primary unit | Case؛ با واحدهای تو‌در‌توی Report، Claim، Citation، Action item و Run |
| Population | Use caseهای B2B/B2C با دادهٔ عمومی وب در Scope تعریف‌شده |
| Input | Brief استاندارد + required outputs |
| Output | Report با market، competitors، demand evidence، risks، unknowns، next steps و citations |
| Budget | ≤ 30 دقیقه و ≤ 10 دلار برای هر Case |
| Candidate systems | حداکثر ۵ Tool با plan/version/date/region ثبت‌شده |
| Baseline | Search + Sheet + verification + synthesis template |
| Tracks | Standardized و Optimized؛ جداگانه گزارش می‌شوند |
| Primary outcome | Claim-level citation support |
| Secondary | Coverage، factual accuracy، actionability، time، cost، robustness |
| Guardrails | Fabricated source و critical factual error |
| Exclusions | فارسی، دادهٔ خصوصی، Due diligence حقوقی/مالی، expert workflow |
| Claim boundary | فقط برای Tool، Dataset، Protocol، version و window ثبت‌شده |
| Freeze | Git tag `spec-v0.1` + date + change log |

---

## 7. طراحی تجربهٔ بصری

### صحنهٔ اصلی: Specification Builder

- سمت چپ: سؤال مبهم با کلمات برجستهٔ `BEST / AI / RESEARCH`.
- وسط: زنجیرهٔ `DECISION → CONSTRUCT → TASK → UNIT → SCOPE → BASELINE → CLAIM`.
- سمت راست: Inspector هر فیلد با `WHY IT EXISTS / EXAMPLE / FAILURE IF MISSING`.
- با تکمیل هر فیلد، سؤال اولیه کوچک‌تر و دقیق‌تر شود.
- در انتها Button نمایشی `FREEZE v0.1` سند را با Timestamp قفل کند.
- Toggle `SHOW WHAT CHANGED` تفاوت Draft و Freeze را نشان دهد.

### Proof objectهای اصلی

1. ترازو روی Object اشتباه.
2. Evidence circle داخل Construct circle.
3. Report → Claim → Citation hierarchy.
4. Scope boundary box.
5. Baseline manual workflow با Timer.
6. Standardized vs Optimized tracks.
7. Specification Builder.
8. Git diff و Change Log.

---

## 8. سایت‌هایی که باید نمایش داده شوند

| زمان | سایت | بخش | نکتهٔ گفتاری | زمان نمایش |
|---|---|---|---|---:|
| 01:30 | [NIST AI 800-2 IPD](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf) | Abstract، سه مرحله | «Measurement target قبل از Run می‌آید.» | 18 ثانیه |
| 02:20 | [NIST AI 800-2 — Intended uses](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf) | Practice 1.1، صفحات ۷ تا ۹ | «استفاده از نتیجه و Construct باید مستند شوند.» | 15 ثانیه |
| 04:15 | [HELM](https://crfm.stanford.edu/helm/) | Scenarios و Metrics | «یک Scenario را با چند Metric می‌بینیم؛ یک Proxy کل Construct نیست.» | 15 ثانیه |
| 11:35 | [NIST baseline guidance](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf) | صفحهٔ ۱۱، validated baselines | «Comparator باید جایگزین واقعی و شرایطش روشن باشد.» | 12 ثانیه |
| 16:45 | [OSF Preregistration](https://www.cos.io/initiatives/prereg) | planned vs unplanned work | «هدف، ممنوع‌کردن Exploration نیست؛ تفکیک planned و discovered است.» | 15 ثانیه |
| 17:05 | یک Repository محلی | `benchmark_spec_v0.1.md` و Git commit | «برای پروژهٔ کوچک همین Record کافی است.» | 15 ثانیه |

**یادداشت:** NIST AI 800-2 در روز ضبط باید با عبارت `Initial Public Draft — January 2026` معرفی شود.

---

## 9. چک‌لیست علمی قبل از ضبط

- Construct را مترادف Metric نگو؛ Metric فقط Operationalization یا بخشی از Evidence است.
- Specification را تضمین Validity معرفی نکن؛ ابزار شفافیت و کنترل تغییر است.
- Preregistration را جایگزین طراحی خوب، Peer review یا Replication ندان.
- `۴۸ Case` را در این قسمت به‌عنوان Sample کافی برای جهان معرفی نکن.
- Standardized و Optimized track را در یک Ranking مخلوط نکن.
- Baseline انسانی را بدون مهارت، ابزار، زمان و Incentive گزارش نکن.
- Claimهای داخل یک Report را کاملاً مستقل فرض نکن.
- Scope محدود را عذرخواهی یا ضعف نمایش نده؛ شرط نتیجهٔ قابل‌دفاع است.
- NIST AI 800-2 را سند نهایی یا الزام قانونی معرفی نکن.

---

## 10. بستهٔ ضبط

### A-roll حذف‌ناپذیر

- Cold open با مثال ترازو.
- توضیح Decision و Intended use.
- Construct vs proxy.
- Unit hierarchy.
- Baseline manual.
- تکمیل زندهٔ Specification.
- Freeze و Change Log.
- Rule نهایی.

### Screen recording

- Specification Builder خالی تا v0.1.
- Baseline Search + Sheet در ۲۰ تا ۳۰ ثانیهٔ Time-lapse.
- Standardized و Optimized Prompt کنار هم.
- Git commit و `CHANGELOG.md`.

### نقاط مناسب Pattern interrupt

- 00:28: مکث روی «عدد درست، جواب غلط».
- 04:40: کوچک‌شدن Evidence circle.
- 07:10: شکستن Report به Claim/Citation.
- 11:20: ورود Timer به Baseline.
- 13:00: شروع Live build.
- 16:40: صدای Lock هنگام Freeze.

---

## 11. CTA نهایی

> Template یک‌صفحه‌ای Specification را باز کنید و فعلاً فقط دو فیلد را بنویسید: `Intended decision` و `Claim boundary`. اگر هرکدام بیش از یک جمله شد یا پر از واژه‌های مبهم بود، هنوز سؤال Benchmark شما آماده نیست.

---

## 12. منابع اصلی این قسمت

1. NIST, [Practices for Automated Benchmark Evaluations of Language Models — AI 800-2 Initial Public Draft](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf), January 2026.
2. Liang et al., [Holistic Evaluation of Language Models](https://arxiv.org/abs/2211.09110) و [HELM](https://crfm.stanford.edu/helm/).
3. Center for Open Science, [Preregistration](https://www.cos.io/initiatives/prereg) و [OSF Registrations](https://help.osf.io/article/330-welcome-to-registrations).

