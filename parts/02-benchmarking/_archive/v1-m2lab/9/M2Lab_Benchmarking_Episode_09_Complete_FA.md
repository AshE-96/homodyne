# M2Lab Benchmarking Foundations — Episode 09

## Publishing Benchmark Results People Can Trust

**نسخه:** 1.1 — پایان فصل  
**زبان روایت:** فارسی  
**زبان عناصر روی تصویر:** انگلیسی  
**زمان هدف:** 18:00 تا 20:00  
**خروجی این قسمت:** `Public Benchmark Report + Evidence Atlas + Publication Checklist + Correction Policy`  
**پروژهٔ فصل:** تبدیل Result قسمت ۸ به یک Data Product قابل Audit، Version و Rerun

---

## 0. واژه‌های این قسمت

مرجع سریع. روی اسلاید همیشه واژهٔ انگلیسی می‌آید؛ این جدول برای گوش مخاطب است.

| واژه | به فارسی | یک‌خطی |
|---|---|---|
| `Evidence Atlas` | اطلس شواهد | صفحه‌ای که از رتبه تا منبع خام مسیر دارد |
| `Publication level` | سطح انتشار | چقدر از این کار واقعاً قابل بازتولید است |
| `Auditable only` | فقط قابل‌بازرسی | نمی‌شود دوباره اجرا کرد، ولی می‌شود بررسی کرد |
| `Superseded` | جایگزین‌شده | نسخهٔ قبلی پاک نمی‌شود؛ کنار گذاشته می‌شود |
| `Breaking change` | تغییر ناسازگار | از این نقطه به بعد، مقایسه با گذشته معتبر نیست |
| `Correction policy` | سیاست اصلاح | چه کسی، چطور و با چه شدتی خطا را اصلاح می‌کند |
| `Anchor case` | Case لنگر | Caseای که برای دیدن روند، ثابت نگه داشته می‌شود |
| `Disclosure` | افشا | اعلام هر رابطهٔ مالی، قبل از توصیه |
| `Insufficient evidence` | شواهد ناکافی | یک نتیجهٔ معتبر، نه یک صفحهٔ خالی |

---

## 1. قول این قسمت به مخاطب

در پایان قسمت، مخاطب باید بتواند:

- انتشار Benchmark را از ساخت Leaderboard جدا کند؛
- یک Executive result را بدون حذف Caveat بنویسد؛
- Result، Method، Evidence، Decision و Governance را لایه‌بندی کند؛
- Rank را فقط در صورت Separation قابل دفاع نشان دهد؛
- Score را تا Case، Claim، Citation و Raw run قابل Drill-down کند؛
- Methodology، Dataset card و Metric registry را Version کند؛
- میان `Reproducible`، `Repeatable` و `Auditable` Label مناسب بگذارد؛
- Privacy، License و Security را هنگام انتشار Raw evidence رعایت کند؛
- Drift، Rerun و Breaking change را مدیریت کند؛
- Correction، Appeal، Conflict و Sponsorship را شفاف کند؛
- Recommendation سناریومحور بسازد و `Insufficient evidence` را نتیجهٔ معتبر بداند.

جملهٔ محوری:

> **Do not ask people to trust the ranking. Give them a path to inspect it.**

Hook:

> **SHOW THE EVIDENCE**

---

## 2. مسئلهٔ روایی

### THE CLAIM

«برای انتشار Benchmark، یک جدول رتبه، Methodology link و چند نمودار کافی است.»

### THE EVIDENCE

کاربر نمی‌تواند از Rank به Result سازندهٔ آن برسد؛ Version و Date گم می‌شوند؛ CI در Footnote می‌رود؛ Failureها پشت Average پنهان می‌مانند؛ Methodology قابل تغییر است؛ و Correction تاریخچهٔ قبلی را بازنویسی می‌کند.

### THE STRESS TEST

یک Leaderboard بدون Evidence باز می‌شود. کاربر روی Score کلیک می‌کند و صفحهٔ Methodology خالی است. سپس همان Result در Atlas بازسازی می‌شود: Rank → Profile → Case → Claim → Source → Run → Version.

### THE VERDICT

اعتماد Feature بصری نیست؛ معماری دسترسی به Evidence و Governance پس از انتشار است. Benchmark خوب فقط می‌گوید چه دیدیم؛ نشان می‌دهد چگونه دیدیم، کجا مطمئن نیستیم و چگونه می‌توان Result را اصلاح کرد.

### THE BUILD

M2Lab Benchmark Atlas با پنج لایه ساخته می‌شود:

`RESULT → METHOD → EVIDENCE → DECISION → GOVERNANCE`

---

## 3. تئوری علمی و معماری Publication

### 3.1 چرا Documentation بخشی از Measurement است؟

`Datasheets for Datasets` پیشنهاد می‌کند Motivation، Composition، Collection، Use و Maintenance داده مستند شوند. `Model Cards` Intended use، Evaluation، Limitations و تفاوت عملکرد در گروه‌های مرتبط را وارد گزارش می‌کند. `BenchmarkCards` همین منطق را برای انتخاب و Riskهای Benchmark صورت‌بندی می‌کند.

این Cardها تزئین Repository نیستند. بدون آنها Consumer نمی‌داند Result برای تصمیمش مناسب است یا نه.

### 3.2 پنج لایهٔ انتشار

| لایه | سؤال کاربر | محتوای لازم |
|---|---|---|
| Result | چه اتفاقی افتاد؟ | profile، primary estimate، uncertainty، guardrail، date |
| Method | چگونه سنجیدید؟ | spec، dataset card، protocol، metric registry، analysis plan |
| Evidence | این عدد از کجا آمد؟ | case، run، claim، label، source، raw/derived output |
| Decision | برای من چه معنایی دارد؟ | scenario recommendation، caveat، insufficient-evidence zone |
| Governance | بعداً چه می‌شود؟ | versions، changes، issues، conflicts، corrections، rerun |

اگر فقط لایهٔ Result وجود داشته باشد، Benchmark عملاً یک Claim با ظاهر عددی است.

### 3.3 Executive summary شش‌جمله‌ای

Summary باید در شش جمله این اجزا را داشته باشد:

1. Decision و Scope؛
2. Toolها/نسخه‌ها و Run window؛
3. N اصلی و Dataset؛
4. Primary result + Uncertainty؛
5. Guardrail/Trade-off اصلی؛
6. مهم‌ترین Limitation.

Summary خوب Caveat را به Appendix تبعید نمی‌کند.

### 3.4 Leaderboard چه زمانی Rank نشان می‌دهد؟

قانون M2Lab:

- Raw rank می‌تواند برای Navigation باشد؛
- Verdict rank فقط وقتی نمایش داده شود که paired evidence و Practical threshold Separation بدهند؛
- در حالت نامطمئن از `TIER`, `CONTENDER SET` یا `UNRESOLVED` استفاده شود؛
- CI، Rank interval/spread، N و Date کنار Score بمانند؛
- Composite پیش‌فرض نباید Weight سناریوی جذاب را پنهان کند؛
- Guardrail status داخل Score حل نشود.

Rank absence یک نقص UI نیست. گاهی صادقانه‌ترین نمایش Evidence است.

### 3.5 Evidence trace و Provenance

حداقل مسیر:

`Result → Metric contribution → Case → Evaluation unit → Label → Source/Raw output → Run manifest`

هر Node شناسه و Version دارد. اگر Source تغییر یا حذف شد، Snapshot date، locator و وضعیت availability باقی می‌ماند. Hash اثبات Truth نیست؛ فقط کمک می‌کند تغییر Artifact دیده شود.

### 3.6 Publication level

سه Label:

- `REPRODUCIBLE`: Code/Data/Environment اجازهٔ بازتولید محاسبه را می‌دهند؛
- `PARTIALLY REPRODUCIBLE`: بخشی از Pipeline باز است اما Product/Web بسته یا پویاست؛
- `AUDITABLE ONLY`: Evidence و روش قابل بررسی‌اند ولی System دقیقاً قابل بازاجرا نیست.

برای Consumer productهای زنده، Label سوم یا دوم اغلب صادقانه‌تر است. ادعای Full reproducibility بدون امکان دسترسی به Version قبلی غلط است.

### 3.7 Transparency مرز دارد

منتشر نمی‌شود:

- API key، session token و credential؛
- Personal/private data؛
- copyrighted full text خارج از مجوز؛
- Prompt یا exploit امنیتی حساس؛
- Holdout answerهایی که انتشارشان Benchmark را می‌شکند؛
- Output خامی که Terms اجازه نمی‌دهد.

در این موارد Derived label، Excerpt مجاز، Hash، Timestamp، Locator و دلیل عدم انتشار ارائه می‌شود. `Not public` نباید `not documented` باشد.

### 3.8 Versioning و Comparability

چهار Version مستقل:

- `Benchmark version`
- `Dataset version`
- `Protocol version`
- `Tool/model version`

قاعدهٔ ساده:

- `Patch`: Correction بدون تغییر معنی Result؛
- `Minor`: Case/Metric سازگار اضافه می‌شود؛
- `Major`: Claim، Dataset distribution یا Scoring تغییر Breaking دارد.

NIST AI 800-2 Versioning و ثبت Exact model version را توصیه می‌کند و Breaking change را نقطه‌ای می‌داند که مقایسهٔ قبل/بعد دیگر مستقیم معتبر نیست.

### 3.9 Drift و Rerun

Rerun نسخهٔ اول Quarterly است:

- ۸۰٪ Anchor ثابت؛
- ۲۰٪ Fresh cases؛
- Off-cycle rerun برای Tool release عمده؛
- Date badge روی هر Result؛
- مقایسهٔ Trend فقط وقتی Method/Dataset compatible هستند؛
- تغییر مشاهده‌شده به Tool، Dataset یا Protocol نسبت داده نمی‌شود مگر Evidence جداسازی وجود داشته باشد.

### 3.10 Corrections، Appeals و Conflict

هر Issue باید `case_id/run_id/claim_id` داشته باشد و یکی از Statusها:

`OPEN / UNDER REVIEW / ACCEPTED / REJECTED / FIXED`

Severity:

- `Minor`: typo/link بدون اثر Score؛
- `Material`: Label/Cost/Metric تغییر می‌کند؛
- `Critical`: Leakage، Misconfiguration یا Method error Claim اصلی را تهدید می‌کند.

Material/Critical نیازمند Banner، Version جدید، Impact note و حفظ نسخهٔ Superseded هستند.

Vendor حق ارائهٔ Evidence و factual preview دارد؛ حق حذف Verdict نامطلوب ندارد. Sponsor/Affiliate بالای Result و قبل از Recommendation افشا می‌شود.

---

## 4. فلو زمانی نهایی

| زمان | Beat | هدف | Proof object |
|---|---|---|---|
| 00:00–01:10 | A leaderboard with no evidence | تعریف مشکل انتشار | broken methodology link |
| 01:10–03:20 | Five layers of trust | ساخت معماری | result→governance stack |
| 03:20–05:40 | A rank is not a verdict | طراحی Result view | profile + CI + guardrail |
| 05:40–07:40 | Method must be readable | Documentation | spec/data/protocol/metric cards |
| 07:40–09:40 | Show evidence without leaking it | Provenance + privacy | evidence drill-down |
| 09:40–11:45 | Every result expires | Versioning + drift | timeline + breaking change |
| 11:45–13:50 | Trust after publication | Correction + appeal | issue/correction flow |
| 13:50–15:50 | Recommendation by scenario | تبدیل Evidence به Decision | scenario selector |
| 15:50–17:30 | Build M2Lab Benchmark Atlas | Data product نهایی | atlas architecture |
| 17:30–18:40 | Close the season | مرور ۹ قسمت و Next test | season montage |

---

## 5. متن کامل آمادهٔ ضبط

### 00:00–01:10 — Leaderboard بدون Evidence

**تصویر:** جدول رتبه‌ها. کلیک روی `METHODOLOGY` به صفحهٔ خالی می‌رود؛ کلیک روی Score هیچ Caseی باز نمی‌کند.

**متن گفتاری:**

«اگر فقط رتبه و امتیاز را منتشر کنم، از شما خواسته‌ام به نتیجه‌ای اعتماد کنید که مسیر ساختش را نمی‌بینید.

آن لینک کوچک Methodology زیر جدول، تزئین نیست.

آزمونش ساده است. اگر نتوانید از امتیاز به Case برسید، از Case به برچسب، و از برچسب به شواهد — این Benchmark برای شما قابل بازرسی نیست.

انتشار قابل‌اعتماد به پنج سؤال جواب می‌دهد.

چه اتفاقی افتاد؟ چطور سنجیده شد؟ شواهد کجاست؟ برای چه تصمیمی معتبر است؟ و اگر خطایی پیدا شد، چه کسی اصلاحش می‌کند؟

امروز ویدئوی نتیجه را به یک Data product تبدیل می‌کنیم.

هدف این نیست که به M2Lab اعتماد کنید. هدف این است که بتوانید M2Lab را بررسی کنید.»

**در یک جمله:** اعتماد یک نشان نیست که بدهند؛ یک مسیر است که باید بشود طی‌اش کرد.

**روی تصویر:**

`TRUST IS A PATH, NOT A BADGE.`

### 01:10–03:20 — پنج لایهٔ انتشار

**تصویر:** پنج Layer عمودی. هرکدام با کلیک یک نمونه واقعی از قسمت ۸ باز می‌کند.

**متن گفتاری:**

«Atlas پنج لایه دارد. هرکدام برای یک مخاطب.

لایهٔ Result، برای نگاه سریع: برآورد اصلی، بازه، Guardrail، هزینه، زمان، تاریخ و N.

لایهٔ Method، برای فهمیدن طراحی: Specification، Dataset card، Protocol، Metric registry و Analysis plan.

لایهٔ Evidence، برای بازرسی: Case، Run، Claim، برچسب، منبع و خروجی خام.

لایهٔ Decision، برای استفاده: در کدام سناریو کدام گزینه، با چه هشداری؟ و کجا شواهد کافی نیست؟

لایهٔ Governance، برای بعد از انتشار: نسخه، تغییر، اعتراض، تعارض، اصلاح و اجرای مجدد.

حالا نکتهٔ اصلی. بیشتر Leaderboardها لایهٔ اول را خوب می‌سازند. بعضی Methodology هم دارند.

اما اعتماد جای دیگری ساخته می‌شود: وقتی این لایه‌ها واقعاً به هم لینک باشند.

کاربر عادی باید در سی ثانیه یافته را بفهمد. بازرس باید بتواند تا Run خام پایین برود.

و این دو تجربه نباید دو حقیقت متفاوت نشان دهند.»

**در یک جمله:** پنج لایه برای پنج نیاز — و اعتماد از لینک‌بودنشان می‌آید، نه از وجودشان.

### 03:20–05:40 — Rank، Verdict نیست

**تصویر:** Medal table به Result profile تبدیل می‌شود. Rank 1/2 به Tier A یا `UNRESOLVED` بدل می‌شود.

**متن گفتاری:**

«یک ردیف در Atlas فقط اسم و امتیاز کلی نیست.

نسخهٔ ابزار دارد. برآورد اصلی. بازه. Guardrail. هزینهٔ میانه. زمان میانه و p95. تعداد Runهای معتبر. و تاریخ آخرین تست.

حالا یک قاعدهٔ رابط کاربری. اگر اختلاف از آستانهٔ عملی رد نشده، یا عدم‌قطعیت جدایی روشنی نمی‌دهد، رابط کاربری حق ندارد با مدال به شما بگوید برنده داریم.

به‌جایش Tier نشان می‌دهیم، یا `UNRESOLVED`.

Composite هم فقط یک View کمکی است. وزن‌ها دیده می‌شوند و انتخابگر سناریو تغییرشان می‌دهد.

و نمای پیش‌فرض همان Primary metric فریز‌شده است. نه آن وزنی که جذاب‌ترین برنده را می‌سازد.

سه الگوی بد را هم حذف کرده‌ایم.

رتبهٔ بزرگ با هشدار ریز. رنگ سبز و قرمز بدون آستانهٔ مشخص. و اعشاری بیشتر از دقت داده.

روی این آخری تأکید کنم. اگر Rubric انسانی یک تا پنج است و نمونه محدود، نوشتن `84.372` علم اضافه نمی‌کند.

دقت نمایشی، عدم‌قطعیت واقعی را پنهان می‌کند.»

**در یک جمله:** وقتی داده اجازهٔ اعلام برنده را نمی‌دهد، رابط کاربری هم نباید برنده نشان دهد.

### 05:40–07:40 — Method باید خواندنی باشد، نه فقط موجود

**تصویر:** چهار Card: Specification، Dataset، Protocol، Metric. کلیک روی هر Card Version و Change باز کند.

**متن گفتاری:**

«Methodology نباید شما را مجبور کند از روی کد حدس بزنید ما چه کرده‌ایم.

چهار سند، هرکدام یک کار.

Specification می‌گوید تصمیم، کاربر، Task، دامنه، Baseline و مرز ادعا چه بوده.

Dataset card می‌گوید Caseها از کجا آمده‌اند، چه بخش‌هایی پوشش دارند، چه چیزی کم‌پوشش است، Ground truth چطور ساخته شد، و چه ریسکی برای آلودگی باقی مانده.

Protocol نسخه، Prompt، دسترسی، بودجه، Retry، برچسب‌گذاری، تصادفی‌سازی و انحراف‌ها را ثبت می‌کند.

Metric registry برای هر معیار می‌گوید: واحد، فرمول، روش تجمیع، قاعدهٔ داده‌های گمشده، آستانه، روش عدم‌قطعیت و سوگیری‌های شناخته‌شده.

Datasheets، Model Cards و BenchmarkCards همه یک اصل مشترک دارند: نتیجه بدون زمینه، برای انتخاب مسئولانه کافی نیست.

یک خلاصهٔ مدیریتی شش‌جمله‌ای هم داریم. اما سه محدودیت اصلی، همان صفحهٔ اول دیده می‌شوند.

چون هشدار نباید جایزهٔ کسی باشد که تا آخر PDF دوام آورده است.»

**در یک جمله:** روش باید خواندنی باشد، نه فقط موجود — و محدودیت‌ها باید صفحهٔ اول باشند، نه پاورقی.

### 07:40–09:40 — Evidence را نشان بده، اما همه‌چیز را منتشر نکن

**تصویر:** Score → Case → Claim → Source. در یک Case، Source private/restricted است و Derived evidence با دلیل نمایش داده می‌شود.

**متن گفتاری:**

«روی امتیاز اصلی کلیک می‌کنید و Caseهای سازنده‌اش باز می‌شوند.

یک Case را انتخاب می‌کنید. Claim، Citation و برچسب را می‌بینید. Snapshot منبع نشان می‌دهد ارزیاب دقیقاً چه دیده است.

اما شفافیت نامحدود نیست. و این را باید صریح گفت.

این‌ها منتشر نمی‌شوند: Credential، دادهٔ شخصی، متن کامل دارای Copyright، محتوای امنیتی، و پاسخ Holdout.

اگر شرایط استفادهٔ یک ابزار انتشار خروجی خام را ببندد، به‌جایش برچسب مشتق، Metadata، هش و دلیل محدودیت می‌آید.

یک تذکر دربارهٔ هش. هش نمی‌گوید ادعا درست است. فقط کمک می‌کند بفهمیم فایل عوض شده یا نه.

و برای هر بخش یک `Publication level` (سطح انتشار) می‌گذاریم: reproducible، partially reproducible، یا auditable only.

محصول بسته روی وب زنده شاید هیچ‌وقت دقیقاً بازتولید نشود. برچسب "auditable only" شکست نیست. برچسب صادقانهٔ یک محدودیت واقعی است.

و قاعدهٔ آخر: چیزی که نمی‌شود عمومی کرد، باز هم باید در Governance مستند باشد. نه اینکه انگار اصلاً وجود نداشته.»

**در یک جمله:** همه‌چیز را نمی‌شود منتشر کرد، ولی هر چیزی که منتشر نمی‌شود باید نامش جایی نوشته شود.

### 09:40–11:45 — هر Result تاریخ انقضا دارد

**تصویر:** Timeline نسخه‌ها؛ Tool update، Dataset minor، Protocol major. مقایسهٔ شکسته با خط قرمز.

**متن گفتاری:**

«یک محصول AI امروز، با همان محصول سه ماه بعد یکی نیست.

نتیجهٔ بدون نسخه و تاریخ، خیلی زود تبدیل به یک ادعای بی‌زمان می‌شود.

ما چهار ساعت جدا داریم: Benchmark، Dataset، Protocol و Tool.

Patch یعنی اصلاحی که معنا را عوض نمی‌کند. Minor یعنی Case یا Metric سازگار اضافه شده.

Major جای دیگری است. وقتی ادعا، توزیع یا نحوهٔ امتیازدهی عوض شود. آن‌وقت مقایسهٔ مستقیم قبل و بعد می‌شکند.

NIST AI 800-2 هم همین را توصیه می‌کند: نسخه‌گذاری، نگهداری Log کامل، و ثبت نسخهٔ دقیق مدل. یک `Breaking change` (تغییر ناسازگار) باید کاملاً پیدا باشد.

اجرای مجدد ما فصلی است. هشتاد درصد Caseهای لنگر برای دیدن روند می‌مانند. بیست درصد تازه می‌شوند.

اگر ابزاری نسخهٔ بزرگی منتشر کرد، اجرای خارج از نوبت ممکن است. ولی نتایج با تاریخ‌های دور، بدون Badge، در یک جدول قاطی نمی‌شوند.

و مهم‌ترین قاعدهٔ این بخش. اگر امتیاز تغییر کرد، سه فرضیه داریم: ابزار عوض شده، Dataset عوض شده، یا Protocol عوض شده.

تا وقتی طراحی اجازهٔ جداکردن این سه را ندهد، فقط مشاهده را می‌گوییم: نتیجه تغییر کرد.

علت را حدس نمی‌زنیم.»

**در یک جمله:** خط روند فقط جایی کشیده می‌شود که روش و داده با هم سازگار باشند.

### 11:45–13:50 — اعتماد بعد از Publish شروع می‌شود

**تصویر:** Issue با `claim_id` ثبت می‌شود؛ Statusها حرکت می‌کنند؛ Correction نسخهٔ قبلی را Superseded می‌کند نه Delete.

**متن گفتاری:**

«یک Benchmark منتشرشده باید بشود بهش اعتراض کرد. وگرنه اعلامیه است، نه پژوهش.

هر اعتراض با شناسهٔ Case، Run یا Claim ثبت می‌شود. وضعیتش یکی از این‌هاست: باز، در حال بررسی، پذیرفته، رد شده، یا اصلاح‌شده.

تصمیم و دلیلش عمومی می‌ماند — مگر جایی که حریم خصوصی مانع شود.

اصلاح‌ها سه شدت دارند.

Minor: مثل یک غلط تایپی، بدون اثر روی امتیاز.

Material: مثل یک برچسب یا هزینهٔ اشتباه که Metric را تغییر می‌دهد.

Critical: مثل نشت یا پیکربندی غلط که ادعای اصلی را زیر سؤال می‌برد.

دو مورد آخر یک بنر عمومی می‌گیرند، با تاریخ، یادداشت اثر و نسخهٔ جدید. و نسخهٔ قبلی پاک نمی‌شود — `Superseded` (جایگزین‌شده) می‌شود.

سازندهٔ ابزار حق دارد شواهد بدهد و خطای پیکربندی را نشان دهد. این حق واقعی است.

اما یک نتیجهٔ ناخوشایند، فقط به‌خاطر ناخوشایندبودنش حذف نمی‌شود.

و اگر رابطهٔ مالی یا اسپانسری وجود دارد، قبل از هر توصیه‌ای افشا می‌شود. اسپانسر می‌تواند صحت واقعیت‌ها را از قبل ببیند. حق تغییر حکم را ندارد.

اعتماد یعنی امکان اصلاح — به‌علاوهٔ حافظه‌ای که یادش می‌ماند چه چیزی اصلاح شد.»

**در یک جمله:** انتشار پایان کار نیست؛ از همان‌جا مسئولیت اصلاح شروع می‌شود.

### 13:50–15:50 — Recommendation با Scenario شروع می‌شود

**تصویر:** چهار Scenario card. انتخاب هرکدام Tool، Evidence، Trade-off و Caveat را تغییر دهد.

**متن گفتاری:**

«کاربر برای رتبه نیامده. برای تصمیم آمده.

پس هر توصیه چهار بخش دارد: سناریو، گزینهٔ ترجیحی، شواهد، و هشدار.

مثال بزنم.

برای یک Founder تک‌نفره با بودجهٔ محدود، ابزار `[X]` شاید بهترین ارزش را در Dataset ما داشته باشد. هشدارش: Citationهای حساس باید بازبینی شوند.

برای تیمی که گزارش مستقیم وارد تصمیم سرمایه‌گذاری می‌شود، توصیه می‌تواند `NONE FOR UNATTENDED USE` باشد. یعنی هیچ‌کدام، بدون نظارت.

برای بازار کم‌داده، ابزار `[Y]` کمترین افت را داشت — ولی زمان بیشتری می‌برد.

و اگر برای فارسی نمونه نداریم، رابط کاربری توصیهٔ فارسی تولید نمی‌کند.

`INSUFFICIENT EVIDENCE` یک صفحهٔ خالی نیست. یک نتیجهٔ معتبر است.

توصیهٔ خوب معامله را حذف نمی‌کند. صاحب تصمیم می‌تواند وزن‌ها را عوض کند — اما Profile نتیجه و تحلیل حساسیت همان‌جا سر جایشان می‌مانند.»

**در یک جمله:** «شواهد کافی نیست» یک جواب است، نه نبودِ جواب.

### 15:50–17:30 — ساخت M2Lab Benchmark Atlas

**تصویر:** Product map سه نوع صفحه.

**متن گفتاری:**

«این فصل نباید فقط یک Playlist بماند. Benchmark Atlas سه نوع صفحه دارد.

اول، Benchmark Card برای روش‌های موجود — MMLU-Pro، SWE-bench، LMArena و Benchmarkهای Agent.

هر Card این‌ها را دارد: ادعا، Task، Dataset، Metric، نقطهٔ قوت، Failure، ریسک آلودگی و ارتباط با دنیای واقعی.

دوم، صفحهٔ Benchmark خودمان: روش، Dataset، Protocol، نتیجه، شواهد، اعتراض‌ها و اجرای مجدد.

سوم، راهنمای تصمیم. کاربر از Use case خودش شروع می‌کند و می‌بیند کدام Benchmark به دردش می‌خورد و کدام نه.

این یک Data product است، نه آرشیو ویدئو.

هر قسمت یک Card را عمیق‌تر می‌کند. هر اجرا تاریخچه می‌سازد. هر اصلاح کیفیت شواهد را بالا می‌برد.

و مزیت M2Lab تعداد مدل‌هایی که بررسی کرده نیست. مزیتش سه چیز است: مسیر قابل‌ردیابی روش، تحلیل Failure، و تبدیل Benchmark به تصمیم محصولی.»

**در یک جمله:** خروجی این فصل یک فهرست ویدئو نیست؛ یک محصول داده‌ای است که بقیه می‌توانند برش دارند.

### 17:30–18:40 — پایان فصل

**تصویر:** Montage نه‌قسمتی؛ هر قسمت یک جزء را روشن می‌کند.

**متن گفتاری:**

«فصل را با یک فرمول شروع کردیم:

Task به‌علاوهٔ Dataset، به‌علاوهٔ Protocol، به‌علاوهٔ Metric، به‌علاوهٔ Interpretation.

حالا دو مسئولیت دیگر هم اضافه می‌کنیم: عدم‌قطعیت و Governance.

بگذارید نُه قسمت را در نُه جمله مرور کنم.

قسمت اول امتیاز را شکست. دوم خانوادهٔ شواهد را انتخاب کرد. سوم سؤال را فریز کرد. چهارم جهان تست را ساخت. پنجم تصمیم گرفت چه چیزی مهم است. ششم اجرا را کنترل کرد. هفتم روش را بازرسی کرد. هشتم شواهد واقعی تولید کرد. و نهم نتیجه را قابل‌بررسی و قابل‌اصلاح کرد.

یک Benchmark خوب نمی‌گوید "این حقیقت نهایی است".

می‌گوید: در این دامنه، با این داده و این Protocol، این شواهد را داریم. این مقدار عدم‌قطعیت باقی است. و اینجا جایی است که می‌توانید خودتان بررسی کنید.

مرحلهٔ بعد، Atlas است. به‌جای توضیح سطحی Benchmarkها، هرکدام را با همین قرارداد باز می‌کنیم: Claim، Evidence، Stress test، Verdict و Build.

انتخاب اول میان سه مسیر است: Knowledge benchmark، Coding benchmark یا Agent benchmark. رأی شما Winner را تعیین نمی‌کند؛ تعیین می‌کند کدام Measurement system را اول باز کنیم.»

**در یک جمله:** نُه قسمت پیش یک معادله بود؛ حالا یک شیء ساخته‌شده است که دیگری می‌تواند برش دارد، بررسی‌اش کند و دوباره اجرایش کند.

**پایان روی تصویر:**

`MEASURED, NOT ASSUMED.`

---

## 6. معماری صفحهٔ عمومی

| لایه | Componentهای الزامی |
|---|---|
| Result | Profile، primary estimate، CI/rank spread، guardrail، N، date، scenario selector |
| Method | Spec، dataset card، protocol، metric registry، analysis plan، deviations |
| Evidence | Case/run/claim trace، source، label، raw/derived output، publication level |
| Decision | Recommendation، caveat، trade-off، insufficient-evidence zones |
| Governance | Versions، changelog، issue tracker، conflicts، corrections، rerun schedule |

### مدل دادهٔ حداقلی

```text
benchmark_id
benchmark_version
dataset_version
protocol_version
result_release_id
tool_id / tool_version
case_id / run_id / claim_id / citation_id
metric_id / estimate / interval / n
guardrail_status
evidence_uri / publication_level
issue_id / correction_id / supersedes
tested_at / published_at / next_rerun
```

---

## 7. Publication Checklist

### Result

- [ ] N، Date، Tool version و Protocol version کنار Result است.
- [ ] Point estimate با Uncertainty و Practical threshold همراه است.
- [ ] Guardrail جداست.
- [ ] Distribution، Worst group و Failure rate قابل مشاهده‌اند.
- [ ] Rank نامطمئن با Tier/Unresolved جایگزین شده است.

### Method

- [ ] Specification و Claim boundary عمومی‌اند.
- [ ] Dataset card Coverage و Missing segments را می‌گوید.
- [ ] Protocol شامل Prompt، Budget، Retry، Annotation و Deviation است.
- [ ] Metric registry Unit، Formula، Missing rule و Bias را توضیح می‌دهد.
- [ ] Analysis plan و Post-lock changes مشخص‌اند.

### Evidence

- [ ] هر Score حداقل به Case و Run trace می‌شود.
- [ ] Critical claimها Source/Label دارند.
- [ ] Raw/derived publication level روشن است.
- [ ] Privacy، License و Security review انجام شده است.
- [ ] Holdout/Restricted evidence دلیل عدم انتشار دارد.

### Decision

- [ ] Recommendation با Scenario شروع می‌شود.
- [ ] Evidence و Caveat کنار Preferred option هستند.
- [ ] Insufficient evidence قابل انتخاب/نمایش است.
- [ ] Unattended/high-risk use صریحاً محدود شده است.

### Governance

- [ ] Changelog و Semantic version وجود دارند.
- [ ] Breaking comparability Badge دارد.
- [ ] Issue/Appeal path عمومی است.
- [ ] Correction severity و SLA تعریف شده‌اند.
- [ ] Conflict/Sponsor/Affiliate disclosure واضح است.
- [ ] Rerun/retirement schedule وجود دارد.

---

## 8. Correction Policy پیشنهادی

| Severity | مثال | اقدام | هدف زمانی پیشنهادی |
|---|---|---|---|
| Minor | typo، link شکسته | Patch + changelog | ۷ روز |
| Material | label/cost اشتباه با اثر Metric | Banner + corrected release + impact note | ۷۲ ساعت پس از تأیید |
| Critical | leakage/misconfiguration/method failure | Suspend claim + public incident note + rerun decision | ۲۴ ساعت برای Banner اولیه |

این SLAها Target داخلی M2Lab هستند، نه Standard عمومی.

---

## 9. طراحی تجربهٔ بصری

### صحنهٔ اصلی: Evidence Atlas

- همان زبان `Editorial Benchmark Atlas` انتخاب‌شده؛
- Graphite، warm off-white و signal amber؛
- بدون Gradient، Glassmorphism، Card clutter یا Slide controls؛
- Model/Tool row قابل انتخاب؛
- Inspector واقعی با `PROFILE / SCORES / LIMITS / SOURCES`؛
- Evidence drill-down بدون ترک صفحه؛
- Version timeline و Correction banner؛
- Focus mode برای ضبط؛
- Mobile: Model index به Selector فشرده تبدیل شود.

### Interactionهای امضادار

1. `SHOW EVIDENCE`: Score به Claim/Source باز شود.
2. `SHOW UNCERTAINTY`: Rank به Tier/range تبدیل شود.
3. `CHANGE SCENARIO`: Recommendation و Weight عوض شود؛ Raw profile ثابت بماند.
4. `VIEW VERSION`: Result قدیم و جدید با Breaking badge مقایسه شوند.
5. `REPORT AN ISSUE`: Form با case/run/claim ID پر شود.
6. `WHY NOT PUBLIC?`: دلیل محدودیت Evidence را نشان دهد.

---

## 10. سایت‌هایی که باید نمایش داده شوند

| زمان | سایت | چیزی که نمایش داده می‌شود | کاربرد |
|---|---|---|---|
| 04:50 | Datasheets for Datasets | motivation/composition/use/maintenance | Dataset documentation |
| 05:10 | Model Cards | intended use/evaluation/limitations | Context و subgroup reporting |
| 05:25 | BenchmarkCards | standardized benchmark documentation | انتخاب و Risk benchmark |
| 09:55 | NIST AI 800-2 | versioning + full logs + qualified reporting | مبنای انتشار |
| 10:50 | LMArena Ranking Method | CI و rank spread در UI واقعی | مثال uncertainty-aware display |
| 12:30 | MLCommons benchmark pages | peer review/reproducibility claim | مثال governance سازمانی |
| 15:50 | M2Lab Atlas prototype | پنج لایه و evidence trace | Build نهایی |

---

## 11. چک‌لیست علمی قبل از ضبط

- [ ] تمام Resultهای قسمت ۸ Data-locked هستند.
- [ ] Rank فقط طبق Rule فصل نمایش داده می‌شود.
- [ ] CI/rank spread با Robustness کامل یکی نشده است.
- [ ] Reproducibility label اغراق‌آمیز نیست.
- [ ] Method cardها نسخه و Date دارند.
- [ ] Evidence trace حداقل یک مسیر کامل واقعی دارد.
- [ ] Restricted data دلیل و Publication level دارد.
- [ ] Correction نسخهٔ قبلی را پاک نمی‌کند.
- [ ] Sponsor/Affiliate قبل از Recommendation است.
- [ ] Semantic versioning با Comparability علمی اشتباه گرفته نشده است.
- [ ] Drift cause فقط با Evidence نسبت داده می‌شود.
- [ ] Recommendationها Scenario، Evidence و Caveat دارند.
- [ ] Insufficient evidence به‌عنوان Result معتبر نشان داده شده است.
- [ ] پایان فصل وعدهٔ ساخت‌نشده نمی‌دهد؛ Atlas prototype واقعاً قابل کلیک است.

---

## 12. بستهٔ ضبط

### A-roll حذف‌ناپذیر

- پنج لایهٔ Publication؛
- Rank vs Verdict؛
- Publication level؛
- Version/Drift؛
- Correction/Appeal؛
- Scenario recommendation؛
- پایان نه‌قسمتی.

### Screen recording

- Broken leaderboard؛
- Result profile؛
- Evidence drill-down کامل؛
- Dataset/Protocol/Metric card؛
- Version comparison؛
- Issue و Correction flow؛
- Scenario selector؛
- Atlas product map.

### Pattern interrupt

- 00:30: methodology error؛
- 03:20: Medal table collapse؛
- 07:40: Evidence drill-down؛
- 09:40: version timeline؛
- 11:45: public correction؛
- 15:50: Atlas reveal؛
- 17:30: season montage.

---

## 13. CTA نهایی

> «Atlas را باز کنید و از یک Result تا یک Source پایین بروید. اگر Trace قطع بود، Issue ثبت کنید. سپس انتخاب کنید فصل بعد کدام Measurement system را اول کالبدشکافی کند: Knowledge، Coding یا Agent.»

**Comment prompt:**

> برای اعتماد به یک Leaderboard، اولین چیزی که بعد از Score می‌خواهید ببینید چیست: Case خام، Protocol، Uncertainty، Version history یا Correction log؟

---

## 14. منابع اصلی این قسمت

1. NIST, [Practices for Automated Benchmark Evaluations of Language Models — NIST AI 800-2 IPD](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf), January 2026.
2. NIST, [Expanding the AI Evaluation Toolbox with Statistical Models — NIST AI 800-3](https://www.nist.gov/publications/expanding-ai-evaluation-toolbox-statistical-models), February 2026.
3. Gebru et al., [Datasheets for Datasets](https://arxiv.org/abs/1803.09010), 2018/2021.
4. Mitchell et al., [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993), 2018/2019.
5. Sokol et al., [BenchmarkCards: Standardized Documentation for Large Language Model Benchmarks](https://openreview.net/forum?id=b2IJBWhGFu), NeurIPS 2025.
6. LMArena, [Arena’s Ranking Method](https://news.lmarena.ai/ranking-method/), 2025–2026.
7. LMArena, [Arena-Rank](https://news.lmarena.ai/arena-rank/), open methodology package.
8. MLCommons, [Benchmark Work](https://mlcommons.org/benchmarks/).
9. Crisan et al., [Interactive Model Cards](https://arxiv.org/abs/2205.02894), 2022.

---

## 15. خطاهای ممنوع

- ساخت Leaderboard بدون Evidence trace؛
- نمایش Rank قطعی در حالت Unresolved؛
- پنهان‌کردن N، Date، Version یا Guardrail؛
- ادعای Full reproducibility برای Product بسته/وب زنده؛
- انتشار داده برخلاف Privacy/License/Terms؛
- حذف نسخهٔ اشتباه پس از Correction؛
- مخلوط‌کردن Resultهای ناسازگار پیش/پس از Breaking change؛
- Recommendation بدون Scenario و Caveat؛
- تبدیل Insufficient evidence به Empty state نامرئی؛
- استفاده از Trust badge به‌جای مسیر Evidence؛
- پایان فصل بدون Rerun و Correction policy.

