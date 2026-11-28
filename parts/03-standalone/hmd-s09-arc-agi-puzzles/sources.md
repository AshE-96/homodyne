# HMD-S09 · منابع

> همهٔ منابع ۲۸ نوامبر ۲۰۲۶ باز و خوانده شدند، مگر جایی که نوشته شده. نقل‌قول‌ها کوتاه‌اند و فقط برای نقد و گزارش خبری.
> برچسب‌ها: ✅ از متن منبع خوانده شد · 🔁 از متن یک منبع دیگر نقل شده (منبع اصلی باز نشد) · ⚠️ اختلاف یا ابهام · [VERIFY] پیش از استفاده روی دوربین دوباره ببین.
> **جدول رسمی (R12) هر هفته عوض می‌شود.** عددهای آن «تا ۲۸ نوامبر ۲۰۲۶» هستند؛ روز ضبط (پیش از ۱۳ مه ۲۰۲۷) دوباره بخوان (`prep-fa.md` §۳).

## منبع‌های اصلی

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| R01 | François Chollet, «On the Measure of Intelligence», arXiv 1911.01547 (v1 5 Nov 2019، v2 25 Nov 2019); سرصفحه: Google, Inc. — https://arxiv.org/abs/1911.01547 | §II.2.1: «The intelligence of a system is a measure of its skill-acquisition efficiency over a scope of tasks, with respect to priors, experience, and generalization difficulty.»؛ چکیده: با داده یا پیش‌دانستهٔ بی‌حد می‌شود مهارت «خرید»؛ مثال شطرنج (§I)؛ §III.1.1: ۴۰۰ آموزشی، ۶۰۰ ارزیابی (۴۰۰ عمومی + ۲۰۰ خصوصی)، به‌طور میانگین ۳٫۳ نمونه، معمولاً ۱ آزمون (گاهی ۲ یا ۳)، ۳ فرصت؛ §III.1.2 دانش پایه: Objectness، Goal-directedness، Numbers and Counting، Basic Geometry and Topology، از نظریهٔ Core Knowledge («priors that humans are born with»)؛ §III.1.4: هر معما را دست‌کم یکی از سه آدم «high-IQ» حل کرده | ✅ (متن PDF با pdftotext؛ بازبینی دوباره ۲۸ نوامبر ۲۰۲۶) |
| R02 | ARC-AGI-1، github.com/fchollet/ARC-AGI (commit 3990304، ۴ آوریل ۲۰۲۵): README و LICENSE | ۴۰۰ آموزشی و ۴۰۰ ارزیابی در مخزن؛ «3 trials» برای هر ورودی آزمون؛ فقط پاسخ دقیق؛ **مجوز Apache-2.0** (Copyright 2019 Francois Chollet) | ✅ ⚠️ کارت ایده «MIT» نوشته؛ فایل LICENSE مخزن Apache-2.0 است |
| R03 | ARC-AGI-2، github.com/arcprize/ARC-AGI-2 (commit f3283f7، ۱۵ مه ۲۰۲۵): readme و LICENSE | ۱٬۰۰۰ آموزشی و ۱۲۰ ارزیابی عمومی؛ «Average human performance on these tasks in our test sample was 66%»؛ هر معمای ارزیابی را دست‌کم ۲ نفر در ۲ فرصت یا کمتر حل کرده‌اند؛ دو مجموعهٔ نیمه‌خصوصی و خصوصی بیرون از مخزن؛ «2 trials» برای هر ورودی آزمون؛ شبکه ۱×۱ تا ۳۰×۳۰، رقم ۰ تا ۹؛ **Apache-2.0** (Copyright 2019 ARC Prize Foundation) | ✅ ⚠️ readme در یک جا هنوز «3 trials» دارد (بخش قالب فایل)؛ بخش «Task success criterion» دو فرصت می‌گوید |
| R04 | ARC Prize Foundation, «ARC-AGI-2: A New Challenge for Frontier AI Reasoning Systems», arXiv 2505.11831 (HTML v2) | §4.3: ۴۰۷ شرکت‌کننده در ۵۱۵ جلسه؛ ۸٬۲۷۷ از ۱۳٬۴۰۵ تلاش درست (۶۲٪)؛ §5: «100% of ARC-AGI-2 tasks were solved by at least two independent, non-expert human testers»؛ §7.1: میانگین ۲٫۷ دقیقه برای هر معما؛ §4.1: پرداخت پایهٔ ۱۱۵ تا ۱۵۰ دلار برای ۹۰ دقیقه + ۵ دلار برای هر معمای درست؛ جدول ۱ (نیمه‌خصوصی، ۱۴ مه ۲۰۲۵): o3 (Medium) ARC-AGI-2 **۳٫۰٪** و ARC-AGI-1 ۵۳٪ | ✅ |
| R05 | ARC Prize, «OpenAI o3 Breakthrough High Score on ARC-AGI-Pub», 20 Dec 2024 (به‌روزرسانی ۱۶ آوریل ۲۰۲۵) — https://arcprize.org/blog/oai-o3-pub-breakthrough | نیمه‌خصوصی، ۱۰۰ معما: **۷۵٫۷٪ با ۲۶ دلار برای هر معما** (کل ۲٬۶۸۰)؛ **۸۷٫۵٪ با ۴٬۵۶۰ دلار برای هر معما** (کل ۴۵۶٬۰۰۰؛ «172x»)؛ عمومی ۴۰۰: ۸۲٫۸٪ و ۹۱٫۵٪؛ «you could pay a human to solve ARC-AGI tasks for roughly $5 per task»؛ «Passing ARC-AGI does not equate to achieving AGI»؛ OpenAI تأیید کرده o3 منتشرشده با نسخهٔ آزموده فرق دارد | ✅ ⚠️ هزینه‌ها بازنگری شده‌اند (۲۴ مارس ۲۰۲۵: قیمت o1-pro؛ ۱۰ دسامبر ۲۰۲۵: قیمت o3-pro، ۸۰ دلار برای هر میلیون توکن؛ عدد اولیهٔ پست ۲۰ دلار / ۲٬۰۱۲ دلار بود)، یعنی برآوردند، نه صورت‌حساب؛ ما عدد امروزِ صفحه را می‌آوریم. R04 §1.2 برآوردهای دیگری دارد (۷۶٪ با حدود ۲۰۰ دلار، ۸۸٪ با حدود ۲۰٬۰۰۰ دلار)؛ روی دوربین R05 |
| R06 | arcprize.org/arc-agi/1 | ARC-AGI-1 از ۲۰۱۹؛ مجموعهٔ نیمه‌خصوصی ۱۰۰ معما (از میانهٔ ۲۰۲۴) و خصوصی ۱۰۰؛ «تا اواخر ۲۰۲۴ حل‌نشده» | ✅ |
| R07 | arcprize.org/arc-agi/2 | ۱٬۰۰۰ / ۱۲۰ / ۱۲۰ / ۱۲۰؛ بیش از ۴۰۰ نفر در سن‌دیگو، اوایل ۲۰۲۵؛ سه سختی تازه: symbolic interpretation، compositional reasoning، contextual rule application؛ «پیشرفت روی ARC-AGI-1 تا اواخر ۲۰۲۴ کند بود، تا وقتی روش‌های test-time adaptation آمد» | ✅ |
| R08 | ARC Prize, «ARC Prize 2025 Results & Analysis» — https://arcprize.org/blog/arc-prize-2025-results-analysis ؛ و arcprize.org/competitions/2025 | **۱٬۴۵۵ تیم**، ۱۵٬۱۵۴ ارسال؛ اول NVARC **۲۴٫۰۳٪** روی مجموعهٔ خصوصی ARC-AGI-2 با **۰٫۲۰ دلار برای هر معما**؛ دوم ARChitects ۱۶٫۵۳٪، سوم MindsAI ۱۲٫۶۴٪؛ جایزهٔ بزرگ بی‌برنده؛ Claude Opus 4.5 (Thinking 64k) ۳۷٫۶٪ با ۲٫۲۰ دلار؛ Poetiq روی Gemini 3 Pro ۵۴٪ با حدود ۳۰ دلار؛ دربارهٔ نشت داده: «We believe this is happening to ARC-AGI-1 and ARC-AGI-2 - either incidentally or intentionally, we cannot tell.» | ✅ |
| R09 | arcprize.org/competitions/2026 و /competitions/2026/arc-agi-2 | ARC Prize 2026: «$2M in prizes. 3 tracks» (ARC-AGI-3، ARC-AGI-2، مقاله)؛ شروع ۲۵ مارس، پایان ارسال ۲ نوامبر، **اعلام نتیجه ۴ دسامبر ۲۰۲۶**؛ «No internet access during evaluation»؛ هدف ۸۵٪ روی مجموعهٔ خصوصی ARC-AGI-2 در حد کارایی کگل؛ دو پیش‌بینی برای هر ورودی؛ کد برنده‌ها با مجوز آزاد (CC0 یا MIT-0)؛ آخرین سالِ ARC-AGI-2 در کگل | ✅ ⚠️ صفحه سقف سخت‌افزار را نمی‌گوید (به صفحهٔ کگل ارجاع می‌دهد) |
| R10 | ARC Prize, «ARC-AGI-3 launch», 25 Mar 2026 — https://arcprize.org/blog/arc-agi-3-launch | «Humans score 100%»؛ «Frontier AI scores 0.51%»؛ صدها محیط نوبتی و هزاران مرحله | ✅ |
| R11 | ARC Prize Foundation, ARC-AGI-3 technical paper, arXiv 2603.24621 (v1 24 Mar، v2 17 Apr 2026) | ۲۵ بازی عمومی، ۵۵ نیمه‌خصوصی، ۵۵ خصوصی؛ شبکهٔ ۶۴×۶۴ با ۱۶ رنگ؛ نمرهٔ RHAE: هر مرحله `min(1.15, h/a)²` (h = میانهٔ بالای تعداد حرکت آدم‌ها، a = حرکت‌های مدل)، وزن مرحله‌ها خطی، سقف حرکت ۵ برابر میانهٔ آدم؛ ۱۰ نفر برای هر محیط، محیط فقط اگر دست‌کم ۲ نفر حلش کردند؛ ۴۸۶ شرکت‌کننده؛ هنگام انتشار: Opus 4.6 ۰٫۵۰٪، Gemini 3.1 Pro ۰٫۴۰٪، GPT-5.4 ۰٫۲۰٪ | ✅ |
| R12 | ARC Prize leaderboard — https://arcprize.org/leaderboard (خوانده‌شده ۲۸ نوامبر ۲۰۲۶) | GPT-6.2 Astra (۱۷ نوامبر ۲۰۲۶): ARC-AGI-1 ۹۸٫۵٪، **ARC-AGI-2 ۹۵٫۸٪**، ARC-AGI-3 Standard **۷۰٫۳٪** / Provider adapter **۱۰۰٫۰٪**؛ Claude Fable 5.2 (۹ نوامبر): ۹۸٫۵ / ۹۳٫۸ / **۸۱٫۲٪** / ۹۷٫۷٪؛ Gemini 4 Carbon (۱۰ نوامبر): ۹۸٫۵ / ۹۴٫۲ / ۶۵٫۱ / ۹۹٫۱ | ✅ ⚠️ صفحه کوتاه‌شده خوانده شد (۷۹ از ۱۲۷ ردیف)؛ ستون «Cost» (مثلاً ۲۴٫۲ هزار دلار) تعریف نشده؛ کنار ستون Score (= ARC-AGI-3 Standard) است و با «۱۹ ورودی بالای سقف ۱۰٬۰۰۰ دلار برای هر اجرا»ی Epoch (R13) جور است، پس احتمالاً کل اجرای ARC-AGI-3 است؛ برای ARC-AGI-2 هیچ هزینه‌ای روی جدول نیست → روی دوربین نمی‌آوریم [VERIFY]. صفحه مجموعهٔ ارزیابی را نمی‌گوید؛ «نیمه‌خصوصی» از سیاست آزمون ARC Prize و R11 §4.3 است |
| R13 | Epoch AI, «ARC-AGI-3 benchmark review», 30 Oct 2026 — https://epoch.ai/benchmarks/arc-agi-3/review | حکم «Flawed»؛ نمره «واقعاً درصد نیست»؛ مهار استاندارد استدلال را بعد از هر حرکت دور می‌ریزد و تاریخچه را در ۱۷۵٬۰۰۰ نویسه می‌بُرد؛ هر دو مهار شبکه را به شکل **متن** می‌فرستند؛ GPT-6 Astra (max) از ۶۲٫۷٪ به ۹۸٫۶٪ با مهار شرکت؛ Provider Adapter از ۳ سپتامبر ۲۰۲۶ روی جدول؛ ۱۹ ورودی بیش از سقف ۱۰٬۰۰۰ دلار، تا **۴۹٬۸۰۰ دلار**؛ برآورد نمرهٔ آدم معمولی روی بازی‌های عمومی **حدود ۴۸٪**؛ دستور سیستم در ۲۰ مه ۲۰۲۶ بدون شمارهٔ نسخهٔ تازه عوض شد | ✅ |
| R14 | docs.arcprize.org | `pip install arc-agi`؛ `ARC_API_KEY` اختیاری؛ «If no key is provided, an anonymous key will be used»؛ کلید ثبت‌شده بازی‌های عمومی را باز می‌کند | ✅ مجوز بازی‌ها گفته نشده؛ مخزن‌های github.com/arcprize/arc-agi و ARC-AGI-3-Agents: MIT (GitHub API، ۲۸ نوامبر ۲۰۲۶، فقط کد) |
| R18 | arcprize.org/terms (به‌روزرسانی ۳ ژوئن ۲۰۲۴) | مجوز شخصی و غیرتجاری؛ «publicly displayed» و استفادهٔ تجاری بدون اجازهٔ کتبی ممنوع | ✅ → ضبط بازی‌ها و اسکرین‌شات سایت فقط با اجازه (team@arcprize.org) |

## زمینهٔ کمکی (روی دوربین نه، یا فقط در یادداشت راوی)

| شناسه | منبع | چه چیزی | وضعیت |
|---|---|---|---|
| R15 | W. Lemes de Oliveira و همکاران, «ARC-AGI-2 Technical Report», arXiv 2603.06590 (فوریهٔ ۲۰۲۶) | محیط کگل: «240 tasks within 12 hours using 4×L4 GPUs»؛ مدل LongT5 با ۲۰۰ میلیون پارامتر حدود ۲۷٪ | ✅ (گزارش یک شرکت‌کننده، نه صفحهٔ رسمی) → در گفتار فقط «بی‌اینترنت، سخت‌افزار محدود» |
| R16 | arcprize.org/competitions/2025 (از نتیجهٔ جست‌وجو) | جایزهٔ بزرگ ۲۰۲۵: دست‌کم ۸۵٪ روی مجموعهٔ خصوصی با کارایی حدود ۲٫۵ دلار برای هر معما | 🔁 [VERIFY] (صفحهٔ بایگانی باز شد ولی این عددها را نداشت) |
| R17 | NVIDIA developer blog دربارهٔ NVARC | مدل ۴ میلیارد پارامتری، داده‌های مصنوعی، حدود ۲۰ سنت برای هر معما؛ ۲۷٫۶۴٪ روی تابلوی عمومی کگل | 🔁 (از نتیجهٔ جست‌وجو) → استفاده نمی‌شود |

## عددهای حساب‌شدهٔ خودمان

| عدد | از کجا |
|---|---|
| شبکهٔ آزمون معمای ۱ = ۴۹ نویسه؛ کل پرامپت معمای ۱ = ۱٬۲۱۵ نویسه | `arc_core.prompt_for`، پنل «How the model sees it» |
| خانهٔ زیری = ۲ × عرض نویسه بعد (۵ ستون → ۱۰؛ ۳۰ ستون → ۶۰) | `arc_core.column_gap` |
| ۳۵ فراخوان، حدود ۱۶٬۶۰۰ نویسه برای هر مدل، سقف هزینه با قیمت احتیاطی حدود ۴۳ دلار | `arc_run.py plan` |
| `solve_fractal.py`: ۶ از ۶ جفت معمای ۲؛ روی معمای ۱ هیچ | `solve_fractal.py`، `arc_live.py --selftest` |
| «بیش از نهصد برابر» | ۴٬۵۶۰ ÷ ۵ = ۹۱۲ (R05) |

## چیزهایی که بیرون ماندند

| ادعا | چرا |
|---|---|
| «بچه حلش می‌کند» | هیچ آزمون رسمی ARC روی کودکان پیدا نکردیم. R04 §4.2 و R11 §5.2 آزمون‌شونده‌ها را «members of the general public»، «diverse professional backgrounds»، با دستمزد جلسه‌ای توصیف می‌کنند؛ سن صریح گفته نشده («بزرگسال» استنباط است). عنوان عوض شد («معمای ARC: آدم حل می‌کند، AI هنوز نه؟»)؛ قاب ۴ فقط دربارهٔ دانش پایهٔ ذاتی (R01) است و قاب ۱۳ مرز را می‌گوید. |
| «AI هنوز نمی‌تواند» | تا ۲۸ نوامبر ۲۰۲۶ غلط است (R12). عنوان با علامت سؤال است و جواب قاب ۱۴ «تقریباً بله، با خرج زیاد» است. |
| ستون Cost جدول (مثلاً ۲۴٫۲ هزار دلار) | معنی‌اش (کل اجرا؟ کدام نسخه؟) روی صفحه روشن نبود. |
| نتیجهٔ ARC Prize 2026 | ۴ دسامبر ۲۰۲۶ اعلام می‌شود؛ پس از اعلام اضافه شود. |
| «ARC-AGI-1 مجوز MIT» (کارت ایده) | LICENSE مخزن Apache-2.0 است (R02). |
| H-ARC و پژوهش‌های دانشگاهی دیگر دربارهٔ نمرهٔ آدم روی ARC-AGI-1 | باز نشد؛ از عدد آن‌ها استفاده نمی‌کنیم. |

## نقل‌قول‌های روی صفحه (ترجمهٔ ما، کوتاه)

| در دک | اصل | منبع |
|---|---|---|
| «هوش یک سیستم، کارایی آن در کسب مهارت است.» | «The intelligence of a system is a measure of its skill-acquisition efficiency…» | R01 §II.2.1 |
| «قبولی در ARC-AGI یعنی رسیدن به AGI نیست.» | «Passing ARC-AGI does not equate to achieving AGI» | R05 |
| «… عمدی یا سهوی، نمی‌توانیم بگوییم.» | «either incidentally or intentionally, we cannot tell» | R08 |
| «واقعاً درصد نیست» | «isn't a true percentage» (بازنویسی Epoch) | R13 |
