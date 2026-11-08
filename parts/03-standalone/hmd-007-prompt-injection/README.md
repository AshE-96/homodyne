# HMD-007 · می‌شود با یک متن، دستیار AI را از کارش منحرف کرد؟

**قالب:** AI in Production (مستقل) · **فصل ۱، پس از HMD-006** · **وضعیت:** آمادهٔ ضبط. قاب ۱۱ می‌گوید مدل واقعی هنوز اجرا نشده (ویدیوی پیگیری).
**زمان برآوردی:** ۱۲ تا ۱۴ دقیقه · **واژهٔ گفتاری:** ۱۵۹۹ (متن v6) · **قاب:** 14 · **قاب‌های دک:** 14

**جملهٔ مرکزی:** برای مدل زبانی، دستور تو و متن سند در یک جریان واژه می‌رسند؛ پس یک سند می‌تواند دستور بدهد. برچسب «داده» (spotlighting) از مدل می‌خواهد گول نخورد؛ حداقل دسترسی و تأیید انسانی خسارت را محدود می‌کند حتی وقتی گول خورد، ولی جلوی جملهٔ گمراه‌کننده در جواب را نمی‌گیرد.

**مرز ادعا:** ۲۰ سند ساختگی و ابزار قلابی، گواهی امنیت هیچ سامانهٔ واقعی نیست. مدل‌های جایگزین ILLUSTRATIVE‌اند. هیچ نرخ موفقیت حمله یا دفاعی برای مدل واقعی از پیش نوشته نشده.

## فایل‌ها

| فایل | چیست |
|---|---|
| [`script-fa.md`](script-fa.md) | متن ضبط v5، ۱۴ قاب (قاب ۱۱: NOT RUN YET + شاهد بیرونی) |
| [`hooks-fa.md`](hooks-fa.md) | پنج هوک + توصیه (برنده: Story-Open) |
| [`package-fa.md`](package-fa.md) | بستهٔ انتشار کامل |
| [`deck-fa.html`](deck-fa.html) | دک ضبط v6، فارسی و راست‌به‌چپ: کاور + ۱۴ قاب (→ ← · F · H · N) |
| [`deck-en.html`](deck-en.html) | همان دک به انگلیسی، با همان قاب‌ها و همان ترتیب |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ هر دو دک؛ بعد از ویرایش `make decks` |
| [`sources.md`](sources.md) | R33، OWASP LLM01، Hines 2024، Greshake 2023 |
| [`artifact/injection_lab.py`](artifact/injection_lab.py) | آزمایشگاه آفلاین: ابزار قلابی، چهار حالت (baseline، spotlight، least_privilege، combined)، سنجه‌ها، trace |
| [`artifact/cases.json`](artifact/cases.json) | ۲۰ سند ساختگی: ۱۲ حمله (۷ ابزاری، ۵ فقط-جواب)، ۸ سالم |
| [`artifact/adapter_template.py`](artifact/adapter_template.py) | راهنما و قالب وصل‌کردن مدل واقعی (پیش‌فرض خاموش) |
| [`artifact/results-illustrative-2026-11-02.md`](artifact/results-illustrative-2026-11-02.md) | خروجی دو مدل جایگزین (ILLUSTRATIVE) |
| [`artifact/trace-A01-illustrative-2026-11-02.txt`](artifact/trace-A01-illustrative-2026-11-02.txt) | trace سند A01 برای دموی قاب ۷ و ۹ |

### اجرا

```bash
cd parts/03-standalone/hmd-007-prompt-injection/artifact
python3 injection_lab.py                                  # دو مدل جایگزین × چهار حالت (ILLUSTRATIVE)
python3 injection_lab.py --trace A01 --model naive        # لاگ قدم‌به‌قدم برای دمو
# مدل واقعی (برای ویدیوی پیگیری) — ترجیحاً محلی (Ollama / llama.cpp) تا هیچ داده‌ای بیرون نرود:
export HMD007_ENABLE=1 HMD007_BASE_URL=http://localhost:11434/v1 HMD007_MODEL=<model>
python3 injection_lab.py --model adapter_template:model --out results-<model>-<date>.md --json results-<model>-<date>.json
```

هر تابعی با امضای `model(messages, tools) -> {"answer": str, "tool_calls": [...]}` را می‌شود با `--model ماژول:تابع` وصل کرد. خود harness ابزارها را اجرا، مجوزها و دروازهٔ تأیید را اعمال و نمره را حساب می‌کند.

## پیش از ضبط باید حل شود

- [x] تصمیم ۷ نوامبر ۲۰۲۶: اجرای مدل واقعی به ویدیوی پیگیری رفت؛ قاب ۱۱ و دک بازنویسی شدند.
- [x] R33 در ۷ نوامبر ۲۰۲۶ تأیید شد: نمودار Opus 4.5 «8.0%، 7.6%، 1.4%» (مدل تنها، محافظ قدیم، محافظ بهبودیافته)؛ متن مقاله «A 1% attack success rate» می‌گوید، پس در گفتار «تو نمودارشون حدود ۱٫۴٪». جملهٔ «far from a solved problem» تأیید شد.
- [ ] اجرای دوبارهٔ مدل‌های جایگزین و تطبیق با فایل‌های illustrative.
- [ ] اگر اجرای واقعی ممکن نشد: قاب ۱۱ را با «اجرای مدل واقعی در ویدیوی تکمیلی» جایگزین کن و هیچ نرخی نگو.

**زنجیره:** قبلی [HMD-006](../../02-benchmarking/e03-what-exactly-are-we-measuring/README.md) (خطای کم‌تر) → بعدی HMD-008 (جواب‌نامهٔ غلط، `parts/02-benchmarking/e04-who-decides-the-right-answer/`).
