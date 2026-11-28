# HMD-S03 · منابع

> همهٔ منابع ۲۸ نوامبر ۲۰۲۶ (۷ آذر ۱۴۰۵) باز و خوانده شدند، مگر جایی که نوشته شده. نقل‌قول‌ها کوتاه‌اند و فقط برای گزارش و نقد.
> برچسب‌ها: ✅ از متن منبع خوانده شد · 🔁 از متن یک منبع اصلیِ دیگر یا از یک وارسی واسطه نقل شده · 🟡 دانستهٔ استاندارد، این بار باز نشد · ⚠️ اختلاف یا ابهام.
> عددهایی که «حساب ما» نوشته شده‌اند از `artifact/fold_live.py` می‌آیند و `--selftest` همه را از دادهٔ ذخیره‌شده دوباره می‌سازد (`artifact/derived/SOURCE.txt`).

## AlphaFold، CASP، نوبل

| شناسه | منبع | چه چیزی از آن آمده | وضعیت |
|---|---|---|---|
| R01 | Jumper et al., «Highly accurate protein structure prediction with AlphaFold», *Nature* 596, 583–589 (2021), DOI 10.1038/s41586-021-03819-2 (متن کامل از Europe PMC، PMC8371605) | CASP14: میانهٔ دقت ستون اصلی «0.96 Å r.m.s.d.95» در برابر 2.8 Å روش بعدی (متن مقاله، نه چکیده)؛ اجزا: MSA، بازنمایی جفت‌ها، Evoformer، ماژول ساختار، بازچرخش (recycling)؛ pLDDT = «predicted local-distance difference test»؛ آموزش: «structures from the PDB with a maximum release date of 30 April 2018»؛ جست‌وجوی الگو (template) در PDB70 | ✅ |
| R02 | Nobel Prize in Chemistry 2024, press release, 9 Oct 2024 — https://www.nobelprize.org/prizes/chemistry/2024/press-release/ | نیمی به دیوید بیکر «for computational protein design»؛ نیم دیگر مشترک به دمیس هسابیس و جان جامپر «for protein structure prediction» | ✅ (وارسی واسطه، متن صفحه) |
| R03 | Google DeepMind blog, «AlphaFold: a solution to a 50-year-old grand challenge in biology», 30 Nov 2020 — https://deepmind.google/discover/blog/alphafold-a-solution-to-a-50-year-old-grand-challenge-in-biology/ | «median score of 92.4 GDT overall across all targets» در CASP14؛ پارادوکس لوینتال (شمار شکل‌های ممکن نجومی است، پروتئین‌ها در میلی‌ثانیه تا ثانیه تا می‌خورند) | ✅ (وارسی واسطه) |
| R04 | Protein Structure Prediction Center — https://predictioncenter.org | CASP از ۱۹۹۴، هر دو سال، پیش‌بینی کور؛ بنیان‌گذاران John Moult و Krzysztof Fidelis؛ CASP14 در ۲۰۲۰ | ✅ (وارسی واسطه) |
| R05 | AlphaFold Protein Structure Database — https://alphafold.ebi.ac.uk (صفحهٔ اصلی و FAQ؛ FAQ با جاوااسکریپت بار می‌شود و از بستهٔ سایت خوانده شد) | «over 260 million protein structure predictions»؛ مجوز «CC-BY 4.0»؛ pLDDT «per-residue estimate of its confidence on a scale from 0 - 100»؛ نوارهای رنگ: بالای ۹۰ خیلی بالا، ۷۰ تا ۹۰ بالا، ۵۰ تا ۷۰ کم، زیر ۵۰ خیلی کم و «reasonably strong predictor of disorder»؛ PAE: «expected position error at residue x if the predicted and true structures were aligned on residue y» | ✅ (وارسی واسطه) ⚠️ صفحه یک خط قدیمی «over 200 million» هم دارد؛ عدد ۲۶۰ میلیون را روز ضبط دوباره ببین |
| R06 | Abramson et al., «Accurate structure prediction of biomolecular interactions with AlphaFold 3», *Nature* 630, 493–500 (2024) | Pairformer به‌جای Evoformer؛ «diffusion module» که مختصات اتم‌ها را مستقیم می‌سازد؛ MSA کم‌رنگ‌تر؛ لیگاند، اسید نوکلئیک، یون و باقیمانده‌های تغییریافته | ✅ (وارسی واسطه) |
| R06b | github.com/google-deepmind/alphafold3 (README، LICENSE، WEIGHTS_TERMS_OF_USE، تاریخچهٔ commit) | کد: نوامبر ۲۰۲۴ با CC BY-NC-SA 4.0؛ ۹ ژوئن ۲۰۲۶ به Apache 2.0؛ وزن‌ها با شرایط جداگانه و فقط غیرتجاری (از ژوئیهٔ ۲۰۲۶ لینک مستقیم به‌جای فرم)؛ AlphaFold Server برای استفادهٔ غیرتجاری | ✅ (وارسی واسطه) ⚠️ کارت ایده «Apache-2.0 و وزن با درخواست» نوشته بود؛ امروز این درست است: کد Apache، وزن غیرتجاری |
| R07 | Litvin, Lytras, Jack, Robertson, Hughes, Grove, «Viro3D: a comprehensive database of virus protein structure predictions», *Mol Syst Biol* 21, 1599–1617 (2025), DOI 10.1038/s44320-025-00147-9؛ خبر CVR گلاسگو ۲۵ فوریهٔ ۲۰۲۶ | «AlphaFold2-ColabFold and ESMFold»؛ بیش از ۸۵ هزار پروتئین از بیش از ۴۴۰۰ ویروس؛ پوشش ساختاری ویروس‌ها «30-fold» بیشتر از ساختارهای تجربی؛ ورود به AlphaFold DB؛ سربرگ فایل مدل NP: «UNDER CC-BY 4.0 LICENCE» | ✅ (چکیده با وارسی واسطه؛ سربرگ فایل را خودمان خواندیم) |
| R08 | Nobel Prize in Chemistry 1972, Christian Anfinsen — https://www.nobelprize.org/prizes/chemistry/1972/summary/ | «the connection between the amino acid sequence and the biologically active conformation» | ✅ (وارسی واسطه) |
| R26 | Isomorphic Labs, news (۲۹ سپتامبر، ۱۷ و ۱۹ نوامبر ۲۰۲۶) — https://www.isomorphiclabs.com | هیچ اعلام رسمی آغاز کارآزمایی انسانی پیدا نشد؛ هیچ داروی تأییدشده‌ای که کشفش به AlphaFold نسبت داده شود پیدا نشد | ✅ (وارسی واسطه؛ «پیدا نشد» یعنی تا ۲۸ نوامبر ۲۰۲۶) |

## داده‌ای که دمو می‌خواند

| شناسه | منبع | چه چیزی | وضعیت |
|---|---|---|---|
| R09 | AlphaFold DB API — `https://alphafold.ebi.ac.uk/api/prediction/P08148` و `…/P89522` (+ فایل‌های مدل، pLDDT و PAE) | **GP63:** AF-P08148-F1، نسخهٔ ۶، «AlphaFold Monomer v2.0 pipeline»، ساخت ۱ اوت ۲۰۲۵، میانگین pLDDT ۸۷٫۱۲، ۷۶٫۶٪ خیلی بالا، ۱۲٫۵٪ خیلی کم. **NP:** AF-0000000365761428، نسخهٔ ۱، «ColabFold v1.5.2»، ارائه‌دهنده Viro3D، ساخت ۳ ژوئیهٔ ۲۰۲۵، میانگین ۸۹٫۸۸ | ✅ با کد خودمان |
| R10 | UniProt — https://rest.uniprot.org/uniprotkb/P08148.json و P89522.json (نسخهٔ ۱۴۳ و ۷۷، ۴ نوامبر ۲۰۲۶)؛ مجوز https://www.uniprot.org/help/license | GP63: ۶۰۲ اسیدآمینه؛ سیگنال ۱–۳۹، پپتید فعال‌ساز ۴۰–۱۰۰، زنجیرهٔ بالغ ۱۰۱–۵۷۷ با لنگر GPI روی ۵۷۷، پپتید ۵۷۸–۶۰۲ «Removed in mature form»؛ محل فعال ۲۶۵، روی ۲۶۴/۲۶۸/۳۳۴. NP: ۴۸۲ اسیدآمینه، سویهٔ «Nigeria/IbAr10200/1970»، موتیف DEVD ۲۶۶–۲۶۹ (برش کاسپاز ۳). مجوز CC BY 4.0 | ✅ |
| R11 | PDB 1LML — https://www.rcsb.org/structure/1LML؛ Schlagenhauf, Etges, Metcalf, *Structure* 6, 1035–1046 (1998), DOI 10.1016/S0969-2126(98)00104-X | پراش پرتو ایکس، ۱٫۸۶ Å، انتشار ۱۷ سپتامبر ۱۹۹۷؛ پروتئین «purified from promastigote membranes»؛ «three domains, two of which have novel folds»؛ خانوادهٔ متزینسین | ✅ |
| R12 | PDB 4AQF و 4AQG؛ Wang et al., *J Virol* 86, 12294–12303 (2012) | 4AQG تک‌مولکول، ۲٫۸ Å؛ 4AQF الیگومر، ۳٫۱ Å؛ هر دو سویهٔ IbAr10200، انتشار ۲۶ سپتامبر ۲۰۱۲؛ الیگومرشدن جای برش کاسپاز را می‌پوشاند | ✅ |
| R13 | Carter et al., *J Virol* 86, 10914–10923 (2012), PDB 4AKL (سویهٔ Baghdad-12) | «a large globular domain» و «a protruding arm domain» با جای برش DEVD؛ مقایسهٔ ساختارها: بازو با چرخش «180 degrees» و جابه‌جایی «40 Å» | ✅ (وارسی واسطه) |
| R14 | Guo et al., *PNAS* 109, 5046–5051 (2012), PDB 3U3I | «racket-shaped… 'head' and 'stalk' domains»؛ ادعای فعالیت اندونوکلئازی که فقط همین مقاله گزارش کرده | ✅ (وارسی واسطه) ⚠️ سویهٔ 3U3I: PDB می‌گوید IbAr10200، خود نویسندگان بعدها YL04057؛ در دمو استفاده نشد |
| R15 | PDB 9WA3/9WA4 (انتشار ۱۸ نوامبر ۲۰۲۶)؛ Song et al., *PNAS* 2026, DOI 10.1073/pnas.2624265123 | میکروسکوپ الکترونی سرمایی RNP اصیل ویروس؛ 9WA4 «2xNP local reconstruction»، ۳٫۵۵ Å، سویهٔ IbAr10200 | ✅ |
| R16 | PDB 9ZMQ/9ZMR/9ZMS (انتشار ۳۰ سپتامبر ۲۰۲۶)؛ *Nat Commun* 2026, DOI 10.1038/s41467-026-76702-1 | ساختار NP با یک **پادتن** محافظ غیرخنثی‌کننده (9D5)، نه دارو | ✅ (وارسی واسطه) ⚠️ نام نویسندهٔ اول را تأیید نکردیم؛ فقط «Nat Commun 2026» بگو |
| R25 | wwPDB usage policies — https://www.wwpdb.org/about/usage-policies | «available under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication» | ✅ |
| — | حساب ما (`artifact/fold_live.py`) | GP63 در برابر 1LML: ۴۶۵ Cα (باقیماندهٔ ۱۰۰ تا ۵۷۴)، RMSD ۰٫۲۷ Å، TM ۰٫۹۹۹؛ میانگین pLDDT زنجیرهٔ بالغ ۹۵٫۸؛ نوارهای زیر ۵۰: ۱–۴۴، ۹۱–۹۶، ۵۷۸–۶۰۲. NP: بازو ۱۸۱–۲۹۹ از روی PAE، pLDDT بازو ۸۰٫۹، PAE سر↔سر ۳٫۹، بازو↔بازو ۶٫۵، بازو↔سر ۱۸٫۶ Å؛ در برابر 4AQG: کل ۹٫۷۲، فقط سر ۱٫۰۷، بازو ۱۷۸°؛ 4AQF: ۲٫۸۹ / ۱٫۰۱ / ۲۶°؛ 9WA4: ۵٫۳۸ / ۲٫۰۰ / ۴۶°؛ 4AQG در برابر 4AQF (دو آزمایش): سر ۰٫۷۶، کل ۹٫۲۲، بازو ۱۴۳°؛ فاصلهٔ میانگین دو Cα پشت سر هم ۳٫۸۴ Å | ✅ selftest |

## دو بیماری

| شناسه | منبع | چه چیزی | وضعیت |
|---|---|---|---|
| R17 | WHO, Leishmaniasis fact sheet, 12 Jan 2023 — https://www.who.int/news-room/fact-sheets/detail/leishmaniasis | «600 000 to 1 million new cases» سالک در سال (برآورد)؛ نیش پشه‌خاکی ماده؛ زخم پوست و جای زخم مادام‌العمر؛ «a treatable and curable disease»؛ فهرست کشوری ندارد | ✅ (وارسی واسطه) |
| R18 | WHO Global Health Observatory, `NTD_LEISHCNUM`, Iran — https://ghoapi.azureedge.net/api/NTD_LEISHCNUM?$filter=SpatialDim%20eq%20%27IRN%27 | موارد گزارش‌شدهٔ سالک در ایران: ۲۰۲۱: ۱۴٬۰۲۰ · ۲۰۲۲: ۹٬۹۷۷ · ۲۰۲۳: ۴٬۶۵۹ · ۲۰۲۴: ۵٬۴۴۱ · **۲۰۲۵: ۶٬۴۵۳** (به‌روزرسانی ۱۰ نوامبر ۲۰۲۶)؛ صفحهٔ موضوعی GHO: در ۲۰۲۵ شش کشور، از جمله ایران، بیش از ۵۰۰۰ مورد گزارش کردند | ✅ (API را خودمان خواندیم) |
| R19 | WHO, *Weekly Epidemiological Record* No. 45, 7 Nov 2025 (دادهٔ ۲۰۲۴) | ۲۱۱٬۴۶۶ مورد تازهٔ گزارش‌شدهٔ سالک در جهان؛ ایران جزو ۱۲ کشور با بیش از ۲۰۰۰ مورد | ✅ (وارسی واسطه) |
| R20 | «Cutaneous leishmaniasis in Iran: a review of epidemiological aspects…», *Parasite* 29 (2022), DOI 10.1051/parasite/2022047 | سالک روستایی (L. major) با مخزن جوندگان مثل Rhombomys opimus و پشه‌خاکی P. papatasi؛ سالک شهری (L. tropica) در مشهد، کرمان، یزد…؛ ناقل شهری P. sergenti | ✅ (وارسی واسطه) |
| R20b | EMHJ 21(10), 2015 (تحلیل ۱۹۸۳–۲۰۱۲) | میانگین سالانه ۱۸٬۸۸۴ مورد در آن دوره؛ L. major در ۱۷ استان از ۳۱ | ✅ (وارسی واسطه؛ فقط در study) |
| R21 | Yao, Donelson, Wilson, *Infect Immun* 78 (2010), PMID 19858295 | GP63 «the most abundant glycoprotein» غشای پروماستیگوت؛ نقش در فرار از کمپلمان | ✅ (وارسی واسطه) |
| R22 | WHO, Crimean–Congo haemorrhagic fever fact sheet, 20 Feb 2025 — https://www.who.int/news-room/fact-sheets/detail/crimean-congo-haemorrhagic-fever | «a case fatality rate of 10–40%»؛ کنهٔ Hyalomma؛ تماس با خون و بافت دام آلوده هنگام و بلافاصله بعد از ذبح؛ انسان به انسان و بیمارستانی؛ «There is no vaccine available»؛ ریباویرین با «considerable uncertainties» | ✅ (وارسی واسطه) |
| R23 | Nasirian et al., «Six-year trend of CCHF cases in Islamic Republic of Iran», *EMHJ* 32(7), 446–453 (2026), DOI 10.26719/2026.32.7.446 | سیستان و بلوچستان ۲۰۱۸–۲۰۲۴: ۴۳۳ مورد ثبت‌شده، مرگ ۱۱٫۰٪ (۴۷ از ۴۳۳)؛ بیشترین موارد کشور در همین استان | ✅ (وارسی واسطه) |
| R24 | Chinikar et al., *Transbound Emerg Dis* (2008), DOI 10.1111/j.1865-1682.2008.01028.x | نظام مراقبت CCHF ایران «established in 1999» | ✅ (وارسی واسطه) |

## چیزهایی که بیرون ماندند

| ادعا | چرا بیرون ماند |
|---|---|
| «سالک سالی ۱۵ تا ۲۰ هزار مورد در ایران» | قدیمی است (میانگین ۱۹۸۳–۲۰۱۲، R20b). عدد تازه: ۶٬۴۵۳ مورد گزارش‌شده در ۲۰۲۵ (R18). |
| «WHO ایران را جزو ده کشور اول سالک می‌شمارد» | برگهٔ WHO فهرست کشوری ندارد؛ به‌جایش GHO ۲۰۲۵ (R18) و WER (R19). |
| «اوج کریمه‌کنگو در ایران حوالی عید قربان» (در کارت ایده) | **هیچ منبع اصلی ایرانی پیدا نشد.** تنها روند شش‌سالهٔ سیستان و بلوچستان اوج زمستانی یافت (R23). فقط می‌گوییم ذبح دام یکی از راه‌های انتقال است (R22). |
| گلستان به‌عنوان کانون سالک | فقط منبع درجه‌دو؛ گلستان کانون کریمه‌کنگوست. |
| «GP63 برای ساختار 1LML قند‌زدایی شد» | در مقاله نیست (R11). |
| «بیش از ۵۰۰ هزار نسخه GP63 روی هر سلول» | فقط منبع درجه‌دو؛ می‌گوییم «فراوان‌ترین گلیکوپروتئین سطح» (R21). |
| جمع کشوری موارد کریمه‌کنگو (۱۵۰۰ یا ۱۸۷۲ مورد از ۲۰۰۰) | فقط از خبر و مرور درجه‌دو؛ با هم نمی‌خوانند. |
| «۲۱۴ میلیون ساختار» | قدیمی؛ امروز صفحه «بیش از ۲۶۰ میلیون» می‌گوید (R05). |
| «AI داروی سالک/کریمه‌کنگو را پیدا کرد» | هیچ منبعی؛ و پادتن 9D5 (R16) دارو نیست و به AlphaFold هم ربطی ندارد. |
| «پروتئین NP فعالیت اندونوکلئازی دارد» | فقط یک مقاله (R14)؛ مقاله‌های دیگر ندیدند. وارد نمی‌شویم. |
| ISM8969 «داروی Isomorphic» | غلط رایج وبلاگ‌ها؛ مال Insilico است. وارد نمی‌شویم. |
| تصویر بیماران سالک یا کریمه‌کنگو | حساس و بی‌اجازه؛ استفاده نمی‌شود (`media/CREDITS.md`). |
