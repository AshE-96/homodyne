#!/usr/bin/env python3
"""HMD-S05 · imo_core.py — data, protocol, mock models and the Problem 1 checker for the live page.

Standard library only. Nothing here calls a paid API; imo_live.py does that, and only with --live --yes.

    rebuild()       re-derive derived/imo-stats.json from imo-official.org (public pages, no login)
    load_stats()    the committed aggregate statistics (no contestant names are ever stored)
    sunny_ks(n)     brute-force: which k work in IMO 2025 Problem 1 for this n (small n only)
    statement()     the official English statement, read from artifact/data/ (git-ignored; IMO copyright)
"""
import hashlib
import html as htmllib
import json
import math
import re
import shutil
import statistics
import subprocess
import time
import urllib.request
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DERIVED = HERE / 'derived'
DATA = HERE / 'data'                       # git-ignored (.gitignore: parts/*/*/artifact/data/)
STATS = DERIVED / 'imo-stats.json'
BASE = 'https://www.imo-official.org'
UA = 'Mozilla/5.0 (compatible; homodyne-research/1.0; public IMO statistics)'
PAGES = {
    'edition_2024': '/editions/2024/', 'edition_2025': '/editions/2025/', 'edition_2026': '/editions/2026/',
    'team_2024': '/results/team/year/2024/', 'team_2025': '/results/team/year/2025/',
    'team_2026': '/results/team/year/2026/',
    'individual_2024': '/results/individual/year/2024/', 'individual_2025': '/results/individual/year/2025/',
    'individual_2026': '/results/individual/year/2026/',
    'iran_history': '/results/team/country/IRN/', 'iran_country': '/countries/IRN/',
}
PROBLEM_PDF = BASE + '/assets/documents/problems/2025/2025_eng.pdf'

# Hand-entered from primary sources (sources.md). grader: official | company | claim.
AI_RESULTS = [
    {'year': 2024, 'system': 'AlphaProof + AlphaGeometry 2', 'lab': 'Google DeepMind', 'score': 28,
     'per_problem': [7, 7, 0, 7, 0, 7], 'grader': 'company', 'graders_fa': 'گاورز و مایرز، بیرون از داوری رسمی',
     'conditions_fa': 'صورت مسئله را آدم به Lean ترجمه کرد · تا سه روز برای بعضی مسئله‌ها',
     'conditions_en': 'humans translated the problems into Lean · up to three days on some problems', 'src': 'R10'},
    {'year': 2025, 'system': 'Gemini Deep Think (advanced)', 'lab': 'Google DeepMind', 'score': 35,
     'per_problem': [7, 7, 7, 7, 7, 0], 'grader': 'official', 'graders_fa': 'هماهنگ‌کنندگان IMO، با معیار دانش‌آموزان',
     'conditions_fa': 'زبان طبیعی · در ۴٫۵ ساعت · با راهنمایی و مجموعهٔ حل‌های گزیده در دستور',
     'conditions_en': 'natural language · within 4.5 h · hints and a curated corpus of solutions in its instructions',
     'src': 'R11'},
    {'year': 2025, 'system': 'experimental reasoning model', 'lab': 'OpenAI', 'score': 35,
     'per_problem': [7, 7, 7, 7, 7, 0], 'grader': 'company', 'graders_fa': 'سه مدال‌آور سابق IMO در ارزیابی خود شرکت، اجماع',
     'conditions_fa': 'زبان طبیعی · دو جلسهٔ ۴٫۵ ساعته · بی ابزار و اینترنت (خوداظهاری)',
     'conditions_en': 'natural language · two 4.5 h sessions · no tools or internet (self-reported)', 'src': 'R12'},
    {'year': 2026, 'system': 'Celia · dots-note-3.0', 'lab': 'Huawei · Xiaohongshu', 'score': 42,
     'per_problem': None, 'grader': 'claim', 'graders_fa': 'ادعای شرکت؛ بیانیهٔ IMO پیدا نشد',
     'conditions_fa': 'گزارش AFP، ۲۳ ژوئیهٔ ۲۰۲۶', 'conditions_en': 'AFP report, 23 July 2026', 'src': 'R16'},
]


# ── fetching and parsing imo-official.org ─────────────────────────────────────────────────────────
def fetch(path, raw_dir):
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / (path.strip('/').replace('/', '_') + '.html')
    if not out.exists():
        req = urllib.request.Request(BASE + path, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            out.write_bytes(r.read())
        time.sleep(1.0)                    # be polite to a volunteer-run site
    return out.read_text(encoding='utf-8')


def plain(fragment):
    return re.sub(r'\s+', ' ', htmllib.unescape(re.sub(r'<[^>]+>', ' ', fragment))).strip()


def tbody_rows(html):
    body = html[html.find('<tbody'):html.find('</tbody>')]
    return [re.findall(r'<td([^>]*)>(.*?)</td>', r, re.S) for r in re.findall(r'<tr[^>]*>(.*?)</tr>', body, re.S)]


def num(s):
    s = plain(s)
    return int(s) if s.isdigit() else 0


def parse_individual(html):
    """[(country_iso, award, total, [p1..p6])]. The name cell is dropped here and never stored."""
    rows = []
    for tds in tbody_rows(html):
        iso = re.search(r'country-iso">([A-Z]+)<', tds[1][1])
        aw = re.search(r'award-circle--(\w+)', tds[3][1])
        rows.append((iso.group(1) if iso else '', aw.group(1) if aw else '', num(tds[4][1]),
                     [num(v) for _, v in tds[5:11]]))
    return rows


def parse_team_row(tds, offset):
    """Team table cells from `offset` (rank): rank, [ratio], points, p1..p6, G, S, B, HM."""
    vals = [plain(v) for _, v in tds[offset:]]
    if '%' in vals[1]:
        vals.pop(1)
    n = [int(v) if v.isdigit() else 0 for v in vals[:12]]
    return {'rank': n[0], 'points': n[1], 'problems': n[2:8], 'gold': n[8], 'silver': n[9], 'bronze': n[10],
            'hm': n[11]}


def parse_team(html, iso):
    for tds in tbody_rows(html):
        if f'country-iso">{iso}<' in tds[0][1]:
            return parse_team_row(tds, 1)
    raise ValueError(f'{iso} not in team table')


def parse_history(html):
    out = []
    for tds in tbody_rows(html):
        year = plain(tds[0][1])
        if year.isdigit():
            out.append({'year': int(year), **parse_team_row(tds, 1)})
    return sorted(out, key=lambda r: r['year'])


def parse_edition(html):
    t = plain(html)
    m = re.search(r'1959 ([^·]+?) · (\w+ \d+ - \d+) (\d+) Countries (\d+) Contestants', t)
    cut = {k: int(v) for k, v in re.findall(r'(Gold|Silver|Bronze) ≥(\d+) pts', t)}
    cnt = {k: int(v) for v, k in re.findall(r'(\d+) (Gold|Silver|Bronze|Hon\. Mentions|Perfect Scores)', t)}
    return {'place': m.group(1).strip(), 'dates': m.group(2), 'countries': int(m.group(3)),
            'contestants': int(m.group(4)), 'cutoffs': {k.lower(): v for k, v in cut.items()},
            'counts': {'gold': cnt['Gold'], 'silver': cnt['Silver'], 'bronze': cnt['Bronze'],
                       'hm': cnt['Hon. Mentions'], 'perfect': cnt['Perfect Scores']}}


def problem_stats(rows):
    out = []
    for p in range(6):
        sc = [r[3][p] for r in rows]
        out.append({'problem': p + 1, 'hist': [sc.count(k) for k in range(8)], 'mean': round(statistics.mean(sc), 3),
                    'full': sc.count(7), 'zero': sc.count(0)})
    return out


def rebuild(raw_dir=None):
    """Download (or reuse) the public pages, keep only aggregates, write derived/imo-stats.json."""
    raw_dir = Path(raw_dir) if raw_dir else DATA / 'raw'
    pages = {k: fetch(v, raw_dir) for k, v in PAGES.items()}
    years = {}
    for y in (2024, 2025, 2026):
        rows = parse_individual(pages[f'individual_{y}'])
        totals = [r[2] for r in rows]
        years[str(y)] = {**parse_edition(pages[f'edition_{y}']), 'n_rows': len(rows),
                         'problems': problem_stats(rows), 'total_hist': [totals.count(s) for s in range(43)],
                         'iran': parse_team(pages[f'team_{y}'], 'IRN')}
    t = plain(pages['iran_country'])
    first = re.search(r'(\d{4}) First Participation (\d+) Participations', t)
    aw = {k: int(v) for v, k in re.findall(r'(\d+) (Gold|Silver|Bronze|Hon\. Mentions|Perfect Scores)', t)}
    stats = {'source': BASE, 'derived_on': time.strftime('%Y-%m-%d'),
             'note': 'Aggregates only. No contestant names or photos are stored (minors).',
             'pages_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k, v in pages.items()},
             'years': years, 'iran_history': parse_history(pages['iran_history']),
             'iran_overall': {'first': int(first.group(1)), 'participations': int(first.group(2)),
                              'gold': aw['Gold'], 'silver': aw['Silver'], 'bronze': aw['Bronze'],
                              'hm': aw['Hon. Mentions'], 'perfect': aw['Perfect Scores']},
             'ai_results': AI_RESULTS}
    DERIVED.mkdir(exist_ok=True)
    STATS.write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding='utf-8')
    return stats


def load_stats():
    return json.loads(STATS.read_text(encoding='utf-8'))


# ── Problem 1 (sunny lines): exhaustive check for small n ──────────────────────────────────────────
def _lines(points):
    """Every line through >= 2 of the points, plus every boring line through >= 1, as (mask, sunny)."""
    idx = {p: i for i, p in enumerate(points)}
    found = {}
    for i, (x1, y1) in enumerate(points):
        for x2, y2 in points[i + 1:]:
            a, b = y2 - y1, x1 - x2
            c = a * x1 + b * y1
            g = math.gcd(math.gcd(abs(a), abs(b)), abs(c))
            a, b, c = a // g, b // g, c // g
            if a < 0 or (a == 0 and b < 0):
                a, b, c = -a, -b, -c
            found[(a, b, c)] = None
    for x, y in points:                    # horizontal, vertical, anti-diagonal through each point
        found[(0, 1, y)] = found[(1, 0, x)] = found[(1, 1, x + y)] = None
    out = []
    for a, b, c in found:
        mask = sum(1 << idx[p] for p in points if a * p[0] + b * p[1] == c)
        out.append((mask, not (a == 0 or b == 0 or a == b)))
    return out


def sunny_ks(n):
    """All k for which n distinct lines, exactly k sunny, cover {(a,b): a,b >= 1, a+b <= n+1}."""
    pts = [(a, b) for a in range(1, n + 1) for b in range(1, n + 2 - a)]
    lines = _lines(pts)
    through = [[ln for ln in lines if ln[0] >> i & 1] + [(1 << i, True)] for i in range(len(pts))]

    @lru_cache(maxsize=None)
    def f(unc, r):                          # set of sunny counts using exactly r more distinct lines
        if not unc:
            return frozenset(range(r + 1))  # spare lines: any mix of fresh sunny / fresh boring lines
        if r == 0:
            return frozenset()
        i = (unc & -unc).bit_length() - 1   # first uncovered point: some line must pass through it
        out = set()
        for mask, sunny in through[i]:
            out |= {s + sunny for s in f(unc & ~mask, r - 1)}
        return frozenset(out)

    return sorted(f((1 << len(pts)) - 1, n))


# ── the fixed protocol (protocol.md is the human-readable copy) ────────────────────────────────────
SYSTEM = ('You are a contestant at the International Mathematical Olympiad. Solve the problem below. '
          'Write a complete, rigorous proof in English, as you would on the answer sheet. State the final answer '
          'clearly at the start. Do not use any tools, code or outside sources. You have one attempt.')
PROBLEMS = {'P1': {'day': 1, 'rubric': 'rubrics/2025-P1.json'}, 'P6': {'day': 2, 'rubric': 'rubrics/2025-P6.json'}}
MAX_TOKENS = 32000


def statement(pid):
    """Official English statement from artifact/data/problems/2025-<pid>.txt (see fetch_statements)."""
    f = DATA / 'problems' / f'2025-{pid}.txt'
    if not f.exists():
        raise FileNotFoundError(f'{f} missing: run `python3 imo_live.py --fetch-problems` (needs network) '
                                'or paste the statement there yourself. It is not bundled (IMO copyright).')
    return f.read_text(encoding='utf-8').strip()


def fetch_statements():
    """Download the official 2025 English PDF to artifact/data/ and cut out P1 and P6 with pdftotext."""
    d = DATA / 'problems'
    d.mkdir(parents=True, exist_ok=True)
    pdf = d / '2025_eng.pdf'
    if not pdf.exists():
        req = urllib.request.Request(PROBLEM_PDF, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            pdf.write_bytes(r.read())
    if not shutil.which('pdftotext'):
        return f'saved {pdf}; pdftotext not found: paste Problem 1 and 6 into {d}/2025-P1.txt and 2025-P6.txt'
    text = subprocess.run(['pdftotext', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
    for pid, a, b in (('P1', 'Problem 1.', 'Problem 2.'), ('P6', 'Problem 6.', 'Language: English')):
        part = text[text.index(a) + len(a):text.index(b, text.index(a))]
        (d / f'2025-{pid}.txt').write_text(re.sub(r'[ \t]+', ' ', part).strip() + '\n', encoding='utf-8')
    return f'saved {pdf} (sha256 {hashlib.sha256(pdf.read_bytes()).hexdigest()[:16]}…) and the P1, P6 statements'


def rubric(pid):
    return json.loads((HERE / PROBLEMS[pid]['rubric']).read_text(encoding='utf-8'))


def prompt_for(pid, text):
    return f'Problem ({pid[1:]}). {text}\n\nWrite your full solution.'


# ── mock models for rehearsal (no key, no network; every answer is marked MOCK) ───────────────────
MOCK_SLOTS = [{'slot': s, 'label': l, 'model': f'mock:{s}'} for s, l in
              (('gemini', 'Gemini'), ('claude', 'Claude'), ('gpt', 'GPT'), ('open1', 'Open model 1'),
               ('open2', 'Open model 2'))]
MOCK_SECONDS = {'gemini': 41, 'claude': 63, 'gpt': 88, 'open1': 29, 'open2': 52}


def mock_answer(slot, pid):
    """A fixed placeholder so the page can be rehearsed. It is not a model output and it is never graded."""
    h = int(hashlib.sha256(f'{slot}{pid}'.encode()).hexdigest()[:6], 16)
    lines = ['[MOCK ANSWER — not written by any model; for rehearsal only]',
             f'Slot {slot}, problem {pid}. Placeholder text whose length varies by slot ({h % 7 + 3} paragraphs).']
    lines += [f'Paragraph {i + 1}: placeholder reasoning step.' for i in range(h % 7 + 3)]
    return '\n\n'.join(lines)


def usd(ev, prices):
    """Dollar cost of one answer: OpenRouter's reported cost, else prices.json; None when unknown."""
    if ev.get('cost_usd') is not None:
        return ev['cost_usd']
    p = prices.get('models', {}).get(ev['model'])
    if not p:
        return None
    return (ev['input_tokens'] * p['input_per_mtok'] + ev['output_tokens'] * p['output_per_mtok']) / 1e6


def upper_bound_usd(ev, prices):
    fb = prices['fallback'].get(ev['model'].split(':')[0], prices['fallback']['default'])
    return (ev['input_tokens'] * fb['input_per_mtok'] + ev['output_tokens'] * fb['output_per_mtok']) / 1e6


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['rebuild']:
        s = rebuild()
        print('wrote', STATS, '·', {y: v['n_rows'] for y, v in s['years'].items()})
    elif sys.argv[1:2] == ['sunny']:            # on camera: python3 imo_core.py sunny 6
        for n in range(3, int(sys.argv[2]) + 1 if len(sys.argv) > 2 else 7):
            t = time.time()
            pts = n * (n + 1) // 2
            print(f'n = {n}  ({pts} points, {n} lines)  possible numbers of sunny lines: {sunny_ks(n)}'
                  f'   [{time.time() - t:.2f} s, exhaustive search: a check of small cases, not a proof]')
    else:
        print(__doc__)
