# HMD-005 · چرا نوشتن فارسی برای بعضی AIها توکن بیشتری می‌برد؟

**قالب:** Benchmark Lab (مستقل) · **فصل ۱، جایگاه پس از HMD-K01** · **وضعیت:** آمادهٔ تمرین — اندازه‌گیری واقعاً اجرا شده؛ هیچ نتیجهٔ اجرانشده‌ای ندارد.
**زمان برآوردی:** حدود ۱۳ دقیقه · **واژهٔ گفتاری:** ۱۷۹۱ · **قاب:** 15 · **قاب‌های دک:** 15

**جملهٔ مرکزی:** متن فارسی ما معمولاً حرف کمتری از معادل انگلیسی‌اش دارد (میانه ۰٫۸۸)، اما tokenizerها آن را ۱٫۲۱ تا ۴٫۶۱ برابر توکن می‌کنند؛ بسته به اینکه کدام tokenizer بخواند.

**مرز ادعا:** توکن بیشتر یعنی سهم بیشتر از بودجه و سقف متن، نه کیفیت پایین‌تر. ۵۰ جفت جملهٔ خودنوشته، نمایندهٔ همهٔ متن‌های فارسی نیستند؛ روی ۱۰۱۲ جملهٔ ترجمهٔ حرفه‌ای FLORES-200 همهٔ نسبت‌ها بالاتر بودند (پس دست‌کم در مقایسه با آن جمله‌ها، ۵۰ جفت شکاف را بزرگ‌تر از واقع نشان نمی‌دهند). محصول امروزِ هیچ شرکتی را نسبت نمی‌دهیم.

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

## دادهٔ واقعی تازه (۲۶ نوامبر ۲۰۲۶)

| قاب | چه | منبع | نتیجه |
|---|---|---|---|
| ۵ | ردیف فارسی مقالهٔ R14 | Petrov و همکاران، پیوست C | cl100k ۳٫۲۸ · GPT-2 ۵٫۳۲ |
| ۸ | اعلام OpenAI | Hello GPT-4o، ۱۳ مه ۲۰۲۴: «۶۱ به ۳۲» | شمارش ما از همان جمله: ۶۳ ← ۳۲ |
| ۸ | Qwen3 ← Qwen3.5 | کارت مدل Qwen3.5 (۲۰۱ زبان) | ۲٫۳۰ ← ۱٫۵۰ روی ۵۰ جفت |
| ۸ | Llama-2 ← PersianMind | دانشگاه تهران، arXiv 2401.06466: ۵۵ تکهٔ عربی/فارسی از ۳۲٬۰۰۰ | ۳٫۴۲ ← ۱٫۱۱ |
| ۱۳ | FLORES-200 devtest (۱۰۱۲ جمله، CC BY-SA 4.0) | NLLB Team | همهٔ نسبت‌ها بالاتر؛ gpt2 ۵٫۲۵ و cl100k ۳٫۲۶ نزدیک R14 |
| ۱، ۳، ۴، ۸، ۱۱ | صفحهٔ آمادهٔ ضبط توکن‌های رنگی | `artifact/token-view.html` | ۱۲ tokenizer × ۳ جمله، بدون اینترنت |
| ۱۰ | عکس کیبورد فارسی | Wikimedia Commons، CC0 | روی دک |

## فایل‌ها

| فایل | چیست |
|---|---|
| [`script-fa.md`](script-fa.md) | متن ضبط v6، ۱۵ قاب |
| [`hooks-fa.md`](hooks-fa.md) | پنج هوک + توصیه (برنده: Shock/Contradiction) |
| [`package-fa.md`](package-fa.md) | عنوان، تامبنیل A/B/C، توضیحات، فصل‌ها، تگ، کامنت، End screen، دو Short، Community |
| [`deck-fa.html`](deck-fa.html) | دک ضبط v6، فارسی و راست‌به‌چپ: کاور + ۱۵ قاب (→ ← · F · H · N) |
| [`deck-en.html`](deck-en.html) | همان دک به انگلیسی، با همان قاب‌ها و همان ترتیب |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ هر دو دک؛ بعد از ویرایش `make decks` |
| [`sources.md`](sources.md) | منابع، نسخهٔ دقیق tokenizerها |
| [`artifact/count_tokens.py`](artifact/count_tokens.py) | اسکریپت شمارش (tiktoken + tokenizerهای باز HF؛ اگر یکی بار نشود، رد می‌شود و گزارش می‌دهد) |
| [`artifact/corpus/pairs.jsonl`](artifact/corpus/pairs.jsonl) | ۵۰ جفت فارسی/انگلیسی خودنوشته در ۷ حوزه |
| [`artifact/results-2026-11-02.md`](artifact/results-2026-11-02.md) · [`.json`](artifact/results-2026-11-02.json) | خروجی اجرای واقعی (۲۶ نوامبر ۲۰۲۶ بازاجرا شد؛ بایت‌به‌بایت یکسان) |
| [`artifact/crosscheck.py`](artifact/crosscheck.py) | ۹ tokenizer + Qwen3.5، PersianMind، gpt-oss روی ۵۰ جفت، FLORES-200 و جملهٔ OpenAI؛ `--selftest` |
| [`artifact/derived/crosscheck-2026-11-26.csv`](artifact/derived/crosscheck-2026-11-26.csv) · [`.json`](artifact/derived/crosscheck-2026-11-26.json) · [`SOURCE.txt`](artifact/derived/SOURCE.txt) | خروجی بررسی متقابل؛ منبع، مجوز، sha256 و فرمان دقیق |
| [`artifact/token_view.py`](artifact/token_view.py) → [`artifact/token-view.html`](artifact/token-view.html) | صفحهٔ ضبط توکن‌های رنگی (←/→ tokenizer، ↑/↓ جمله، A همهٔ میله‌ها)؛ `--selftest` |
| [`media/CREDITS.md`](media/CREDITS.md) | اعتبار تصویرها و متن‌ها + فهرست «دانلود نشد» |

### اجرای فایل همراه

```bash
python3 -m pip install tiktoken==0.9.0 transformers==4.49.0   # transformers اختیاری است
python3 parts/03-standalone/hmd-005-persian-tokens/artifact/count_tokens.py            # دانلود tokenizerها در اولین اجرا
python3 parts/03-standalone/hmd-005-persian-tokens/artifact/count_tokens.py --offline  # فقط کش محلی
python3 parts/03-standalone/hmd-005-persian-tokens/artifact/count_tokens.py --only o200k_base cl100k_base

# بررسی متقابل و صفحهٔ ضبط (FLORES یک بار، ~۲۵ مگابایت، در artifact/data/ که git-ignored است)
mkdir -p parts/03-standalone/hmd-005-persian-tokens/artifact/data/flores200
curl -L -o parts/03-standalone/hmd-005-persian-tokens/artifact/data/flores200/flores200_dataset.tar.gz https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz
cd parts/03-standalone/hmd-005-persian-tokens/artifact
python3 -I crosscheck.py --selftest && python3 -I token_view.py --selftest
python3 -I crosscheck.py --flores data/flores200/flores200_dataset.tar.gz
python3 -I token_view.py
```

خروجی `count_tokens.py` با تاریخ روز در کنار اسکریپت نوشته می‌شود (`results-YYYY-MM-DD.md/json`)؛ `crosscheck.py` در `derived/`؛ `token_view.py` در `token-view.html`. برای متن خودت، یک خط به `pairs.jsonl` اضافه کن: `{"id": "...", "domain": "...", "fa": "...", "en": "..."}`.

## پیش از ضبط باید حل شود

- [x] ✔ آینه‌های Llama-3.2 و Gemma-3 (unsloth) و Llama-2 (NousResearch): یکسان‌بودن فایل tokenizer با مخزن رسمی را بررسی کن، یا روی صفحه بگو «tokenizer files via public mirror». (تأیید ۷ نوامبر ۲۰۲۶)
- [x] ✔ قیمت: در ویدیو قیمتی گفته نمی‌شود؛ اگر در توضیحات یا Short لازم شد، فقط از صفحهٔ رسمی همان روز با لینک. (تأیید ۷ نوامبر ۲۰۲۶)
- [x] ✔ اجرای دوبارهٔ `count_tokens.py --offline` و تطبیق با `results-2026-11-02.md` (۲۶ نوامبر ۲۰۲۶: بایت‌به‌بایت یکسان).
- [ ] خوانش آزمایشی و تنظیم زمان قاب‌ها و `data-start` دک (زمان‌ها برای ۱۳۰ تا ۱۵۰ واژه در دقیقه چیده شده‌اند).
- [ ] پیش از ضبط `artifact/token-view.html` را یک بار در مرورگر خودت باز کن و کلیدها را امتحان کن (فهرست ضبط‌ها در `media/CREDITS.md` و پایین همین فایل).

## چه چیزهایی را هنگام ضبط بگیر

- **ضبط صفحهٔ `artifact/token-view.html`** (تمام‌صفحه): `#s=demo&t=o200k_base` (قاب ۳)، سپس → تا cl100k_base و gpt2 (r50k) (قاب ۴)؛ `#s=gpt4o&t=cl100k_base` → o200k_base و `#s=demo&t=Llama-2` → PersianMind (قاب ۸)؛ `#s=demo&t=DeepSeek-V3` (قاب ۱۱، دو تکهٔ بایتی نیم‌فاصله)؛ کلید A برای نمای همهٔ میله‌ها.
- **ترمینال:** `python3 artifact/count_tokens.py --offline` (قاب ۶) و اختیاری `python3 -I artifact/crosscheck.py --flores … --offline` (قاب ۱۳).
- **صفحه‌هایی که خودت باز می‌کنی و ضبط می‌کنی (بازنشر نمی‌کنیم):** https://openai.com/index/hello-gpt-4o/ بخش «Language tokenization» (قاب ۸)؛ https://huggingface.co/Qwen/Qwen3.5-9B (قاب ۸)؛ https://arxiv.org/abs/2401.06466 صفحهٔ اول (قاب ۸)؛ https://arxiv.org/abs/2305.15425 (قاب ۵).
- **دوربین:** نمای نزدیک کیبورد گوشی خودت، «ی» فارسی و «ي» عربی (قاب ۱۰)؛ عکس CC0 در `media/` جایگزین است.

**زنجیره:** قبلی HMD-K01 (AI در کنکور؛ «چرا یکی از مدل‌ها برای فارسی چند برابر توکن سوزوند؟») → بعدی HMD-S02 (مسابقهٔ شطرنج مدل‌های AI، زنده روی صفحه).
