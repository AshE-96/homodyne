<div dir="rtl">

# HMD-022 · منابع

بازبینی روی وب: ۲۴ نوامبر ۲۰۲۶. شناسه‌های Rxx مخصوص همین قسمت‌اند. هر منبع باز و خوانده شد؛ ستون «بازبینی» می‌گوید کدام صفحه.

| شناسه | منبع | لینک | بازبینی | در این قسمت برای |
|---|---|---|---|---|
| R01 | Ong, Almahairi, Wu, Chiang, Wu, Gonzalez, Kadous, Stoica · *RouteLLM: Learning to Route LLMs with Preference Data* · arXiv 2406.18665 · ICLR 2025 (در صفحهٔ کنفرانس با عنوان «…from Preference Data») | https://arxiv.org/abs/2406.18665 · HTML نسخهٔ v4: https://arxiv.org/html/2406.18665v4 · کنفرانس: https://proceedings.iclr.cc/paper_files/paper/2025/hash/5503a7c69d48a2f86fc00b3dc09de686-Abstract-Conference.html | ۲۴ نوامبر ۲۰۲۶: صفحهٔ arXiv (v1 ۲۶ ژوئن ۲۰۲۴، v4 ۲۳ فوریهٔ ۲۰۲۵)، متن HTML v4 (بخش ۳.۲، ۴.۱، ۵، جدول‌های ۱ تا ۳ و ۶)، صفحهٔ ICLR 2025 در نتیجهٔ جست‌وجو | چکیده: «significantly reduces costs … by over 2 times in certain cases»، «without compromising» کیفیت جواب؛ داده: حدود ۸۰ هزار نبرد Chatbot Arena، پس از پالایش حدود ۶۵ هزار مقایسه؛ مدل قوی gpt-4-1106-preview، مدل ضعیف Mixtral 8x7B؛ آزمون‌ها MT Bench، MMLU، GSM8K؛ جدول ۶ (CPT 50٪): MT Bench ۳٫۶۶×، GSM8K ۱٫۴۹×، MMLU ۱٫۴۱× در برابر GPT-4؛ و در همان نقطه، امتیاز مسیریاب کمتر از GPT-4 است: یادداشت جدول‌های ۱ تا ۳ «8.8 is 95% that of GPT-4's score (9.3)» (MT Bench)، MMLU ۷۵ در برابر ۸۱ (۹۲٪)، GSM8K ۷۵ در برابر ۸۶ (۸۷٪)؛ یعنی صرفه‌جویی با کمی افت کیفیت همراه بود (بازبینی دوباره ۲۴ نوامبر ۲۰۲۶) · قاب ۵، ۱۴؛ هوک ۵؛ کامنت پین‌شده |
| R01b | lm-sys/RouteLLM · مخزن کد | https://github.com/lm-sys/RouteLLM | ۲۴ نوامبر ۲۰۲۶ | مجوز **Apache-2.0**؛ README: «reduce costs by up to 85% while maintaining 95% GPT-4 performance» روی MT Bench. **در گفتار استفاده نشد** (ادعای README با چکیده فرق دارد؛ ما فقط چکیده و جدول مقاله را نقل می‌کنیم). هیچ کدی از این مخزن در artifact نیست |
| R02 | Chen, Zaharia, Zou · *FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance* · Transactions on Machine Learning Research (۱۲/۲۰۲۴)؛ نسخهٔ arXiv 2305.05176 (۹ مه ۲۰۲۳) | https://arxiv.org/abs/2305.05176 · نسخهٔ TMLR: https://lingjiaochen.com/papers/2024_FrugalGPT_TMLR.pdf · OpenReview: https://openreview.net/forum?id=cSimKw5p6R | ۲۴ نوامبر ۲۰۲۶: صفحهٔ arXiv؛ متن PDF نسخهٔ TMLR (سطر اول «Published in Transactions on Machine Learning Research (12/2024)»، چکیده، بخش ۳ و شکل ۱ و ۲) | «fees that can differ by two orders of magnitude» (در چکیدهٔ نسخهٔ arXiv مهٔ ۲۰۲۳ هم هست) ← در گفتار «سال دو هزار و بیست‌وسه … تا حدود صد برابر»؛ آبشار: مدل‌ها پشت سر هم صدا زده می‌شوند تا نمرهٔ یک داور از آستانه بگذرد؛ داور یک DistilBERT کوچک؛ «up to a 98% cost reduction» در برابر بهترین مدل تکی، روی HEADLINES (دادهٔ تیترهای خبری مالی)؛ در جدول ۲ صرفه‌جویی بین ۵۰٪ و ۹۸٪ روی داده‌های مختلف · قاب ۲، ۷، ۱۴؛ Short 1؛ هوک ۲ |

## محاسبه‌شده توسط ما (اجرای محلی، ۲۴ نوامبر ۲۰۲۶، بدون هیچ مدل زبانی)

- `python3 artifact/taskset.py` → `artifact/tasks/tasks.json` (seed 22): ۲۰۰ سؤال، ۸۰ تنظیم و ۱۲۰ آزمون؛ هر دسته ۴۰ (۲۰ فارسی، ۲۰ انگلیسی)؛ هیچ سؤال تکراری و هیچ هم‌پوشانی بین تنظیم و آزمون. از ۱۲۰ سؤال آزمون، ۹۶ بیرون از دستهٔ پرخطر و ۲۴ در آن (قاب ۸، ۱۱، ۱۲). **ساختگی (ILLUSTRATIVE)**؛ سه داروی Zelvorin، Tamirex و Orvadin وجود ندارند.
- جواب مرجع: برای تبدیل‌ها، متن‌ها، مسئله‌ها و دوزها با کد حساب شده؛ ۴۰ سؤال ساده دست‌نویس و از دانستنی‌های ثابت (پایتخت‌ها، نماد شیمیایی، تقویم). نمونه‌های روی صفحه عیناً از همین مجموعه‌اند: قاب ۱ «۱۲٬۵۰۰ تومان چند ریال» (CON-fa-09) و «کودک ۲۱ کیلویی، بروشور تامیرکس» (HIG-fa-07)، هر دو از دستهٔ تنظیم؛ قاب ۳ «پایتخت استرالیا» (LOO-fa-11)، «۳٫۷ کیلومتر» (CON-fa-04)، کرایهٔ تاکسی (MUL-fa-03). نمونه‌ها برای روشنی انتخاب شده‌اند، نه به‌عنوان نمایندهٔ سختی دسته؛ همهٔ ۲۰۰ سؤال در `tasks.json` باز است.
- `routing_lab.py plan` → `artifact/results/plan.txt`: ۸۰۰ فراخوانی، حدود ۱۱۰ هزار توکن ورودی (برآورد تقریبی از نویسه).
- `HOMODYNE_MODEL=mock:echo routing_lab.py --selftest` → `artifact/results/MOCK-selftest/`: **داده و قیمت ساختگی؛ نتیجه نیست** و در ویدیو استفاده نمی‌شود.

## نیازمند اجرا [RUN]

- همهٔ عددهای قاب ۱۱، ۱۲ و ۱۳: `run` و بعد `report` (`artifact/README.md`). قیمت هر دو مدل در `artifact/prices.json` با تاریخ خواندن، از صفحهٔ رسمی قیمت همان ارائه‌دهنده. نام و نسخهٔ مدل‌ها از `model_served` در `runs/<run>/items.jsonl`.

## مجوزها

- کد artifact: MIT (فایل `LICENSE.md` مخزن). متن و سؤال‌ها: CC BY-NC-SA 4.0. همه نوشتهٔ خود هومودین؛ هیچ داده یا کدی از RouteLLM یا FrugalGPT کپی نشده.
- RouteLLM: Apache-2.0 (فقط نقل از مقاله). FrugalGPT: فقط نقل از مقاله.
- matplotlib فقط برای ساختن نمودار به‌صورت محلی؛ چیزی از آن منتشر نمی‌شود جز تصویر خروجی.

## آنچه عمداً استفاده نشد

- عدد «۸۵٪» README مخزن RouteLLM و عددهای وبلاگ LMSYS: فقط چکیده و جدول مقاله نقل شد.
- هیچ عددی از R01 یا R02 به‌عنوان پیش‌بینی نتیجهٔ ما؛ هر جا آمده با «روی آزمون‌ها و مدل‌های خودشون».
- قیمت هیچ مدلی در متن نیامده؛ قیمت‌ها را صاحب کانال روز اجرا در `prices.json` می‌نویسد و `report` تاریخش را می‌گوید.
- هیچ عددی از HMD-021 (هزینهٔ آزمایش رزومه): آن قسمت هنوز اجرا نشده است.

</div>
