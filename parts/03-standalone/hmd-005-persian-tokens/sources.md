# HMD-005 · منابع

بازبینی: ۲ نوامبر ۲۰۲۶ (۱۱ آبان ۱۴۰۵). هر عدد ویدیو یا از اجرای خودمان است یا از منبع زیر با شناسه.

## منبع اصلی

### R14 · Language Model Tokenizers Introduce Unfairness Between Languages
- **پیوند:** https://arxiv.org/abs/2305.15425 (بازبینی چکیده: ۲ نوامبر ۲۰۲۶)
- **نویسندگان:** Aleksandar Petrov, Emanuele La Malfa, Philip H. S. Torr, Adel Bibi · NeurIPS 2023
- **استفاده در ویدیو:** قاب ۵ — «طول توکنی یک متن ترجمه‌شده بین زبان‌ها می‌تواند تا ۱۵ برابر فرق کند» (از چکیده). ضریب فارسی از این مقاله **نمی‌آید**؛ طبق یادداشت `references.json` («ضریب خاص فارسی از اجرای خودمان تعیین می‌شود»).
- **احتیاط:** عنوان مقاله «بی‌انصافی» را می‌گوید؛ در ویدیو به خود مقاله نسبت داده می‌شود، نه حکم کانال.

## اندازه‌گیری خودمان (اصلی‌ترین شاهد)

- **فایل:** [`artifact/results-2026-11-02.md`](artifact/results-2026-11-02.md) و داده‌های کامل [`artifact/results-2026-11-02.json`](artifact/results-2026-11-02.json)
- **اسکریپت:** [`artifact/count_tokens.py`](artifact/count_tokens.py) · **پیکره:** [`artifact/corpus/pairs.jsonl`](artifact/corpus/pairs.jsonl) (۵۰ جفت خودنوشته، ۷ حوزه؛ نشانی‌ها و شماره‌ها ساختگی‌اند)
- **محیط:** Python 3.11.7 · tiktoken 0.9.0 · transformers 4.49.0 · tokenizers 0.21.0 · macOS · تاریخ اجرا ۲ نوامبر ۲۰۲۶
- **tokenizerها و نسخه‌ها:**

| برچسب | منبع | نسخه/commit |
|---|---|---|
| o200k_base | tiktoken | 0.9.0 |
| cl100k_base | tiktoken | 0.9.0 |
| gpt2 (r50k) | tiktoken | 0.9.0 |
| Llama-2 | `NousResearch/Llama-2-7b-hf` (آینهٔ فایل‌های tokenizer) | 8efe6c9b93655b934e27bd9981e3ec13e55aee9d |
| Llama-3.2 | `unsloth/Llama-3.2-1B-Instruct` (آینه) | 5a8abab4a5d6f164389b1079fb721cfab8d7126c |
| Gemma-3 | `unsloth/gemma-3-1b-it` (آینه) | 5b11413a10db4e486ef16a20101fd028f8f2499c |
| Qwen3 | `Qwen/Qwen3-8B` | b968826d9c46dd6066d109eabc6255188de91218 |
| DeepSeek-V3 | `deepseek-ai/DeepSeek-V3` | e815299b0bcbac849fa540c768ef21845365c9eb |
| Mistral-Nemo | `mistralai/Mistral-Nemo-Instruct-2407` | 04d8a90549d23fc6bd7f642064003592df51e9b3 |

مخزن‌های رسمی Llama و Gemma gated هستند؛ از آینه‌های عمومی استفاده شد. ✔ بررسی ۷ نوامبر ۲۰۲۶ (API فایل‌های Hugging Face، اندازه و SHA): **Gemma-3** فایل‌های tokenizer.json و tokenizer.model در unsloth با مخزن رسمی google بایت‌به‌بایت یکسان‌اند. **Llama-3.2** فایل unsloth با قالب تازهٔ merges ذخیره شده؛ بازنویسی آن دقیقاً همان فایل رسمی را می‌سازد (SHA-1 5cc5f00a5b20…)، پس از نظر کارکرد یکسان است. **Llama-2** فایل tokenizer.model در NousResearch با رسمی یکسان است. پس می‌شود گفت «tokenizer رسمی»، با پانویس «از آینهٔ عمومی».

- **عددهای استفاده‌شده در متن:** جملهٔ نمایشی (۱۵ / ۲۲ / ۴۶ / ۶۹ و بقیه)، میانهٔ نسبت‌ها (۱٫۲۱ تا ۴٫۶۱)، IQR و min/max برای o200k، میانهٔ حوزه‌ها، اثر ی/ک عربی، نیم‌فاصله و رقم‌ها، نسبت حرف‌ها ۰٫۸۸. همه از فایل نتیجه.
- **از ردیف‌های `results-2026-11-02.json` (شمارش ۷ نوامبر ۲۰۲۶):** Gemma-3 در ۷ جفت فارسیِ کم‌توکن‌تر داشت (code-01، num-01، num-02، num-03، num-06، addr-03، addr-04) و ۵ جفت مساوی؛ همان «۷۶٪ fa > en» جدول. o200k: فارسی در ۵۰ از ۵۰ جفت بیشتر.
- **حساب‌های مشتق در قاب ۹ تا ۱۱:** نیم‌فاصله در DeepSeek-V3 = ستون `zwnj_space` (−۱۳٫۵٪ یعنی عوض‌کردن نیم‌فاصله با فاصله ۱۳٫۵٪ توکن کم می‌کند)؛ رقم Gemma-3 = ستون `latin_digits` (+۱۴٫۳٪ یعنی رقم لاتین گران‌تر)؛ ۷۲٪ = ۱ ÷ ۱٫۳۹.

## تیزر قاب ۱۴ (از HMD-006)

- «یک مدل سه برابر کمتر خطا کرده» و کارت‌های `26%` / `75%` روی دک: جدول SimpleQA در R01 (OpenAI، «Why Language Models Hallucinate»، سپتامبر ۲۰۲۵؛ https://openai.com/index/why-language-models-hallucinate/)، تأییدشده در `parts/02-benchmarking/e03-what-exactly-are-we-measuring/sources.md` (۷ نوامبر ۲۰۲۶). ۷۵ ÷ ۲۶ ≈ ۲٫۹.

## نسبت tokenizer به مدل

- **tiktoken** · https://github.com/openai/tiktoken — نقشهٔ `MODEL_TO_ENCODING` در نسخهٔ 0.9.0 (بررسی‌شده در محیط محلی): `gpt-4o`, `o1`, `o3` → `o200k_base`؛ `gpt-4`, `gpt-3.5-turbo` → `cl100k_base`؛ `gpt2` → `gpt2`.
- **استفاده:** قاب ۴ و ۷ فقط با عبارت «tiktoken آن را به … نسبت می‌دهد». دربارهٔ اینکه محصول امروز کدام tokenizer را دارد ادعا نمی‌شود.

## قیمت

- هیچ قیمتی در ویدیو گفته نمی‌شود. فرمول: `cost = tokens × price_per_token`؛ ورودی و خروجی جدا. اگر در توضیحات یا Short مثال قیمت لازم شد: صفحهٔ رسمی قیمت همان سرویس، همان روز، با لینک ✔.

## منابعی که عمداً استفاده نشدند

- ادعای «اولین پژوهش دربارهٔ توکن فارسی» (حذف طبق `episodes.json`).
- latency یا کیفیت پاسخ فارسی: اندازه گرفته نشده.
