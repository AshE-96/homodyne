<div dir="rtl">

# منابع · HMD-017 · یوتیوب چرا این ویدیو را به تو پیشنهاد داد؟

تاریخ بازبینی همهٔ لینک‌ها: ۱۳ نوامبر ۲۰۲۶ (۲۲ آبان ۱۴۰۵). شناسه‌های S1 تا S8 مال همین قسمت‌اند و با شناسه‌های Rxx در `private/planning/production-v3/references.json` (R01 تا R39) فرق دارند.

| شناسه | منبع | چه چیزی از آن استفاده شد | کجا |
|---|---|---|---|
| S1 (منبع اصلی) | [How YouTube recommendations work — YouTube Help](https://support.google.com/youtube/answer/16089387?hl=en) | سیگنال‌های اصلی به گفتهٔ خود یوتیوب: تاریخچهٔ تماشا، تاریخچهٔ جست‌وجو، اشتراک کانال، لایک، دیس‌لایک، «Not interested»، «Don't recommend channel» و نظرسنجی رضایت. صفحهٔ اول بیشتر بر پایهٔ تاریخچهٔ تماشا؛ Up next: «the video you're currently watching as the main signal». کنترل‌ها: خاموش/پاک کردن تاریخچه، «Not interested». (در گفتار شش دسته گفته شد؛ «Don't recommend channel» با «علاقه ندارم» یک‌جا آمد.) صفحهٔ هم‌خانواده: [YouTube's recommendation system](https://support.google.com/youtube/answer/16533387?hl=en). نشانی قدیمی howyoutubeworks برای ابزار ما در دسترس نبود. | قاب ۲، ۱۴؛ هوک ۵ |
| S2 | [On YouTube's recommendation system — Cristos Goodrow, YouTube Official Blog, ۱۵ سپتامبر ۲۰۲۱](https://blog.youtube/inside-youtube/on-youtubes-recommendation-system/) | «we learned back in 2011 that clicking on a video doesn't mean you actually watched it» و «we added in watchtime in 2012»؛ «over 80 billion pieces of information we call signals»؛ valued watchtime با نظرسنجی یک تا پنج ستاره؛ «Recommendations drive a significant amount of the overall viewership on YouTube, even more than channel subscriptions or search». | قاب ۲؛ هوک ۵؛ توضیحات |
| S3 | [Deep Neural Networks for YouTube Recommendations — Covington, Adams, Sargin, RecSys '16 (Boston, سپتامبر ۲۰۱۶)](https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/) · [PDF](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/45530.pdf) | متن PDF خوانده شد. دو مرحله: «the enormous YouTube corpus is winnowed down to hundreds of videos»؛ شکل ۲: millions ← hundreds ← dozens. هدف رتبه‌بندی: «generally a simple function of expected watch time per impression»؛ «Ranking by click-through rate often promotes deceptive videos». آفلاین در برابر زنده: «live A/B results are not always correlated with offline experiments». همه دربارهٔ سیستم ۲۰۱۶، نه امروز. | قاب ۳، ۱۱ |
| S4 | [MovieLens ml-latest-small — GroupLens, README و مجوز](https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html) · Harper & Konstan, *The MovieLens Datasets: History and Context*, ACM TiiS 5(4), 2015, [doi:10.1145/2827872](https://doi.org/10.1145/2827872) | ۱۰۰٬۸۳۶ امتیاز، ۶۱۰ کاربر، ۹٬۷۴۲ فیلم؛ ساخته‌شده ۲۶ سپتامبر ۲۰۱۸. مجوز: بازنشر فقط با همان شرایط؛ بدون ادعای تأیید دانشگاه مینه‌سوتا/GroupLens؛ ذکر استفاده در انتشار؛ «may not use this information for any commercial or revenue-bearing purposes without first obtaining permission». ما داده را در مخزن نمی‌گذاریم؛ `fetch_movielens.py` آن را از GroupLens می‌گیرد و SHA-256 را چک می‌کند. | قاب ۳ تا ۱۰؛ artifact |
| S5 | [Liu et al., *Short-term exposure to filter-bubble recommendation systems has limited polarization effects: Naturalistic experiments on YouTube*, PNAS 122(8) e2318127122, ۱۸ فوریهٔ ۲۰۲۵](https://doi.org/10.1073/pnas.2318127122) · [متن کامل PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11874454/) | چهار آزمایش، «nearly 9,000 participants» (N ترکیبی ۸٬۸۸۳)، سایت شبیه یوتیوب با ویدیوها و پیشنهادهای واقعی؛ دستکاری پیشنهادها به سمت حباب یا متعادل؛ اثر محدود بر نظر (دو موضوع سیاسی). محدودیت به گفتهٔ خودشان: «we cannot rule out effects from long-term exposure or to small vulnerable subsets of users». | قاب ۱۲ |
| S6 | [Carbonell & Goldstein, *The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries*, SIGIR 1998, pp. 335–336, doi:10.1145/290941.291025](https://dblp.org/rec/conf/sigir/CarbonellG98.html) | تعریف MMR: ترکیب «مرتبط بودن» با «تکراری نبودن» نسبت به آنچه انتخاب شده. ما به‌جای شباهت متن، هم‌پوشانی ژانر را تکرار حساب کردیم. | قاب ۶؛ artifact |
| S7 | [Järvelin & Kekäläinen, *Cumulated gain-based evaluation of IR techniques*, ACM TOIS 20(4): 422–446, 2002, doi:10.1145/582415.582418](https://doi.org/10.1145/582415.582418) | تعریف DCG/NDCG. ما سود دودویی (امتیاز ۴ یا بیشتر = مرتبط) و تخفیف log2 به کار بردیم. | قاب ۷، ۱۰؛ artifact |
| S8 | [Chaney, Stewart, Engelhardt, *How Algorithmic Confounding in Recommendation Systems Increases Homogeneity and Decreases Utility*, RecSys 2018 (arXiv 1710.11214)](https://arxiv.org/abs/1710.11214) | پیش‌زمینه: حلقهٔ بازخورد در شبیه‌سازی می‌تواند رفتار را هم‌شکل کند. در گفتار نقل نشده؛ فقط برای اینکه بدانیم شبیه‌سازی ما تازه نیست و نتیجه‌اش («دورتر شدند، تنگ‌تر نه») با طراحی ساده‌تر ما گره خورده است. | قاب ۹ (گفتار و دک)، artifact README |

## محاسبه‌شده توسط ما

اجرا: ۱۳ نوامبر ۲۰۲۶، Python 3.9، numpy 1.26.4، از پوشهٔ `artifact/`. خروجی کامل: [`artifact/results/report.txt`](artifact/results/report.txt).

- **داده:** `ml-latest-small.zip`، SHA-256 `696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436` (MD5 با فایل `.md5` خود GroupLens یکی است). کاتالوگ: ۳٬۰۳۷ فیلم با دست‌کم ۵ امتیاز آموزشی و دست‌کم یک ژانر؛ ۱۸ ژانر (IMAX و «بدون ژانر» کنار گذاشته شدند).
- **مدل:** شباهت کسینوسی فیلم‌به‌فیلم روی سیگنال دودویی «امتیاز داده» با shrinkage ۱۰؛ numpy.
- **آزمون آفلاین (دادهٔ واقعی):** ۲۰٪ آخر امتیازهای هر نفر به ترتیب زمان کنار گذاشته شد؛ ۵۸۷ نفر دست‌کم یک فیلم مرتبط (≥ ۴) در بخش کنارگذاشته داشتند.

| سیاست | NDCG@10 | نسبت به شباهت محض (بازهٔ ۹۵٪، بوت‌استرپ جفتی، ۲۰۰۰ بار) | ژانر در فهرست | پوشش کاتالوگ |
|---|---|---|---|---|
| پرطرفدارترین‌های هنوز ندیده | 0.0758 | شباهت محض در برابر این: +14.5% [−1.2%, +33.3%] | 11.81 | 98 فیلم (3.2%) |
| شباهت محض (λ = 1) | 0.0868 | — | 10.91 | 294 (9.7%) |
| λ = 0.9 | 0.0879 | +1.3% [−2.2%, +4.7%] | 12.15 | 298 (9.8%) |
| λ = 0.8 | 0.0851 | −1.9% [−7.2%, +3.4%] | 12.84 | 313 (10.3%) |
| **λ = 0.7** | 0.0840 | **−3.2% [−9.9%, +3.6%]** | **13.40** | **328 (10.8%)** |
| λ = 0.6 | 0.0811 | −6.6% [−13.6%, +0.9%] | 13.70 | 331 (10.9%) |
| λ = 0.5 | 0.0758 | −12.6% [−20.2%, −4.7%] | 14.00 | 339 (11.2%) |

  تنوع درون‌فهرست (میانگین فاصلهٔ ژانر جفت‌ها): ۰٫۷۵۰ ← ۰٫۸۷۸ (λ = 0.7). λ = 0.7 پیش از اولین اجرا در `CONFIG` ثبت شده بود. «پرطرفدارترین‌ها» برای هر نفر فیلم‌های تاریخچه‌اش را کنار می‌گذارد (فهرست ثابت نیست). شباهت محض در برابر پرطرفدارترین‌ها: NDCG مثبت ۱۴٫۵٪، بازهٔ ۹۵٪ [منفی ۱٫۲٪، مثبت ۳۳٫۳٪]؛ صفر داخل بازه (همان بوت‌استرپ جفتی، بعد از مقایسه‌های λ کشیده شده تا بازه‌های آن‌ها عوض نشوند؛ بازبین مستقل با ترتیب دیگری از همان بذر [منفی ۱٫۸٪، مثبت ۳۴٪] گرفت).
- **یک کلیک (دادهٔ واقعی، یک پروفایل ساختگی):** پنج فیلم شروع: Toy Story، Forrest Gump، Jurassic Park، The Matrix، The Shawshank Redemption. افزودن The Shining: ۰ از ۱۰ عوض شد (نزدیک‌ترین فیلم‌هایش پیش از کلیک: Psycho رتبهٔ ۲۲۸، A Clockwork Orange ۹۳، Goodfellas ۶۱). افزودن Sleepless in Seattle: ۴ از ۱۰ (Apollo 13 از رتبهٔ ۱۱، The Lion King ۱۲، Speed ۱۷، Mrs. Doubtfire ۲۵). چرخاندن λ از ۱ به ۰٫۷: ۵ از ۱۰. نزدیک‌ترین فیلم‌های خود Sleepless in Seattle (Pretty Woman رتبهٔ ۶۹، Ghost ۸۰) وارد نشدند. **پراکندگی:** برای ۱۲۳ فیلم با ۷۰ تا ۱۱۶ امتیاز آموزشی (۰٫۸ برابرِ کمتری تا ۱٫۲ برابرِ بیشتریِ دو کلیک)، تعداد فیلم عوض‌شده با یک کلیک: ۰ ← ۱۳ فیلم، ۱ ← ۶۷، ۲ ← ۲۵، ۳ ← ۳، ۴ ← ۹، ۵ ← ۶. یعنی The Shining و Sleepless in Seattle دو سرِ طیف‌اند و متن همین را می‌گوید (بازبین با تعریف دیگری از «هم‌اندازه» روی ۱۹۳ فیلم همین شکل را دید).
- **شبیه‌سازی (ILLUSTRATIVE):** ۲۰۰ جفت اجرا، ۲۰ دور؛ قانون کلیک: جایگاه k با احتمال متناسب با 1/k، با عدد تصادفی مشترک برای هر دو کاربر. فیلم مشترک از ۱۰: شباهت محض ۶٫۰ ← ۲٫۹ (دور ۵) ← ۲٫۰ (دور ۱۰) ← ۰٫۹ (دور ۲۰)؛ λ = 0.7: ۶٫۰ ← ۴٫۳ ← ۳٫۰ ← ۱٫۸. ژانر در فهرست: ۱۲٫۰ ← ۱۲٫۲ (شباهت)، ۱۵٫۰ ← ۱۳٫۴ (λ = 0.7). میانگین تعداد امتیاز آموزشی فیلم‌های فهرست: ۲۰۴ ← ۱۳۴ (شباهت)، ۱۹۵ ← ۱۳۵ (λ = 0.7).
- **ثبت یک تغییر:** در اولین اجرا کلیک A «Silence of the Lambs» بود؛ این فیلم از قبل در فهرست شروع بود، پس یکی از «تغییرها» فقط خروج خود فیلم بود. پیش از نوشتن متن، با The Shining (با تعداد امتیاز نزدیک به Sleepless in Seattle) عوض شد. این تغییر در `CONFIG` توضیح داده شده است.

## آنچه عمداً استفاده نشد

- هیچ ادعایی دربارهٔ وزن واقعی سیگنال‌ها در یوتیوب امروز؛ نه S1 و نه S2 وزن نمی‌دهند.
- «۸۰ میلیارد سیگنال» (S2) در گفتار نیامد؛ بدون تعریف دقیق، عدد بزرگِ بی‌معناست.
- پژوهش‌های «حفرهٔ خرگوش» یوتیوب با ادعای قطعی در هر دو جهت؛ S5 تنها آزمایش تصادفی است که نقل شد، با مرز خودش.
- نتیجه‌ای دربارهٔ تغییر سلیقهٔ آدم واقعی؛ نه داده‌اش را داریم و نه آزمایشش را.

</div>
