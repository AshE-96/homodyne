# HMD-007 · می‌شود با یک متن، دستیار AI را از کارش منحرف کرد؟

**قالب:** AI in Production (مستقل) · **فصل ۱، پس از HMD-S03** · **وضعیت:** آمادهٔ ضبط (۲۶ نوامبر ۲۰۲۶: دو ماجرای واقعی و مستند در قاب ۴ و ۹). قاب ۱۱ می‌گوید مدل واقعی هنوز اجرا نشده (ویدیوی پیگیری).
**زمان برآوردی:** حدود ۱۲ دقیقه (گفتار ۱۱:۵۵) · **واژهٔ گفتاری:** ۱۶۶۳ (متن v6) · **قاب:** 14 · **قاب‌های دک:** 14

**جملهٔ مرکزی:** برای مدل زبانی، دستور تو و متن سند در یک جریان واژه می‌رسند؛ پس یک سند می‌تواند دستور بدهد. برچسب «داده» (spotlighting) از مدل می‌خواهد گول نخورد؛ حداقل دسترسی و تأیید انسانی خسارت را محدود می‌کند حتی وقتی گول خورد، ولی جلوی جملهٔ گمراه‌کننده در جواب را نمی‌گیرد.

**مرز ادعا:** ۲۰ سند ساختگی و ابزار قلابی، گواهی امنیت هیچ سامانهٔ واقعی نیست. مدل‌های جایگزین ILLUSTRATIVE‌اند. هیچ نرخ موفقیت حمله یا دفاعی برای مدل واقعی از پیش نوشته نشده. دو ماجرای واقعی (CVE-2025-32711 در Microsoft 365 Copilot؛ دعوت‌نامهٔ تقویم و Gemini) یافتهٔ پژوهشگر و بسته‌شده‌اند، نه آسیب ثبت‌شده به کاربر؛ ما تکرارشان نکردیم.

## چه چیزی واقعی است و چه چیزی ساختگی

| قاب | چیز | وضعیت | منبع |
|---|---|---|---|
| ۴ | کارت پروندهٔ CVE-2025-32711 (تاریخ، Critical 9.3، Exploited: No، fully mitigated، یابنده) | **واقعی** | NVD و MSRC → [`artifact/derived/cve-2025-32711.json`](artifact/derived/cve-2025-32711.json) |
| ۴ | سه قدم ایمیل ← سؤال عادی ← خروج داده | واقعی، به روایت یابنده؛ متن کارت از ماست | مرور Reddy و Gujral (arXiv 2509.10540)؛ بردار MSRC `UI:N` |
| ۹ | عکس «Thanks» ← «Boiler turned on» | **واقعی** (آزمایش کنترل‌شدهٔ پژوهشگرها روی حساب‌های خودشان) | [`media/CREDITS.md`](media/CREDITS.md)، arXiv 2508.12175، CC BY 4.0 |
| ۸، ۱۱ | ۵۰٪ ← ۲٪ (Hines) و ۱٫۴٪ (Anthropic) | واقعی، از خود منبع؛ با دموی ما قابل‌مقایسه نیست | `sources.md` |
| ۱، ۵–۱۰ | فاکتور، ۲۰ سند، trace و جدول‌ها | **ساختگی / ILLUSTRATIVE** (مدل جایگزین قاعده‌محور) | `artifact/` |
| ۱۱ | نتیجهٔ مدل واقعی روی ۲۰ سند | **NOT RUN YET** | `artifact/ollama_adapter.py` برای ویدیوی پیگیری |

## فایل‌ها

| فایل | چیست |
|---|---|
| [`script-fa.md`](script-fa.md) | متن ضبط v5، ۱۴ قاب (قاب ۱۱: NOT RUN YET + شاهد بیرونی) |
| [`hooks-fa.md`](hooks-fa.md) | پنج هوک + توصیه (برنده: Story-Open) |
| [`package-fa.md`](package-fa.md) | بستهٔ انتشار کامل |
| [`deck-fa.html`](deck-fa.html) | دک ضبط v6، فارسی و راست‌به‌چپ: کاور + ۱۴ قاب (→ ← · F · H · N) |
| [`deck-en.html`](deck-en.html) | همان دک به انگلیسی، با همان قاب‌ها و همان ترتیب |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ هر دو دک؛ بعد از ویرایش `make decks` |
| [`sources.md`](sources.md) | R33، CVE-2025-32711 (NVD/MSRC)، Nassi و همکاران ۲۰۲۵، OWASP LLM01، Hines 2024، Greshake 2023؛ و آنچه رد شد |
| [`media/CREDITS.md`](media/CREDITS.md) | اعتبار عکس قاب ۹ و فهرست «دانلود نشد» |
| [`artifact/injection_lab.py`](artifact/injection_lab.py) | آزمایشگاه آفلاین: ابزار قلابی، چهار حالت (baseline، spotlight، least_privilege، combined)، سنجه‌ها، trace |
| [`artifact/cases.json`](artifact/cases.json) | ۲۰ سند ساختگی: ۱۲ حمله (۷ ابزاری، ۵ فقط-جواب)، ۸ سالم |
| [`artifact/ollama_adapter.py`](artifact/ollama_adapter.py) | ویدیوی پیگیری: مدل محلی Ollama، رایگان، فقط loopback (هر OLLAMA_HOST دیگری رد می‌شود)؛ `--selftest` آفلاین |
| [`artifact/adapter_template.py`](artifact/adapter_template.py) | راهنما و قالب وصل‌کردن هر سرور سازگار با OpenAI (پیش‌فرض خاموش) |
| [`artifact/cve_record.py`](artifact/cve_record.py) | استخراج چند فیلد پروندهٔ CVE-2025-32711 از NVD و MSRC؛ `--selftest` آفلاین |
| [`artifact/derived/`](artifact/derived/) | `cve-2025-32711.json` + `SOURCE.txt` (URL، sha256، فرمان). دادهٔ خام در `artifact/data/` (git-ignored) |
| [`artifact/results-illustrative-2026-11-02.md`](artifact/results-illustrative-2026-11-02.md) | خروجی دو مدل جایگزین (ILLUSTRATIVE) |
| [`artifact/trace-A01-illustrative-2026-11-02.txt`](artifact/trace-A01-illustrative-2026-11-02.txt) | trace سند A01 برای دموی قاب ۷ و ۹ |

### اجرا

```bash
cd parts/03-standalone/hmd-007-prompt-injection/artifact
python3 injection_lab.py                                  # دو مدل جایگزین × چهار حالت (ILLUSTRATIVE)
python3 injection_lab.py --trace A01 --model naive        # لاگ قدم‌به‌قدم برای دمو
python3 ollama_adapter.py --selftest && python3 cve_record.py --selftest   # آزمون‌های آفلاین
# ویدیوی پیگیری: مدل واقعی محلی و رایگان (برای ویدیوی پیگیری؛ فقط 127.0.0.1):
ollama pull llama3.2:3b
export HMD007_OLLAMA_MODEL=llama3.2:3b
python3 injection_lab.py --model ollama_adapter:model --conditions baseline        # اول: errors باید 0 باشد
python3 injection_lab.py --model ollama_adapter:model --out results-ollama-<model>-<date>.md --json results-ollama-<model>-<date>.json
python3 injection_lab.py --model ollama_adapter:model --trace A01                   # trace جلوی دوربین
```

هر تابعی با امضای `model(messages, tools) -> {"answer": str, "tool_calls": [...]}` را می‌شود با `--model ماژول:تابع` وصل کرد. خود harness ابزارها را اجرا، مجوزها و دروازهٔ تأیید را اعمال و نمره را حساب می‌کند.

## پیش از ضبط باید حل شود

- [x] تصمیم ۷ نوامبر ۲۰۲۶: اجرای مدل واقعی به ویدیوی پیگیری رفت؛ قاب ۱۱ و دک بازنویسی شدند.
- [x] R33 در ۷ نوامبر ۲۰۲۶ تأیید شد: نمودار Opus 4.5 «8.0%، 7.6%، 1.4%» (مدل تنها، محافظ قدیم، محافظ بهبودیافته)؛ متن مقاله «A 1% attack success rate» می‌گوید، پس در گفتار «تو نمودارشون حدود ۱٫۴٪». جملهٔ «far from a solved problem» تأیید شد.
- [x] ۲۶ نوامبر ۲۰۲۶: اجرای دوبارهٔ مدل‌های جایگزین؛ با فایل‌های illustrative یکی است.
- [x] قاب ۱۱ از ۷ نوامبر «اجرای مدل واقعی در ویدیوی جدا» را می‌گوید و هیچ نرخی برای مدل ما ندارد.
- [x] ۲۶ نوامبر ۲۰۲۶: CVE-2025-32711 (NVD، MSRC) و arXiv 2508.12175 خوانده و ثبت شد؛ زمان‌های قاب‌ها با ۱۴۰ واژه در دقیقه دوباره تنظیم شد (دک، فصل‌ها، کارت‌ها).
- [ ] صفحهٔ Aim Labs دربارهٔ EchoLeak را خودت در مرورگر باز کن و دو جملهٔ قاب ۴ را با آن تطبیق بده (به درخواست خودکار ما 403 داد).
- [ ] `make teleprompter` (برگهٔ ضبط و تله‌پرامپتر هنوز متن و زمان‌های قبلی را دارند).

## چه چیزی را هنگام ضبط بگیری

- **قاب ۴ (اختیاری):** ضبط صفحهٔ https://nvd.nist.gov/vuln/detail/CVE-2025-32711 که خودت باز می‌کنی؛ روی شرح یک‌خطی و تاریخ ۰۶/۱۱/۲۰۲۵ زوم کن. لوگو یا صفحهٔ خود محصول را نشان نده.
- **قاب ۷:** ترمینال `python3 artifact/injection_lab.py --trace A01 --model naive` (بزرگ، چهار خط اصلی).
- **قاب ۹:** همان trace؛ بخش `least_privilege` با دو خط BLOCKED. عکس آبگرمکن از `media/` با زیرنویس اعتبار.
- **قاب ۱۰:** ضبط صفحهٔ `artifact/cases.json` روی A03 و A06.
- **ویدیوی پیگیری:** با Ollama محلی، همان سه فرمان بالا؛ `ollama --version` و `ollama show <model>` را هم ضبط کن.

**زنجیره:** قبلی HMD-S03 (AlphaFold، سالک و تب کریمه‌کنگو) → بعدی HMD-S04 (AI و پیش‌بینی طوفان).
