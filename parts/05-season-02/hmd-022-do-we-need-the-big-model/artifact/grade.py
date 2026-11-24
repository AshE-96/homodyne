"""HMD-022 · graders. Truth only: exact or normalised match. No model judges the main metric.

A reply is JSON {"answer": "...", "confidence": 0-100}. The answer is correct when
- number: it contains exactly one distinct number (after Persian digits, separators and words such as
  «میلیون» / "million" are normalised) and that number equals the truth (absolute tolerance 0.005);
- text: one accepted alias appears as whole words, after case, Arabic/Persian letter and punctuation folding;
- yes/no: it says yes or no in Persian or English, and not both.
Anything else, including an empty or unparseable reply, is wrong. A hedge that lists two numbers is wrong.
"""
import json
import re

DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
LETTERS = str.maketrans({'ي': 'ی', 'ى': 'ی', 'ك': 'ک', 'ة': 'ه', 'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ۀ': 'ه', '‌': ' ',
                         'á': 'a', 'í': 'i', 'é': 'e'})
SCALE = {'هزار': 1e3, 'thousand': 1e3, 'میلیون': 1e6, 'million': 1e6, 'میلیارد': 1e9, 'billion': 1e9}
YES = {'yes', 'بله', 'بلی', 'آره', 'اره', 'مجاز', 'مجاز است', 'allowed', 'true'}
NO = {'no', 'خیر', 'نه', 'not', 'غیرمجاز', 'ممنوع', 'مجاز نیست', 'نباید', 'false', 'not allowed'}


def fold(text):
    t = str(text).translate(DIGITS).translate(LETTERS).lower()
    t = re.sub(r'[ً-ْٰ]', '', t)                      # Arabic diacritics
    return t


def numbers(text):
    """Every number in the text as a float, with Persian/English separators and scale words applied."""
    t = fold(text).replace('٫', '.').replace('٬', ',')
    t = re.sub(r'(?<=\d),(?=\d{3}\b)', '', t)                      # 1,250,000 -> 1250000
    t = re.sub(r'(?<=\d)\s(?=\d{3}\b)', '', t)                     # 1 250 000 -> 1250000
    out = []
    for m in re.finditer(r'(-?\d+(?:\.\d+)?)\s*(هزار|thousand|میلیون|million|میلیارد|billion)?', t):
        v = float(m.group(1)) * SCALE.get(m.group(2) or '', 1)
        out.append(v)
    return out


def words(text):
    return re.findall(r'[a-z0-9]+|[؀-ۿ]+', fold(text))


def has_phrase(text, phrase):
    w, p = words(text), words(phrase)
    return bool(p) and any(w[i:i + len(p)] == p for i in range(len(w) - len(p) + 1))


def parse_confidence(raw):
    """Self-reported confidence -> (value on a 0-100 scale or None, flag).

    The prompt asks for an integer 0-100. Replies drift, so each other form is converted and flagged:
    'ok' 0-100 number · 'percent_string' "85%" · 'unit_scale' a fraction such as 0.85 (x 100) ·
    'out_of_range' below 0 or above 100 (dropped) · 'missing' no field · 'unparsed' anything else (dropped).
    A float of exactly 0.0 or 1.0 is read as a fraction; an integer 0 or 1 as a percentage.
    """
    if raw is None or raw == '':
        return None, 'missing'
    flag = 'ok'
    if isinstance(raw, str):
        t = raw.strip().translate(DIGITS).replace('٪', '%').replace('٫', '.')
        if t.endswith('%'):
            t, flag = t[:-1].strip(), 'percent_string'
        try:
            v = float(t)
        except ValueError:
            return None, 'unparsed'
        is_fraction = flag == 'ok' and '.' in t and 0 <= v <= 1
    elif isinstance(raw, bool):
        return None, 'unparsed'
    elif isinstance(raw, (int, float)):
        v = float(raw)
        is_fraction = isinstance(raw, float) and 0 <= v <= 1
    else:
        return None, 'unparsed'
    if is_fraction:
        v, flag = v * 100, 'unit_scale'
    if not 0 <= v <= 100:
        return None, 'out_of_range'
    return v, flag


def parse_reply(text):
    """Pull {"answer", "confidence"} out of a reply; tolerate code fences and words around the JSON."""
    m = re.search(r'\{.*\}', text or '', re.S)
    if m:
        try:
            d = json.loads(m.group(0))
            conf, flag = parse_confidence(d.get('confidence'))
            return {'answer': str(d.get('answer', '')).strip(), 'confidence': conf, 'conf_flag': flag, 'ok': True}
        except json.JSONDecodeError:
            pass
    return {'answer': (text or '').strip(), 'confidence': None, 'conf_flag': 'no_json', 'ok': False}


def correct(truth, answer):
    if not str(answer).strip():
        return False
    kind = truth['type']
    if kind == 'number':
        vals = sorted({round(v, 6) for v in numbers(answer)})
        return len(vals) == 1 and abs(vals[0] - truth['value']) <= 0.005
    if kind == 'text':
        return any(has_phrase(answer, a) for a in truth['aliases'])
    if kind == 'yesno':
        t = ' '.join(words(answer))
        said_yes = any(has_phrase(t, y) for y in YES) and not any(has_phrase(t, n) for n in ('not allowed', 'مجاز نیست'))
        said_no = any(has_phrase(t, n) for n in NO)
        if said_yes == said_no:
            return False
        return said_yes == truth['value']
    raise ValueError(kind)


def same_answer(a, b):
    """Do two replies give the same final answer? Used by the self-consistency cascade."""
    na, nb = sorted({round(v, 6) for v in numbers(a)}), sorted({round(v, 6) for v in numbers(b)})
    if na or nb:
        return na == nb
    return ' '.join(words(a)) == ' '.join(words(b))


def selfcheck():
    num = lambda v: {'type': 'number', 'value': v}
    cases = [
        (num(79000000), '۷۹٬۰۰۰٬۰۰۰', True), (num(79000000), '79 million rials', True), (num(79000000), '۷۹ میلیون', True),
        (num(8.25), '۸٫۲۵ میلی‌لیتر', True), (num(8.25), '8.25 or 8.5', False), (num(600), '720 mg, capped at 600', False),
        (num(3), '30', False), (num(1260000), '1,260,000 toman', True), (num(25.25), '$25.25', True), (num(-40), '-40 °F', True),
        ({'type': 'text', 'aliases': ['کانبرا', 'canberra']}, 'Canberra', True),
        ({'type': 'text', 'aliases': ['کانبرا', 'canberra']}, 'سیدنی', False),
        ({'type': 'text', 'aliases': ['مشتری', 'jupiter']}, 'سیارهٔ مشتری', True),
        ({'type': 'text', 'aliases': ['k']}, 'K', True), ({'type': 'text', 'aliases': ['k']}, 'Kr', False),
        ({'type': 'yesno', 'value': False}, 'خیر', True), ({'type': 'yesno', 'value': False}, 'بله', False),
        ({'type': 'yesno', 'value': True}, 'yes', True), ({'type': 'yesno', 'value': False}, 'No, not allowed', True),
        (num(5), '', False),
    ]
    out = [(t, a, want, correct(t, a)) for t, a, want in cases]
    for raw, want in ((85, (85.0, 'ok')), ('85%', (85.0, 'percent_string')), (0.85, (85.0, 'unit_scale')),
                      ('0.9', (90.0, 'unit_scale')), (1, (1.0, 'ok')), (1.0, (100.0, 'unit_scale')), (140, (None, 'out_of_range')),
                      ('high', (None, 'unparsed')), (None, (None, 'missing')), ('۷۰٪', (70.0, 'percent_string'))):
        out.append(('confidence', raw, want, parse_confidence(raw)))
    return out
