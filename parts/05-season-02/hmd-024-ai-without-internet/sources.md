<div dir="rtl">

# HMD-024 · منابع

بازبینی: ۲۳ و ۲۴ نوامبر ۲۰۲۶ (۲ و ۳ آذر ۱۴۰۵). هر لینک همان روز باز و خوانده شد؛ صفحه‌های ollama.com و ai.google.dev به ابزار خواندن خودکار پاسخ 403 دادند، پس صفحه‌های ollama.com در مرورگر باز و خوانده شدند، و کارت Gemma به‌جای ai.google.dev از Hugging Face (همان متن) خوانده شد. شناسه‌ها برای این قسمت تازه‌اند (R01 تا R20 در محدودهٔ HMD-024).

## پایهٔ فنی

| شناسه | منبع | لینک | بازبینی | در این قسمت برای |
|---|---|---|---|---|
| R01 (منبع اصلی) | ggml-org · *llama.cpp* (مخزن) | https://github.com/ggml-org/llama.cpp | ۲۳ نوامبر ۲۰۲۶ | توصیف پروژه «LLM inference in C/C++»؛ مجوز MIT. نقطهٔ شروع پژوهش؛ قاب ۳ («پروژهٔ متن‌باز برای اجرای همین مدل‌ها روی کامپیوترهای معمولی») و قاب ۸. |
| R02 (منبع اصلی) | llama.cpp · *tools/quantize/README.md* | https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md | ۲۳ نوامبر ۲۰۲۶ | جدول Llama 3.1 8B: `F16` ۱۶٫۰۰۰۵ بیت بر وزن، **۱۴٫۹۶ GiB**؛ `Q8_0` ۸٫۵۰۰۸، ۷٫۹۵ GiB؛ `Q4_K_M` ۴٫۸۹۴۴ بیت بر وزن، **۴٫۵۸ GiB**. راهنما می‌گوید کوانتیزه‌کردن «may introduce some accuracy loss». · قاب ۳ (۱۵ ← ۴٫۶ گیگ، «تقریباً یک‌سوم» = ۰٫۳۱)؛ هوک ۵؛ Short 1. **مدل ما نیست.** |
| R03 | Ollama Blog · *Ollama's new engine for multimodal models* · ۱۵ مه ۲۰۲۵ | https://ollama.com/blog/multimodal-models | ۲۳ نوامبر ۲۰۲۶ (مرورگر) | «Ollama has so far relied on the ggml-org/llama.cpp project for model support»؛ موتور تازه روی کتابخانهٔ GGML («the tensor library that powers Ollama's inference»). یعنی جملهٔ «Ollama پوستهٔ llama.cpp است» امروز دقیق نیست: Ollama با llama.cpp شروع کرد و مدل‌های تازه را روی موتور خودش با همان کتابخانهٔ GGML اجرا می‌کند. قاب ۸ می‌گوید «اولش روی لاما سی‌پی‌پی ساخته شد، و هنوز از کتابخونهٔ پایه‌ش استفاده می‌کنه». |
| R04 | Ollama Docs · *API: Chat* | https://docs.ollama.com/api/chat | ۲۳ نوامبر ۲۰۲۶ | `stream` (پیش‌فرض true، NDJSON)، `think` (true / false / null)، `format` (json یا JSON schema)، `options` (`seed`، `temperature`، `num_ctx`، `num_predict`)، `keep_alive` («0 to unload immediately»)؛ تکه‌ها `message.content` و `message.thinking`؛ شمارنده‌ها `total_duration`، `load_duration`، `prompt_eval_count`، `prompt_eval_duration`، `eval_count`، `eval_duration` به نانوثانیه. · `ollama_client.py`، قاب ۷ و ۸. |
| R05 | Ollama Docs · *FAQ* | https://docs.ollama.com/faq | ۲۳ نوامبر ۲۰۲۶ | پنجرهٔ پیش‌فرض ۴۰۹۶ توکن (ما `num_ctx 8192` می‌گذاریم)؛ مدل‌ها در `~/.ollama/models`؛ «Ollama runs locally. We don't see your prompts or data when you run locally»؛ پیش‌فرض روی 127.0.0.1:11434؛ `ollama ps` و ستون PROCESSOR؛ مدل‌ها ۵ دقیقه در حافظه می‌مانند؛ حالت فقط‌محلی: `OLLAMA_NO_CLOUD=1` یا `disable_ollama_cloud` در `~/.ollama/server.json`. · قاب ۸، ۱۴؛ `doctor`. |
| R06 | Ollama Docs · *macOS* | https://docs.ollama.com/macos | ۲۳ نوامبر ۲۰۲۶ | «MacOS Sonoma (v14) or newer»؛ «Apple M series (CPU and GPU support)»؛ نصب با کشیدن Ollama.app به Applications؛ حذف: `rm -rf ~/.ollama`. · README، `doctor`. |
| R07 | Ollama · *docs/api.md* (GitHub) | https://github.com/ollama/ollama/blob/main/docs/api.md | ۲۳ نوامبر ۲۰۲۶ | پاسخ `/api/show`: `details.format`، `family`، `parameter_size`، `quantization_level`؛ پاسخ `/api/ps`: `size`، `size_vram`. · `ollama_client.py`، کارت. |
| R08 | Ollama · *Download for macOS* | https://ollama.com/download/mac | ۲۳ نوامبر ۲۰۲۶ (مرورگر) | دستور نصب `curl -fsSL https://ollama.com/install.sh \| sh` و دانلود دستی Ollama.dmg؛ «In the CLI, a cloud model name ends in :cloud». · قاب ۱۴ («مدلی که اسمش با کلاد تموم بشه»)؛ رد مدل‌های `:cloud` در `run --local`. |
| R09 | Ollama · *ollama/ollama releases* (GitHub API) | https://github.com/ollama/ollama/releases | ۲۳ نوامبر ۲۰۲۶ | آخرین نسخه در روز بازبینی: v0.40.17 (۱۰ نوامبر ۲۰۲۶). نسخهٔ واقعی اجرا را `run` در `meta.json` ثبت می‌کند. |
| R21 | Ollama · *LICENSE* (GitHub API) | https://github.com/ollama/ollama/blob/main/LICENSE | ۲۴ نوامبر ۲۰۲۶ | مجوز MIT؛ مبنای «رایگان و متن‌باز» در قاب ۸. |
| R10 | Hugging Face Optimum · *Quantization* (راهنمای مفهومی) | https://huggingface.co/docs/optimum/en/concept_guides/quantization | ۲۳ نوامبر ۲۰۲۶ | تعریف ساده: نمایش وزن‌ها «with low-precision data types like 8-bit integer (int8) instead of the usual 32-bit floating point»؛ حافظهٔ کمتر، محاسبهٔ سریع‌تر. · قاب ۳ (تعریف کوانتیزه‌کردن). |

## مدل‌ها (اندازه، کوانتیزه‌شدن، زبان، مجوز)

| شناسه | منبع | لینک | بازبینی | در این قسمت برای |
|---|---|---|---|---|
| R11 | ollama.com · *qwen3.5* (برچسب‌ها) و صفحهٔ `qwen3.5:2b-q4_K_M` و `qwen3.5:4b-q4_K_M` | https://ollama.com/library/qwen3.5/tags | ۲۳ نوامبر ۲۰۲۶ (مرورگر) | `qwen3.5:2b-q4_K_M` ۱٫۹GB (مدل qwen35، ۱٫۸۸B، Q4_K_M + projector clip ۳۳۱M BF16)؛ `qwen3.5:4b-q4_K_M` ۳٫۳GB (۴٫۲۱B، Q4_K_M + projector ۳۳۴M)؛ پنجرهٔ ۲۵۶K؛ مجوز Apache 2.0؛ پارامترهای پیش‌فرض `temperature 1, top_k 20, top_p 0.95, presence_penalty 1.5` (ما temperature 0 می‌گذاریم). برچسب کوتاه `qwen3.5:4b` بازهٔ «3.3GB - 4.0GB» نشان می‌دهد (ساخت‌های MLX)؛ برای همین برچسب صریح. «1 month ago». · قاب ۴، `models.json`. |
| R12 | Hugging Face · *Qwen/Qwen3.5-2B* (کارت مدل) | https://huggingface.co/Qwen/Qwen3.5-2B | ۲۳ نوامبر ۲۰۲۶ | «Expanded support to 201 languages and dialects»؛ فارسی صریحاً نام برده نشده؛ «Qwen3.5-2B operates in non-thinking mode by default»؛ Apache-2.0؛ همین جمله در صفحهٔ Ollama مدل ۴B (R11). · قاب ۴ («دویست‌ویک زبان و گویش»؛ «اسم فارسی صریح نیامده»). |
| R13 | Qwen Team · *Qwen3: Think Deeper, Act Faster* · ۲۹ آوریل ۲۰۲۵ | https://qwenlm.github.io/blog/qwen3/ | ۲۳ نوامبر ۲۰۲۶ | جدول زبان‌ها: Persian در ردیف Indo-European (۱۱۹ زبان نسل قبل). در گفتار نیامده؛ در `models.json` به‌عنوان «نسل قبلی Persian را نام برده». |
| R14 | Hugging Face · *Qwen/Qwen3-1.7B* | https://huggingface.co/Qwen/Qwen3-1.7B | ۲۳ نوامبر ۲۰۲۶ | «Support of 100+ languages and dialects»؛ thinking به‌طور پیش‌فرض روشن. گزینهٔ جایگزین (`--models qwen3:1.7b`)، انتخاب نشد. |
| R15 | ollama.com · *gemma3* (برچسب‌ها) و صفحهٔ `gemma3:4b-it-q4_K_M` | https://ollama.com/library/gemma3/tags | ۲۳ نوامبر ۲۰۲۶ (مرورگر) | `gemma3:4b-it-q4_K_M` ۳٫۴GB (۳٫۸۸B، Q4_K_M + projector ۴۲۰M)، پنجرهٔ ۱۲۸K؛ `gemma3:1b` ۸۰۶MB، ۳۲K؛ README صفحه: «support for over 140 languages». · قاب ۴. |
| R16 | Hugging Face · *google/gemma-3-4b-it* (کارت مدل) | https://huggingface.co/google/gemma-3-4b-it | ۲۳ نوامبر ۲۰۲۶ | «multilingual support in over 140 languages»؛ «The training dataset includes content in over 140 languages»؛ فارسی نام برده نشده؛ «A limitation of our evaluations was they included only English language prompts»؛ مجوز: gemma. · قاب ۴؛ `models.json`. |
| R17 | Google · *Gemma Terms of Use* (متن کامل در فایل مجوز مدل روی Ollama) | https://ollama.com/library/gemma3/blobs/dd084c7d92a3 (اصل: https://ai.google.dev/gemma/terms) | ۲۳ نوامبر ۲۰۲۶ (مرورگر) | «Last modified: February 21, 2024»؛ بند ۳٫۲: استفاده نباید برای کاربردهای ممنوع در Gemma Prohibited Use Policy باشد؛ بند ۳٫۳: «Google claims no rights in Outputs you generate using Gemma». نتیجه: نشان‌دادن خروجی در ویدیو مشکلی ندارد؛ وزن‌ها را منتشر نمی‌کنیم. |
| R18 | ollama.com · *llama3.2* | https://ollama.com/library/llama3.2 | ۲۳ نوامبر ۲۰۲۶ (مرورگر) | «English, German, French, Italian, Portuguese, Hindi, Spanish, and Thai are officially supported»؛ فارسی نیست؛ انتخاب نشد. |
| R19 | Hugging Face · *CohereLabs/aya-expanse-8b* | https://huggingface.co/CohereLabs/aya-expanse-8b | ۲۴ نوامبر ۲۰۲۶ | Persian در فهرست ۲۳ زبان؛ مجوز CC-BY-NC + Acceptable Use Policy کوهیر. روی Ollama `aya-expanse:8b` ۵٫۰۶GB (R20). انتخاب نشد: برای ۸ گیگ کنار ضبط‌کننده سنگین است و مجوزش غیرتجاری است. |
| R20 | Ollama registry · manifests (`registry.ollama.ai/v2/library/<model>/manifests/<tag>`) | https://registry.ollama.ai/v2/library/qwen3.5/manifests/4b-q4_K_M | ۲۳ نوامبر ۲۰۲۶ | وارسی دوم اندازه و `file_type` (Q4_K_M) هر مدل از روی فایل پیکربندی رجیستری؛ با R11 و R15 می‌خواند. `gemma4:e2b` ۴٫۵۹GB با projector (انتخاب نشد). فقط manifest و config (چند کیلوبایت) خوانده شد؛ هیچ مدلی دانلود نشد. |

## داده و متن‌های این قسمت

- **۳۰ کار (`artifact/task_bank.py`):** همه را هومودین برای همین قسمت نوشته است؛ آدم‌ها، فروشگاه‌ها، قیمت‌ها و تاریخ‌ها ساختگی‌اند. هیچ متن بیرونی استفاده نشده، پس مجوز متن مطرح نیست. دو دفتر بلند (۱۶۰ و ۲۲۰ خط) را کد با بذر ثابت (۲۴ و ۲۰۲۴) می‌سازد.
- **تصویرها:** دک فقط متن و نمودارهای خودمان را دارد. B-roll (لپ‌تاپ، کابل، Finder، ترمینال) را مالک خودش ضبط می‌کند؛ هیچ لوگو یا تصویر بیرونی لازم نیست.

## محاسبه‌شده یا ساخته‌شده توسط ما

- **۱۵ ← ۴٫۶ گیگ:** ۴٫۵۸ ÷ ۱۴٫۹۶ = ۰٫۳۰۶ ≈ «تقریباً یک‌سوم». (GiB؛ در گفتار «گیگابایت»، روی صفحه GiB.)
- **«کمتر از سه‌ونیم گیگابایت» (قاب ۱):** بزرگ‌ترین فایل ما ۳٫۴GB (R15). اگر در روز ضبط مدل دیگری روی صفحه است، با `ollama list` همان روز وارسی شود.
- **اندازهٔ دیسک لازم:** ۱٫۹ + ۳٫۳ + ۳٫۴ = ۸٫۶GB برای مدل‌ها، به‌اضافهٔ برنامهٔ Ollama.
- **خروجی selftest (`artifact/selftest-output.txt`، ۲۴ نوامبر ۲۰۲۶):** سرور ساختگی روی 127.0.0.1 و مدل mock، بدون هیچ تماس شبکه‌ای؛ ردشدن `run --local` با بررسی ساختگی آزموده شد. با `--selftest --net` (یک بار، ۲۴ نوامبر، گذشت) بررسی واقعی هم اجرا می‌شود و `run --local` در زیرفرایندی با `OLLAMA_HOST=127.0.0.1:1` و پوشهٔ موقت، پس به هیچ Ollama یا نتیجهٔ واقعی دست نمی‌زند. **هیچ عدد DEMO در ویدیو نمی‌آید.**

## نیازمند اجرا پیش از ضبط [RUN]

- قاب ۹ تا ۱۳: همهٔ عددها از `python3 parts/05-season-02/hmd-024-ai-without-internet/artifact/offline_lab.py report` پس از `run --local` (آفلاین) و `run --online`. نام و digest مدل، نسخهٔ Ollama، تاریخ اجرا، فرض‌های `cost.json` و تاریخ قیمت (`prices.json`) روی دک و در این فایل ثبت شوند.

## آنچه عمداً استفاده نشد

- هیچ عدد یا تاریخ دربارهٔ قطعی‌های اینترنت در ایران؛ قاب ۲ فقط تجربهٔ مشترک را یادآوری می‌کند.
- هیچ ادعای «مدل X فارسی را خوب/بد می‌فهمد» از منبع بیرونی؛ همین را آزمایش می‌کنیم.
- عدد سرعت یا حافظهٔ مدل‌ها از سایت‌های دیگر؛ فقط اندازه‌گیری خود ما.
- هیچ داور هوش مصنوعی (LLM judge) در نمرهٔ اصلی.

</div>
