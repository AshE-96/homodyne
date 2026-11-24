<div dir="rtl">

# HMD-023 · منابع

بازبینی: ۲۳ نوامبر ۲۰۲۶ (۲ آذر ۱۴۰۵). هر منبع همان روز باز و خوانده شد. شناسه‌ها فقط برای همین قسمت‌اند (R01 تا R10). نقل‌قول‌ها کوتاه و به زبان اصلی‌اند.

| شناسه | منبع | لینک | بازبینی | در این قسمت برای |
|---|---|---|---|---|
| R01 (منبع اصلی) | Jones, Wilkes, Murphy, Smith · *Site Reliability Engineering* (Google)، فصل ۴: «Service Level Objectives» | https://sre.google/sre-book/service-level-objectives/ | ۲۳ نوامبر ۲۰۲۶، متن فصل | تعریف SLI (اندازهٔ کمّی یک جنبه از سرویس) و SLO («a target value or range of values for a service level»)؛ «We generally prefer to work with percentiles rather than the mean»؛ نمونهٔ «99% of Get RPC calls will complete in less than 100 ms». · قاب ۳، ۴؛ کامنت پین |
| R02 | Alejandro Forero Cuervo · همان کتاب، فصل ۲۱: «Handling Overload» | https://sre.google/sre-book/handling-overload/ | ۲۳ نوامبر ۲۰۲۶، متن فصل | جواب سبک‌تر وقتی سرویس زیر بار است (پاسخ تنزل‌یافته ارزان‌تر از پاسخ کامل است)؛ «A moving target makes a poor metric» دربارهٔ «پرس‌وجو در ثانیه» به‌عنوان سنجهٔ ظرفیت؛ کنترل تلاش دوباره سمت کاربر. · قاب ۶، ۱۲ |
| R03 | Mike Ulrich · همان کتاب، فصل ۲۲: «Addressing Cascading Failures» | https://sre.google/sre-book/addressing-cascading-failures/ | ۲۳ نوامبر ۲۰۲۶، بخش‌های Queue Management و Load Shedding and Graceful Degradation | صف کوتاه نسبت به تعداد کارگرها برای ترافیک نسبتاً یکنواخت؛ دور ریختن بخشی از بار پیش از فروپاشی؛ «Graceful degradation shouldn't trigger very often»؛ تلاش‌های دوباره که در لایه‌ها ضرب می‌شوند. · قاب ۱۲؛ مرز ادعا |
| R04 | Grafana k6 · *Thresholds* | https://grafana.com/docs/k6/latest/using-k6/thresholds/ (خوانده از منبع همان صفحه در GitHub: `grafana/k6-docs`، `docs/sources/k6/next/using-k6/thresholds.md`، commit `41b88c2c14` ۱۱ سپتامبر ۲۰۲۶؛ grafana.com به ابزار ما 403 داد) | ۲۳ نوامبر ۲۰۲۶ | «Often, testers use thresholds to codify their SLOs»؛ نمونهٔ `http_req_failed: ['rate<0.01']` و `http_req_duration: ['p(95)<200']`؛ اگر شرطی رد شود، k6 با کد خروج غیرصفر تمام می‌شود. · قاب ۳ |
| R05 | Grafana k6 · *Open and closed models* | منبع: `grafana/k6-docs`، `docs/sources/k6/next/using-k6/scenarios/concepts/open-vs-closed.md` | ۲۳ نوامبر ۲۰۲۶ | در مدل بسته، تکرار بعدی تا پایان قبلی شروع نمی‌شود؛ در مدل باز، رسیدن‌ها مستقل از تمام‌شدن کارند. پایهٔ درس «کاربر هم‌زمان ≠ درخواست در ثانیه». · قاب ۶ |
| R06 | John D. C. Little · «A Proof for the Queuing Formula: L = λW» · *Operations Research* 9(3):383–387، ۱۹۶۱ · doi:10.1287/opre.9.3.383 | https://doi.org/10.1287/opre.9.3.383 (رکورد RePEc: https://econpapers.repec.org/RePEc:inm:oropre:v:9:y:1961:i:3:p:383-387 ؛ خلاصه: https://en.wikipedia.org/wiki/Little%27s_law) | ۲۳ نوامبر ۲۰۲۶، رکورد کتاب‌شناختی و صورت قانون | L = λW: میانگین تعداد در سیستم = نرخ رسیدن × میانگین زمان ماندن، برای سیستم پایا و میانگین بلندمدت. · قاب ۹، ۱۲ |
| R07 | Ollama · *FAQ* (Local) | https://docs.ollama.com/faq (و منبع آن در GitHub: `ollama/ollama`، `docs/faq.mdx`، آخرین commit `afc7c06022` ۲۰ نوامبر ۲۰۲۶) | ۲۳ نوامبر ۲۰۲۶ | `OLLAMA_NUM_PARALLEL`: «The maximum number of parallel requests each model will process at the same time»؛ اگر خالی یا صفر باشد، روی MLX/Metal خودش یک پیش‌فرض محتاطانه برمی‌دارد و در بقیه ۱ است؛ موازی‌بودن، context را چند برابر می‌کند و حافظهٔ بیشتری می‌خواهد. `OLLAMA_MAX_QUEUE` پیش‌فرض ۵۱۲؛ بعد از آن خطای 503. مدل‌ها پیش‌فرض ۵ دقیقه در حافظه می‌مانند (`keep_alive`). روی macOS: `launchctl setenv` و راه‌اندازی دوبارهٔ برنامه. · قاب ۱۰؛ README؛ `run --target ollama` |
| R08 | Ollama · *API: Generate a chat message* | https://docs.ollama.com/api/chat | ۲۳ نوامبر ۲۰۲۶ | `stream` پیش‌فرض true؛ زمان‌ها (`total_duration`، `load_duration`، `eval_duration`) به نانوثانیه؛ `options.num_predict` سقف توکن خروجی؛ `keep_alive` در خود درخواست. · کلاینت `loadgen.py` |
| R09 | Ollama Library · `qwen2.5` (صفحهٔ tags و صفحهٔ `qwen2.5:1.5b`) | https://ollama.com/library/qwen2.5/tags · https://ollama.com/library/qwen2.5:1.5b | ۲۳ نوامبر ۲۰۲۶ (با مرورگر؛ ابزار fetch ما 403 گرفت) | `qwen2.5:1.5b`: digest `65ec06548149`، ۹۸۶ MB، ۱٫۵۴B پارامتر، Q4_K_M، context ۳۲K، مجوز Apache 2.0. همان صفحه: «all models except the 3B and 72B are released under the Apache 2.0 license»؛ یعنی `qwen2.5:3b` (۱٫۹ GB) مجوز دیگری دارد و پیشنهاد ما نیست. · قاب ۱۰؛ README |
| R10 | Qwen · کارت مدل *Qwen2.5-1.5B-Instruct* | https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct | ۲۳ نوامبر ۲۰۲۶ | مجوز apache-2.0؛ ۱٫۵۴ میلیارد پارامتر؛ «over 29 languages» (فارسی در فهرست نام‌برده نیست؛ برای آزمون بار مهم نیست، چون کیفیت جواب را نمی‌سنجیم). · مرز ادعا |

## محاسبه‌شده یا ساخته‌شده توسط ما

- **فرض مدل‌سازی، نه واقعیت منبع‌دار — `contention`:** در سرویس ساختگی هر جریان به ازای هر جای کار مشغولِ دیگر ۱۰٪ کندتر می‌شود (`--contention 0.10`). این عدد را ما انتخاب کردیم تا «چند جای کار روی یک سخت‌افزار» مجانی نباشد؛ هیچ منبعی آن را اندازه نگرفته است. نتیجهٔ سیاست «دو برابر جای کار، همان سخت‌افزار» در قاب ۱۲ مستقیماً از همین فرض می‌آید و در گفتار هم همین گفته می‌شود.
- **انتخاب مدل لپ‌تاپ (`qwen2.5:1.5b`):** فقط متن؛ attention استاندارد، پس `OLLAMA_NUM_PARALLEL` همان‌طور که FAQ می‌گوید رفتار می‌کند؛ حالت «فکر کردن» ندارد، پس زمان تا اولین کلمه تمیز است؛ Apache 2.0؛ ۹۸۶ MB (R09، R10). `qwen2.5:3b` مجوز Qwen Research دارد و کنار گذاشته شد.
- **سرویس ساختگی (`artifact/fake_server.py`) و همهٔ عددهایش:** SIMULATED SERVICE (ILLUSTRATIVE). پارامترها و چهار سیاست قاب ۱۲ را خودمان انتخاب کردیم (چهار جای کار، سرعت‌ها، شروع سرد چهار ثانیه، اندازهٔ صف، کوتاه‌کردن جواب از صف دونفره) و در `artifact/results/simulated/meta.json` ثبت شده‌اند. اجرا: ۲۴ نوامبر ۲۰۲۶، Python 3.11.7، Apple M1، ۸ GB، با `--timescale 0.25` (`config_sha256` در `meta.json`). خلاصه: `artifact/results/simulated/summary.md`.
- **نقطهٔ اشباع نظری بار بسته:** N* = (S + Z) / (S / c)، با S زمان خدمت، Z زمان فکر و c تعداد جای کار؛ فقط در یادداشت دک و README.
- **سقف صف از قانون لیتل:** طول صف مجاز ≈ گذردهی × بودجهٔ انتظار. عددها در قاب ۹ و ۱۲ از همان خروجی شبیه‌سازی.
- **گذردهی:** جواب‌های کامل ÷ طول واقعی مرحله (از شروع تا آخرین جواب یا رها شدن)، نه ۱۲۰ ثانیهٔ رسیدن درخواست‌ها.
- **«جواب کامل نگرفت» ≠ «جواب نگرفت»:** بیشتر درخواست‌هایی که به سقف ۳۰ ثانیه خوردند، اولین کلمه را دیده بودند؛ `summary.md` هر دو را می‌شمارد.
- **selftest (`artifact/selftest-output.txt`، ۲۴ نوامبر ۲۰۲۶، ۲۷ از ۲۷):** فقط سرویس ساختگی روی ۱۲۷٫۰٫۰٫۱ و پوشهٔ موقت؛ هیچ عدد selftest در ویدیو نمی‌آید.

## نیازمند اجرا پیش از ضبط [RUN]

- قاب ۱۰ و ۱۱: همهٔ عددهای لپ‌تاپ از `python3 parts/05-season-02/hmd-023-hundred-users-at-once/artifact/load_lab.py report` پس از `run --target ollama --num-parallel <عدد>`. نسخهٔ Ollama، digest مدل، `OLLAMA_NUM_PARALLEL`، تراشه، حافظه، منبع برق و تاریخ اجرا در `meta.json` همان اجرا ثبت می‌شوند و روی دک می‌آیند.

## آنچه عمداً استفاده نشد

- آزمون بار روی API ابری هیچ شرکتی. `tools/llm.py` خطای 429 را خودش چند بار دوباره امتحان می‌کند، پس رفتار سقف درخواست از بیرون دیده نمی‌شد؛ و بار گذاشتن روی سرویس دیگران بیرون از مرز این قسمت است.
- هر عدد «فلان سرویس با چند کاربر کند شد» از خبرها یا شبکه‌های اجتماعی؛ هیچ‌کدام سخت‌افزار و الگوی بارشان را نمی‌گویند.
- عدد واقعی صف بانک یا سایت‌های ایرانی؛ صحنهٔ بانک یک تصویر آشناست، نه داده.

</div>
