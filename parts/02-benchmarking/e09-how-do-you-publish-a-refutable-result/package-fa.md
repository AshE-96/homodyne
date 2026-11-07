# بستهٔ انتشار · HMD-018 · Benchmark E09 (قسمت آخر دورهٔ بنچمارک)

**کلیدواژهٔ اصلی:** نمره هوش مصنوعی · **کلیدواژه‌های دوم:** بازتولید نتایج هوش مصنوعی، بنچمارک AI، SHA-256 چیست، reproducibility، SWE-bench Verified
**منبع ترافیک هدف:** Browse و Suggested (کانال زیر ۱K) · **وعده:** یک نمرهٔ AI را جلوی چشمت از صفر دوباره حساب می‌کنیم، سه بار دستکاری‌اش می‌کنیم و می‌بینیم کدام چک هر تقلب را می‌گیرد؛ با فهرست فایل‌هایی که هر نتیجهٔ قابل‌بررسی لازم دارد. هیچ نتیجهٔ اجرای مدل واقعی وعده داده نمی‌شود.

## ۱. عنوان‌ها

| نوع | عنوان | نویسه |
|---|---|---|
| **اصلی (Hybrid)** | این نمرهٔ AI از کجا آمده؟ خودت بررسی کن | ۳۹ |
| Browse | نمرهٔ دستکاری‌شده از همهٔ چک‌ها رد شد؛ چطور؟ | ۴۴ |
| Search | نتیجهٔ بنچمارک AI را چطور خودت دوباره حساب کنی؟ | ۴۷ |

**توصیه:** عنوان اصلی؛ کلیدواژهٔ «نمرهٔ AI» در نیمهٔ اول، سؤالِ عنوان در قاب ۱۵ با «پس جواب کوتاه» جواب داده می‌شود. عنوان Browse فقط برای آزمایش؛ قولش (تقلب از چک‌های داخلی رد شد) در قاب ۱۰ تحویل می‌شود ولی بدون «لنگر» نیمه‌کاره است، پس در تامبنیل همان عنوان «PASS» را تکرار نکن.

## ۲. تامبنیل

**تقسیم اطلاعات:** عنوان می‌پرسد «از کجا آمده؟» و دستور می‌دهد «خودت بررسی کن»؛ تامبنیل نیمهٔ دیگر را می‌آورد: یک تقلب که از چک رد شد.

**متن (اصلی):** «تقلبی که رد شد» (۳ واژه)

**بریف:**
- **نقطهٔ تمرکز:** یک سطر بزرگ از فایل CSV در سمت چپ (۵۵٪ کادر): `q06 · A · wrong` که `wrong` خط خورده و بالایش با دست نوشته شده `correct`؛ روی آن مهر بزرگ `PASS` به رنگ کهربایی `#E8A33D` (تنها رنگ تأکید)، کمی کج. زمینه `#111214`.
- **چهره:** محمد سمت راست، نیم‌رخ سه‌چهارم، یک ابرو بالا، نگاه به مهر؛ حالت «این نباید رد می‌شد»؛ نه تعجب اغراقی.
- **متن:** فارسی بولد روشن `#F3F1EC`، بالا راست، یک خط، با سایهٔ نرم؛ در ۱۶۸×۹۴ خوانا. هیچ متن دیگری جز `PASS`.
- **عمق:** سطر CSV با فوکوس تیز، پس‌زمینه با نویز ترمینال محو.
- **موبایل:** در اندازهٔ کوچک فقط سه چیز دیده می‌شود: مهر PASS، کلمهٔ خط‌خورده، صورت. اعداد هش حذف.
- **ممنوع:** لوگوی OpenAI، NeurIPS یا هر مدل واقعی؛ قفل و هکر کلاه‌دار کلیشه‌ای؛ عدد بی‌برچسب.

**نسخهٔ B (فقط متن):** «خودت دوباره حساب کن» — فرضیه: دعوت مستقیم به عمل برای بینندهٔ کنجکاو CTR بهتری دارد.
**نسخهٔ C (فقط تصویر):** به‌جای سطر CSV، اسکرین‌شات فورواردشدهٔ `#1` (ساختگی) با یک ذره‌بین که زیرش چهار آیکن فایل پیدا می‌شود؛ همان متن اصلی — فرضیه: صحنهٔ آشنای فوروارد از سطر کد برای بینندهٔ عام قابل‌فهم‌تر است.
**پروتکل:** «Test & compare» یوتیوب؛ ۷ روز؛ معیار سهم زمان تماشا + CTR؛ هر بار یک متغیر.

## ۳. توضیحات (copy-paste)

```
این نمرهٔ AI از کجا آمده؟ یک نمرهٔ بنچمارک هوش مصنوعی را از صفر دوباره حساب می‌کنیم، سه بار دستکاری‌اش می‌کنیم و می‌بینیم کدام چک تقلب را می‌گیرد.

قسمت آخر دورهٔ بنچمارک هومودین:
• فرق «محاسبهٔ دوباره» (recompute) با «اجرای دوباره» (rerun)
• چهار فایلی که هر نمرهٔ قابل‌بررسی لازم دارد: جواب‌های برچسب‌خورده، روش، کد، دفتر اصلاحیه
• اثرانگشت دیجیتال (SHA-256)، مانیفست، و «لنگری» که بیرون از بسته منتشر می‌شود
• چرا یک تقلب تمیز از همهٔ چک‌های داخلی رد می‌شود، و اصلاح صادقانه با تقلب چه فرقی دارد
• نمونهٔ واقعی: کنار گذاشتن SWE-bench Verified در فوریهٔ ۲۰۲۶

مرز ادعا: بررسی‌پذیری فقط درستیِ حساب را نشان می‌دهد، نه درستی برچسب‌ها و نه اینکه اجرای دوبارهٔ مدل همان جواب‌ها را بدهد. فایل دمو آموزشی است (ILLUSTRATIVE): ۱۰ سؤال، دو مدل خیالی؛ هیچ مدلی فراخوانی نشده.

منابع:
- NeurIPS 2026 Paper Checklist: https://neurips.cc/public/guides/PaperChecklist
- MLRC 2026 (NeurIPS blog): https://blog.neurips.cc/2026/05/04/mlrc-2026-reproducibility-as-an-official-track-at-neurips/
- HELM, Liang et al.: https://arxiv.org/abs/2211.09110
- Model Cards, Mitchell et al.: https://arxiv.org/abs/1810.03993
- Datasheets for Datasets, Gebru et al.: https://arxiv.org/abs/1803.09010
- OpenAI, Why we no longer evaluate SWE-bench Verified: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- OpenAI, Separating signal from noise in coding evaluations: https://openai.com/index/separating-signal-from-noise-coding-evaluations/
- COPE retraction guidelines: https://publicationethics.org/guidance/guideline/retraction-guidelines

فایل همراه (recompute_check.py): پس از انتشار مخزن، لینک اینجا قرار می‌گیرد.
لنگر بستهٔ این قسمت (SHA-256 مانیفست): [روز انتشار از خروجی واقعی اضافه شود]

فصل‌ها:
[از بخش ۴ همین فایل، پس از تدوین نهایی]

دورهٔ بنچمارک هومودین:
E01 چطور با همان جواب‌ها، برندهٔ AI عوض می‌شود؟
E02 مدل اول جدول، برای تو هم بهترین است؟
E03 وقتی می‌گویند AI کمتر خطا می‌کند، چه چیزی را نمی‌گویند؟
E04 اگر جواب‌نامه غلط باشد، کدام AI می‌بازد؟
E05 نمرهٔ منفی می‌تواند AI را محتاط‌تر کند؟
E06 هزار بار امتحان کردیم؛ حالا می‌شود اعتماد کرد؟
E07 این جدول درست است؛ چرا گمراه‌کننده است؟
E08 کدام AI به‌موقع می‌گوید «نمی‌دانم»؟ نتیجهٔ آزمون ما
E09 این نمرهٔ AI از کجا آمده؟ خودت بررسی کن (همین قسمت)

#هوش_مصنوعی #بنچمارک #هومودین
```

## ۴. Chapters (پس از تدوین نهایی تنظیم شود)

```
00:00 «خودشون گفتن»
00:46 از یوتیوب تا نمره
01:39 چک‌لیست NeurIPS
02:29 دوباره حساب کردن یا دوباره اجرا کردن؟
03:28 چهار فایلی که لازم است
04:24 اثرانگشت فایل (SHA-256)
05:21 چیزی که نمی‌شود منتشر کرد
06:08 دمو: بستهٔ سالم
07:09 دمو: دو دستکاری
08:09 تقلبی که PASS گرفت
09:00 لنگر بیرون از بسته
09:42 همان ویرایش، این بار علنی
10:46 SWE-bench Verified
11:38 مرز ادعا
12:19 جواب و کل دوره
13:35 قسمت بعد
```

۱۶ فصل، اولی 00:00، کوتاه‌ترین حدود ۳۲ ثانیه (بالای حداقل ۱۰ ثانیهٔ یوتیوب). اگر در تدوین قاب ۱۱ کوتاه‌تر از ۲۰ ثانیه شد، «لنگر» را با «تقلبی که PASS گرفت» یکی کن.

## ۵. تگ‌ها و هشتگ‌ها

**تگ‌ها:** نمره هوش مصنوعی, بنچمارک هوش مصنوعی, بازتولید نتایج هوش مصنوعی, AI benchmark reproducibility, recompute vs rerun, SHA-256 چیست, هش فایل, SWE-bench Verified, NeurIPS checklist, ارزیابی مدل زبانی, هوش مصنوعی, هومودین, Homodyne

**هشتگ‌ها:** #هوش_مصنوعی #بنچمارک #هومودین

## ۶. کامنت پین‌شده

```
منبع اصلی: NeurIPS 2026 Paper Checklist — https://neurips.cc/public/guides/PaperChecklist
فایل recompute_check.py و لنگر بستهٔ این قسمت پس از انتشار مخزن همین‌جا می‌آید؛ همهٔ عددهای دمو ILLUSTRATIVE‌اند.

سؤال: آخرین باری که یک «مدل X اول شد» را باور یا فوروارد کردی، اگر می‌خواستی چکش کنی، اولین فایلی که سراغش می‌رفتی چه بود؟ و پیدا شد؟
```

## ۷. End screen و کارت‌ها

- **End screen (از 13:35، حدود ۳۲ ثانیهٔ آخر):** چپ: HMD-019 «مقاله را به AI دادیم؛ می‌تواند آزمایشش را تکرار کند؟» (طبق زنجیرهٔ فصل). راست: پلی‌لیست «دورهٔ بنچمارک هومودین» (برای بیننده‌ای که از قسمت آخر وارد شده). دکمهٔ Subscribe وسط.
- **کارت ۱ (حدود 02:29، ۱۸٪، recompute ≠ rerun):** HMD-010 / E05 «نمرهٔ منفی می‌تواند AI را محتاط‌تر کند؟» — متن: «نمره‌دادن دوباره ≠ رفتار تازه».
- **کارت ۲ (حدود 09:42، ۶۹٪، اصلاح یک برچسب برنده را عوض کرد):** HMD-008 / E04 «اگر جواب‌نامه غلط باشد، کدام AI می‌بازد؟» — متن: «یک برچسب، یک برندهٔ دیگر».
- **گفتار هم‌زمان end screen:** تیزر قاب ۱۶ («مقاله رو به AI دادیم…»)؛ «ممنون که دیدید» ممنوع.

## ۸. دو Short

### Short 1 · «تقلب PASS گرفت» (۵۵ ثانیه) · منبع: 07:09–09:42

- **هوک ۲ ثانیه:** گفتار «من نمره رو دستکاری کردم، و چک‌کنندهٔ خودم گفت PASS.» · متن روی صفحه: `I TAMPERED. IT SAID PASS.`
- **متن کامل:**
  من نمره رو دستکاری کردم، و چک‌کنندهٔ خودم گفت PASS. [ردیف PASS کهربایی]
  یه فایل جواب داریم، ده سؤال، دو مدل. یه «غلط» رو کردم «درست». برنامه گرفتش: اثرانگشت فایل عوض شده بود. [FAIL]
  دفعهٔ بعد فهرست اثرانگشت‌ها رو هم از نو ساختم. باز گرفت: نمرهٔ منتشرشده با محاسبهٔ دوباره نمی‌خوند. [FAIL]
  دفعهٔ سوم همه‌چیز رو بازنویسی کردم: جواب، نمره، فهرست. PASS. [مکث]
  تنها چیزی که لوم داد؟ یه اثرانگشت که روز اول بیرون از بسته منتشر شده بود. [لنگر → FAIL]
  کامل توضیحش تو ویدیوی بلند.
- **CTA:** «ویدیوی کامل: این نمرهٔ AI از کجا آمده؟»
- **مرز ادعا روی صفحه از ثانیهٔ ۱:** `ILLUSTRATIVE · teaching file · 10 questions · 2 made-up models`
- **عنوان Short:** `I tampered with an AI score` · **هشتگ:** #هوش_مصنوعی #بنچمارک #هومودین
- **حلقه:** آخرین فریم همان ردیف PASS اول است.

### Short 2 · «فاکتور رستوران» (۴۵ ثانیه) · منبع: 02:29–03:28

- **هوک ۲ ثانیه:** گفتار «دوباره حساب کردن فاکتور، با دوباره سفارش دادن غذا فرق داره.» · متن روی صفحه: `RECOMPUTE ≠ RERUN`
- **متن کامل:**
  دوباره حساب کردن فاکتور، با دوباره سفارش دادن غذا فرق داره. [فاکتور + ماشین‌حساب]
  جمع فاکتور رو هر چند بار حساب کنی، باید همون عدد دربیاد. اگه نیومد، یکی اشتباه کرده.
  ولی همون غذا فردا ممکنه یه مزهٔ دیگه بده. آشپز عوض شده. [بشقاب]
  با نمرهٔ AI هم همینه. جواب‌های قبلی رو دوباره نمره بدی، باید عیناً همون عدد بشه. سؤال‌ها رو دوباره از مدل بپرسی، ممکنه جواب‌ها عوض بشن؛ و این لزوماً تقلب نیست.
  پس اول بپرس: کدوم یکی رو چک می‌کنی؟
- **CTA:** «چهار فایلی که برای چک‌کردن لازمه، تو ویدیوی کامل.»
- **مرز ادعا روی صفحه:** `recompute checks the arithmetic, not the labels`

## ۹. پست Community

**پیش از انتشار (نظرسنجی):**
```
حدس بزن: یک غریبه برای اینکه نمرهٔ یک AI را بدون اعتماد به سازنده‌اش دوباره حساب کند، حداقل چند فایل لازم دارد؟
○ ۱
○ ۲ تا ۳
○ ۴ تا ۵
○ بیشتر از ۱۰
جواب، و فایلی که بدونش بقیه تقریباً بی‌فایده‌اند، در قسمت آخر دورهٔ بنچمارک.
```

**پس از انتشار:**
```
جواب: چهار فایل (جواب‌های برچسب‌خورده، روش، کد، دفتر اصلاحیه) + یک مانیفست اثرانگشت. ولی در ویدیو دیدیم یک تقلب تمیز از همهٔ این‌ها رد می‌شود، مگر اینکه «لنگرِ» مانیفست بیرون از بسته و با تاریخ منتشر شده باشد.
[لینک پس از انتشار]
```

## ۱۰. زمان انتشار و پلی‌لیست

- **زمان پیشنهادی:** پنجشنبه، ساعت ۱۹ تا ۲۰ به وقت تهران (مثل بقیهٔ دوره). فرضیه است؛ با دادهٔ Studio بازبینی شود.
- **پلی‌لیست:** «دورهٔ بنچمارک هومودین» (E09، آخر) + «هومودین فصل ۱». بعد از انتشار، توضیحات پلی‌لیست دوره را با یک خط «دوره کامل شد» به‌روز کن.
- Short 1 روز انتشار + ۱؛ Short 2 روز انتشار + ۳.

## ۱۱. پیش از انتشار (چک‌لیست SEO)

- [ ] «نمرهٔ AI» در نیمهٔ اول عنوان و در ۲۵ واژهٔ اول توضیحات.
- [ ] توضیحات زیر ۵۰۰۰ نویسه؛ هشتگ‌ها در توضیحات، نه عنوان.
- [ ] فصل‌ها از 00:00، هر کدام دست‌کم ۱۰ ثانیه، با زمان‌های تدوین نهایی.
- [ ] تگ‌ها زیر ۵۰۰ نویسه.
- [ ] تامبنیل سفارشی؛ زیرنویس فارسی بازبینی شده؛ «Not made for kids»؛ دسته‌بندی Science & Technology؛ زبان فارسی.
- [ ] لنگر واقعی بسته و لینک مخزن جایگزین جای‌نگهدارها شد (URL ساختگی ممنوع).

---

## English metadata

**Primary keyword:** AI benchmark score · **Secondary:** reproducibility, recompute vs rerun, SHA-256 manifest, SWE-bench Verified

| Type | Title | Chars |
|---|---|---|
| **Main (Hybrid)** | Where did this AI score come from? Check it yourself | 52 |
| Browse | I tampered with an AI score and my checker said PASS | 52 |
| Search | How to recompute an AI benchmark score yourself | 47 |

**Description (EN):**
```
Where did this AI score come from? We recompute an AI benchmark score from scratch, tamper with it three times, and see which check catches each tamper.

Final episode of the Homodyne benchmark course (Persian narration, English on-screen text):
• Recompute (same answers + same code = same number) vs rerun (ask the model again; answers may change)
• The four files a reader needs: labelled answers, method, scoring code, correction log
• SHA-256 fingerprints, a manifest, and an anchor published outside the bundle
• Why a clean forgery passes every internal check, and how an honest correction differs
• Real example: OpenAI stopped reporting SWE-bench Verified (Feb 2026)

Claim boundary: being checkable shows the arithmetic is right, not that the labels are right or that a rerun gives the same answers. The demo bundle is ILLUSTRATIVE: 10 questions, two made-up models, no model was called.

Sources:
- NeurIPS 2026 Paper Checklist: https://neurips.cc/public/guides/PaperChecklist
- MLRC 2026: https://blog.neurips.cc/2026/05/04/mlrc-2026-reproducibility-as-an-official-track-at-neurips/
- HELM: https://arxiv.org/abs/2211.09110
- OpenAI on SWE-bench Verified: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- COPE retraction guidelines: https://publicationethics.org/guidance/guideline/retraction-guidelines

Companion script (recompute_check.py): link added when the repository is published.

#AI #benchmark #Homodyne
```

**Tags (EN):** AI benchmark score, AI benchmark reproducibility, recompute vs rerun, reproducible machine learning, SHA-256 manifest, SWE-bench Verified, NeurIPS paper checklist, ML Reproducibility Challenge, HELM, model evaluation, correction log, Homodyne

**Chapters (EN):**
```
00:00 "They said so"
00:46 From YouTube to the score
01:39 The NeurIPS checklist
02:29 Recompute vs rerun
03:28 The four files
04:24 File fingerprints (SHA-256)
05:21 What you can't publish
06:08 Demo: a clean bundle
07:09 Demo: two tampers
08:09 The forgery that passed
09:00 An anchor outside the bundle
09:42 The same edit, in public
10:46 SWE-bench Verified
11:38 Claim boundary
12:19 The answer, and the whole course
13:35 Next episode
```

**Pinned comment (EN):**
```
Main source: NeurIPS 2026 Paper Checklist. All demo numbers are ILLUSTRATIVE. Question: the last time you shared a "model X is #1" claim, what is the first file you would have needed to check it, and could you find it?
```

**Shorts titles (EN):** `I tampered with an AI score` · `Recompute is not rerun`
