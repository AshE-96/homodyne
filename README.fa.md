<div dir="rtl">

# هومودین · Homodyne

**یک سؤال آشنا دربارهٔ AI و علم، با یک آزمایش دیدنی.**
کانال یوتیوب فارسی با زیرنویس انگلیسی، وبلاگ دوزبانه در **[homodyne.m2gh.ir](https://homodyne.m2gh.ir)**، و متن، منبع و فایل قابل‌اجرای هر قسمت در همین مخزن.

[English](README.md)

## چهار قول در هر قسمت

1. **سؤال در عنوان** و جواب صریح در پایان.
2. **منبع اصلی** روی صفحه، با نام و تاریخ.
3. **یک artifact** که خودت اجرا کنی یا بخوانی (`artifact/`).
4. **مرز ادعا:** نتیجه چه چیزی را نشان **نمی‌دهد**.

هر عدد یا از منبعی با نام می‌آید یا از اجرایی در همین مخزن. دادهٔ شبیه‌سازی‌شده برچسب ILLUSTRATIVE دارد. آزمایشی که هنوز اجرا نشده، همین نام را می‌گیرد.

## فصل ۱

| HMD | سؤال | پوشه |
|---|---|---|
| 002 | چطور با همان جواب‌ها، برندهٔ AI عوض می‌شود؟ | [`e01`](parts/02-benchmarking/e01-is-a-higher-score-better/) |
| 003 | می‌شود آتش جنگل را وقتی هنوز کوچک است پیدا کرد؟ | [`hmd-003`](parts/03-standalone/hmd-003-wildfire-from-space/) |
| 004 | مدل اول جدول، برای تو هم بهترین است؟ | [`e02`](parts/02-benchmarking/e02-which-benchmark-answers-your-question/) |
| 005 | چرا نوشتن فارسی برای بعضی AIها توکن بیشتری می‌برد؟ | [`hmd-005`](parts/03-standalone/hmd-005-persian-tokens/) |
| 006 | وقتی می‌گویند AI کمتر خطا می‌کند، چه چیزی را نمی‌گویند؟ | [`e03`](parts/02-benchmarking/e03-what-exactly-are-we-measuring/) |
| 007 | می‌شود با یک متن، دستیار AI را از کارش منحرف کرد؟ | [`hmd-007`](parts/03-standalone/hmd-007-prompt-injection/) |
| 008 | اگر جواب‌نامه غلط باشد، کدام AI می‌بازد؟ | [`e04`](parts/02-benchmarking/e04-who-decides-the-right-answer/) |
| 009 | گوگل‌مپس از کجا می‌فهمد کی می‌رسی؟ | [`hmd-009`](parts/03-standalone/hmd-009-maps-eta/) |
| 010 | نمرهٔ منفی می‌تواند AI را محتاط‌تر کند؟ | [`e05`](parts/02-benchmarking/e05-how-do-you-penalise-a-bluff/) |
| G01 | وقتی AI از نوشته‌های AI یاد بگیرد چه می‌شود؟ | [`hmd-g01`](parts/04-global/hmd-g01-model-collapse/) |
| 012 | هزار بار امتحان کردیم؛ حالا می‌شود اعتماد کرد؟ | [`e06`](parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/) |
| 014 | این جدول درست است؛ چرا گمراه‌کننده است؟ | [`e07`](parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/) |
| 016 | کدام AI به‌موقع می‌گوید «نمی‌دانم»؟ | [`e08`](parts/02-benchmarking/e08-which-model-knows-when-to-abstain/) |
| 018 | این نمرهٔ AI از کجا آمده؟ خودت بررسی کن | [`e09`](parts/02-benchmarking/e09-how-do-you-publish-a-refutable-result/) |
| B07 | AI از یک عکس می‌فهمد کجایی؟ | [`hmd-b07`](parts/04-global/hmd-b07-photo-geolocation/) |

نقشهٔ کامل با وضعیت: [`channel/README.md`](channel/README.md) و [`channel/season-01/README-fa.md`](channel/season-01/README-fa.md).

## اجرا

```bash
make episodes
```

```bash
make teleprompter
```

```bash
make site
```

- `make episodes` همهٔ بسته‌ها را بررسی می‌کند.
- `make teleprompter` تله‌پرامپتر و برگهٔ ضبط هر قسمت را در `parts/…/recording/` می‌سازد.
- `make site` وبسایت را در `site/dist` می‌سازد.

## اصلاح

عدد یا ادعای اشتباهی دیدی؟ یک [issue اصلاح](../../issues/new?template=correction.yml) با منبع باز کن.

## مجوز

محتوا CC BY-NC-SA 4.0 و کد MIT. جزئیات در [`LICENSE.md`](LICENSE.md).

</div>
