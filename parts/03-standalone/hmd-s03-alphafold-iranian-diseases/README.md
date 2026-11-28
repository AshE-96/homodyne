# HMD-S03 · Silent Breakthrough · AlphaFold پروتئین سالک و تب کریمه‌کنگو را درست دید؟

*Did AlphaFold get the proteins of salak and Crimean–Congo fever right?*

**قالب:** Silent Breakthrough · **فصل ۱، پس از HMD-006 و پیش از HMD-007** · **هوک:** Curiosity-Gap
**وضعیت:** آمادهٔ تمرین (۲۸ نوامبر ۲۰۲۶ / ۷ آذر ۱۴۰۵). همهٔ عددها همان روز از منبع یا از خروجی دمو بازبینی شدند. `--selftest` سبز. هیچ API پولی، کلید یا [RUN] ندارد.
**زمان برآوردی:** حدود ۱۲:۰۵ · **واژهٔ گفتاری:** ۱٬۴۷۹ · **قاب:** ۱۵ · **قاب‌های دک:** ۱۵ + کاور
**سؤال قسمت:** AlphaFold پروتئین سالک و تب کریمه‌کنگو را درست دید؟

**جملهٔ مرکزی:** پیش‌بینی AlphaFold برای GP63 انگل سالک با ساختار بلوری 1LML فقط ۰٫۲۷ آنگستروم (۴۶۵ کربن آلفا) فاصله دارد، و تکه‌های «نارنجی»اش همان پپتیدهایی‌اند که سلول جدا می‌کند. برای نوکلئوپروتئین ویروس کریمه‌کنگو (مدل Viro3D/ColabFold)، سر با هر سه ساختار تجربی ۱ تا ۲ آنگستروم می‌خواند، ولی جای «بازو» فرق می‌کند (۲۶ تا ۱۷۸ درجه)؛ PAE دقیقاً همین را پرچم زده بود (بازو↔سر ۱۸٫۶ Å در برابر سر↔سر ۳٫۹ Å)، و دو آزمایش یک آزمایشگاه هم بازو را ۱۴۳ درجه متفاوت دارند.

**مرز ادعا:** آزمون کور نیست (ساختارها پیش از پایان دادهٔ آموزش AF2، ۳۰ آوریل ۲۰۱۸، در PDB بودند)؛ مدل ایستاست؛ RMSD فقط روی کربن آلفاست؛ ساختار، دارو یا درمان نیست؛ **این قسمت توصیهٔ پزشکی نیست.**

## فایل‌ها

| فایل | چیست |
|---|---|
| [`script-fa.md`](script-fa.md) | متن ضبط v6، ۱۵ قاب |
| [`hooks-fa.md`](hooks-fa.md) | پنج هوک؛ Curiosity-Gap انتخاب شده (Story-Open به دستور ترتیب فصل کنار رفت) |
| [`package-fa.md`](package-fa.md) | عنوان، تامبنیل، توضیحات، Chapters، دو Short، پست Community |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ دک → `deck-fa.html` و `deck-en.html` (`python3 scripts/build-decks.py --only hmd-s03`) |
| [`sources.md`](sources.md) | منابع R01–R26، وضعیت بازبینی، و فهرست «بیرون ماند» |
| [`study-fa.md`](study-fa.md) | **سند مطالعه برای محمد**: پروتئین، CASP، سازوکار AlphaFold، pLDDT/PAE، RMSD/TM، دو بیماری، بگو/نگو، ۱۲ پرسش |
| [`cheatsheet-fa.md`](cheatsheet-fa.md) | یک صفحه برای روز ضبط |
| [`prep-fa.md`](prep-fa.md) | داده، تمرین، URL هر قاب، چک‌لیست روز ضبط، ریسک‌ها |
| [`artifact/fold_live.py`](artifact/fold_live.py) | دموی زنده: ساخت صفحه، `--fetch` (بی‌کلید)، `--serve` (+ بررسی زندهٔ AFDB با کلید L)، `--selftest` (بی‌شبکه) |
| [`artifact/fold_core.py`](artifact/fold_core.py) | ریاضی، فقط stdlib: خواندن PDB/mmCIF، هم‌ترازی توالی، Kabsch (کواترنیون هورن)، RMSD، TM-score، نوارهای pLDDT |
| [`artifact/fold_data.py`](artifact/fold_data.py) | دانلود از AlphaFold DB، RCSB PDB و UniProt، و ساخت دادهٔ مشتق |
| `artifact/fold_page.html` → `artifact/fold_live.html` | قالب صفحه و صفحهٔ ساخته‌شده (نمای سه‌بعدی با canvas خودمان، PAE، نوار pLDDT، جدول مقایسه) |
| [`artifact/derived/`](artifact/derived/SOURCE.txt) | `fold-data.json` (۲۳۲ KB) با `SOURCE.txt` (مجوز، sha256، نتیجه‌ها) |
| `artifact/data/` | دادهٔ خام (git-ignored؛ با `--fetch` ساخته می‌شود) |
| [`media/CREDITS.md`](media/CREDITS.md) | هیچ تصویر بیرونی؛ فهرست «استفاده نمی‌شود» |

## وارسی‌ها (۲۸ نوامبر ۲۰۲۶)

- `python3 -I artifact/fold_live.py --selftest` (کلیدها unset، بی‌شبکه) → `selftest ok`: Kabsch چرخش معلوم را تا 1e-14 بازمی‌یابد؛ دترمینان +۱؛ نویز ۱ Å ← RMSD ≈ √۳؛ آینه روی اصل نمی‌نشیند؛ میانگین pLDDT و کسر نوارها با API AFDB می‌خواند؛ هر RMSD ذخیره‌شده از مختصات دوباره ساخته می‌شود؛ Kabsch با SVD در numpy 1.26.4 تا 1e-6 یکی است؛ نارنجی‌های GP63 بیرون زنجیرهٔ بالغ‌اند؛ PAE بازو↔سر بیش از ۱۰ Å و بیش از دو برابر بازو↔بازو.
- `python3 scripts/voice-lint.py …/script-fa.md` → exit 0 (۱٬۴۷۹ واژه؛ همهٔ قاب‌ها ۱۱۲ تا ۱۴۷ واژه در دقیقه).
- `python3 scripts/build-decks.py --only hmd-s03` → `ok · 15 beats + cover`، بدون هشدار.
- اسکرین‌شات Chrome بی‌سر (۱۶۰۰×۹۰۰) از ۱۴ قاب دک fa، دو قاب en، و دو حالت دمو (GP63؛ NP با fit روی سر و رنگ فاصله).
- `--serve` + `/api/live?acc=P89522` → پاسخ زندهٔ AFDB، «same: true».

## پیش از ضبط باید حل شود

- [x] **عنوان:** «AlphaFold پروتئین سالک و تب کریمه‌کنگو را درست دید؟» انتخاب شد (README، `package-fa.md` §۱، کاور fa/en دک). عنوان قبلی manifest «AlphaFold و دو بیماری ایرانی: سالک و تب کریمه‌کنگو» بود.
- [ ] روز ضبط: کلید L روی هر دو پروتئین؛ صفحهٔ AFDB هنوز «over 260 million»؟ (`prep-fa.md` §۶)
- [x] تاریخ‌های نسبی مطلق شدند (پخش حدود اواخر ژانویهٔ ۲۰۲۷): قاب ۲ «سال ۲۰۲۵»، قاب ۳ «حدود ۱۹۶۰»، قاب ۱۱ «نوامبر ۲۰۲۶».

## یادداشت‌ها

- **مدل NP را DeepMind نساخته:** ColabFold v1.5.2 از پروژهٔ Viro3D (گلاسگو)، میزبانی‌شده در AlphaFold DB. در متن، دک و توضیحات گفته شده.
- **سرور فایل‌های AFDB** به `curl` با User-Agent پیش‌فرض 403 می‌دهد؛ Python urllib با User-Agent توصیفی کار می‌کند (هیچ ورود یا محافظتی دور زده نمی‌شود).
- **[RUN] اختیاری کنار گذاشته شد:** پرسیدن از پنج مدل زبانی (`tools/llm.py`) به داستان کمکی نمی‌کرد؛ ساخته نشد.
