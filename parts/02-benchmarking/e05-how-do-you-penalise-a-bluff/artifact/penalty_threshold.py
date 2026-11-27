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
     filtered by the rule.
  5. REAL PUBLISHED NUMBERS, RESCORED BY US: reads artifact/derived/*.json
     (AA-Omniscience paper, OpenAI SimpleQA table; see derived/SOURCE.txt) and
     scores the SAME frozen answers under k = 0, 1/3, 1, 3. Inputs are rounded
     as published, so every score is shown with its rounding range and a winner
     is called only if the ranges do not overlap. If no real input is found,
     a labelled toy pair is used instead.
  Whether a REAL model changes its answers when told the rule is NOT computed
  here - that needs a recorded run [RUN].

Standard library only.
  python3 penalty_threshold.py [--seed 5] [--data-dir DIR] [--csv OUT] [--selftest]
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path

STATUS = "ILLUSTRATIVE (simulated answerers, no model was called)"
HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE / "derived"
REAL_KS = (("0 (accuracy)", Fraction(0)), ("1/3 (Konkur)", Fraction(1, 3)),
           ("1", Fraction(1)), ("3", Fraction(3)))
ROUND = 0.5   # published percentages are whole numbers: true value within +-0.5
TOY_REAL = {  # fallback only - never shown as real
    "dataset": "TOY fallback (no derived/*.json found)", "status": "ILLUSTRATIVE",
    "unit": "percent of all questions", "kind": "accuracy+error", "native_k": 0,
    "rows": [{"model": "toy A", "accuracy": 60, "error": 30},
             {"model": "toy B", "accuracy": 50, "error": 5}]}


# ---------------------------------------------------------------- parts 1-4

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


# ---------------------------------------------------------------- part 5

def wrong_share(row: dict, acc: float | None = None, second: float | None = None) -> float:
    """Percent of ALL questions answered wrongly.

    AA-Omniscience publishes hallucination rate H = i/(p+i+a) = i/(N-c), so
    i/N = H * (1 - accuracy) exactly (no approximation)."""
    acc = row["accuracy"] if acc is None else acc
    if "error" in row:
        return float(row["error"] if second is None else second)
    hal = row["hallucination_rate"] if second is None else second
    return hal * (100 - acc) / 100


def score(row: dict, k: Fraction, acc=None, second=None) -> float:
    """Points per 100 questions: right +1, I-don't-know 0, wrong -k."""
    acc = row["accuracy"] if acc is None else acc
    return acc - float(k) * wrong_share(row, acc, second)


def score_range(row: dict, k: Fraction) -> tuple[float, float]:
    """Min/max score if each published (rounded) percentage is off by up to 0.5."""
    second = row.get("error", row.get("hallucination_rate"))
    vals = [score(row, k, row["accuracy"] + da, second + db)
            for da, db in product((-ROUND, ROUND), repeat=2)]
    return min(vals), max(vals)


def winner(rows: list[dict], k: Fraction) -> tuple[list[str], bool]:
    """Best model(s) at k. Returns (names, clear). 'clear' only if the leader's
    worst case beats every other model's best case; otherwise every model whose
    range overlaps the leader's is returned as a tie."""
    best = max(rows, key=lambda r: score(r, k))
    lo = score_range(best, k)[0]
    tied = [r["model"] for r in rows if r is best or score_range(r, k)[1] >= lo]
    return tied, len(tied) == 1


def load_real(data_dir: Path) -> list[dict]:
    sets = []
    for f in sorted(Path(data_dir).glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if "rows" not in d or not d["rows"]:
            raise ValueError(f"{f.name}: no rows")
        for r in d["rows"]:
            if "accuracy" not in r or not ("error" in r or "hallucination_rate" in r):
                raise ValueError(f"{f.name}: row {r.get('model')} lacks accuracy/error")
        d["_file"] = f.name
        sets.append(d)
    return sets


def rescore_table(ds: dict) -> list[dict]:
    out = []
    for r in ds["rows"]:
        rec = {"dataset": ds.get("_file", "toy"), "model": r["model"],
               "accuracy_pct": r["accuracy"], "wrong_pct_of_all": round(wrong_share(r), 2)}
        for label, k in REAL_KS:
            key = label.split()[0]
            lo, hi = score_range(r, k)
            rec[f"score_k={key}"] = round(score(r, k), 1)
            rec[f"range_k={key}"] = f"{lo:.1f}..{hi:.1f}"
        if "published_index" in r:
            rec["published_index_k=1"] = r["published_index"]
        out.append(rec)
    return out


def print_real(sets: list[dict], csv_out: str | None) -> None:
    print("5) REAL PUBLISHED NUMBERS, RESCORED BY US (same frozen answers, new rule)")
    print("   score = right - k x wrong, in points per 100 questions; staying silent on everything = 0")
    all_rows = []
    for ds in sets:
        tag = "ILLUSTRATIVE" if ds is TOY_REAL else "REAL"
        print(f"\n   [{tag}] {ds['dataset']}")
        if ds.get("prompt_note"):
            print(f"   prompt: {ds['prompt_note']}")
        print("   " + f"{'model':<20}{'right%':>7}{'wrong%':>8}"
              + "".join(f"{'k=' + l.split()[0]:>22}" for l, _ in REAL_KS))
        for r in ds["rows"]:
            cells = ""
            for _, k in REAL_KS:
                lo, hi = score_range(r, k)
                cells += f"{score(r, k) + 0.0:>8.1f} [{lo:>6.1f},{hi:>6.1f}]"
            print(f"   {r['model']:<20}{r['accuracy']:>7}{wrong_share(r):>8.1f}{cells}")
        for label, k in REAL_KS:
            names, clear = winner(ds["rows"], k)
            verdict = names[0] if clear else "tie within rounding: " + " ~ ".join(names)
            print(f"   winner at k = {label:<13} -> {verdict}")
        if any("published_index" in r for r in ds["rows"]):
            print("   check, k = 1 computed vs index printed in the paper: "
                  + " · ".join(f"{r['model']} {score(r, Fraction(1)) + 0.0:+.1f} vs {r['published_index']:+}"
                               for r in ds["rows"]))
        all_rows += rescore_table(ds)
    if any(ds is not TOY_REAL for ds in sets):
        print("\n   ours: arithmetic on published, rounded numbers. The models were NOT re-run;"
              " nobody changed an answer - only the ruler changed.")
    else:
        print("\n   TOY numbers only (ILLUSTRATIVE): add real inputs to derived/ to rescore published results.")
    if csv_out:
        keys = list(dict.fromkeys(k for r in all_rows for k in r))
        with open(csv_out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            w.writerows(all_rows)
        print(f"   wrote {csv_out}")


# ---------------------------------------------------------------- selftest

def selftest() -> int:
    assert threshold(Fraction(1, 3)) == Fraction(1, 4)
    assert threshold(Fraction(9)) == Fraction(9, 10)
    assert expected_guess(Fraction(1, 4), Fraction(1, 3)) == 0
    assert expected_guess(Fraction(1, 2), Fraction(1, 3)) == Fraction(1, 3)
    qs = simulate(5)
    s, c, r = run_policy(qs, 3, 0.75, False)
    assert (round(s, 3), round(c, 2), round(r, 2)) == (0.130, 0.29, 0.14), (s, c, r)
    s, c, r = run_policy(qs, 3, 0.75, True)
    assert (round(s, 3), round(c, 2), round(r, 2)) == (-0.054, 0.59, 0.27), (s, c, r)
    assert round(run_policy(qs, 3, 0.75, False, always_answer=True)[0], 3) == -0.792
    # part 5 maths on a synthetic row: acc 40, H 50 -> wrong 30 of all
    row = {"model": "x", "accuracy": 40, "hallucination_rate": 50}
    assert wrong_share(row) == 30 and score(row, Fraction(1)) == 10 and score(row, Fraction(3)) == -50
    lo, hi = score_range(row, Fraction(1))
    assert lo < 10 < hi and abs((hi - lo) - 2.1) < 1e-9, (lo, hi)
    a = {"model": "a", "accuracy": 60, "error": 30}
    b = {"model": "b", "accuracy": 50, "error": 5}
    assert winner([a, b], Fraction(0)) == (["a"], True)
    assert winner([a, b], Fraction(3)) == (["b"], True)
    near = {"model": "c", "accuracy": 50, "error": 5.2}
    assert winner([b, near], Fraction(1))[1] is False          # overlapping ranges -> tie
    with tempfile.TemporaryDirectory() as td:
        Path(td, "t.json").write_text(json.dumps({"dataset": "t", "rows": [row, a]}), encoding="utf-8")
        assert len(load_real(Path(td))[0]["rows"]) == 2
        Path(td, "bad.json").write_text(json.dumps({"dataset": "bad", "rows": [{"model": "z"}]}), encoding="utf-8")
        try:
            load_real(Path(td))
            raise AssertionError("bad row accepted")
        except ValueError:
            pass
    if DEFAULT_DATA.is_dir():                                    # committed inputs parse and agree
        for ds in load_real(DEFAULT_DATA):
            for r in ds["rows"]:
                if "published_index" in r:                       # k=1 within rounding of the paper
                    lo, hi = score_range(r, Fraction(1))
                    assert lo - 0.5 <= r["published_index"] <= hi + 0.5, (r["model"], lo, hi)
    print("selftest ok")
    return 0


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--data-dir", default=str(DEFAULT_DATA), help="folder with real *.json inputs")
    ap.add_argument("--csv", help="also write the part-5 table as CSV")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    print(f"# parts 1-4: {STATUS}\n# part 5: REAL published numbers, our arithmetic\n")

    print("1) THE ANSWER THRESHOLD  t = k / (k + 1)")
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

    print("4) RESCORING vs CHANGING BEHAVIOUR (calibrated answerer) - ILLUSTRATIVE")
    print(f"   {'k':>4} | {'answers frozen (always answer)':>31} | {'answers filtered by t':>22}")
    for k in (1, 3, 9):
        t = k / (k + 1)
        frozen, _, _ = run_policy(qs, k, t, False, always_answer=True)
        filtered, cov, _ = run_policy(qs, k, t, False)
        print(f"   {k:>4} | {frozen:>31.3f} | {filtered:>14.3f} (cover {cov:.0%})")
    print("   rescoring changes the NUMBER; only a new run can show whether a real model changes its ANSWERS [RUN]\n")

    try:
        sets = load_real(Path(a.data_dir))
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"   (could not read real inputs: {e})")
        sets = []
    if not sets:
        print("   no real inputs found -> TOY fallback, ILLUSTRATIVE")
        sets = [TOY_REAL]
    print_real(sets, a.csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
