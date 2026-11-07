# HMD-004 · منابع

بازبینی: ۲ نوامبر ۲۰۲۶. شناسه‌های Rxx از `private/planning/production-v3/references.json`؛ منابع W از جست‌وجوی همین نوبت.

| شناسه | منبع | لینک | بازبینی | در این قسمت برای |
|---|---|---|---|---|
| R03 | OpenAI · *Why we no longer evaluate SWE-bench Verified* · 23 Feb 2026 | https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/ | references.json + جست‌وجوی ۲ نوامبر ۲۰۲۶ (صفحه به ابزار خودکار 403 داد؛ عدد از نتیجهٔ جست‌وجو و پوشش Decrypt تأیید شد) | ۱۳۸ مسئلهٔ بازبینی‌شده که مدل به‌طور پیوسته حل نمی‌کرد؛ «at least 59.4%» تست معیوب که راه‌حل درست را رد می‌کند؛ نشانه‌های آلودگی؛ توقف گزارش و اشاره به Pro · قاب ۹، ۱۰. نمونه تصادفی کل مجموعه نیست. |
| R04 | OpenAI · *Separating signal from noise in coding evaluations* · 8 Jul 2026 | https://openai.com/index/separating-signal-from-noise-coding-evaluations/ | references.json (تاریخ) + جست‌وجوی ۲ نوامبر ۲۰۲۶ | «we retract our earlier recommendation to adopt SWE-Bench Pro»؛ برآورد حدود ۳۰٪ مسئلهٔ خراب · قاب ۱۰ |
| R05 | *SimpleQA Verified* · arXiv 2509.07968 | https://arxiv.org/abs/2509.07968 | references.json | ۱٬۰۰۰ پرسش، نسخهٔ بازبینی‌شده · قاب ۱۱ |
| R11 | *BetterBench* · arXiv 2411.12990 | https://arxiv.org/abs/2411.12990 | references.json | پشتوانهٔ ایدهٔ «کیفیت آزمون در کل چرخهٔ عمر» (یادداشت، نه عدد) · قاب ۱۰ |
| W1 | LMSYS · *Does style matter? Disentangling style and substance in Chatbot Arena* · 29 Aug 2024 | https://lmsys.org/blog/2024-08-28-style-control/ | ۲ نوامبر ۲۰۲۶ | «length was the dominant style factor»؛ markdown «second order»؛ GPT-4o-mini کلی ۶ → ۱۱ (markdown یا هر دو کنترل)، Claude 3 Opus کلی ۱۶ → ۱۰ (هر دو کنترل)؛ «our analysis is still observational» · قاب ۱، ۳ |

## اجرا‌شده توسط ما (۲ نوامبر ۲۰۲۶، از ریشهٔ مخزن)

- `python3 -m m2bench families --decision "customer support bot for my online shop" --failure "tells customers the wrong refund policy"` → نزدیک‌ترین مثال: agents_tool_use، safety_security، robustness؛ NOT knowledge، reasoning (قاب ۶).
- `python3 -m m2bench families --decision "question answering assistant for my online shop" --failure "a confident wrong answer about refunds"` → calibration_abstention، factuality، multilingual_cultural؛ diagnostic only knowledge؛ NOT human_preference، reasoning، agents_tool_use؛ built as bluff-v1 (قاب ۷).
- منطق تطبیق: `m2bench/families.py`، تابع `select()` — هم‌پوشانی واژه‌های بلندتر از ۴ حرف با مثال‌های آماده.
- `framework/00-landscape/benchmark-families.yaml` (خوانده‌شده با `m2bench/families.py`): ۱۶ خانواده در ۴ گروه capability، system، trust، value (قاب ۸).
- `python3 -m m2bench families --lifecycle` → شش وضعیت با تاریخ «as of 2026-09-29» (قاب ۱۰).

## آموزشی (ILLUSTRATIVE)

- مدل‌های X و Y و عددهای قاب ۴؛ دو پاسخ نمونهٔ قاب ۳؛ تقسیم توکن نمادین قاب ۱۴ (خروجی واقعی tokenizer نیست).

## فایل‌های همراه

- [artifact/decision-card.md](artifact/decision-card.md) — کارت چهارخانه (تازه در v5).
- [artifact/landscape-card.md](artifact/landscape-card.md) — پنج سؤال، دو محور، شش وضعیت (از v2، بدون تغییر).
- [artifact/family-selection-bluff.md](artifact/family-selection-bluff.md) — زنجیرهٔ انتخاب برای bluff-v1 (از v2، بدون تغییر؛ مرحلهٔ طراحی، بدون نتیجهٔ تجربی).

## آنچه عمداً استفاده نشد

- عدد HLE (زیر ۱۰٪ تا ۳۸٫۳٪) و «۲۹ از ۶۰» از نسخهٔ v2؛ در این نوبت دوباره تأیید نشدند و برای روایت لازم نبودند.
- رتبه‌های امروز LMArena و هر عدد زنده.
