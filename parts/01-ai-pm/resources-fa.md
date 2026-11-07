# منابع تکمیلی — Homodyne · قسمت ۰۱: AI Product Management

فهرست منتخب و توضیح‌دار. با ⭐ مشخص شده‌ها اولویت اول‌اند. اگر فقط سه ساعت وقت دارید، فقط ستاره‌دارها را بخوانید.
همه‌ی لینک‌ها در مهر ۱۴۰۵ / سپتامبر ۲۰۲۶ بررسی شده‌اند.

---

## ۱. Evals و Error Analysis — مهم‌ترین مهارت

| منبع | چرا مهم است |
|------|--------------|
| ⭐ [AI Evals: Everything You Need to Know — Hamel Husain & Shreya Shankar](https://hamel.dev/blog/posts/evals-faq/) | مرجع اصلی و به‌روز (سپتامبر ۲۰۲۶). چرا eval دودویی، چطور error analysis کنید، و چطور قاضی LLM را با برچسب انسانی بسنجید. اگر فقط یک لینک باز می‌کنید، همین. |
| ⭐ [Why AI evals are the hottest new skill for product builders — Lenny's Podcast](https://www.lennysnewsletter.com/p/why-ai-evals-are-the-hottest-new-skill) | گفت‌وگو با Hamel Husain و Shreya Shankar (سپتامبر ۲۰۲۵). نسخه‌ی شنیدنی همان محتوا، مناسب مسیر رفت‌وآمد. |
| [Evals, error analysis, and better prompts — How I AI](https://www.lennysnewsletter.com/p/evals-error-analysis-and-better-prompts) | Claire Vo با Hamel Husain (اکتبر ۲۰۲۵). یک error analysis واقعی را جلوی دوربین اجرا می‌کنند. |
| [AI Evals for PMs — Aakash Gupta & Hamel Husain](https://www.news.aakashg.com/p/ai-evals) | نوشته‌ی صریحاً PM-محور؛ کمترین اصطلاح فنی. |
| [Evals are the new PRD — Braintrust](https://www.braintrust.dev/blog/evals-are-the-new-prd) | تغییر مدل ذهنی از «توصیف رفتار» به «اثبات رفتار». |
| [Anthropic — تعریف معیار موفقیت و ساخت Eval](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) | مستندات عملی با مثال کد: code-based، LLM-based و human grading. |
| [OpenAI Evals (GitHub)](https://github.com/openai/evals) | فریم‌ورک متن‌باز. حتی اگر کد نمی‌نویسید، خواندن چند نمونه‌ی eval بینش می‌دهد. |
| [دوره‌ی AI Evals for Engineers & PMs — Maven](https://maven.com/parlance-labs/evals) | دوره‌ی پولی Hamel و Shreya. مرجع صنعتیِ این حوزه. |

---

## ۲. نقش AI PM — تعریف و چشم‌انداز

| منبع | چرا مهم است |
|------|--------------|
| ⭐ [How AI will impact product management — Lenny Rachitsky (۲۰۲۴)](https://www.lennysnewsletter.com/p/how-ai-will-impact-product-management) | تحلیل اینکه کدام بخش کار PM بیشتر عوض می‌شود. نکته: پیش‌بینی ۲۰۲۴ است؛ با همین نگاه بخوانید. |
| [Why PMs are best positioned to thrive in an AI world — Lenny Rachitsky (۲۰۲۴)](https://www.lennysnewsletter.com/p/why-pms-are-best-positioned-to-thrive) | پادزهر اضطراب «AI جای PM را می‌گیرد». |
| [5 Principles for PMs in the AI Era — Anish Acharya, a16z (۲۰۲۵)](https://a16z.com/stay-relevant-in-ai/) | کوتاه، عملی، از دید سرمایه‌گذار. |
| [How close is AI to replacing product managers? — Mike Taylor (۲۰۲۴)](https://www.lennysnewsletter.com/p/how-close-is-ai-to-replacing-product) | آزمایش کور: AI در دو تا از سه کار PM از پاسخ انسان بهتر شد. خودِ روش آزمایش هم درس است. |

---

## ۳. مبانی فنی — دقیقاً به‌اندازه‌ای که یک PM لازم دارد

| منبع | چرا مهم است |
|------|--------------|
| ⭐ [What We've Learned From A Year of Building with LLMs](https://applied-llms.org/) | جمع‌بندی شش سازنده‌ی باتجربه. سه بخش: تاکتیکی، عملیاتی، استراتژیک. بخش استراتژیک را حتماً بخوانید. |
| ⭐ [Building effective agents — Anthropic](https://www.anthropic.com/engineering/building-effective-agents) | کِی ایجنت بسازیم و — مهم‌تر — کِی نسازیم. |
| [Patterns for Building LLM-based Systems — Eugene Yan](https://eugeneyan.com/writing/llm-patterns/) | نقشه‌ی الگوهای معماری: RAG، fine-tuning، caching، guardrails. |
| [Building LLM applications for production — Chip Huyen](https://huyenchip.com/2023/04/11/llm-engineering.html) | کلاسیک این حوزه (۲۰۲۳). چرا فاصله‌ی دمو تا production این‌قدر زیاد است. |
| [Why language models hallucinate — OpenAI (۲۰۲۵)](https://openai.com/index/why-language-models-hallucinate/) | چرا مدل‌ها حدس می‌زنند: ارزیابی‌هایی که فقط درستی را نمره می‌دهند. مستقیماً به طراحی eval شما مربوط است. |
| [OpenAI — راهنمای Prompt Engineering](https://developers.openai.com/api/docs/guides/prompt-engineering) | مستندات vendor دست‌کم گرفته می‌شوند؛ نباید. |
| [Evaluating AI Agents — DeepLearning.AI × Arize](https://www.deeplearning.ai/short-courses/evaluating-ai-agents/) | رایگان، حدود ۲.۵ ساعت، عملی. |

---

## ۴. طراحی و UX برای محصولات AI

| منبع | چرا مهم است |
|------|--------------|
| ⭐ [The Shape of AI — Emily Campbell](https://www.shapeof.ai/) | کتابخانه‌ی الگوهای تعامل AI با نام و مثال. بهترین منبع بصری موجود. |
| [People + AI Guidebook — Google PAIR](https://pair.withgoogle.com/guidebook/) | مرجع طراحی انسان‌محور برای AI. |
| [فصل Errors + Graceful Failure — PAIR](https://pair.withgoogle.com/chapter/errors-failing/) | مستقیم‌ترین متن درباره‌ی طراحی برای لحظه‌ای که محصول اشتباه می‌کند. |
| [Measuring GitHub Copilot's impact on productivity — CACM (۲۰۲۴)](https://cacm.acm.org/research/measuring-github-copilots-impact-on-productivity) | منبع مثال Autocomplete در اسلاید ۱۴: نرخ پذیرش حدود ۲۶٪، و همین نرخ بهترین پیش‌بینی‌کننده‌ی بهره‌وری ادراک‌شده. |

---

## ۵. ریسک، ایمنی و رگولاتوری

| منبع | چرا مهم است |
|------|--------------|
| ⭐ [EU AI Act Explorer](https://artificialintelligenceact.eu/) | سطح ریسک محصولتان را قبل از برنامه‌ریزی رودمپ بدانید. توجه: با Digital Omnibus (اجرایی از ۲۷ ژوئیه ۲۰۲۶) الزامات Annex III به ۲ دسامبر ۲۰۲۷ منتقل شد. |
| [خلاصه‌ی تغییرات Digital Omnibus — Orrick](https://www.orrick.com/en/Insights/2026/07/EU-AI-Act-Update-Digital-Omnibus-Finalizes-8-Compliance-Changes) | هشت تغییر اصلی و تاریخ‌های جدید، در یک صفحه. |
| [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) | چارچوب مرجع برای صحبت با تیم حقوقی و امنیت. |
| [OWASP Top 10 for LLM Applications (نسخه‌ی ۲۰۲۵)](https://genai.owasp.org/llm-top-10/) | ده ریسک امنیتی — prompt injection هنوز رتبه‌ی اول است. OWASP برای agentها هم پروژه‌ی جداگانه دارد. |

---

## ۶. ابزارهایی که خوب است بشناسید

| ابزار | کاربرد |
|-------|--------|
| [LangSmith](https://www.langchain.com/langsmith) / [Braintrust](https://www.braintrust.dev/) / [Langfuse](https://langfuse.com/) | Trace، eval و observability. |
| [Evidently AI — LLM Guide](https://www.evidentlyai.com/llm-guide) | راهنمای جامع و رایگان کیفیت LLM؛ ابزار متن‌باز برای پایش در production. |
| [OpenRouter](https://openrouter.ai/) | مقایسه‌ی سریع مدل‌ها از نظر قیمت و در دسترس بودن. |
| [Artificial Analysis](https://artificialanalysis.ai/) | مقایسه‌ی مستقل latency و هزینه‌ی مدل‌ها. برای بحث مثلث کیفیت/هزینه/سرعت. |

---

## ۷. پیشنهاد مسیر مطالعه

**هفته‌ی اول** — AI Evals FAQ نوشته‌ی Hamel و Shreya + اپیزود Lenny's Podcast. یک صفحه یادداشت از چیزهایی که نمی‌دانستید.

**هفته‌ی دوم** — `applied-llms.org` را کامل بخوانید. بخش استراتژیک را دو بار.

**هفته‌ی سوم** — Shape of AI را ورق بزنید و برای هر الگو یک محصول واقعی که از آن استفاده می‌کند پیدا کنید.

**هفته‌ی چهارم** — دوره‌ی Evaluating AI Agents را تمام کنید و بیست eval دودویی برای یک محصول واقعی بنویسید.

---

*آخرین بازبینی: مهر ۱۴۰۵ / September 2026*
