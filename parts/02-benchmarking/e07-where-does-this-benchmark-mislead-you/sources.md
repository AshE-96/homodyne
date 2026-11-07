# منابع · HMD-014 · Benchmark E07

تاریخ بازبینی: ۷ نوامبر ۲۰۲۶ (۱۶ آبان ۱۴۰۵). شناسه‌های `R` از `private/planning/production-v3/references.json` هستند؛ شناسه‌های `S` محلی همین قسمت‌اند (تا با شناسه‌های موجود R12 و R13 تداخل نکنند).

| شناسه | منبع | چه چیزی از آن استفاده شد | کجا |
|---|---|---|---|
| R10 | [The Leaderboard Illusion — arXiv 2504.20879](https://arxiv.org/abs/2504.20879) · Singh, Nan, Wang, D'Souza, Kapoor, Üstün, Koyejo, Deng, Longpre, Smith, Ermis, Fadaee, Hooker · v1 ۲۹ آوریل ۲۰۲۵، v2 ۱۲ مه ۲۰۲۵ | از چکیده (v2): «undisclosed private testing practices benefit a handful of providers who are able to test multiple variants before public release and retract scores if desired»؛ «the ability of these providers to choose the best score leads to biased Arena scores due to selective disclosure of performance results»؛ «we identify 27 private LLM variants tested by Meta in the lead-up to the Llama-4 release». عددهای دیگر چکیده (سهم دادهٔ Google ۱۹٫۲٪ و OpenAI ۲۰٫۴٪، ۸۳ مدل open-weight روی‌هم ۲۹٫۷٪، بهبود نسبی تا ۱۱۲٪) خوانده شدند ولی در گفتار نیامده‌اند. وابستگی نویسندگان (Cohere، Cohere Labs و چند دانشگاه) از S3. | قاب ۸، هوک ۵، توضیحات |
| S3 | [BetaKit، «Cohere Labs head calls "unreliable" AI leaderboard rankings a "crisis" in the field» (۲ مه ۲۰۲۵)](https://betakit.com/cohere-labs-head-calls-unreliable-ai-leaderboard-rankings-a-crisis-in-the-field/) — منبع ثانویه | LMArena در پستی در X رفتار ناعادلانه با ارائه‌دهندگان را رد کرد، فهرستی از «factual errors» مقاله داد و گفت سیاست آزمون پیش از انتشارش عمومی بوده. پست اصلی X مستقیم خوانده نشد؛ در گفتار فقط «این برداشت رو رد کرد و گفت مقاله خطای واقعی داره» گفته می‌شود. | قاب ۸ |
| S1 | Bickel, P. J., Hammel, E. A., O'Connell, J. W. (1975). *Sex Bias in Graduate Admissions: Data from Berkeley.* Science 187(4175): 398–404. [doi:10.1126/science.187.4175.398](https://www.science.org/doi/10.1126/science.187.4175.398) | صفحهٔ Science برای ابزار ما 403 داد؛ عددها از دو منبع ثانویهٔ هم‌خوان که هر دو به همین مقاله ارجاع می‌دهند (S4 و یادداشت Reinhart در همان ردیف): پاییز ۱۹۷۳، ۸٬۴۴۲ متقاضی مرد (حدود ۴۴٪ پذیرش) و ۴٬۳۲۱ متقاضی زن (حدود ۳۵٪). با تفکیک رشته‌ها، زنان بیشتر برای رشته‌های سخت‌گیرتر درخواست داده بودند؛ داده‌های تجمیع‌شده با وزن رشته «a small but statistically significant bias in favor of women» نشان داد (به نقل S4). | قاب ۴، توضیحات |
| S4 | [Wikipedia، Simpson's paradox (بخش UC Berkeley gender bias)](https://en.wikipedia.org/wiki/Simpson%27s_paradox) — منبع ثانویه | جدول ۱۲٬۷۶۳ / ۸٬۴۴۲ / ۴٬۳۲۱ و ۴۱٪ / ۴۴٪ / ۳۵٪؛ «۴ رشته به ضرر زنان و ۶ رشته به ضرر مردان معنی‌دار بودند» (در گفتار نیامده). [یادداشت Alex Reinhart (۸ مه ۲۰۱۶)](https://www.refsmmat.com/posts/2016-05-08-simpsons-paradox-berkeley.html) همان جدول (۸۴۴۲ مرد، ۴۴٪؛ ۴۳۲۱ زن، ۳۵٪) را از مقاله آورده و به نقل از مصاحبهٔ Bickel با Wall Street Journal می‌گوید برکلی فقط از شکایت می‌ترسید و شکایتی نشد؛ برای همین در متن حرفی از «دادگاه» یا «شکایت» نیست. | قاب ۴، یادداشت تدوین |
| S2 | [A Careful Examination of Large Language Model Performance on Grade School Arithmetic — arXiv 2405.00332](https://arxiv.org/abs/2405.00332) · Hugh Zhang و ۱۴ همکار، Scale AI · v1 ۱ مه ۲۰۲۴، v4 ۲۲ نوامبر ۲۰۲۴ ([متن HTML v4](https://arxiv.org/html/2405.00332v4)) | v4: «GSM1k consists of 1205 problems»؛ ساخته‌شده فقط با نویسندگان انسانی که Scale AI استخدام کرد؛ برای پیشگیری از آلودگی منتشر نشد (با شرط انتشار بعدی)؛ «accuracy drops of up to 8%»؛ «several families of models showing evidence of systematic overfitting across almost all model sizes»، از جمله Phi و Mistral؛ «many models, especially those on the frontier, show minimal signs of overfitting». نسخه‌های قبلی عدد دیگری برای افت داشتند؛ در گفتار فقط عدد v4 (۸٪) می‌آید. | قاب ۱۰ |
| R11 | [BetterBench — arXiv 2411.12990](https://arxiv.org/abs/2411.12990) · Reuel, Hardy, Smith, Lamparth, Hardy, Kochenderfer · ۲۰ نوامبر ۲۰۲۴ (NeurIPS 2024) | چارچوب ۴۶ بهترین‌روش در چرخهٔ عمر بنچمارک؛ ارزیابی ۲۴ بنچمارک AI؛ «large quality differences»؛ بیشتر بنچمارک‌ها معنی‌داری آماری نتایج را گزارش نمی‌کنند. | قاب ۱۲ |
| R07 | [Adding Error Bars to Evals — arXiv 2411.00640](https://arxiv.org/abs/2411.00640) | پیش‌زمینهٔ «holdout هم یک نمونه است و خطا دارد»؛ در گفتار نقل نشده؛ پیوند به HMD-012. | قاب ۹ (زمینه) |

## محاسبه‌ها و اجرای خودمان (ILLUSTRATIVE)

`artifact/mislead_lab.py`، اجرا ۷ نوامبر ۲۰۲۶ با Python 3، seed 7 (پیش‌فرض، پیش از اجرا انتخاب شد). خروجی کامل در `README.md`.

- **جدول (دستی، ثابت):** ۱٬۰۰۰ سؤال (۶۰۰ آسان، ۴۰۰ سخت). A: آسان ۶۰۰ جواب / ۵۷۰ درست؛ سخت ۳۹۰ / ۲۳۴. B: آسان ۵۹۰ / ۵۵۵؛ سخت ۶۰ / ۳۳.
- **دقت روی جواب‌ها:** کل A ۸۱٫۲٪، B ۹۰٫۵٪؛ آسان A ۹۵٫۰٪، B ۹۴٫۱٪؛ سخت A ۶۰٫۰٪، B ۵۵٫۰٪. سهم سؤال سخت از جواب‌ها: A ۳۹٪، B ۹٪.
- **درست از کل:** A ۸۰٫۴٪ (۸۰۴)، B ۵۸٫۸٪ (۵۸۸). غلط‌ها: A ۱۸۶، B ۶۲.
- **جریمه (+۱ / ۰ / −k، امتیاز در هر ۱۰۰ سؤال):** k=0: ۸۰٫۴ / ۵۸٫۸؛ k=1: ۶۱٫۸ / ۵۲٫۶؛ k=2: ۴۳٫۲ / ۴۶٫۴؛ k=3: ۲۴٫۶ / ۴۰٫۲. نقطهٔ برابری k = (۸۰۴ − ۵۸۸) / (۱۸۶ − ۶۲) = ۲۱۶/۱۲۴ ≈ ۱٫۷۴.
- **انتشار گزینشی:** ۱۰ نسخه با دقت واقعی ۷۰٪، هر کدام ۲۰۰ سؤال (دوجمله‌ای). seed 7: نمره‌ها 74.5 70.0 70.5 69.0 74.0 68.0 70.5 71.0 65.0 66.5؛ میانگین ۶۹٫۹٪؛ منتشرشده ۷۴٫۵٪. در ۲٬۰۰۰ تکرار: میانگین بهترین ۷۴٫۹٪.
- **holdout:** seed 7، همان نسخه روی ۲۰۰ سؤال تازه: ۷۴٫۰٪ (یک اجرای پرنویز). در ۲٬۰۰۰ تکرار: منتشرشده ۷۴٫۹٪ → holdout ۶۹٫۹٪. با seed 11: یک اجرا ۷۸٫۵٪ → ۶۹٫۵٪؛ میانگین‌ها ۷۴٫۹٪ → ۷۰٫۰٪ (همان جهت).
- **ممیزی، فاصلهٔ Wilson دوطرفهٔ ۹۵٪، سقف ۵٪ (انتخاب طراحی، نه استاندارد):** ۰ از ۲ → ۰ تا ۶۵٫۸٪ UNKNOWN؛ ۰ از ۲۰ → ۰ تا ۱۶٫۱٪ UNKNOWN؛ ۰ از ۱۰۰ → ۰ تا ۳٫۷٪ PASS؛ ۳ از ۲۰ → ۵٫۲ تا ۳۶٫۰٪ BREACH. کمترین n با صفر خطا برای PASS: ۷۳.
- **`tools/bluff_lab.py score tools/bluff-demo.csv --condition t75 --max-fabrication 0.05`** (اجرا ۷ نوامبر ۲۰۲۶، دادهٔ ILLUSTRATIVE): برای هر دو مدل `n_u_completed 2`، `fabrication_count 0`، `ci95_wilson [0.0, 0.6576]`، `status UNKNOWN`؛ همان قاعدهٔ PASS / BREACH / UNKNOWN که `tools/README-bluff-lab.md` تعریف کرده.

## چیزی که نمی‌گوییم

- هیچ عددی از A و B به مدل یا شرکت واقعی نسبت داده نمی‌شود؛ Bluff اجرا نشده و هیچ نتیجهٔ تجربی‌ای در این قسمت نیست.
- نمی‌گوییم Chatbot Arena یا Meta تقلب کرده‌اند؛ فقط یافتهٔ نویسندگان مقاله با تاریخ، و اعتراض LMArena.
- نمی‌گوییم «همهٔ جدول‌ها» یا «بیشتر جدول‌ها» گمراه‌کننده‌اند؛ تنها ادعای کمّی دربارهٔ کیفیت بنچمارک‌ها از R11 است. (جملهٔ «تقریباً هیچ جدولی» فقط در هوک ۴ است که انتخاب نشده.)
- نمی‌گوییم برکلی تبعیض داشت یا نداشت؛ فقط اینکه عدد کل و عدد تفکیک‌شده داستان متفاوتی گفتند (S1، S4).
- دربارهٔ GSM1k نام مدل خاصی جز دو خانواده‌ای که خود مقاله نام برده نمی‌آید.
