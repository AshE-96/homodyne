# منابع · HMD-018 · Benchmark E09

تاریخ بازبینی: ۷ نوامبر ۲۰۲۶ (۱۶ آبان ۱۴۰۵). شناسه‌های R03، R04، R07 و R11 از `private/planning/production-v3/references.json` هستند؛ R40 تا R44 برای این قسمت تازه‌اند.

| شناسه | منبع | چه چیزی از آن استفاده شد | کجا |
|---|---|---|---|
| R40 (منبع اصلی) | [NeurIPS 2026 Paper Checklist Guidelines](https://neurips.cc/public/guides/PaperChecklist) — خوانده‌شده ۷ نوامبر ۲۰۲۶ | چک‌لیست برای کنفرانس ۲۰۲۶ اجباری است: «The papers not including the checklist will be desk rejected.» سؤال «Open access to data and code»: «…the code, data, and instructions needed to reproduce the main experimental results». سؤال‌های دیگر: بازتولیدپذیری نتایج، جزئیات تنظیمات آزمایش، error bar. جواب «no» یا «n/a» با توجیه، دلیل رد نیست. | قاب ۳، ۷؛ هوک ۵ |
| R41 | [MLRC 2026: Reproducibility as an Official Track at NeurIPS — NeurIPS blog (۴ مه ۲۰۲۶)](https://blog.neurips.cc/2026/05/04/mlrc-2026-reproducibility-as-an-official-track-at-neurips/) | Machine Learning Reproducibility Challenge از ICLR 2018 (Joelle Pineau) شروع شد؛ در NeurIPS 2026 «برای اولین بار در تاریخ MLRC» بخش رسمی کنفرانس است؛ داوری اول در TMLR. | قاب ۳ |
| R42 | [HELM: Holistic Evaluation of Language Models — Liang et al., arXiv 2211.09110 (v1 ۱۶ نوامبر ۲۰۲۲؛ TMLR 2023)](https://arxiv.org/abs/2211.09110) | چکیده: «we release all raw model prompts and completions publicly for further analysis». (۳۰ مدل، ۴۲ سناریو؛ در گفتار نقل نشده.) | قاب ۵ |
| R42b | [Model Cards for Model Reporting — Mitchell et al., arXiv 1810.03993 (۲۰۱۸؛ FAT* 2019)](https://arxiv.org/abs/1810.03993) · [Datasheets for Datasets — Gebru et al., arXiv 1803.09010 (۲۰۱۸؛ CACM 2021)](https://arxiv.org/abs/1803.09010) | «کارت مدل» و «شناسنامهٔ داده»؛ نسخهٔ اول هر دو ۲۰۱۸. | قاب ۵ |
| R03 | [Why we no longer evaluate SWE-bench Verified — OpenAI (۲۳ فوریهٔ ۲۰۲۶)](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) | OpenAI گزارش نمرهٔ SWE-bench Verified (۵۰۰ مسئله) را متوقف کرد. ممیزی ۱۳۸ مسئله (حدود ۲۷٫۶٪ مجموعه؛ مسئله‌هایی که o3 در ۶۴ اجرا پیوسته حل نکرده بود؛ هر کدام دست‌کم شش مهندس): ۵۹٫۴٪ «material issues in test design and/or problem description»؛ تست‌های معیوب راه‌حل‌های درست را رد می‌کردند. دلیل دوم: مسئله‌ها از مخزن‌های عمومی‌ای که در دادهٔ آموزش هستند (آلودگی). **تأیید:** openai.com برای ابزار ما 403 داد؛ عددها و تاریخ از دو منبع ثانویهٔ هم‌خوان ([AI Weekly](https://aiweekly.co/alerts/openai-drops-swe-bench-verified-backs-pro-after-flaw-audit) و خلاصهٔ نتایج جست‌وجوی نقل‌کنندهٔ متن OpenAI) و با R03 پروژه («نمونهٔ ممیزی ۱۳۸ مسئلهٔ شکست‌خورده بود؛ نمایندهٔ تصادفی کل مجموعه نبود») تطبیق شد. «۵۹٫۴٪» فقط از ۱۳۸ مسئله است، نه از کل ۵۰۰. | قاب ۱۳؛ هوک ۵ |
| R43 (= R04 پروژه) | [Separating signal from noise in coding evaluations — OpenAI (۸ ژوئیهٔ ۲۰۲۶)](https://openai.com/index/separating-signal-from-noise-coding-evaluations/) | OpenAI توصیهٔ قبلی خود به SWE-bench Pro (جایگزین Verified) را پس گرفت. عدد ممیزی Pro در گفتار نقل نشده (صفحهٔ اصلی 403؛ فقط از منابع ثانویه دیده شد). | قاب ۱۳ |
| R44 | [COPE Retraction Guidelines](https://publicationethics.org/guidance/guideline/retraction-guidelines) (نسخهٔ ۲۰۱۹؛ نسخهٔ تازهٔ سپتامبر ۲۰۲۵ طبق [Retraction Watch](https://retractionwatch.com/2025/09/04/new-cope-retraction-guidelines-address-paper-mills-third-parties-and-more/)) | «The primary purpose of retraction is to correct the literature and ensure its integrity, rather than to punish authors.» اطلاعیه باید به مقاله لینک شود، روشن برچسب بخورد و دلیل را بگوید. سایت COPE برای ابزار ما 403 داد؛ نقل از متن ۲۰۱۹ در نتایج جست‌وجو. در گفتار فقط مضمون (اصلاح، نه تنبیه؛ دلیل در اطلاعیه) آمده است. | قاب ۱۲ |
| R11 | [BetterBench — arXiv 2411.12990](https://arxiv.org/abs/2411.12990) | پیش‌زمینهٔ کیفیت بنچمارک در چرخهٔ عمر (منبع مرکزی v4)؛ در گفتار v5 نقل نشده. | — |
| R07 | [Adding Error Bars to Evals — arXiv 2411.00640](https://arxiv.org/abs/2411.00640) | پیش‌زمینه؛ در گفتار نقل نشده. | — |

## محاسبه‌ها و اجرای خودمان (ILLUSTRATIVE)

- `artifact/recompute_check.py --selftest` (اجرا ۷ نوامبر ۲۰۲۶، Python 3، فقط stdlib؛ امتیازدهی از `tools/bluff_lab.py`):
  - داده: `tools/bluff-demo.csv` بایت‌به‌بایت (SHA-256 `35ceaaf427d7…`؛ همان `input_sha256` خروجی `bluff_lab.py score … --condition t75`). شرط t75، k = 3. ۱۰ پرامپت × ۲ مدل خیالی.
  - v0.1 منتشرشده: A = −0.100، B = +0.100 امتیاز به‌ازای هر پرامپت. لنگر v0.1 = `e6db5cb88679bd980353f1188a716a1a34b6d07eb03f3ccc2e6206677eb0ad2b`.
  - یک ویرایش: q06 / مدل A / فارسی از `wrong` به `correct` ⇒ A = −0.100 + (1 − (−3))/10 = +0.300؛ B بدون تغییر ⇒ ترتیب برعکس می‌شود. هش فایل: `35ceaaf4…` → `0fb34f0c…`.
  - نتیجه‌ها: original PASS/PASS؛ tamper-csv FAIL (هش results.csv)؛ tamper-csv-manifest FAIL (بی‌لنگر: «published −0.100، recomputed +0.300»؛ با لنگر: مانیفست)؛ tamper-all **PASS بدون لنگر**، FAIL با لنگر؛ correction (v0.2 + CHANGELOG + لنگر تازه `577728283b70…`) PASS/PASS. خروجی کامل در `README.md`.
- هیچ مدلی فراخوانی نشده؛ هیچ نتیجهٔ Bluff واقعی وجود ندارد یا ادعا نمی‌شود.

## چیزی که نمی‌گوییم

- نمی‌گوییم بستهٔ بررسی‌پذیر یعنی برچسب‌ها درست‌اند؛ محاسبهٔ دوباره فقط حساب را چک می‌کند.
- نمی‌گوییم لنگر تعویض را ناممکن می‌کند؛ فقط آن را بی‌صدا نمی‌گذارد، به شرط آنکه جایی باشد که ناشر به‌تنهایی کنترلش نمی‌کند.
- هیچ عددی دربارهٔ SWE-bench Pro، رتبهٔ مدل‌ها یا «درصد مقاله‌های غیرقابل‌بازتولید» نقل نمی‌کنیم.
- اینکه اجرای دوباره چرا فرق می‌کند (نمونه‌گیری تصادفی، تغییر نسخهٔ سرویس) توضیح مفهومی است، نه اندازه‌گیری.
