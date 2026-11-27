"""HMD-K01 · shared core: paths, question schema, the locked prompt, reply parsing and Konkur scoring.

Everything that defines the experiment lives here, so `konkur_run.py` can fingerprint it (sha256) before a paid run.
Standard library only. Reuses: tools/llm.py (calls), tools/bluff_lab.py::value (the −1/3 score of one answer),
hmd-022 grade.py::DIGITS (Persian/Arabic digits), hmd-022 runmeta.py::dollar_lines (the $ upper bound).

Copyright: real Konkur questions are NEVER stored in git. They live in private/konkur/ (git-ignored):
    private/konkur/raw/        official PDFs (booklets + final keys) the owner downloads from Sanjesh
    private/konkur/pages/      rendered pages (konkur_prep.py render)
    private/konkur/crops/      figure crops   (konkur_prep.py crop)
    private/konkur/questions/  transcribed question files, one per exam (e.g. 1404-tajrobi.json)
    private/konkur/runs/       raw model replies and live events
Only aggregate results (no question text) go to artifact/results/.
KONKUR_PRIVATE=/some/dir moves all of that elsewhere (self-tests use a temp folder).
"""
import json
import math
import os
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT / 'tools', ROOT / 'parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact'):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import bluff_lab            # noqa: E402  value(label, penalty): 1 / 0 / −penalty
from grade import DIGITS    # noqa: E402  Persian + Arabic-Indic digits → ASCII

PENALTY = 1 / 3             # Konkur: a wrong answer costs one third of a right one (3 right = +9, 1 wrong = −3 … /3)
GROUPS = {'tajrobi': 'علوم تجربی', 'riazi': 'ریاضی و فنی'}
SUBJECTS = {'bio': 'زیست‌شناسی', 'chem': 'شیمی', 'phys': 'فیزیک', 'math': 'ریاضی', 'geo': 'زمین‌شناسی',
            'other': 'سایر'}
YEARS = (1403, 1404, 1405)
FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')


def private_dir():
    return Path(os.environ.get('KONKUR_PRIVATE') or ROOT / 'private' / 'konkur')


def fa(x):
    return str(x).translate(FA)


# ── the locked prompt (protocol.md §3) ───────────────────────────────────────────────────────────
SYSTEM = (
    'تو در آزمون سراسری ایران (کنکور) شرکت کرده‌ای. هر سؤال چهار گزینه دارد و فقط یک گزینه درست است.\n'
    'قانون نمره همان قانون کنکور است: پاسخ درست سه نمرهٔ مثبت، پاسخ غلط یک نمرهٔ منفی '
    '(یعنی هر پاسخ غلط یک‌سوم یک پاسخ درست را پاک می‌کند) و سؤال بی‌پاسخ صفر.\n'
    'بی‌پاسخ گذاشتن مجاز است. اینترنت، ابزار و ماشین‌حساب نداری. اگر شکلی لازم باشد، به پیوست همان سؤال است.\n'
    'فقط یک شیء JSON برگردان و هیچ متن دیگری ننویس: {"choice": 1} تا {"choice": 4} برای جواب، '
    'یا {"choice": null} اگر سؤال را بی‌پاسخ می‌گذاری.')
SCHEMA = {'type': 'object',
          'properties': {'choice': {'type': ['integer', 'null'], 'enum': [1, 2, 3, 4, None],
                                    'description': 'شمارهٔ گزینه (۱ تا ۴) یا null برای بی‌پاسخ'}},
          'required': ['choice'], 'additionalProperties': False}
MAX_TOKENS = 16000          # reasoning models think inside this cap; a reply that hits it is recorded as truncated


def prompt_for(q):
    """The user turn for one question. Same text for every model."""
    lines = [f'کنکور سراسری {fa(q["year"])} · گروه {GROUPS[q["group"]]} · درس {SUBJECTS[q["subject"]]} · '
             f'سؤال {fa(q["number"])}', '', q['stem'].strip(), '']
    lines += [f'{fa(i)}) {opt.strip()}' for i, opt in enumerate(q['options'], 1)]
    if q.get('figures'):
        lines += ['', f'({fa(len(q["figures"]))} تصویر پیوست این سؤال است.)']
    return '\n'.join(lines)


def figure_paths(q, base=None):
    base = Path(base or private_dir())
    return [str(base / f['path']) for f in q.get('figures', [])]


# ── question files (konkur_prep.py validate) ─────────────────────────────────────────────────────
KEY_STATUS = ('final', 'preliminary', 'cancelled')


def validate_exam(doc, base=None, check_files=True):
    """Problems (strings) in one question file; empty list = valid. See protocol.md §2 for the schema."""
    errs = []
    exam = doc.get('exam') if isinstance(doc, dict) else None
    if not isinstance(exam, dict):
        return ['top level must be {"exam": {...}, "questions": [...]}']
    for k in ('year', 'group', 'booklet', 'key_source'):
        if exam.get(k) in (None, ''):
            errs.append(f'exam.{k} missing')
    if exam.get('year') not in YEARS:
        errs.append(f'exam.year must be one of {YEARS}')
    if exam.get('group') not in GROUPS:
        errs.append(f'exam.group must be one of {list(GROUPS)}')
    qs = doc.get('questions')
    if not isinstance(qs, list) or not qs:
        return errs + ['questions must be a non-empty list']
    seen_id, seen_n = set(), set()
    for i, q in enumerate(qs):
        at = f'questions[{i}] ({q.get("id", "?")})' if isinstance(q, dict) else f'questions[{i}]'
        if not isinstance(q, dict):
            errs.append(f'{at}: not an object')
            continue
        for k in ('id', 'year', 'group', 'subject', 'number', 'stem', 'options', 'key_status'):
            if k not in q:
                errs.append(f'{at}: {k} missing')
        if q.get('id') in seen_id:
            errs.append(f'{at}: duplicate id')
        seen_id.add(q.get('id'))
        if q.get('number') in seen_n:
            errs.append(f'{at}: duplicate number')
        seen_n.add(q.get('number'))
        if (q.get('year'), q.get('group')) != (exam.get('year'), exam.get('group')):
            errs.append(f'{at}: year/group differ from exam')
        if q.get('subject') not in SUBJECTS:
            errs.append(f'{at}: subject must be one of {list(SUBJECTS)}')
        if not isinstance(q.get('number'), int) or q.get('number', 0) < 1:
            errs.append(f'{at}: number must be a positive integer (booklet number)')
        if not str(q.get('stem', '')).strip():
            errs.append(f'{at}: empty stem')
        opts = q.get('options')
        if not (isinstance(opts, list) and len(opts) == 4 and all(isinstance(o, str) and o.strip() for o in opts)):
            errs.append(f'{at}: options must be 4 non-empty strings')
        st, key = q.get('key_status'), q.get('key')
        if st not in KEY_STATUS:
            errs.append(f'{at}: key_status must be one of {KEY_STATUS}')
        if st == 'cancelled':
            if key not in (None, []):
                errs.append(f'{at}: a cancelled question has key null')
        elif not (isinstance(key, list) and key and all(k in (1, 2, 3, 4) for k in key) and len(set(key)) == len(key)):
            errs.append(f'{at}: key must be a list of accepted options, e.g. [3] (two only if Sanjesh accepted two)')
        for f in q.get('figures', []):
            if not isinstance(f, dict) or not f.get('path'):
                errs.append(f'{at}: each figure needs a path (relative to private/konkur/)')
            elif check_files and not (Path(base or private_dir()) / f['path']).exists():
                errs.append(f'{at}: figure file not found: {f["path"]}')
            if isinstance(f, dict) and 'crop' in f:
                c = f['crop']
                if not (isinstance(c, dict) and c.get('pdf') and isinstance(c.get('page'), int)
                        and isinstance(c.get('box'), list) and len(c['box']) == 4):
                    errs.append(f'{at}: crop must be {{"pdf", "page", "dpi", "box": [x, y, w, h]}}')
        if '$' in q.get('stem', '') and q['stem'].count('$') % 2:
            errs.append(f'{at}: unbalanced $…$ LaTeX in stem')
    return errs


def load_exams(paths):
    """Questions from question files, in exam order (year, group, booklet number)."""
    qs = []
    for p in paths:
        doc = json.loads(Path(p).read_text(encoding='utf-8'))
        qs += doc['questions']
    return sorted(qs, key=lambda q: (q['year'], q['group'], q['number']))


def question_files(names=None):
    d = private_dir() / 'questions'
    files = sorted(d.glob('*.json')) if d.exists() else []
    return [f for f in files if not names or f.stem in names]


# ── replies and scoring ──────────────────────────────────────────────────────────────────────────
def parse_choice(text):
    """(choice 1-4 or None, flag). flag: ok · blank (said null) · unparsed (no usable answer; scored blank)."""
    t = str(text or '').translate(DIGITS).strip()
    t = re.sub(r'^```(?:json)?|```$', '', t, flags=re.M).strip()
    m = re.search(r'\{[^{}]*\}', t)
    if m:
        try:
            v = json.loads(m.group(0)).get('choice', 'missing')
        except (ValueError, AttributeError):
            v = 'missing'
        if v is None or (isinstance(v, str) and v.strip().lower() in ('', 'null', 'none')):
            return None, 'blank'
        if isinstance(v, str) and v.strip().isdigit():
            v = int(v.strip())
        if isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 4:
            return v, 'ok'
    hits = set(re.findall(r'(?:choice|گزینه[ٔ]?(?:\s*ی)?)\s*"?\s*[:=]?\s*"?([1-4])\b', t))
    if len(hits) == 1:
        return int(hits.pop()), 'ok'
    return None, 'unparsed'


def label_for(q, choice):
    """correct / wrong / abstain, or None for a cancelled question (not scored)."""
    if q.get('key_status') == 'cancelled':
        return None
    if choice is None:
        return 'abstain'
    return 'correct' if choice in q['key'] else 'wrong'


def item_value(label):
    """Points of one answer in units of one right answer (bluff_lab.value with the Konkur penalty)."""
    return 0.0 if label is None else bluff_lab.value(label, PENALTY)


def konkur_percent(labels):
    """Konkur درصد: (3·right − wrong) / (3·n) × 100, n = scored questions (cancelled ones excluded)."""
    scored = [x for x in labels if x is not None]
    if not scored:
        return None
    return 100 * sum(item_value(x) for x in scored) / len(scored)


def bootstrap_diff(a, b, reps=4000, seed=1405):
    """Percentile interval (95%) for mean(a) − mean(b) of per-question values, resampling questions."""
    if not a or not b:
        return None
    rng = random.Random(seed)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    diffs = sorted(sum(rng.choice(a) for _ in a) / len(a) - sum(rng.choice(b) for _ in b) / len(b)
                   for _ in range(reps))
    return ma - mb, diffs[int(0.025 * reps)], diffs[int(0.975 * reps) - 1]


def mean_ci(xs):
    """Mean of per-question values with a normal 95% interval (questions as the sample)."""
    if not xs:
        return None
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, m, m
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))
    h = 1.96 * sd / math.sqrt(len(xs))
    return m, m - h, m + h


def median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def selfcheck():
    assert parse_choice('{"choice": 3}') == (3, 'ok')
    assert parse_choice('```json\n{"choice": "۲"}\n```') == (2, 'ok')
    assert parse_choice('{"choice": null}') == (None, 'blank')
    assert parse_choice('گزینهٔ ۴') == (4, 'ok')
    assert parse_choice('گزینه 4 درست است') == (4, 'ok')
    assert parse_choice('1 or 2') == (None, 'unparsed')
    assert parse_choice('{"choice": 7}') == (None, 'unparsed')
    q = {'key_status': 'final', 'key': [2]}
    assert [label_for(q, c) for c in (2, 3, None)] == ['correct', 'wrong', 'abstain']
    assert label_for({'key_status': 'cancelled', 'key': None}, 1) is None
    assert abs(konkur_percent(['correct'] * 3 + ['wrong'] * 3) - 100 * (3 - 1) / 6) < 1e-9
    assert abs(konkur_percent(['wrong'] * 4) + 100 / 3) < 1e-9                   # the floor: all wrong = −33.3%
    assert konkur_percent(['abstain', None]) == 0.0
    d = bootstrap_diff([1.0] * 20, [0.0] * 20)
    assert d[0] == 1.0 and d[1] == d[2] == 1.0
    return True
