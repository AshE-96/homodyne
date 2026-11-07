# HMD-005 · چرا نوشتن فارسی برای بعضی AIها توکن بیشتری می‌برد؟

**قالب:** Benchmark Lab (مستقل) · **فصل ۱، جایگاه پس از HMD-004** · **وضعیت:** آمادهٔ تمرین — اندازه‌گیری واقعاً اجرا شده؛ هیچ نتیجهٔ اجرانشده‌ای ندارد.
**زمان برآوردی:** ۱۲ تا ۱۴ دقیقه · **واژهٔ گفتاری:** 1,518 · **قاب:** 14 · **قاب‌های دک:** 14

**جملهٔ مرکزی:** متن فارسی ما معمولاً حرف کمتری از معادل انگلیسی‌اش دارد (میانه ۰٫۸۸)، اما tokenizerها آن را ۱٫۲۱ تا ۴٫۶۱ برابر توکن می‌کنند؛ بسته به اینکه کدام tokenizer بخواند.

**مرز ادعا:** توکن بیشتر یعنی سهم بیشتر از بودجه و سقف متن، نه کیفیت پایین‌تر. ۵۰ جفت جملهٔ خودنوشته، نمایندهٔ همهٔ متن‌های فارسی نیستند. محصول امروزِ هیچ شرکتی را نسبت نمی‌دهیم.

## سرتیتر اندازه‌گیری (۲ نوامبر ۲۰۲۶)

| tokenizer | میانهٔ نسبت fa/en | IQR |
|---|---:|---|
| Gemma-3 | 1.21 | 1.05–1.38 |
| Mistral-Nemo | 1.29 | 1.15–1.45 |
| Llama-3.2 | 1.39 | 1.19–1.46 |
| o200k_base | 1.39 | 1.23–1.50 |
| DeepSeek-V3 | 1.63 | 1.43–1.85 |
| Qwen3 | 2.30 | 1.90–2.59 |
| cl100k_base | 2.92 | 2.59–3.32 |
| Llama-2 | 3.42 | 2.90–3.87 |
| gpt2 (r50k) | 4.61 | 4.00–5.32 |

اثرها (میانهٔ تغییر توکن فارسی): «ی/ک» عربی +۶٫۷٪ (o200k)، +۱۱٫۵٪ (Llama-3.2، Gemma-3)؛ نیم‌فاصله→فاصله ≈۰٪ روی بیشتر tokenizerها ولی −۱۳٫۵٪ روی DeepSeek-V3؛ رقم لاتین به‌جای فارسی −۸٫۳٪ (o200k)، −۲۱٫۲٪ (cl100k)، +۱۴٫۳٪ (Gemma-3). جزئیات: [`artifact/results-2026-11-02.md`](artifact/results-2026-11-02.md).

## فایل‌ها

| فایل | چیست |
|---|---|
| [`script-fa.md`](script-fa.md) | متن ضبط v5، ۱۴ قاب |
| [`hooks-fa.md`](hooks-fa.md) | پنج هوک + توصیه (برنده: Shock/Contradiction) |
| [`package-fa.md`](package-fa.md) | عنوان، تامبنیل A/B/C، توضیحات، فصل‌ها، تگ، کامنت، End screen، دو Short، Community |
| [`deck.html`](deck.html) | دک ضبط، ۱۴ قاب، بدون منبع بیرونی |
| [`sources.md`](sources.md) | منابع، نسخهٔ دقیق tokenizerها |
| [`artifact/count_tokens.py`](artifact/count_tokens.py) | اسکریپت شمارش (tiktoken + tokenizerهای باز HF؛ اگر یکی بار نشود، رد می‌شود و گزارش می‌دهد) |
| [`artifact/corpus/pairs.jsonl`](artifact/corpus/pairs.jsonl) | ۵۰ جفت فارسی/انگلیسی خودنوشته در ۷ حوزه |
| [`artifact/results-2026-11-02.md`](artifact/results-2026-11-02.md) · [`.json`](artifact/results-2026-11-02.json) | خروجی اجرای واقعی |

### اجرای فایل همراه

```bash
python3 -m pip install tiktoken==0.9.0 transformers==4.49.0   # transformers اختیاری است
python3 parts/03-standalone/hmd-005-persian-tokens/artifact/count_tokens.py            # دانلود tokenizerها در اولین اجرا
python3 parts/03-standalone/hmd-005-persian-tokens/artifact/count_tokens.py --offline  # فقط کش محلی
python3 parts/03-standalone/hmd-005-persian-tokens/artifact/count_tokens.py --only o200k_base cl100k_base
```

خروجی با تاریخ روز در کنار اسکریپت نوشته می‌شود (`results-YYYY-MM-DD.md/json`). برای متن خودت، یک خط به `pairs.jsonl` اضافه کن: `{"id": "...", "domain": "...", "fa": "...", "en": "..."}`.

## پیش از ضبط باید حل شود

- [x] ✔ آینه‌های Llama-3.2 و Gemma-3 (unsloth) و Llama-2 (NousResearch): یکسان‌بودن فایل tokenizer با مخزن رسمی را بررسی کن، یا روی صفحه بگو «tokenizer files via public mirror». (تأیید ۷ نوامبر ۲۰۲۶)
- [x] ✔ قیمت: در ویدیو قیمتی گفته نمی‌شود؛ اگر در توضیحات یا Short لازم شد، فقط از صفحهٔ رسمی همان روز با لینک. (تأیید ۷ نوامبر ۲۰۲۶)
- [ ] اجرای دوبارهٔ `count_tokens.py --offline` و تطبیق با `results-2026-11-02.md`.
- [ ] خوانش آزمایشی و تنظیم زمان قاب‌ها و `data-start` دک.

**زنجیره:** قبلی HMD-004 (مدل اول جدول) → بعدی [HMD-006](../../02-benchmarking/e03-what-exactly-are-we-measuring/README.md) (خطای کم‌تر).
