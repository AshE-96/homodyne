# M2Lab Benchmarking Foundations — Episode 01

## Benchmark Is Not Just a Score

**نسخه:** 1.0  
**تاریخ کنترل منابع:** ۹ اوت ۲۰۲۶  
**مدت هدف:** ۱۸:۲۰  
**حداقل قابل قبول پس از تدوین:** ۱۶:۳۰  
**زبان گفتار:** فارسی  
**زبان اصطلاحات و گرافیک:** انگلیسی  

---

## 1. نتیجه‌ای که مخاطب باید بگیرد

مخاطب باید پس از دیدن این قسمت بتواند:

1. Benchmark را به‌عنوان یک «سیستم یا قرارداد اندازه‌گیری» توضیح دهد، نه یک Score یا Leaderboard.
2. Benchmark را از Evaluation، Test، Metric، KPI، Baseline، Target و Leaderboard تفکیک کند.
3. هر ادعای «بهترین مدل» را با پنج سؤال Task، Dataset، Protocol، Metric و Interpretation باز کند.
4. بفهمد چرا امتیاز ۸۰ در MMLU، HumanEval و Arena معنای یکسان ندارد.
5. یک سؤال مبهم محصولی را به Benchmark Question اولیه تبدیل کند.

## 2. بسته انتشار

- **عنوان اصلی:** Benchmark Is Not Just a Score
- **عنوان کلیک‌پذیر جایگزین:** Why “The Best AI Model” Is Usually a Meaningless Claim
- **متن Thumbnail:** BEST AT WHAT?
- **جمله محوری:** Score is the output. The benchmark is the measurement system.
- **خروجی مخاطب:** Benchmark Anatomy Card
- **سؤال کامنت:** آخرین باری که براساس رتبه یا Score یک ابزار AI را انتخاب کردید چه زمانی بود، نتیجه چه شد و کدام بخش Methodology را پیدا نکردید؟

## 3. معماری روایت

| زمان | بخش | وظیفه روایی | تصویر اصلی |
|---|---|---|---|
| 00:00–01:15 | دو برنده؛ هر دو درست | ساخت تناقض | Arena در برابر Artificial Analysis |
| 01:15–03:15 | Best یعنی چه؟ | بازنویسی ادعای مبهم | BEST AT WHAT? + پنج سؤال |
| 03:15–06:30 | آناتومی Benchmark | مدل ذهنی مرکزی | فرمول پنج‌جزئی + HELM |
| 06:30–09:45 | مرزبندی اصطلاحات | تئوری لازم | جدول هشت اصطلاح |
| 09:45–13:15 | سه امتیاز ۸۰ | Evidence | MMLU، HumanEval و Arena |
| 13:15–16:20 | پروژه واقعی فصل | Build in public | Deep Research Benchmark v0.1 |
| 16:20–17:35 | محدودیت و خطا | جلوگیری از قطعیت کاذب | NIST TEVV + دو هشدار |
| 17:35–18:20 | جمع‌بندی و پل | CTA و قسمت بعد | کارت پنج سؤال + Landscape |

روایت نباید با تعریف فرهنگ‌لغتی Benchmark شروع شود. ترتیب M2Lab چنین است:

> Contradiction → Decision problem → Mental model → Theory → Evidence → Build → Limitation → Next experiment

---

# 4. متن کامل ضبط و فلو تولید

## 00:00–01:15 — Hook: دو برنده؛ هر دو درست

### هدف

ایجاد یک تناقض فوری و شکستن تصور «یک رتبه جهانی برای همه‌چیز».

### قبل از شروع ضبط

این دو تب را از قبل باز و روی بخش لازم تنظیم کن:

1. [Arena Text Leaderboard](https://lmarena.ai/leaderboard/text)
2. [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index)

رتبه‌ها را در روز ضبط کنترل کن. نام برنده را وارد Voice-over دائمی نکن، چون Leaderboard زنده تغییر می‌کند.

### متن گفتاری

«دو سایت معتبر را باز می‌کنیم. در این یکی یک مدل بالاتر از بقیه ایستاده؛ در دیگری ممکن است مدل متفاوتی رتبه اول باشد. هر دو سایت هم جدول، عدد، نمودار و Methodology دارند. آیا یکی از آن‌ها اشتباه می‌کند؟ نه لزوماً.

ممکن است این سایت ترجیح کاربران را در گفت‌وگوهای واقعی اندازه بگیرد و آن یکی مجموعه‌ای از مسئله‌های علمی، کدنویسی و Agentic Task را با وزن‌های مشخص ترکیب کند. حتی ممکن است یک مدل در کیفیت اول باشد، اما وقتی قیمت یا سرعت را وارد تصمیم می‌کنیم، انتخاب مناسب کاملاً عوض شود.

مشکل از جایی شروع می‌شود که تمام این اندازه‌گیری‌های متفاوت را با یک جمله خلاصه می‌کنیم: این بهترین مدل دنیاست. بهترین در چه چیزی؟ برای چه کسی؟ تحت چه شرایطی؟

در این قسمت می‌خواهم یک سوءتفاهم اساسی را باز کنم: Benchmark یک Score یا جدول رتبه‌بندی نیست. Score فقط خروجی است. Benchmark سیستم اندازه‌گیری‌ای است که به آن خروجی معنا می‌دهد. اگر سیستم اندازه‌گیری را نبینیم، یک عدد دقیق می‌تواند ما را با اعتمادبه‌نفس به تصمیم اشتباه برساند.»

### تدوین

- Cold open؛ معرفی کانال و لوگو بعد از تناقض بیاید.
- در ثانیه ۲۵ تا ۳۵ Split Screen دو سایت نمایش داده شود.
- بعد از جمله «هر دو می‌توانند درست باشند» موسیقی برای نیم ثانیه قطع شود.
- کارت زیر ۲.۵ ثانیه تمام‌صفحه بماند:

> A score is the output. The benchmark is the measurement system.

---

## 01:15–03:15 — مسئله: Best یعنی چه؟

### هدف

تبدیل ادعای بازاریابی «بهترین» به سؤالی که بتواند یک تصمیم واقعی را پشتیبانی کند.

### متن گفتاری

«کلمه Best تقریباً همیشه یک سؤال ناقص است. بهترین برای چه Taskی؟ برای چه کاربری؟ با چه بودجه و زمانی؟ با چه سطحی از ریسک؟ و بر اساس چه شواهدی؟

برای یک پژوهشگر، عملکرد روی سؤال‌های دشوار علمی می‌تواند Signal مهمی باشد. برای یک تیم پشتیبانی، نرخ حل صحیح تیکت واقعی، Latency در ساعت شلوغ، هزینه هر پاسخ و درصد ارجاع به اپراتور انسانی مهم‌تر است. برای یک Founder غیرفنی، شاید کیفیت منابع، قابل‌اقدام‌بودن نتیجه و زمان رسیدن به تصمیم، از هر Score آکادمیکی باارزش‌تر باشد.

پس سؤال بهترین مدل کدام است را این‌طور بازنویسی می‌کنیم: برای این کاربر مشخص، در انجام این کار مشخص، تحت این محدودیت‌ها و با توجه به این شکست پرهزینه، کدام گزینه شواهد بهتری دارد؟

این بازنویسی ساده یک مرز مهم می‌سازد. قبل از آن، ما فقط رتبه‌ها را مصرف می‌کنیم؛ بعد از آن، می‌توانیم بپرسیم آیا Benchmark واقعاً به تصمیم ما مربوط است یا نه.

یک قاعده عملی: اگر نتوانید جمله بهترین برای... را کامل کنید، هنوز آماده انتخاب ابزار نیستید. و اگر Benchmark نتواند توضیح دهد دقیقاً چه ادعایی را پشتیبانی می‌کند، رتبه اول آن نباید به‌تنهایی تصمیم شما را تعیین کند.»

### کارت تصویر

```text
BEST = USER + TASK + CONSTRAINTS + FAILURE COST + EVIDENCE
```

### مثال‌های روی تصویر

| کاربر | تصمیم واقعی | Signal مرتبط | Signal ناکافی |
|---|---|---|---|
| پژوهشگر | انتخاب مدل برای Q&A علمی | صحت علمی، Calibration، Citation | رتبه محبوبیت عمومی |
| تیم پشتیبانی | انتخاب Copilot تیکت | Resolution، latency، escalation، cost | MMLU تنها |
| Founder | انتخاب Deep Research | منابع، extraction، actionability، time | یک Score مرکب بدون Methodology |

---

## 03:15–06:30 — مدل ذهنی: آناتومی Benchmark

### فرمول مرکزی فصل

```text
Benchmark = Task + Dataset + Protocol + Metric + Interpretation
```

این فرمول یک تعریف استاندارد رسمی نیست؛ چارچوب تحلیلی M2Lab برای بازکردن هر Benchmark است. اجزای آن با اصول طراحی Evaluation و شفافیت در HELM، NIST و MLCommons همسو هستند.

### متن گفتاری

«تعریف عملی این فصل چنین است: Benchmark برابر است با Task، به‌علاوه Dataset، به‌علاوه Protocol، به‌علاوه Metric، به‌علاوه Interpretation.

Task یعنی سیستم دقیقاً باید چه کاری انجام دهد. تحقیق بازار انجام بده هنوز مبهم است. سه رقیب مستقیم را پیدا کن، قیمت‌گذاری فعلی آن‌ها را استخراج کن و برای هر ادعا یک منبع پشتیبان بده، یک Task قابل مشاهده‌تر است.

Dataset یعنی این Task روی چه نمونه‌ها و سناریوهایی اجرا می‌شود. اگر فقط سه شرکت مشهور آمریکایی را انتخاب کنیم، نتیجه برای بازار B2B کوچک، زبان فارسی یا صنایعی با داده کم قابل تعمیم نیست. Dataset در واقع تعیین می‌کند کدام بخش از جهان وارد آزمایش ما شده و کدام بخش حذف شده است.

Protocol یعنی اجرا دقیقاً تحت چه شرایطی انجام شده: نسخه مدل، تاریخ، Prompt، ابزارهای مجاز، تعداد تکرار، Temperature، Timeout، منطقه سرویس و حتی اینکه Login یا Subscription چه سطحی داشته است. اگر Protocol عوض شود، ممکن است Score عوض شود؛ پس Protocol حاشیه آزمایش نیست، بخشی از خود Benchmark است.

Metric یعنی موفقیت چگونه به عدد یا قضاوت تبدیل می‌شود: Accuracy، pass@k، Task Success، کیفیت Citation، Cost، Latency یا ترجیح انسانی. Metric با Benchmark یکی نیست؛ Metric فقط تابع اندازه‌گیری داخل آن است.

Interpretation می‌گوید نتیجه چه ادعایی را پشتیبانی می‌کند و چه چیزی را ثابت نمی‌کند. اگر مدلی روی سؤال‌های چندگزینه‌ای علمی خوب عمل کند، نمی‌توانیم بدون شواهد اضافه نتیجه بگیریم بهترین Agent برای اجرای یک فرایند تجاری است.

اگر یکی از این پنج جزء مبهم باشد، ما احتمالاً یک Score داریم، نه یک Benchmark قابل دفاع. HELM نمونه خوبی برای نشان‌دادن این نگاه است: به‌جای چسبیدن به یک Accuracy، سناریوها و چند معیار مانند Robustness، Fairness، Toxicity و Efficiency را کنار هم قرار می‌دهد.»

### جدول مثال Deep Research

| جزء | سؤال | مثال اولیه M2Lab |
|---|---|---|
| Task | چه کاری؟ | پیدا کردن رقیب، استخراج قیمت، پشتیبانی ادعا و خلاصه تصمیم |
| Dataset | روی چه نمونه‌ای؟ | بازارهای B2B/B2C، صنایع و زبان‌های تعریف‌شده |
| Protocol | چگونه؟ | نسخه، تاریخ، Prompt policy، ابزار، timeout و repeats |
| Metric | موفقیت چیست؟ | extraction accuracy، citation support، actionability، cost، time |
| Interpretation | چه ادعایی؟ | بهترین گزینه برای همان User و Scenario؛ نه بهترین ابزار پژوهش جهان |

### سایت لازم

[Stanford HELM](https://crfm.stanford.edu/helm/) را باز کن و فقط این سه چیز را نشان بده:

1. وجود Scenarioهای متعدد؛
2. وجود Metricهای متعدد؛
3. امکان مشاهده Methodology و نتایج جزئی به‌جای یک عدد تنها.

---

## 06:30–09:45 — تئوری: Benchmark با چه چیزهایی فرق دارد؟

### متن گفتاری

«چند واژه مرتب به‌جای هم استفاده می‌شوند. بیایید مرز آن‌ها را روشن کنیم.

Evaluation واژه چتری است: هر فرایند نظام‌مند برای قضاوت درباره کیفیت، رفتار، ریسک یا ارزش یک سیستم. Benchmark یکی از ابزارهای Evaluation است، نه تمام آن.

Test یک بررسی یا اجرای مشخص است. مثلاً آیا خروجی این مسئله درست است؟ آیا مدل لینک جعلی تولید می‌کند؟ یک Benchmark معمولاً مجموعه‌ای استاندارد از Testها را همراه با داده، قواعد اجرا و روش امتیازدهی بسته‌بندی می‌کند تا مقایسه ممکن شود.

Metric روش تبدیل مشاهده به اندازه‌گیری است. Accuracy یک Metric است؛ MMLU یک Benchmark است که از Accuracy در مجموعه‌ای از سؤال‌ها استفاده می‌کند. Cost per successful task نیز Metric است، نه Benchmark.

Baseline نقطه مرجع است: انتخاب تصادفی، روش ساده، نسخه قبلی، نیروی انسانی یا ابزار فعلی. بدون Baseline نمی‌دانیم عدد واقعاً پیشرفت است یا فقط بهتر از هیچ.

Target سطحی است که از قبل برای موفقیت تعیین می‌کنیم؛ مثلاً حداقل ۹۰ درصد Citationها باید واقعاً ادعای مربوط را پشتیبانی کنند. Target نتیجه نیست؛ شرط تصمیم است.

KPI شاخص پایش محصول یا کسب‌وکار در دنیای واقعی و در طول زمان است؛ مثل Retention، Cost per resolved ticket یا نرخ Escalation. KPI ممکن است از یک Evaluation تغذیه شود، اما هدفش Monitoring عملیات واقعی است.

Leaderboard فقط لایه نمایش و مرتب‌سازی نتایج است. ظاهر مرتب، تعداد رقم اعشار و رتبه اول، اعتبار Methodology را تضمین نمی‌کند.

پس این جمله را نگه دارید: Leaderboard ویترین است؛ Benchmark موتور اندازه‌گیری پشت ویترین است. اگر فقط ویترین را ببینیم، نمی‌دانیم کالا چگونه تولید شده، تحت چه شرایطی آزمایش شده و برای نیاز ما مناسب هست یا نه.»

### جدول تئوری

| اصطلاح | وظیفه | مثال | با چه چیزی اشتباه نشود؟ |
|---|---|---|---|
| Evaluation | قضاوت نظام‌مند درباره کیفیت/ریسک/ارزش | ارزیابی کامل Copilot | Benchmark فقط یکی از ابزارهاست |
| Test | بررسی یک رفتار یا شرط | صحت یک Citation | مجموعه استاندارد کامل نیست |
| Metric | تابع اندازه‌گیری | Accuracy، pass@k، latency | Metric به‌تنهایی Benchmark نیست |
| Benchmark | بسته مقایسه استاندارد | MMLU یا HumanEval با Setup | Leaderboard نمایش نتیجه است |
| Baseline | نقطه مرجع | Random، نسخه قبلی، انسان | Target نیست |
| Target | آستانه تصمیم از پیش تعیین‌شده | Citation support ≥ 90% | نتیجه مشاهده‌شده نیست |
| KPI | پایش عملکرد واقعی در زمان | Cost per resolved ticket | آزمون کنترل‌شده نیست |
| Leaderboard | مرتب‌سازی و نمایش نتایج | جدول رتبه‌ها | ظاهر آن Methodology را معتبر نمی‌کند |

### جمله کلیدی تدوین

> Leaderboard ویترین است؛ Benchmark موتور اندازه‌گیری پشت ویترین.

---

## 09:45–13:15 — Evidence: سه Benchmark، سه معنای متفاوت

### متن گفتاری

«سه Benchmark مشهور را کنار هم می‌گذاریم.

MMLU در مقاله اصلی برای اندازه‌گیری عملکرد چندوظیفه‌ای روی ۵۷ موضوع معرفی شد؛ از ریاضی و تاریخ تا حقوق و علوم کامپیوتر. قالب اصلی سؤال چندگزینه‌ای است و Metric محوری Accuracy است. اگر مدلی ۸۰ درصد بگیرد، یعنی تحت همان Setup، تقریباً ۸۰ درصد سؤال‌های آن مجموعه را درست پاسخ داده. این عدد چیزی درباره سرعت API، تجربه کاربری، کار با مرورگر یا هزینه یک Task تجاری نمی‌گوید.

HumanEval برای سنجش Functional Correctness در تولید کد ساخته شد. نسخه اصلی ۱۶۴ مسئله دست‌نویس برنامه‌نویسی دارد. مدل از توضیح و امضای تابع، کد تولید می‌کند؛ سپس کد اجرا می‌شود و Unit Testها تعیین می‌کنند راه‌حل کار می‌کند یا نه. Metricهایی مانند pass@k می‌پرسند آیا حداقل یکی از k نمونه تولیدشده Testها را پاس می‌کند. پس ۸۰ درصد در HumanEval واحدی متفاوت از ۸۰ درصد Accuracy در MMLU دارد.

Arena مسئله دیگری را اندازه می‌گیرد. دو پاسخ از مدل‌های ناشناس به کاربر نشان داده می‌شود و کاربر انتخاب می‌کند کدام را ترجیح می‌دهد. رأی‌های جفتی با یک مدل رتبه‌بندی مانند Bradley–Terry به Score و رتبه تبدیل می‌شوند. این برای سنجش ترجیح انسان در گفت‌وگوی باز مفید است، اما نتیجه به ترکیب کاربران، Promptها، Pairing مدل‌ها و روش تجمیع رأی‌ها وابسته است. Preference لزوماً همان Factual Accuracy نیست.

حالا سه عدد ۸۰ داریم: ۸۰ درصد پاسخ صحیح، ۸۰ درصد Taskهایی که حداقل یک کد تست‌ها را پاس کرده، و ۸۰ درصد ترجیح در یک مقایسه انسانی فرضی. شکل عدد یکی است؛ Construct، Task، Data و Interpretation متفاوت است.

این مثل آن است که بگوییم سرعت خودرو ۸۰، رضایت مشتری ۸۰ و نمره آزمون ۸۰ است. هیچ‌کس این سه را مستقیماً مقایسه نمی‌کند؛ اما در AI مرتب چنین خطایی انجام می‌دهیم.»

### کارت مقایسه

| Benchmark | Claim | Task | Metric | 80 چه معنایی دارد؟ | چه چیزی را ثابت نمی‌کند؟ |
|---|---|---|---|---|---|
| MMLU | دانش و حل مسئله چندموضوعی در قالب مشخص | سؤال چهارگزینه‌ای در ۵۷ موضوع | Accuracy | ۸۰٪ پاسخ صحیح در همان Setup | Agent، latency، UX یا cost |
| HumanEval | Functional correctness برای تابع Python | تولید کد از docstring و اجرای Test | pass@k | حل مسئله با حداقل یک نمونه موفق در k تلاش | مهندسی Repository و امنیت |
| Arena | ترجیح نسبی کاربر در گفت‌وگوی باز | رأی ناشناس بین دو پاسخ | Bradley–Terry-based score | ترجیح نسبی در جمعیت و Promptهای مشاهده‌شده | Factual accuracy یا بهترین برای همه |

### منابعی که روی تصویر نشان داده می‌شوند

- [MMLU paper](https://arxiv.org/abs/2009.03300)
- [MMLU official repository](https://github.com/hendrycks/test)
- [HumanEval paper](https://arxiv.org/abs/2107.03374)
- [HumanEval official repository](https://github.com/openai/human-eval)
- [How Arena Works](https://lmarena.ai/how-it-works)
- [Arena FAQ](https://lmarena.ai/faq)

### تدوین عدد ۸۰

عدد 80 سه بار در مرکز ثابت بماند و فقط Unit عوض شود:

```text
80% CORRECT ANSWERS
80% TASKS SOLVED WITH ≥1 PASSING SAMPLE
80% PAIRWISE PREFERENCE — HYPOTHETICAL
```

سپس عبارت `SAME SCORE` خط بخورد و `DIFFERENT CLAIM` ظاهر شود.

---

## 13:15–16:20 — Build: پروژه واقعی فصل

### سؤال خام

> بهترین ابزار Deep Research برای Founderها چیست؟

### Benchmark Question v0.1

> برای یک Founder غیرفنی که می‌خواهد در کمتر از ۳۰ دقیقه و با هزینه حداکثر ۱۰ دلار یک تحقیق اولیه بازار بسازد، کدام ابزار در مجموعه‌ای از سناریوهای واقعی می‌تواند رقبا و قیمت‌گذاری را دقیق‌تر استخراج کند، ادعاها را با منابع معتبر پشتیبانی کند و خروجی قابل‌اقدام‌تری بدهد؟

### متن گفتاری

«حالا از مثال‌های آکادمیک به پروژه واقعی M2Lab برگردیم. سؤال خام ما این است: بهترین ابزار Deep Research برای Founderها چیست؟ این سؤال برای یک Thumbnail جذاب است، اما برای Benchmark ضعیف است.

نسخه قابل‌سنجش‌تر را این‌طور می‌نویسیم: برای یک Founder غیرفنی که می‌خواهد در کمتر از ۳۰ دقیقه و با هزینه حداکثر ۱۰ دلار یک تحقیق اولیه بازار بسازد، کدام ابزار در مجموعه‌ای از سناریوهای واقعی می‌تواند رقبا و قیمت‌گذاری را دقیق‌تر استخراج کند، ادعاها را با منابع معتبر پشتیبانی کند و خروجی قابل‌اقدام‌تری بدهد؟

همین یک جمله چند تصمیم را روشن می‌کند. User ما Founder غیرفنی است. Task تحقیق اولیه بازار است. زمان و هزینه Constraint هستند. ابعاد کیفیت شامل دقت استخراج، کیفیت Citation و Actionability است. همچنین می‌دانیم ادعای نهایی درباره همه کارهای پژوهشی نخواهد بود؛ فقط درباره سناریوهای تعریف‌شده و این تیپ کاربر صحبت می‌کنیم.

اما هنوز Benchmark کامل نیست. Dataset نداریم. تعداد و توزیع سناریوها مشخص نشده. Protocol استفاده از ابزارها را ننوشته‌ایم. نمی‌دانیم Prompt یکسان می‌دهیم یا بهترین Prompt مختص هر ابزار. Ground Truth نداریم. روش ارزیابی Actionability و میزان توافق داورها معلوم نیست. و نمی‌دانیم اگر ابزار A دو امتیاز بالاتر شد، این اختلاف واقعاً معنادار است یا محصول Sample ما.

این شکاف‌ها ضعف ویدئو نیستند؛ نقشه ادامه فصل‌اند. در قسمت‌های بعد، Specification، Dataset، Ground Truth، Metrics، Protocol و تحلیل عدم قطعیت را می‌سازیم. در پایان فصل قرار نیست فقط Benchmark را توضیح داده باشیم؛ باید داده خام، Methodology و یک گزارش عمومی قابل بررسی داشته باشیم.»

### عناصر روشن‌شده در v0.1

- User: Founder غیرفنی
- Job: تحقیق اولیه بازار
- Constraint: کمتر از ۳۰ دقیقه
- Constraint: حداکثر ۱۰ دلار
- Quality: استخراج رقیب و قیمت
- Trust: پشتیبانی Citation
- Outcome: Actionability

### شکاف‌های باز

- Dataset و Sampling
- Ground Truth
- Prompt policy: Equal conditions یا best attainable output
- تعداد repeats
- Metric definition و وزن‌ها
- Human evaluator rubric
- Inter-rater agreement
- Statistical uncertainty
- Claim boundary

---

## 16:20–17:35 — Risk: محدودیت و خطا

### متن گفتاری

«دو هشدار مهم.

اول اینکه هر مقایسه‌ای لازم نیست Benchmark عمومی و Leaderboard شود. گاهی یک Product Test کوچک برای انتخاب داخلی کافی است. وقتی نتیجه را با عنوان Benchmark منتشر می‌کنیم، مسئولیت بیشتری می‌پذیریم: روش باید مشخص، اجرا تا حد ممکن تکرارپذیر، داده و محدودیت شفاف و ادعا متناسب با شواهد باشد.

دوم اینکه Benchmark هرگز تمام واقعیت نیست. هر Benchmark یک مدل فشرده از جهان است. بعضی کاربران، زبان‌ها، Failureها و شرایط را وارد می‌کند و بعضی را حذف می‌کند. اگر ویژگی مهمی حذف شده باشد، Score دقیق هم می‌تواند تصمیم غلط بسازد.

بنابراین هدف ساخت عدد بدون نقص نیست. هدف ساخت اندازه‌گیری‌ای است که Construct و محدودیتش را می‌فهمیم و برای یک تصمیم مشخص، به‌اندازه کافی معتبر است. به همین دلیل NIST در TEVV فقط از یک آزمون نهایی صحبت نمی‌کند؛ Testing، Evaluation، Validation و Verification باید با ریسک و چرخه عمر سیستم مرتبط باشند. Benchmark یک مدرک است، نه حکم نهایی.»

### دو کارت هشدار

```text
NOT EVERY TEST NEEDS A PUBLIC LEADERBOARD
EVERY BENCHMARK IS A MODEL OF THE WORLD
```

### سایت Context

[NIST AI TEVV](https://www.nist.gov/ai-test-evaluation-validation-and-verification-tevv)

این صفحه را فقط ۵ تا ۸ ثانیه نشان بده؛ قسمت اول جای توضیح کامل استاندارد TEVV نیست.

---

## 17:35–18:20 — جمع‌بندی، CTA و پل

### متن گفتاری

«از این قسمت فقط یک عادت را با خودتان ببرید. هر بار عدد یا رتبه‌ای دیدید، پنج سؤال بپرسید: Task چیست؟ Dataset چیست؟ Protocol چگونه بوده؟ Metric چه چیزی را محاسبه کرده؟ و Interpretation مجاز این نتیجه تا کجاست؟

اگر یکی از این خانه‌ها خالی بود، هنوز برای انتخاب شواهد کافی ندارید.

کارت تشخیص Benchmark را در لینک صفحه گذاشته‌ام. یک Leaderboard که اخیراً دیده‌اید انتخاب کنید و این پنج خانه را پر کنید. در کامنت هم بنویسید آخرین بار براساس رتبه یک ابزار AI تصمیم گرفتید، نتیجه چه شد و کدام اطلاعات را پیدا نکردید.

در قسمت بعد نقشه کل قلمرو را می‌سازیم: Benchmarkهای دانش، استدلال، کدنویسی، Agent، Multimodal، RAG، Safety، Bias، Efficiency و Business. قرار نیست اسم‌ها را حفظ کنیم؛ می‌خواهیم بفهمیم هر خانواده چه چیزی را می‌سنجد و چه چیزی را نمی‌سنجد.»

### End card

```text
TASK?
DATASET?
PROTOCOL?
METRIC?
INTERPRETATION?
```

---

# 5. Browser Run of Show

## تب‌هایی که قبل ضبط باید باز باشند

| ترتیب تب | زمان نمایش | سایت | دقیقاً چه چیزی نشان داده شود؟ | نقش |
|---:|---:|---|---|---|
| 1 | 00:08 | [Arena Text Leaderboard](https://lmarena.ai/leaderboard/text) | Overall و یک Category؛ تفاوت رتبه‌ها | Hook |
| 2 | 00:28 | [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index) | Score مرکب و چند محور قیمت/سرعت | Hook contrast |
| 3 | 04:55 | [Stanford HELM](https://crfm.stanford.edu/helm/) | Scenario و Metricهای متعدد | Mental model proof |
| 4 | 10:02 | [MMLU repository](https://github.com/hendrycks/test) | 57 task و ساختار ارزیابی | Primary proof |
| 5 | 11:08 | [HumanEval repository](https://github.com/openai/human-eval) | اجرای Test و pass@k | Primary proof |
| 6 | 12:10 | [How Arena Works](https://lmarena.ai/how-it-works) | Compare، Vote، Reveal | Method proof |
| 7 | 16:58 | [NIST AI TEVV](https://www.nist.gov/ai-test-evaluation-validation-and-verification-tevv) | جای Benchmark در چرخه Evaluation | Context |

## لینک‌های Description؛ لازم نیست حتماً روی تصویر بیایند

- [Artificial Analysis Methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
- [Arena FAQ](https://lmarena.ai/faq)
- [HELM paper](https://arxiv.org/abs/2211.09110)
- [MMLU paper](https://arxiv.org/abs/2009.03300)
- [HumanEval paper](https://arxiv.org/abs/2107.03374)
- [Arena paper](https://arxiv.org/abs/2403.04132)
- [MLCommons Benchmarks](https://mlcommons.org/benchmarks/)
- [METR Time Horizons](https://metr.org/time-horizons/)

## قواعد Screen recording

1. Zoom مرورگر روی ۱۱۰ تا ۱۲۵ درصد تنظیم شود.
2. Tab title و URL برای اعتبار منبع قابل دیدن باشد، اما اطلاعات حساب نمایش داده نشود.
3. Notification، Bookmarkهای شخصی و Extensionهای غیرضروری پنهان شوند.
4. Scroll هر سایت قبل ضبط تمرین و نقطه شروع ثابت شود.
5. برای ادعاهای مقاله، پایین تصویر `Source — Author/Org — Year` بین ۳ تا ۵ ثانیه بماند.
6. نام Model برنده در تدوین ثابت نوشته نشود؛ در صورت نیاز از برچسب `LIVE RANKING — AUG 2026` استفاده شود.

---

# 6. Shot List نهایی

| Shot | نوع | محتوا | مدت تقریبی |
|---:|---|---|---:|
| 01 | A-roll close | جمله اول بدون معرفی | 8s |
| 02 | Screen | Arena Overall | 10s |
| 03 | Screen | Artificial Analysis Index | 12s |
| 04 | Split screen | دو «رتبه اول» متفاوت | 8s |
| 05 | Card | Score vs Measurement System | 3s |
| 06 | A-roll medium | سؤال‌های Best | 35s |
| 07 | Motion card | USER + TASK + CONSTRAINTS + FAILURE + EVIDENCE | 20s |
| 08 | Motion graphic | فرمول پنج‌جزئی | 50s مجموع |
| 09 | Screen | HELM scenarios/metrics | 15s |
| 10 | Table crop | هشت اصطلاح، ردیف‌به‌ردیف | 90s مجموع |
| 11 | Card | Leaderboard ویترین است | 5s |
| 12 | Screen/proof | MMLU paper/repo | 18s |
| 13 | Screen/proof | HumanEval repo | 20s |
| 14 | Screen/proof | Arena how it works | 18s |
| 15 | Motion compare | سه عدد 80 و سه Unit | 35s |
| 16 | Screen | Benchmark Question v0.1 | 60s مجموع |
| 17 | Graphic | پنج شکاف باز | 20s |
| 18 | A-roll close | دو محدودیت | 35s |
| 19 | Screen | NIST TEVV | 8s |
| 20 | End card | پنج سؤال + CTA | 8s |

---

# 7. طراحی بصری و تدوین

## هویت

- Graphite: `#14171A`
- Warm off-white: `#F4F1EA`
- Signal amber: `#E8A33D`
- فونت انگلیسی: Inter / Geist / grotesk مشابه
- Accent فقط برای هشدار، عدد یا جزء فعال استفاده شود.

## ریتم

- هر ۴۵ تا ۷۵ ثانیه یک Visual reset کافی است.
- Reset الزاماً Jump cut نیست؛ تغییر قاب، Card، Screen recording یا Highlight کافی است.
- در بخش Theory سرعت بیش از حد بالا نرود؛ هدف تفکیک مفهوم است.
- در بخش Limitations ریتم عمداً ۱۰ تا ۱۵ درصد آرام‌تر شود.
- جدول کامل روی موبایل نمایش داده نشود؛ فقط ردیف مورد بحث Zoom شود.

## موسیقی و صدا

- Hook با Pulse مینیمال شروع شود.
- بعد از «هر دو می‌توانند درست باشند» نیم ثانیه سکوت.
- بخش Theory موسیقی بسیار کم یا بدون موسیقی.
- بخش Build ضرب آرام‌تر ولی رو به جلو.
- Limitations بدون موسیقی یا با Drone بسیار کم.

---

# 8. Benchmark Anatomy Card — خروجی قابل دانلود مخاطب

## Template

```markdown
# Benchmark Anatomy Review

Benchmark / Leaderboard:
Review date:
Decision I want to make:

## 1. Task
What exactly does the system do?

## 2. Dataset
What examples, users, languages and conditions are represented?

## 3. Protocol
Model/version/date/prompt/tools/repeats/settings/timeout:

## 4. Metric
How is success calculated? What is the unit?

## 5. Interpretation
What claim does the result support?
What does it NOT prove?

## Decision relevance
- Relevant
- Partially relevant
- Not enough evidence

Missing information:
```

---

# 9. چک‌لیست علمی پیش از ضبط

- [ ] رتبه‌ها و نام مدل برنده در روز ضبط دوباره کنترل شده‌اند.
- [ ] روایت به نام برنده زنده وابسته نیست.
- [ ] MMLU «هوش عمومی» نامیده نمی‌شود؛ دامنه و قالب آن گفته می‌شود.
- [ ] HumanEval معادل کل برنامه‌نویسی معرفی نمی‌شود.
- [ ] Arena به‌عنوان Accuracy-based توضیح داده نمی‌شود.
- [ ] Benchmark، Evaluation، Test و Metric مترادف استفاده نمی‌شوند.
- [ ] تفاوت Baseline و Target روشن است.
- [ ] محدودیت Benchmark در A-roll گفته می‌شود.
- [ ] مثال ۱۰ دلار و ۳۰ دقیقه Constraint اختصاصی M2Lab معرفی می‌شود.
- [ ] نام و لینک منابع رسمی در Description آمده است.
- [ ] هر عدد روی تصویر Unit دارد.
- [ ] در مثال ۸۰، Arena به‌صورت «نرخ ترجیح فرضی» نوشته می‌شود تا با Arena Score زنده اشتباه نشود.

# 10. چک‌لیست روز ضبط

- [ ] هفت Tab اصلی باز و مرتب هستند.
- [ ] Scroll position هر Tab آماده است.
- [ ] Notificationها خاموش‌اند.
- [ ] مرورگر و Screen recording روی رزولوشن نهایی تنظیم شده‌اند.
- [ ] A-roll Hook دو بار با انرژی متفاوت ضبط می‌شود.
- [ ] جمله Core Idea یک Take جداگانه دارد.
- [ ] فرمول پنج‌جزئی بدون تپق و با Pause میان Blockها ضبط می‌شود.
- [ ] جمله Leaderboard/Benchmark یک Take جداگانه دارد.
- [ ] بخش Limitations بدون عجله ضبط می‌شود.
- [ ] CTA فقط یک‌بار و کوتاه است.

# 11. معیار پذیرش اپیزود

| معیار | حد پذیرش |
|---|---|
| مدت نهایی | حداقل ۱۶:۳۰؛ هدف ۱۸:۲۰ |
| Hook | تناقض در ۱۵ ثانیه اول روشن شود |
| Core idea | تا ۷۵ ثانیه اول بیان شود |
| Theory | هشت اصطلاح بدون تناقض تعریف شوند |
| Evidence | حداقل سه منبع Primary روی تصویر |
| Build | Benchmark Question v0.1 واقعاً ساخته شود |
| Limitation | حداقل دو محدودیت در خود ویدئو |
| CTA | یک تمرین پنج‌خانه‌ای قابل انجام |
| Bridge | خانواده‌های قسمت دوم Preview شوند |

# 12. Description آماده

Benchmark فقط یک Score یا Leaderboard نیست. در قسمت اول M2Lab Benchmarking Foundations، مدل پنج‌جزئی `Task + Dataset + Protocol + Metric + Interpretation` را می‌سازیم و با MMLU، HumanEval و Arena نشان می‌دهیم چرا عددهای ظاهراً مشابه معنای یکسانی ندارند.

در طول فصل، یک Benchmark واقعی برای ابزارهای AI Deep Research در تحقیق بازار استارتاپ می‌سازیم: از Specification و Dataset تا اجرای آزمایش، تحلیل خطا و انتشار نتایج.

**تمرین این قسمت:** یک Leaderboard واقعی انتخاب کنید و پنج بخش Task، Dataset، Protocol، Metric و Interpretation آن را پیدا کنید. اگر بخشی پیدا نشد، در کامنت بنویسید کدام اطلاعات غایب بود.

## منابع اصلی

1. [HELM — Holistic Evaluation of Language Models](https://arxiv.org/abs/2211.09110)
2. [Stanford HELM](https://crfm.stanford.edu/helm/)
3. [MMLU paper](https://arxiv.org/abs/2009.03300)
4. [MMLU official repository](https://github.com/hendrycks/test)
5. [HumanEval / Codex evaluation paper](https://arxiv.org/abs/2107.03374)
6. [OpenAI HumanEval repository](https://github.com/openai/human-eval)
7. [Chatbot Arena paper](https://arxiv.org/abs/2403.04132)
8. [Arena — How it works](https://lmarena.ai/how-it-works)
9. [Artificial Analysis Intelligence Methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
10. [NIST AI TEVV](https://www.nist.gov/ai-test-evaluation-validation-and-verification-tevv)
11. [MLCommons Benchmarks](https://mlcommons.org/benchmarks/)

---

## یادداشت نهایی برای مجری

این قسمت قرار نیست ثابت کند Leaderboardها بی‌فایده‌اند. ادعای درست‌تر این است:

> Leaderboard زمانی مفید است که Task، Dataset، Protocol، Metric و Interpretation آن با تصمیم ما هم‌راستا باشد.

هدف روایت، بدبین‌کردن مخاطب به اعداد نیست؛ هدف ساختن عادت بررسی Methodology پیش از تصمیم است.
