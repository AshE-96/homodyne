# M2Lab Benchmarking Foundations — Episode 06

## How to Run a Fair AI Experiment

**نسخه:** 1.1 — آمادهٔ ضبط مشروط به اجرای Dry Run  
**زبان روایت:** فارسی  
**زبان عناصر روی تصویر:** انگلیسی  
**زمان هدف:** 19:00 تا 20:30  
**خروجی این قسمت:** `Experimental Protocol v1.0 + Run Log Schema + Deviation Log`  
**پروژهٔ فصل:** Freeze کردن شرایط اجرای Benchmark ابزارهای Deep Research پیش از مشاهدهٔ نتایج اصلی

---

## 0. واژه‌های این قسمت

مرجع سریع. روی اسلاید همیشه واژهٔ انگلیسی می‌آید؛ این جدول برای گوش مخاطب است.

| واژه | به فارسی | یک‌خطی |
|---|---|---|
| `Protocol` | شیوه‌نامهٔ اجرا | همهٔ شرایطی که قبل از دیدن نتیجه قفل می‌شوند |
| `Estimand` | کمیت هدف | دقیقاً چه چیزی را می‌خواهیم تخمین بزنیم |
| `Stochastic` | تصادفی‌رفتار | یک ورودی، هر بار یک خروجی متفاوت |
| `Adaptation` | تطبیق ورودی | همان اطلاعات، در قالب بومی هر ابزار |
| `Blocking` | بلوک‌بندی | گروه‌بندی Caseها تا اثر زمان با اثر ابزار قاطی نشود |
| `Randomization` | تصادفی‌سازی | جابه‌جاکردن ترتیب تا خودِ ترتیب امتیاز نسازد |
| `Judge` | داور | مدلی که خروجی را نمره می‌دهد — خودش یک ابزار اندازه‌گیری است |
| `Position bias` | سوگیری جایگاه | داور به اینکه پاسخ اول است یا دوم حساس است |
| `Auditability` | قابلیت بازرسی | شخص سوم بتواند ببیند چه شد و چرا |
| `Deviation` | انحراف | اتفاقی خارج از Protocol، که ثبت می‌شود نه پاک |
| `Freeze` | قفل‌کردن | تصمیم‌ها قبل از دیدن نتیجه ثبت و بسته می‌شوند |

---

## 1. قول این قسمت به مخاطب

در پایان قسمت، مخاطب باید بتواند:

- دقیق بگوید مقایسه قرار است کدام کمیت یا `Estimand` را تخمین بزند؛
- Fairness را از «یکسان‌سازی کور همه‌چیز» جدا کند؛
- نسخه، Plan، Interface، دسترسی وب، Region، زمان و Budget را ثبت کند؛
- بین `Standardized track` و `Optimized track` انتخاب آگاهانه داشته باشد؛
- Non-determinism، Order effect و Service drift را با تکرار، Blocking و Randomization مدیریت کند؛
- LLM-as-a-Judge را Instrument بداند، نه Ground truth؛
- Failure، Retry، Timeout، Refusal و Missing output را پیش از Run تعریف کند؛
- هر Score را از Annotation تا Raw run و Environment trace کند؛
- Protocol را Freeze و هر انحراف را بدون پاک‌کردن تاریخچه ثبت کند.

جملهٔ محوری:

> **Fairness is not sameness. Fairness is alignment between the test and the claim.**

Hook:

> **SAME QUESTION. THREE ANSWERS. WHICH ONE COUNTS?**

---

## 2. مسئلهٔ روایی

### THE CLAIM

«اگر یک Prompt را به چند Tool بدهیم و بهترین پاسخ هرکدام را مقایسه کنیم، تست منصفانه است.»

### THE EVIDENCE

مدل‌ها و Agentها stochastic هستند؛ Interface، Plan، Tool access، زمان اجرا، Queue، Retry و حتی Prompt formatting می‌توانند نتیجه را تغییر دهند. NIST AI 800-2 نیز Protocol را مجموعهٔ کامل رویه‌های عملیاتی Evaluation می‌داند و تأکید می‌کند که طراحی آن باید از هدف Evaluation شروع شود.

### THE STRESS TEST

یک Case واقعی را سه بار با همان Prompt اجرا می‌کنیم. سپس فقط یکی از عوامل را تغییر می‌دهیم: Output schema، Tool order یا Retry policy. مخاطب می‌بیند که «Winner» بدون تغییر سؤال می‌تواند عوض شود.

### THE VERDICT

Run منصفانه Run بی‌نقص نیست. Run منصفانه Runی است که Target، شرایط، استثناها و روش تحلیلش قبل از دیدن نتیجه تعریف شده و همهٔ خروجی‌ها—خوب، بد و خراب—در Evidence باقی مانده‌اند.

### THE BUILD

Protocol نسخهٔ `v1.0`، Run Log و Deviation Log پروژه Freeze می‌شوند. در پایان صفحه از حالت editable به حالت `FROZEN BEFORE MAIN RUN` می‌رود.

---

## 3. تئوری علمی و تصمیم‌های طراحی

### 3.1 Estimand: دقیقاً چه چیزی را تخمین می‌زنیم؟

چهار سؤال ظاهراً مشابه، چهار Estimand متفاوت می‌سازند:

| سؤال | چیزی که واقعاً سنجیده می‌شود |
|---|---|
| کیفیت اولین Run | تجربهٔ معمول کاربر با یک تلاش |
| بهترین خروجی از سه Run | عملکرد `best-of-3` با هزینه و زمان بیشتر |
| کیفیت پس از Prompt optimization | سقف عملکرد تحت اپراتور ماهر |
| کیفیت متوسط تحت Budget ثابت | Utility مورد انتظار در محدودیت عملیاتی |

Estimand اصلی M2Lab:

> عملکرد مورد انتظار یک Founder غیرفنی در اولین اجرای معتبر با Prompt استاندارد، تحت سقف زمان و هزینهٔ ثابت.

یک زیرنمونهٔ ۱۲ Case سه بار تکرار می‌شود تا Run-to-run variability دیده شود. `Best-of-3` فقط تحلیل ثانویه است و جای نتیجهٔ اصلی را نمی‌گیرد.

### 3.2 Comparability، External validity و Cost control

NIST AI 800-2 سه جهت طراحی مرتبط را روشن می‌کند:

- `Comparability`: شرایط باید به اندازه‌ای سازگار باشند که مقایسه معنا داشته باشد.
- `External validity`: Protocol باید به محیطی که Claim دربارهٔ آن است نزدیک باشد.
- `Cost control`: وقتی هدف Utility واقعی است، هزینه باید با استفادهٔ واقعی هم‌تراز باشد.

این سه همیشه کاملاً هم‌جهت نیستند. API کنترل بیشتر می‌دهد، اما Founder ممکن است Product UI را بخرد. بنابراین Benchmark UI و API را در یک Ranking مخلوط نمی‌کنیم.

### 3.3 Fairness با Equality فرق دارد

ورودی byte-for-byte یکسان همیشه منصفانه نیست. اگر یک Tool فقط فایل می‌پذیرد و Tool دیگر URL، می‌توان اطلاعات معادل را با Interface بومی هرکدام داد. Adaptation مجاز باید:

1. اطلاعات جدید اضافه نکند؛
2. سطح مهارت اپراتور را تغییر ندهد؛
3. در Log ثبت شود؛
4. برای همهٔ Toolهای مشابه قاعدهٔ یکسان داشته باشد.

هدف، حذف تفاوت محصول نیست؛ حذف مزیت پنهانی است که از روش تست آمده، نه از خود محصول.

### 3.4 Standardized در برابر Optimized

دو Track را مخلوط نمی‌کنیم:

- `Standardized`: یک Brief، اطلاعات معادل، Prompt grammar مشترک و بودجهٔ ثابت.
- `Optimized`: Prompt و Workflow برای هر Tool به‌طور مساوی و فقط روی Pilot بهینه می‌شود.

اگر برای یک Tool پنج Prompt امتحان شود و برای دیگری فقط یک Prompt، Selection bias ساخته‌ایم. اگر Optimization روی Test set انجام شود، Protocol به همان Caseها Overfit می‌شود. NIST پیشنهاد می‌کند Optimization روی Dev set جدا انجام شود.

### 3.5 Replication، Blocking و Randomization

یک Run از سیستم stochastic نمایندهٔ Distribution عملکرد نیست. اما سه تکرار کامل برای `48 × 5` اجرا ممکن است از Budget خارج شود. طراحی نسخهٔ اول:

- یک Main run روی همهٔ Caseهای اصلی؛
- سه تکرار روی ۱۲ Case stratified؛
- اجرای Toolها برای هر Case در Window حداکثر ۲۴ ساعت؛
- Randomize کردن Tool order داخل Blockهای Difficulty/Segment؛
- ثبت زمان، Queue، Region و Service error؛
- Randomize کردن جای چپ/راست در Pairwise evaluation.

این زیرنمونه Variability را تشخیص می‌دهد؛ آن را برآورد کامل Reliability کل سیستم معرفی نمی‌کنیم.

### 3.6 Judge یک Instrument است

پژوهش MT-Bench/Chatbot Arena نشان داد LLM judge می‌تواند برای Scale مفید باشد، اما Position، Verbosity و Self-enhancement bias دارد. کنترل‌های پروژه:

- Swap کردن ترتیب A/B؛
- حذف نام و نشانهٔ Tool؛
- Rubric ثابت با Anchor قابل مشاهده؛
- جداکردن factual verification از Actionability؛
- Calibration روی Gold انسانی؛
- بررسی Agreement به تفکیک Dimension؛
- Human review برای همهٔ Critical facts و Disagreementهای مهم.

Judge خروجی را به Claim می‌شکند و Pre-label می‌دهد؛ Verdict بحرانی انسانی است.

### 3.7 Failure policy بخشی از Metric است

| رخداد | قاعدهٔ Main run | وضعیت تحلیلی |
|---|---|---|
| Timeout | پایان در سقف ۳۰ دقیقه | Failure + زمان کامل ثبت شود |
| Service error | یک Retry با فاصلهٔ ثابت | Reliability event باقی بماند |
| Refusal | بدون Retry محتوایی | Failure یا Safety track طبق Case |
| Incomplete output | بدون تکمیل انسانی | Missing طبق Metric registry |
| Parser error | Raw دست‌نخورده؛ Parser اصلاح و version شود | Deviation/processing event |
| Operator intervention | فقط Adaptation مجاز | Action در Log ثبت شود |

`Unknown`، `Missing` و `Failure` یک چیز نیستند. حذف Silent یک Error، Reliability را مصنوعی بهتر می‌کند.

### 3.8 Auditability به‌جای ادعای Reproducibility کامل

Productهای بسته، مدل‌های درحال تغییر و وب زنده ممکن است دقیقاً بازتولید نشوند. هدف عملی:

- `Traceable`: هر Score به Label، Claim، Raw output و Run وصل باشد؛
- `Auditable`: شخص ثالث بفهمد چه اتفاقی افتاده است؛
- `Repeatable where possible`: با همان نسخه و تنظیمات بتوان Run نزدیک ساخت؛
- `Versioned`: تغییرات Benchmark، Dataset، Protocol و Tool جدا ثبت شوند.

NIST AI 800-2 توصیه می‌کند Full log کنار Summary حفظ شود و Exact model/system version داخل Log باشد.

---

## 4. فلو زمانی نهایی

| زمان | Beat | هدف | Proof object |
|---|---|---|---|
| 00:00–01:15 | Same prompt, three outputs | شکستن توهم Determinism | three-run trace |
| 01:15–03:20 | What are we estimating? | تعریف Estimand | four outcome cards |
| 03:20–06:10 | The environment changes the result | کنترل نسخه و دسترسی | environment manifest |
| 06:10–08:25 | Same prompt is not always fair | Standardized vs optimized | prompt diff + adaptation log |
| 08:25–10:40 | One run is not a distribution | تکرار و Order effect | randomized block timeline |
| 10:40–13:10 | The judge can move the score | Bias و Calibration | blind judge swap test |
| 13:10–15:30 | Trace every number | Logging و Auditability | score-to-raw trace |
| 15:30–17:30 | Keep the failures | Failure policy | failure decision tree |
| 17:30–18:50 | Freeze Protocol v1.0 | Build واقعی | protocol inspector |
| 18:50–19:40 | Verdict and bridge | ورود به Risk Audit | frozen protocol under attack |

---

## 5. متن کامل آمادهٔ ضبط

### 00:00–01:15 — همان سؤال، سه پاسخ

**تصویر:** یک Case واقعی، یک Prompt hash و سه Run کنار هم. فقط خروجی‌های واقعی Dry Run نمایش داده شوند؛ تا آن زمان از `DEMO DATA` استفاده شود.

**متن گفتاری:**

«یک سؤال. یک Tool. یک Prompt کاملاً یکسان.

و سه پاسخ که یکی نیستند. تعداد منابع فرق دارد. زمان فرق دارد. شاید حتی نتیجه‌گیری فرق کند.

حالا فرض کنید فقط بهترینشان را نگه دارم. آن‌وقت Tool را Benchmark نکرده‌ام — بهترین برداشتش را انتخاب کرده‌ام.

و اگر فقط بدترین را نگه دارم؟ آن هم بی‌طرفی نیست.

پس سؤال مهم این نیست که کدام خروجی را بیشتر دوست دارم. سؤال این است: قبل از اجرا گفته بودم کدام خروجی حساب می‌شود؟

در سیستم‌های `Stochastic` (تصادفی‌رفتار)، Protocol یک تنظیم پشت‌صحنه نیست. Protocol بخشی از همان چیزی است که اندازه می‌گیریم.

امروز آن را قبل از Main run قفل می‌کنیم. تا نتیجهٔ خوب و نتیجهٔ بد، شانس برابر برای دیده‌شدن داشته باشند.»

**در یک جمله:** وقتی یک ورودی چند خروجی می‌دهد، «کدام خروجی حساب می‌شود» باید قبل از دیدن خروجی‌ها تصمیم گرفته شده باشد.

**روی تصویر:**

`THE RESULT CHANGED. THE QUESTION DIDN'T.`

### 01:15–03:20 — قبل از Fairness، Estimand را تعریف کن

**تصویر:** چهار Outcome card: `FIRST RUN / BEST OF 3 / EXPERT OPTIMIZED / FIXED BUDGET`.

**متن گفتاری:**

«وقتی می‌گوییم Performance، دقیقاً کدام Performance؟

اولین خروجی یک کاربر عادی؟ بهترین خروجی بعد از سه تلاش؟ خروجی‌ای که یک Prompt engineer بعد از یک ساعت گرفته؟ یا میانگین کیفیت زیر یک سقف هزینه؟

این‌ها یک Metric با چهار تنظیم نیستند. چهار سؤال اندازه‌گیری کاملاً متفاوت‌اند.

واژهٔ دقیقش `Estimand` (کمیت هدف) است: همان چیزی که می‌خواهیم با آزمایش تخمین بزنیم.

Estimand اصلی ما این است — و کلمه به کلمه‌اش مهم است:

عملکرد مورد انتظار یک Founder غیرفنی، در اولین اجرای معتبر، با Prompt استاندارد، زیر سقف زمان و هزینه.

نه بهترین Run. نه سقف عملکرد با یک اپراتور متخصص.

کنار این، دوازده Case را سه بار اجرا می‌کنیم تا ببینیم خروجی چقدر نوسان دارد. اما Best-of-3 را با تجربهٔ یک‌بار استفاده قاطی نمی‌کنیم.

قاعده ساده است: اگر سؤال عوض شد، برچسب نتیجه هم باید عوض شود.»

**در یک جمله:** قبل از اینکه بپرسیم «منصفانه است؟» باید بدانیم داریم دقیقاً چه چیزی را اندازه می‌گیریم.

**خط کلیدی:**

> «آزمایش منصفانه از یکسان‌کردن شروع نمی‌شود؛ از روشن‌کردن سؤال شروع می‌شود.»

### 03:20–06:10 — Environment بخشی از سیستم است

**تصویر:** Inspector زنده با فیلدهای Tool، Plan، Model label، Interface، Region، Web access، Files، Date، Queue، Cost cap.

**متن گفتاری:**

«نام Tool برای ثبت آزمایش کافی نیست. ما یک Product زنده را می‌سنجیم، و Product یک اسم ثابت نیست.

پس این‌ها را می‌پرسیم. Plan اشتراک چیست؟ کدام مدل پشت Interface فعال است؟ حالت Research روشن بوده؟ دسترسی به وب، فایل یا Connector داشته؟ Region کجاست؟ Run چه تاریخی بوده؟

دلیلش این است: دو کاربر می‌توانند همان نام Tool را ببینند و عملاً از دو سیستم متفاوت استفاده کنند.

Budget را هم روی هر Case قفل می‌کنیم. حداکثر سی دقیقه، حداکثر ده دلار. Retry هم داخل همین Budget است.

زمان صف را جدا ثبت می‌کنیم، ولی حذفش نمی‌کنیم. کاربر صف را هم تجربه می‌کند.

NIST AI 800-2 یک اصل دارد: Protocol باید به هدف Evaluation خدمت کند.

هدف ما خرید یک Product توسط Founder است. پس تست کنترل‌شدهٔ API به‌تنهایی جواب ما نیست. API و UI دو سیستم جدا هستند. شاید هر دو را تست کنیم — ولی در دو Track جدا، نه یک Ranking.

و چون وب تغییر می‌کند، همهٔ ابزارها برای یک Case در یک بازهٔ نزدیک اجرا می‌شوند. منابع مرجع هم در همان بازه Snapshot می‌شوند.

نکتهٔ آخر را نگه دارید: ما فقط مدل را اندازه نمی‌گیریم. مدل، ابزارها، Interface و وب را با هم به‌عنوان یک System می‌سنجیم.»

**در یک جمله:** «GPT در برابر Claude» یک آزمایش نیست — آنچه واقعاً می‌سنجیم یک محصول کامل در یک محیط مشخص است.

### 06:10–08:25 — Prompt یکسان همیشه منصفانه نیست

**تصویر:** چپ `STANDARDIZED TRACK`، راست `OPTIMIZED TRACK`. در وسط Adaptation log.

**متن گفتاری:**

«روش رایج این است: همان Prompt را Copy و Paste کنیم و بگوییم شرایط برابر بود.

ساده است. ولی همیشه منصفانه نیست.

فرض کنید یک Tool لینک می‌گیرد و دیگری فقط فایل. اگر همان اطلاعات را در قالب بومی هرکدام بدهیم، ورودی از نظر فنی فرق کرده — ولی کار منصفانه‌تر شده.

شرطش یکی است: `Adaptation` (تطبیق ورودی) نباید اطلاعات یا استدلال تازه اضافه کند.

پس دو Track تعریف می‌کنیم.

در Standardized track، Brief، خروجی لازم، محدودیت‌ها و دستور زبان Prompt مشترک‌اند.

در Optimized track، هر Tool می‌تواند Workflow بومی خودش را داشته باشد. اما بودجهٔ بهینه‌سازی برابر است و کل tuning فقط روی Pilot انجام می‌شود.

چرا این‌قدر سخت‌گیری؟ چون اگر پنج Prompt را برای Tool A امتحان کنیم و یکی را برای B، دیگر کیفیت ابزارها را نمی‌سنجیم. میزان توجه خودمان را می‌سنجیم.

یک آزمون کوچک هم داریم. شش Case را یک‌بار با Schema سخت و یک‌بار با Schema آزاد اجرا می‌کنیم.

اگر Ranking عوض شد، نمی‌گوییم کدام درست است. می‌گوییم نتیجه به قالب خروجی حساس است. و همین را گزارش می‌کنیم.»

**در یک جمله:** انصاف یعنی حذف مزیتی که از روش تست آمده، نه حذف تفاوتی که خود محصول است.

### 08:25–10:40 — یک Run، Distribution نیست

**تصویر:** ۱۲ Case در سه Repeat، با Blockهای Easy/Medium/Hard و Tool order تصادفی.

**متن گفتاری:**

«سه تکرار کامل برای چهل‌وهشت Case و پنج Tool یعنی هزینه و برچسب‌گذاری چند برابر. نسخهٔ اول باید هم علمی باشد هم شدنی.

پس این‌طور می‌کنیم. یک Main run روی همهٔ Caseها. و سه تکرار روی یک زیرنمونهٔ دوازده‌تایی که از همهٔ لایه‌ها نمونه دارد.

این زیرنمونه Variability را تشخیص می‌دهد. ادعای کامل دربارهٔ Reliability نمی‌سازد و ما هم چنین ادعایی نمی‌کنیم.

حالا دو تکنیک که مهم‌اند.

اول `Blocking` (بلوک‌بندی). Caseها را طوری گروه می‌کنیم که هر بلوک ترکیبی نزدیک از Segment و Difficulty داشته باشد.

دوم `Randomization` (تصادفی‌سازی). ترتیب ابزارها را داخل هر بلوک تصادفی می‌کنیم.

چرا؟ چون اگر Tool A همیشه صبح اجرا شود و Tool E همیشه شب، فشار سرویس یا تغییر وب با نام ابزار قاطی می‌شود. آن‌وقت نمی‌فهمیم کدام اثر مال کیست.

در Pairwise evaluation هم جای چپ و راست تصادفی است. اگر Seed قابل کنترل باشد ثبتش می‌کنیم؛ اگر نباشد، Run ID و Timestamp را نگه می‌داریم.

و قاعدهٔ اصلی این بخش: قانون تجمیع بعد از دیدن خروجی‌ها اختراع نمی‌شود.

Best run، Median run یا First valid run — هرکدام را که می‌خواهید. فقط باید قبل از اجرا انتخاب شده باشد.»

**در یک جمله:** یک اجرا یک نقطه است، نه یک توزیع — و ترتیب اجرا خودش می‌تواند به یک ابزار امتیاز بدهد.

### 10:40–13:10 — Judge می‌تواند برنده را جابه‌جا کند

**تصویر:** دو Report بی‌نام. ابتدا Judge با A/B، سپس Swap به B/A. Verdict تغییر می‌کند و Badge `POSITION SENSITIVE` روشن می‌شود.

**متن گفتاری:**

«خروجی Research جواب چندگزینه‌ای نیست. برای Scale به `Judge` (داور) ماشینی نیاز داریم.

اما یک چیز را نباید فراموش کنیم: Judge خودش یک دستگاه اندازه‌گیری است.

پژوهش MT-Bench نشان داد داورهای زبانی به سه چیز حساس‌اند. ترتیب پاسخ. طول پاسخ. و خروجی مدل‌های هم‌خانوادهٔ خودشان.

پس یک Prompt و یک اسم مدل، اعتبار نمی‌سازد. کنترل لازم است.

پاسخ‌ها بی‌نام می‌شوند. ترتیب A و B جابه‌جا می‌شود. Rubric رفتار قابل‌مشاهده توصیف می‌کند، نه صفت‌هایی مثل "excellent".

و یک ترتیب مهم: Factها و Citation قبل از Actionability بررسی می‌شوند. چرا؟ چون یک Report خوش‌نگارش می‌تواند حس درست‌بودن بدهد. این را نمی‌گذاریم روی داوری صحت اثر بگذارد.

نقش Judge ماشینی مشخص است. Claimها را استخراج می‌کند و برچسب اولیه می‌زند. تمام.

تمام Factهای بحرانی، یک نمونهٔ تصادفی و همهٔ اختلاف‌های بزرگ را انسان بررسی می‌کند.

Agreement را هم یک عدد کلی نمی‌کنیم. ممکن است Judge در Citation خوب باشد و در Actionability ضعیف. این دو را جدا گزارش می‌کنیم.

و یک قاعدهٔ ساده: اگر با جابه‌جاکردن ترتیب، رأی Judge عوض شد، آن Case می‌رود برای بازبینی انسانی.

توجه کنید — این Failure ابزار ارزیابی ماست، نه Failure ابزاری که داریم می‌سنجیم.»

**در یک جمله:** داور بخشی از دستگاه اندازه‌گیری است، پس خودش هم باید کالیبره و گزارش شود.

### 13:10–15:30 — هر Score باید مسیر برگشت داشته باشد

**تصویر:** کلیک روی Score و بازشدن مسیر `Score → Label → Claim → Raw Output → Run → Environment`.

**متن گفتاری:**

«اصل این بخش یک جمله است. هر عدد نهایی باید مسیر برگشت به شواهد خام داشته باشد.

برای هر Run این‌ها ثبت می‌شوند: Case ID، Tool ID، نسخهٔ Protocol، هش Prompt، زمان شروع و پایان، ورودی خام، خروجی خام، Citationها، Usage، هزینه، Retry، Error و هر اقدام اپراتور.

یک قانون سفت: خروجی خام ویرایش نمی‌شود.

اگر Parser اشتباه کند، نسخهٔ Parse‌شده اصلاح و نسخه‌گذاری می‌شود. خام دست‌نخورده می‌ماند. اگر اپراتور مجبور شد فایلی را دوباره Attach کند، همان لحظه در Log می‌آید.

حالا یک حرف صادقانه. تکرارپذیری کامل، برای وب زنده و ابزار بسته، همیشه ممکن نیست.

پس ادعای ما این نیست. ادعای ما `Auditability` (قابلیت بازرسی) است.

یعنی شخص دیگری باید بتواند ببیند چه اجرا شد، چه چیزی تغییر کرد، و چرا امروز ممکن است جواب دیگری بگیرد.

و آخرین نکته: نسخه چهار لایه دارد. Benchmark، Dataset، Protocol و Tool.

عبارت "آخرین مدل" نسخه نیست. تاریخ، Plan و برچسب قابل‌مشاهده باید ثبت شوند.»

**در یک جمله:** تکرارپذیری کامل را قول نمی‌دهیم؛ قابلیت بازرسی را قول می‌دهیم — و آن یکی شدنی است.

### 15:30–17:30 — Failureها را بعداً تعریف نکن

**تصویر:** Failure decision tree با Timeout، Service error، Refusal، Incomplete، Parser error.

**متن گفتاری:**

«سه سؤال، که همه‌شان وسط کار پیش می‌آیند.

اگر Tool بعد از سی‌ویک دقیقه جواب عالی بدهد، حساب می‌شود؟

اگر یک بار Error داد و تلاش دوم موفق شد، آن Error پاک می‌شود؟

اگر نصف Report را نوشت، جای خالی را صفر می‌گذاریم یا کل Case را کنار می‌گذاریم؟

نکته اینجاست: اگر این تصمیم‌ها بعد از دیدن نام Tool گرفته شوند، راه Cherry-picking باز است. پس همین حالا تصمیم می‌گیریم.

Timeout در سی دقیقه، Failure است. تمام.

Service error یک Retry دارد با فاصلهٔ ثابت. ولی Error اول از Log پاک نمی‌شود.

خروجی ناقص را انسان کامل نمی‌کند.

خطای Parser روی نتیجهٔ Tool اثر ندارد. Parser اصلاح و نسخه‌گذاری می‌شود و یک Deviation ثبت می‌گردد.

Refusal کمی پیچیده‌تر است. اگر Case سالم و داخل Scope بود، Refusal یک Failure است. اما اگر Case پرریسک یا خارج Scope بود، ایراد از طراحی Dataset ماست — و باید به Safety track برود.

و دو کلمهٔ آخر که یکی نیستند. Unknown را صفر نمی‌کنیم. Missing را بی‌صدا حذف نمی‌کنیم.

چرا این‌قدر مهم است؟ چون Failure policy تعیین می‌کند چه چیزی وارد مخرج کسر می‌شود. یعنی خودش بخشی از معنای Metric است.»

**در یک جمله:** قواعد Failure قبل از اجرا نوشته می‌شوند، وگرنه بعداً همان قواعد را می‌سازیم که نتیجهٔ دلخواهمان را بدهد.

### 17:30–18:50 — Freeze کردن Protocol نسخهٔ 1.0

**تصویر:** کاربر فیلدها را تکمیل می‌کند و `FREEZE v1.0` را می‌زند. Hash و Timestamp ظاهر می‌شود.

**متن گفتاری:**

«حالا نسخهٔ یک را قفل می‌کنیم. با هم مرور کنیم چه چیزی بسته می‌شود.

چهل‌وهشت Case، شامل Pilot و Main و Holdout. یک Main run برای همهٔ ابزارها. سه تکرار روی دوازده Case لایه‌بندی‌شده.

Prompt استاندارد با نسخهٔ ثبت‌شده. بازهٔ حداکثر بیست‌وچهار ساعت برای هر Case. سقف سی دقیقه و ده دلار. یک Retry برای خطای سرویس.

خروجی خام بدون ویرایش. برچسب‌گذاری کور. Judge فقط برای نمرهٔ اولیه. بررسی انسانی برای Factهای بحرانی. برچسب‌گذاری دوگانه روی حداقل بیست درصد.

تحلیل paired روی Caseهای یکسان. و گزارش Distribution، عدم‌قطعیت، بدترین گروه و Failureهای بحرانی.

هر انحراف هم یک `deviation_id` می‌گیرد، با دلیل، زمان کشف و اثر احتمالی. انحراف جدی هم در تحلیل اصلی Flag می‌شود هم در تحلیل حساسیت.

یک چیز را روشن بگویم. Freeze تضمین نمی‌کند طراحی ما درست است.

فقط جلوی یک کار را می‌گیرد: اینکه بعداً وانمود کنیم تصمیم‌های بعد از نتیجه، از اول وجود داشته‌اند.»

**در یک جمله:** Freeze طراحی را درست نمی‌کند؛ فقط نمی‌گذارد بعداً تاریخ را بازنویسی کنیم.

### 18:50–19:40 — Verdict و پل به قسمت هفتم

**تصویر:** Protocol Freeze می‌شود؛ سپس X-Ray آن Riskهای Leakage، Judge bias و Selective reporting را نشان می‌دهد.

**متن گفتاری:**

«مقایسهٔ منصفانه یعنی تفاوت‌های Protocol با Claim بخوانند. نه اینکه همه‌چیز ظاهراً یکسان باشد.

ما هشت چیز را قبل از Main run ثبت کردیم: سؤال، محیط، بودجه، سیاست Prompt، تکرار، Judge، Logging و قواعد Failure.

اما یک واقعیت ناراحت‌کننده باقی است. یک Protocol کاملاً شفاف هم می‌تواند روی سؤال بد، Dataset آلوده یا Metric قابل‌بازی سوار باشد.

پس قسمت بعد، همین Benchmark خودمان را مثل یک بازرس باز می‌کنیم.

Leakage، Goodhart، Cherry-picking، سوگیری Judge، ناپایداری Ranking و فاصلهٔ آزمایشگاه تا محصول.

هدفمان ساختن یک Trust Score خوشگل نیست. هدف پیداکردن جایی است که شواهد تمام می‌شوند.»

**در یک جمله:** Protocol شفاف لازم است، ولی کافی نیست — قسمت بعد همین شفافیت را زیر فشار می‌گذاریم.

**پایان روی تصویر:**

`NEXT: THE LEADERBOARD ILLUSION`

---

## 6. Experimental Protocol v1.0

| بخش | تصمیم Freeze‌شده |
|---|---|
| Estimand | first valid run for a non-technical founder under fixed constraints |
| Interface | Consumer product UI؛ API در Track جدا |
| Cases | 48 total: 6 pilot / 36 main / 6 holdout |
| Repeats | 1 main run + 3 runs on 12 stratified cases |
| Time cap | 30 minutes per run including retry |
| Cost cap | USD 10 per run; actual billed cost logged |
| Prompt | standardized prompt؛ version/hash required |
| Adaptation | interface-only; no added reasoning or information |
| Retry | one fixed-delay retry for service error only |
| Annotation | blinded; 20% double; critical facts human-verified |
| Judge | pre-label only; A/B swap; calibrated by dimension |
| Analysis | paired case-level comparison + uncertainty + sensitivity |
| Publication | raw/derived evidence subject to license/privacy |

---

## 7. Run Log Schema

| گروه | فیلدهای ضروری |
|---|---|
| Identity | `run_id`, `case_id`, `tool_id`, `protocol_version` |
| Environment | `tool_version`, `plan`, `interface`, `region`, `access_flags` |
| Input | `prompt_version`, `prompt_hash`, `attachments`, `operator_action` |
| Timing | `queued_at`, `started_at`, `completed_at`, `active_time`, `total_wait` |
| Usage | `tokens_if_available`, `searches_if_available`, `billed_cost`, `retry_count` |
| Output | `raw_uri`, `parsed_uri`, `citation_count`, `completion_status` |
| Failure | `error_type`, `timeout`, `refusal`, `deviation_id` |
| Audit | `checksum`, `created_by`, `annotation_status`, `review_status` |

### Deviation Log

`deviation_id / run_id / detected_at / planned_rule / observed_event / action_taken / expected_bias / inclusion_status / reviewer`

---

## 8. طراحی تجربهٔ بصری

### صحنهٔ اصلی: Protocol Flight Recorder

صفحه شبیه ابزار کنترل آزمایش است، نه فرم اداری:

- چپ: Case و Tool sequence؛
- مرکز: Timeline اجرای Runها؛
- راست: Inspector نسخه، Prompt، Access، Cost و Failure؛
- پایین: Trace زنده از Score تا Raw output؛
- حالت `FREEZE`: همهٔ فیلدها قفل و Hash نمایان شود؛
- حالت `DEVIATION`: فقط خط تغییرکرده Amber و اثر احتمالی آن باز شود.

### Interactionهای اصلی

1. `RUN THREE TIMES`: سه خروجی واقعی را کنار هم باز کند.
2. `CHANGE ESTIMAND`: Ranking view میان first-run و best-of-3 تغییر کند.
3. `SWAP JUDGE ORDER`: Position sensitivity را نشان دهد.
4. `TRACE SCORE`: مسیر Evidence را مرحله‌به‌مرحله باز کند.
5. `FREEZE v1.0`: صفحه را از Design mode به Evidence mode ببرد.

### قواعد تصویر

- خروجی Dry Run واقعی باشد یا Badge واضح `DEMO DATA` داشته باشد.
- هیچ اسم Tool کنار Judge انسانی نمایش داده نشود.
- Error و Timeout از Timeline حذف نشوند.
- Version، Date، N و Cost روی هر نمودار باقی بمانند.
- A-roll بیش از ۷۵ ثانیه بدون تغییر Proof object نماند.

---

## 9. سایت‌هایی که باید نمایش داده شوند

| زمان | سایت | چیزی که نمایش داده می‌شود | نکتهٔ گفتاری |
|---|---|---|---|
| 02:40 | NIST AI 800-2 | سه مرحله و Practice 2.1 | سند `Initial Public Draft — January 2026` است |
| 04:20 | NIST AI 800-2 | Comparability، External validity، Cost control | Protocol تابع Objective است |
| 09:40 | NIST AI 800-2 | trials per item و tracking results | یک Run، System distribution نیست |
| 11:20 | MT-Bench paper | Position/verbosity/self-enhancement biases | Judge مفید اما نیازمند Audit است |
| 14:20 | MLCommons Benchmark Work | Rules و Reproducibility | مثال Governance صنعتی، نه نسخهٔ آماده برای پروژه |
| 18:20 | NIST AI 800-3 | explicit statistical model و sources of variation | روش پیشرفته‌تر برای نسخهٔ بعد |

---

## 10. چک‌لیست علمی قبل از ضبط

- [ ] سه خروجی Hook از Dry Run واقعی‌اند یا `DEMO DATA` دارند.
- [ ] Estimand اصلی و Secondary analysis جدا نوشته شده‌اند.
- [ ] UI و API در یک Ranking مخلوط نشده‌اند.
- [ ] Plan، Version، Region، Date و Access flags ثبت شده‌اند.
- [ ] Prompt tuning فقط روی Pilot انجام شده است.
- [ ] Tool order و A/B position واقعاً Random شده‌اند.
- [ ] Repeated subset قبل از Result انتخاب شده است.
- [ ] Judge swap و Human calibration انجام شده‌اند.
- [ ] Timeout، Retry، Refusal و Missing rule از قبل Freeze شده‌اند.
- [ ] Raw output قابل تغییر نیست و Parser version جداست.
- [ ] همهٔ Scoreها Evidence trace دارند.
- [ ] NIST AI 800-2 به‌عنوان Initial Public Draft معرفی شده است.
- [ ] هیچ‌جا Freeze یا Preregistration «تضمین اعتبار» نامیده نمی‌شود.

---

## 11. بستهٔ ضبط

### A-roll حذف‌ناپذیر

- تفاوت Estimandها؛
- Fairness در برابر sameness؛
- Standardized vs optimized؛
- Judge as instrument؛
- Failure policy؛
- معنای Freeze.

### Screen recording

- سه Run واقعی یک Case؛
- Prompt diff و hash؛
- Randomized run order؛
- Blind judge swap؛
- Score-to-raw evidence trace؛
- Freeze و ثبت Deviation.

### Pattern interrupt

- 01:15: چهار Estimand؛
- 06:10: دو Track؛
- 10:40: Judge swap؛
- 13:10: Trace animation؛
- 17:30: Freeze event.

### حذف‌ناپذیر در تدوین

- جملهٔ «یک Run، Distribution نیست»؛
- محدودیت زیرنمونهٔ ۱۲ Case؛
- باقی‌ماندن Service error پس از Retry موفق؛
- تفاوت Auditability و Reproducibility کامل؛
- توضیح اینکه Freeze کیفیت را تضمین نمی‌کند.

---

## 12. CTA نهایی

> «Protocol Template را قبل از اولین Main run کامل و Freeze کنید. سپس یک Case را سه بار اجرا کنید. اگر Result تغییر کرد، قبل از افزایش Sample مشخص کنید کدام منبع Variation را ثبت نکرده‌اید.»

**Comment prompt:**

> در مقایسه‌های AI کدام متغیر بیشتر از همه نادیده گرفته می‌شود: Prompt، Version، Retry، Judge یا زمان اجرا؟

---

## 13. منابع اصلی این قسمت

1. NIST, [Practices for Automated Benchmark Evaluations of Language Models — NIST AI 800-2 IPD](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf), January 2026.
2. NIST, [Expanding the AI Evaluation Toolbox with Statistical Models — NIST AI 800-3](https://www.nist.gov/publications/expanding-ai-evaluation-toolbox-statistical-models), February 2026.
3. Zheng et al., [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685), 2023.
4. MLCommons, [Benchmark Work](https://mlcommons.org/benchmarks/).
5. Madaan et al., [Quantifying Variance in Evaluation Benchmarks](https://arxiv.org/abs/2406.10229), 2024.
6. Google AI for Developers, [Gemini Deep Research Agent](https://ai.google.dev/gemini-api/docs/deep-research), documentation accessed August 2026.

---

## 14. خطاهای ممنوع

- انتخاب بهترین Run بدون Label `best-of-n`؛
- تغییر Prompt یا Metric پس از Result بدون Change Log؛
- حذف Service error یا Timeout از Denominator بدون Rule قبلی؛
- معرفی LLM judge به‌عنوان Ground truth؛
- مقایسهٔ Toolهای اجراشده در Windowهای دور بدون Date badge؛
- استفاده از عبارت «شرایط کاملاً یکسان» وقتی Interface و Access متفاوت‌اند؛
- انتشار Secret، Session token، دادهٔ شخصی یا محتوای دارای محدودیت.

