<div dir="rtl">

# HMD-015 · منابع

بازبینی روی وب: ۱۳ نوامبر ۲۰۲۶. شناسه‌های Rxx مخصوص همین قسمت‌اند.

| شناسه | منبع | لینک | بازبینی | در این قسمت برای |
|---|---|---|---|---|
| R01 | Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni, Liang · *Lost in the Middle: How Language Models Use Long Contexts* · TACL 12 (2024) 157–173 · DOI 10.1162/tacl_a_00638 | https://aclanthology.org/2024.tacl-1.9/ · نسخهٔ arXiv: https://arxiv.org/abs/2307.03172 | ۱۳ نوامبر ۲۰۲۶: صفحهٔ arXiv و متن PDF نسخهٔ v3 (۲۰ نوامبر ۲۰۲۳) خوانده شد؛ مشخصات TACL (جلد، صفحه، DOI) با جست‌وجو در Anthology و Crossref تأیید شد. صفحهٔ Anthology به ابزار ما timeout داد | منحنی U («accuracy highest at the beginning or end»)؛ آزمایش چندسندی با ۲۰ سند در شکل ۱ (در مقاله ۱۰، ۲۰ و ۳۰ سند)؛ GPT-3.5-Turbo با جواب در وسط زیر حالت بدون سند (closed-book، ۵۶٫۱٪)؛ مدل‌ها: MPT-30B-Instruct، LongChat-13B، GPT-3.5-Turbo، Claude-1.3 (مدل‌های ۲۰۲۳)؛ نویسندگان از Stanford، UC Berkeley و Samaya AI · قاب ۵، ۱۱، ۱۳ |
| R02 | Lewis, Perez, Piktus, Petroni و همکاران · *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* · NeurIPS 2020 | https://arxiv.org/abs/2005.11401 | ۱۳ نوامبر ۲۰۲۶ (صفحهٔ arXiv: v1 ۲۲ مه ۲۰۲۰، «Accepted at NeurIPS 2020») | ریشهٔ نام RAG · قاب ۴ |
| R03 | Robertson & Zaragoza · *The Probabilistic Relevance Framework: BM25 and Beyond* · Foundations and Trends in IR 3(4), 333–389, 2009 · DOI 10.1561/1500000019 | https://nowpublishers.com/article/Details/INR-019 | ۱۳ نوامبر ۲۰۲۶ (مشخصات با ناشر و DBLP) | BM25 و پیش‌فرض‌های k1 = 1.2، b = 0.75 در artifact · قاب ۷ |
| R04 | Cormack, Clarke, Büttcher · *Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods* · SIGIR 2009, 758–759 · DOI 10.1145/1571941.1572114 | https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf | ۱۳ نوامبر ۲۰۲۶ (مشخصات با چند فهرست کتاب‌شناختی) | ادغام دو رتبه‌بندی در «جست‌وجوی ترکیبی»، ثابت k = 60 · قاب ۸ (فقط artifact و دک) |
| R05 | Li, Li, Zhang, Mei, Bendersky · *Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach* · EMNLP 2024 (Industry) | https://arxiv.org/abs/2407.16833 | ۱۳ نوامبر ۲۰۲۶ (صفحهٔ arXiv: v1 ۲۳ ژوئیهٔ ۲۰۲۴) | پشتوانهٔ «برندهٔ همه‌جایی نداریم»: با منابع کافی، متن بلند به‌طور میانگین بهتر بود و RAG بسیار ارزان‌تر؛ مسیریاب Self-Route · توضیحات و یادداشت مرز ادعا (در گفتار نام برده نمی‌شود) |
| R06 | Anthropic · *Introducing Contextual Retrieval* · ۱۹ سپتامبر ۲۰۲۴ | https://www.anthropic.com/news/contextual-retrieval | ۱۳ نوامبر ۲۰۲۶ | نمونهٔ یک توصیهٔ صنعتی: پایگاه دانش زیر ۲۰۰ هزار توکن (حدود ۵۰۰ صفحه) را می‌شود کامل در پرامپت گذاشت؛ ترکیب BM25 و embedding با rank fusion. توصیهٔ یک فروشنده است، نه نتیجهٔ آزمون ما · package (کامنت پین‌شده و توضیحات) |
| R07 | Hsieh و همکاران · *RULER: What's the Real Context Size of Your Long-Context Language Models?* · COLM 2024 | https://arxiv.org/abs/2404.06654 | ۱۳ نوامبر ۲۰۲۶ | پیشینه: از ۱۷ مدل که پنجرهٔ دست‌کم ۳۲ هزار توکنی ادعا می‌کردند، حدود نیمی در ۳۲K عملکرد رضایت‌بخش داشتند · فقط یادداشت تدوین و توضیحات |

## محاسبه‌شده توسط ما (اجرای محلی، ۱۳ نوامبر ۲۰۲۶، بدون هیچ مدل زبانی)

- `python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py retrieval` → `artifact/results/retrieval-local.txt` و `.json` و `retrieval-per-question.csv`. اسناد و سؤال‌ها **ساختگی (ILLUSTRATIVE)**.
- پروندهٔ کوتاه: ۵۳ بند، ۲٬۲۹۶ کلمه. پروندهٔ بلند: ۲۲۵ بند، ۹٬۴۶۴ کلمه (قاب ۶).
- BM25، بند درست بین ۵ نتیجهٔ اول: کوتاه ۴۰ از ۴۲، بلند ۳۴ از ۴۲ (قاب ۷). ترکیبی: ۴۰ و ۳۸.
- همهٔ ۸ جاافتادهٔ BM25 در پروندهٔ بلند از ۱۲ سؤالی‌اند که پیش از اجرا برچسب «هم‌پوشانی کم» گرفته بودند؛ BM25 ۴ از ۱۲، ترکیبی ۸ از ۱۲؛ سؤال‌های هم‌پوشانی زیاد و متوسط ۳۰ از ۳۰ (قاب ۸).
- پنج بار به‌هم‌ریختن ترتیب پرونده: پنج نتیجهٔ اول هیچ سؤالی عوض نشد (قاب ۸).
- سؤال عینک (L01)، پروندهٔ بلند، BM25: رتبهٔ ۱ FAQ-02 (۱۴۰۲، ۲ میلیون)، رتبهٔ ۲ INS-1404-01 (۳ میلیون)، رتبهٔ ۳ INS-1405-01 (۴٫۵ میلیون) (قاب ۹).
- از ۱۴ سؤالی که نسخهٔ قدیمی‌شان هم در پروندهٔ بلند بود، BM25 در ۱۰ تا نسخهٔ قدیمی را بالاتر از نسخهٔ معتبر نشاند (قاب ۹).
- `estimate`: هر پرسش «کل پرونده» روی پروندهٔ بلند حدود ۲۹ برابرِ «جست‌وجوی ساده» نویسه دارد (حدود ۵۶ هزار در برابر ۱٫۹ هزار نویسه؛ برآورد توکن با ۲٫۵ نویسه در هر توکن، تقریبی) (قاب ۱۲).

## نیازمند اجرا [RUN]

- همهٔ عددهای قاب ۱۰ و ۱۱ و جملهٔ کروشه‌ای قاب ۱۲: `run` و بعد `report` (`artifact/README.md`). قیمت‌ها در `artifact/prices.json` با تاریخ، از صفحهٔ رسمی قیمت همان ارائه‌دهنده.

## آنچه عمداً استفاده نشد

- رتبه‌بندی مدل‌ها یا ادعای «پنجرهٔ متن مدل X»؛ این قسمت دربارهٔ روش سنجیدن است.
- هیچ عددی از R05، R06 یا R07 در گفتار نیامده، چون دامنه و مدل‌هایشان با آزمون ما فرق دارد.
- عددهای دقیق منحنی U مقالهٔ R01 روی صفحه نمی‌آیند؛ فقط شکل کلی و جملهٔ «زیر حالت بدون سند».

</div>
