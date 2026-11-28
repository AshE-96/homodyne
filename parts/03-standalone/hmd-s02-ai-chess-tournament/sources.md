# HMD-S02 · منابع

> همهٔ منابع ۲۸ نوامبر ۲۰۲۶ (۷ آذر ۱۴۰۵) باز و خوانده شدند، مگر جایی که نوشته شده. نقل‌قول‌ها کوتاه‌اند و فقط برای نقد و گزارش.
> برچسب‌ها: ✅ از متن یا دادهٔ خود منبع خوانده شد · 🔁 از گزارش یک منبع دیگر (منبع اصلی باز نشد) · ⚠️ اختلاف یا ابهام · `[VERIFY]` پیش از انتشار دوباره ببین.
> **هیچ نتیجه‌ای از مسابقهٔ خود ما در این فایل نیست.** آن عددها فقط از `artifact/results/<run>/report.md` می‌آیند، بعد از اجرای واقعی ([RUN]).

## جدول‌ها و آزمون‌های منتشرشده

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| R01 | Kaggle Benchmarks، جدول «Chess Text» — `https://www.kaggle.com/api/v1/benchmarks/kaggle/chess-text/leaderboard` (JSON، بی‌ورود، ۱۳۵٬۳۸۲ بایت، تاریخ ارزیابی ۲۴ نوامبر ۲۰۲۶) | **۴۶ مدل**. اول Gemini 4 Neon با امتیاز **۱٬۷۹۱** (بازه +۳۵/−۳۵)، دوم Gemini 4 Carbon ۱٬۶۵۱، سوم GPT-6.2 Astra ۱٬۵۸۵. بهترین Claude: Claude Fable 5.2، **رتبهٔ ۱۲** با ۱٬۳۲۴. آخر: Claude Sonnet 4.5 با ۰. ستون «Avg. Tokens/Turn» از ۱٬۵۲۴ (Claude Opus 5.5) تا ۲۹٬۶۷۹ (Grok 4.7). خلاصه در `artifact/derived/kaggle_chess_text_facts.json` | ✅ ⚠️ مجوز ذکر نشده `[VERIFY]`؛ خام را بازنشر نمی‌کنیم، نمودار را خودمان می‌کشیم. واحد ستون «Avg. Cost/Turn» روشن نیست؛ استفاده نمی‌شود. یک بار خطای TLS داد و بار دوم جواب داد |
| R02 | Kaggle، دیتاست «Chess Openings Gameplay» — `kaggle.com/datasets/kaggle/chess-text-openings-gameplay` (توضیح از `api/v1/datasets/view/...`) | لاگ بازی‌های Game Arena؛ «all-play-all»؛ هر جفت **۴۰ بازی، ۲۰ با سفید و ۲۰ با سیاه**؛ مجوز **CC BY 4.0**؛ ۲٫۳ گیگابایت؛ به‌روزرسانی ۵ مه ۲۰۲۶؛ هشدار خودشان: استدلال نمایش‌داده «خلاصهٔ تولیدشده» است، نه ردّ واقعی محاسبه | ✅ (توضیح دیتاست؛ خود داده دانلود نشد) |
| R03 | Kaggle Blog، «Revealing the first Game Arena Leaderboard: the Chess Text Leaderboard» — `kaggle.com/blog/chess-text-leaderboard` | امتیاز با مدل **Bradley–Terry** روی نتیجهٔ بازی مدل‌ها با هم، «نسبت به همین جمعِ مدل‌ها»؛ Elo انسانی تخمینی با بازی در برابر سطح‌های Stockfish و رگرسیون خطی؛ بازهٔ اطمینان با ۵۰۰ بار bootstrap | 🔁 صفحه با جاوااسکریپت ساخته می‌شود و متنش باز نشد؛ از خلاصهٔ جست‌وجو. `[VERIFY]` پیش از گفتن «Bradley–Terry» روی دوربین؛ در متن گفتاری فقط «امتیازی که خود Kaggle از بازی مدل‌ها با هم حساب می‌کند» |
| R04 | Epoch AI، «Chess Puzzles» — `epoch.ai/benchmarks/chess-puzzles` + `epoch.ai/data/benchmark_data.zip` (`chess_puzzles.csv`، ۱۷۱ ردیف، ۲۸ نوامبر ۲۰۲۶) | **۱۰۰ وضعیت**، هر کدام یک بهترین حرکت؛ ساختهٔ خود Epoch با Stockfish («do not appear in any other source»)؛ ورودی FEN؛ جواب چهارنویسه‌ای مثل b1c3؛ نمره‌دهی دقیق (نسخهٔ ۲، ۱۴ اکتبر ۲۰۲۶). اول gemini-4-neon_xhigh **۰٫۸۳**، دوم claude-fable-5-2_max ۰٫۷۹. پنج بازیکن انسان هر کدام حدود ۲۰ معما بی‌کمک حل کردند؛ دو نفر اول **۷۵٪** (نمونه‌شان از کل سخت‌تر است). مجوز داده: **CC BY 4.0** (README داخل zip) | ✅ ⚠️ در کارت ایده ۱۷۰ ردیف بود؛ امروز ۱۷۱ |
| R05 | Kolasani, Saplin, Crispino, Montgomery, Davis, Zaharia, Wang, Wang، «LLM CHESS: Benchmarking Reasoning and Instruction-Following in LLMs through Chess»، arXiv 2512.01992 (۱ دسامبر ۲۰۲۵) + مخزن `github.com/maxim-saplin/llm_chess` | **بیش از ۵۰ مدل** در برابر بازیکن **تصادفی**؛ مدل می‌تواند صفحه و **فهرست حرکت‌های مجاز** را بخواهد (`get_legal_moves`)؛ سه اشتباه در یک نوبت = باخت. مدل‌های غیراستدلالی: میانگین **۰٫۷٪ برد**، **۷۱٫۹٪** باخت‌ها از خطای پیروی از دستور؛ استدلالی: ۴۵٫۴٪ برد. o3 (low): Elo تعدیل‌شده حدود **۷۵۸**؛ «far below the human master level»؛ موتور Elo: Komodo Dragon 1 (پیوست B.2)، میانگین کاربر chess.com ۶۱۱٫۱۰ (متن مقاله). جدول ۲: GPT-4.1-mini در ۳۱٫۳٪ نیم‌حرکت‌ها blunder | ✅ (HTML مقاله؛ بازبینی ۲۸ نوامبر: عددهای ۰٫۷٪، ۷۱٫۹٪، ۴۵٫۴٪، ۷۵۸، ۳۱٫۳٪، Dragon 1 و ۶۱۱٫۱۰ در متن هست؛ نقل روی دک عین چکیده: «many state-of-the-art models struggle to complete games») ⚠️ مجوز مخزن در README دوگانه (Apache-2.0 / MIT)؛ کد آن را استفاده نمی‌کنیم |
| R06 | Chess.com، «OpenAI's o3 Crushes Grok 4 In Final, Wins Kaggle's AI Chess Exhibition Tournament»، به‌روزرسانی ۷ اوت ۲۰۲۵ — `chess.com/news/view/kaggle-game-arena-chess-2025-day-3`؛ پیش‌نمایش ۴ اوت: `chess.com/news/view/which-ai-model-is-the-best-at-chess-kaggle-game-arena` | فینال نمایشی Kaggle Game Arena (۵ تا ۷ اوت ۲۰۲۵): **o3، Grok 4 را ۴–۰ برد**؛ رده‌بندی سوم: Gemini 2.5 Pro، o4-mini را ۳٫۵–۰٫۵. پیش‌نمایش: مدل‌ها «make illegal moves and absurd resignations» | ✅ |
| R07 | Google DeepMind، `github.com/google-deepmind/game_arena` (README، Apache-2.0) | هارنس Game Arena: ورودی دست‌کم وضعیت بازی (FEN) و نام بازیکن، اختیاری تاریخچه و حرکت‌های مجاز؛ «rethinking»: بعد از حرکت غیرقانونی «the model is prompted again… a limited number of times»؛ حالت رأی اکثریت: حرکت غیرقانونی = باخت | ✅ ⚠️ تعداد دقیق دفعه‌های rethink در جدول Kaggle نوشته نشده `[VERIFY]` |

## پیشینهٔ پژوهشی (درون مدل)

| شناسه | منبع | چه چیزی | وضعیت |
|---|---|---|---|
| R08 | Nicholas Carlini، «Playing chess with large language models»، ۲۲ سپتامبر ۲۰۲۳ — `nicholas.carlini.com/writing/2023/chess-llm.html` | gpt-3.5-turbo-instruct با ورودی PGN؛ پس از «at least a few thousand moves» هیچ حرکت نامعتبری نزد؛ GPT-4 در یک بازی چند حرکت غیرقانونی؛ عدد Elo نداده | ✅ |
| R09 | dynomight، «Something weird is happening with LLMs and chess»، نوامبر ۲۰۲۴ — `dynomight.net/chess/` | ۱۱ مدل در برابر Stockfish در **پایین‌ترین** سطح؛ فقط gpt-3.5-turbo-instruct «Excellent»، بقیه (از جمله مدل‌های بزرگ‌تر چت) «Terrible»؛ برای مدل‌های OpenAI تا ۱۰ بار تلاش و بعد حرکت تصادفی | ✅ |
| R10 | Adam Karvonen، «Chess-GPT's Internal World Model»، ۳ ژانویهٔ ۲۰۲۴ — `adamkarvonen.github.io/machine_learning/2024/01/03/chess-world-models.html`؛ مقاله: arXiv 2403.15498 (COLM 2024) | مدل **۵۰ میلیون پارامتری** که فقط روی متن بازی‌ها آموزش دید: **۹۹٫۸٪** حرکت قانونی؛ یک «کاوشگر خطی» (linear probe) از فعال‌سازی‌های درونش جای مهره‌ها را در **۹۹٫۲٪** خانه‌ها درست خواند (۱۰٬۰۰۰ بازی) | ✅ (بلاگ؛ چکیدهٔ arXiv) |
| R11 | Ruoss و دیگران (Google DeepMind)، «Amortized Planning with Large-Scale Transformers: A Case Study on Chess»، arXiv 2402.04494 (v2 اکتبر ۲۰۲۴؛ نسخهٔ اول با عنوان «Grandmaster-Level Chess Without Search») | ترنسفورمر تا **۲۷۰ میلیون** پارامتر، ۱۰ میلیون بازی با برچسب Stockfish 16، **بدون جست‌وجوی صریح**؛ Elo بلیتس Lichess **۲۸۹۵** در برابر آدم‌ها | ✅ (چکیده) |

## داور، فرمول‌ها و ابزار

| شناسه | منبع | چه چیزی | وضعیت |
|---|---|---|---|
| R12 | کد Lichess: `lichess-org/scalachess` `core/src/main/scala/eval.scala`؛ `lichess-org/lila` `modules/analyse/src/main/AccuracyPercent.scala` و `modules/tree/src/main/Advice.scala` | win% = 50 + 50·(2/(1+e^(−0.00368208·cp)) − 1)، cp بریده در ±۱۰۰۰؛ دقت حرکت = 103.1668·e^(−0.04354·Δwin%) − 3.1669 (+۱)؛ آستانه‌ها روی «شانس برد» (−۱ تا +۱): ۰٫۳ blunder، ۰٫۲ mistake، ۰٫۱ inaccuracy. صفحهٔ `lichess.org/page/accuracy` به WebFetch ۴۰۳ داد؛ از خود کد خواندیم | ✅ |
| R13 | Lichess cloud eval API — `lichess.org/api/cloud-eval?fen=…` (بی‌توکن) | بعد از 1.e4: **+۱۸ سانتی‌پیاده** به نفع سفید، عمق ۷۰ (همان عدد کارت ایده؛ ۲۸ نوامبر دوباره آزموده شد). explorer `/masters` بی‌توکن ۲۰۰؛ `/lichess` حالا **۴۰۱** (توکن می‌خواهد) | ✅ |
| R14 | `github.com/lichess-org/chess-openings` (commit 48a8c0e7، ۲۰ نوامبر ۲۰۲۶) | ۳٬۸۶۵ خط گشایش نام‌دار؛ **CC0**؛ کتاب گشایش دموی ما (`artifact/derived/openings.tsv`) | ✅ |
| R15 | Stockfish — `stockfishchess.org`؛ Homebrew: «stable 19»؛ مجوز GPL-3.0 · python-chess 1.11.2 (GPL-3.0، `pip3 install --user chess`) | داور اختیاری دمو؛ قوانین شطرنج در دمو | ✅ (`brew info stockfish`؛ نصب نشده) |
| R16 | فرمول Elo (امتیاز مورد انتظار E = 1/(1+10^((Rb−Ra)/400))) — آرپاد الو، *The Rating of Chessplayers, Past and Present* (۱۹۷۸)؛ همان در مقررات رتبه‌بندی FIDE (جدول تبدیل) | مثال: ۲۰۰ امتیاز اختلاف ⇒ حدود ۰٫۷۶ | 🔁 (فرمول استاندارد؛ کتاب باز نشد) |
| R17 | FIDE Laws of Chess (اجرا از ۱ ژانویهٔ ۲۰۲۳)، ماده ۷٫۵٫۵ — `rcc.fide.com/article7/` | حرکت غیرقانونیِ کامل‌شدهٔ اول: دو دقیقه به حریف؛ **دومی** از همان بازیکن: «the arbiter shall declare the game lost»، مگر حریف با هیچ ترتیبی نتواند مات کند (آن‌وقت تساوی). سریع/برق‌آسا (پیوست‌ها، از اصلاحیهٔ ۲۰۱۸): اولی یک دقیقه به حریف، دومی باخت (از گزارش‌های ثانوی؛ پیش از ۲۰۱۸ در برق‌آسا اولی می‌توانست باخت باشد) | 🔁 متن ماده از خلاصهٔ جست‌وجو و پیشنهاد اصلاحیهٔ ۲۰۱۸ (Annex 19)؛ صفحهٔ RCC (و `handbook.fide.com`) ۲۸ نوامبر هم ۴۰۴/بی‌جواب بود `[VERIFY]`. در گفتار با «معمولاً» |

## عددهای خود ما (نه منبع بیرونی)

| چه | کجا |
|---|---|
| ۷٬۹۸۲ وضعیت در کتاب گشایش؛ «Ruy Lopez (C60)» بعد از 1.e4 e5 2.Nf3 Nc6 3.Bb5 | `artifact/chess_core.py` و `--selftest` |
| win%(+۱۰۰) = ۵۹٫۱، win%(+۱۸) = ۵۱٫۷؛ دقت حرکتی که از ۰ به −۱۰۰ می‌برد = ۶۷٫۲ | `--selftest` (فرمول R12) |
| از وضعیت برابر، −۶۰ = inaccuracy، −۱۵۰ = mistake، −۲۰۰ و −۳۰۰ = blunder | `--selftest` (فرمول R12) |
| هر چیزی دربارهٔ مسابقهٔ پنج مدل | **[RUN]** `artifact/results/<run>/` |

## بیرون ماند

- نام و رتبهٔ بازیکنان ایرانی (کارت ایده: فیروزجا، مقصودلو): بازبینی نشد؛ در متن نیامد. اگر لازم شد، از `ratings.fide.com` با تاریخ.
- نقل‌های تفسیر فینال نمایشی ۲۰۲۵ (گزارشگر مشهور): فقط از خلاصهٔ جست‌وجو؛ استفاده نمی‌شود.
- مقالهٔ `chessbench llm failures` (York University PDF) و `lightnesscaster/Chess-LLM-Benchmark`: در جست‌وجو دیده شد، باز نشد.
- «Bradley–Terry» روی دوربین: تا R03 خوانده نشده، نه.
