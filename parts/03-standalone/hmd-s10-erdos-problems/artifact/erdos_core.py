"""erdos_core.py · HMD-S10 · parsing and maths for the Erdős-problems demo (standard library only).

Data (all public, key-less, read from GitHub — never from erdosproblems.com, whose robots.txt
disallows AI agents such as Claude-User and ChatGPT-User):
  teorth/erdosproblems  data/problems.yaml, data/statistics_history.csv   Apache-2.0
  teorth/erdosproblems  wiki page "AI contributions to Erdős problems"    frozen 30 Jun 2026; facts only

Maths (Erdős problem #1026, the weighted Erdős–Szekeres problem):
  For distinct positive reals x_1..x_n let A_i (B_i) be the largest sum of an increasing (decreasing)
  subsequence that ends at x_i. The squares [A_i - x_i, A_i] x [B_i - x_i, B_i] never overlap and fit in
  [0, A] x [0, B], A = max A_i, B = max B_i. Hence sum x_i^2 <= A*B, and by Cauchy–Schwarz
  max(A, B) >= sum x_i / sqrt(n). For n = k^2 and sum 1 that is 1/k, and 1/k cannot be improved.
"""
import csv
import io
import random
import re

RAW = 'https://raw.githubusercontent.com/teorth/erdosproblems/main/'
WIKI_RAW = 'https://raw.githubusercontent.com/wiki/teorth/erdosproblems/AI-contributions-to-Erd%C5%91s-problems.md'
FILES = {'problems.yaml': RAW + 'data/problems.yaml', 'statistics_history.csv': RAW + 'data/statistics_history.csv',
         'STATISTICS.md': RAW + 'STATISTICS.md', 'LICENSE': RAW + 'LICENSE', 'wiki-ai.md': WIKI_RAW}

# informal_status.state -> the four families used on screen (wording follows STATISTICS.md)
FAMILY = {'proved': 'solved', 'disproved': 'solved', 'solved': 'solved',
          'open': 'open',
          'falsifiable': 'finite', 'verifiable': 'finite', 'decidable': 'finite',
          'not provable': 'zfc', 'not disprovable': 'zfc', 'independent': 'zfc'}
STATES = ['proved', 'disproved', 'solved', 'open', 'falsifiable', 'verifiable', 'decidable',
          'not provable', 'not disprovable', 'independent']

SECTIONS = {  # wiki section -> (short label, what it means), from "AI contribution section placement system"
    '1a': ('AI standalone', 'comparable literature unknown; no significant human input'),
    '1b': ('AI alongside literature', 'comparable literature discovered AFTERWARDS'),
    '1c': ('AI building on literature', 'comparable literature known beforehand'),
    '1d': ('AI collaborating with humans', 'significant human involvement'),
    '2a': ('Literature search', 'AI found existing work'),
    '2b': ('Formalization', 'AI turned a known proof into Lean'),
    '2c': ('Rewriting', 'AI rewrote or critiqued an argument'),
    '2d': ('Computation', 'AI ran a well-defined calculation'),
}
COLOR = {'🟢': 'full', '🟡': 'partial', '🔴': 'incorrect', '⚪': 'unverified'}
MONTHS = {m: i for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}


# ---------------------------------------------------------------- problems.yaml (fixed, regular layout)
def _field(block, key):
    m = re.search(r'^  ' + key + r':\n((?:    .*\n?|      .*\n?)+)', block, re.M)
    if not m:
        return {}
    sub = m.group(1)
    out = {}
    for k in ('state', 'last_update', 'url'):
        mm = re.search(r'^    ' + k + r': "([^"]*)"', sub, re.M)
        if mm:
            out[k] = mm.group(1)
    mm = re.search(r'^    note: "(.*?)"\s*$', sub, re.M | re.S)
    if mm:
        out['note'] = re.sub(r'\s+', ' ', mm.group(1))
    return out


def parse_problems(text):
    rows = []
    for block in re.split(r'\n(?=- number: )', '\n' + text):
        m = re.match(r'\s*- number: "([0-9\-]+)"', block)
        if not m:
            continue
        block = block.replace('- number', '  number', 1)
        prize = re.search(r'^  prize: "([^"]*)"', block, re.M)
        inf, frm, st = _field(block, 'informal_status'), _field(block, 'formal_status'), _field(block, 'status')
        rows.append(dict(n=m.group(1), prize=prize.group(1) if prize else 'no', state=inf.get('state', '?'),
                         informal_update=inf.get('last_update', ''), formal=frm.get('state', 'unformalized'),
                         formal_note=frm.get('note', ''), status=st.get('state', '?'), updated=st.get('last_update', '')))
    return rows


def status_counts(rows):
    by_state = {s: 0 for s in STATES}
    lean = {s: 0 for s in STATES}
    for r in rows:
        by_state[r['state']] = by_state.get(r['state'], 0) + 1
        if r['formal'] == 'Lean':
            lean[r['state']] = lean.get(r['state'], 0) + 1
    fam = {}
    for s, c in by_state.items():
        fam[FAMILY.get(s, 'other')] = fam.get(FAMILY.get(s, 'other'), 0) + c
    return dict(total=len(rows), by_state=by_state, lean_by_state=lean, family=fam,
                prize=sum(1 for r in rows if r['prize'] not in ('no', '')),
                open_lean=[r['n'] for r in rows if r['status'] == 'open (Lean)'])


def update_months(rows):
    """How many problems had their (informal) status last changed in each month. Only the LAST change is stored,
    so this undercounts churn; the 2025-08-31 spike is the database's creation date, not a wave of solutions."""
    out = {}
    for r in rows:
        m = r['informal_update'][:7]
        if m:
            out[m] = out.get(m, 0) + 1
    return dict(sorted(out.items()))


# ---------------------------------------------------------------- statistics_history.csv
def parse_history(text, every_days=7):
    """One row per commit -> one row per week (the last commit of each ISO week), plus the very last row."""
    rows = list(csv.DictReader(io.StringIO(text)))
    keep, last_week = [], None
    for i, r in enumerate(rows):
        day = r['date'][:10]
        y, mo, d = (int(x) for x in day.split('-'))
        week = _ordinal(y, mo, d) // every_days
        row = dict(date=day, total=int(r['total_problems']), solved=int(r['total_solved']),
                   open=int(r['open']) if r.get('open') not in (None, '', 'None') else None,
                   lean_solved=int(r['lean_solved']), lean_statements=int(r['lean_formalized']))
        if week != last_week or i == len(rows) - 1:
            keep.append(row)
            last_week = week
        else:
            keep[-1] = row
    return keep


def _ordinal(y, m, d):
    import datetime
    return datetime.date(y, m, d).toordinal()


# ---------------------------------------------------------------- the wiki tables
def _first_date(s):
    """First calendar date in the wiki's free-form Date cell: '22-23 Jun, 2026', 'Feb 5, 2026',
    '25 Oct, 2025-4 Feb, 2026', '2025'. Returns 'YYYY-MM-DD', or 'YYYY' when only a year is given."""
    s = re.sub(r'^(\d{1,2})-\d{1,2}\s', r'\1 ', s.strip())
    m = re.search(r'(?:(\d{1,2})\s+)?([A-Z][a-z]{2})(?:\s+(\d{1,2})(?=,))?', s)
    if not m or m.group(2) not in MONTHS:
        y = re.search(r'(\d{4})', s)
        return y.group(1) if y else ''
    y = re.search(r'(\d{4})', s[m.end():])
    return f'{y.group(1) if y else "????"}-{MONTHS[m.group(2)]:02d}-{int(m.group(1) or m.group(3) or 1):02d}'


def parse_wiki(md):
    entries, sect, head = [], None, []
    for line in md.splitlines():
        a = re.match(r'<a id="sect-(\d[a-d])"></a>', line.strip())
        if a:
            sect, head = a.group(1), []
            continue
        if line.startswith('| Problem'):
            head = [c.strip() for c in line.strip().strip('|').split('|')]
            continue
        if not (sect and head and line.startswith('| [[')):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        cell = dict(zip(head, cells))
        num = re.match(r'\[\[([0-9\-]+)\]\]', cells[0]).group(1)
        outcome = cell.get('Outcome', '')
        col = next((COLOR[e] for e in COLOR if outcome.startswith(e) or (outcome and e in outcome[:3])), None)
        if col is None and outcome:
            col = next((COLOR[e] for e in COLOR if e in outcome), None)
        if sect in ('2b', '2c', '2d'):
            col = 'done'
        entries.append(dict(p=num, sec=sect, date=_first_date(cell.get('Date', '')), date_text=cell.get('Date', ''),
                            ai=cell.get('AI systems', ''), humans=cell.get('Humans', ''),
                            outcome=re.sub(r'[🟢🟡🔴⚪]\s*', '', outcome).strip() or cell.get('Computation', '')
                            or cell.get('Proof to formalize', '') or cell.get('Argument to rewrite', ''),
                            color=col, lit=cell.get('Literature', ''), lit_found=cell.get('Literature found on', ''),
                            similar=cell.get('Similar?', '')))
    return entries


def wiki_summary(entries):
    out = {}
    for e in entries:
        s = out.setdefault(e['sec'], {'rows': 0, 'problems': set(), 'colors': {}})
        s['rows'] += 1
        s['problems'].add(e['p'])
        s['colors'][e['color']] = s['colors'].get(e['color'], 0) + 1
    return {k: dict(rows=v['rows'], problems=len(v['problems']), colors=v['colors']) for k, v in sorted(out.items())}


# ---------------------------------------------------------------- Erdős #1026: monotone sums and the squares
def monotone_sums(x):
    """A[i], B[i]: largest sum of an increasing / decreasing subsequence ending at x[i] (O(n^2) DP),
    with back-pointers so the best subsequences can be drawn."""
    n = len(x)
    A, B, pa, pb = list(x), list(x), [-1] * n, [-1] * n
    for j in range(n):
        for i in range(j):
            if x[i] < x[j] and A[i] + x[j] > A[j]:
                A[j], pa[j] = A[i] + x[j], i
            if x[i] > x[j] and B[i] + x[j] > B[j]:
                B[j], pb[j] = B[i] + x[j], i
    return A, B, pa, pb


def best_monotone(x):
    A, B, pa, pb = monotone_sums(x)
    ia = max(range(len(x)), key=lambda i: A[i])
    ib = max(range(len(x)), key=lambda i: B[i])

    def walk(i, p):
        out = []
        while i >= 0:
            out.append(i)
            i = p[i]
        return out[::-1]
    return dict(A=A[ia], B=B[ib], inc=walk(ia, pa), dec=walk(ib, pb))


def brute_best(x):
    """Exponential check for small n: the best monotone subsequence sum by trying every subset."""
    n, best = len(x), 0.0
    for mask in range(1, 1 << n):
        idx = [i for i in range(n) if mask >> i & 1]
        v = [x[i] for i in idx]
        if all(a < b for a, b in zip(v, v[1:])) or all(a > b for a, b in zip(v, v[1:])):
            best = max(best, sum(v))
    return best


def squares(x):
    A, B, _, _ = monotone_sums(x)
    return [(A[i] - x[i], B[i] - x[i], x[i]) for i in range(len(x))]   # (left, bottom, side)


def overlap(sq):
    """Largest overlap area between any two squares (0 when the packing argument holds)."""
    worst = 0.0
    for i in range(len(sq)):
        for j in range(i):
            (a, b, s), (c, d, t) = sq[i], sq[j]
            w = min(a + s, c + t) - max(a, c)
            h = min(b + s, d + t) - max(b, d)
            if w > 1e-12 and h > 1e-12:
                worst = max(worst, w * h)
    return worst


def alice(k, eps=1e-3, seed=None):
    """Alice's best split for k^2 piles: nearly equal piles in k blocks, each block decreasing and the blocks
    increasing (3 2 1 6 5 4 9 8 7 for k = 3). Every increasing subsequence takes at most one pile per block and
    every decreasing one stays inside a block, so Bob gets about k piles of about 1/k^2 each: about 1/k."""
    order = [b * k + (k - 1 - j) for b in range(k) for j in range(k)]
    raw = [1 + eps * (r + 1) / (k * k) for r in order]
    s = sum(raw)
    return [v / s for v in raw]


def random_piles(n, seed=None):
    rng = random.Random(seed)
    raw = [rng.random() + 0.05 for _ in range(n)]
    s = sum(raw)
    return [v / s for v in raw]
