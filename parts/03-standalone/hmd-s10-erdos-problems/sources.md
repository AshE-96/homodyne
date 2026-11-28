# HMD-S10 · منابع

> همهٔ منابع ۲۸ نوامبر ۲۰۲۶ باز و خوانده شدند، مگر جایی که نوشته شده. نقل‌قول‌ها کوتاه‌اند و فقط برای نقد و گزارش خبری.
> برچسب‌ها: ✅ از متن منبع خوانده شد · 🔁 از متن یک منبع اصلیِ دیگر نقل شده (خود منبع باز نشد) · ⚠️ اختلاف یا ابهام · 🚫 عمداً باز نشد.
> **قاعدهٔ این قسمت:** صفحه‌های erdosproblems.com را با ابزار AI باز نکردیم، چون `robots.txt` سایت ایجنت‌های AI (از جمله `Claude-User` و `ChatGPT-User`) را منع کرده است (R02). هر چه از سایت لازم بود، از نسخهٔ باز گیت‌هاب (R01، R04) یا از گزارش‌های دیگر آمده. محمد می‌تواند صفحه‌ها را خودش در مرورگر باز کند (`prep-fa.md` §۱).

## داده و سیاست سایت

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| R01 | پایگاه دادهٔ باز مسئله‌های اردوش، `github.com/teorth/erdosproblems` (Apache-2.0؛ نگه‌دارنده‌ها: Thomas Bloom و Terence Tao طبق `CITATIONS.cff`؛ شروع ۱ سپتامبر ۲۰۲۵). فایل‌ها: `data/problems.yaml`، `data/statistics_history.csv`، `STATISTICS.md`، `README.md`. commit دادهٔ ما: `706c140` (۲۴ نوامبر ۲۰۲۶) | ۱٬۲۲۱ مسئله؛ ۳۳۹ اثبات‌شده (۱۸۴ در Lean)، ۱۴۴ ردشده (۹۷)، ۱۰۴ «به شکل دیگر حل‌شده» (۳۵)، ۵۷۰ «کاملاً باز»، ۲۹ / ۹ / ۸ «باز ولی با محاسبهٔ متناهی»، ۵ / ۹ / ۴ مربوط به ZFC؛ ۱۱۴ با جایزهٔ نقدی (از ۱۰ تا ۱۰٬۰۰۰ دلار، و چند پوند و روپیه)؛ ۷ مسئلهٔ «open (Lean)» با یادداشت «Not yet digested by a human reader, so the informal status remains open»؛ تاریخچهٔ شمارش‌ها از ۳۱ اوت ۲۰۲۵؛ متن STATISTICS.md: شمارش‌ها «moved here on October 6, 2026» و سایت «no longer displays the statuses of problems, nor the count or percentage of problems solved»؛ README: نمودار پیشرفت «frozen as of October 6, 2026» | ✅ دانلود شد (`artifact/data/`، sha256 در `prep-fa.md` §۳) |
| R02 | `https://www.erdosproblems.com/robots.txt` (۲۸ نوامبر ۲۰۲۶) | `Content-Signal: search=yes,ai-train=no,use=reference` برای همه؛ `Disallow: /` برای ده‌ها خزندهٔ آموزش، جست‌وجوی AI و «AI Agents» از جمله `Claude-User` و `ChatGPT-User` | ✅ |
| R03 | erdosproblems.com، پست سیاست تازه، ۶ اکتبر ۲۰۲۶ (`/forum/thread/blog:9`) | فقط از طریق نقل R01: سایت دیگر وضعیت و درصد حل‌شده را نشان نمی‌دهد؛ «open questions worth understanding rather than as a scoreboard» (عبارت R01، نه لزوماً خود پست) | 🚫 🔁 [VERIFY] محمد پست را در مرورگر بخواند و یک جملهٔ کوتاه از خودش را در قاب ۱۳ بگذارد |
| R04 | ویکی همان مخزن: «AI contributions to Erdős problems» + «AI contribution section placement system» + «Disclaimers and caveats» + «Notable cases» + «How have AI companies been invested…» — `github.com/teorth/erdosproblems/wiki` (commit `c8ad430`، «freeze»، ۳۰ ژوئن ۲۰۲۶) | ۵۳۸ ردیف در ۸ بخش (شمارش ما): 1(a) ۶۱، 1(b) ۲۵، 1(c) ۳۸، 1(d) ۱۳۲، 2(a) ۸۴، 2(b) ۱۸۵، 2(c) ۱۰، 2(d) ۳؛ تعریف بخش‌ها؛ رنگ‌ها 🟢🟡🔴⚪؛ هشدارها: «This page is not a benchmark»، «“open” is always provisional»، «Absence of past progress may reflect obscurity rather than difficulty»، «we cannot conclude… influenced by this literature»؛ ردیف‌های #333، #728، #1026، #90، #1196 | ✅ (git clone) |
| R04b | همان ویکی، صفحهٔ «Notable cases of AI contributions…» (commit `c8ad430`) | #۱۱۹۶: «human experts have already spent substantial effort»؛ #۹۰: «prior widespread expert attention» | ✅ (git clone، ۲۸ نوامبر ۲۰۲۶) |
| R04a | همان ویکی، شمارش ما از بخش 2(a) | ۲۰ ردیف «GPT-5» با تاریخ ۱۱ تا ۲۰ اکتبر ۲۰۲۵: ۱۰ «Full solution found» و ۱۰ «Partial results found» (`erdos_live.py --selftest`) | ✅ حساب ما |

## ماجرای اکتبر ۲۰۲۵

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| R05 | Anthony Ha, «OpenAI's 'embarrassing' math», TechCrunch, 19 Oct 2025 — https://techcrunch.com/2025/10/19/openais-embarrassing-math/ | توییت پاک‌شدهٔ Kevin Weil (معاون OpenAI): «GPT-5 found solutions to 10 (!) previously unsolved Erdős problems and made progress on 11 others»؛ Bloom: «a dramatic misrepresentation»، «I personally am unaware of a paper which solves it»، «GPT-5 found references, which solved these problems, that I personally was unaware of»؛ Hassabis: «This is embarrassing»؛ Bubeck: «only solutions in the literature were found» و «I know how hard it is to search the literature» | ✅ |
| R06 | Matthias Bastian, The Decoder, 18 Oct 2025 — https://the-decoder.com/leading-openai-researcher-announced-a-gpt-5-math-breakthrough-that-never-happened/ | پاک‌شدن توییت و پس‌گرفتن ادعا | ✅ (بخش رایگان؛ بقیه پشت paywall) ⚠️ تاریخ دقیق خود توییت در هیچ‌کدام نیست؛ در متن فقط «اواسط اکتبر» |

## داستان‌های ۲۰۲۵ تا ۲۰۲۶

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| R07 | MacTutor, «Paul Erdős» — https://mathshistory.st-andrews.ac.uk/Biographies/Erdos/ | ۲۶ مارس ۱۹۱۳ بوداپست – ۲۰ سپتامبر ۱۹۹۶ ورشو؛ «بیش از ۱۵۰۰ مقاله» (به نقل از سوگ‌نامهٔ New York Times)؛ خانهٔ ثابت نداشت؛ درآمد سخنرانی‌ها را به دانشجوها یا جایزهٔ مسئله‌ها می‌داد | ✅ |
| R08 | Konstantin Kakaes, «Why the Legendary Erdős Problems Are Falling to AI», *Quanta Magazine*, 3 Aug 2026 — https://www.quantamagazine.org/how-ai-tore-through-a-mathematical-community-20260803/ | بلوم سایت را «early 2023» با چند صد مسئله راه انداخت؛ صبح کریسمس ۲۰۲۵ Kevin Barreto اثبات #333 را گذاشت با عبارت «the first case of an LLM fully autonomously resolving an Erdős problem»؛ چند ساعت بعد معلوم شد اردوش در مقاله‌ای از ۱۹۷۷ حلش کرده؛ #728 تا ۴ ژانویه ۲۰۲۶؛ در زمان انتشار «565 solved and 652 open»؛ Gowers: «No previous AI-generated proof has come close to that»؛ چند هفته بعد ریاضی‌دان‌ها نتیجهٔ #90 را بهتر کردند | ✅ (خلاصهٔ WebFetch؛ نقل‌ها کوتاه) ⚠️ «565 / 652» دسته‌بندی سایت در اوت است و با دسته‌بندی R01 امروز قابل مقایسه نیست |
| R09 | Terence Tao, «The story of Erdős problem #1026», بلاگ، 8 Dec 2025 — https://terrytao.wordpress.com/2025/12/08/the-story-of-erdos-problem-126/ (نشانی «126» دارد، ولی مطلب دربارهٔ #1026 است) | صورت بازی (آلیس، باب، کپه‌ها)؛ ۷ دسامبر: Boris Alexeev با Aristotle اثبات خودکار c(k²) = 1/k در Lean؛ ابزارهای deep research مقاله را پیدا نکردند، یک جست‌وجوی Google Scholar مقالهٔ Tidor–Wang–Yang (2016) را پیدا کرد؛ اثبات Aristotle نسخه‌ای از استدلال Seidenberg (1959)؛ «turned out to not be particularly novel»؛ AlphaEvolve برای کران بالا تا n ≤ 16؛ نابرابری Σxᵢ² ≤ (بیشینهٔ صعودی)·(بیشینهٔ نزولی)؛ حدس کلی c(k²+2a+1) = k/(k²+a) و اثبات با Baek–Koizumi–Ueoro (2024) و Praton | ✅ |
| R10 | google-deepmind/formal-conjectures, `FormalConjectures/ErdosProblems/1026.lean` (Apache-2.0) | صورت دقیق: k² عدد مثبت متمایز با جمع ۱ ⇒ زیردنبالهٔ یکنوایی با جمع ≥ 1/k؛ «first proved by Tidor, Wang, and Yang [TWY16]… implicit in work of Wagner [Wa17]. A proof was given and formalised by Aristotle»؛ Hanani (1957): c ≥ 1/√2؛ اثبات Lean در `plby/lean-proofs` | ✅ |
| R11 | J. Tidor, V. Wang, B. Yang, «1-color avoiding paths, special tournaments, and incidence geometry», arXiv 1608.04153 (2016) | نتیجهٔ وزن‌دار (به گفتهٔ R09 و R10) | 🔁 (فقط چکیده باز شد؛ چکیده خود نتیجهٔ وزن‌دار را نمی‌گوید) |
| R12 | Nat Sothanaphan, «Resolution of Erdős Problem #728: a writeup of Aristotle's Lean proof», arXiv 2601.07421 (12 Jan 2026) | «the first Erdős problem… regarded as fully resolved autonomously by an AI system»؛ GPT-5.2 Pro + Aristotle (Harmonic)؛ راهبرد شبیه کارهای اردوش و Pomerance | ✅ (چکیده) |
| R13 | T. Feng, T. Trinh, G. Bingham و ۲۱ نفر دیگر، «Semi-Autonomous Mathematics Discovery with Gemini: A Case Study on the Erdős Problems», arXiv 2601.22401 (29 Jan 2026) | ۷۰۰ مسئلهٔ «Open» بررسی شد؛ ۱۳ تا حل شد؛ ۵ «seemingly novel»؛ ۸ در مقاله‌های قبلی؛ «obscurity rather than difficulty»؛ خطر «subconscious plagiarism» | ✅ (چکیده) ⚠️ کارت ایده «حدود ۷۰۰ غربال، ۴ حل» نوشته بود؛ عدد درست همین است |
| R14 | OpenAI, «model disproves discrete geometry conjecture», 20 May 2026 — https://openai.com/index/model-disproves-discrete-geometry-conjecture/ | حدس فاصلهٔ واحد اردوش (n^(1+o(1))) غلط است: بی‌نهایت پیکربندی با دست‌کم n^(1+δ) جفت؛ δ در اثبات اصلی صریح نیست، بهبود Will Sawin: δ = 0.014؛ مدل استدلالی داخلی و عمومی؛ «checked by a group of external mathematicians» (بی‌شمار و بی‌نام)؛ سال طرح ۱۹۴۶؛ نقل‌ها: Alon «one of Erdős' favorite problems»، Gowers «a milestone in AI mathematics» و توصیه به پذیرش در Annals اگر نویسنده انسان بود، Tsimerman، Bloom «a moderated yes» | ✅ |
| R15 | N. Alon, T. F. Bloom, W. T. Gowers, D. Litt, W. Sawin, A. Shankar, J. Tsimerman, V. Wang, M. M. Wood, «Remarks on the disproof of the unit distance conjecture», arXiv 2605.20695 (20 May 2026) | «a short, digested, human-verified version» از مثال نقض OpenAI (عبارت «checked by hand» در متن نیست؛ در بدنه فقط Litt وارسی خودش را شرح می‌دهد)؛ ایده‌ها در نگاه به عقب به Ellenberg–Venkatesh، Golod–Shafarevich و Hajir–Maire–Ramakrishna می‌رسد | ✅ (چکیده) |
| R16 | B. Alexeev, K. Barreto, Y. Li, J. D. Lichtman, L. Price, J. I. Shah, Q. Tang, T. Tao, «Primitive sets and von Mangoldt chains: Erdős Problem #1196 and beyond», arXiv 2605.00301 (1 May 2026) | روش «suggested from output of GPT-5.4 Pro»؛ #1196 و #1217؛ اثبات کوتاه حدس مجموعه‌های اولیه (#164) | ✅ (چکیده؛ فقط در study) |
| R17 | P. Erdős, G. Szekeres, «A combinatorial problem in geometry», Compositio Math. 2 (1935) 463–470؛ A. Seidenberg, «A simple proof of a theorem of Erdős and Szekeres», J. London Math. Soc. 34 (1959) 352 | قضیهٔ زیردنبالهٔ یکنوا؛ برچسب‌گذاری جفت‌ها | 🔁 (ارجاع در R09 و R10؛ متن‌ها باز نشد؛ ریاضی را خودمان بازسازی و در `--selftest` آزمودیم) |

## حساب‌های خودمان (`artifact/erdos_live.py --selftest`، ۲۸ نوامبر ۲۰۲۶)

| عدد | از کجا |
|---|---|
| شمارش‌های وضعیت (۳۳۹، ۱۴۴، ۱۰۴، ۵۷۰، ۴۶، ۱۸، ۱۱۴، ۷) | `problems.yaml` در commit `706c140`؛ برابر `STATISTICS.md` |
| ۲۰ ردیف GPT-5 در اکتبر ۲۰۲۵ (۱۰ + ۱۰) | ویکی R04، بخش 2(a) |
| بازی سکه‌ها: سهم باب ≥ 1/k؛ تقسیم آلیس ۳ ۲ ۱ ۶ ۵ ۴ ۹ ۸ ۷ سهم باب را به 1/k نزدیک می‌کند؛ مربع‌ها هرگز روی هم نمی‌افتند (۲۴۰ تقسیم تصادفی) | `erdos_core.py` |

## چیزهایی که بیرون ماندند

| مورد | چرا |
|---|---|
| صفحه‌های خود erdosproblems.com (مسئله‌ها، انجمن، blog:2 و blog:9) | robots.txt ایجنت AI را منع کرده (R02)؛ از R01 و R04 استفاده شد؛ محمد در مرورگر نگاه کند. |
| نقل‌های Tao در Mastodon دربارهٔ #728 («سرعت، نه سختی») | فقط در گزارش پشت paywall دیدیم (The Decoder، ۱۶ ژانویه ۲۰۲۶)؛ متن اصلی پیدا نشد. |
| «Tao گفت فقط ۱ تا ۲ درصد مسئله‌ها…» | فقط در خلاصهٔ جست‌وجو؛ منبع اصلی باز نشد. |
| اعلام OpenAI در ۱ اوت ۲۰۲۶ (مدل «Astra»، «سه مسئلهٔ دیگر اردوش») | فقط از R08؛ منبع اصلی باز نشد؛ لازم نبود. |
| مسئلهٔ #3 (جایزهٔ ۵۰۰۰ دلاری) با برچسب «open (Lean)» | واقعیت ثبت‌شده در R01 است، ولی ادعای پشتش (یک اثبات Lean از مخزن `openai/math`) را هیچ انسانی هنوز هضم نکرده؛ در متن گفتاری نیامد؛ فقط study §۶ با احتیاط. |
| نام مدل‌ها در ویکی (مثل «Claude Mythos»، «GPT-5.5 Pro») | در صفحهٔ دمو هست (همان‌طور که ویکی ثبت کرده)؛ در گفتار رده‌بندی شرکت‌ها نمی‌سازیم. |
| «اولین بار AI…» | فقط به صورت نقل ادعای دیگران (#333، #728)، نه ادعای ما. |

## نقل‌قول‌های روی دوربین (ترجمهٔ ما، کوتاه)

| در متن | اصل | منبع |
|---|---|---|
| «اولین باره که یه مدل زبانی، کاملاً خودکار، یه مسئلهٔ اردوش رو حل کرده» | «the first case of an LLM fully autonomously resolving an Erdős problem» | R08 (Barreto) |
| «برای ده مسئلهٔ حل‌نشده راه‌حل پیدا کرد» | «found solutions to 10 (!) previously unsolved Erdős problems» | R05 (Weil) |
| «تحریف شدید» | «a dramatic misrepresentation» | R05 (Bloom) |
| «من شخصاً مقاله‌ای سراغ ندارم که حلش کرده باشه» | «I personally am unaware of a paper which solves it» | R05 (Bloom) |
| «خجالت‌آوره» | «This is embarrassing» | R05 (Hassabis) |
| «می‌دونم جست‌وجو تو مقاله‌ها چقدر سخته» | «I know how hard it is to search the literature» | R05 (Bubeck) |
| «گمنامی، نه سختی» | «obscurity rather than difficulty» | R13، R04 |
| «معلوم شد چندان تازه نبود» | «turned out to not be particularly novel» | R09 (Tao) |
| «یه نقطهٔ عطف در ریاضیِ هوش مصنوعی» | «a milestone in AI mathematics» | R14 (Gowers) |
| «سؤال بازی که ارزش فهمیدن داره، نه جدول امتیاز» | «open questions worth understanding rather than as a scoreboard» | R01 (عبارت مخزن، به نقل از سیاست R03) |
