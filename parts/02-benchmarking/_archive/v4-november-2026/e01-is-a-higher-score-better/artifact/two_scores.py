#!/usr/bin/env python3
"""Same answers, two scoring rules, two winners.

Re-scores published benchmark outcomes under a penalty for wrong answers,
following the "explicit confidence target" rule in Kalai et al. (2025),
"Why Language Models Hallucinate", section 4.2:

    correct = +1,  "I don't know" = 0,  wrong = -k,   where k = t / (1 - t)

t is the confidence threshold above which a model should answer.

Default data: SimpleQA, as published by OpenAI (5 Sep 2025, from the GPT-5
System Card). Percentages of all questions.

Caveat that travels with every number this prints: this is RE-scoring.
The models were not told about the penalty, so they might have answered
differently if they had been. Measuring that is what bluff-v1 is for.

Usage:
    python3 two_scores.py
    python3 two_scores.py --a "model A" 24 75 1 --b "model B" 22 26 52
                                  (accuracy, error, abstention in %)
"""
from __future__ import annotations

import argparse


def score(acc: float, err: float, k: float) -> float:
    """Points per 100 questions under penalty k per wrong answer."""
    return acc - k * err


def crossover(a: tuple[float, float], b: tuple[float, float]) -> float | None:
    """Penalty k at which two (accuracy, error) profiles score the same."""
    (acc_a, err_a), (acc_b, err_b) = a, b
    if err_a == err_b:
        return None
    k = (acc_a - acc_b) / (err_a - err_b)
    return k if k >= 0 else None


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--a", nargs=4, metavar=("NAME", "ACC", "ERR", "IDK"),
                   default=["OpenAI o4-mini", "24", "75", "1"])
    p.add_argument("--b", nargs=4, metavar=("NAME", "ACC", "ERR", "IDK"),
                   default=["gpt-5-thinking-mini", "22", "26", "52"])
    args = p.parse_args()

    models = []
    for name, acc, err, idk in (args.a, args.b):
        acc, err, idk = float(acc), float(err), float(idk)
        if abs(acc + err + idk - 100) > 1.5:
            print(f"warning: {name}: accuracy + error + abstention = {acc + err + idk:g}%, not 100%")
        models.append((name, acc, err, idk))

    print("SimpleQA re-scored  ·  points per 100 questions  ·  correct +1, IDK 0, wrong -k\n")
    width = max(len(m[0]) for m in models)
    print(f"{'t (confidence target)':>22} {'k':>7}   " + "   ".join(f"{m[0]:>{width}}" for m in models) + "   winner")
    for t in (0.0, 0.25, 0.5, 0.75, 0.9):
        k = t / (1 - t)
        s = [score(m[1], m[2], k) for m in models]
        win = models[0][0] if s[0] > s[1] else models[1][0] if s[1] > s[0] else "tie"
        print(f"{t:>22.2f} {k:>7.3f}   " + "   ".join(f"{v:>{width}.1f}" for v in s) + f"   {win}")

    k = crossover((models[0][1], models[0][2]), (models[1][1], models[1][2]))
    print()
    if k is None:
        print("No crossover at a non-negative penalty: one model wins under every rule.")
    else:
        t = k / (1 + k)
        print(f"Crossover: k = {k:.4f} points per wrong answer (confidence target t = {t:.1%}).")
        print(f"A wrong answer costing 1/{1 / k:.1f} of a right one is enough to flip the winner.")
    print("\nRe-scoring, not re-running: models told about the penalty might answer differently.")


if __name__ == "__main__":
    main()
