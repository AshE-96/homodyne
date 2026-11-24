"""HMD-024 · numbers as spoken Persian (the way the channel writes them on the teleprompter)."""

ONES = ['صفر', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه', 'ده', 'یازده', 'دوازده', 'سیزده',
        'چهارده', 'پونزده', 'شونزده', 'هفده', 'هجده', 'نوزده']
TENS = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود']
HUNDREDS = ['', 'صد', 'دویست', 'سیصد', 'چهارصد', 'پونصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد']
FA_DIGITS = str.maketrans('0123456789.', '۰۱۲۳۴۵۶۷۸۹٫')


def words_fa(n):
    """Integer → spoken Persian: 24 → بیست‌وچهار, 140 → صد و چهل, 1500 → هزار و پونصد."""
    n = int(round(n))
    if n < 0:
        return 'منفی ' + words_fa(-n)
    if n < 20:
        return ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        return TENS[t] + ('‌و' + ONES[o] if o else '')
    if n < 1000:
        h, r = divmod(n, 100)
        return HUNDREDS[h] + (' و ' + words_fa(r) if r else '')
    for size, name in ((10 ** 9, 'میلیارد'), (10 ** 6, 'میلیون'), (1000, 'هزار')):
        if n >= size:
            h, r = divmod(n, size)
            return (words_fa(h) + ' ' if h > 1 or size > 1000 else '') + name + (' و ' + words_fa(r) if r else '')
    return str(n)


def dec_fa(x):
    """One decimal, spoken: 1.2 → یک و دو دهم · 0.8 → هشت دهم · 12.5 → دوازده و نیم · 3.0 → سه."""
    x = round(float(x), 1)
    whole, tenth = int(x), int(round((x - int(x)) * 10))
    if tenth == 10:
        whole, tenth = whole + 1, 0
    if tenth == 0:
        return words_fa(whole)
    frac = 'نیم' if tenth == 5 else f'{ONES[tenth]} دهم'
    return frac if whole == 0 and tenth != 5 else (f'{words_fa(whole)} و {frac}' if whole else 'نیم')


def smart_fa(x):
    """Whole numbers for 10 and up, one decimal below 10."""
    return words_fa(x) if x is not None and x >= 10 else dec_fa(x or 0)


def pct_fa(part, whole):
    return words_fa(round(100 * part / whole)) + ' درصد' if whole else '⟨درصد⟩'


def fa_num(s):
    return str(s).translate(FA_DIGITS)
