"""HMD-024 · graders. Each returns {'pass': bool, 'score': 0..1, 'why': str, ...}.

Plain rules, stated in the episode:
  points  (summaries)    exactly N bullet lines AND every required key point present (word groups, normalised)
  fields  (extraction)   a JSON object; every field equal to the key after normalising digits, separators, dates
  short   (QA)           exactly one candidate answer, and it is the accepted one (a hedge like «۷ یا ۸» fails);
                         answering NOT_IN_TEXT is a fail
  absent  (QA, no answer) the reply says NOT_IN_TEXT; any other answer counts as an invented answer
  terms   (translation)  AUTO CHECK ONLY: required numbers/names survive. The main grade is the owner's blind sheet.
  label   (classify)     exactly one allowed label, and it is the right one
  final   (no-go)        the 'ANSWER:' line (or the last line) commits to exactly one candidate, the key
"""
import json
import re

from task_bank import NOT_IN_TEXT

DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')


def norm(text):
    """Persian/Arabic digits → ASCII, Arabic ي/ك → Persian, ZWNJ → space, separators out, lower case."""
    t = str(text).translate(DIGITS)
    t = t.replace('ي', 'ی').replace('ك', 'ک').replace('ـ', '').replace('‌', ' ').replace('‏', '')
    t = re.sub(r'(?<=\d)[٬,](?=\d{3})', '', t)
    t = re.sub(r'(?<=\d)٫(?=\d)', '.', t)
    t = t.lower()
    t = re.sub(r'[«»"“”\'`*_#()\[\]{}،؛:!?؟.,;]+(?!\d)', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def has(text, alt):
    """Whole-token containment: '3' is not found inside '30'."""
    a, t = norm(alt), norm(text)
    if not a:
        return False
    return re.search(r'(?<![\w.])' + re.escape(a) + r'(?![\w])', t) is not None


def bullets(text):
    lines = [l.strip() for l in str(text).strip().splitlines() if l.strip()]
    return [l for l in lines if re.match(r'^([-•*–]|\d+[.)]|[۰-۹]+[.)])\s*', l)]


def g_points(t, out):
    b = bullets(out)
    nonb = [l for l in str(out).strip().splitlines() if l.strip() and l.strip() not in b]
    hit = [all(any(has(out, alt) for alt in group) for group in kp) for kp in t['keypoints']]
    fmt = len(b) == t['n'] and not nonb
    ok = fmt and all(hit)
    return {'pass': ok, 'score': sum(hit) / len(hit), 'format_ok': fmt,
            'why': f'{len(b)} bullets (want {t["n"]}), key points {sum(hit)}/{len(hit)}'}


def parse_json(out):
    s = str(out).strip()
    s = re.sub(r'^```(?:json)?\s*|\s*```$', '', s)
    m = re.search(r'\{.*\}', s, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        try:
            return json.loads(m.group(0).translate(DIGITS))
        except json.JSONDecodeError:
            return None


def _num(v):
    s = str(v).translate(DIGITS)
    s = re.sub(r'(?<=\d)[٬,](?=\d{3})', '', s).replace('٫', '.')
    m = re.search(r'-?\d+(?:\.\d+)?', s)
    return float(m.group(0)) if m else None


def _date(v):
    s = str(v).translate(DIGITS)
    m = re.search(r'(\d{4})\D(\d{1,2})\D(\d{1,2})', s)
    return f'{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}' if m else None


def field_ok(kind, want, got):
    if got is None:
        return False
    if kind in ('int', 'num'):
        n = _num(got)
        return n is not None and abs(n - float(want)) < 0.005
    if kind == 'date':
        return _date(got) == _date(want)
    if kind == 'time':
        m = re.search(r'(\d{1,2})[:.](\d{2})', str(got).translate(DIGITS))
        return bool(m) and f'{int(m.group(1)):02d}:{m.group(2)}' == want
    if kind == 'code':
        return re.sub(r'[\s\-]', '', str(got)).upper() == want.upper()
    # str: every token of one accepted spelling appears in the value (honorifics like «آقای»/«Ms» are ignored)
    toks = set(norm(got).split())
    return any(set(norm(a).split()) <= toks for a in want)


def g_fields(t, out):
    d = parse_json(out)
    if not isinstance(d, dict):
        return {'pass': False, 'score': 0.0, 'json_ok': False, 'why': 'no valid JSON object'}
    res = {k: field_ok(kind, want, d.get(k)) for k, (kind, want) in t['fields'].items()}
    n = sum(res.values())
    return {'pass': n == len(res), 'score': n / len(res), 'json_ok': True, 'fields': res,
            'why': f'fields {n}/{len(res)}' + ('' if n == len(res) else ' · wrong: ' + ', '.join(k for k, v in res.items() if not v))}


def says_absent(out):
    o = norm(out)
    return norm(NOT_IN_TEXT) in o or 'not in the text' in o or 'در متن نیست' in o or 'در متن نیامده' in o


HEDGE = re.compile(r'(?:^|\s)(?:or|یا)(?:\s|$)|/', re.I)


def one_answer(text, accept):
    """True only if `text` commits to exactly one candidate and it is an accepted one.
    Numbers and times: every distinct number (or HH:MM) in the text must be the same accepted value, so
    «۷٫۹ یا ۸٫۲» fails. Words: an accepted word must appear and no 'or' / «یا» / '/' hedge."""
    t = norm(text)
    times = [a for a in accept if re.fullmatch(r'\d{1,2}:\d{2}', a)]
    nums = [a for a in accept if re.fullmatch(r'-?\d+(?:\.\d+)?', a)]
    if times:
        found = {f'{int(h):02d}:{m}' for h, m in re.findall(r'(?<!\d)(\d{1,2}):(\d{2})(?!\d)', t)}
        return len(found) == 1 and found <= {f'{int(x.split(":")[0]):02d}:{x.split(":")[1]}' for x in times}
    found = {float(x) for x in re.findall(r'(?<![\d.])-?\d+(?:\.\d+)?(?![\d.])', t)}
    if found:
        return len(found) == 1 and any(abs(next(iter(found)) - float(n)) < 1e-9 for n in nums)
    return any(has(t, a) for a in accept) and not HEDGE.search(t)


def g_short(t, out):
    if says_absent(out):
        return {'pass': False, 'score': 0.0, 'why': 'said NOT_IN_TEXT for an answerable question'}
    ok = one_answer(out, t['accept'])
    return {'pass': ok, 'score': float(ok), 'why': 'one answer, the right one' if ok else 'wrong, missing or hedged answer'}


def g_absent(t, out):
    ok = says_absent(out)
    return {'pass': ok, 'score': float(ok), 'invented': not ok,
            'why': 'said NOT_IN_TEXT' if ok else 'gave an answer that is not in the text'}


def g_terms(t, out):
    hit = [any(has(out, a) for a in group) for group in t['terms']]
    fa_chars = len(re.findall(r'[؀-ۿ]', str(out)))
    lat_chars = len(re.findall(r'[A-Za-z]', str(out)))
    right_script = (fa_chars > lat_chars) if t['direction'] == 'en→fa' else (lat_chars > fa_chars)
    ok = all(hit) and right_script
    return {'pass': ok, 'score': sum(hit) / len(hit), 'auto_only': True,
            'why': f'required terms {sum(hit)}/{len(hit)}' + ('' if right_script else ' · wrong language')}


def g_label(t, out):
    syn = t.get('synonyms', {})
    found = [lab for lab in t['labels'] if has(out, lab) or any(has(out, s) for s in syn.get(lab, []))]
    ok = found == [t['answer']]
    return {'pass': ok, 'score': float(ok), 'why': f'labels found: {found or "none"}'}


def final_line(out):
    s = str(out).translate(DIGITS)
    m = re.findall(r'answer\s*[:：]\s*(.+)', s, re.I)
    if m:
        return m[-1].strip()
    lines = [l for l in s.strip().splitlines() if l.strip()]
    return lines[-1] if lines else ''


def g_final(t, out):
    fl = final_line(out)
    ok = one_answer(fl, t['accept'])
    return {'pass': ok, 'score': float(ok), 'final': fl[:60], 'why': ('final answer ok' if ok else f'final answer: {fl[:40]!r}')}


GRADERS = {'points': g_points, 'fields': g_fields, 'short': g_short, 'absent': g_absent, 'terms': g_terms,
           'label': g_label, 'final': g_final}


def grade(task, output):
    if output is None:
        return {'pass': False, 'score': 0.0, 'why': 'no output'}
    return GRADERS[task['grader']](task, output)
