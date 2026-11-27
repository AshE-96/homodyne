#!/usr/bin/env python3
"""HMD-004 · real data behind beats 4, 5 and 11 (no network, no model calls).

  python3 -I artifact/real_data.py epoch   <benchmark_data.zip>       [--out artifact/derived]
  python3 -I artifact/real_data.py lmarena <text-full.parquet>        [--out artifact/derived]
  python3 -I artifact/real_data.py --selftest

epoch    Reads Epoch AI's benchmark ZIP (CC BY 4.0, https://epoch.ai/benchmarks/use-this-data)
         without extracting it and writes:
           epoch_profile.csv      the two models our rule picks, on four benchmarks (beat 5)
           epoch_summary.json     the rule, how many pairs pass it, and the OTIS Mock AIME
                                  saturation count (beat 11)
         The rule (ours): among models with a score and a standard error on GPQA Diamond,
         SimpleQA Verified and FrontierMath Tiers 1-3 (v2), keep ordered pairs (A, B) where
         A beats B on SimpleQA Verified by more than 3 combined standard errors and B beats A
         on FrontierMath by more than 3. Pick the pair whose GPQA Diamond scores are closest
         (ties: smaller combined GPQA standard error, then names).
lmarena  Reads LMArena's leaderboard archive (lmarena-ai/leaderboard-dataset, subset `text`,
         split `full`, CC BY 4.0) and writes lmarena_maverick_2025-04.json: every archived
         April-May 2025 `overall` row for Llama 4 Maverick, plus how many models each snapshot
         lists and whether the experimental variant appears at all (beat 4). Needs pyarrow.

Stdlib only, except pyarrow for the `lmarena` command.
"""
import argparse
import csv
import io
import itertools
import json
import math
import os
import sys
import tempfile
import zipfile

GPQA, SQA, FM, CHESS, OTIS = ('gpqa_diamond', 'simpleqa_verified', 'frontiermath_tiers_1_3_v2',
                              'chess_puzzles', 'otis_mock_aime_2024_2025')
PROFILE = [GPQA, SQA, FM, CHESS]
Z = 3.0
SINCE = '2026-07-01'


# ── Epoch ────────────────────────────────────────────────────────────────────

def load_bench(zf, name):
    """model version -> (mean_score, stderr or None, release date, organization)."""
    out = {}
    with zf.open(name + '.csv') as raw:
        for r in csv.DictReader(io.TextIOWrapper(raw, encoding='utf-8', newline='')):
            if not r.get('mean_score'):
                continue
            se = r.get('stderr') or ''
            out[r['Model version']] = (float(r['mean_score']), float(se) if se else None,
                                       r.get('Release date', ''), r.get('Organization', ''))
    return out


def zscore(data, bench, a, b):
    sa, ea = data[bench][a][0], data[bench][a][1]
    sb, eb = data[bench][b][0], data[bench][b][1]
    se = math.hypot(ea, eb)
    return (sa - sb) / se if se > 0 else 0.0


def select_pair(data):
    """Apply the rule in the module docstring. Returns (pair or None, n_models, n_pairs, n_pass)."""
    need = (GPQA, SQA, FM)
    models = sorted(m for m in set.intersection(*(set(data[b]) for b in need))
                    if all(data[b][m][1] is not None for b in need))
    passing = []
    for a, b in itertools.permutations(models, 2):
        if zscore(data, SQA, a, b) > Z and zscore(data, FM, a, b) < -Z:
            gap = abs(data[GPQA][a][0] - data[GPQA][b][0])
            se = math.hypot(data[GPQA][a][1], data[GPQA][b][1])
            passing.append((round(gap, 12), se, a, b))
    n_pairs = len(models) * (len(models) - 1) // 2
    if not passing:
        return None, len(models), n_pairs, 0
    passing.sort()
    return passing[0][2:], len(models), n_pairs, len(passing)


def saturation(otis, since=SINCE):
    scores = [(s, rel) for s, _, rel, _ in otis.values()]
    recent = [s for s, rel in scores if rel >= since]
    return {'benchmark': OTIS, 'models': len(scores), 'perfect': sum(1 for s, _ in scores if s == 1.0),
            'released_since': since, 'models_since': len(recent),
            'perfect_since': sum(1 for s in recent if s == 1.0)}


def run_epoch(zip_path, out_dir, quiet=False):
    with zipfile.ZipFile(zip_path) as zf:
        data = {b: load_bench(zf, b) for b in PROFILE + [OTIS]}
    pair, n_models, n_pairs, n_pass = select_pair(data)
    if pair is None:
        sys.exit('no pair passes the rule')
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'epoch_profile.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['benchmark', 'model_version', 'organization', 'release_date', 'mean_score_pct',
                    'stderr_pct', 'models_on_benchmark'])
        for b in PROFILE:
            for m in pair:
                if m in data[b]:
                    s, se, rel, org = data[b][m]
                    w.writerow([b, m, org, rel, f'{100 * s:.1f}', '' if se is None else f'{100 * se:.1f}',
                                len(data[b])])
    gaps = {b: round(100 * (data[b][pair[0]][0] - data[b][pair[1]][0]), 1)
            for b in PROFILE if pair[0] in data[b] and pair[1] in data[b]}
    summary = {
        'rule': ('ordered pairs (A,B) on GPQA Diamond + SimpleQA Verified + FrontierMath Tiers 1-3 v2 '
                 f'(score and stderr present): A ahead on SimpleQA Verified by > {Z:g} combined SE and '
                 f'B ahead on FrontierMath by > {Z:g}; pick the closest GPQA Diamond scores. Ours, not Epoch\'s.'),
        'models_with_all_three': n_models,
        'unordered_pairs': n_pairs,
        'pairs_passing_rule': n_pass,
        'selected': {'A': pair[0], 'B': pair[1]},
        'gap_A_minus_B_points': gaps,
        'z_A_minus_B': {b: round(zscore(data, b, *pair), 1) for b in (SQA, FM, CHESS)
                        if pair[0] in data[b] and pair[1] in data[b]
                        and data[b][pair[0]][1] is not None and data[b][pair[1]][1] is not None},
        'saturation': saturation(data[OTIS]),
    }
    with open(os.path.join(out_dir, 'epoch_summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write('\n')
    if not quiet:
        print(json.dumps(summary, indent=2, ensure_ascii=False))


# ── LMArena ──────────────────────────────────────────────────────────────────

def maverick_rows(rows):
    """rows: dicts with model_name, category, leaderboard_publish_date, rating, rating_lower,
    rating_upper, rank. Returns the archive summary for April-May 2025, category overall."""
    window = [r for r in rows if r['category'] == 'overall'
              and '2025-04-01' <= r['leaderboard_publish_date'] <= '2025-05-31']
    listed, top = {}, {}
    for r in window:
        d = r['leaderboard_publish_date']
        listed[d] = listed.get(d, 0) + 1
        if d not in top or r['rating'] > top[d]['rating']:
            top[d] = r
    mav = sorted((r for r in window if 'maverick' in r['model_name'].lower()),
                 key=lambda r: (r['leaderboard_publish_date'], r['model_name']))
    experimental = sum(1 for r in rows if 'experimental' in r['model_name'].lower()
                       and 'maverick' in r['model_name'].lower())
    return {
        'category': 'overall',
        'experimental_maverick_rows_in_whole_archive': experimental,
        'snapshots': [{'date': d, 'models_listed': listed[d], 'top_model': top[d]['model_name'],
                       'top_rating': round(top[d]['rating'], 1)} for d in sorted(listed)],
        'maverick': [{'date': r['leaderboard_publish_date'], 'model': r['model_name'],
                      'rating': round(r['rating'], 1), 'rating_lower': round(r['rating_lower'], 1),
                      'rating_upper': round(r['rating_upper'], 1), 'rank': int(r['rank']),
                      'models_listed': listed[r['leaderboard_publish_date']]} for r in mav],
        'note': ('The archive is the leaderboard as LMArena publishes it today; models removed later '
                 'are absent from old snapshots, so archived ranks can differ from ranks shown on the day.'),
    }


def run_lmarena(parquet_path, out_dir):
    try:
        import pyarrow.parquet as pq
    except ImportError:
        sys.exit('the lmarena command needs pyarrow')
    cols = ['model_name', 'category', 'leaderboard_publish_date', 'rating', 'rating_lower', 'rating_upper', 'rank']
    rows = pq.read_table(parquet_path, columns=cols).to_pylist()
    summary = maverick_rows(rows)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'lmarena_maverick_2025-04.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(json.dumps(summary, indent=2, ensure_ascii=False))


# ── self-test (offline, synthetic data, < 1 s) ───────────────────────────────

HEADER = 'Model version,mean_score,Best score (across scorers),Release date,Organization,stderr\n'


def _zip(path, tables):
    with zipfile.ZipFile(path, 'w') as zf:
        for name, rows in tables.items():
            zf.writestr(name + '.csv', HEADER + ''.join(f'{m},{s},{s},{rel},Org{m[0]},{se}\n'
                                                        for m, s, rel, se in rows))


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        z = os.path.join(tmp, 'b.zip')
        _zip(z, {
            GPQA: [('alpha', 0.90, '2026-08-01', 0.01), ('beta', 0.90, '2026-09-01', 0.01),
                   ('gamma', 0.95, '2026-01-01', 0.01), ('delta', 0.80, '2026-01-01', '')],
            SQA: [('alpha', 0.50, '2026-08-01', 0.01), ('beta', 0.20, '2026-09-01', 0.01),
                  ('gamma', 0.10, '2026-01-01', 0.01), ('delta', 0.90, '2026-01-01', 0.01)],
            FM: [('alpha', 0.40, '2026-08-01', 0.02), ('beta', 0.80, '2026-09-01', 0.02),
                 ('gamma', 0.90, '2026-01-01', 0.02), ('delta', 0.10, '2026-01-01', 0.02)],
            CHESS: [('alpha', 0.2, '2026-08-01', 0.04), ('beta', 0.6, '2026-09-01', 0.05)],
            OTIS: [('alpha', 1.0, '2026-08-01', 0.0), ('beta', 0.98, '2026-09-01', 0.01),
                   ('gamma', 1.0, '2026-01-01', 0.0)],
        })
        with zipfile.ZipFile(z) as zf:
            data = {b: load_bench(zf, b) for b in PROFILE + [OTIS]}
        pair, n_models, n_pairs, n_pass = select_pair(data)
        assert n_models == 3, n_models            # delta has no GPQA stderr
        assert n_pairs == 3, n_pairs
        assert pair == ('alpha', 'beta'), pair    # equal GPQA beats gamma's 5-point gap
        assert n_pass == 3, n_pass                # (alpha,beta) (alpha,gamma) (beta,gamma)
        sat = saturation(data[OTIS])
        assert (sat['models'], sat['perfect'], sat['models_since'], sat['perfect_since']) == (3, 2, 2, 1), sat
        out = os.path.join(tmp, 'out')
        run_epoch(z, out, quiet=True)
        with open(os.path.join(out, 'epoch_profile.csv'), encoding='utf-8') as f:
            prof = list(csv.DictReader(f))
        assert [(r['benchmark'], r['model_version']) for r in prof][:2] == [(GPQA, 'alpha'), (GPQA, 'beta')]
        assert len(prof) == 8 and prof[-1]['mean_score_pct'] == '60.0', prof[-1]
        with open(os.path.join(out, 'epoch_summary.json'), encoding='utf-8') as f:
            assert json.load(f)['gap_A_minus_B_points'][SQA] == 30.0
        rows = [dict(model_name=m, category=c, leaderboard_publish_date=d, rating=r, rating_lower=r - 5,
                     rating_upper=r + 5, rank=k)
                for m, c, d, r, k in [('top', 'overall', '2025-04-09', 1400.0, 1),
                                      ('llama-4-maverick-x', 'overall', '2025-04-09', 1270.0, 2),
                                      ('llama-4-maverick-x', 'coding', '2025-04-09', 1300.0, 1),
                                      ('old', 'overall', '2024-08-28', 1200.0, 1)]]
        s = maverick_rows(rows)
        assert s['experimental_maverick_rows_in_whole_archive'] == 0
        assert s['snapshots'] == [{'date': '2025-04-09', 'models_listed': 2, 'top_model': 'top', 'top_rating': 1400.0}]
        assert s['maverick'][0]['rank'] == 2 and s['maverick'][0]['models_listed'] == 2
    print('selftest ok')


def main():
    if '--selftest' in sys.argv[1:]:
        selftest()
        return
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('command', choices=['epoch', 'lmarena'])
    ap.add_argument('path')
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'derived'))
    a = ap.parse_args()
    (run_epoch if a.command == 'epoch' else run_lmarena)(a.path, a.out)


if __name__ == '__main__':
    main()
