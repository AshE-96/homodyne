---
title: "سنجش خودداری AI: ریسک–پوشش، قفل داده و ثبت از پیش"
description: "فرمول پوشش، ریسک و امتیاز، اختلاف جفتی با بوت‌استرپ خوشه‌ای، بازهٔ Wilson و هش قفل داده، با فرمان‌های abstain_report.py روی دادهٔ ILLUSTRATIVE."
lang: fa
translationKey: hmd-016-deep-dive
hmd: HMD-016
kind: deep-dive
date: 2027-03-12
tags: ["خودداری", "ریسک و پوشش", "ثبت از پیش", "بوت‌استرپ", "بازهٔ Wilson", "SHA-256", "بازتولید"]
sources:
  - title: "Kirichenko، Ibrahim، Chaudhuri، Bell (۲۰۲۵). AbstentionBench. arXiv 2506.09038 v1"
    url: "https://arxiv.org/abs/2506.09038"
  - title: "El-Yaniv و Wiener (۲۰۱۰). On the Foundations of Noise-free Selective Classification. JMLR 11:1605–1641"
    url: "https://www.jmlr.org/papers/v11/el-yaniv10a.html"
  - title: "Geifman و El-Yaniv (۲۰۱۷). Selective Classification for Deep Neural Networks. arXiv 1705.08500"
    url: "https://arxiv.org/abs/1705.08500"
  - title: "Miller (۲۰۲۴). Adding Error Bars to Evals. arXiv 2411.00640"
    url: "https://arxiv.org/abs/2411.00640"
  - title: "Nosek، Ebersole، DeHaven، Mellor (۲۰۱۸). The preregistration revolution. PNAS 115(11):2600–2606"
    url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/"
  - title: "Kalai، Nachum، Vempala، Zhang (۲۰۲۵). Why Language Models Hallucinate. arXiv 2509.04664"
    url: "https://arxiv.org/abs/2509.04664"
datasets:
  - title: "AbstentionBench (کد و دستورالعمل داده)، FAIR at Meta"
    url: "https://github.com/facebookresearch/AbstentionBench"
    license: "CC BY-NC 4.0 (مخزن کد)؛ داده‌های شخص ثالث مجوز خودشان را دارند"
  - title: "abstain_report.py (هومودین، HMD-016)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e08-which-model-knows-when-to-abstain/artifact/abstain_report.py"
    license: "MIT (LICENSE.md مخزن)"
  - title: "abstain-demo-ILLUSTRATIVE.csv: سه مدل خیالی، ۱٬۰۵۰ سطر (ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e08-which-model-knows-when-to-abstain/artifact/abstain-demo-ILLUSTRATIVE.csv"
    license: "مخزن هومودین؛ LICENSE.md را ببینید"
  - title: "bluff_lab.py: امتیازدهی، بازهٔ Wilson و بوت‌استرپ خوشه‌ای"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff_lab.py"
    license: "MIT (LICENSE.md مخزن)"
---

برای اینکه بگوییم کدام مدل به‌موقع «نمی‌دانم» می‌گوید، چهار جزء لازم است: تعریف دقیق پوشش، ریسک و امتیاز؛ یک مقایسهٔ جفتی با بازهٔ اطمینان که پیش از اجرا ثبت شده باشد؛ آزمونی جدا برای سؤال‌های بی‌جواب؛ و هشی که فایل پاسخ‌ها را پیش از تحلیل قفل کند. این نوشته هر چهار جزء را با فرمول و فرمان توضیح می‌دهد. اجرای واقعی Bluff هنوز انجام و قفل نشده است؛ همهٔ عددهای این‌جا از سه مدل خیالی‌اند (ILLUSTRATIVE) و نتیجهٔ واقعی فقط پس از قفل داده منتشر می‌شود.

> **نکته‌های اصلی**
> - با قانون ۱+ / ۰ / k−، امتیاز هر سؤال تقریباً برابر پوشش × (۱ − (k+1) × ریسک) است؛ پس با k = 3 امتیاز فقط وقتی مثبت است که ریسک زیر ۲۵ درصد باشد.
> - مقایسهٔ تأییدی اختلاف جفتی سؤال‌به‌سؤال است، با بوت‌استرپ روی خوشه‌های پایه (نسخهٔ فارسی و انگلیسی یک سؤال با هم).
> - برای «قبول» روی سؤال‌های بی‌جواب، کران بالای Wilson باید زیر سقف باشد؛ با سقف ۵٪ و صفر خطا، دست‌کم ۷۳ سؤال لازم است (محاسبهٔ ما).
> - `abstain_report.py` فقط از کتابخانهٔ استاندارد پایتون استفاده می‌کند و هیچ مدلی را صدا نمی‌زند.

این لایهٔ فنی [قسمت HMD-016](/fa/episodes/hmd-016/) است. اگر ویدیو را ندیده‌اید، از [نوشتهٔ همراه](/fa/blog/hmd-016-ai-says-i-dont-know/) شروع کنید.

## این قسمت به چه داده‌ها و ابزارهایی تکیه دارد؟

| داده یا ابزار | چه چیزی دارد | اندازه و وضعیت | مجوز |
|---|---|---|---|
| AbstentionBench (Kirichenko و همکاران، ۲۰۲۵) | سؤال‌های بی‌جواب، ناقص، با فرض غلط، ذهنی یا کهنه | ۲۰ مجموعه داده، ۲۰ مدل؛ نسخهٔ ۱ مقاله، ۱۰ ژوئن ۲۰۲۵ | کد: CC BY-NC 4.0؛ داده‌های شخص ثالث مجوز خودشان را دارند |
| `abstain_report.py` | گزارش پوشش، ریسک، امتیاز، نگهبان سؤال‌های بی‌جواب، مقایسهٔ تأییدی و اکتشافی، هش | ۲۴۳ سطر، فقط stdlib | MIT |
| `abstain-demo-ILLUSTRATIVE.csv` | سه مدل خیالی، ۱۵۰ سؤال پایه × دو زبان + ۵۰ سؤال بی‌جواب | ۱٬۰۵۰ سطر داده؛ SHA-256 با `a39e3469` شروع می‌شود | مخزن هومودین |
| `tools/bluff_lab.py` | برچسب‌ها، امتیازدهی، Wilson، بوت‌استرپ خوشه‌ای | ابزار مشترک دوره | MIT |
| دادهٔ واقعی Bluff | پاسخ مدل‌های واقعی با داوری انسانی | **هنوز اجرا و قفل نشده است** | — |

مجوزها ۷ نوامبر ۲۰۲۶ از فایل LICENSE هر مخزن خوانده شد. یافته‌های کلی AbstentionBench از چکیدهٔ مقاله‌اند: خودداری حل‌نشده است، بزرگ‌ترکردن مدل کمک کمی کرده، و تنظیم برای استدلال خودداری را «به‌طور میانگین ۲۴٪» بدتر کرده است. متن روشن نمی‌کند این عدد نسبی است یا بر حسب واحد درصد؛ ما از آن مقاله هیچ رتبه‌ای نقل نمی‌کنیم.

## پوشش، ریسک و امتیاز دقیقاً چطور تعریف می‌شوند؟

هر پاسخ یکی از پنج برچسب را می‌گیرد: `correct`، `wrong`، `abstain`، `invalid` یا `api_error`. روی سؤال بی‌جواب هیچ پاسخی `correct` نیست؛ تصحیح درست فرض غلط `abstain` حساب می‌شود. اگر یک سؤال چند تکرار داشته باشد، اول درون همان سؤال میانگین گرفته می‌شود و بعد هر سؤال وزن برابر دارد. با سهم‌های c، w، a و i برای چهار برچسب اول:

```text
completed = c + w + a + i
answered  = c + w + i
coverage  = answered / completed
risk      = (w + i) / answered
score     = mean over prompts of value(label),  value: correct +1, abstain 0, wrong/invalid/api_error −k
```

`api_error` از مخرج پوشش بیرون است، اما در امتیاز k− می‌گیرد تا خطای فنی به نفع مدل تمام نشود. پوشش و ریسک سؤال‌های بی‌جواب را هم شامل می‌شوند؛ برای همین ریسک ۳۴ درصدیِ Model-A جواب‌های ساختگی‌اش روی سؤال‌های بی‌جواب را هم در خود دارد.

### خط صفر روی صفحهٔ ریسک–پوشش کجاست؟

اگر `api_error` نباشد، با جایگذاری c = coverage × (1 − risk) و w + i = coverage × risk:

```text
score = coverage · (1 − risk) − k · coverage · risk = coverage · (1 − (k + 1) · risk)
```

پس امتیاز فقط وقتی مثبت است که risk < 1/(k+1). با k = 3 این مرز ۲۵ درصد است، یعنی همان 1 − t برای خط سکوت ۷۵ درصدی [قسمت HMD-010](/fa/blog/hmd-010-silence-line-calibration/). پوشش فقط اندازهٔ امتیاز را تعیین می‌کند، نه علامتش را. با عددهای گردشدهٔ جدول، این فرمول برای A، B و C به‌ترتیب 0.346−، 0.214+ و 0.374+ می‌دهد؛ اختلافش با خروجی دقیق (0.331−، 0.203+، 0.383+) فقط از گردکردن درصدهاست. اتحاد «امتیاز = درست − ۳ × غلط» در `--selftest` بررسی می‌شود.

### منحنی ریسک–پوشش این‌جا چه شکلی دارد؟

در طبقه‌بندی گزینشی، یک مدل با یک آستانهٔ اطمینان کار می‌کند و با جابه‌جاکردن آستانه، یک منحنی کامل از نقطه‌های (پوشش، ریسک) ساخته می‌شود ([El-Yaniv و Wiener ۲۰۱۰](https://www.jmlr.org/papers/v11/el-yaniv10a.html)؛ برای شبکه‌های عمیق [Geifman و El-Yaniv ۲۰۱۷](https://arxiv.org/abs/1705.08500)). در آزمون رفتاری ما به اطمینان درونی مدل دسترسی نداریم؛ هر مدل در هر شرط فقط **یک نقطه** است. آستانه در خود دستور است: شرط‌های `t50`، `t75` و `t90` با جریمهٔ ۱، ۳ و ۹. شرط اصلی این قسمت `t75` است.

## قفل داده و ثبت از پیش دقیقاً شامل چه چیزهایی است؟

پیش از تحلیل این‌ها ثابت و منتشر می‌شود: فایل پاسخ‌ها، داوری نهایی، فهرست اجراهای مورد انتظار (manifest)، طرح تحلیل ثبت‌شده و هش هر کدام. فهرست اجراهای مورد انتظار به این دلیل لازم است که `bluff_lab.py` به پاسخ‌های `api_error` و `invalid` امتیاز k− می‌دهد، اما سطری را که کلاً از فایل غایب است نمی‌تواند تشخیص دهد. طرح در یک فایل JSON با همان کلیدهای `DEMO_PLAN` نوشته می‌شود:

```json
{
  "primary_condition": "t75",
  "confirmatory_pair": ["Model-B", "Model-A"],
  "practical_delta_points_per_prompt": 0.10,
  "max_fabrication_design_choice": 0.05,
  "everything_else": "EXPLORATORY"
}
```

(نسخهٔ کامل `DEMO_PLAN` دو کلید توصیفی دیگر هم دارد: `status` و `primary_metric`.) هش طرح روی JSON با کلیدهای مرتب‌شده گرفته می‌شود، پس ترتیب نوشتن کلیدها هش را عوض نمی‌کند؛ `--selftest` همین را امتحان می‌کند. هش طرح آموزشی با `e1f87007` شروع می‌شود.

Nosek و همکاران ثبت از پیش را تعهد به مراحل تحلیل «without advance knowledge of the research outcomes» تعریف می‌کنند و بر تمایز پیش‌بینی از توضیحِ پس از دیدن داده (postdiction) تکیه دارند ([PNAS 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/)). مقایسه‌ای که پیش از دیدن داده ثبت شده، آزمون است؛ هر چه بعد از دیدن داده انتخاب شود، سرنخ است.

## مقایسهٔ تأییدی چطور حساب می‌شود؟

برای دو مدل A و B که به همان سؤال‌ها جواب داده‌اند، اختلاف جفتی میانگین اختلاف امتیاز سؤال‌به‌سؤال است:

```text
d̄ = (1/n) · Σ_i (s_B,i − s_A,i)
```

[Miller (۲۰۲۴)](https://arxiv.org/abs/2411.00640) در بخش «Paired analysis» استفاده از خطای معیار جفتی را هر جا ممکن باشد توصیه می‌کند و در بخش دیگری دربارهٔ سؤال‌های خوشه‌ای، مثل ترجمه‌های یک سؤال، بحث می‌کند. بازهٔ ما از بوت‌استرپ خوشه‌ای `bluff_lab.py` می‌آید: ۲۰۰ خوشهٔ پایه (۱۵۰ سؤال دوزبانه و ۵۰ سؤال بی‌جواب) با جایگذاری نمونه‌گیری می‌شوند، همهٔ نسخه‌های زبانی هر خوشه با هم می‌مانند، و در هر تکرار برآوردگر نسبتی «جمع اختلاف‌ها تقسیم بر تعداد سؤال‌ها» دوباره حساب می‌شود. بازه صدک‌های ۲٫۵ و ۹۷٫۵ از ۲٬۰۰۰ تکرار با seed 42 است. دقت کنید: Miller بوت‌استرپ را برای خطای معیار ساده لازم نمی‌داند؛ ما آن را به‌خاطر برآوردگر نسبتی و خوشه‌های نامساوی به کار برده‌ایم و این انتخاب را به او نسبت نمی‌دهیم.

<svg viewBox="0 0 640 260" width="100%" role="img" aria-labelledby="hmd016-fa-dd-chart-title" direction="ltr" style="direction:ltr" font-size="13" fill="currentColor">
<title id="hmd016-fa-dd-chart-title">ILLUSTRATIVE: اختلاف جفتی و بازهٔ ۹۵٪ بوت‌استرپ خوشه‌ای برای مدل‌های خیالی، خروجی abstain_report.py --demo</title>
<g stroke="currentColor" stroke-opacity="0.2"><line x1="220" y1="25" x2="220" y2="215"/><line x1="315" y1="25" x2="315" y2="215"/><line x1="505" y1="25" x2="505" y2="215"/><line x1="600" y1="25" x2="600" y2="215"/></g>
<line x1="410" y1="25" x2="410" y2="215" stroke="currentColor" stroke-opacity="0.7"/>
<line x1="429" y1="25" x2="429" y2="215" stroke="#E8A33D" stroke-dasharray="3 3"/>
<g stroke="#E8A33D" stroke-width="3"><line x1="472.7" y1="40" x2="550.2" y2="40"/></g>
<circle cx="511.5" cy="40" r="5" fill="#E8A33D"/>
<g stroke="currentColor" stroke-width="2"><line x1="234.1" y1="75" x2="315.6" y2="75"/><line x1="344.8" y1="105" x2="406.2" y2="105"/><line x1="385.9" y1="140" x2="527.8" y2="140"/><line x1="402.4" y1="170" x2="506.3" y2="170"/><line x1="385.9" y1="200" x2="456.9" y2="200"/></g>
<g><circle cx="274.3" cy="75" r="4"/><circle cx="375.8" cy="105" r="4"/><circle cx="461.9" cy="140" r="4"/><circle cx="453.1" cy="170" r="4"/><circle cx="422.7" cy="200" r="4"/></g>
<g text-anchor="end" font-size="12"><text x="205" y="44" font-weight="bold">B − A (confirmatory)</text><text x="205" y="79">A − C (exploratory)</text><text x="205" y="109">B − C (exploratory)</text><text x="205" y="144">A: English − Persian</text><text x="205" y="174">B: English − Persian</text><text x="205" y="204">C: English − Persian</text></g>
<g font-size="11" text-anchor="middle" fill-opacity="0.7"><text x="220" y="232">−1</text><text x="315" y="232">−0.5</text><text x="410" y="232">0</text><text x="505" y="232">+0.5</text><text x="600" y="232">+1</text><text x="410" y="252">points per prompt · dashed: practical delta +0.10 · ILLUSTRATIVE</text></g>
</svg>

در دادهٔ آموزشی، B − A برابر 0.534+ با بازهٔ 0.330+ تا 0.738+ شد. صفر بیرون بازه است و کران پایین از حد عملی ثبت‌شده (0.10+) بالاتر است. همین عدد را `tools/bluff_lab.py compare` هم مستقل از گزارش داد؛ با seed بوت‌استرپ ۷ هم اختلاف همان ماند و بازه 0.332+ تا 0.736+ شد.

## چرا بقیهٔ مقایسه‌ها فقط اکتشافی‌اند؟

بازه‌ها «نقطه‌ای»اند، یعنی هر کدام فقط برای یک مقایسهٔ تنها معتبر است. با m مدل، m(m − 1)/2 جفت وجود دارد. اگر همهٔ تفاوت‌های واقعی صفر باشند و m آزمون مستقل باشند، احتمال دست‌کم یک هشدار کاذب با بازه‌های ۹۵ درصدی برابر است با:

```text
P = 1 − 0.95^m   →   m = 3: 14%   ·   m = 15: 54%
```

مقایسه‌های جفتی روی یک مجموعه سؤال مستقل نیستند، پس این عدد فقط برای شهود است. ابزار عمداً هیچ تصحیح چندگانه‌ای اعمال نمی‌کند و هیچ رتبه‌بندی خودکاری نمی‌سازد؛ به‌جای آن، فقط یک مقایسه تأییدی است. در دمو، B − C برابر 0.180− با بازهٔ 0.343− تا 0.020− است؛ بازه صفر را بیرون گذاشته، اما چون ثبت نشده بود، سرنخ است نه یافته. فاصلهٔ انگلیسی و فارسی هم برای هر سه مدل خیالی بازه‌ای دارد که صفر را می‌پوشاند (برای A: 0.273+ با بازهٔ 0.127− تا 0.620+، روی ۱۵۰ جفت).

## نگهبان سؤال‌های بی‌جواب چطور تصمیم می‌گیرد؟

روی سؤال‌های بی‌جواب، هر پاسخ `wrong` یا `invalid` یعنی ساختن جواب. فقط تکرار اول هر سؤال شمرده می‌شود تا تکرارها نمونهٔ مستقل حساب نشوند. با x جواب ساختگی از n، بازهٔ Wilson دوطرفهٔ ۹۵ درصدی حساب می‌شود (z ≈ 1.96):

```text
center = (x/n + z²/(2n)) / (1 + z²/n)
half   = z · sqrt( (x/n)(1 − x/n)/n + z²/(4n²) ) / (1 + z²/n)
PASS    if upper ≤ cap
BREACH  if lower > cap
UNKNOWN otherwise (also if any U item has api_error)
```

در دمو با سقف ۵٪: Model-A با ۳۷ از ۵۰ بازهٔ ۶۰٪ تا ۸۴٪ دارد (BREACH)، Model-B با ۳ از ۵۰ بازهٔ ۲٪ تا ۱۶٪ (UNKNOWN) و Model-C با ۰ از ۵۰ بازهٔ ۰٪ تا ۷٫۱٪ (UNKNOWN). با x = 0 کران بالا z²/(n + z²) می‌شود؛ برای اینکه به ۵٪ یا کمتر برسد باید n ≥ 73 باشد. یعنی با این سقف، حتی مدل بی‌خطا هم با کمتر از ۷۳ سؤال بی‌جواب «قبول» نمی‌گیرد (محاسبهٔ ما). سقف ۵٪ انتخاب طراحی است، نه استاندارد ایمنی.

## چطور همهٔ این‌ها را بازتولید کنیم؟

همهٔ فرمان‌ها از ریشهٔ مخزن اجرا می‌شوند و فقط پایتون ۳ لازم دارند (اجرای ما: Python 3.11.7، ۷ نوامبر ۲۰۲۶):

```bash
A=parts/02-benchmarking/e08-which-model-knows-when-to-abstain/artifact
python3 $A/abstain_report.py --selftest          # دمو قطعی است، یک برچسب هش را می‌شکند، میانگین جفتی، اتحاد امتیاز
python3 $A/abstain_report.py --demo              # فایل ILLUSTRATIVE را می‌سازد و گزارش کامل را چاپ می‌کند
shasum -a 256 $A/abstain-demo-ILLUSTRATIVE.csv   # a39e3469b7ca0e03…
python3 tools/bluff_lab.py compare $A/abstain-demo-ILLUSTRATIVE.csv --a Model-B --b Model-A --iterations 2000
python3 $A/abstain_report.py --demo --seed 7     # بررسی پایداری بازه
```

`--demo` فایل CSV را در همان پوشه دوباره می‌نویسد؛ چون مولد قطعی است (seed 16)، محتوا و هش عوض نمی‌شوند. برای اجرای واقعی، پس از قفل داده:

```bash
python3 $A/abstain_report.py locked.csv --plan plan.json
```

`locked.csv` ستون‌های `item_id,cluster_id,model,condition,repeat,language,split,answerable,label,source_status` را لازم دارد و دادهٔ ILLUSTRATIVE و EMPIRICAL را نمی‌شود در یک اجرا مخلوط کرد. اگر `plan.json` را با همان مقادیر `DEMO_PLAN` بسازید و روی فایل دمو اجرا کنید، هش طرح باز با `e1f87007` شروع می‌شود.

## این چه چیزی را نشان نمی‌دهد

- اجرای واقعی Bluff هنوز انجام و قفل نشده است؛ هیچ عددی در این نوشته به مدل واقعی تعلق ندارد و هیچ عدد آموزشی به نام مدل واقعی وصل نمی‌شود.
- مدل‌های A، B و C و سؤال‌هایشان ساختگی‌اند (ILLUSTRATIVE). پارامترهای مولدشان در `DEMO_MODELS` آمده و عمداً طوری انتخاب شده‌اند که سازوکار دیده شود.
- خروجی را می‌سنجیم، نه اطمینان درونی مدل را؛ هر مدل در هر شرط یک نقطه است، نه یک منحنی کامل ریسک–پوشش.
- بازه‌ها نقطه‌ای‌اند و تصحیح چندگانه ندارند. عدم تشخیص تفاوت یعنی برابری نیست.
- هش تغییرنکردن فایل را ثابت می‌کند، نه درستی برچسب‌ها یا کامل‌بودن داده را.
- یافته‌های AbstentionBench فقط دربارهٔ همان مطالعه‌اند و معنای دقیق «۲۴٪» در متن روشن نیست.

## برای مطالعهٔ بیشتر

- Kirichenko و همکاران، *AbstentionBench*، [arXiv 2506.09038](https://arxiv.org/abs/2506.09038)؛ کد در [GitHub](https://github.com/facebookresearch/AbstentionBench).
- El-Yaniv و Wiener، *On the Foundations of Noise-free Selective Classification*، [JMLR 2010](https://www.jmlr.org/papers/v11/el-yaniv10a.html).
- Geifman و El-Yaniv، *Selective Classification for Deep Neural Networks*، [arXiv 1705.08500](https://arxiv.org/abs/1705.08500).
- Miller، *Adding Error Bars to Evals*، [arXiv 2411.00640](https://arxiv.org/abs/2411.00640)؛ بخش‌های تحلیل جفتی و سؤال‌های خوشه‌ای.
- Nosek و همکاران، *The preregistration revolution*، [PNAS 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/).
- [قسمت HMD-018](/fa/episodes/hmd-018/)، دربارهٔ انتشار بسته‌ای که هر کس بتواند نتیجه را دوباره حساب کند.

*نسخهٔ انگلیسی این نوشته: [Measuring AI abstention: risk–coverage and preregistration](/en/blog/hmd-016-risk-coverage-preregistration/)*
