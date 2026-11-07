# HMD-012 · Benchmark E06 · v5

## هزار بار امتحان کردیم؛ حالا می‌شود اعتماد کرد؟

**وضعیت:** آمادهٔ تمرین و ضبط. همهٔ عددهای شبیه‌سازی از اجرای واقعی `artifact/power_lab.py` (seed 12، ۷ نوامبر ۲۰۲۶)؛ منبع‌ها ۷ نوامبر ۲۰۲۶ از متن PDF بازبینی شدند. هیچ مدلی صدا زده نشده و Bluff اجرا نشده است.
**قالب:** Benchmark Lab · **زنجیره:** HMD-011 (پیش‌بینی هوا) ← **HMD-012** → HMD-013 (ردِ AI در متن)
**زمان:** حدود ۱۴ دقیقه · واژهٔ گفتاری: 1622 · ۱۵ قاب · هوک: Curiosity-Gap «دو جدول»

**جملهٔ مرکزی:** هزار ردیف همیشه هزار شاهد نیست؛ اعتماد به «A بهتر از B است» به سه چیز بستگی دارد: چند سؤالِ واقعاً مستقل داری، دو مدل را سؤال‌به‌سؤال مقایسه کرده‌ای یا نه، و پیش از اجرا نوشته‌ای آزمونت چه فرقی را می‌تواند ببیند.

**مرز ادعا:** عددهای شبیه‌سازی ILLUSTRATIVE‌اند (نرخ اختلاف ۱۰٪ و ICC ۰٫۵ فرضی) و هیچ مدلی صدا زده نشده؛ نمی‌گوییم کدام مدل یا بنچمارک واقعی کم‌توان است؛ Bluff اجرا نشده؛ «معنادار» یعنی احتمالاً واقعی، نه لزوماً مهم.

**چه چیزی نسبت به v4 عوض شد:** از ۱۰ قاب و حدود ۶۲۰ واژه به ۱۵ قاب و 1622 واژه؛ هوک Curiosity-Gap «دو جدول»؛ منبع اصلی R07 روی صفحه با نقل و عددهای واقعی (۹۶۹، ۳٫۰۵)؛ عدد Card (۲۵٪) و بازسازی‌اش با کد؛ artifact تازهٔ `power_lab.py` (توان، MDE، جفتی، خوشه، مقایسه‌های چندگانه)؛ کارت اجرای منصفانه و پیش‌ثبت. نسخهٔ v4: `../_archive/v4-november-2026/e06-how-many-questions-and-a-fair-run/`.

## فایل‌ها

| فایل | محتوا |
|---|---|
| [script-fa.md](script-fa.md) | متن ضبط v5 (۱۵ قاب، MID-CTA در ۲۶٪، RE-HOOK در ۶۱٪) |
| [hooks-fa.md](hooks-fa.md) | پنج هوک + توصیه (برنده: Curiosity-Gap) |
| [package-fa.md](package-fa.md) | بستهٔ انتشار کامل + metadata انگلیسی |
| [`deck-fa.html`](deck-fa.html) | دک ضبط v6، فارسی و راست‌به‌چپ: کاور + ۱۵ قاب (→ ← · F · H · N) |
| [`deck-en.html`](deck-en.html) | همان دک به انگلیسی، با همان قاب‌ها و همان ترتیب |
| [`deck.src.html`](deck.src.html) | منبع دوزبانهٔ هر دو دک؛ بعد از ویرایش `make decks` |
| [sources.md](sources.md) | منابع R07، R09–R13، محاسبه‌ها، پارامترهای شبیه‌سازی |
| [artifact/power_lab.py](artifact/power_lab.py) | توان و MDE مقایسهٔ جفتی؛ McNemar دقیق؛ تکرار؛ خوشه‌ها و اثر طرح؛ ۱۵ جفت (stdlib، seeded) |
| [artifact/power_lab-output.txt](artifact/power_lab-output.txt) | خروجی اجرای seed 12 (منبع همهٔ عددهای ILLUSTRATIVE متن و دک) |
| [artifact/selftest-output.txt](artifact/selftest-output.txt) | خروجی `--selftest` (۱۶/۱۶) |
| [artifact/fair-run-card.md](artifact/fair-run-card.md) | کارت اجرای منصفانه + برگهٔ پیش‌ثبت (ابزار بیننده) |
| [artifact/handoff-v3.md](artifact/handoff-v3.md) | پیوند به پیش‌نیازهای اجرای Bluff (از نسخهٔ قبل، دست‌نخورده) |

## اجرا (از ریشهٔ مخزن)

```bash
python3 parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/power_lab.py             # seed 12 (عددهای متن، حدود ۵ ثانیه)
python3 parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/power_lab.py --seed 11   # پایداری
python3 parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/power_lab.py --icc 0.2   # همبستگی درون‌گروهی دیگر
python3 parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/power_lab.py --selftest
python3 tools/bluff_lab.py plan --sd 1 --n 450 --delta 0.10                                            # قاب ۱۱
python3 tools/bluff_lab.py plan --sd 2 --n 450 --delta 0.10
python3 scripts/check-season-01.py                                                                     # HMD-012 ok
```

## باید پیش از ضبط حل شود

| برچسب | مورد | کجا | اقدام |
|---|---|---|---|
| ✔ | عددهای Card (پیوست C) و Miller (§5، جدول ۴) | قاب ۳، ۶، ۷، ۹ | از متن PDF در ۷ نوامبر ۲۰۲۶ خوانده و با artifact بازسازی شدند. |
| ✔ | اجرای artifact و ذخیرهٔ خروجی | قاب ۳، ۵–۷، ۱۰، ۱۲؛ دک | seed 12 و seed 11 اجرا شد؛ `power_lab-output.txt`. |
| باز | خوانش آزمایشی با زمان‌سنج | `data-start` دک، فصل‌های package | زمان‌ها برآورد ۱۲۵ واژه در دقیقه‌اند؛ بعد از خوانش بازتنظیم شوند. |
| باز | تیزر HMD-013 | قاب ۱۵ | فقط سؤال است، بدون عدد؛ اگر عنوان یا زاویهٔ HMD-013 عوض شد، جملهٔ دانشجو را تطبیق بده. |
| باز | پل از HMD-011 | قاب ۲ | پوشهٔ HMD-011 هنوز در مخزن نیست؛ جمله فقط به عنوان و تیزر «۷۰٪ احتمال باران» تکیه دارد. اگر HMD-011 زاویهٔ دیگری گرفت، یک جمله را عوض کن. |
| باز | پیوندهای `artifact/handoff-v3.md` | artifact | به `examples/bluff-v1/production-v3/` اشاره می‌کنند که پس از جداشدن مخزن هومودین اینجا نیست؛ در متن و دک استفاده نشده‌اند. |
