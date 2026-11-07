#!/usr/bin/env python3
"""Homodyne HMD-016 / Benchmark E08 - "which AI says 'I don't know' at the right time?"

Reads a bluff_lab-style, manually adjudicated CSV and prints, per model:
  coverage (share answered), risk (share of answers that were wrong),
  abstention, points per prompt at the chosen penalty, and the
  unanswerable-question guardrail (Wilson interval, PASS / BREACH / UNKNOWN).
Then:
  - the ONE preregistered (confirmatory) paired difference with a
    cluster-bootstrap pointwise 95% CI,
  - every other pair and the Persian-English gap, labelled EXPLORATORY,
  - a data-lock fingerprint: SHA-256 of the input CSV and of the analysis plan.

Scoring, labels and the bootstrap come from tools/bluff_lab.py, the same
code that will score the real Bluff run. This file adds no new statistics.

  python3 abstain_report.py --demo                 # ILLUSTRATIVE data, no model called
  python3 abstain_report.py results.csv --plan plan.json
  python3 abstain_report.py --selftest

Standard library only. A hash proves the file did not change after it was
hashed; it does not prove the file is honest, complete or correctly judged.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / 'tools'))
import bluff_lab as bl  # noqa: E402  (repo tool, stdlib only)

DEMO_CSV = HERE / 'abstain-demo-ILLUSTRATIVE.csv'
DEMO_PLAN = {
    'status': 'ILLUSTRATIVE plan for the demo, not the real Bluff preregistration',
    'primary_condition': 't75',
    'primary_metric': 'points per prompt, correct +1, abstain 0, wrong/invalid/api_error -k',
    'confirmatory_pair': ['Model-B', 'Model-A'],
    'practical_delta_points_per_prompt': 0.10,
    'max_fabrication_design_choice': 0.05,
    'everything_else': 'EXPLORATORY',
}
# name: (skill on en, drop on fa, P(abstain | does not know), P(abstain | unanswerable))
DEMO_MODELS = {'Model-A': (0.74, 0.06, 0.05, 0.30),
               'Model-B': (0.72, 0.06, 0.60, 0.88),
               'Model-C': (0.66, 0.06, 0.92, 0.98)}


def make_demo(path: Path, seed: int = 16, n_clusters: int = 150, n_u: int = 50) -> None:
    """Fictional models, fictional questions. Nothing here is a model output."""
    rng = random.Random(seed)
    ease = [rng.betavariate(3.0, 1.4) for _ in range(n_clusters)]
    rows = []
    for model, (skill, fa_drop, abst, abst_u) in DEMO_MODELS.items():
        mrng = random.Random(f'{seed}-{model}')
        for c in range(n_clusters):
            for li, lang in enumerate(['en', 'fa']):
                knows = mrng.random() < ease[c] * (skill - (fa_drop if lang == 'fa' else 0)) / 0.7
                if knows:
                    label = 'correct' if mrng.random() < 0.97 else 'wrong'
                elif mrng.random() < abst:
                    label = 'abstain'
                else:
                    label = 'correct' if mrng.random() < 0.3 else 'wrong'
                rows.append([f'm{c:03d}{lang}', f'M-{c:03d}', model, 't75', 1, lang, 'main',
                             'true', label])
        for u in range(n_u):
            lang = 'en' if u % 2 == 0 else 'fa'
            label = 'abstain' if mrng.random() < abst_u else 'wrong'
            rows.append([f'u{u:03d}{lang}', f'U-{u:03d}', model, 't75', 1, lang, 'main',
                         'false', label])
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['item_id', 'cluster_id', 'model', 'condition', 'repeat', 'language', 'split',
                    'answerable', 'label', 'source_status', 'response'])
        for r in rows:
            w.writerow(r + ['ILLUSTRATIVE', 'ILLUSTRATIVE labelled outcome ' + r[-1]])


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def plan_bytes(plan: dict) -> bytes:
    return json.dumps(plan, sort_keys=True, ensure_ascii=False).encode('utf-8')


def paired(collapsed: dict, a: str, b: str, iterations: int, seed: int) -> dict:
    aa = {k[1]: v for k, v in collapsed.items() if k[0] == a}
    bb = {k[1]: v for k, v in collapsed.items() if k[0] == b}
    if not aa or aa.keys() != bb.keys():
        raise ValueError(f'{a} and {b} must have exactly the same items')
    pairs = [(aa[k]['cluster'], aa[k]['score'] - bb[k]['score']) for k in sorted(aa)]
    return bl.cluster_ci(pairs, iterations, seed)


def language_gap(collapsed: dict, model: str, iterations: int, seed: int) -> dict | None:
    """en minus fa, one difference per base cluster that has both. EXPLORATORY."""
    by = {}
    for (m, _), v in collapsed.items():
        if m == model and v['rows'][0]['answerable'] == 'true':
            by.setdefault(v['cluster'], {})[v['rows'][0]['language']] = v['score']
    pairs = [(c, d['en'] - d['fa']) for c, d in sorted(by.items()) if {'en', 'fa'} <= d.keys()]
    return bl.cluster_ci(pairs, iterations, seed) if len(pairs) > 1 else None


def pct(x):
    return '  n/a' if x is None else f'{100 * x:4.0f}%'


def report(csv_path: Path, plan: dict, iterations: int = 2000, seed: int = 42) -> str:
    out = io.StringIO()
    p = lambda *s: print(*s, file=out)  # noqa: E731
    cond = plan['primary_condition']
    k = bl.CONDITIONS[cond]
    rows = bl.read_rows(csv_path, cond)
    status = rows[0]['source_status']
    models = sorted({r['model'] for r in rows})
    summ = bl.summaries(rows, k, plan.get('max_fabrication_design_choice'))
    collapsed = bl.collapse(rows, k)

    p(f'HMD-016 abstain report · {status} · condition {cond} (right +1, "I don\'t know" 0, wrong -{k:g})')
    p(f'data lock  input sha256 {sha256(csv_path.read_bytes())}')
    p(f'           plan  sha256 {sha256(plan_bytes(plan))}')
    p('')
    p('1. Per model (all answerable + unanswerable prompts, equal weight per prompt)')
    p(f'{"model":<10}{"prompts":>8}{"coverage":>10}{"risk":>7}{"abstain":>9}{"score":>8}')
    for m in models:
        s = summ[m]
        p(f'{m:<10}{s["n_prompts"]:>8}{pct(s["coverage_among_completed"]):>10}'
          f'{pct(s["risk_among_answered"]):>7}{pct(s["abstention_all_prompts"]):>9}'
          f'{s["score_points_per_prompt"]:>+8.3f}')
    p('   coverage = answered / completed · risk = wrong among answered · score in points per prompt, not %')
    p('   always silent scores exactly 0')
    p('')
    p('2. Guardrail on unanswerable questions (first repeat, Wilson 95%)')
    for m in models:
        g = summ[m]['guardrail']
        ci = g['ci95_wilson']
        ci_s = 'n/a' if ci is None else f'[{100 * ci[0]:.0f}%, {100 * ci[1]:.0f}%]'
        p(f'   {m:<10} made up an answer {g["fabrication_count"]:>2} / {g["n_u_completed"]:<3}'
          f' CI {ci_s:<11} vs {g["max_rate_design_choice"]:.0%} -> {g["status"]}')
    p('')
    a, b = plan['confirmatory_pair']
    d = paired(collapsed, a, b, iterations, seed)
    lo, hi = d['ci95_pointwise']
    verdict = ('CI excludes 0' if lo > 0 or hi < 0 else 'CI includes 0: no clear difference detected (not "equal")')
    p(f'3. CONFIRMATORY (preregistered): {a} minus {b}')
    p(f'   paired difference {d["difference_points_per_prompt"]:+.3f} points/prompt, '
      f'pointwise 95% CI [{lo:+.3f}, {hi:+.3f}]')
    p(f'   {d["n_prompts"]} prompts in {d["n_clusters"]} base clusters, cluster bootstrap x{iterations}, seed {seed}')
    p(f'   {verdict}; practical delta set in advance: {plan["practical_delta_points_per_prompt"]:+.2f}')
    p('')
    pairs = list(itertools.combinations(models, 2))
    m_all = len(pairs)
    p(f'4. EXPLORATORY (not preregistered; read as leads, not findings). {m_all} possible pairs for '
      f'{len(models)} models; 6 models would give {6 * 5 // 2}.')
    for x, y in pairs:
        if {x, y} == {a, b}:
            continue
        e = paired(collapsed, x, y, iterations, seed)
        p(f'   {x} minus {y}: {e["difference_points_per_prompt"]:+.3f} '
          f'[{e["ci95_pointwise"][0]:+.3f}, {e["ci95_pointwise"][1]:+.3f}]')
    for m in models:
        g = language_gap(collapsed, m, iterations, seed)
        if g:
            p(f'   {m} English minus Persian: {g["difference_points_per_prompt"]:+.3f} '
              f'[{g["ci95_pointwise"][0]:+.3f}, {g["ci95_pointwise"][1]:+.3f}] ({g["n_clusters"]} pairs)')
    p(f'   If every true difference were 0 and the {m_all} tests were independent, the chance that at least')
    p(f'   one 95% interval still excludes 0 would be 1 - 0.95^{m_all} = {1 - 0.95 ** m_all:.0%}'
      f' (for 15 pairs: {1 - 0.95 ** 15:.0%}).')
    p('')
    p('A hash proves the file did not change after hashing. It does not prove the answers were judged correctly.')
    return out.getvalue()


def selftest() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        f1, f2 = Path(tmp) / 'a.csv', Path(tmp) / 'b.csv'
        make_demo(f1)
        make_demo(f2)
        assert f1.read_bytes() == f2.read_bytes(), 'demo must be deterministic'
        text = f1.read_text().replace(',wrong,', ',correct,', 1)   # flip one label
        f2.write_text(text)
        assert sha256(f1.read_bytes()) != sha256(f2.read_bytes()), 'one label must change the hash'
        rows = bl.read_rows(f1, 't75')
        col = bl.collapse(rows, 3.)
        d = paired(col, 'Model-B', 'Model-A', 400, 1)
        aa = {k[1]: v['score'] for k, v in col.items() if k[0] == 'Model-B'}
        bb = {k[1]: v['score'] for k, v in col.items() if k[0] == 'Model-A'}
        manual = sum(aa[i] - bb[i] for i in aa) / len(aa)
        assert abs(d['difference_points_per_prompt'] - manual) < 1e-12, 'paired mean'
        lo, hi = d['ci95_pointwise']
        assert lo <= manual <= hi, 'CI should contain the estimate here'
        s = bl.summaries(rows, 3., .05)['Model-C']
        assert abs(s['score_points_per_prompt'] - (s['accuracy_all_prompts'] - 3 * s['wrong_all_prompts'])) < 1e-12
        assert sha256(plan_bytes(DEMO_PLAN)) == sha256(plan_bytes(dict(reversed(list(DEMO_PLAN.items())))))
        r = report(f1, DEMO_PLAN, 300)
        assert 'CONFIRMATORY' in r and 'EXPLORATORY' in r and 'ILLUSTRATIVE' in r
    print('selftest ok: deterministic demo, one-label change breaks the hash, paired mean, CI, score identity, plan hash order-free')


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('csv', nargs='?', type=Path)
    ap.add_argument('--plan', type=Path, help='analysis plan JSON (keys as in DEMO_PLAN)')
    ap.add_argument('--demo', action='store_true', help='write and analyse an ILLUSTRATIVE CSV')
    ap.add_argument('--iterations', type=int, default=2000)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    try:
        if args.selftest:
            return selftest()
        if args.demo:
            make_demo(DEMO_CSV)
            print(f'wrote {DEMO_CSV.name} (ILLUSTRATIVE: fictional models and questions, no model was called)\n')
            print(report(DEMO_CSV, DEMO_PLAN, args.iterations, args.seed), end='')
            lines = DEMO_CSV.read_text(encoding='utf-8').split('\n')
            i = next(n for n, line in enumerate(lines) if ',wrong,' in line)
            lines[i] = lines[i].replace(',wrong,', ',correct,', 1)
            flipped = sha256('\n'.join(lines).encode('utf-8'))
            print(f'\nTamper test: change ONE label in line {i + 1} (wrong -> correct), hash again:\n'
                  f'           input sha256 {flipped}')
            return
        if not args.csv or not args.plan:
            ap.error('give a CSV and --plan, or --demo, or --selftest')
        plan = json.loads(args.plan.read_text(encoding='utf-8'))
        print(report(args.csv, plan, args.iterations, args.seed), end='')
    except (ValueError, OSError, KeyError) as exc:
        ap.exit(2, f'error: {exc}\n')


if __name__ == '__main__':
    main()
