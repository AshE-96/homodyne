#!/usr/bin/env python3
"""mislead_lab.py - HMD-014 / Benchmark E07: a correct table that still misleads.

ILLUSTRATIVE ONLY. No model was called. Every number below is either a fixed,
hand-built teaching count or comes from a seeded simulation in this file.

Sections
  1. One results table. Every cell is arithmetically correct.
  2. Four honest-looking headlines from that same table, two different winners.
  3. Penalty choice (E05): the k where the winner flips.
  4. Selective disclosure: test N private variants, publish only the best.
  5. Holdout: re-test the published variant on questions it never saw.
  6. Audit: zero errors found is not the same as "safe" (PASS / BREACH / UNKNOWN).

Usage
  python3 mislead_lab.py                 # seed 7 (numbers used in the script)
  python3 mislead_lab.py --seed 11       # stability check
  python3 mislead_lab.py --variants 20   # more private attempts
  python3 mislead_lab.py --selftest      # assertions, exits 0 on success

Python 3.8+, standard library only.
"""
import argparse
import math
import random
import sys

# ---------------------------------------------------------------- 1. the table
# 1,000 questions: 600 easy, 400 hard (same questions for both systems).
# answered = questions where the system gave an answer instead of "I don't know".
TABLE = {
    'A': {'easy': {'n': 600, 'answered': 600, 'correct': 570},
          'hard': {'n': 400, 'answered': 390, 'correct': 234}},
    'B': {'easy': {'n': 600, 'answered': 590, 'correct': 555},
          'hard': {'n': 400, 'answered': 60, 'correct': 33}},
}
SUBSETS = ('easy', 'hard')


def totals(model):
    rows = TABLE[model].values()
    n = sum(r['n'] for r in rows)
    answered = sum(r['answered'] for r in rows)
    correct = sum(r['correct'] for r in rows)
    return {'n': n, 'answered': answered, 'correct': correct,
            'wrong': answered - correct, 'abstain': n - answered}


def pct(x, y):
    return 100.0 * x / y


def precision(r):
    """Accuracy among answered questions (what many tables call 'accuracy')."""
    return pct(r['correct'], r['answered'])


def penalised(model, k):
    """Points per 100 questions with +1 right, 0 abstain, -k wrong (E05 rule)."""
    t = totals(model)
    return 100.0 * (t['correct'] - k * t['wrong']) / t['n']


def crossover_k():
    """k where A and B have the same penalised score."""
    a, b = totals('A'), totals('B')
    return (a['correct'] - b['correct']) / (a['wrong'] - b['wrong'])


def headlines():
    """Each headline is true. They do not agree on the winner."""
    a, b = totals('A'), totals('B')
    out = []
    pa, pb = precision(a), precision(b)
    out.append(('Accuracy on answered questions (all)', pa, pb, 'B' if pb > pa else 'A'))
    for s in SUBSETS:
        ra, rb = TABLE['A'][s], TABLE['B'][s]
        out.append((f'Accuracy on answered questions ({s} only)', precision(ra), precision(rb),
                    'A' if precision(ra) > precision(rb) else 'B'))
    ca, cb = pct(a['correct'], a['n']), pct(b['correct'], b['n'])
    out.append(('Correct out of ALL 1,000 questions', ca, cb, 'A' if ca > cb else 'B'))
    return out


# ------------------------------------------------- 4-5. best-of-N and holdout
def binom(rng, n, p):
    return sum(rng.random() < p for _ in range(n))


def best_of_n(seed, variants, n_test, true_acc, n_holdout, reps):
    rng = random.Random(seed)
    scores = [binom(rng, n_test, true_acc) for _ in range(variants)]
    best = max(range(variants), key=lambda i: scores[i])
    holdout = binom(rng, n_holdout, true_acc)
    # Expected inflation over many repetitions of the same game.
    inflation, fresh = [], []
    for _ in range(reps):
        inflation.append(max(binom(rng, n_test, true_acc) for _ in range(variants)) / n_test)
        fresh.append(binom(rng, n_holdout, true_acc) / n_holdout)
    return {'scores': [pct(s, n_test) for s in scores], 'best': best,
            'best_score': pct(scores[best], n_test),
            'mean_score': sum(pct(s, n_test) for s in scores) / variants,
            'holdout': pct(holdout, n_holdout),
            'avg_published': 100.0 * sum(inflation) / reps,
            'avg_holdout': 100.0 * sum(fresh) / reps}


# ---------------------------------------------------------------- 6. audit
def wilson(x, n, z=1.959963984540054):
    """Two-sided 95% Wilson interval for x successes in n trials."""
    if n == 0:
        return (0.0, 1.0)
    p = x / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def audit_status(errors, n, limit):
    lo, hi = wilson(errors, n)
    if hi <= limit:
        return 'PASS', lo, hi
    if lo > limit:
        return 'BREACH', lo, hi
    return 'UNKNOWN', lo, hi


def min_n_for_pass(limit):
    """Smallest n with zero observed errors whose Wilson upper bound <= limit."""
    n = 1
    while wilson(0, n)[1] > limit:
        n += 1
    return n


# ---------------------------------------------------------------- printing
def report(args):
    print('ILLUSTRATIVE - teaching numbers, no model was called.\n')
    print('1) ONE TABLE. Every cell is correct.')
    print(f'{"system":<7}{"subset":<7}{"questions":>10}{"answered":>10}{"correct":>9}{"wrong":>7}{"acc_answered":>14}')
    for m in TABLE:
        for s in SUBSETS:
            r = TABLE[m][s]
            print(f'{m:<7}{s:<7}{r["n"]:>10}{r["answered"]:>10}{r["correct"]:>9}'
                  f'{r["answered"] - r["correct"]:>7}{precision(r):>13.1f}%')
        t = totals(m)
        print(f'{m:<7}{"ALL":<7}{t["n"]:>10}{t["answered"]:>10}{t["correct"]:>9}'
              f'{t["wrong"]:>7}{precision(t):>13.1f}%')

    print('\n2) FOUR TRUE HEADLINES, SAME TABLE')
    for name, a, b, win in headlines():
        print(f'  {name:<42} A {a:5.1f}%  B {b:5.1f}%  -> winner {win}')
    a, b = totals('A'), totals('B')
    print(f'  Why: B answered {TABLE["B"]["hard"]["answered"]} of 400 hard questions, '
          f'A answered {TABLE["A"]["hard"]["answered"]}. '
          f'Hard share of answered: A {pct(TABLE["A"]["hard"]["answered"], a["answered"]):.0f}%, '
          f'B {pct(TABLE["B"]["hard"]["answered"], b["answered"]):.0f}%.')

    print('\n3) PENALTY CHOICE (+1 right, 0 abstain, -k wrong), points per 100 questions')
    for k in (0, 1, 2, 3):
        pa, pb = penalised('A', k), penalised('B', k)
        print(f'  k={k}:  A {pa:6.1f}   B {pb:6.1f}   -> winner {"A" if pa > pb else "B"}')
    print(f'  Winner flips at k = {crossover_k():.2f}')

    r = best_of_n(args.seed, args.variants, args.n_test, args.true_acc, args.n_holdout, args.reps)
    print(f'\n4) SELECTIVE DISCLOSURE: {args.variants} private variants, identical true accuracy '
          f'{100 * args.true_acc:.0f}%, {args.n_test} test questions each (seed {args.seed})')
    print('  private scores: ' + ' '.join(f'{s:.1f}' for s in r['scores']))
    print(f'  mean of all variants: {r["mean_score"]:.1f}%   published (best only): '
          f'variant #{r["best"] + 1} {r["best_score"]:.1f}%')
    print(f'  over {args.reps} repeats of this game, the published best averages '
          f'{r["avg_published"]:.1f}% (true {100 * args.true_acc:.0f}%)')

    print(f'\n5) HOLDOUT: re-test variant #{r["best"] + 1} on {args.n_holdout} fresh questions')
    print(f'  this run: published {r["best_score"]:.1f}%  ->  holdout {r["holdout"]:.1f}%  (true {100 * args.true_acc:.0f}%)')
    print(f'  over {args.reps} repeats: published best {r["avg_published"]:.1f}%  ->  holdout {r["avg_holdout"]:.1f}%')
    print('  one holdout of this size is noisy too; the average is the lesson.')

    print(f'\n6) AUDIT: invented answers on unanswerable questions, limit {100 * args.limit:.0f}% (design choice)')
    for errors, n in ((0, 2), (0, 20), (0, 100), (3, 20)):
        status, lo, hi = audit_status(errors, n, args.limit)
        print(f'  {errors} errors in {n:>3} checked -> 95% interval {100 * lo:4.1f}%..{100 * hi:5.1f}%  {status}')
    print(f'  zero errors needs n >= {min_n_for_pass(args.limit)} checked questions before PASS at '
          f'{100 * args.limit:.0f}%')


def selftest():
    a, b = totals('A'), totals('B')
    # Table is internally consistent.
    for m in TABLE:
        for s in SUBSETS:
            r = TABLE[m][s]
            assert 0 <= r['correct'] <= r['answered'] <= r['n']
    assert a['n'] == b['n'] == 1000
    # Simpson-style reversal: A wins every subset, B wins the pooled precision.
    for s in SUBSETS:
        assert precision(TABLE['A'][s]) > precision(TABLE['B'][s])
    assert precision(b) > precision(a)
    # Metric choice: correct-out-of-all favours A.
    assert a['correct'] > b['correct']
    # Penalty choice flips the winner between k=1 and k=3.
    assert penalised('A', 1) > penalised('B', 1)
    assert penalised('B', 3) > penalised('A', 3)
    assert 1 < crossover_k() < 3
    assert abs(penalised('A', crossover_k()) - penalised('B', crossover_k())) < 1e-9
    # Best-of-N is never below the mean; on average it inflates.
    r = best_of_n(7, 10, 200, 0.70, 200, 300)
    assert r['best_score'] >= r['mean_score']
    assert r['avg_published'] > 70.0 + 2.0
    assert abs(r['avg_holdout'] - 70.0) < 1.0
    assert r['avg_published'] - r['avg_holdout'] > 2.0
    # Wilson: known value for 0/20 upper bound = z^2/(n+z^2).
    z2 = 1.959963984540054 ** 2
    assert abs(wilson(0, 20)[1] - z2 / (20 + z2)) < 1e-12
    assert audit_status(0, 2, 0.05)[0] == 'UNKNOWN'
    assert audit_status(0, 20, 0.05)[0] == 'UNKNOWN'
    assert audit_status(0, 100, 0.05)[0] == 'PASS'
    assert audit_status(3, 20, 0.05)[0] == 'BREACH'
    assert wilson(0, min_n_for_pass(0.05))[1] <= 0.05 < wilson(0, min_n_for_pass(0.05) - 1)[1]
    print('selftest: OK (reversal, metric flip, penalty flip, best-of-N inflation, Wilson, audit states)')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--seed', type=int, default=7)
    p.add_argument('--variants', type=int, default=10)
    p.add_argument('--n-test', type=int, default=200)
    p.add_argument('--n-holdout', type=int, default=200)
    p.add_argument('--true-acc', type=float, default=0.70)
    p.add_argument('--reps', type=int, default=2000)
    p.add_argument('--limit', type=float, default=0.05)
    p.add_argument('--selftest', action='store_true')
    args = p.parse_args()
    if args.selftest:
        selftest()
        return 0
    report(args)
    return 0


if __name__ == '__main__':
    sys.exit(main())
