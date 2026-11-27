# HMD-S01 · منابع

> همهٔ منابع ۲۷ نوامبر ۲۰۲۶ باز و خوانده شدند، مگر جایی که نوشته شده. نقل‌قول‌ها کوتاه‌اند و فقط برای نقد و گزارش خبری.
> برچسب‌ها: ✅ از متن منبع خوانده شد · 🔁 از متن یک منبع اصلیِ دیگر نقل شده (منبع اصلی باز نشد) · ⚠️ اختلاف یا ابهام.

## منابع اصلی ۲۰۲۶

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| R01 | Anthropic, «Claude has improved on a longstanding lower bound for the fraction of zeros of the Riemann zeta function that satisfy the Riemann hypothesis», 10 Aug 2026, به‌روزرسانی ۱۳ اوت — https://www.anthropic.com/research/riemann-zeta | مدل پژوهشیِ **منتشرنشده** (بی‌نام)؛ «from 41.6% to 67.2%»؛ «over two sessions in Claude Code»؛ «31 million output tokens»؛ «a day and a half coordinating about 60 Claude subagents»؛ «2,400 shell commands»؛ «tried 650 ideas, none of which worked»؛ جرد سامنر (غیرریاضی‌دان) و جملهٔ «take a real stab»؛ آلپوگه و فورمن «examined and validated»؛ اریک ایزلی و Lean (comparator)؛ کانری و گلدستون «examined the paper on short notice»؛ «We don't expect that the techniques Claude used will lead to proving the Riemann hypothesis.» | ✅ |
| R02 | Claude (Anthropic), «More than two thirds of the zeros of the Riemann zeta function are simple and on the critical line», نسخهٔ ۱۱ اوت ۲۰۲۶، PDF پیوندشده در R01 (https://assets.claude.com/95c246936988e43127bc6b2ceb7077c1dad2d68e.pdf)؛ همان در arXiv: Alpöge, Furman, arXiv 2608.13637 (13 Aug 2026، v2 19 Aug؛ توضیح: «Proof discovered autonomously by Claude (Anthropic); verified and communicated by the listed authors») | قضیهٔ A: ≥ 2/3 ساده و روی خط، ≥ 5/6 متمایز؛ با پنجرهٔ مونتگومری–تیلور 0.67250… و 0.83625…؛ رکوردهای قبلی «5/12 [PRZZ20]» و «0.6603 [Wu15]»؛ «No mollifier, zero-density estimate, or zero-free region is used»؛ §1.4 «What the results are not» (کران پایین؛ برای Davenport–Heilbronn و Epstein هم برقرار؛ فراتر از 2/3 نیازمند اطلاعات بیش از پهنای باند ۱)؛ §1.3 تاریخچه (Selberg، Levinson 1/3، Conrey > 2/5، BCY/Feng/PRZZ، Montgomery 2/3 به شرط RH)؛ پیوست A: Lean 4 (v4.33.0-rc2)، `#print axioms` فقط propext، Classical.choice، Quot.sound، بدون sorry؛ مخزن github.com/anthropics/zeta-23-lean | ✅ (متن PDF با pdftotext خوانده شد؛ صفحهٔ arXiv فقط چکیده) |
| R03 | Joseph Howlett, «No, AI didn't just solve the thorniest problem in math» (عنوان صفحه: «No, Anthropic's AI didn't just solve math's hardest problem»), *Scientific American*, 12 Aug 2026 — https://scientificamerican.com/article/no-ai-didnt-just-solve-the-thorniest-problem-in-math | ۴۱٫۶٪ ← ۶۷٫۲٪؛ RH «no closer to being solved»؛ حتی ۱۰۰٪ هم جایزه نمی‌گیرد؛ Maynard: «The problem was in need of a new real idea, which this new result seems to provide.» و «Even being very optimistic, there is no pathway for any of these approaches to deal with the actual Riemann hypothesis.»؛ پست Anthropic «remarkably restrained» | ✅ |
| R04 | Russell Brandom, «An unreleased Anthropic model made progress on one of math's biggest unsolved problems», TechCrunch, 11 Aug 2026 — https://techcrunch.com/2026/08/11/an-unreleased-anthropic-model-made-progress-on-one-of-maths-biggest-unsolved-problems/ | تیتر قاب ۲؛ جایزهٔ یک میلیون دلاری؛ پاورقی نقش زیرعامل‌ها (۲ / ۱۳ / ۳۰ / ۱۳ / ۲)؛ «confirmed by two of Anthropic's in-house mathematicians» | ✅ |
| R05 | Konstantin Kakaes, «AI Proved the Quasi-Riemann Hypothesis. What Happens Now?», *Quanta Magazine*, 19 Oct 2026 — https://quantamagazine.org/ai-proved-the-quasi-riemann-hypothesis-what-happens-now-20261019 | نسخهٔ ۱ (۳۰ سپتامبر): 1/8–7/8، ۱۹۹ صفحه، وارسی‌شده در Lean؛ نسخهٔ ۲ (۵ اکتبر): 1/12–11/12، ۴۹ صفحه، وارسی‌نشده، تنها مقالهٔ ویرایش‌شده به دست انسان؛ فرم‌های متاپلکتیک، فرمول Dunn–Radziwiłł (2021)، Iwaniec 2002؛ نقل‌ها: Lichtman «the most significant AI-for-math achievement so far, by quite a margin.»، Radziwiłł «horribly written (in a way that would lead to immediate rejection at any mathematical journal)» و «the vast majority of consequences of RH already follow from quasi-RH»، Sarnak (تا انسان‌ها همه را بررسی نکنند «a Theorem» نمی‌نامد)، Sawin، Dunn «a surprising synthesis of well-known ideas» | ✅ ⚠️ در لید «377 results» و پایین‌تر «722 OpenAI papers» |
| R06 | Alicia Gallegos, «OpenAI withdraws three preprints a day after releasing 722 manuscripts on unsolved math problems», Retraction Watch, 8 Oct 2026 — https://retractionwatch.com/?p=136176 | ۶ اکتبر: ۷۲۲ دست‌نوشته دربارهٔ ۳۷۲ مسئله؛ ۷ اکتبر: سه پس‌گرفته (Weil classes on split abelian eightfolds؛ Kuga–Satake برای K3؛ Hodge برای حاصل‌ضرب K3)؛ «a sign error»؛ ۱۴ اصلاح؛ پیدا شده در بازبینی داخلی (سخن‌گو)؛ حدود ۵۰٪ نتیجه‌ها تأییدنشده منتشر شد؛ Townsend: «OpenAI should have announced the manuscripts that were lean verified first» | ✅ |
| R07 | OpenAI, `openai/math` README — https://raw.githubusercontent.com/openai/math/main/README.md | امروز: «730 manuscripts organized into 375 families»؛ «~42% top-line results formalized»؛ «Some of the unformalized results could have issues»؛ نوشتار 11/12 «human edited for readability»؛ هر نتیجه به‌طور میانگین «three hours of ChatGPT Pro thinking compute» | ✅ (README خوانده شد؛ خود دست‌نوشته‌ها نه) |
| R08 | Youness Lamzouri, «A new proof that more than 2/3 of the zeros of the Riemann zeta function are simple and on the critical line», arXiv 2609.02882 (v1 2 Sep 2026، v2 8 Sep) — https://arxiv.org/abs/2609.02882 | اثبات تازه با روشی دیگر (یک نابرابری در فضای هیلبرت؛ چکیده استدلال Claude را «technically intricate» می‌خواند) برای > 67.25٪ و ≥ 83.62٪؛ چکیده Claude و آلپوگه–فورمن را نام می‌برد | ✅ (چکیده) |
| R09 | K. M. Knausgård, «More than 83.9% of the zeros of the Riemann zeta function are distinct and more than 67.35% are simple and on the critical line», arXiv 2610.08965 (6 Oct 2026) | ≥ 0.67353؛ Lean 4 با سه اصل اضافه («یک برنامهٔ جست‌وجو true برگرداند»)؛ «تجربه‌ای در پژوهش ریاضی با کمک AI»؛ داوری‌نشده | ✅ (چکیده) ⚠️ چکیده یک جا «67.80%» دارد که با عنوان نمی‌خواند |
| R09b | Biao Wang, «Proportions of the non-trivial zeros of the Riemann zeta function», arXiv 2609.24167 | بهبود بسیار کوچک (δ ≈ 6.7×10⁻⁸) روی روش لامزوری؛ **پس گرفته شده** | ✅ (چکیده؛ استفاده نمی‌شود) |
| R19 | github.com/anthropics/zeta-23-lean (README مخزن) | ساخت با `lake build` در هر پوشه؛ شرط CI: بدون sorry بیرون از فایل گزاره + «Your solution is okay!» از comparator؛ خود README می‌گوید وفاداری گزاره به مقاله را جداگانه باید بررسی کرد | ✅ |

## تاریخچهٔ سهم صفرها روی خط (R10 تا R15، R18)

| شناسه | مقاله | عدد استفاده‌شده | وضعیت |
|---|---|---|---|
| R10 | G. H. Hardy, «Sur les zéros de la fonction ζ(s) de Riemann», C. R. Acad. Sci. Paris 158 (1914) 1012–1014 | بی‌نهایت صفر روی خط | 🔁 (ارجاع و محتوا در جست‌وجو و arXiv 1601.06512، Ivić؛ متن اصلی فرانسوی باز نشد) |
| R11 | A. Selberg, «On the zeros of Riemann's zeta-function», Skr. Norske Vid.-Akad. Oslo I 1942, no. 10 | κ > 0 | 🔁 (R15 §1، R02 §1.3) |
| R12 | N. Levinson, «More than one third of zeros of Riemann's zeta-function are on σ = 1/2», Adv. Math. 13 (1974) 383–436 | > 1/3 | 🔁 (عنوان در مراجع R02؛ «κ > 1/3 in 1974» در R15) |
| R13 | J. B. Conrey, «More than two fifths of the zeros of the Riemann zeta function are on the critical line», J. reine angew. Math. 399 (1989) 1–26 | κ > 0.4088 | 🔁 (R15 ص ۷) |
| R14 | H. M. Bui, B. Conrey, M. P. Young, «More than 41% of the zeros of the zeta function are on the critical line», Acta Arith. 150 (2011) 35–64 — arXiv 1002.4127 | κ > 0.4105 (R15 ص ۸)؛ چکیده: «more than 41%» | ✅ (چکیده) |
| R14b | S. Feng, J. Number Theory 132 (2012) 511–542 | κ > 0.4128؛ یک شکاف که بعداً ترمیم شد (R15 ص ۸) | 🔁 (فقط در جدول study؛ روی دوربین نه) |
| R15 | K. Pratt, N. Robles, A. Zaharescu, D. Zeindler, «More than five-twelfths of the zeros of ζ are on the critical line», Res. Math. Sci. 7 (2020), Paper 2 — arXiv 1802.10521 (v3 15 Sep 2019) | **κ > 0.417293** (ص ۹؛ با بهینه‌سازی §8: κ ≥ 0.417293962)؛ صفرهای ساده: κ* ≥ 0.407511 | ✅ (متن کامل v3 خوانده شد) |
| R18 | H. L. Montgomery, «The pair correlation of zeros of the zeta function», Proc. Sympos. Pure Math. 24 (1973) 181–193 | 2/3 ساده، **به شرط RH** | 🔁 (R02 §1.1 و §1.3) |

### ⚠️ ۴۱٫۶ یا ۴۱٫۷؟
- R15 خودش: κ > 0.417293 ⇒ **۴۱٫۷٪**. عنوانش: «بیش از پنج دوازدهم» (5/12 = 41.67٪).
- R01 و R03: «41.6%». R02: «previous record 5/12».
- **تصمیم:** روی صفحه `41.7%` با زیرنویس «Anthropic's post rounds it as 41.6%»؛ در گفتار «حدود چهل‌ودو درصد». در جدول دمو: `> 41.7%` با همین یادداشت.
- ظرافت دیگر: Claude صفرهای «ساده **و** روی خط» را می‌شمارد؛ رکورد ۲۰۲۰ برای همین نوع 0.4075 بود (R15). R02 خودش با «5/12» مقایسه می‌کند. روی دوربین وارد نمی‌شویم.

## زمینه و اعداد عمومی

| شناسه | منبع | چه چیزی | وضعیت |
|---|---|---|---|
| R16 | Clay Mathematics Institute, Riemann Hypothesis — https://www.claymath.org/millennium/riemann-hypothesis/ | «Formulated in Riemann's 1859 paper»؛ «checked for the first 10,000,000,000,000 solutions»؛ جزو Millennium Prize Problems (مبلغ یک میلیون دلار در R03 و R04، نه در متنی که از Clay دیدیم) | ✅ |
| R17 | D. Platt, T. Trudgian, «The Riemann hypothesis is true up to 3·10¹²», arXiv 2004.09765 (Bull. LMS، DOI 10.1112/blms.12460) | همهٔ صفرها تا ارتفاع 3·10¹² روی خط‌اند | ✅ (چکیده) |
| R20 | mpmath 1.3.0 (نصب‌شده روی همین Mac) | وارسی مستقل دمو: `zeta`، `zetazero`، `nzeros`، `li`، `siegeltheta` | ✅ اجرا شد |
| R21 | OEIS A006880 (π(10ⁿ)) | π(10³)=168، π(10⁴)=1229، π(10⁶)=78498، π(10⁹)=50847534 | 🔁 دانستهٔ استاندارد؛ π تا 10⁶ را خودمان شمردیم |

## چیزهایی که بیرون ماندند

| ادعا | چرا بیرون ماند |
|---|---|
| نام مدل Claude | R01 نامی نمی‌برد. |
| «کانری و گلدستون تأیید کردند» | R01: «examined the paper on short notice»؛ R02: «carefully reading… comments». حکمشان منتشر نشده. می‌گوییم «خواندند». |
| «داوری‌شده / منتشرشده در مجله» | پیدا نکردیم. |
| «نسخهٔ ۱۱/۱۲ قوی‌تر است» (در یادداشت پژوهشی اولیه) | **غلط.** نوار 1/12–11/12 پهن‌تر و ادعا ضعیف‌تر است؛ قوی‌ترِ وارسی‌شده 7/8 است (R05). |
| «۷۲۲ مقالهٔ OpenAI دربارهٔ ریمان» | بیشترشان نه؛ سه پس‌گرفته دربارهٔ هندسهٔ جبری‌اند (R06). |
| «۵۶۰ مقالهٔ وارسی‌نشده / ۱۶۲ صوری‌شده» | فقط در یک سایت درجه‌دو (axeetech)؛ جایش «~42% top-line» از README خود مخزن. |
| پیش‌چاپ Baiying Liu (arXiv 2610.12234، ناحیهٔ کمی بزرگ‌تر) | متن باز نشد؛ فقط در study با 🟡. |
| نقل‌قول Live Science (ماجرای لامزوری) | WebFetch به دامنه اجازه نداد؛ به‌جایش چکیدهٔ خود مقالهٔ لامزوری (R08). |
| Wikipedia | WebFetch اجازه نداد؛ جایش مقاله‌های اصلی. |
| مریم میرزاخانی | روی «سطوح ریمان» کار می‌کرد، نه فرضیهٔ ریمان؛ در این قسمت پیوند نمی‌سازیم (study §۱۵). |
| Gowers دربارهٔ «قضیه‌های بی‌نام ریاضی‌دان» (R04) | موضوع جانبی (انتساب)؛ جا نشد. |
| «اولین بار AI…» | هیچ ادعای «اولین» در متن نیست. |

## نقل‌قول‌های روی دوربین (ترجمهٔ ما، کوتاه)

| در متن | اصل | منبع |
|---|---|---|
| «یه تلاش واقعی بکن» | «take a real stab» | R01 |
| «هیچ مسیری… به خود فرضیه نیست» (فقط study و هوک ۵) | «there is no pathway for any of these approaches to deal with the actual Riemann hypothesis» | R03، Maynard |
| «مهم‌ترین دستاورد هوش مصنوعی تو ریاضی، با فاصلهٔ زیاد» | «the most significant AI-for-math achievement so far, by quite a margin» | R05، Lichtman |
| «نوشتار… اون‌قدر بده که هر مجله‌ای فوراً ردشون می‌کرد» | «horribly written (in a way that would lead to immediate rejection at any mathematical journal)» | R05، Radziwiłł |
| «تا آدم‌ها همهٔ جزئیات رو بررسی نکنن، بهش نمی‌گه قضیه» | نقل غیرمستقیم Quanta از Sarnak | R05 |
