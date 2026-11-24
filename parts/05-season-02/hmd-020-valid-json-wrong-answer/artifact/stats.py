"""HMD-020 · small statistics and spoken-Persian number helpers (standard library only)."""

import math
import random

Z = 1.959964


def wilson(k, n):
    """95% Wilson interval for k successes out of n, as (low, high) proportions."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def paired_bootstrap(a, b, reps=4000, seed=20):
    """a, b: lists of 0/1 for the same records. 95% percentile interval of mean(a) - mean(b), resampling records."""
    n = len(a)
    if n == 0:
        return (0.0, 0.0, 0.0)
    rng = random.Random(seed)
    diffs = []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(sum(a[i] - b[i] for i in idx) / n)
    diffs.sort()
    return (sum(x - y for x, y in zip(a, b)) / n, diffs[int(0.025 * reps)], diffs[int(0.975 * reps) - 1])


def mcnemar_exact(a, b):
    """Two-sided exact McNemar (sign test on discordant pairs). Returns (only_a, only_b, p)."""
    only_a = sum(1 for x, y in zip(a, b) if x and not y)
    only_b = sum(1 for x, y in zip(a, b) if y and not x)
    n, k = only_a + only_b, min(only_a, only_b)
    if n == 0:
        return only_a, only_b, 1.0
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n * 2
    return only_a, only_b, min(1.0, p)


# ── spoken Persian (written the way the channel's scripts write numbers) ──────────────────────────
ONES = ['صفر', 'یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه', 'ده', 'یازده', 'دوازده', 'سیزده',
        'چهارده', 'پونزده', 'شونزده', 'هفده', 'هجده', 'نوزده']
TENS = ['', '', 'بیست', 'سی', 'چهل', 'پنجاه', 'شصت', 'هفتاد', 'هشتاد', 'نود']
HUNDREDS = ['', 'صد', 'دویست', 'سیصد', 'چهارصد', 'پونصد', 'ششصد', 'هفتصد', 'هشتصد', 'نهصد']


def words_fa(n):
    """Integer → spoken Persian (بیست‌وچهار, صد و چهل)."""
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


def dec_fa(x, places=1):
    x = round(x, places)
    whole = int(x)
    frac = round((x - whole) * 10 ** places)
    return words_fa(whole) + (f' ممیز {words_fa(frac)}' if frac else '')


def pct_words(k, n):
    """«بیست‌وچهار درصد» from k of n, rounded to a whole percent."""
    return words_fa(round(100 * k / n)) + ' درصد' if n else 'نامعلوم'


FA_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def fa(x):
    return str(x).translate(FA_DIGITS).replace('.', '٫')
