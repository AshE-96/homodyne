"""
HMD-020 · DEMO EXTRACTOR. Not a language model, not an AI result.

A deliberately simple, deterministic regex program, written to put real replies under the three lights on screen
without spending anything. It always prints tidy JSON (json.dumps cannot produce a broken bracket), which is the
point of the demo: a perfect form says nothing about the values inside it.

Its shortcuts are the usual ones in quick extraction code, listed so nobody mistakes them for findings:
    - digits: Persian and Arabic digits are converted; "." and "/" are read as a decimal point
    - quantity: the first number followed by a unit word (so «هندونهٔ ۳ تا ۵ کیلویی» gives 3 pieces)
    - amount: the number right before «تومان/تومن/ریال», times «میلیون/هزار» if written; ریال is NOT divided by 10;
      amounts written only in words are not read
    - date: «فردا» anywhere means tomorrow (so «پس‌فردا» also becomes tomorrow); a Jalali day and month are copied
      into the YYYY-MM-DD slots as they are (1406-01-25); weekdays and «... دیگه» are not read
"""

import datetime as dt
import json
import re

import world

DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
UNIT_WORDS = {'کیلو': 'kg', 'گرم': 'g', 'تا': 'piece', 'دونه': 'piece', 'لیتر': 'liter', 'بسته': 'pack',
              'شونه': 'pack'}
NUM_WORDS = {'یه': 1, 'یک': 1, 'دو': 2, 'سه': 3, 'نیم': 0.5}
MONTHS = {m: i + 1 for i, m in enumerate(world.JALALI_MONTHS)}


def _num(s):
    s = s.replace('٬', '').replace(',', '').replace('/', '.')
    if s.count('.') > 1:
        s = s.replace('.', '', s.count('.') - 1)
    return float(s)


def extract(message, today=world.TODAY):
    t = message.translate(DIGITS)
    product = None
    aliases = sorted(((a, p) for p, v in world.CATALOG.items() for a in v[1]), key=lambda x: -len(x[0]))
    for alias, p in aliases:
        if alias in t:
            product = p
            break
    quantity = unit = None
    m = re.search(r'([\d./]+|یه|یک|دو|سه|نیم)\s*(کیلو|گرم|تا|دونه|لیتر|بسته|شونه)', t)
    if m:
        quantity = NUM_WORDS.get(m.group(1)) or _num(m.group(1))
        unit = UNIT_WORDS[m.group(2)]
    paid = None
    m = re.search(r'([\d٬,./]+)\s*(میلیون|هزار)?\s*(تومان|تومن|ریال)', t)
    if m:
        paid = _num(m.group(1)) * {'میلیون': 1_000_000, 'هزار': 1000, None: 1}[m.group(2)]
        paid = int(round(paid))
    date = None
    if 'فردا' in t:
        date = (today + dt.timedelta(days=1)).isoformat()
    elif 'امروز' in t:
        date = today.isoformat()
    else:
        m = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', t) or None
        if m:
            date = f'{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
        else:
            m = re.search(r'(\d{1,2})\s+(' + '|'.join(MONTHS) + ')', t)
            if m:
                date = f'1406-{MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}'
    rec = {'product': product, 'quantity': quantity, 'unit': unit, 'paid_toman': paid, 'delivery_date': date}
    return json.dumps(rec, ensure_ascii=False)
