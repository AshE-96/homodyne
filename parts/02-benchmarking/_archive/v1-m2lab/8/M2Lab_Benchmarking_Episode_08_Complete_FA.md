# M2Lab Benchmarking Foundations — Episode 08

## I Built a Real AI Benchmark for Startup Research

**نسخه:** 1.1 — متن دو‌مرحله‌ای؛ ضبط Result فقط پس از Data Lock  
**زبان روایت:** فارسی  
**زبان عناصر روی تصویر:** انگلیسی  
**زمان هدف:** 21:00 تا 23:00  
**خروجی این قسمت:** `Dataset Card + Frozen Protocol + Run Evidence + Analysis Notebook + Result Profile`  
**پروژهٔ فصل:** اجرای واقعی Benchmark ابزارهای Deep Research برای تحقیق اولیهٔ بازار استارتاپ

---

## 0. قاعدهٔ غیرقابل‌مذاکره

این قسمت قبل از Run کامل نمی‌شود.

- بخش‌های Setup، Method و Run process پیش از Data Lock قابل ضبط‌اند.
- Hook نتیجه، Result profile، Failure teardown و Verdict فقط پس از Run، Annotation، QA و Freeze تحلیل ضبط می‌شوند.
- هیچ عدد، نام Winner یا Screenshot ساختگی در نسخهٔ منتشرشده باقی نمی‌ماند.
- هر فیلد با برچسب `LOCKED_RESULT` باید از خروجی Analysis pipeline پر شود.
- اگر اختلاف روشن نیست، عنوان و Thumbnail نباید Winner بسازند.
- اگر Guardrail بحرانی Fail شود، Score بالا آن را پاک نمی‌کند.

**تعریف Data Lock:**

> Raw runs کامل، Exclusion/Deviationها ثبت، Annotation بحرانی تأیید، Metric code versioned، Primary analysis اجرا و Result checksum ذخیره شده است.

### واژه‌های این قسمت

مرجع سریع. روی اسلاید همیشه واژهٔ انگلیسی می‌آید؛ این جدول برای گوش مخاطب است.

| واژه | به فارسی | یک‌خطی |
|---|---|---|
| `Data Lock` | قفل داده | لحظه‌ای که دیگر هیچ چیزی به داده اضافه یا از آن کم نمی‌شود |
| `Prediction log` | دفتر پیش‌بینی | قبل از دیدن نتیجه نوشتیم چه انتظاری داریم |
| `POST-LOCK` | پس از قفل | برچسب هر تصمیمی که بعد از دیدن نتیجه گرفته شده |
| `Paired difference` | اختلاف جفتی | اختلاف دو ابزار روی همان Case، نه اختلاف دو میانگین |
| `Claim–source mismatch` | فاصلهٔ ادعا و منبع | لینک هست، ولی منبع دقیقاً همان حرف را نمی‌زند |
| `Coverage blind spot` | نقطهٔ کور پوشش | مشهورها را پیدا کرد، بقیه را ندید |
| `Teardown` | کالبدشکافی | باز کردن یک Failure واقعی تا ریشه‌اش |
| `Frequency vs. anecdote` | نرخ در برابر نمونه | یک مورد مکانیزم را نشان می‌دهد، نرخ اندازه را |
| `Dominated` | مغلوب | ابزاری که دیگری هم بهتر است هم ارزان‌تر |

---

## 1. قول این قسمت به مخاطب

در پایان قسمت، مخاطب باید:

- Proof of work فصل را ببیند، نه Summary تزئینی؛
- بفهمد ۴۸ Case چگونه میان Pilot، Main و Holdout تقسیم شده‌اند؛
- Version، Plan، Interface و Run window هر Tool را ببیند؛
- هزینه، زمان، Error، Retry و Missing output را داخل Result ببیند؛
- Claim-level Citation support را تا Source واقعی Audit کند؛
- Result را به‌صورت Profile، CI، Slice، Failure و Pareto بخواند؛
- تفاوت Statistical separation و Practical value را تشخیص دهد؛
- بداند کدام Scenario کدام Tool را ترجیح می‌دهد؛
- محدودیت‌های نسخهٔ `v1.0` و برنامهٔ Rerun را ببیند.

جملهٔ محوری:

> **The result is not the ranking. The result is the evidence profile.**

Hook باید یکی از Findingهای واقعی زیر باشد، نه الزاماً Winner:

- یک Rank غیرمنتظره؛
- یک Guardrail failure؛
- اختلاف نامطمئن میان دو Tool؛
- سقوط عملکرد در Low-data market؛
- Trade-off روشن Quality–Cost؛
- تفاوت شدید First run و Repeat run.

---

## 2. سؤال و Scope نهایی

### سؤال اصلی

کدام ابزار Deep Research، برای یک Founder غیرفنی، با استفاده از وب عمومی و تحت محدودیت زمان و هزینه، Report تحقیق اولیهٔ بازار انگلیسی دقیق‌تر، قابل‌استنادتر و قابل‌اقدام‌تری تولید می‌کند؟

### واحد تحلیل

- `Case`: Brief تحقیق بازار؛
- `Run`: اجرای یک Tool روی یک Case؛
- `Report`: خروجی کامل؛
- `Claim`: ادعای قابل بررسی؛
- `Citation`: منبع متصل به Claim؛
- `Action item`: پیشنهاد قابل اقدام.

### داخل Scope

- Research اولیهٔ بازار؛
- Competitive landscape؛
- Pricing و positioning عمومی؛
- Evidence of demand؛
- مقررات عمومی سطح اول؛
- خروجی انگلیسی؛
- Product UI برای کاربر غیرفنی.

### خارج Scope

- Due diligence حقوقی/مالی؛
- زبان فارسی؛
- دادهٔ خصوصی یا Paywalled اختصاصی؛
- تصمیم سرمایه‌گذاری بدون Human review؛
- کیفیت مدل خام خارج از Product؛
- API benchmark؛
- ادعای نمایندگی تمام Founderها، کشورها و صنایع.

---

## 3. Tool inclusion و Baseline

### قاعدهٔ انتخاب

حداکثر چهار Product تجاری + یک Baseline دستی. هر Tool باید در هفتهٔ Freeze:

1. Research mode عمومی و قابل خرید داشته باشد؛
2. روی وب عمومی کار کند؛
3. Citation یا Source list تولید کند؛
4. Report بلند بسازد؛
5. برای کاربر غیرفنی قابل استفاده باشد؛
6. Terms استفاده و انتشار Derived result را منع نکند؛
7. در Region اجرا قابل دسترس باشد.

Candidate pool فقط پس از Accessibility check نهایی می‌شود. صفحات رسمی فعلی شامل ChatGPT Deep Research، Gemini Deep Research، Claude Research و Perplexity Research هستند؛ حضور در Candidate pool به معنی Inclusion قطعی یا endorsement نیست.

### Baseline دستی

یک Researcher با Search عمومی، Template ثابت و همان سقف زمانی/هزینه‌ای که برای انسان قابل تعریف است، یک زیرنمونهٔ ۶ Case را انجام می‌دهد. Baseline انسانی برای Rank عمومی چهار Tool استفاده نمی‌شود مگر Protocol و Budget آن هم‌ارز و Sample کافی باشد؛ نقش اصلی آن Context و Debug کردن Task است.

### Blindness

در Annotation، نام Tool با `T01…T04` جایگزین می‌شود. نام‌ها پس از Data Lock برای Presenter آشکار می‌شوند. Operator اجرا Blind نیست، اما Actionهای او محدود و Logged است.

---

## 4. طراحی Dataset و Run

### ساختار ۴۸ Case

| Split | تعداد | نقش | ورود به Primary result |
|---|---:|---|---|
| Pilot | 6 | Debug، Prompt، Rubric و Parser | خیر |
| Main | 36 | مقایسهٔ ثبت‌شدهٔ اصلی | بله |
| Holdout | 6 | Stress test پس از Freeze | جداگانه |

پس عبارت دقیق روی تصویر:

> `48-CASE SYSTEM / 36 PRIMARY TEST CASES`

نه عبارت گمراه‌کنندهٔ `48 independent scored tasks`.

### ترکیب Main set

- B2B و B2C متوازن؛
- Easy/Medium/Hard با تمرکز بیشتر روی Medium/Hard؛
- هشت Industry؛
- High/Medium/Low public-data availability؛
- چند Geography و Market maturity؛
- Caseهای Freshness، مشابهت نام، Pricing مبهم، Rebrand و Source conflict.

### Run design

- هر Tool یک Main run روی ۳۶ Case؛
- ۱۲ Case stratified با سه تکرار؛
- اجرای Toolها داخل Window نزدیک و Order تصادفی؛
- سقف ۳۰ دقیقه و ۱۰ دلار برای هر Run؛
- یک Retry فقط برای Service error؛
- Prompt استاندارد Freeze‌شده؛
- Raw output بدون ویرایش؛
- Error، Timeout و Incomplete داخل Result باقی می‌مانند؛
- Holdout فقط پس از Freeze Metric/Protocol باز می‌شود.

---

## 5. مدل ارزیابی نهایی

پژوهش‌های DeepResearch Bench، ReportBench و ResearchRubrics نشان می‌دهند ارزیابی Research report نیازمند Rubric چندبعدی، بررسی Factuality، Source use، completeness و reasoning/report quality است. M2Lab این ایده‌ها را برای Use case Founder محدود می‌کند؛ Metricهای اختصاصی ما استاندارد عمومی نیستند.

### 5.1 Primary metric

`Claim-level Citation Support Rate`

هر Claim دارای Citation به یکی از وضعیت‌ها می‌رود:

- `Supported`
- `Partially supported`
- `Unsupported`
- `Contradicted`
- `Source unavailable`

فرمول Primary فقط Unitهای واجد ارزیابی را طبق Missing rule ثبت‌شده حساب می‌کند. Weight ادعاهای بحرانی در Profile جداست؛ داخل Average پنهان نمی‌شود.

### 5.2 Diagnostics

- Competitor recall/precision روی Reference set؛
- Factual accuracy برای Facts snapshot-backed؛
- Source quality tier؛
- Coverage/completeness؛
- Actionability rubric؛
- Median و p95 total time؛
- Billed cost و Cost per valid report؛
- Run-to-run consistency؛
- Worst-group score؛
- Refusal، timeout، service error و incomplete rate.

### 5.3 Guardrails

1. `Fabricated source`: URL/منبع وجود ندارد یا منبع معرفی‌شده واقعی نیست.
2. `Critical factual error`: Fact بحرانی قابل Snapshot خلاف واقع گزارش شده است.

Thresholdها پیشنهاد M2Lab‌اند و قبل از Result Freeze می‌شوند. هر Guardrail status جدا از Composite منتشر می‌شود.

### 5.4 Judge و Human review

- LLM برای Claim extraction و Pre-label؛
- Human verification برای Critical facts، fabricated source، disagreement و Sample تصادفی؛
- Blind annotation؛
- ۲۰٪ Double annotation؛
- Agreement به تفکیک Label/Dimension؛
- Adjudication برای اختلاف بحرانی.

### 5.5 Analysis

- Case-level paired comparison؛
- Point estimate + uncertainty interval؛
- Practical threshold؛
- Main set و Holdout جدا؛
- Slice by difficulty/data availability/business model؛
- Worst group؛
- Weight sensitivity برای Composite کمکی؛
- Pareto frontier در Quality–Cost و Quality–Time؛
- Sensitivity با/بدون Runهای دارای Deviation.

برای نسخهٔ `v1.0`، Paired bootstrap روش اصلی توصیفی است. NIST AI 800-3 نشان می‌دهد مدل‌های آماری صریح مانند GLMM می‌توانند منابع variation و item difficulty را بهتر جدا کنند؛ آن روش به‌عنوان Extension تحلیل می‌آید، نه وعدهٔ اجباری نسخهٔ اول.

---

## 6. Gateهای قبل از ضبط Result

### Stop conditions

اگر یکی از موارد زیر برقرار است، بخش Result ضبط نمی‌شود:

- Raw run ناقص یا بدون checksum؛
- Tool version یا Run window نامشخص؛
- Placeholder عددی باقی‌مانده؛
- Primary metric پس از مشاهدهٔ Result عوض شده و Change Log ندارد؛
- Critical failures Human-verified نشده‌اند؛
- Annotation agreement/diagnostic QA انجام نشده؛
- Score تا Raw output trace نمی‌شود؛
- Exclusion/Deviationها ثبت نشده‌اند؛
- Uncertainty یا حداقل paired difference گزارش نشده؛
- Sponsor/Affiliate relationship افشا نشده؛
- Terms/Privacy انتشار Artifact را منع می‌کند.

### Result payload اجباری

```text
LOCKED_RESULT.RUN_WINDOW=
LOCKED_RESULT.TOOLS_AND_VERSIONS=
LOCKED_RESULT.N_MAIN_VALID_BY_TOOL=
LOCKED_RESULT.PRIMARY_ESTIMATE_BY_TOOL=
LOCKED_RESULT.PAIRED_DIFFERENCES_AND_CI=
LOCKED_RESULT.GUARDRAIL_STATUS=
LOCKED_RESULT.MEDIAN_COST=
LOCKED_RESULT.MEDIAN_AND_P95_TIME=
LOCKED_RESULT.WORST_GROUP=
LOCKED_RESULT.REPEAT_VARIABILITY=
LOCKED_RESULT.ANNOTATION_AGREEMENT=
LOCKED_RESULT.TOP_3_FAILURE_CASES=
LOCKED_RESULT.SENSITIVITY_SUMMARY=
LOCKED_RESULT.HOLDOUT_SUMMARY=
LOCKED_RESULT.DEVIATIONS=
```

---

## 7. فلو زمانی نهایی

| زمان | Beat | هدف | Proof object |
|---|---|---|---|
| 00:00–01:20 | Result-first hook | مهم‌ترین Finding واقعی | locked result chart |
| 01:20–03:05 | The question we froze | جلوگیری از تغییر Claim | frozen spec + prediction log |
| 03:05–05:25 | 48-case system | نشان‌دادن جهان Test | dataset grid + holdout lock |
| 05:25–07:20 | Tools and protocol | اثبات Comparability | version cards + protocol hash |
| 07:20–09:40 | The real run | نمایش هزینه، زمان و Error | run control room |
| 09:40–11:55 | From report to evidence | توضیح Annotation | claim-source x-ray |
| 11:55–15:35 | Main results | Profile، CI، slices و Guardrail | result atlas |
| 15:35–18:20 | Three failures that matter | تحلیل Failure، نه فقط Rank | case teardown |
| 18:20–20:15 | Cost, time and Pareto | Recommendation سناریومحور | frontier + scenario selector |
| 20:15–21:30 | What this does not prove | Limitations و Next run | claim boundary + rerun plan |

---

## 8. متن کامل آمادهٔ ضبط

### 00:00–01:20 — Hook نتیجه‌محور

**این بخش فقط پس از Data Lock نوشته/ضبط می‌شود. یکی از چهار Branch انتخاب شود.**

#### Branch A — برتری روشن در Primary metric

«در ۳۶ Case اصلی، `[TOOL]` بالاترین Claim-level citation support را داشت. اختلاف ثبت‌شده با `[COMPARATOR]` برابر `[EFFECT]` بود و Interval `[CI]` را نشان داد. اما این پایان داستان نیست: `[GUARDRAIL/SLICE]` باعث می‌شود آن را Winner مطلق ننامیم.»

#### Branch B — تفاوت نامطمئن

«در جدول، `[TOOL A]` بالاتر است. اما وقتی Caseهای یکسان را Pair می‌کنیم، Interval اختلاف `[CI]` صفر/threshold عملی را پوشش می‌دهد. دادهٔ فعلی Winner روشن نمی‌دهد. Finding مهم‌تر جای دیگری است: `[FAILURE/TRADE-OFF]`.»

#### Branch C — برنده سناریومحور

«هیچ Toolی همه‌چیز را نبرد. `[TOOL A]` در Citation quality، `[TOOL B]` در Cost و `[TOOL C]` در Low-data markets بهتر بود. سؤال “بهترین کدام است؟” در دادهٔ ما یک جواب ندارد؛ سه Scenario دارد.»

#### Branch D — Guardrail شکست خورد

«این Tool Overall score بالایی گرفت، اما `[N]` Source ساختگی/خطای بحرانی داشت. Score آن حذف نشده؛ کنار آن Guardrail قرمز قرار گرفته است. Average خوب نمی‌تواند Failure غیرقابل‌قبول را بازنویسی کند.»

**در یک جمله:** Hook همان چیزی است که داده واقعاً پشتیبانی می‌کند — و اگر اختلاف روشن نبود، عنوان و Thumbnail برنده نمی‌سازند.

**روی تصویر:**

`RESULTS ARE LOCKED / RUN WINDOW: [DATE] / PROTOCOL: [VERSION]`

### 01:20–03:05 — سؤالی که قبل از Result Freeze شد

**تصویر:** Specification نسخهٔ Freeze‌شده، Prediction log و Change history.

**متن گفتاری:**

«قبل از اینکه یک عدد ببینیم، سؤال را محدود کردیم. کلمه به کلمه‌اش را بشنوید:

کدام Product Research، برای یک Founder غیرفنی، در تحقیق اولیهٔ بازار انگلیسی، روی وب عمومی، زیر سقف زمان و هزینه، شواهد دقیق‌تر و قابل‌اقدام‌تری می‌سازد؟

و حالا آنچه این Benchmark درباره‌اش نیست: هوش عمومی. زبان فارسی. Due diligence. کیفیت API.

قبل از Run یک `Prediction log` (دفتر پیش‌بینی) هم نوشتم. کجا انتظار داشتم ابزارها فرق کنند. کدام Failure محتمل بود. کدام Metric ممکن است کم‌قدرت باشد.

این کار برای نمایش پیشگویی نیست. برای دو چیز است: اینکه غافلگیری قابل‌دیدن شود، و اینکه من نتوانم بی‌سروصدا با هر نتیجه‌ای موافقت کنم.

Specification، Metric registry و هش Protocol قبل از Main run ثبت شدند. هر تغییر بعدی داخل Change Log است.

و اگر تصمیمی بعد از دیدن نتیجه گرفته شده، روی تصویر برچسب `POST-LOCK` می‌خورد.»

**در یک جمله:** سؤال و پیش‌بینی قبل از داده نوشته شدند، تا بعداً نتوانیم نتیجه را به جای انتظار جا بزنیم.

### 03:05–05:25 — ۴۸ Case، اما فقط ۳۶ Case در Result اصلی

**تصویر:** Dataset grid با سه رنگ Pilot/Main/Holdout. `SHOW WHO IS MISSING` خلأها را نشان دهد.

**متن گفتاری:**

«Dataset ما چهل‌وهشت Case دارد. اما در جدول اصلی چهل‌وهشت نتیجه نمی‌بینید. توضیح می‌دهم.

شش Case برای Pilot بود. با آن‌ها Prompt، Parser و Rubric را Debug کردیم.

و دقیقاً به همین دلیل وارد نتیجهٔ اصلی نمی‌شوند: روش ما با دیدن این Caseها تغییر کرده است.

سی‌وشش Case، Main test هستند. مقایسهٔ اصلی همین‌جاست.

شش Case، Holdout. تا وقتی Metric و Protocol فریز نشدند، اصلاً بازشان نکردیم. نتیجه‌شان جدا می‌آید، به‌عنوان Stress test — نه اینکه با Main قاطی شود و امتیاز را بهتر کند.

Caseها B2B و B2C، صنایع مختلف، سطوح Difficulty و میزان دادهٔ عمومی را پوشش می‌دهند.

اما — و این مهم است — این نمونهٔ احتمالی از کل اقتصاد نیست. برای بازار فارسی، آفریقا، دادهٔ خصوصی سازمانی و خیلی از صنایع، پوشش کافی نداریم.

پس چهل‌وهشت عدد جادویی نیست. یک Pilot تشخیصی است، با یک Grid که همه می‌توانند ببینند.»

**در یک جمله:** شش Case برای Debug، سی‌وشش برای مقایسه، شش برای اینکه بعداً خودمان را گول نزنیم.

### 05:25–07:20 — دقیقاً چه Toolهایی و تحت چه شرایطی؟

**تصویر:** Tool cards با نام پس از Unblind؛ Version، Plan، Interface، Date، Access و Price. هیچ Rank هنوز نمایش داده نشود.

**متن گفتاری:**

«ابزارها بر اساس محبوبیت انتخاب نشدند. پنج شرط داشتند.

حالت Research عمومی. دسترسی به وب. Citation. Report بلند. و قابل‌استفاده برای یک Founder غیرفنی.

نسخه‌های دقیق روی تصویرند: `[LOCKED_RESULT.TOOLS_AND_VERSIONS]`. بازهٔ اجرا از `[START]` تا `[END]` بود.

اگر محصولی وسط این بازه تغییر کرد، یک Deviation ثبت شده. پاکش نکردیم.

همه در Product UI و Track استاندارد اجرا شدند. Brief و خروجی لازم معادل بود. تطبیق فقط برای Interface انجام شد.

سقف هر Run: سی دقیقه و ده دلار. یک Retry برای خطای سرویس.

و یک نکتهٔ صادقانه. این تنظیمات ثابت نمی‌کنند هر ابزار به سقف توانش رسیده.

این‌ها تجربهٔ اولین اجرای یک کاربر غیرفنی را می‌سنجند. Track optimized یک سؤال دیگر است و باید جدا اجرا شود.»

**در یک جمله:** آنچه سنجیده شد، اولین تجربهٔ یک کاربر غیرفنی است — نه سقف توان هیچ ابزاری.

### 07:20–09:40 — اجرای واقعی تمیز نبود، و نباید باشد

**تصویر:** Run control room؛ Completed، Timeout، Error، Retried، Incomplete. Cost meter و Timeline واقعی.

**متن گفتاری:**

«Main run اصلاً شبیه آن جدول تمیز نبود. صف داشت. خطا داشت. بعضی خروجی‌ها ناقص بودند.

اعداد واقعی: `[N]` Run برنامه‌ریزی شد. `[N_COMPLETED]` بدون Retry کامل شد. `[N_RETRIED]` نیاز به Retry داشت. `[N_TIMEOUT]` تایم‌اوت شد. `[N_INCOMPLETE]` ناقص ماند.

حالا سه کاری که نکردیم.

Retry موفق، خطای اول را پاک نکرد. Timeout از Dataset حذف نشد. و خروجی خام را من با دست کامل نکردم.

چرا؟ چون این رخدادها خودشان بخشی از Reliability محصول‌اند. حذفشان یعنی گزارش یک محصول خیالی.

برای هر Run این‌ها ثبت شده: هش Prompt، زمان، هزینه، خروجی و خطا. جایی که ابزار مصرف دقیق را نشان نداد، `UNKNOWN` نوشتیم. عدد تخمینی را با هزینهٔ واقعی قاطی نکردیم.

و این مهم‌ترین تفاوت یک Benchmark واقعی با مقایسهٔ اسکرین‌شاتی است: شواهد زشت هم سر جایشان می‌مانند.»

**در یک جمله:** خطاها، صف‌ها و خروجی‌های ناقص پاک نشدند — چون خودشان بخشی از محصول‌اند.

### 09:40–11:55 — از Report زیبا تا Claim قابل بررسی

**تصویر:** یک Report به Claimها می‌شکند. Claim به Citation و Source snapshot وصل می‌شود. Label تغییر می‌کند.

**متن گفتاری:**

«یک Report بلند را با یک نمرهٔ کلی نسنجیدیم. مسیرش این بود.

اول متن به Claimهای قابل‌بررسی شکسته شد.

برای هر Claim دو سؤال: Citation کجاست؟ و آیا آن منبع واقعاً همین ادعا را پشتیبانی می‌کند؟

پنج جواب ممکن بود: Supported، Partial، Unsupported، Contradicted، یا Source unavailable.

بعد Factهای بحرانی — قیمت، نام شرکت، کشور، الزامات — با Snapshot بررسی شدند.

Actionability هم با Rubric رفتاری سنجیده شد. Next step، اولویت، شواهد، Dependency و سؤال باز.

Judge ماشینی استخراج Claim و برچسب اولیه را سریع کرد. اما همهٔ Failureهای بحرانی را انسان تأیید کرد.

بیست درصد Caseها دوبار برچسب خوردند. Agreement برابر `[LOCKED_RESULT.ANNOTATION_AGREEMENT]` شد.

و یک قاعده: اگر Agreement در یک بُعد پایین است، همان Metric را با اعتماد کمتر گزارش می‌کنیم.

اختلاف برچسب‌گذارها فقط نویز مزاحم نیست. ممکن است بگوید سازه یا Rubric ما هنوز مبهم است.»

**در یک جمله:** از هر عدد می‌شود به Claim رسید، از Claim به Citation، و از Citation به منبع با تاریخ.

### 11:55–15:35 — Result profile، نه Medal table

**تصویر:** Result Atlas. انتخاب هر Tool، Primary estimate، CI، Guardrail، Cost، Time و Slice را باز کند.

**متن گفتاری — بلوک ثابت:**

«معیار اصلی ما Claim-level citation support بود. برآوردها روی تصویرند.

ولی ترتیب جدول، به‌تنهایی، حکم نیست.

هر ابزار روی Caseهای یکسان مقایسه شده. پس `paired difference` (اختلاف جفتی) داریم، همراه با بازه‌اش.

دو برچسب داریم و هر دو را واقعاً به کار می‌بریم.

اگر بازه جدایی روشنی نشان ندهد: `UNRESOLVED`.

اگر اختلاف از نظر آماری روشن باشد ولی زیر آستانهٔ عملی: `SMALL PRACTICAL EFFECT`.

و امتیاز کلی همیشه کنار سه چیز دیگر می‌آید: Distribution، بدترین گروه، و Failureهای بحرانی.

Composite فقط یک View کمکی است — و حساسیتش به وزن‌ها همان‌جا باز می‌شود.»

**سپس این Payload واقعی خوانده شود:**

```text
Primary result: [LOCKED_RESULT.PRIMARY_ESTIMATE_BY_TOOL]
Primary comparison: [LOCKED_RESULT.PAIRED_DIFFERENCES_AND_CI]
Guardrails: [LOCKED_RESULT.GUARDRAIL_STATUS]
Worst group: [LOCKED_RESULT.WORST_GROUP]
Repeat variability: [LOCKED_RESULT.REPEAT_VARIABILITY]
Holdout: [LOCKED_RESULT.HOLDOUT_SUMMARY]
```

**متن تفسیر—براساس Branch انتخابی:**

«این Evidence از `[CLAIM_SUPPORTED]` پشتیبانی می‌کند. دربارهٔ `[CLAIM_NOT_SUPPORTED]` چیزی ثابت نمی‌کند. اختلاف اصلی در `[DIMENSION]` دیده شد و بزرگ‌ترین عدم‌قطعیت `[SOURCE]` است.»

**ممنوع:** خواندن تمام جدول. فقط یک Comparison، یک Slice، یک Guardrail و یک Trade-off در ویدئو باز شود؛ جدول کامل روی سایت بماند.

**در یک جمله:** جدول رتبه یک نما است، نه حکم — امتیاز کلی همیشه کنار توزیع، بدترین گروه و Guardrail خوانده می‌شود.

### 15:35–18:20 — سه Failure که بیشتر از Rank به ما یاد دادند

هر Failure باید واقعی، Human-verified و قابل Trace باشد.

#### Failure 1 — Claim/Source mismatch

«در Case `[ID]`، Report نوشته بود `[PARAPHRASED CLAIM]`. Citation وجود داشت، اما Source فقط `[WHAT SOURCE ACTUALLY SAID]` را پشتیبانی می‌کرد. مشکل نبودن لینک نبود؛ فاصلهٔ Claim و Evidence بود.»

#### Failure 2 — Coverage blind spot

«در Case `[ID]`، Tool رقبای مشهور را پیدا کرد اما `[LOW-DATA/LOCAL]` segment را از دست داد. Overall report قانع‌کننده بود؛ Retrieval distribution ناقص بود.»

#### Failure 3 — Operational failure یا misleading action

«در Case `[ID]`، `[TIMEOUT/ERROR/ACTIONABILITY FAILURE]` رخ داد. این Failure در Score نگارشی دیده نمی‌شد، اما برای Founder تصمیم را تغییر می‌دهد.»

**متن جمع‌بندی:**

«Failure analysis توضیح می‌دهد چرا امتیازها این‌طور شدند.

اما یک خط قرمز داریم: از یک Case، یک روایت کلی نمی‌سازیم.

پس کنار هر `Teardown` (کالبدشکافی)، نرخ آن Failure و برشی که در آن رخ داده را هم نشان می‌دهیم.

قاعده‌اش ساده است. یک نمونه مکانیزم را نشان می‌دهد. نرخ، اندازه را.»

**در یک جمله:** یک شکست واقعی می‌گوید چه اتفاقی می‌افتد؛ نرخ آن می‌گوید چقدر باید نگران باشید.

### 18:20–20:15 — Quality، Cost و Time یک Winner ندارند

**تصویر:** Pareto frontier و Scenario selector: `SOLO FOUNDER / EVIDENCE FIRST / LOW-DATA MARKET / SPEED CRITICAL`.

**متن گفتاری:**

«حالا هزینه و زمان را اضافه کنیم. رتبه‌بندی دوباره شکل عوض می‌کند.

هزینهٔ میانه `[VALUES]` بود. زمان میانه و p95 برابر `[VALUES]`.

و ابزاری که بالاترین کیفیت را داشت، لزوماً بهترین هزینه به‌ازای هر گزارش معتبر نبود.

در نمودار Pareto، یک گزینه وقتی `Dominated` (مغلوب) است که ابزار دیگری هم کیفیت بهتری دارد هم هزینهٔ کمتر. آن را حذف می‌کنیم.

گزینه‌های روی مرز، معاملهٔ واقعی‌اند. انتخاب بینشان به سناریو بستگی دارد، نه به داده.

برای Founder تنها با بودجهٔ محدود: `[RECOMMENDATION + CAVEAT]`.

برای Workflow مبتنی بر شواهد: `[RECOMMENDATION + CAVEAT]`.

برای بازار کم‌داده: `[RECOMMENDATION + CAVEAT]`.

و برای استفادهٔ بدون بازبینی انسانی در تصمیم پرریسک، پاسخ می‌تواند `NONE` باشد.

یک توصیهٔ خوب همیشه یک اسم نمی‌گوید. گاهی می‌گوید شواهد کافی نیست. گاهی می‌گوید بازبینی انسانی اجباری است.»

**در یک جمله:** وقتی هیچ ابزاری مغلوب نیست، خروجی صادقانه یک مدال نیست — چند سناریو است.

### 20:15–21:30 — این Benchmark چه چیزی را ثابت نمی‌کند؟

**تصویر:** `SUPPORTS / DOES NOT PROVE / NEXT TEST`.

**متن گفتاری:**

«این نتیجه برای چهار چیز معتبر است: سی‌وشش Case اصلی، نسخه‌های ثبت‌شدهٔ ابزارها، خروجی انگلیسی، و همان بازهٔ اجرا.

حالا فهرست چیزهایی که ثابت نمی‌کند.

نمونهٔ احتمالی از همهٔ Founderها نیست. دربارهٔ زبان فارسی حرفی ندارد. دربارهٔ دادهٔ خصوصی هم. دربارهٔ Due diligence هم. و دربارهٔ نسخه‌های آینده هیچ.

Ground truth ما برای Actionability به یک Rubric و تعداد محدودی برچسب‌گذار تکیه دارد. و همهٔ Runها را کامل تکرار نکردیم.

نسخهٔ بعد سه کار دارد. پوشش برش‌های ضعیف را زیاد می‌کنیم. Track optimized را اجرا می‌کنیم. و بعد از هر تغییر بزرگ ابزارها دوباره اجرا می‌کنیم.

هشتاد درصد Caseهای لنگر ثابت می‌مانند. بیست درصد برای تازگی عوض می‌شوند.

قسمت بعد نشان می‌دهد چطور همین نتیجه را منتشر کنیم — طوری که مخاطب از رتبه به Case برسد، از Case به Claim، و از Claim به منبع.

و اگر خطایی پیدا کرد، بتواند یک Correction ثبت کند.»

**در یک جمله:** فهرست چیزهایی که این نتیجه ثابت نمی‌کند، به‌اندازهٔ خودِ نتیجه بخشی از خروجی است.

**پایان روی تصویر:**

`RESULTS WITHOUT EVIDENCE ARE JUST CLAIMS.`

---

## 9. Result statement template

> «در Dataset نسخهٔ `[D]` شامل `[N]` Main case، تحت Protocol نسخهٔ `[P]` و Run window `[DATES]`، Tool `[X]` در Primary metric امتیاز `[VALUE]` گرفت. اختلاف paired با `[Y]` برابر `[EFFECT]` با interval `[L,U]` بود و `[INTERPRETATION]`. Guardrail status برابر `[STATUS]` بود. این نتیجه فقط برای `[SCOPE]` تفسیر می‌شود و دربارهٔ `[EXCLUSIONS]` Evidence کافی ندارد.»

### Limitation statement template

> «این Benchmark نمونهٔ احتمالی از کل بازار Research نیست. Coverage روی `[SEGMENTS]` متمرکز است و `[UNDERREPRESENTED]` را کم پوشش می‌دهد. Toolها در بازهٔ `[DATES]` و نسخه‌های `[VERSIONS]` اجرا شدند. Ground truth در ابعاد کیفی بر `[N]` ارزیاب و Rubric متکی است. ریسک‌های باقیمانده شامل `[DRIFT/JUDGE/CONTAMINATION/SAMPLE]` است.»

---

## 10. طراحی تجربهٔ بصری

### صحنهٔ اصلی: Live Evidence Atlas

- بالای صفحه: Run window، Protocol hash و Data lock badge؛
- چپ: Tool index؛
- مرکز: Profile، CI و Pareto؛
- راست: Inspector تب‌های `RESULT / SLICES / FAILURES / EVIDENCE`؛
- کلیک روی Score: Case list؛
- کلیک روی Case: Report/Claim/Citation؛
- کلیک روی Citation: Source snapshot + support label؛
- Scenario selector Recommendation را تغییر دهد؛
- `SHOW UNCERTAINTY` Rank را به Tier/interval تبدیل کند؛
- `SHOW DEVIATIONS` Runهای مسئله‌دار را از Main جدا کند.

### Proof objectهای حذف‌ناپذیر

1. Dataset split واقعی؛
2. Tool/version cards؛
3. Run event log؛
4. Claim-source trace؛
5. Primary paired result + uncertainty؛
6. Guardrail status؛
7. سه Failure واقعی؛
8. Pareto/Scenario recommendation؛
9. `DOES NOT PROVE`؛
10. Rerun schedule.

### ممنوع بصری

- Confetti برای Winner؛
- Medal table بدون CI/Guardrail؛
- مخفی‌کردن Errorها در Footnote؛
- نمایش Composite بدون Profile؛
- نمودار بدون N، Date، Unit و Version؛
- Screenshot منبع بدون اتصال به Claim.

---

## 11. سایت‌هایی که باید نمایش داده شوند

| زمان | سایت | نمایش | کارکرد |
|---|---|---|---|
| 02:20 | NIST AI 800-2 | define/run/analyze-report stages | ستون Method |
| 05:40 | صفحات رسمی Toolهای Included | Product capability + Date | Version/feature evidence |
| 10:50 | DeepResearch Bench | multidimensional report evaluation | Context علمی، نه مقایسه مستقیم |
| 11:10 | ReportBench | reference/factual accuracy focus | دلیل Claim/Source evaluation |
| 11:30 | ResearchRubrics | expert-written fine-grained criteria | دلیل Rubric رفتاری |
| 14:40 | NIST AI 800-3 | statistical modeling and variation | مسیر تحلیل پیشرفته |
| 20:45 | Dataset/Model/Benchmark Cards | Documentation pattern | پل انتشار |

صفحات رسمی Toolها فقط برای Version/capability نمایش داده شوند؛ ادعای Marketing آنها Evidence عملکرد M2Lab نیست.

---

## 12. چک‌لیست علمی قبل از ضبط Result

- [ ] تمام `LOCKED_RESULT`ها پر شده‌اند.
- [ ] هیچ Placeholder در Graphic/VO باقی نمانده است.
- [ ] ۶ Pilot داخل Primary result نیستند.
- [ ] Holdout جدا گزارش شده است.
- [ ] N معتبر به تفکیک Tool نمایش داده شده است.
- [ ] Tool/Plan/Version/Date دقیق‌اند.
- [ ] Error، Retry، Timeout و Incomplete باقی مانده‌اند.
- [ ] Critical guardrailها Human-verified هستند.
- [ ] Agreement و Annotation limitation گزارش شده‌اند.
- [ ] paired comparison روی Case index یکسان انجام شده است.
- [ ] Effect، interval و Practical threshold کنار هم‌اند.
- [ ] Worst group و Distribution نمایش داده شده‌اند.
- [ ] Weight sensitivity برای Composite انجام شده است.
- [ ] Failure storyها Frequency/Slice دارند.
- [ ] Recommendationها Scenario + Caveat دارند.
- [ ] Sponsor/Affiliate قبل از Verdict افشا شده است.
- [ ] Terms، Privacy و License انتشار Raw/derived evidence بررسی شده‌اند.
- [ ] Result statement و Limitation statement نهایی‌اند.

---

## 13. بستهٔ ضبط دو‌مرحله‌ای

### مرحله A — قبل از Run

- سؤال و Scope؛
- Dataset split؛
- Tool inclusion؛
- Protocol؛
- Prediction log؛
- Run UI بدون Result؛
- توضیح Annotation.

### مرحله B — بعد از Data Lock

- Result-first Hook؛
- آمار Run واقعی؛
- Result profile؛
- Failure teardown؛
- Pareto و Scenario recommendation؛
- Limitations؛
- Verdict.

### A-roll حذف‌ناپذیر

- ۴۸ Case system در برابر ۳۶ Main؛
- باقی‌ماندن Errorها؛
- Claim-level scoring؛
- Uncertainty/Practical threshold؛
- سه Failure واقعی؛
- Does not prove.

---

## 14. عنوان و Thumbnail پس از Result

### اگر Separation روشن وجود داشت

- **Title:** `I Tested [N] AI Research Tools on 36 Startup Tasks`
- **Alternate:** `[TOOL] Won Our Research Benchmark — But Failed This Test`
- **Thumbnail:** `36 TASKS. RAW RESULTS.`

### اگر Winner روشن نبود

- **Title:** `I Benchmarked AI Research Tools — There Was No Clear Winner`
- **Thumbnail:** `NO CLEAR WINNER`

### اگر Scenario split Finding اصلی بود

- **Title:** `The Best AI Research Tool Depends on What You Value`
- **Thumbnail:** `QUALITY ≠ VALUE`

عدد Toolها، Caseها و نام Tool فقط پس از Freeze نهایی شود.

---

## 15. CTA نهایی

> «Result page را باز کنید و از یک Score تا یک Claim و Source پایین بروید. اگر مسیر Evidence قطع شد یا Labelی را اشتباه دیدید، Case ID را ثبت کنید. نسخهٔ بعد با تعداد View بهتر نمی‌شود؛ با Errorهای قابل بررسی بهتر می‌شود.»

**Comment prompt:**

> برای نسخهٔ بعد کدام Case، Market یا Failure باید اضافه شود—و چرا ممکن است Winner را عوض کند؟

---

## 16. منابع اصلی این قسمت

1. NIST, [Practices for Automated Benchmark Evaluations of Language Models — NIST AI 800-2 IPD](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf), January 2026.
2. NIST, [Expanding the AI Evaluation Toolbox with Statistical Models — NIST AI 800-3](https://www.nist.gov/publications/expanding-ai-evaluation-toolbox-statistical-models), February 2026.
3. Du et al., [DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents](https://arxiv.org/abs/2506.11763), 2025.
4. Li et al., [DeepResearch Bench II: Diagnosing Deep Research Agents via Rubrics from Expert Report](https://arxiv.org/abs/2601.08536), 2026.
5. [ReportBench: Evaluating Deep Research Agents via Factuality and Reference Quality](https://arxiv.org/abs/2508.15804), 2025.
6. [ResearchRubrics: A Benchmark of Prompts and Rubrics for Deep Research Agents](https://arxiv.org/abs/2511.07685), 2025.
7. Gebru et al., [Datasheets for Datasets](https://arxiv.org/abs/1803.09010), 2018/2021.
8. OpenAI, [Introducing Deep Research](https://openai.com/index/introducing-deep-research/), official product documentation.
9. Google AI for Developers, [Gemini Deep Research Agent](https://ai.google.dev/gemini-api/docs/deep-research), official documentation, 2026.
10. Anthropic, [Use Research on Claude](https://support.anthropic.com/en/articles/11088861-using-research-on-claude-ai), official documentation, updated 2026.
11. Perplexity, [What is Research Mode?](https://www.perplexity.ai/help-center/en/articles/10738684-what-is-research-mode.html), official documentation, updated 2026.

---

## 17. خطاهای ممنوع

- نوشتن Result قبل از Data Lock؛
- استفاده از Pilot برای بالا‌بردن N اصلی؛
- معرفی Holdout به‌عنوان Secret proof بدون روش روشن؛
- تغییر Primary metric پس از Result بدون Disclosure؛
- رتبه‌دادن به Tool با N نامعتبر مشابه دیگران؛
- حذف Error/Timeout برای «تمیزشدن داده»؛
- انتخاب Failure anecdote بدون Frequency؛
- ادعای تعمیم به زبان فارسی یا تمام بازارها؛
- عنوان Winner وقتی Difference unresolved است؛
- انتشار Raw data برخلاف Privacy، Terms یا License؛
- توصیهٔ unattended use در تصمیم پرریسک فقط براساس Score.

