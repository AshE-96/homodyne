# HMD-S02 · Silent Breakthrough · مسابقهٔ شطرنج مدل‌های AI: کدام واقعاً بازی می‌کند؟

**قالب:** Silent Breakthrough (تک‌قسمتی علم و داده) · **فصل ۱، پس از HMD-005 و پیش از HMD-006** · **هوک:** Curiosity-Gap (همسایه‌ها Shock دارند)
**وضعیت:** نیازمند اجرا [RUN] (۲۸ نوامبر ۲۰۲۶). منابع عمومی همان روز از منبع اصلی بازبینی شدند؛ دمو و `--selftest` بی‌کلید و بی‌شبکه سبز است. **هیچ API پولی صدا زده نشد؛ هیچ عددی از مسابقهٔ خودمان نوشته نشده.**
**زمان برآوردی:** حدود ۱۲:۱۵ · **واژهٔ گفتاری:** ۱٬۴۵۹ (بی‌جمله‌های [RUN]) · **قاب:** ۱۵ · **قاب‌های دک:** ۱۵ + کاور

**جملهٔ مرکزی:** معما عکس است، بازی فیلم. مدل صفحه را نمی‌بیند؛ از یک خط متن (FEN) و تاریخچه باید هر بار بسازدش. پنج مدل در یک دورهٔ ۲۰ بازی با قانونِ از‌پیش‌قفل‌شده (بی‌فهرست حرکت مجاز، یک فرصت دوباره، بار دوم باخت) بازی می‌کنند؛ هر حرکت غیرقانونی تشخیص داده می‌شود (هفت نوع)، داخل و بیرون کتاب گشایش جدا شمرده می‌شود، و حرکت‌های قانونی با Stockfish (اختیاری) سنجیده می‌شوند.

**مرز ادعا:** بیست بازی در یک روز؛ Elo ساخته نمی‌شود؛ ورودی فقط متن؛ فرق داخل/بیرون کتاب نشانه است نه اثبات؛ دربارهٔ «فهمیدن» چیزی نمی‌گوید.

## فایل‌ها

| فایل | چیست |
|---|---|
| [`script-fa.md`](script-fa.md) | متن ضبط v6، ۱۵ قاب، جاهای [RUN] با شاخه |
| [`hooks-fa.md`](hooks-fa.md) | پنج هوک؛ Curiosity-Gap انتخاب شده (Shock برای این جایگاه ممنوع) |
| [`package-fa.md`](package-fa.md) | عنوان، تامبنیل، توضیحات، Chapters، دو Short، پست Community |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ دک → `deck-fa.html` و `deck-en.html` (`python3 scripts/build-decks.py --only hmd-s02`) |
| [`sources.md`](sources.md) | منابع R01–R17، وضعیت بازبینی، مجوزها، «بیرون ماند» |
| [`study-fa.md`](study-fa.md) | **سند مطالعه**: قانون، نمادها، سانتی‌پیاده و دقت، Elo، چرا LLM خطا می‌کند، کتاب گشایش، هارنس؛ ۱۲ سؤال |
| [`cheatsheet-fa.md`](cheatsheet-fa.md) | یک صفحه برای روز ضبط |
| [`prep-fa.md`](prep-fa.md) | کلیدها، قیمت‌ها، Stockfish، پایلوت، اجرا، ضبط، ریسک‌ها |
| [`artifact/protocol.md`](artifact/protocol.md) | پروتکل قفل‌شده (اثرانگشت در هر اجرا) |
| [`artifact/chess_live.py`](artifact/chess_live.py) | **صفحهٔ زنده** (SSE): صفحه، فهرست حرکت، نوار ارزیابی، شمارندهٔ غیرقانونی، زمان/توکن/$ هر درخواست، «چیزی که مدل دید»؛ `--mock` · `--live` · `--replay RUN [--speed N]` · `--selftest` |
| [`artifact/chess_run.py`](artifact/chess_run.py) | `plan` (سقف دلار) · `run` (دورهٔ کامل، قابل‌ازسرگیری، `--max-usd` اجباری) · `report` |
| [`artifact/chess_core.py`](artifact/chess_core.py) | دستور ثابت، خواندن جواب، تشخیص هفت نوع خطا، کتاب گشایش، فرمول‌های Lichess، Stockfish اختیاری، بازیکن‌های MOCK |
| [`artifact/chess_report.py`](artifact/chess_report.py) · [`chess_selftest.py`](artifact/chess_selftest.py) · [`chess_page.html`](artifact/chess_page.html) | گزارش و PGN · آزمون بی‌شبکه · قالب صفحه |
| [`artifact/models.json`](artifact/models.json) · [`prices.json`](artifact/prices.json) | پنج slot (خالی تا روز اجرا) · قیمت‌ها (خالی؛ سقف پشتیبان) |
| [`artifact/derived/`](artifact/derived/SOURCE.txt) | کتاب گشایش Lichess (CC0)، معمای Epoch (CC BY 4.0)، چند عدد Kaggle (مجوز نامعلوم، فقط واقعیت با منبع) |
| [`media/CREDITS.md`](media/CREDITS.md) | هیچ تصویر بیرونی؛ فهرست «دانلود نشد» |

پوشه‌ها: `artifact/data/` (git-ignored: اجراها و کش هر بازی) · `artifact/results/<run>/` (پس از `report`: report.md، summary.json، games.pgn، events.jsonl، spoken-fa.txt).

## وارسی‌ها (۲۸ نوامبر ۲۰۲۶)

- `python3 artifact/chess_live.py --selftest` (کلیدها unset) → `selftest ok (Stockfish not installed: engine checks skipped)`، حدود ۳ ثانیه: ۱۲ حالت تشخیص خطا، دوپهلو، کتاب گشایش (Ruy Lopez C60)، win%(۱۰۰) = ۵۹٫۱، دقت ۶۷٫۲، آستانه‌ها، Elo ۰٫۷۶؛ دورهٔ MOCK بیست‌بازی با رنگ‌های متوازن، گزارش/PGN/spoken با برچسب MOCK، ازسرگیری، قانون «دومی باخت»، سقف دلار؛ بازپخش، صفحه، `/state`، SSE.
- `python3 scripts/voice-lint.py …/script-fa.md` → exit 0 (۱٬۴۵۹ واژه، همهٔ قاب‌ها ۱۱۶ تا ۱۴۶ واژه در دقیقه).
- `python3 scripts/build-decks.py --only hmd-s02` → `ok · 15 beats + cover`، بی‌هشدار.
- اسکرین‌شات Chrome بی‌سر ۱۶۰۰×۹۰۰ از صفحهٔ زنده در حالت MOCK (`?game=G03`).
- python-chess 1.11.2 (`pip3 install --user chess`) لازم است؛ Stockfish اختیاری.

## پیش از ضبط باید حل شود

- [ ] کلیدها، پنج مدل (`models.json`)، قیمت‌ها (`prices.json`)، `brew install stockfish` (`prep-fa.md` §۱).
- [ ] پایلوت پولی و بعد اجرای کامل؛ `report`؛ پرکردن [RUN]های متن و دک از `spoken-fa.txt` و `report.md`.
- [ ] `[VERIFY]`: مجوز جدول Kaggle (R01)، متن بلاگ Kaggle دربارهٔ روش امتیاز (R03)، تعداد rethink در Game Arena (R07)، متن مادهٔ ۷٫۵٫۵ FIDE (R17).
- [ ] R01 و R04 روز ضبط دوباره (هفتگی عوض می‌شوند).

## چه چیزهایی سر ضبط بگیری

جدول کامل در `prep-fa.md` §۵: چهره (قاب ۱، ۵، ۹، ۱۳)، صفحهٔ شطرنج واقعی (قاب ۲)، ترمینال `plan` (قاب ۴)، صفحهٔ زنده یا بازپخش برچسب‌دار (قاب ۳، ۷، ۸، ۹، ۱۱).
