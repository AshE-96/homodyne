# M2Lab Benchmarking Foundations — Episode 02

## Every Type of AI Benchmark Explained

**نسخه:** 1.0 — آمادهٔ ضبط  
**زبان روایت:** فارسی  
**زبان عناصر روی تصویر:** انگلیسی  
**زمان هدف:** 19:30 تا 21:00  
**خروجی این قسمت:** `M2Lab Benchmark Landscape Map v1`  
**پروژهٔ فصل:** انتخاب Benchmark Stack برای مقایسهٔ ابزارهای Deep Research در تحقیق بازار استارتاپ

---

## 1. قول این قسمت به مخاطب

در پایان این قسمت، مخاطب قرار نیست نام چهارده Benchmark را حفظ کرده باشد. باید بتواند هر Benchmark جدید را با چهار سؤال کالبدشکافی کند:

1. دقیقاً چه ادعایی را می‌سنجد؟
2. Task واقعی داخل آن چیست؟
3. با چه Metricی نتیجه می‌دهد؟
4. مهم‌ترین Blind Spot آن چیست؟

جملهٔ محوری قسمت:

> **A model has no single rank. It has a performance profile.**

نسخهٔ فارسی برای روایت:

> یک مدل «رتبهٔ واقعی» واحد ندارد؛ بسته به چیزی که اندازه می‌گیریم، یک پروفایل عملکرد دارد.

---

## 2. مسئلهٔ روایی

### THE CLAIM

«مدلی که در Leaderboard بالاتر است، مدل بهتری است.»

### THE EVIDENCE

Leaderboardها اغلب Taskها، Datasetها و Metricهای متفاوت را به عددهایی تبدیل می‌کنند که در ظاهر قابل مقایسه‌اند، اما به سؤال‌های متفاوت جواب می‌دهند. MMLU دانش چندموضوعی را روی ۵۷ Task می‌سنجد؛ HumanEval درستی عملکردی کدهای کوتاه را با Test بررسی می‌کند؛ SWE-bench اصلاح Issue واقعی در Repository را می‌سنجد؛ Arena ترجیح انسانی را از مقایسه‌های جفتی جمع می‌کند.

### THE STRESS TEST

یک مدل فرضی را از چهار لنز Knowledge، Coding، Agent و Efficiency نگاه می‌کنیم. با هر لنز، برنده و معنای «بهتر» تغییر می‌کند.

### THE VERDICT

رتبه فقط داخل مرز همان Measurement Contract معتبر است. تغییر Task، Dataset، Protocol یا Metric می‌تواند Ranking را تغییر دهد، بدون اینکه هیچ‌کدام از نتایج الزاماً جعلی باشند.

### THE BUILD

برای پروژهٔ Deep Research فصل، به‌جای یک Benchmark مشهور، یک Benchmark Stack پنج‌لایه می‌سازیم: Retrieval، Factuality، Product Outcome، Efficiency و Robustness.

---

## 3. مدل علمی قسمت

### 3.1 دو محور نقشه

محور افقی:

- `CONTROLLED / STATIC`: سؤال‌ها و محیط از قبل ثابت‌اند؛ تکرارپذیری بیشتر، واقع‌گرایی معمولاً کمتر.
- `LIVE / INTERACTIVE`: سیستم با محیط، ابزار یا کاربر تعامل می‌کند؛ واقع‌گرایی بیشتر، کنترل و بازتولید دشوارتر.

محور عمودی:

- `REFERENCE ANSWER`: پاسخ، Test یا وضعیت موفقیت از قبل تعریف شده است.
- `HUMAN / JUDGE / OUTCOME`: کیفیت با ترجیح انسان، Rubric، Judge یا نتیجهٔ واقعی کار سنجیده می‌شود.

این ماتریس «Taxonomy رسمی و نهایی» نیست؛ یک مدل ذهنی M2Lab برای قرار دادن Benchmarkها و دیدن Trade-off میان تکرارپذیری، هزینه و واقع‌گرایی است.

### 3.2 چهارده خانواده

| خانواده | ادعای اصلی | Task نمونه | Metric رایج | Blind Spot اصلی |
|---|---|---|---|---|
| Knowledge | مدل چه می‌داند؟ | سؤال چندموضوعی | Accuracy | شناخت گزینه با کاربرد دانش یکی نیست |
| Reasoning | آیا چند مرحله استنتاج را مدیریت می‌کند؟ | سؤال دشوار چندمرحله‌ای | Exact/graded answer | جواب درست، فرایند درست را ثابت نمی‌کند |
| Mathematics | آیا مسئلهٔ ریاضی را حل می‌کند؟ | Word problem یا Competition problem | Exact/equivalent answer | حساسیت به قالب و آشنایی قبلی |
| Coding | آیا کد درست تولید می‌کند؟ | Function یا Patch | pass@k / tests passed | Test ناقص می‌تواند خطای واقعی را نبیند |
| Multimodal | آیا چند مدالیته را ترکیب می‌کند؟ | سؤال متن+تصویر/صوت/ویدئو | Accuracy / rubric | ممکن است بدون استفاده از مدالیته هم حل شود |
| Retrieval / RAG | آیا شواهد مناسب را پیدا و استفاده می‌کند؟ | Retrieve then answer | Recall@k / faithfulness | Retrieval و Generation می‌توانند خطاهای متفاوت داشته باشند |
| Agents / Tool Use | آیا هدف را در محیط انجام می‌دهد؟ | Browser/terminal task | Task success / steps | Environment و scaffold بخشی از نتیجه‌اند |
| Robustness | آیا با تغییر بی‌ربط پایدار می‌ماند؟ | Paraphrase/typo/injection | Performance drop | میانگین، سقوط Sliceها را پنهان می‌کند |
| Factuality | آیا ادعا پشتیبانی می‌شود؟ | Claim verification | Support/error rate | وجود Citation به معنی پشتیبانی نیست |
| Safety / Security | آیا رفتار پرریسک کنترل می‌شود؟ | Adversarial request | Attack success / refusal | Over-refusal می‌تواند Utility را نابود کند |
| Bias / Fairness | عملکرد میان گروه‌ها چطور تغییر می‌کند؟ | Group slices | Gap / worst-group | گروه‌ها و Labelها زمینه‌مندند |
| Human Preference | کدام خروجی بیشتر ترجیح داده می‌شود؟ | Blind pairwise comparison | Win rate / rating | ترجیح برابر با حقیقت نیست |
| Efficiency | با چه منابعی این کیفیت تولید می‌شود؟ | Fixed workload | latency / throughput / cost | بدون Hardware، Region و workload قابل مقایسه نیست |
| Product / Business | آیا کار واقعی بهتر انجام شد؟ | End-to-end user task | completion / time / ROI proxy | UI، آموزش و Context روی نتیجه اثر دارند |

### 3.3 قاعدهٔ انتخاب

> **Decision → Costly failure → Required evidence → Benchmark family**

از نام Benchmark شروع نکن. ابتدا تصمیم را بنویس، سپس Failure پرهزینه را مشخص کن، بعد Evidence لازم و خانوادهٔ مناسب را انتخاب کن.

---

## 4. فلو زمانی نهایی

| زمان | Beat | هدف روایی | Proof object روی تصویر |
|---|---|---|---|
| 00:00–01:15 | Cold open | شکستن ایدهٔ رتبهٔ واحد | یک مدل، چهار رتبه |
| 01:15–02:45 | The map | ساخت مدل ذهنی | ماتریس دو محوره |
| 02:45–07:10 | Capability | تشخیص توانایی‌های پایه | پنج Lens روی یک مدل |
| 07:10–10:45 | System & action | عبور از پاسخ به انجام کار | RAG pipeline + agent trace |
| 10:45–13:55 | Trust | جداکردن درست‌بودن، ایمنی و انصاف | Citation x-ray + refusal trade-off |
| 13:55–16:20 | Value | وصل‌کردن کیفیت به کاربر و هزینه | quality–cost plane |
| 16:20–18:20 | Diagnosis game | فعال‌کردن یادگیری | سه Brief قابل انتخاب |
| 18:20–19:45 | Build | ساخت Stack پروژه فصل | پنج لایهٔ Deep Research |
| 19:45–20:30 | Verdict & bridge | تثبیت Rule و ورود به قسمت ۳ | Decision first |

در تدوین می‌توان ۳۰ تا ۶۰ ثانیه از مثال‌های خانواده‌ها کم کرد، اما Cold open، Diagnosis game و Build نباید حذف شوند.

---

## 5. متن کامل آمادهٔ ضبط

### 00:00–01:15 — یک مدل، چهار پاسخ متفاوت

**ON SCREEN:** `THE CLAIM`  
**HEADLINE:** `ONE MODEL. FOUR RANKS.`

**تصویر:** نام یک مدل فرضی با برچسب واضح `ILLUSTRATIVE PROFILE`. چهار Lens یکی‌یکی فعال شوند: Knowledge = 91، Coding = 63، Agent = 38، Efficiency = 88. این اعداد دادهٔ واقعی نیستند و فقط برای نشان‌دادن منطق استفاده می‌شوند.

**متن گفتاری:**

«این مدل را نگاه کنید. اگر فقط سؤال‌های علمی از آن بپرسیم، شاید یکی از بهترین گزینه‌ها باشد. اگر از آن بخواهیم یک Bug واقعی را در یک Repository پیدا و اصلاح کند، رتبه‌اش پایین‌تر می‌آید. اگر مجبورش کنیم با مرورگر وارد چند صفحه شود، داده جمع کند و کار را تمام کند، ممکن است کاملاً شکست بخورد. و بااین‌حال، شاید سریع‌ترین و ارزان‌ترین مدل این مقایسه باشد.

پس کدام رتبه، رتبهٔ واقعی مدل است؟

هیچ‌کدام به‌تنهایی.

مدل یک رتبهٔ واحد ندارد؛ یک پروفایل عملکرد دارد. هر Benchmark فقط یکی از برش‌های این پروفایل را می‌بیند. مشکل از جایی شروع می‌شود که برش محدود را به یک حکم کلی تبدیل می‌کنیم: این مدل باهوش‌تر است، بهتر است یا برای محصول من مناسب‌تر است.

در این قسمت قرار نیست صد اسم را حفظ کنیم. می‌خواهیم یک نقشه بسازیم که هر Benchmark جدید را در چند ثانیه داخل آن قرار بدهیم و بفهمیم چه چیزی را می‌سنجد، چه چیزی را نمی‌بیند و برای کدام تصمیم مفید است.»

**EDIT:** هنگام جملهٔ «هیچ‌کدام به‌تنهایی»، همهٔ عددها محو شوند و فقط Radar profile باقی بماند.

### 01:15–02:45 — دو سؤال قبل از هر Benchmark

**ON SCREEN:** `THE MODEL`  
**HEADLINE:** `MAP THE TEST BEFORE YOU READ THE SCORE.`

**متن گفتاری:**

«برای ساختن نقشه، دو سؤال می‌پرسم.

سؤال اول: محیط ثابت و کنترل‌شده است یا زنده و تعاملی؟ در MMLU سؤال‌ها از قبل مشخص‌اند. اما در WebArena سیستم باید با یک محیط وب تعامل کند؛ انتخاب قبلی می‌تواند وضعیت مرحلهٔ بعد را تغییر دهد.

سؤال دوم: پاسخ درست از قبل داریم یا باید کیفیت را با انسان، Judge یا Outcome قضاوت کنیم؟ در یک مسئلهٔ ریاضی، جواب مرجع داریم. در Arena دو پاسخ ناشناس به کاربر نشان داده می‌شوند و او ترجیح خود را اعلام می‌کند. در یک Benchmark محصولی، شاید معیار واقعی زمان صرفه‌جویی‌شده یا نرخ تکمیل کار باشد.

هیچ گوشهٔ این نقشه ذاتاً بهتر نیست. محیط ثابت، ارزان‌تر و تکرارپذیرتر است؛ اما ممکن است از کار واقعی فاصله بگیرد. محیط زنده واقعی‌تر است؛ اما نسخهٔ ابزار، شبکه، UI و حتی زمان اجرا وارد آزمایش می‌شوند. Ground truth صریح، Scoring را ساده می‌کند؛ اما برای خروجی‌های باز همیشه پاسخ واحد نداریم. قضاوت انسانی این ظرافت را می‌گیرد، اما هزینه و اختلاف‌نظر را اضافه می‌کند.

این نقشه قرار نیست پیچیدگی را حذف کند. قرار است جای پیچیدگی را نشان دهد.»

### 02:45–04:45 — Knowledge، Reasoning و Math: سه چیز نزدیک اما یکسان‌نبودنی

**ON SCREEN:** `WHAT THE SCORE SEES`

**متن گفتاری:**

«اولین قلمرو Capability است. اما حتی اینجا سه خانواده‌ای که معمولاً با هم مخلوط می‌شوند، یکسان نیستند.

Knowledge Benchmark می‌پرسد مدل در گستره‌ای از موضوعات چه می‌داند و آیا می‌تواند پاسخ درست را تشخیص دهد. MMLU نمونهٔ کلاسیک است: ۵۷ Task از ریاضی و تاریخ تا حقوق و علوم کامپیوتر. مزیتش پوشش گسترده و اجرای نسبتاً ساده است. ولی سؤال چندگزینه‌ای می‌تواند حذف گزینه، شناخت الگو یا آشنایی با Dataset را هم پاداش دهد. امتیاز بالا روی آن ثابت نمی‌کند مدل بتواند یک پروژهٔ چندمرحله‌ای را تمام کند.

Reasoning Benchmark می‌خواهد استنتاج چندمرحله‌ای را سخت‌تر کند. GPQA در نسخهٔ اصلی ۴۴۸ سؤال تخصصی زیست، فیزیک و شیمی دارد؛ نویسندگان گزارش کردند متخصصان دارای یا درحال‌دریافت PhD حدود ۶۵ درصد دقت داشتند. اما حتی اینجا جواب نهایی درست، مسیر درست را تضمین نمی‌کند. مدل می‌تواند حدس درست بزند یا توضیحی قانع‌کننده برای پاسخ اشتباه بسازد.

Math Benchmark یک Construct محدودتر دارد: حل مسئلهٔ ریاضی. Metric معمولاً Exact Answer یا equivalence است. قوتش قضاوت روشن‌تر است؛ ضعفش این است که تغییر قالب، اعداد یا نوع صورت مسئله می‌تواند عملکرد را عوض کند.

این سه خانواده نزدیک‌اند، اما هر سه را با کلمهٔ مبهم “intelligence” جمع نکنید. هرچه Claim مبهم‌تر باشد، Score راحت‌تر بیش‌ازحد تفسیر می‌شود.»

### 04:45–07:10 — از Function تا Repository، و از Text تا Multimodal

**ON SCREEN:** `THE STRESS TEST`  
**HEADLINE:** `A PASSING TEST CAN STILL MISS THE JOB.`

**متن گفتاری:**

«در Coding تفاوت Task بسیار دیدنی است. HumanEval از مدل می‌خواهد تابع‌های کوتاه Python را از روی Docstring بسازد و کد با Unit Test سنجیده می‌شود. این یک Signal مفید از Functional correctness است.

اما مهندسی نرم‌افزار واقعی فقط ساخت یک تابع نیست. SWE-bench یک Repository و Issue واقعی می‌دهد و سیستم باید Patchی تولید کند که Testهای پروژه را پاس کند. اینجا جست‌وجوی فایل، فهم Context، تغییر چندبخشی و Environment وارد اندازه‌گیری می‌شوند.

ممکن است یک مدل روی HumanEval خوب باشد و روی SWE-bench ضعیف‌تر؛ تناقضی وجود ندارد. Task عوض شده است. حتی در SWE-bench هم Test Suite کامل‌بودن راه‌حل را تضمین نمی‌کند و محیط اجرا بخشی از Benchmark است.

در Multimodal همین اشتباه تکرار می‌شود. MMMU سؤال‌هایی با نمودار، نقشه، نت موسیقی و ساختار شیمیایی دارد. اما اگر سؤال بدون دیدن تصویر هم قابل پاسخ باشد، Score بالا لزوماً Vision understanding را ثابت نمی‌کند. به همین دلیل Text-only baseline مهم است: تصویر را حذف کن و ببین چه مقدار از عملکرد باقی می‌ماند.

قاعدهٔ این بخش ساده است: Benchmark را با نامش قضاوت نکن. Task را باز کن. ورودی واقعی چیست؟ خروجی چیست؟ Success چگونه تشخیص داده می‌شود؟»

### 07:10–08:50 — RAG: یک Score، سه محل شکست

**ON SCREEN:** `THE EVIDENCE`  
**HEADLINE:** `RETRIEVAL AND GENERATION FAIL DIFFERENTLY.`

**تصویر:** Pipeline سه‌مرحله‌ای `QUERY → RETRIEVAL → ANSWER`؛ روی هر مرحله یک Failure باز شود.

**متن گفتاری:**

«در RAG یک Accuracy کلی معمولاً تشخیص را خراب می‌کند. حداقل سه سؤال جدا داریم: آیا سند مرتبط پیدا شد؟ آیا پاسخ واقعاً به Context متکی بود؟ و آیا پاسخ نهایی درست و مفید بود؟

ممکن است Retrieval عالی باشد اما مدل از سند استفاده نکند. ممکن است پاسخ ظاهراً درست باشد اما از سند نامرتبط آمده باشد. یا ممکن است Citation وجود داشته باشد ولی منبع، Claim را پشتیبانی نکند.

برای همین Metricهایی مثل Recall@k، Context relevance، Faithfulness و Answer correctness را جدا می‌بینیم. چارچوب‌هایی مانند Ragas دقیقاً برای تفکیک بخش‌های Pipeline ساخته شده‌اند، هرچند Judge خودکار هم خطا و Bias دارد.

اگر فقط Final answer را ببینیم، نمی‌دانیم کدام جزء باید اصلاح شود. Benchmark خوب فقط Ranking تولید نمی‌کند؛ محل شکست را نیز قابل‌تشخیص می‌کند.»

### 08:50–10:45 — Agent: پاسخ خوب کافی نیست، کار باید تمام شود

**ON SCREEN:** `MEASURED, NOT ASSUMED`

**متن گفتاری:**

«Agent Benchmark از مدل می‌خواهد در محیط عمل کند: هدف را بفهمد، برنامه بسازد، ابزار انتخاب کند، نتیجهٔ ابزار را بخواند و از خطا برگردد. WebArena محیط‌های وب بازسازی‌شده دارد و Success نهایی Task را بررسی می‌کند.

اینجا پاسخ زیبا ارزشی ندارد اگر کار تمام نشود. Metric اصلی می‌تواند Task Success Rate باشد، اما برای فهم رفتار، Step count، cost، recovery rate، constraint violation و irreversible error را هم ثبت می‌کنیم.

Blind Spot مهم این خانواده خودِ Harness است. یک Agent با Browser tool بهتر، Memory بیشتر یا scaffold متفاوت ممکن است Score بالاتری بگیرد، حتی وقتی مدل پایه یکسان است. بنابراین ادعای دقیق باید درباره “سیستم تحت این پیکربندی” باشد، نه فقط نام مدل.

Robustness هم به همین قلمرو نزدیک است. یک Prompt را پارافرایز کنید، typo اضافه کنید، ترتیب گزینه‌ها را عوض کنید یا یک دستور مزاحم داخل سند بگذارید. اگر نتیجه سقوط کرد، میانگین روی دادهٔ تمیز این شکنندگی را پنهان کرده بود.»

### 10:45–12:20 — Factuality: لینک داشتن، شاهد داشتن نیست

**ON SCREEN:** `WHAT IT MISSES`  
**HEADLINE:** `A CITATION CAN EXIST AND STILL SUPPORT NOTHING.`

**تصویر:** یک Claim، یک Citation و سه وضعیت: `EXISTS / RELEVANT / SUPPORTS`.

**متن گفتاری:**

«در Factuality، واحد ارزیابی را کوچک می‌کنیم. یک Report می‌تواند ده‌ها Claim داشته باشد. برای هر Claim می‌پرسیم: منبع وجود دارد؟ معتبر و مرتبط است؟ و دقیقاً همین ادعا را پشتیبانی می‌کند؟

TruthfulQA با ۸۱۷ سؤال در ۳۸ دسته طراحی شد تا ببیند مدل‌ها باورهای غلط رایج انسانی را تکرار می‌کنند یا نه. اما Truthfulness با Honesty، Calibration یا Citation quality یکی نیست. یک مدل می‌تواند صادقانه اشتباه کند؛ یا با لحن مطمئن، ادعای درست اما بدون شاهد ارائه دهد.

برای پروژهٔ Deep Research، فقط شمردن لینک‌ها کافی نیست. Citation support باید Claim-level باشد. همین تفاوت کوچک جلوی یک Score فریبنده را می‌گیرد.»

### 12:20–13:55 — Safety و Fairness: کمتر پاسخ‌دادن همیشه امن‌تر نیست

**ON SCREEN:** `DOES NOT PROVE`

**متن گفتاری:**

«Safety Benchmark رفتار سیستم در برابر درخواست‌های پرریسک، Jailbreak و Prompt Injection را می‌سنجد. HarmBench و JailbreakBench تلاش کرده‌اند Threat model، رفتارهای هدف، حمله و Scoring را استانداردتر کنند.

اما نرخ Refusal بالا به‌تنهایی امنیت را ثابت نمی‌کند. مدلی که درخواست سالم را هم رد کند، Utility را از بین می‌برد. بنابراین Safety حداقل دو طرف دارد: Attack success روی درخواست‌های مضر و over-refusal روی درخواست‌های مجاز.

در Fairness هم Average کافی نیست. باید ببینیم عملکرد میان گروه‌ها، زبان‌ها و شرایط مختلف چطور تغییر می‌کند. ولی گروه‌ها و Labelها زمینه‌مندند؛ Dataset انگلیسی و آمریکایی نمایندهٔ جهان نیست. اگر Population هدف نوشته نشده باشد، Gap هم تفسیر روشنی ندارد.

Trust یک Dimension واحد نیست. درست‌بودن، ایمنی، انصاف و Calibration باید جدا دیده شوند، چون یک مدل می‌تواند در یکی قوی و در دیگری ضعیف باشد.»

### 13:55–16:20 — Preference، Efficiency و Product Outcome

**ON SCREEN:** `THE VERDICT`  
**HEADLINE:** `PREFERRED IS NOT THE SAME AS CORRECT.`

**متن گفتاری:**

«وقتی پاسخ واحد نداریم، Human preference مفید می‌شود. در Arena دو پاسخ ناشناس و تصادفی کنار هم قرار می‌گیرند و کاربر انتخاب می‌کند. این روش تفاوت‌هایی مثل وضوح، لحن و usefulness را بهتر از Exact Match می‌گیرد.

اما Preference یعنی مردم کدام پاسخ را بیشتر ترجیح داده‌اند؛ نه اینکه کدام پاسخ حقیقت بیشتری دارد. پاسخ طولانی‌تر یا مطمئن‌تر ممکن است جذاب‌تر باشد. ترکیب کاربران و Promptها نیز نتیجه را شکل می‌دهد.

Efficiency می‌پرسد این کیفیت با چه هزینه‌ای به دست آمده است: latency، throughput، memory، energy یا cost. MLCommons روی قواعد ثابت و مقایسهٔ منصفانه تأکید می‌کند. مقایسهٔ latency بدون Hardware، Region، Batch size و طول ورودی و خروجی تقریباً بی‌معناست.

و در نهایت Product Outcome: آیا کاربر کارش را سریع‌تر، دقیق‌تر یا با ریسک کمتر انجام داد؟ برای محصول، این نزدیک‌ترین خانواده به تصمیم است؛ ولی UI، آموزش، انگیزه و فرایند سازمانی وارد نتیجه می‌شوند.

به همین دلیل Benchmark آفلاین و Pilot واقعی رقیب هم نیستند. اولی کنترل می‌دهد؛ دومی Relevance. تصمیم خوب معمولاً به هر دو نیاز دارد.»

### 16:20–18:20 — بازی تشخیص: سه تصمیم، سه Stack متفاوت

**ON SCREEN:** `THE STRESS TEST`  
**تعامل:** سه Brief نشان داده شود. قبل از پاسخ، سه ثانیه مکث و از مخاطب خواسته شود خانواده‌ها را انتخاب کند.

**متن گفتاری:**

«حالا سه تصمیم را بدون تکیه بر نام Benchmark حل کنیم.

اول: می‌خواهیم مدلی برای پاسخ‌گویی به Ticketهای فنی انتخاب کنیم. Knowledge مفید است، اما کافی نیست. Retrieval برای پیدا کردن سند، Factuality برای تکیه بر سند، Task success برای حل واقعی Ticket، latency برای تجربهٔ کاربر و Escalation برای Failure لازم‌اند.

دوم: می‌خواهیم دستیار Coding داخل IDE بسازیم. HumanEval یک Signal اولیه است؛ اما برای کار واقعی Repository-level task، امنیت کد، latency و Acceptance rate توسعه‌دهنده مهم‌تر می‌شوند.

سوم: می‌خواهیم بهترین Chatbot عمومی را معرفی کنیم. Preference مهم است؛ ولی Factuality، Safety و Cost باید جدا باقی بمانند. اگر همه را داخل یک Score حل کنیم، Trade-off اصلی را از مخاطب پنهان کرده‌ایم.

الگوی مشترک چیست؟ هر سه بار از Decision شروع کردیم، Failure پرهزینه را نوشتیم و بعد خانواده‌ها را انتخاب کردیم. Benchmark مشهور نقطهٔ شروع نبود.»

### 18:20–19:45 — ساخت Stack پروژهٔ فصل

**ON SCREEN:** `THE BUILD`  
**HEADLINE:** `BUILD THE EVIDENCE STACK AROUND THE DECISION.`

**متن گفتاری:**

«سؤال پروژهٔ فصل این است: برای یک Founder غیرفنی، با دادهٔ عمومی وب و بودجه و زمان محدود، کدام ابزار Deep Research گزارش تحقیق بازار دقیق‌تر، قابل‌استنادتر و قابل‌اقدام‌تری تولید می‌کند؟

یک Benchmark عمومی دانش به این سؤال جواب نمی‌دهد. Stack نسخهٔ اول ما پنج لایه دارد.

Retrieval: آیا منابع مرتبط و متنوع پیدا شدند؟

Factuality: آیا Claimها واقعاً توسط همان منابع پشتیبانی می‌شوند؟

Product outcome: آیا خروجی، تصمیم بعدی Founder را روشن می‌کند؟

Efficiency: هر Report موفق چقدر زمان و هزینه می‌گیرد؟

Robustness: آیا با تغییر صنعت، جغرافیا، زبان یا کمبود داده، کیفیت سقوط می‌کند؟

Knowledge عمومی را مرکز قرار نمی‌دهیم، چون Decision ما انتخاب ابزار تحقیق بازار است. Agent behavior را نیز فقط در محدودهٔ استفاده از وب می‌سنجیم. این محدودکردن ضعف نیست؛ شرط ادعای قابل‌دفاع است.»

### 19:45–20:30 — جمع‌بندی و پل

**ON SCREEN:** `NEXT TEST`

**متن گفتاری:**

«پس Rule این قسمت این است: قبل از دیدن Score، خانوادهٔ اندازه‌گیری را پیدا کنید. بپرسید چه Claimی، چه Taskی، چه Metricی و چه Blind Spotی پشت عدد است.

حالا خانواده‌های درست را برای پروژه انتخاب کرده‌ایم، اما هنوز Benchmark نداریم. سؤال ما هنوز آن‌قدر مبهم است که می‌توانیم بعد از دیدن نتیجه، تعریف “بهتر” را عوض کنیم.

در قسمت بعد، همین سؤال را جلوی دوربین به یک Specification یک‌صفحه‌ای تبدیل می‌کنیم: Decision، Construct، Unit، Scope، Baseline و Claim boundary. آنجا می‌بینیم چرا یک Benchmark خوب قبل از Dataset شروع می‌شود.

در کامنت بنویسید برای محصول یا ایدهٔ شما کدام خانواده مهم‌تر است—و مهم‌تر از آن، چه Failureی باعث شد آن را انتخاب کنید.»

---

## 6. طراحی تجربهٔ بصری

### صحنهٔ اصلی: Model Lens Explorer

این بخش باید شبیه ابزار واقعی باشد، نه Slide:

- سمت چپ: فهرست Modelهای فرضی با برچسب `ILLUSTRATIVE`.
- مرکز: پروفایل چندبعدی مدل انتخاب‌شده.
- بالا: Lensهای `KNOWLEDGE / CODE / AGENT / TRUST / VALUE`.
- سمت راست: چهار فیلد ثابت `CLAIM / TASK / METRIC / BLIND SPOT`.
- با تغییر Lens، عدد، توضیح و Position مدل تغییر کند.
- یک Toggle با عنوان `SHOW THE CONTRACT` باید Task، Dataset، Protocol و Metric را آشکار کند.

### قواعد تصویر

- متن روی تصویر کوتاه و انگلیسی باشد؛ توضیح کامل با صدای فارسی.
- یک Proof object در هر قاب: عدد، Contrast، Pipeline، Citation یا Failure.
- عددهای ساختگی همیشه `ILLUSTRATIVE DATA` داشته باشند.
- رتبهٔ زندهٔ مدل‌ها در روایت ثابت گفته نشود؛ فقط در Screen recording روز ضبط دیده شود.
- از Radar chart فقط برای Profile استفاده شود، نه اثبات برتری کلی.

### Assetهای ضروری

1. ماتریس دو محورهٔ Benchmark Landscape.
2. چهارده Family chip با رنگ‌بندی چهار قلمرو.
3. HumanEval → SWE-bench task expansion.
4. RAG failure pipeline.
5. Citation support x-ray.
6. Safety utility trade-off.
7. Quality–cost plane.
8. Deep Research Benchmark Stack.

---

## 7. سایت‌هایی که هنگام صحبت باید نمایش داده شوند

| زمان | سایت | چیزی که نشان می‌دهی | جملهٔ همراه | حداکثر زمان |
|---|---|---|---|---:|
| 03:00 | [MMLU paper](https://arxiv.org/abs/2009.03300) | Abstract و عبارت 57 tasks | «این یک تست چندموضوعی است، نه آزمون همهٔ اشکال intelligence.» | 12 ثانیه |
| 03:35 | [GPQA paper](https://arxiv.org/abs/2311.12022) | 448 سؤال و دقت متخصصان در Abstract | «دشواری Benchmark بخشی از طراحی است، نه فضیلت مستقل.» | 12 ثانیه |
| 05:00 | [HumanEval paper](https://arxiv.org/abs/2107.03374) | تعریف functional correctness | «این Task نوشتن تابع از Docstring است.» | 10 ثانیه |
| 05:30 | [SWE-bench](https://www.swebench.com/) | یک Instance و Methodology/Leaderboard | «اینجا واحد کار از Function به Repository و Issue تغییر کرده است.» | 18 ثانیه |
| 06:25 | [MMMU paper](https://arxiv.org/abs/2311.16502) | نمونهٔ سؤال‌های تصویری | «بدون Text-only baseline، ممکن است Vision را بیش‌ازحد ادعا کنیم.» | 12 ثانیه |
| 07:45 | [Ragas paper](https://arxiv.org/abs/2309.15217) | تفکیک ابعاد RAG | «Pipeline را به محل‌های شکست جدا تقسیم می‌کنیم.» | 12 ثانیه |
| 09:10 | [WebArena paper](https://arxiv.org/abs/2307.13854) | محیط و Taskهای تعاملی | «Agent باید کار را تمام کند، نه فقط جواب خوبی بنویسد.» | 15 ثانیه |
| 11:05 | [TruthfulQA](https://arxiv.org/abs/2109.07958) | 817 سؤال و 38 دسته | «Truthfulness یک Construct مشخص است، نه کل Trust.» | 10 ثانیه |
| 12:40 | [HarmBench](https://www.harmbench.org/) یا [JailbreakBench](https://jailbreakbench.github.io/) | دسته‌ها/Threat model | «Attack success را کنار over-refusal ببینید.» | 15 ثانیه |
| 14:15 | [Arena — How it works](https://arena.ai/how-it-works) | battle، vote و ranking method | «Preference، انتخاب انسانی است؛ نه Fact check.» | 18 ثانیه |
| 15:20 | [MLCommons Benchmarks](https://mlcommons.org/benchmarks/) | Benchmark principles و performance/quality | «سرعت فقط با workload و شرایط ثابت معنا دارد.» | 12 ثانیه |
| 19:05 | [NIST AI 800-2 — Initial Public Draft](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf) | صفحهٔ Abstract و سه مرحله | «اول measurement target، بعد run، بعد analysis و report.» | 15 ثانیه |

**قاعدهٔ تدوین سایت‌ها:** صفحه را از قبل روی نقطهٔ موردنظر باز کن. Scroll و جست‌وجوی زنده انجام نده. Cursor فقط یک عبارت را Highlight کند. رتبه‌های زنده را با تاریخ ضبط در گوشهٔ تصویر ثبت کن.

---

## 8. چک‌لیست علمی قبل از ضبط

- MMLU را آزمون «هوش عمومی» معرفی نکن؛ آزمون multitask accuracy روی ۵۷ Task است.
- GPQA را معیار مستقیم reasoning process ننام؛ پاسخ‌های دشوار تخصصی را می‌سنجد.
- HumanEval را معادل software engineering نگو.
- SWE-bench Score را فقط به مدل پایه نسبت نده؛ Agent scaffold و Harness مؤثرند.
- Arena را معیار حقیقت یا Safety معرفی نکن؛ ترجیح انسانی را اندازه می‌گیرد.
- Ragas و LLM-as-a-Judge را Ground truth بی‌خطا معرفی نکن.
- Efficiency را بدون workload، Hardware، Region، batch و طول Token مقایسه نکن.
- Product outcome را از Context محصول جدا نکن.
- ماتریس دو محوره را «مدل ذهنی M2Lab» بنام، نه Taxonomy اجماعی رسمی.
- NIST AI 800-2 را `Initial Public Draft — January 2026` معرفی کن، نه استاندارد نهایی.

---

## 9. بستهٔ ضبط

### A-roll ضروری

- Cold open کامل در یک Take پیوسته.
- جملهٔ «مدل یک رتبهٔ واحد ندارد؛ یک پروفایل عملکرد دارد» در دو ریتم آرام و قاطع.
- Bridgeهای چهار قلمرو جداگانه برای امکان Cut.
- Diagnosis game با مکث واقعی سه‌ثانیه‌ای.
- Verdict نهایی بدون نگاه به نمایشگر.

### B-roll ضروری

- انتخاب Lensهای مختلف روی Atlas.
- بازکردن Task/Metric/Blind Spot هر خانواده.
- Zoom روی Abstract منابع، نه صفحهٔ کامل و ناخوانا.
- RAG pipeline و Citation x-ray.
- ساخت Stack پنج‌لایه در پایان.

### حذف‌پذیر در تدوین

- مثال دوم Math.
- توضیح فرعی Fairness metric.
- یکی از دو سایت Safety.

### حذف‌ناپذیر

- Cold open.
- چهار سؤال ثابت.
- تفاوت HumanEval و SWE-bench.
- تفاوت Preference و Correctness.
- Diagnosis game.
- Benchmark Stack پروژه.

---

## 10. CTA نهایی

> نقشهٔ Benchmark Landscape را بردارید و برای محصول خود فقط سه خانه را پر کنید: تصمیم، Failure پرهزینه و خانوادهٔ Evidence. اگر هنوز از نام یک Benchmark شروع می‌کنید، احتمالاً سؤال محصول را به سؤال Leaderboard واگذار کرده‌اید.

---

## 11. منابع اصلی این قسمت

1. Hendrycks et al., [Measuring Massive Multitask Language Understanding](https://arxiv.org/abs/2009.03300).
2. Rein et al., [GPQA: A Graduate-Level Google-Proof Q&A Benchmark](https://arxiv.org/abs/2311.12022).
3. Chen et al., [Evaluating Large Language Models Trained on Code](https://arxiv.org/abs/2107.03374).
4. Jimenez et al., [SWE-bench](https://arxiv.org/abs/2310.06770) و [سایت رسمی](https://www.swebench.com/).
5. Yue et al., [MMMU](https://arxiv.org/abs/2311.16502).
6. Es et al., [Ragas](https://arxiv.org/abs/2309.15217).
7. Zhou et al., [WebArena](https://arxiv.org/abs/2307.13854).
8. Lin et al., [TruthfulQA](https://arxiv.org/abs/2109.07958).
9. Mazeika et al., [HarmBench](https://arxiv.org/abs/2402.04249).
10. Chao et al., [JailbreakBench](https://arxiv.org/abs/2404.01318).
11. Chiang et al., [Chatbot Arena](https://arxiv.org/abs/2403.04132) و [روش فعلی Arena](https://arena.ai/how-it-works).
12. [MLCommons Benchmark Work](https://mlcommons.org/benchmarks/).
13. NIST, [Practices for Automated Benchmark Evaluations of Language Models — AI 800-2 Initial Public Draft](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf), January 2026.

