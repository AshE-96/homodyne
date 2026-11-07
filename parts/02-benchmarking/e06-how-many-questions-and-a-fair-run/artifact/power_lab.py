#!/usr/bin/env python3
"""Homodyne HMD-012 / Benchmark E06 - "we tested it a thousand times; can we trust it now?"

How many questions does a model comparison need, and what do repeats and
question clusters do to that number?  Paired comparison of two models A and B
on the SAME questions.  Per question the paired difference d is
  +1  A right, B wrong      (probability p10)
  -1  A wrong, B right      (probability p01)
   0  both right or both wrong
discordant rate = p10 + p01 (how often the two models disagree);
true difference delta = p10 - p01 (in accuracy points).

Sections
  1. Card et al. 2020, appendix C scenario (500 vs 2000 questions, delta = 2 points,
     90% agreement): analytic power + seeded simulation with an exact McNemar test.
  2. Minimum Detectable Effect (MDE) table: questions x discordant rate.
     Check against Miller 2024 (arXiv 2411.00640) sec. 5: 3 points needs ~969 questions.
  3. Paired vs unpaired on the same questions; repeats (Miller sec. 5: n = 198,
     K = 1 -> 10 repeats moves the MDE from 13.2% to 7.5%).
  4. Clusters: 1,000 rows as 1000x1, 250x4 or 50x20 (question x variants/repeats)
     with an intra-cluster correlation (ICC). Design effect, effective n, MDE, and
     a seeded simulation of how often a NAIVE test vs a CLUSTERED test declares a
     winner when there is NO real difference, and power for a small real one.
  5. Many comparisons: 6 models = 15 pairs; chance of at least one false "winner".

Everything here is a SCENARIO with assumed rates: ILLUSTRATIVE.  No model was
called.  Normal approximation, two-sided alpha = 0.05, power = 0.80 unless stated.

Standard library only.
  python3 power_lab.py                 # all sections (seed 12, 2000 reps)
  python3 power_lab.py --reps 500      # faster, noisier
  python3 power_lab.py --selftest      # checks the formulas against the papers
"""
from __future__ import annotations

import argparse
import math
import random
import sys

STATUS = "ILLUSTRATIVE (assumed rates, simulated data; no model was called)"
Z_A = 1.959963984540054      # two-sided alpha 0.05
Z_B = 0.8416212335729143     # power 0.80
ZSUM = Z_A + Z_B


def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


# ---------------------------------------------------------------- analytic

def paired_sd(p10: float, p01: float) -> float:
    """SD of one question's paired difference d in {-1, 0, +1}."""
    mean = p10 - p01
    return math.sqrt(p10 + p01 - mean * mean)


def split(discordant: float, delta: float) -> tuple[float, float]:
    p10, p01 = (discordant + delta) / 2, (discordant - delta) / 2
    if p01 < 0 or p10 > 1:
        raise ValueError("delta cannot exceed the discordant rate")
    return p10, p01


def mde(n_eff: float, sd: float) -> float:
    return ZSUM * sd / math.sqrt(n_eff)


def power(n_eff: float, sd: float, delta: float) -> float:
    return phi(abs(delta) / (sd / math.sqrt(n_eff)) - Z_A)


def n_needed(sd: float, delta: float) -> int:
    return math.ceil((ZSUM * sd / delta) ** 2)


def design_effect(m: int, icc: float) -> float:
    return 1 + (m - 1) * icc


# ---------------------------------------------------------------- exact McNemar

_crit: dict[int, int] = {}


def mcnemar_lower_crit(m: int, alpha: float = 0.05) -> int:
    """Largest k with two-sided exact p-value <= alpha when min(b, c) = k (-1 if none)."""
    if m not in _crit:
        k, cdf, best = 0, 0.0, -1
        denom = 2 ** m
        while k <= m // 2:
            cdf += math.comb(m, k) / denom
            if min(1.0, 2 * cdf) <= alpha:
                best = k
                k += 1
            else:
                break
        _crit[m] = best
    return _crit[m]


def mcnemar_significant(b: int, c: int) -> bool:
    return min(b, c) <= mcnemar_lower_crit(b + c)


def simulate_mcnemar(n: int, p10: float, p01: float, reps: int, rng: random.Random):
    hits, sig_effects = 0, []
    for _ in range(reps):
        b = c = 0
        for _ in range(n):
            u = rng.random()
            if u < p10:
                b += 1
            elif u < p10 + p01:
                c += 1
        if mcnemar_significant(b, c):
            hits += 1
            sig_effects.append(abs(b - c) / n)
    type_m = (sum(sig_effects) / len(sig_effects)) / (p10 - p01) if sig_effects and p10 != p01 else float("nan")
    return hits / reps, type_m


# ---------------------------------------------------------------- clusters

def draw_d(u: float, p10: float, p01: float) -> int:
    return 1 if u < p10 else (-1 if u < p10 + p01 else 0)


def simulate_clusters(k: int, m: int, icc: float, p10: float, p01: float,
                      reps: int, rng: random.Random) -> tuple[float, float]:
    """Share of runs where |z| > 1.96 with a naive SE and with a clustered SE.

    Each item copies its cluster's outcome with probability sqrt(icc), otherwise
    draws a fresh outcome, so the intra-cluster correlation of d is icc.
    """
    s = math.sqrt(icc)
    n = k * m
    naive_hits = clus_hits = 0
    for _ in range(reps):
        sums, total, sq = [], 0, 0
        for _ in range(k):
            base = draw_d(rng.random(), p10, p01)
            cs = 0
            for _ in range(m):
                d = base if rng.random() < s else draw_d(rng.random(), p10, p01)
                cs += d
                sq += d * d
            sums.append(cs)
            total += cs
        mean = total / n
        var = (sq - n * mean * mean) / (n - 1)
        se_naive = math.sqrt(var / n) if var > 0 else 0.0
        se_clus = math.sqrt(sum((cs - m * mean) ** 2 for cs in sums)) / n
        if se_naive > 0 and abs(mean) / se_naive > Z_A:
            naive_hits += 1
        if se_clus > 0 and abs(mean) / se_clus > Z_A:
            clus_hits += 1
    return naive_hits / reps, clus_hits / reps


# ---------------------------------------------------------------- report

def pct(x: float, digits: int = 1) -> str:
    return f"{100 * x:.{digits}f}%"


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=12)
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--icc", type=float, default=0.5, help="intra-cluster correlation for section 4")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        sys.exit(selftest())
    rng = random.Random(a.seed)
    print(f"# {STATUS}")
    print(f"# seed {a.seed} · {a.reps} simulated runs per cell · alpha 0.05 two-sided · power target 0.80\n")

    # 1 ---------------------------------------------------------------
    print("1) CARD ET AL. 2020, APPENDIX C SCENARIO  (true difference 2 points, models agree on 90%)")
    p10, p01 = split(0.10, 0.02)
    sd = paired_sd(p10, p01)
    print(f"   p(A right, B wrong) = {p10:.2f} · p(A wrong, B right) = {p01:.2f}")
    print("   questions  analytic power  simulated power (exact McNemar)  exaggeration when 'significant'")
    for n in (500, 2000):
        sim, tm = simulate_mcnemar(n, p10, p01, a.reps, rng)
        print(f"   {n:>9}  {pct(power(n, sd, 0.02), 0):>14}  {pct(sim, 0):>31}  x{tm:.1f}")
    print("   paper reports: n=500 power ~0.25, exaggeration x1.9 · n=2000 'nearly 80%', x1.1\n")

    # 2 ---------------------------------------------------------------
    print("2) MINIMUM DETECTABLE EFFECT (accuracy points; 80% power, alpha 0.05, paired, independent questions)")
    rates = (0.05, 0.10, 0.20, 0.30)
    print("   questions " + "".join(f"  disagree {int(r*100):>2}%" for r in rates))
    for n in (100, 250, 500, 1000, 2000, 4000):
        print(f"   {n:>9} " + "".join(f"  {100*mde(n, math.sqrt(r)):>10.1f} pt" for r in rates))
    print("   (SD of d = sqrt(disagreement rate): exact when the true gap is 0, close for small gaps)")
    print(f"   Miller 2024 check: omega^2 = 1/9, delta = 0.03 -> n = {n_needed(math.sqrt(1/9), 0.03)} questions (paper: ~969)\n")

    # 3 ---------------------------------------------------------------
    print("3) PAIRED vs UNPAIRED, and REPEATS")
    pa, pb = 0.72, 0.70
    p10, p01 = split(0.10, pa - pb)
    sd_p = paired_sd(p10, p01)
    sd_u = math.sqrt(pa * (1 - pa) + pb * (1 - pb))
    print(f"   same 500 questions, accuracy A {pct(pa,0)} vs B {pct(pb,0)}, disagree on 10%:")
    print(f"     unpaired (compare two totals)   MDE {100*mde(500, sd_u):.1f} pt")
    print(f"     paired   (question by question) MDE {100*mde(500, sd_p):.1f} pt")
    w2, s2 = 1 / 9, 1 / 6
    for K in (1, 2, 10, 100):
        d = ZSUM * math.sqrt(w2 + 2 * s2 / K) / math.sqrt(198)
        print(f"   Miller sec. 5: 198 questions, each answered K={K:<3} times -> MDE {pct(d)}")
    print("   (paper, rounded: 13.2% at K=1, 7.5% at K=10)")
    print(f"   ceiling with infinite repeats: {pct(ZSUM*math.sqrt(w2)/math.sqrt(198))} (repeats cannot replace questions)\n")

    # 4 ---------------------------------------------------------------
    icc = a.icc
    print(f"4) THE SAME 1,000 ROWS, THREE SHAPES  (ICC = {icc} inside a cluster; models disagree on 10% of rows)")
    print("   shape      design effect  effective n  MDE (clustered)  NO real difference:  naive 'winner'  clustered 'winner'   real 3-pt gap: clustered power")
    p10_0, p01_0 = split(0.10, 0.0)
    p10_3, p01_3 = split(0.10, 0.03)
    for k, m in ((1000, 1), (250, 4), (50, 20)):
        de = design_effect(m, icc)
        neff = 1000 / de
        null_naive, null_clus = simulate_clusters(k, m, icc, p10_0, p01_0, a.reps, rng)
        _, alt_clus = simulate_clusters(k, m, icc, p10_3, p01_3, a.reps, rng)
        print(f"   {k:>4} x {m:<3}  {de:>13.2f}  {neff:>11.0f}  {100*mde(neff, math.sqrt(0.10)):>12.1f} pt"
              f"  {'':>19}{pct(null_naive):>14}  {pct(null_clus):>18}  {pct(alt_clus):>30}")
    print("   naive = treats all 1,000 rows as independent; clustered = Miller eq. 8 (sum within cluster first).")
    print("   With only 50 clusters a z-test is slightly liberal; a t or bootstrap test is safer.\n")
    # 5 ---------------------------------------------------------------
    print("5) MANY COMPARISONS  (6 models -> 15 pairs; no real difference anywhere; tests treated as independent)")
    pairs = math.comb(6, 2)
    print(f"   pairs = {pairs} · chance at least one pair looks 'significant' at 5% = {pct(1 - 0.95 ** pairs)}")
    print("   (pairs share models, so they are not independent; the point is the order of magnitude)\n")
    print("Not shown: real model behaviour, real disagreement rates, real ICCs. Measure them in a pilot.")


# ---------------------------------------------------------------- self-test

def selftest() -> int:
    checks = []
    checks.append(("Miller sec.5 n for delta .03, omega^2 1/9 == 969",
                   n_needed(math.sqrt(1 / 9), 0.03) == 969))
    d1 = ZSUM * math.sqrt(1 / 9 + 2 / 6) / math.sqrt(198)
    d10 = ZSUM * math.sqrt(1 / 9 + 2 / 60) / math.sqrt(198)
    checks.append(("Miller sec.5 MDE K=1 matches paper 13.2% (within 0.1 pt)", abs(100 * d1 - 13.2) < 0.1))
    checks.append(("Miller sec.5 MDE K=10 matches paper 7.5% (within 0.1 pt)", abs(100 * d10 - 7.5) < 0.1))
    p10, p01 = split(0.10, 0.02)
    checks.append(("split(0.10, 0.02) == (0.06, 0.04)", abs(p10 - 0.06) < 1e-12 and abs(p01 - 0.04) < 1e-12))
    sd = paired_sd(p10, p01)
    checks.append(("paired SD = sqrt(0.10 - 0.0004)", abs(sd - math.sqrt(0.0996)) < 1e-12))
    checks.append(("analytic power n=2000 within 0.75-0.85 (paper: nearly 80%)", 0.75 < power(2000, sd, 0.02) < 0.85))
    checks.append(("analytic power n=500 within 0.20-0.35 (paper: ~0.25)", 0.20 < power(500, sd, 0.02) < 0.35))
    checks.append(("exact McNemar: 0 vs 6 discordant is significant", mcnemar_significant(0, 6)))
    checks.append(("exact McNemar: 0 vs 5 discordant is not (p = 0.0625)", not mcnemar_significant(0, 5)))
    checks.append(("exact McNemar: 10 vs 10 is not significant", not mcnemar_significant(10, 10)))
    checks.append(("design effect m=4, icc .5 == 2.5", design_effect(4, 0.5) == 2.5))
    checks.append(("15 pairs: P(at least one false winner) = 53.7%", round(100 * (1 - 0.95 ** math.comb(6, 2)), 1) == 53.7))
    checks.append(("design effect m=1 == 1", design_effect(1, 0.9) == 1))
    rng = random.Random(1)
    naive, clus = simulate_clusters(50, 20, 0.5, 0.05, 0.05, 300, rng)
    checks.append(("null, 50x20, icc .5: naive false-winner rate > clustered", naive > clus))
    checks.append(("null, 50x20, icc .5: naive false-winner rate > 20%", naive > 0.20))
    rng = random.Random(2)
    naive1, clus1 = simulate_clusters(1000, 1, 0.5, 0.05, 0.05, 300, rng)
    checks.append(("null, 1000x1: both rates near 5% (2-10%)", 0.02 < naive1 < 0.10 and 0.02 < clus1 < 0.10))
    failed = 0
    for name, ok in checks:
        print(("ok   " if ok else "FAIL ") + name)
        failed += not ok
    print(f"\n{len(checks) - failed}/{len(checks)} checks pass")
    return 1 if failed else 0


if __name__ == "__main__":
    main()
