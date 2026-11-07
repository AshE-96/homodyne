#!/usr/bin/env python3
"""Homodyne HMD-010 / Benchmark E05 - "can negative marking make an AI more cautious?"

Scoring rule used throughout: correct +1, "I don't know" 0, wrong -k.
Answering pays on average only if P(correct) > t, where t = k / (k + 1).

Parts:
  1. threshold table, including the Konkur-style rule (+3 / -1 == +1 / -1/3)
  2. Konkur arithmetic for a 4-option question: blind guess vs. eliminating options
  3. ILLUSTRATIVE simulation: a calibrated answerer vs. an overconfident one,
     each following "answer only if your confidence > t"
  4. RESCORING vs. CHANGING BEHAVIOUR: same answerer, answers frozen vs. answers
     filtered by the rule. Whether a REAL model changes behaviour when told the
     rule is NOT simulated here - that needs a recorded run [RUN].

Standard library only.  python3 penalty_threshold.py [--seed 5]
"""
from __future__ import annotations

import argparse
import random
from fractions import Fraction

STATUS = "ILLUSTRATIVE (simulated answerers, no model was called)"


def threshold(k: Fraction) -> Fraction:
    return k / (k + 1)


def expected_guess(p: Fraction, k: Fraction) -> Fraction:
    return p * 1 - (1 - p) * k


def simulate(seed: int, n: int = 1000) -> list[tuple[float, float, bool]]:
    """(true p, stated confidence of overconfident answerer, correct?) per question."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        p = min(0.99, max(0.01, rng.betavariate(1.6, 1.2)))   # true chance of being right
        correct = rng.random() < p
        stated_over = min(0.99, p + 0.25)                      # says it is surer than it is
        out.append((p, stated_over, correct))
    return out


def run_policy(qs, k: float, t: float, use_overconfident: bool, always_answer: bool = False):
    answered = right = wrong = 0
    for p, over, correct in qs:
        conf = over if use_overconfident else p
        if always_answer or conf > t:
            answered += 1
            right += correct
            wrong += not correct
    n = len(qs)
    score = (right - k * wrong) / n
    cov = answered / n
    risk = wrong / answered if answered else float("nan")
    return score, cov, risk


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=5)
    a = ap.parse_args()
    print(f"# {STATUS}\n")

    print("1) THE SILENCE LINE  t = k / (k + 1)")
    rows = [("binary grading", Fraction(0)), ("Konkur-style (+3/-1)", Fraction(1, 3)),
            ("t50", Fraction(1)), ("t75", Fraction(3)), ("t90", Fraction(9))]
    for name, k in rows:
        print(f"   {name:<22} k={str(k):>4}  ->  answer only if P(correct) > {float(threshold(k)):.0%}")
    print("   note: arXiv 2509.04664v1 sec. 4.2 prints 't = 0.75 (penalty 2)'; its own formula t/(1-t) gives 3\n")

    print("2) KONKUR ARITHMETIC (4 options, wrong = -1/3 of a right answer)")
    k = Fraction(1, 3)
    for label, p in (("blind guess, 4 options left", Fraction(1, 4)),
                     ("one option eliminated, 3 left", Fraction(1, 3)),
                     ("two options eliminated, 2 left", Fraction(1, 2))):
        ev = expected_guess(p, k)
        print(f"   {label:<32} P={str(p):>4}  expected value = {str(ev):>5} of a right answer ({float(ev):+.3f})")
    print("   -> this penalty makes BLIND guessing worth zero on average; it does not forbid informed guessing\n")

    qs = simulate(a.seed)
    print(f"3) SIMULATED ANSWERERS on {len(qs)} questions (seed {a.seed}) - ILLUSTRATIVE")
    print(f"   {'k':>4} {'t':>5} | {'calibrated: score':>18} {'cover':>6} {'risk':>5} | {'overconfident: score':>21} {'cover':>6} {'risk':>5}")
    for k in (0, 1, 3, 9):
        t = k / (k + 1)
        s1, c1, r1 = run_policy(qs, k, t, use_overconfident=False)
        s2, c2, r2 = run_policy(qs, k, t, use_overconfident=True)
        print(f"   {k:>4} {t:>5.0%} | {s1:>18.3f} {c1:>6.0%} {r1:>5.0%} | {s2:>21.3f} {c2:>6.0%} {r2:>5.0%}")
    print("   score = points per question (range -k..+1), not a percentage\n")

    print("4) RESCORING vs CHANGING BEHAVIOUR (calibrated answerer)")
    print(f"   {'k':>4} | {'answers frozen (always answer)':>31} | {'answers filtered by t':>22}")
    for k in (1, 3, 9):
        t = k / (k + 1)
        frozen, _, _ = run_policy(qs, k, t, False, always_answer=True)
        filtered, cov, _ = run_policy(qs, k, t, False)
        print(f"   {k:>4} | {frozen:>31.3f} | {filtered:>14.3f} (cover {cov:.0%})")
    print("   rescoring changes the NUMBER; only a new run can show whether a real model changes its ANSWERS [RUN]")


if __name__ == "__main__":
    main()
