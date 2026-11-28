#!/usr/bin/env python3
"""erdos_live.py · HMD-S10 · live demo page for recording, standard library only.

    python3 -I artifact/erdos_live.py              # build artifact/erdos_live.html from artifact/derived/erdos-derived.json
    python3 -I artifact/erdos_live.py --fetch      # download the public data again from GitHub, re-derive, build
    python3 -I artifact/erdos_live.py --serve      # build, then serve on http://127.0.0.1:8770/erdos_live.html
    python3 -I artifact/erdos_live.py --selftest   # offline checks (no network, no keys)

Views (keys 1 2 3):
  1 · ledger   how the database records status: four families, the weekly history, the "open (Lean)" label,
               and the 6 Oct 2026 policy line (no headline percentage, by the site owner's request)
  2 · records  every documented AI contribution (frozen wiki, 30 Jun 2026) on a timeline, one row per KIND of
               contribution; colour = the wiki's own outcome mark. Grouped by kind, never by company.
  3 · coins    Erdős problem #1026 as a game: Alice splits one coin-heap into k^2 piles, Bob keeps the best
               monotone run. Bob's share, Alice's best split, and the non-overlapping squares behind the proof.
URL parameters fix a state for a take: ?view=a · ?view=b&sec=2a · ?view=c&k=3&preset=alice&sq=1
Data is read from GitHub (Apache-2.0), never from erdosproblems.com: its robots.txt disallows AI agents.
"""
import argparse
import datetime
import http.server
import json
import math
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import erdos_core as ec  # noqa: E402

DERIVED = HERE / 'derived' / 'erdos-derived.json'
RAWDIR = HERE / 'data'                       # git-ignored: raw downloads
PAGE = HERE / 'erdos_live.html'
UA = 'homodyne-demo/1.0 (+https://homodyne.m2gh.ir)'

# Events drawn on the history chart. Every line is checked in ../sources.md (ids in brackets).
EVENTS = [
    dict(d='2025-10-11', t='GPT-5 literature search: old papers found for "open" problems', src='R05 R06 R07'),
    dict(d='2025-12-07', t='#1026: Aristotle proves the k² case in Lean; a 2016 paper turns up next day', src='R09 R10'),
    dict(d='2025-12-25', t='#333: "first autonomous" claim; Erdős & Newman (1977) found the same day', src='R08 R11'),
    dict(d='2026-01-06', t='#728: Aristotle + GPT-5.2 Pro, Lean proof (Pomerance 2014 similar)', src='R12'),
    dict(d='2026-01-29', t='Aletheia paper: 700 "open" checked, 13 addressed, 8 already in the literature', src='R13'),
    dict(d='2026-05-20', t='#90 unit distance conjecture disproved (OpenAI model; checked by outside mathematicians; 9-author companion paper)', src='R14 R15'),
    dict(d='2026-06-30', t='AI-contributions wiki frozen', src='R04'),
    dict(d='2026-10-06', t='erdosproblems.com stops showing statuses and solved counts', src='R03'),
]


def fetch():
    RAWDIR.mkdir(exist_ok=True)
    for name, url in ec.FILES.items():
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            (RAWDIR / name).write_bytes(r.read())
        print(f'  got {name:24} {(RAWDIR / name).stat().st_size:>8} bytes  ({url})')


def derive():
    yaml_t = (RAWDIR / 'problems.yaml').read_text(encoding='utf-8')
    csv_t = (RAWDIR / 'statistics_history.csv').read_text(encoding='utf-8')
    wiki_t = (RAWDIR / 'wiki-ai.md').read_text(encoding='utf-8')
    rows = ec.parse_problems(yaml_t)
    hist = ec.parse_history(csv_t)
    last_commit = csv_t.strip().splitlines()[-1].split(',')[0]
    entries = ec.parse_wiki(wiki_t)
    notes = {r['n']: r['formal_note'] for r in rows if r['status'] == 'open (Lean)'}
    data = dict(
        meta=dict(made_by='artifact/erdos_live.py --fetch (erdos_core.py, standard library)',
                  derived_on=datetime.date.today().isoformat(), repo='github.com/teorth/erdosproblems',
                  repo_commit=last_commit, repo_last_commit_date=hist[-1]['date'], licence='Apache-2.0',
                  wiki='github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erdős-problems (frozen 30 Jun 2026)'),
        counts=ec.status_counts(rows), open_lean_notes=notes, updates=ec.update_months(rows),
        history=hist, wiki=entries, wiki_summary=ec.wiki_summary(entries), sections=ec.SECTIONS,
        problems=[[r['n'], r['state'], r['informal_update'], r['prize']] for r in rows])
    DERIVED.parent.mkdir(exist_ok=True)
    DERIVED.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'wrote {DERIVED.relative_to(HERE.parent)}: {len(rows)} problems, {len(hist)} weekly rows, {len(entries)} wiki rows')
    return data


def build(do_fetch=False):
    if do_fetch:
        fetch()
        derive()
    data = json.loads(DERIVED.read_text(encoding='utf-8'))
    data['events'] = EVENTS
    html = (HERE / 'erdos_page.html').read_text(encoding='utf-8')
    PAGE.write_text(html.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':'))), encoding='utf-8')
    c = data['counts']
    print(f'wrote {PAGE.relative_to(HERE.parent)}  ({c["total"]} problems · data commit {data["meta"]["repo_commit"][:7]} '
          f'of {data["meta"]["repo_last_commit_date"]})')


def selftest():
    ok = True

    def check(name, cond, detail=''):
        nonlocal ok
        ok &= bool(cond)
        print(('  ok    ' if cond else '  FAIL  ') + f'{name:52} {detail}')

    d = json.loads(DERIVED.read_text(encoding='utf-8'))
    c, by = d['counts'], d['counts']['by_state']
    check('1221 problems in the derived table', c['total'] == 1221 == len(d['problems']), str(c['total']))
    check('states add up to the total', sum(by.values()) == c['total'], str(sum(by.values())))
    # the same figures STATISTICS.md printed on 24 Nov 2026 (commit 706c140)
    want = {'proved': 339, 'disproved': 144, 'solved': 104, 'open': 570, 'falsifiable': 29, 'verifiable': 9,
            'decidable': 8, 'not provable': 5, 'not disprovable': 9, 'independent': 4}
    check('per-state counts = STATISTICS.md (24 Nov 2026)', by == want, ' '.join(f'{k}:{v}' for k, v in by.items()))
    lb = d['counts']['lean_by_state']
    check('Lean-formalised solutions 184 / 97 / 35', (lb['proved'], lb['disproved'], lb['solved']) == (184, 97, 35))
    check('114 problems carry a prize', c['prize'] == 114, str(c['prize']))
    check('7 problems are "open (Lean)"', len(c['open_lean']) == 7, ' '.join(c['open_lean']))
    h = d['history']
    check('history ends at 1221 / 591 solved / 630 open', (h[-1]['total'], h[-1]['solved'], h[-1]['open']) == (1221, 591, 630),
          str(h[-1]))
    check('CSV "solved" = proved+disproved+solved+independent', 339 + 144 + 104 + 4 == h[-1]['solved'])
    check('CSV "open" = everything else', 1221 - 591 == h[-1]['open'])
    check('history dates ascending', [r['date'] for r in h] == sorted(r['date'] for r in h), f'{len(h)} weeks')
    w, s = d['wiki'], d['wiki_summary']
    check('538 wiki rows in 8 sections', len(w) == 538 and len(s) == 8, str({k: v['rows'] for k, v in s.items()}))
    oct25 = [e for e in w if e['sec'] == '2a' and e['ai'] == 'GPT-5' and e['date'].startswith('2025-10')]
    check('Oct 2025 GPT-5 literature search: 10 full + 10 partial',
          sum(e['color'] == 'full' for e in oct25) == 10 and sum(e['color'] == 'partial' for e in oct25) == 10, str(len(oct25)))
    p1026 = [e for e in w if e['p'] == '1026' and e['sec'] == '1b']
    check('#1026 in 1(b): Aristotle, 7 Dec 2025, Tidor–Wang–Yang',
          p1026 and p1026[0]['date'] == '2025-12-07' and 'Tidor' in p1026[0]['lit'])
    p333 = [e for e in w if e['p'] == '333' and e['sec'] == '1b']
    check('#333 in 1(b): literature Erdős & Newman (1977)', p333 and '1977' in p333[0]['lit'])
    p90 = [e for e in w if e['p'] == '90' and e['sec'] == '1a']
    check('#90 in 1(a): 20 May 2026, full', p90 and p90[0]['date'] == '2026-05-20' and p90[0]['color'] == 'full')
    check('every wiki row has a 4-digit year', all(e['date'][:4].isdigit() for e in w))
    # ---- maths of #1026
    import random
    rng = random.Random(1026)
    for n in (1, 2, 5, 8, 10):
        for _ in range(30):
            x = ec.random_piles(n, rng.random())
            b = ec.best_monotone(x)
            assert abs(max(b['A'], b['B']) - ec.brute_best(x)) < 1e-12
    check('DP best monotone sum = brute force (n <= 10, 150 runs)', True)
    worst_area, worst_ratio = 0.0, 9.0
    for n in (4, 9, 16, 25, 49, 100):
        for _ in range(40):
            x = ec.random_piles(n, rng.random())
            b = ec.best_monotone(x)
            worst_area = max(worst_area, ec.overlap(ec.squares(x)))
            assert sum(v * v for v in x) <= b['A'] * b['B'] + 1e-12
            worst_ratio = min(worst_ratio, max(b['A'], b['B']) * math.sqrt(n))
    check('squares never overlap (240 random splits)', worst_area == 0.0, f'max overlap {worst_area}')
    check('sum x^2 <= A*B and best >= 1/sqrt(n) (sum = 1)', worst_ratio >= 1 - 1e-12, f'min best*sqrt(n) = {worst_ratio:.4f}')
    for k in (2, 3, 4, 5):
        x = ec.alice(k, eps=1e-6)
        b = ec.best_monotone(x)
        best = max(b['A'], b['B'])
        assert len(set(x)) == len(x) and abs(sum(x) - 1) < 1e-12
        check(f"Alice's split k={k}: Bob gets ~1/{k}, never less", 1 / k <= best + 1e-12 and best - 1 / k < 1e-5,
              f'{best:.7f} vs 1/k = {1 / k:.7f}; runs of length {len(b["inc"])}/{len(b["dec"])}')
    x = ec.alice(3, eps=1e-3)
    check('k=3 order is 3 2 1 6 5 4 9 8 7', [sorted(x).index(v) + 1 for v in x] == [3, 2, 1, 6, 5, 4, 9, 8, 7])
    page = (HERE / 'erdos_page.html').read_text(encoding='utf-8')
    check('page template has 3 views and a data slot', all(f'id="{v}"' in page for v in 'abc') and '__DATA__' in page)
    check('page fetches nothing from erdosproblems.com', 'fetch(' not in page and 'XMLHttpRequest' not in page)
    print('selftest ok' if ok else 'selftest FAILED')
    return 0 if ok else 1


def serve(port=8770):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(HERE), **kw)  # noqa: E731
    with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as srv:
        print(f'open http://127.0.0.1:{port}/erdos_live.html   (Ctrl-C to stop)')
        srv.serve_forever()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--serve', action='store_true')
    ap.add_argument('--fetch', action='store_true', help='download again from GitHub (public, no key)')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    build(a.fetch)
    if a.serve:
        serve()
