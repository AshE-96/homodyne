# M2Lab Benchmarking Foundations — Episode 04

## Dataset, Sampling and Ground Truth

**نسخه:** 1.1 — آمادهٔ ضبط  
**زبان روایت:** فارسی  
**زبان عناصر روی تصویر:** انگلیسی  
**زمان هدف:** 19:00 تا 20:30  
**خروجی این قسمت:** `Dataset Schema + Sampling Grid + Annotation Guide v0.1`  
**پروژهٔ فصل:** ساخت Dataset تشخیصی ۴۸ Case برای Benchmark ابزارهای Deep Research

---

## 0. واژه‌های این قسمت

مرجع سریع. روی اسلاید همیشه واژهٔ انگلیسی می‌آید؛ این جدول برای گوش مخاطب است.

| واژه | به فارسی | یک‌خطی |
|---|---|---|
| `Dataset` | مجموعهٔ موارد آزمون | همان چیزی که وارد تست می‌شود — نه انبار سؤال |
| `Population` | جامعهٔ هدف | جهانی که می‌خواهیم دربارهٔ آن نتیجه بگیریم |
| `Sampling frame` | چارچوب نمونه‌گیری | آنچه عملاً به آن دسترسی داریم |
| `Claim population` | جهان مجازِ ادعا | جایی که حق داریم نتیجه را تعمیم دهیم |
| `Slice` | برش | یک زیرگروه از Dataset؛ مثلاً «همهٔ Caseهای B2B» |
| `Edge case` | مورد مرزی | نادر است، اما شکستش گران تمام می‌شود |
| `Contamination` | آلودگی داده | Benchmark احتمالاً قبلاً در Training دیده شده |
| `Leakage` | نشت | پاسخ یا برچسب وارد جایی شده که نباید |
| `Reference standard` | معیار مرجع | جای «پاسخ درست» وقتی خروجی باز است |
| `Annotation` | برچسب‌گذاری | داوری انسانی روی خروجی |
| `Agreement` | توافق | میزان هم‌نظری دو برچسب‌گذار |
| `Holdout` | کنارگذاشته | Caseهایی که تا آخر باز نمی‌شوند |

---

## 1. قول این قسمت به مخاطب

Dataset انبار سؤال نیست. یک ادعای طراحی‌شده دربارهٔ جهان هدف است.

در پایان این قسمت، مخاطب می‌تواند:

- Population و واحد ارزیابی را تعریف کند؛
- یک Sampling grid بسازد؛
- Easy، Hard و Edge case را با دلیل از هم جدا کند؛
- Real، Synthetic و Dynamic case را آگاهانه ترکیب کند؛
- Reference standard و Annotation guide بنویسد؛
- اختلاف برچسب‌گذارها را به‌عنوان Signal بخواند، نه نویز؛
- ریسک Contamination، Freshness و Leakage را مستند کند.

جملهٔ محوری:

> **Your dataset decides which world enters the test.**

Hook عددی قسمت:

> روی ۳۰ Case، Tool A برنده است. ده Case کم‌داده اضافه می‌کنیم. Prompt و Metric دست نمی‌خورد. Tool B اول می‌شود.

---

## 2. مسئلهٔ روایی

### THE CLAIM

«هرچه Dataset بزرگ‌تر باشد، Benchmark معتبرتر است.»

### THE EVIDENCE

N بیشتر عدم‌قطعیت نمونه‌گیری را کم می‌کند. اما Dataset نامرتبط، نامتوازن یا بدبرچسب‌خورده با بزرگ‌شدن درست نمی‌شود. Coverage، difficulty، provenance و کیفیت برچسب هیچ‌کدام جایگزین N نیستند.

### THE STRESS TEST

Ranking را با تغییر فقط ده Case برمی‌گردانیم. بعد نشان می‌دهیم Dataset اول بیشتر بازارهای مشهور و داده‌غنی را می‌دید.

### THE VERDICT

Dataset خوب سه سؤال را جواب می‌دهد. نمایندهٔ کدام Population است؟ کدام Failure را آشکار می‌کند؟ Reference standard چطور ساخته شد؟

### THE BUILD

Dataset نسخهٔ `v0.1`: ۴۸ Case، Snapshot، Sampling grid و Annotation guide. شش Pilot، ۳۶ Main test، شش Holdout.

---

## 3. تئوری علمی، بدون تزئین اضافی

### 3.1 چهار لایه‌ای که معمولاً یکی فرض می‌شوند

- `Target population` — جهانی که می‌خواهیم درباره‌اش نتیجه بگیریم.
- `Sampling frame` — مواردی که عملاً امکان انتخابشان را داریم.
- `Sample / Dataset` — مواردی که واقعاً وارد Evaluation شدند.
- `Claim population` — جهانی که با این روش، حق داریم درباره‌اش حرف بزنیم.

اگر نمونه‌گیری احتمالی نداریم، نتیجه را طوری گزارش نکنیم که انگار Dataset نمونهٔ تصادفی کل جهان است. ۴۸ Case در M2Lab یک Pilot هدفمند و تشخیصی است، نه برآورد نهایی از تمام Use caseهای تحقیق بازار.

### 3.2 Distribution یعنی وزن

Average نهایی، میانگین روی Distribution همان Dataset است. اگر سهم Caseهای Easy یا بازار آمریکا زیاد باشد، Ranking برای همان ترکیب وزن می‌گیرد.

`Score = Σ performance(slice) × weight(slice)`

وزن Sliceها معمولاً به‌شکل عدد نوشته نمی‌شود؛ داخل تعداد Caseها پنهان است. تغییر Dataset یعنی تغییر وزن جهان.

### 3.3 Difficulty و Edge case

- `Easy` — منابع مستقیم، Brief روشن، Factهای پایدار.
- `Medium` — چند منبع لازم است، یا اصطلاح مبهم است.
- `Hard` — داده کم، منابع متعارض، مرز بازار مبهم، اطلاعات تازه.
- `Edge / Challenge` — Failure پرهزینه، یا شرایطی که انتظار داریم سیستم بشکند.

Hard باید دلیل داشته باشد. «مدل‌های امروز اینجا امتیاز کم می‌گیرند» دلیل نیست.

### 3.4 سه منبع Case، نه سه رتبه

- `Real` — نزدیک به تقاضای واقعی. ریسک: Privacy، تکرار، پوشش نامتوازن.
- `Controlled synthetic` — یک متغیر مشخص را تغییر می‌دهد. ریسک: Generator bias.
- `Dynamic / fresh` — از دادهٔ تازه یا Snapshot زمانی. ریسک کمترِ Contamination، هزینهٔ بیشترِ نگهداری.

Synthetic جای Real را نمی‌گیرد. Real هم بدون کنترل نمی‌گوید کدام عامل باعث Failure شد.

### 3.5 Contamination، Leakage و Evaluation awareness

- `Contamination` — محتوای Benchmark یا الگوی آن احتمالاً در Training دیده شده.
- `Leakage` — پاسخ یا برچسبی که نباید در دسترس باشد، وارد Run شده.
- `Evaluation awareness` — سیستم می‌فهمد در حال تست است و رفتار عوض می‌کند.

نبود شواهد Contamination، اثبات پاک‌بودن نیست. Risk و اقدام‌های کاهش آن باید گزارش شوند.

### 3.6 Ground truth برای خروجی باز

در خروجی باز، یک پاسخ قطعی واحد نداریم. به‌جای Ground truth از `Reference standard` استفاده می‌کنیم و چهار لایه را جدا نگه می‌داریم:

1. `Verifiable facts` — Fact + Source + Snapshot date.
2. `Claim support` — رابطهٔ Claim با Source: Supported، Partial، Unsupported، Contradicted.
3. `Rubric dimensions` — Actionability و افشای عدم‌قطعیت، با Anchor رفتاری.
4. `Pairwise judgment` — انتخاب کور میان دو Report برای یک تصمیم مشخص.

### 3.7 کیفیت Annotation

«دو Annotator» به‌تنهایی کیفیت نمی‌سازد. لازم داریم:

- دستورالعمل و مثال مرزی؛
- Blindness نسبت به نام Tool؛
- Training round و Pilot؛
- Raw agreement به‌علاوهٔ یک معیار Chance-corrected مناسب؛
- تحلیل اختلاف؛
- Adjudication با ثبت دلیل؛
- نسخه‌گذاری Annotation guide.

Agreement پایین می‌تواند نشانهٔ Annotator ضعیف باشد. می‌تواند هم نشان دهد Label یا Task مبهم است. اختلاف را پاک نکن؛ اول بفهمش.

---

## 4. فلو زمانی نهایی

| زمان | Beat | هدف | Proof object |
|---|---|---|---|
| 00:00–01:20 | Rank flip | شکستن اعتماد به N و Average | ۳۰+۱۰ Case و Winner جدید |
| 01:20–03:20 | Population → sample → claim | تعریف جهان استنتاج | funnel سه‌لایه |
| 03:20–05:40 | Distribution is a weight | آشکارکردن وزن‌های پنهان | slice mixer |
| 05:40–08:10 | Difficulty and edge cases | ساخت failure coverage | difficulty ladder |
| 08:10–10:20 | Real, synthetic, dynamic | انتخاب منبع Case | case factory |
| 10:20–12:20 | Freshness and contamination | مدیریت آشنایی و زمان | snapshot timeline |
| 12:20–15:30 | Reference standard | ساخت پاسخ قابل Audit | fact → claim → rubric pyramid |
| 15:30–17:25 | Annotation and agreement | کنترل کیفیت Label | blind annotator split |
| 17:25–19:10 | Build 48 cases | ساخت Dataset v0.1 | sampling grid |
| 19:10–20:00 | Verdict and bridge | ورود به Metrics | dataset → scorecard |

---

## 5. متن کامل آمادهٔ ضبط

### 00:00–01:20 — ده Case که برنده را عوض کردند

**ON SCREEN:** `THE CLAIM`  
**HEADLINE:** `SAME TOOLS. SAME METRIC. NEW WINNER.`

**تصویر:** داده با برچسب `ILLUSTRATIVE EXAMPLE`.

- ۳۰ Case اولیه: Tool A = 81، Tool B = 77.
- ۱۰ Case جدید Low-data/Hard: Tool A = 40، Tool B = 72.
- ۴۰ Case: Tool A = 70.8، Tool B = 75.8.

**متن گفتاری:**

«روی سی Case، Tool A چهار امتیاز جلوتر است.

حالا هیچ‌چیز را دست نمی‌زنیم. نه Prompt، نه مدل، نه Metric، نه Protocol. فقط ده Case اضافه می‌کنیم: بازارهای کم‌داده، منابع متعارض، Briefهای مبهم.

روی همین ده Case، Tool A چهل می‌گیرد و Tool B هفتادودو. میانگین چهل Case را حساب کنید: Tool A حدود هفتاد ممیز هشت، Tool B حدود هفتادوپنج ممیز هشت.

Winner عوض شد.

ابزارها تغییر کردند؟ نه. Metric عوض شد؟ نه. فقط جهانی که وارد تست شد فرق کرد.

Dataset اول بیشتر بازارهای مشهور و داده‌غنی را می‌دید. نتیجهٔ اول برای همان جهان درست بود. اشتباه آنجا شروع شد که اسمش را گذاشتیم "بهترین ابزار تحقیق بازار".

Dataset مجموعهٔ سؤال نیست. Dataset یک ادعای پنهان است دربارهٔ اینکه کار واقعی چه شکلی دارد.»

**در یک جمله:** عوض‌کردن ده Case از چهل Case، برنده را عوض کرد — پس Dataset خودش یک تصمیم است، نه پس‌زمینه.

**EDIT:** پس از Rank flip، عنوان Leaderboard به `FOR WHICH DISTRIBUTION?` تغییر کند.

### 01:20–03:20 — Population، Sample و حق ادعا

**ON SCREEN:** `THE MODEL`  
**HEADLINE:** `THE SAMPLE IS NOT THE WORLD.`

**متن گفتاری:**

«چهار لایه را از هم جدا کنیم. معمولاً هر چهار تا را یکی فرض می‌کنیم و همان‌جا اشتباه شروع می‌شود.

اول، `Target population` (جامعهٔ هدف): جهانی که می‌خواهیم درباره‌اش تصمیم بگیریم. اینجا یعنی تحقیق اولیهٔ بازار برای Founderهای غیرفنی.

دوم، `Sampling frame` (چارچوب نمونه‌گیری): آنچه واقعاً به آن دسترسی داریم. Briefهایی که می‌توانیم بسازیم و بازارهایی که قابل‌بررسی‌اند.

سوم، Dataset: مواردی که واقعاً وارد Run می‌شوند.

چهارم، `Claim population` (جهان مجازِ ادعا): جهانی که با این روش حق داریم درباره‌اش حرف بزنیم.

حالا یک مثال. اگر بیشتر Caseهای ما انگلیسی، B2B و بازار آمریکا باشند، دربارهٔ تحقیق بازار فارسی هیچ Evidence نداریم. حتی اگر امتیاز عالی بگیریم.

پس ۴۸ Case را نمونهٔ تصادفی جهان معرفی نمی‌کنیم. این یک Pilot هدفمند است: برای مقایسهٔ ابزارها در برش‌های ازپیش‌تعریف‌شده، پیداکردن Failure و ساختن نسخهٔ بعدی.

عدد چهل‌وهشت هم محدودیت بودجه و برچسب‌گذاری ماست. عدد جادویی آماری نیست.»

**در یک جمله:** نتیجه فقط تا مرز همان جهانی معتبر است که واقعاً وارد Dataset شد.

### 03:20–05:40 — Distribution وزن‌های پنهان را تعیین می‌کند

**ON SCREEN:** `WHAT THE SCORE SEES`  
**HEADLINE:** `A DATASET IS A WEIGHTING SYSTEM.`

**تصویر:** Mixer با Sliceهای `EASY / HARD / B2B / B2C / HIGH-DATA / LOW-DATA`.

**متن گفتاری:**

«Average نهایی در عمل یعنی: عملکرد هر `Slice` (برش) ضرب‌در وزن آن برش.

مشکل اینجاست که آن وزن‌ها را کسی به‌شکل عدد ننوشته. داخل تعداد Caseها پنهان شده‌اند.

اگر هشتاد درصد Dataset آسان باشد، ما در عمل عملکرد آسان را وزن داده‌ایم. اگر بیشتر Caseها شرکت‌های مشهور باشند، توانایی پیداکردن دادهٔ فراوان را پاداش داده‌ایم. کسی این تصمیم را اعلام نکرده؛ ولی گرفته شده است.

Sampling grid همین وزن‌ها را از پنهان به آشکار می‌آورد.

برای نسخهٔ اول: B2B و B2C هرکدام بیست‌وچهار Case. Difficulty شانزده Easy، بیست Medium، دوازده Hard. Origin بیست‌وچهار Real، شانزده Controlled variation، هشت Challenge.

این سهم‌ها ادعا نمی‌کنند Distribution واقعی Founderها دقیقاً همین است. هدف نسخهٔ اول Coverage و تشخیص است، نه برآورد.

و یک قانون گزارش: هر Score کلی باید کنار Score هر برش نمایش داده شود. اگر ابزاری فقط به‌خاطر غلبهٔ یک برش برنده شده، مخاطب باید ببیند.»

**در یک جمله:** Dataset یک سیستم وزن‌دهی است؛ تعداد Case در هر برش، همان وزنی است که کسی اعلامش نکرده.

### 05:40–08:10 — Hard بودن یعنی چه Failureای را آشکار می‌کند؟

**ON SCREEN:** `THE STRESS TEST`  
**HEADLINE:** `DIFFICULTY NEEDS A REASON.`

**متن گفتاری:**

«Easy، Medium و Hard را با حس شخصی تعیین نمی‌کنیم.

Easy یعنی Brief روشن، منابع مستقیم، بازار شناخته‌شده. Medium یعنی باید چند منبع را ترکیب کنیم یا یک ابهام را رفع کنیم. Hard یعنی داده کم است، منابع با هم می‌جنگند، یا مرز بازار مبهم است.

`Edge case` (مورد مرزی) با Hard یکی نیست. Edge case ممکن است نادر باشد، ولی شکستش گران تمام می‌شود: ساختن رقیب خیالی، Citation جعلی، اشتباه در واحد پول، یا قاطی‌کردن دو شرکت هم‌نام.

برای هر Case یک `failure_hypothesis` می‌نویسیم. یعنی: این Case قرار است چه ضعفی را آشکار کند؟

اگر تنها جوابمان "سخت است" باشد، هنوز طراحی نکرده‌ایم.

یک روش خیلی خوب، ساخت Pair کنترل‌شده است. یک Brief واقعی را نگه می‌داریم و فقط یک عامل را عوض می‌کنیم. مثلاً همان بازار، ولی یک‌بار با نام شرکت مبهم.

اگر نتیجه فرو ریخت، Robustness را روی یک تفاوت مشخص دیده‌ایم. نه روی دو Case که در ده چیز با هم فرق داشتند.

یک هشدار آخر. Difficulty باید سال بعد هم معنا بدهد. اگر آن را با امتیاز مدل‌های امروز تعریف کنیم، با قوی‌ترشدن مدل‌ها کل Taxonomy فرو می‌ریزد.»

**در یک جمله:** هر Case باید یک شغل داشته باشد — اگر نمی‌دانیم چه Failureای را شکار می‌کند، فقط N را بزرگ کرده‌ایم.

### 08:10–10:20 — Real، Synthetic و Dynamic: سه ابزار، نه سه رتبه

**ON SCREEN:** `THE EVIDENCE`

**متن گفتاری:**

«سه منبع Case داریم و هیچ‌کدام "بهترین" نیست.

Case واقعی، Context و بی‌نظمی واقعی کاربر را نگه می‌دارد. اما Distribution آن معمولاً نامتوازن است و Privacy یا License می‌تواند انتشارش را ببندد.

`Controlled synthetic` (مورد ساختگیِ کنترل‌شده) اجازه می‌دهد یک متغیر را عوض کنیم. مثلاً دو بازار با ساختار یکسان بسازیم؛ در یکی منبع مستقیم هست، در دیگری فقط شواهد غیرمستقیم.

این برای تشخیص فوق‌العاده است. ولی یک ریسک دارد: داده امضای سازنده‌اش را حمل می‌کند. اگر همهٔ Caseها را یک مدل ساخته باشد، Benchmark ممکن است سبک همان مدل را پاداش دهد.

`Dynamic case` (مورد پویا) از دادهٔ تازه یا Snapshot زمانی استفاده می‌کند. ریسک آشنایی قبلی را کم می‌کند و Drift را نشان می‌دهد. در عوض نگهداری و تکرارپذیری‌اش سخت‌تر است.

نسخهٔ اول ما ترکیب هر سه است. Real برای Relevance، Controlled برای تشخیص، Challenge برای Failureهای پرهزینه.»

**در یک جمله:** Real می‌گوید چه اتفاقی می‌افتد، Controlled می‌گوید چرا، و Dynamic نمی‌گذارد Benchmark کهنه شود.

### 10:20–12:20 — Snapshot، Freshness و Contamination

**ON SCREEN:** `WHAT IT MISSES`  
**HEADLINE:** `PUBLIC DATA CAN BECOME TRAINING DATA.`

**متن گفتاری:**

«Benchmark عمومی یک مشکل بنیادی دارد. اگر Dataset را روی وب منتشر کنیم، ممکن است بعداً وارد Training شود.

آن‌وقت Score بخشی از آشنایی را پاداش می‌دهد، نه Generalization را. اسم این `Contamination` (آلودگی داده) است.

Contamination را همیشه نمی‌شود قطعی تشخیص داد. پس عبارت "contamination-free" را بدون شواهد به کار نمی‌بریم. به‌جایش ریسک را ثبت می‌کنیم و چند اقدام کاهش داریم: Caseهای تازه، Holdout خصوصی، پارافرایز کنترل‌شده، Snapshot تاریخ‌دار، و منتشرنکردن Answer key پیش از Main run.

Freshness یک مسئلهٔ جداست. قیمت، تعداد مشتری، Funding و فهرست رقبا با زمان عوض می‌شوند.

پس برای هر Fact سه چیز لازم داریم: Source URL، تاریخ Snapshot، و در موارد حساس نسخهٔ ذخیره‌شده. Ground truth بدون تاریخ، چند ماه بعد غلط می‌شود — بدون اینکه Annotator اولیه اشتباهی کرده باشد.

و `Leakage` (نشت) از Contamination جداست. اگر Answer key وارد Prompt شود، یا Reviewer نام Tool را ببیند، خودِ Run آلوده شده است.

برای همین Holdout، مدیریت دسترسی و Blindness بخشی از Governance خود Dataset هستند، نه کار جانبی.»

**در یک جمله:** آلودگی را نمی‌شود اثبات نکرد؛ فقط می‌شود ریسکش را نوشت و کمش کرد.

### 12:20–15:30 — Ground truth برای Report باز چه شکلی است؟

**ON SCREEN:** `THE MODEL`  
**HEADLINE:** `GROUND TRUTH IS OFTEN A REFERENCE PROCESS.`

**تصویر:** هرم چهارلایهٔ Reference.

**متن گفتاری:**

«در سؤال چندگزینه‌ای، Answer key ساده است. در یک Report تحقیق بازار، ما اصلاً یک متن نهایی و درست نداریم.

پس به‌جای Ground truth، `Reference standard` (معیار مرجع) می‌سازیم: یک فرایند قابل‌بازرسی، نه یک پاسخ.

چهار لایه دارد.

لایهٔ اول، Factهای قابل‌بررسی. برای هر Case فهرستی از Factهای لازم داریم: نام رقیب، مدل درآمدی، شواهد تقاضا. هر Fact یک Source دارد، یک تاریخ Snapshot و یک سطح اطمینان.

لایهٔ دوم، Claim support. Report را به Claimهای قابل‌بررسی می‌شکنیم. هر Claim یکی از چهار برچسب می‌گیرد: Supported، Partial، Unsupported، Contradicted.

اینجا یک نکتهٔ مهم هست. وجود لینک کافی نیست. Source باید دقیقاً همان Claim را پشتیبانی کند، نه چیزی نزدیک به آن.

لایهٔ سوم، Rubric. برای Actionability پاسخ واحد نداریم، پس Anchor رفتاری می‌نویسیم. امتیاز یک یعنی توصیهٔ کلی بدون شواهد. امتیاز سه یعنی Next step مشخص، ولی بدون اولویت. امتیاز پنج یعنی اقدام اولویت‌دار، با شواهد، Dependency، Risk و سؤال باز.

لایهٔ چهارم، Pairwise judgment. دو Report ناشناس را کنار هم می‌گذاریم و برای یک تصمیم مشخص می‌پرسیم کدام مفیدتر است. Annotator انتخاب می‌کند و دلیلش را می‌نویسد.

این چهار لایه جایگزین هم نیستند. Fact table صحت را می‌بیند. Rubric فایده را. Pairwise تفاوت ظریف را.

اگر همه را در یک Rating کلی حل کنیم، Auditability از بین می‌رود.»

**در یک جمله:** وقتی خروجی باز است، حقیقت یک متن نیست — یک فرایند داوریِ چهارلایه و قابل‌بازرسی است.

### 15:30–17:25 — اختلاف Annotatorها خطای مزاحم نیست

**ON SCREEN:** `MEASURED, NOT ASSUMED`  
**HEADLINE:** `DISAGREEMENT CAN REVEAL A BROKEN LABEL.`

**متن گفتاری:**

«اول، شرایط داوری. نام Tool را از Report حذف می‌کنیم و ترتیب پاسخ‌ها را تصادفی می‌کنیم. Annotatorها یک Pilot مشترک دارند، اما در برچسب اصلی مستقل کار می‌کنند.

حداقل ده Case و تمام اختلاف‌های بحرانی، دوبار برچسب می‌خورند.

Raw agreement را نشان می‌دهیم. ولی می‌دانیم توافق تصادفی هم می‌تواند بالا باشد. پس یک معیار Chance-corrected هم لازم داریم، مثل Krippendorff's alpha یا Cohen's kappa.

انتخاب بین این‌ها به تعداد Annotator، نوع Scale و Missing data بستگی دارد. آستانهٔ جادویی که برای همهٔ Taskها کار کند وجود ندارد.

اما مهم‌تر از خودِ عدد، ماتریس اختلاف است.

اگر Annotatorها مدام Supported و Partial را جابه‌جا می‌کنند، احتمالاً تعریف Partial مبهم است. اگر روی Caseهای کم‌داده اختلاف بالا می‌رود، احتمالاً Source standard کافی نیست.

پس Adjudicator فقط برنده را انتخاب نمی‌کند. یک Reason code ثبت می‌کند. Annotation guide نسخه می‌گیرد. و اگر Guide بعد از Pilot عوض شد، برچسب‌های قبلی دوباره بررسی می‌شوند.

Agreement پایین همیشه یعنی Annotator بد؟ نه. گاهی Benchmark دارد به ما می‌گوید سؤالمان هنوز خوب طراحی نشده.»

**در یک جمله:** اختلاف را قبل از حل‌کردن بخوان — گاهی ایراد از داور نیست، از خود سؤال است.

### 17:25–19:10 — ساخت Dataset ۴۸ Case

**ON SCREEN:** `THE BUILD`  
**HEADLINE:** `EVERY CASE NEEDS A JOB.`

**تصویر:** Grid زنده با فیلترهای B2B/B2C، difficulty، origin، geography و failure tag.

**متن گفتاری:**

«نسخهٔ صفر ممیز یک، چهل‌وهشت Case دارد. سه دسته.

شش Case برای Pilot. Prompt، Schema و Rubric را روی این‌ها Debug می‌کنیم. بعد از Tuning، این‌ها یا وارد Ranking اصلی نمی‌شوند یا جدا گزارش می‌شوند.

سی‌وشش Case، Main test. همهٔ ابزارها روی همین‌ها و تحت یک Protocol ثابت اجرا می‌شوند.

شش Case، `Holdout` (کنارگذاشته). این‌ها باز نمی‌شوند تا Metric و قواعد Failure فریز شوند. Answer key و بخشی از Snapshotشان تا پایان Main run عمومی نمی‌شود.

حالا ترکیب. بیست‌وچهار B2B و بیست‌وچهار B2C. شانزده Easy، بیست Medium، دوازده Hard. بیست‌وچهار Real، شانزده Controlled variation، هشت Challenge.

هر Case این فیلدها را دارد: `case_id`، نسخه، Brief، خروجی‌های لازم، سقف زمان، سقف هزینه، دلیل Difficulty، برچسب‌های Edge، Factهای مرجع، Snapshot منبع و Metadata حاکمیتی.

و مهم‌ترین فیلد: `failure_hypothesis`.

هر Case باید یک شغل داشته باشد. اگر نمی‌دانیم چه Coverage یا چه Failureای اضافه می‌کند، فقط N را بزرگ کرده‌ایم.»

**در یک جمله:** ۴۸ Case یعنی سه کار جدا — شش تا برای Debug، سی‌وشش تا برای مقایسه، شش تا برای اینکه بعداً خودمان را گول نزنیم.

### 19:10–20:00 — Verdict و پل به Metric

**ON SCREEN:** `THE VERDICT`

**متن گفتاری:**

«قاعدهٔ این قسمت: Dataset خوب سه سؤال را جواب می‌دهد.

نمایندهٔ کدام جهان است؟ کدام Failureها را آشکار می‌کند؟ Reference standard چطور ساخته شد؟

تعداد مهم است — اما بعد از Relevance، Coverage و کیفیت برچسب. ده‌هزار سؤال نامرتبط، یک ادعای اشتباه را نجات نمی‌دهد.

حالا جهان آزمایش را داریم و چهل‌وهشت Case داخلش. ولی هنوز یک چیز را نمی‌دانیم: Failure چطور به عدد تبدیل می‌شود؟

Precision مهم‌تر است یا Recall؟ Average چه چیزی را پنهان می‌کند؟ اختلاف یک امتیازی واقعاً معنا دارد؟ و اگر وزن‌ها را عوض کنیم، برنده برمی‌گردد؟

قسمت بعد Scorecard را می‌سازیم. و نشان می‌دهیم Metric فقط یک فرمول نیست؛ یک تصمیم است دربارهٔ اینکه کدام خطا گران‌تر است.

در کامنت، سخت‌ترین Edge case واقعی حوزهٔ خودتان را بنویسید. همان موردی که Benchmarkهای عمومی معمولاً نمی‌بینند.»

**در یک جمله:** جهان تست ساخته شد؛ حالا باید تصمیم بگیریم کدام خطا چقدر می‌ارزد.

---

## 6. Dataset Schema پیشنهادی

| گروه | فیلدها |
|---|---|
| Identity | `case_id`, `version`, `created_at`, `status` |
| Context | `industry`, `business_model`, `geography`, `language`, `stage` |
| Task | `brief`, `required_outputs`, `time_limit`, `cost_limit` |
| Difficulty | `tier`, `difficulty_reason`, `scarcity`, `ambiguity`, `freshness`, `edge_tags` |
| Origin | `real`, `controlled_variation`, `challenge`, `parent_case_id` |
| Reference | `fact_id`, `expected_value`, `source_url`, `snapshot_date`, `confidence` |
| Annotation | `unit_id`, `label`, `rubric_anchor`, `annotator_id`, `reason_code` |
| Scoring | `claim_units`, `citation_units`, `action_units`, `critical_failures` |
| Governance | `author`, `reviewer`, `leakage_check`, `change_reason`, `license` |

### ترکیب ۴۸ Case

| بعد | سهم نسخهٔ v0.1 | چرا |
|---|---:|---|
| B2B / B2C | 24 / 24 | جلوگیری از غلبهٔ یک مدل کسب‌وکار |
| Easy / Medium / Hard | 16 / 20 / 12 | پوشش تشخیصی؛ نه تخمین Distribution واقعی |
| Real / Controlled / Challenge | 24 / 16 / 8 | Relevance + diagnosis + high-cost failures |
| Pilot / Main / Holdout | 6 / 36 / 6 | جداسازی Tuning از Test |
| Double-annotated | حداقل 10 + همهٔ Critical disagreements | تخمین Reliability و اصلاح Guide |

---

## 7. Annotation Guide خلاصه

### Claim support labels

| Label | تعریف قابل‌مشاهده |
|---|---|
| Supported | Source صریحاً Claim و Scope آن را پشتیبانی می‌کند |
| Partial | بخشی از Claim یا Scope محدودتری پشتیبانی می‌شود |
| Unsupported | Source مرتبط است، اما Evidence لازم برای Claim را ندارد |
| Contradicted | Source با Claim ناسازگار است |

### Actionability anchors

| Score | Anchor |
|---:|---|
| 1 | توصیهٔ کلی، بدون Evidence، Priority یا Next step |
| 3 | Next step مشخص و بخشی از Evidence؛ Priority/Dependency ناقص |
| 5 | اقدام اولویت‌دار، Evidence، Dependency، Risk، Owner/sequence و سؤال باز |

### Adjudication reason codes

- `UNIT_AMBIGUOUS`
- `SOURCE_SCOPE_MISMATCH`
- `TEMPORAL_CONFLICT`
- `RUBRIC_ANCHOR_GAP`
- `ANNOTATOR_MISREAD`
- `REFERENCE_INCOMPLETE`

---

## 8. طراحی تجربهٔ بصری

### صحنهٔ اصلی: Dataset World Builder

- یک جهان از Caseها به‌شکل نقطه‌های داده نمایش داده شود.
- Sliderها: `DIFFICULTY`, `DATA AVAILABILITY`, `FRESHNESS`, `AMBIGUITY`.
- با تغییر ترکیب Sliceها، Score و Winner زنده تغییر کند.
- Button `SHOW WHO IS MISSING` بخش‌های بدون Coverage را Highlight کند.
- روی هر Case کلیک شود: Brief، failure hypothesis، source snapshot و annotation status باز شود.
- Mode `GROUND TRUTH X-RAY` هرم Fact → Claim → Rubric → Preference را نشان دهد.

### Proof objectهای حذف‌ناپذیر

1. Rank flip ۳۰+۱۰.
2. Population–Frame–Sample–Claim funnel.
3. Slice weighting mixer.
4. Controlled pair.
5. Snapshot timeline.
6. Reference pyramid.
7. Annotator disagreement matrix.
8. Sampling grid ۴۸ Case.

---

## 9. سایت‌هایی که باید نمایش داده شوند

| زمان | سایت | بخش | جملهٔ همراه | زمان |
|---|---|---|---|---:|
| 02:00 | [NIST AI 800-2 IPD](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf) | Practice 1.2؛ diversity، quantity، contamination | «تعداد، Coverage و Diversity سه سؤال جدا هستند.» | 18 ثانیه |
| 08:45 | [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) | Abstract؛ motivation/composition/collection/uses | «Dataset باید منشأ، ترکیب و استفادهٔ توصیه‌شده را مستند کند.» | 15 ثانیه |
| 09:20 | [Data Cards Playbook](https://sites.research.google/datacardsplaybook/) | یک Data Card و بخش‌های آن | «Documentation بخشی از خود Dataset است، نه Appendix تزئینی.» | 15 ثانیه |
| 10:50 | [SWE-bench Goes Live](https://arxiv.org/abs/2505.23419) | ایدهٔ Taskهای تازه و Live | «Freshness هزینهٔ Maintenance دارد، اما ریسک آشنایی را کاهش می‌دهد.» | 12 ثانیه |
| 11:25 | [Benchmark Data Contamination Survey](https://arxiv.org/abs/2406.04244) | Taxonomy یا Abstract | «نبود مدرک Leakage، اثبات پاکی نیست.» | 12 ثانیه |
| 16:05 | [Measuring Annotator Agreement](https://arxiv.org/abs/2212.09503) | Abstract؛ پیچیدگی Task و distance | «Agreement metric باید با نوع Annotation هماهنگ باشد.» | 12 ثانیه |
| 17:45 | Spreadsheet/Atlas محلی | Sampling grid و Case inspector | «هر Case باید Coverage یا Failure مشخصی اضافه کند.» | 25 ثانیه |

---

## 10. چک‌لیست علمی قبل از ضبط

- `۴۸ Case` را Sample size کافی برای تعمیم جهانی ننام؛ Pilot هدفمند و تشخیصی است.
- Quota balance را Representativeness واقعی معرفی نکن.
- Rank flip مثال را با برچسب `ILLUSTRATIVE` نشان بده.
- Hard را فقط براساس Score فعلی مدل‌ها تعریف نکن.
- Synthetic data را ذاتاً ضعیف یا بهتر معرفی نکن؛ Generator bias را بگو.
- `Contamination-free` ادعا نکن مگر شواهد مستقیم داشته باشی.
- Ground truth خروجی باز را یک متن نهایی و مطلق نشان نده.
- Agreement بالا را معادل Validity ندان؛ Annotatorها می‌توانند روی Label غلط توافق کنند.
- Agreement پایین را فقط به Annotator بد نسبت نده.
- Pilot پس از Tuning را بدون برچسب وارد Main score نکن.
- Snapshot و زمان Factهای پویا را حذف نکن.

---

## 11. بستهٔ ضبط

### A-roll حذف‌ناپذیر

- Hook و محاسبهٔ Rank flip.
- جملهٔ «Dataset یک weighting system است».
- تعریف Population/Sample/Claim.
- Controlled pair.
- Reference standard چهارلایه.
- اختلاف Annotatorها به‌عنوان Signal.
- ساخت Grid ۴۸ Case.

### B-roll

- اضافه‌شدن ده Case و تغییر Leaderboard.
- فیلتر Sliceها روی Dataset Builder.
- ساخت یک Case و Controlled variation آن.
- Source snapshot با تاریخ.
- Annotation کور و Swap ترتیب.
- Disagreement matrix و Reason codes.

### نقاط مناسب Pattern interrupt

- 00:45: Winner عوض شود.
- 03:55: Slider سهم Hard را بالا ببرد.
- 06:40: یک Brief به Pair تبدیل شود.
- 11:10: Snapshot تاریخ‌دار باز شود.
- 13:30: Citation ظاهراً معتبر به Unsupported تبدیل شود.
- 16:10: Agreement پایین، Guide را Highlight کند.

---

## 12. CTA نهایی

> Schema را بردارید و فقط ۱۲ Case بسازید: چهار Easy، چهار Medium و چهار Hard. برای هر Case یک `failure_hypothesis` بنویسید. قبل از افزایش N، مطمئن شوید هر ردیف دلیل حضور دارد.

---

## 13. منابع اصلی این قسمت

1. NIST, [Practices for Automated Benchmark Evaluations of Language Models — AI 800-2 Initial Public Draft](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf), January 2026.
2. Gebru et al., [Datasheets for Datasets](https://arxiv.org/abs/1803.09010).
3. Pushkarna et al., [Data Cards: Purposeful and Transparent Dataset Documentation](https://dl.acm.org/doi/10.1145/3531146.3533231) و [Data Cards Playbook](https://sites.research.google/datacardsplaybook/).
4. Xu et al., [Benchmark Data Contamination of Large Language Models: A Survey](https://arxiv.org/abs/2406.04244).
5. Zhang et al., [SWE-bench Goes Live!](https://arxiv.org/abs/2505.23419).
6. Braylan et al., [Measuring Annotator Agreement Generally across Complex Structured, Multi-object, and Free-text Annotation Tasks](https://arxiv.org/abs/2212.09503).
7. van der Lee et al., [Best Practices for the Human Evaluation of Automatically Generated Text](https://aclanthology.org/W19-8643/).
