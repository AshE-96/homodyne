# HMD-007 · منابع

بازبینی: ۲ نوامبر ۲۰۲۶ (۱۱ آبان ۱۴۰۵) · ماجراهای واقعی و بازبینی دوباره: ۲۶ نوامبر ۲۰۲۶ (۵ آذر ۱۴۰۵).

## منبع اصلی (روی کارت قسمت)

### R33 · Mitigating the risk of prompt injections in browser use (Anthropic)
- **پیوند:** https://www.anthropic.com/research/prompt-injection-defenses · تاریخ انتشار: ۲۴ نوامبر ۲۰۲۵ (بازبینی ۲ نوامبر، ۷ نوامبر و ۲۶ نوامبر ۲۰۲۶)
- **محتوا:** تعریف تزریق دستور به‌عنوان دستورهای خصمانهٔ پنهان در محتوایی که مدل پردازش می‌کند؛ سه دفاع (آموزش با یادگیری تقویتی روی محتوای دارای تزریق، طبقه‌بندهای محتوای نامطمئن، red teaming)؛ نرخ موفقیت حمله با حمله‌کنندهٔ تطبیقی Best-of-N («An adaptive attacker is given 100 attempts per environment»): Opus 4.5 ۸٫۰٪ بدون محافظ، ۷٫۶٪ با محافظ قدیم، ۱٫۴٪ با محافظ‌های بهبودیافته.
- **استفاده:** قاب ۱۱ — ۱٫۴٪ برای Opus 4.5 با محافظ‌های بهبودیافته و جملهٔ «far from a solved problem»؛ هوک ۵.
- **احتیاط:** عددها مال آزمون‌های مرورگرِ همان شرکت، در همان تاریخ‌اند؛ با دموی ما قابل‌مقایسه نیستند. طبق `references.json`: «مقاومت کامل ادعا نشده». ✔ ۲۶ نوامبر ۲۰۲۶ دوباره تأیید شد: نمودار ۸٫۰٪ / ۷٫۶٪ / ۱٫۴٪؛ متن مقاله «A 1% attack success rate».

## ماجراهای واقعی (افزوده ۲۶ نوامبر ۲۰۲۶)

### EchoLeak · CVE-2025-32711 · Microsoft 365 Copilot (قاب ۱ حلقهٔ باز، قاب ۴ کارت)
- **پروندهٔ رسمی (منبع اول):**
  - NVD: https://nvd.nist.gov/vuln/detail/CVE-2025-32711 (از راه API 2.0، خوانده‌شده ۲۶ نوامبر ۲۰۲۶). شرح CNA: «Ai command injection in M365 Copilot allows an unauthorized attacker to disclose information over a network.» انتشار ۱۱ ژوئن ۲۰۲۵؛ CWE-74.
  - MSRC: https://msrc.microsoft.com/update-guide/vulnerability/CVE-2025-32711 (از راه API، خوانده‌شده ۲۶ نوامبر ۲۰۲۶). عنوان «M365 Copilot Information Disclosure Vulnerability»؛ انتشار ۱۱ ژوئن ۲۰۲۵؛ Severity: Critical؛ CVSS 9.3 (بردار Microsoft: `AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N/E:U/RL:O/RC:C`)؛ **Exploited: No**؛ Publicly disclosed: No؛ Customer action required: No؛ FAQ: «This vulnerability has already been fully mitigated by Microsoft. There is no action for users of this service to take.» یابنده‌ها: «Aim Labs (Part of Aim Security)» و «Estevam Arantes with Microsoft».
  - NVD نمرهٔ جدای خودش را 7.5 (HIGH) داده؛ روی دک فقط نمرهٔ Microsoft با نام منبع آمده.
  - خلاصهٔ ما: [`artifact/derived/cve-2025-32711.json`](artifact/derived/cve-2025-32711.json) با [`SOURCE.txt`](artifact/derived/SOURCE.txt) (URL، sha256، فرمان).
- **روایت یابنده:** Aim Labs، https://www.aim.security/lp/aim-labs-echoleak-m365 — سایت به درخواست خودکار ما 403 داد؛ خوانده نشد و دور زده نشد. **محمد پیش از ضبط این صفحه را خودش باز کند.**
- **مرور دانشگاهی (منبع دوم، CC BY 4.0):** Reddy و Gujral (George Washington University)، «EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System»، https://arxiv.org/abs/2509.10540 (۶ سپتامبر ۲۰۲۵؛ خوانده‌شده ۲۶ نوامبر ۲۰۲۶). مسیر سطح‌بالا: ایمیلی از بیرون با دستورهای پنهان ← کاربر سؤال عادی می‌پرسد ← Copilot ایمیل را هم بازیابی می‌کند ← داده در نشانی یک تصویر به سرور حمله‌کننده می‌رود؛ «No user action beyond Copilot processing the email is required». نویسندگان حمله را تکرار نکرده‌اند و فقط از داده‌های عمومی نوشته‌اند.
- **جمله‌های گفتار و پشتوانه‌شان:**
  - «خرداد هزار و چهارصد و چهار… پرونده… منتشر کرد» ← MSRC/NVD: ۱۱ ژوئن ۲۰۲۵ = ۲۱ خرداد ۱۴۰۴. (قاب ۱: «سال دو هزار و بیست‌وپنج، نسخهٔ واقعیش…» همین پرونده است.)
  - «یه ایمیل با دستور پنهان کافیه» ← یابنده (از راه مرور arXiv)؛ MSRC: `PR:N` (بدون حساب یا دسترسی).
  - «بی‌هیچ کلیکی» ← MSRC: `UI:N` (بدون تعامل کاربر)؛ مرور arXiv: «zero-click».
  - «می‌تونست اطلاعات داخلی رو بیرون بفرسته» ← شرح CNA «disclose information over a network»؛ عمداً «می‌تونست»، چون سوءاستفاده‌ای ثبت نشده.
  - «قبل از اعلام، مشکل رو بسته بود» ← MSRC FAQ «already been fully mitigated».
  - «تا اون روز سوءاستفاده‌ای ازش دیده نشده بود» ← MSRC: Exploited: No.
- **مرز:** یافتهٔ پژوهشگر و پروندهٔ سازنده است، نه آسیب ثبت‌شده به کاربر. جزئیات فنی دورزدن (طبقه‌بند، پیوند مرجع، پراکسی) عمداً گفته نمی‌شود.

### Invitation Is All You Need · Gemini (قاب ۹، قاب ۱۳ «از ایمیل تا آبگرمکن»)
- **منبع اول:** Ben Nassi، Stav Cohen، Or Yair (دانشگاه تل‌آویو، تکنیون، SafeBreach)، «Invitation Is All You Need! Promptware Attacks Against LLM-Powered Assistants in Production Are Practical and Dangerous»، https://arxiv.org/abs/2508.12175 (ثبت ۱۶ اوت ۲۰۲۵؛ مجوز CC BY 4.0؛ متن و منبع LaTeX خوانده‌شده ۲۶ نوامبر ۲۰۲۶).
- **آنچه از متن مقاله برداشتیم:**
  - همهٔ نمایش‌های «مسموم‌کردن کوتاه‌مدت» با «indirect prompt injection in the title of a meeting invitation» شروع شدند (بخش threat analysis).
  - شکل ۶: «The user thanks Gemini for reading his events and in response, Gemini activates the boiler (left), opens the windows (middle), or turns the lights on in the victim's apartment (right).»
  - اخلاق پژوهش: «performed exclusively on the authors' Gemini accounts».
  - افشای مسئولانه به گوگل در ۲۲ فوریهٔ ۲۰۲۵؛ چکیده: گوگل «deployed dedicated mitigations».
  - بیانیهٔ گوگل (در خود مقاله، به درخواست گوگل): لایه‌های دفاعی «including: enhanced user confirmations for sensitive actions…»؛ گوگل در همان بیانیه این تکنیک‌ها را «theoretical» خوانده.
  - چکیده: ۱۴ سناریوی حمله؛ ۷۳٪ تهدیدها «High-Critical» در ارزیابی خود نویسندگان (در گفتار نیامده).
- **پشتیبان:** Google GenAI Security Team، «Mitigating prompt injection attacks with a layered defense strategy»، ۱۳ ژوئن ۲۰۲۵، https://blog.google/security/mitigating-prompt-injection-attacks/ (خوانده‌شده ۲۶ نوامبر ۲۰۲۶) — یکی از لایه‌ها «User confirmation framework» («Human-In-The-Loop»)؛ از Nassi، Cohen و Yair نام برده.
- **جمله‌های گفتار:** «تابستون دو هزار و بیست‌وپنج» = انتشار اوت ۲۰۲۵ (مرداد ۱۴۰۴)؛ «سه پژوهشگر»؛ «عنوان جلسه دستور پنهان داشت»؛ «گفت ممنون» ← «thanks»؛ «آبگرمکن» ترجمهٔ «boiler»؛ «پنجره رو باز کرد» ← «opens the windows»؛ «روی حساب‌های خود پژوهشگرها و توی یه آزمایش کنترل‌شده» ← بخش اخلاق (بخش I-B): «performed exclusively on the authors' Gemini accounts»، «in a controlled environment» (بازبینی ۲۷ نوامبر ۲۰۲۶؛ مقاله نمی‌گوید دستگاه‌ها در خانهٔ خود نویسندگان بوده، فقط «the user's apartment» و «physical spaces of the authors»)؛ «تأیید بیشتری برای کارهای حساس» ← بیانیهٔ گوگل.
- **مرز:** آزمایش کنترل‌شدهٔ پژوهشگرها روی حساب‌های خودشان؛ هیچ قربانی واقعی. تصویر قاب ۹ با اعتبار در [`media/CREDITS.md`](media/CREDITS.md).

## چارچوب

### OWASP LLM01:2025 Prompt Injection
- **پیوند:** https://genai.owasp.org/llmrisk/llm01-prompt-injection/ (بازبینی ۲ و ۲۶ نوامبر ۲۰۲۶؛ محتوا CC BY-SA 4.0)
- **استفاده:** قاب ۲ (مورد اول فهرست، تعریف مستقیم/غیرمستقیم)، قاب ۹ («Enforce privilege control and least privilege access»، «Require human approval for high-risk actions»)، قاب ۸ («Segregate and identify external content»).
- **جملهٔ تعریف:** «A Prompt Injection Vulnerability occurs when user prompts alter the LLM's behavior or output in unintended ways.»

## پژوهش‌های پشتیبان

### Hines و همکاران ۲۰۲۴ · Defending Against Indirect Prompt Injection Attacks With Spotlighting
- **پیوند:** https://arxiv.org/abs/2403.14720 (ثبت ۲۰ مارس ۲۰۲۴؛ CC BY 4.0؛ بازبینی ۲۶ نوامبر ۲۰۲۶)
- **استفاده:** قاب ۸ — «Using GPT-family models, we find that spotlighting reduces the attack success rate from greater than 50% to below 2%» (چکیده). روش datamarking دموی ما از این مقاله الهام گرفته، ولی پیاده‌سازی دقیق آن نیست.

### Greshake و همکاران ۲۰۲۳ · Not what you've signed up for
- **پیوند:** https://arxiv.org/abs/2302.12173 (پیش‌چاپ arXiv)
- **استفاده:** پیش‌زمینه — معرفی و بررسی تزریق غیرمستقیم در برنامه‌های مبتنی بر LLM. از ۲۶ نوامبر ۲۰۲۶ در گفتار قاب ۴ جایش را به پروندهٔ واقعی CVE-2025-32711 داده؛ در توضیحات ویدیو می‌ماند.

## بررسی‌شده و کنار گذاشته‌شده (۲۶ نوامبر ۲۰۲۶)

- **AgentDojo** (Debenedetti و همکاران، https://arxiv.org/abs/2406.13352؛ نتایج: https://agentdojo.spylab.ai/results/): خود صفحه می‌گوید «not a leaderboard»، چون همهٔ مدل‌ها با همهٔ حمله‌ها آزموده نشده‌اند؛ تازه‌ترین ردیف‌ها مال مدل‌های ۲۰۲۴ تا اوایل ۲۰۲۵‌اند. یک عدد از آن، بیننده را به مقایسهٔ نادرست می‌کشاند.
- **«تاهو یک دلاری» Chevrolet (دسامبر ۲۰۲۳):** منبع اولش پست‌های X است که ما نخواندیم، پس هیچ جزئیاتی از آن نیامده؛ در روایت رایج، تزریق مستقیم است (کاربر خودش تایپ کرد)، نه سندی که دستور بدهد؛ و تصویرهایش مجوز بازاستفاده ندارند.
- **نشت پرامپت Bing Chat (فوریهٔ ۲۰۲۳):** منبع اول در X و تأییدنشده؛ در روایت رایج تزریق مستقیم است و با محور این قسمت (سندی که دستور می‌دهد) جور نیست.

## آزمایش خودمان

- **کد:** [`artifact/injection_lab.py`](artifact/injection_lab.py) — Python 3.10+، فقط کتابخانهٔ استاندارد، بدون هیچ import شبکه‌ای. **داده:** [`artifact/cases.json`](artifact/cases.json) — ۲۰ سند ساختگی (۱۲ حمله: ۷ با ابزار، ۵ فقط تغییر جواب؛ ۸ سالم)، فایل‌های ساختگی، نشانی‌های `.invalid`.
- **مدل‌های جایگزین (ILLUSTRATIVE):** `naive` (از هر خط دستورمانند اطاعت می‌کند) و `boundary` (درون نشانگرهای spotlight را نادیده می‌گیرد؛ پس spotlight روی آن «طبق ساخت» کار می‌کند). خروجی: [`artifact/results-illustrative-2026-11-02.md`](artifact/results-illustrative-2026-11-02.md) و [`artifact/trace-A01-illustrative-2026-11-02.txt`](artifact/trace-A01-illustrative-2026-11-02.txt). ۲۶ نوامبر ۲۰۲۶ دوباره اجرا شد و یکی بود. این عددها رفتار قاعده‌های خودمان‌اند، نه یافته دربارهٔ AI.
- **مدل واقعی:** هنوز اجرا نشده؛ برای ویدیوی پیگیری، رایگان و محلی با [`artifact/ollama_adapter.py`](artifact/ollama_adapter.py) (فقط loopback) یا با [`artifact/adapter_template.py`](artifact/adapter_template.py). هیچ نرخی از پیش نوشته نشده.

## ایمنی

- در دمو هیچ هدف واقعی، محصول واقعی، حساب یا داده‌ای استفاده نشده. خط‌های حمله جمله‌های سادهٔ زبان طبیعی‌اند که فقط ابزارهای قلابی همین فایل را هدف می‌گیرند؛ هیچ ترفند پنهان‌سازی، کدگذاری یا دورزدن محصول خاصی در آن‌ها نیست.
- دو محصول واقعی (Microsoft 365 Copilot و Gemini) فقط به‌عنوان پرونده‌های عمومی و بسته‌شده، با منبع اول، نام برده می‌شوند؛ ما هیچ‌کدام را آزمایش یا تکرار نکردیم.
