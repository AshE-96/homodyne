---
title: "نتیجهٔ ابطال‌پذیر: مانیفست SHA-256، لنگر و دفتر اصلاحیه"
description: "بستهٔ قابل‌بررسی برای نمرهٔ بنچمارک: محاسبهٔ دوباره در برابر اجرای دوباره، مانیفست SHA-256، لنگر بیرونی، نسخه‌بندی و فرمان‌های recompute_check.py."
lang: fa
translationKey: hmd-018-deep-dive
hmd: HMD-018
kind: deep-dive
date: 2027-03-26
tags: ["بازتولیدپذیری", "SHA-256", "مانیفست", "دفتر اصلاحیه", "نسخه‌بندی", "بنچمارک"]
sources:
  - title: "NeurIPS 2026 Paper Checklist Guidelines (خوانده‌شده ۷ نوامبر ۲۰۲۶)"
    url: "https://neurips.cc/public/guides/PaperChecklist"
  - title: "NeurIPS blog (۴ مه ۲۰۲۶). MLRC 2026: Reproducibility as an Official Track at NeurIPS"
    url: "https://blog.neurips.cc/2026/05/04/mlrc-2026-reproducibility-as-an-official-track-at-neurips/"
  - title: "NIST FIPS 180-4, Secure Hash Standard (اوت ۲۰۱۵)"
    url: "https://csrc.nist.gov/pubs/fips/180-4/upd1/final"
  - title: "Liang و همکاران (۲۰۲۲؛ TMLR 2023). Holistic Evaluation of Language Models. arXiv 2211.09110"
    url: "https://arxiv.org/abs/2211.09110"
  - title: "Mitchell و همکاران (۲۰۱۸؛ FAT* 2019). Model Cards for Model Reporting. arXiv 1810.03993"
    url: "https://arxiv.org/abs/1810.03993"
  - title: "Gebru و همکاران (۲۰۱۸؛ CACM 2021). Datasheets for Datasets. arXiv 1803.09010"
    url: "https://arxiv.org/abs/1803.09010"
  - title: "COPE Retraction Guidelines"
    url: "https://publicationethics.org/guidance/guideline/retraction-guidelines"
  - title: "Retraction Watch (۴ سپتامبر ۲۰۲۵). New COPE retraction guidelines"
    url: "https://retractionwatch.com/2025/09/04/new-cope-retraction-guidelines-address-paper-mills-third-parties-and-more/"
  - title: "OpenAI (۲۳ فوریهٔ ۲۰۲۶). Why we no longer evaluate SWE-bench Verified"
    url: "https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/"
  - title: "AI Weekly: OpenAI drops SWE-Bench Verified after flaw audit (منبع ثانویه)"
    url: "https://aiweekly.co/alerts/openai-drops-swe-bench-verified-backs-pro-after-flaw-audit"
datasets:
  - title: "recompute_check.py (هومودین، HMD-018)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e09-how-do-you-publish-a-refutable-result/artifact/recompute_check.py"
    license: "MIT (LICENSE.md مخزن)"
  - title: "bluff-demo.csv: ۲۰ سطر، دو مدل خیالی (ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff-demo.csv"
    license: "مخزن هومودین؛ LICENSE.md را ببینید"
  - title: "bluff_lab.py: نمره‌دهندهٔ دوره"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff_lab.py"
    license: "MIT (LICENSE.md مخزن)"
  - title: "HELM (Stanford CRFM)، کد ارزیابی"
    url: "https://github.com/stanford-crfm/helm"
    license: "Apache 2.0"
---

نتیجهٔ ابطال‌پذیر نتیجه‌ای است که هر خواننده بتواند بدون اعتماد به ناشر بررسی‌اش کند و در صورت خطا، خطا را نشان دهد. برای نمرهٔ بنچمارک این یعنی بسته‌ای شامل جواب‌های برچسب‌خورده، روش، کد نمره‌دهی، نمرهٔ منتشرشده و دفتر اصلاحیه، یک مانیفست SHA-256 از همهٔ این فایل‌ها، و یک «لنگر»، یعنی هش خود مانیفست، که بیرون از بسته و با تاریخ منتشر شده باشد. این نوشته ساختار بسته، چک‌ها، چهار حالت دستکاری و فرمان‌های بازتولید `recompute_check.py` را کامل توضیح می‌دهد. همهٔ داده‌ها آموزشی‌اند (ILLUSTRATIVE).

> **نکته‌های اصلی**
> - محاسبهٔ دوباره (recompute) قطعی است: همان بایت‌ها و همان کد باید عیناً همان عدد را بدهند. اجرای دوباره (rerun) این تضمین را ندارد.
> - مانیفست تغییر هر فایل را لو می‌دهد؛ محاسبهٔ دوباره ناهماهنگی نمره با جواب‌ها را؛ و فقط لنگر بیرونی تعویض کامل و هماهنگ بسته را.
> - اصلاح علنی همان ویرایش تقلب است، به‌اضافهٔ نسخهٔ تازه، سطر دفتر اصلاحیه و لنگر تازه در کنار لنگر قدیمی.
> - `recompute_check.py` فقط از کتابخانهٔ استاندارد پایتون استفاده می‌کند و هیچ مدلی را صدا نمی‌زند.

این لایهٔ فنی [قسمت HMD-018](/fa/episodes/hmd-018/) است. اگر ویدیو را ندیده‌اید، از [نوشتهٔ همراه](/fa/blog/hmd-018-check-an-ai-score/) شروع کنید؛ مرور کل دورهٔ بنچمارک هم همان‌جاست.

## این قسمت به چه داده‌ها و ابزارهایی تکیه دارد؟

| داده یا ابزار | چه چیزی دارد | اندازه | مجوز |
|---|---|---|---|
| `tools/bluff-demo.csv` | ۱۰ سؤال × ۲ مدل خیالی، شرط t75 | ۲۰ سطر؛ SHA-256 با `35ceaaf4` شروع می‌شود | مخزن هومودین |
| `recompute_check.py` | سازندهٔ بستهٔ دمو و چک‌کنندهٔ خواننده | ۲۹۹ سطر، فقط stdlib | MIT |
| `tools/bluff_lab.py` | نمره‌دهندهٔ مشترک دوره (`summaries()`) | — | MIT |
| HELM (Liang و همکاران) | چارچوب ارزیابی با انتشار پرامپت‌ها و جواب‌های خام | ۳۰ مدل، ۴۲ سناریو در نسخهٔ مقاله | Apache 2.0 |

مجوزها ۷ نوامبر ۲۰۲۶ از مخزن‌ها خوانده شد. فایل دمو همان فایل آموزشی قسمت‌های قبلی دوره است و به‌صورت بایت‌به‌بایت در بسته کپی می‌شود؛ برای همین هشش با `input_sha256` خروجی `bluff_lab.py score` یکی است.

## محاسبهٔ دوباره دقیقاً چه چیزی را تضمین می‌کند؟

محاسبهٔ دوباره یک تابع قطعی است: ورودی‌اش بایت‌های `results.csv`، نسخهٔ کد نمره‌دهی و قانون نمره است. اگر این سه ثابت بمانند، خروجی هم باید ثابت بماند. چک‌کننده نمره را با همان تعداد رقم اعشاری که در `published.json` اعلام شده (`decimals: 3`) گرد می‌کند و با نمرهٔ منتشرشده مقایسه می‌کند.

اجرای دوباره چنین تضمینی ندارد. مدل‌ها معمولاً با نمونه‌گیری تصادفی جواب می‌دهند و سرویس‌ها ممکن است نسخهٔ مدل را بی‌صدا عوض کنند. این قسمت این دلیل‌ها را توضیح می‌دهد، اما اندازه نمی‌گیرد. به همین دلیل بسته باید جواب‌های خام را نگه دارد: محاسبهٔ دوباره فقط روی جواب‌های ذخیره‌شده ممکن است.

## بسته چه فایل‌هایی دارد؟

```text
bundle/
  results.csv       # item_id,cluster_id,model,condition,repeat,language,split,answerable,label,source_status,response
  METHOD.md         # rule +1 / 0 / −k, condition t75, k = 3, scorer, who labelled
  published.json    # bundle_version, date, condition, penalty_k, decimals, unit, scorer, scores
  CHANGELOG.md      # newest entry first: version, date, item, reason, effect
  MANIFEST.sha256   # "<64 hex>  <filename>" for the four files above
```

قالب مانیفست همان قالب ابزارهای استاندارد است، پس بدون برنامهٔ ما هم می‌شود آن را چک کرد. در بستهٔ دموی ما، `shasum -a 256 -c MANIFEST.sha256` برای هر چهار فایل `OK` داد. چک‌کننده هر فایلی را هم که در پوشه هست ولی در مانیفست نیست رد می‌کند، تا نشود فایل اضافه‌ای را بی‌صدا کنار بسته گذاشت.

کد نمره‌دهی در این دمو داخل بسته نیست؛ از `tools/bluff_lab.py` در مخزن خوانده می‌شود. در بستهٔ واقعی، یا خود کد را در مانیفست بگذارید یا شناسهٔ دقیق نسخه‌اش (مثلاً شناسهٔ commit) را در `METHOD.md` بنویسید. این یک محدودیت آگاهانهٔ دموست.

## SHA-256 چه چیزی را ثابت می‌کند و چه چیزی را نه؟

SHA-256 در استاندارد [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) تعریف شده و خروجی‌اش ۲۵۶ بیت است، یعنی ۶۴ نویسهٔ هگزادسیمال. تغییر یک برچسب در فایل دمو هش را از `35ceaaf427d7…` به `0fb34f0c362b…` می‌برد.

هش ثابت می‌کند فایل از لحظهٔ هش‌شدن عوض نشده است. ثابت نمی‌کند برچسب‌ها درست‌اند، داده کامل است، یا هش در تاریخ ادعاشده ساخته شده است. سؤال آخر را فقط جایی بیرون از بسته جواب می‌دهد؛ یعنی لنگر.

## چک‌کننده به چه ترتیبی کار می‌کند؟

سه چک پشت سر هم، و اولین ناجوری گزارش می‌شود:

1. **مانیفست:** اگر `--anchor` داده شده باشد، هش `MANIFEST.sha256` باید با آن برابر باشد. بعد هر فایل فهرست‌شده باید وجود داشته باشد و هشش بخواند، و فایل فهرست‌نشده‌ای نباشد.
2. **دفتر اصلاحیه:** `bundle_version` در `published.json` باید نخستین سرفصل `## v…` در `CHANGELOG.md` باشد.
3. **محاسبهٔ دوباره:** نمرهٔ هر مدل با `bluff_lab.summaries()` از روی `results.csv` حساب و با نمرهٔ منتشرشده، یا با عددی که کاربر با `--claim` وارد کرده، مقایسه می‌شود.

خروجی PASS یا FAIL است و کد خروج ۰ یا ۱، پس در اسکریپت و CI هم قابل استفاده است.

## چهار دستکاری و یک اصلاح را کدام چک می‌گیرد؟

در دمو، نمرهٔ منتشرشدهٔ v0.1 برای A برابر 0.100− و برای B برابر 0.100+ است (شرط t75، k = 3، ۱۰ سؤال). همهٔ دستکاری‌ها یک ویرایش مشترک دارند: سؤال q06، مدل A، فارسی، از `wrong` به `correct`. اثرش روی A: (1 − (−3)) / 10 = 0.4، یعنی از 0.100− به 0.300+، و ترتیب A و B برعکس می‌شود. خروجی `--selftest` (اجرا ۷ نوامبر ۲۰۲۶، ILLUSTRATIVE):

| حالت | بدون لنگر | با لنگر | اولین ناجوری |
|---|---|---|---|
| `original` | PASS | PASS | — |
| `tamper-csv` (فقط برچسب) | FAIL | FAIL | هش `results.csv`: مانیفست `35ceaaf4…`، فایل `0fb34f0c…` |
| `tamper-csv-manifest` (+ مانیفست تازه) | FAIL | FAIL | بی‌لنگر: نمرهٔ A منتشرشده 0.100−، محاسبه‌شده 0.300+؛ با لنگر: مانیفست `55734e42…` |
| `tamper-all` (+ نمرهٔ منتشرشده) | **PASS** | FAIL | با لنگر: مانیفست `3013a118…` به‌جای `e6db5cb8…` |
| `correction` (v0.2 + دفتر + لنگر تازه) | PASS | PASS (لنگر `57772828…`) | — |

یک چک دیگر هم در `--selftest` هست: اگر بیننده عدد 0.300+ را از یک اسکرین‌شات برای A وارد کند (`--claim A=0.3`)، چک‌کننده روی بستهٔ اصلی FAIL می‌دهد: «claimed +0.300, recomputed −0.100».

نکتهٔ ردیف `tamper-all` این است که همهٔ چک‌های درونی فقط سازگاری بسته با خودش را می‌سنجند. بسته‌ای که کامل و هماهنگ از نو ساخته شود، بدون مرجع بیرونی تشخیص‌دادنی نیست.

## لنگر کجا و چطور منتشر شود؟

لنگر هش خود مانیفست است: `sha256(MANIFEST.sha256)`. لنگر v0.1 دمو با `e6db5cb88679` شروع می‌شود. روز انتشار، این رشته با تاریخ در جایی گذاشته می‌شود که بسته نیست. معیار انتخاب این است که خود ناشر نتواند آن را بی‌صدا عوض کند:

- **توضیحات ویدیو یا صفحهٔ وب ناشر:** در دسترس، اما ناشر می‌تواند ویرایشش کند. به‌تنهایی ضعیف است.
- **commit در مخزن عمومی گیت:** هر commit هش commit قبلی را در خود دارد، پس تغییر گذشته کل زنجیره را عوض می‌کند. صاحب مخزن می‌تواند تاریخچه را بازنویسی کند، اما نسخه‌هایی که دیگران کلون کرده‌اند تاریخچهٔ قبلی را نگه می‌دارند.
- **نسخهٔ آرشیوشده یا نقل‌قول دیگران:** جایی که کنترلش با ناشر نیست.

لنگر تعویض بی‌صدا را سخت می‌کند، نه ناممکن. ترکیب دو یا سه جای مستقل از یکی بهتر است.

## نسخه‌بندی و دفتر اصلاحیه چطور کار می‌کنند؟

اصلاح دمو این سطر را بالای `CHANGELOG.md` اضافه می‌کند: نسخهٔ v0.2، تاریخ، سؤال اصلاح‌شده (q06، مدل A، فارسی)، دلیل (گزارش خواننده: جواب‌نامه فقط یک املای نام را می‌پذیرفت)، اثر (A از 0.100− به 0.300+؛ B بدون تغییر) و این تعهد که فایل‌ها و لنگر v0.1 در کنار این سطر عمومی می‌مانند. چک‌کننده فقط بررسی می‌کند نسخهٔ منتشرشده تازه‌ترین سطر باشد؛ اینکه دلیل قانع‌کننده است یا نه، داوری انسانی می‌خواهد.

راهنمای پس‌گرفتن مقالهٔ COPE هدف اصلی را اصلاح سابقهٔ علمی می‌داند، نه تنبیه نویسنده، و می‌خواهد اطلاعیه دلیل را بگوید. نسخهٔ ۲۰۱۹ این راهنما در سپتامبر ۲۰۲۵ به‌روز شد ([Retraction Watch](https://retractionwatch.com/2025/09/04/new-cope-retraction-guidelines-address-paper-mills-third-parties-and-more/)). برای گزارش خطا از سوی خواننده، سه فیلد کافی است: شناسهٔ سؤال، شاهد، و اصلاح پیشنهادی.

## با سؤال‌هایی که نمی‌شود منتشر کرد چه کنیم؟

سؤال‌های کنارگذاشته (held-out)، داده‌های شخصی و داده‌های بی‌مجوز بازنشر را می‌شود «متعهد» کرد: امروز فقط هش فایلشان منتشر می‌شود و خود فایل بعداً. روز افشا، هر کس می‌تواند بررسی کند که سؤال‌ها همان‌هایی‌اند که از اول قفل شده بودند. یک احتیاط: اگر محتوا کوتاه یا حدس‌زدنی باشد، هش به‌تنهایی ممکن است با حدس‌زدن و امتحان‌کردن لو برود؛ افزودن یک رشتهٔ تصادفی محرمانه به فایل پیش از هش‌کردن، و افشای آن همراه سؤال‌ها، این خطر را کم می‌کند.

چک‌لیست [NeurIPS 2026](https://neurips.cc/public/guides/PaperChecklist) همین منطق را رسمی کرده است: سؤال‌های «Experimental Result Reproducibility»، «Open Access to Data and Code»، «Experimental Setting/Details»، «Experiment Statistical Significance» و «Licenses» را دارد، مقالهٔ بی‌چک‌لیست بدون داوری رد می‌شود، و جواب «no» یا «n/a» به‌خودی‌خود دلیل رد نیست. چالش بازتولید MLRC هم در NeurIPS 2026 بخش رسمی کنفرانس شده و داوری اولش در مجلهٔ TMLR انجام می‌شود ([NeurIPS blog](https://blog.neurips.cc/2026/05/04/mlrc-2026-reproducibility-as-an-official-track-at-neurips/)).

## نمونهٔ واقعی: SWE-bench Verified

OpenAI در ۲۳ فوریهٔ ۲۰۲۶ گزارش نمرهٔ SWE-bench Verified (۵۰۰ مسئله) را متوقف کرد. طبق منابع ثانویه، از ۱۳۸ مسئلهٔ سخت‌ترِ ممیزی‌شده، که حدود ۲۷٫۶ درصد مجموعه‌اند، ۵۹٫۴ درصد در طراحی تست یا صورت مسئله مشکل جدی داشتند ([AI Weekly](https://aiweekly.co/alerts/openai-drops-swe-bench-verified-backs-pro-after-flaw-audit)). این نمونه تصادفی نبود؛ پس ۵۹٫۴ درصد را نمی‌شود به کل ۵۰۰ مسئله تعمیم داد. دلیل دوم آلودگی دادهٔ آموزش بود. در ژوئیهٔ ۲۰۲۶ هم OpenAI توصیهٔ خودش برای جایگزین را پس گرفت. هر دو مورد نشان می‌دهند که بدون جواب‌ها و تست‌های منتشرشده، چنین خطاهایی دیر پیدا می‌شوند.

## چطور همهٔ این‌ها را بازتولید کنیم؟

از ریشهٔ مخزن، فقط با پایتون ۳:

```bash
A=parts/02-benchmarking/e09-how-do-you-publish-a-refutable-result/artifact
python3 $A/recompute_check.py --selftest                          # پنج بسته، هر کدام بی‌لنگر و با لنگر
python3 $A/recompute_check.py --demo /tmp/b                       # بستهٔ v0.1 و چاپ لنگر
python3 $A/recompute_check.py /tmp/b --anchor e6db5cb88679bd980353f1188a716a1a34b6d07eb03f3ccc2e6206677eb0ad2b   # PASS
(cd /tmp/b && shasum -a 256 -c MANIFEST.sha256)                   # همان چک، بدون برنامهٔ ما
python3 $A/recompute_check.py --demo /tmp/t --variant tamper-all  # تقلب تمیز
python3 $A/recompute_check.py /tmp/t                              # PASS بدون لنگر
python3 $A/recompute_check.py /tmp/t --anchor e6db5cb88679bd980353f1188a716a1a34b6d07eb03f3ccc2e6206677eb0ad2b   # FAIL
python3 $A/recompute_check.py /tmp/b --claim A=0.3                # عددی که روی اسکرین‌شات دیدید: FAIL
python3 $A/recompute_check.py --demo /tmp/c --variant correction  # v0.2 با لنگر 577728283b70…
```

`--demo` پوشهٔ مقصد را اگر وجود داشته باشد پاک و از نو می‌سازد؛ پوشهٔ خالی یا موقت بدهید. گزینه‌های `--variant`: `original`، `tamper-csv`، `tamper-csv-manifest`، `tamper-all`، `correction`. اگر `tools/bluff-demo.csv` روزی عوض شود، همهٔ هش‌های این نوشته هم عوض می‌شوند؛ و اگر سطر q06 مدل A دیگر در آن نباشد، سازندهٔ دستکاری‌ها با پیام خطا متوقف می‌شود.

## این چه چیزی را نشان نمی‌دهد

- محاسبهٔ دوباره درستی حساب را نشان می‌دهد، نه درستی برچسب‌ها را. داوری غلط با محاسبهٔ درست همچنان غلط است.
- نشان نمی‌دهد اجرای دوبارهٔ مدل همان جواب‌ها را می‌دهد؛ دلیل‌های تفاوت را توضیح داده‌ایم، اندازه نگرفته‌ایم.
- لنگر تعویض بی‌صدا را سخت می‌کند، نه ناممکن، و قدرتش به جایی بستگی دارد که منتشر شده است.
- بستهٔ دمو آموزشی است: ده سؤال و دو مدل خیالی (ILLUSTRATIVE). هیچ نتیجهٔ واقعی Bluff در این نوشته نیست.
- صفحه‌های OpenAI و COPE به ابزارهای ما اجازهٔ خواندن ندادند؛ عددهای SWE-bench Verified از منابع ثانویهٔ هم‌خوان و مضمون COPE از متن ۲۰۱۹ در نتایج جست‌وجو آمده است. دربارهٔ SWE-bench Pro یا «درصد مقاله‌های غیرقابل‌بازتولید» عددی نقل نکرده‌ایم.

## برای مطالعهٔ بیشتر

- [NeurIPS 2026 Paper Checklist](https://neurips.cc/public/guides/PaperChecklist)؛ به‌ویژه بخش‌های بازتولید و دسترسی به داده و کد.
- Liang و همکاران، *Holistic Evaluation of Language Models*، [arXiv 2211.09110](https://arxiv.org/abs/2211.09110)؛ کد در [GitHub](https://github.com/stanford-crfm/helm).
- Mitchell و همکاران، *Model Cards for Model Reporting*، [arXiv 1810.03993](https://arxiv.org/abs/1810.03993)؛ Gebru و همکاران، *Datasheets for Datasets*، [arXiv 1803.09010](https://arxiv.org/abs/1803.09010).
- [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)، تعریف SHA-256.
- [نوشتهٔ عمیق HMD-016](/fa/blog/hmd-016-risk-coverage-preregistration/)، دربارهٔ قفل داده و ثبت از پیش برای همین آزمون.

*نسخهٔ انگلیسی این نوشته: [Refutable AI results: SHA-256 manifest, anchor and log](/en/blog/hmd-018-recompute-manifest-anchor/)*
