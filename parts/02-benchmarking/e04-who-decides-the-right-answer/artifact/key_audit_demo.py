#!/usr/bin/env python3
"""Homodyne HMD-008 / Benchmark E04 - "who loses when the answer key is wrong?"

ILLUSTRATIVE ONLY. No model was called. Two fictional models ("K" = knows more,
"P" = repeats popular beliefs) answer a 100-question quiz. Eight answer-key
entries are deliberately wrong in the most dangerous way: the key repeats a
popular misconception (Sydney instead of Canberra, and so on).

The script shows four things:
  1. scoreboard under the flawed key (v1) and the adjudicated key (v2)
  2. the same flaw if key errors were random typos instead of popular myths
  3. why the denominator of an audit matters (random audit vs. suspicious-only)
  4. a two-reviewer adjudication log with raw agreement

It also writes two CSVs in the bluff_lab format so the same flip can be checked
with the channel's existing tool:
  python3 tools/bluff_lab.py score parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/key-v1.csv --condition plain
  python3 tools/bluff_lab.py score parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/key-v2.csv --condition plain
(read "accuracy_all_prompts"; "plain" is the condition name used for a prompt
without any penalty instruction).

Standard library only.  python3 key_audit_demo.py [--write-csv]
"""
from __future__ import annotations

import argparse
import csv
import math
import random
from pathlib import Path

STATUS = "ILLUSTRATIVE"
N = 100

# The eight planted key errors: (question, true answer, popular myth used by key v1)
MYTH_ITEMS = [
    ("Capital of Australia?", "Canberra", "Sydney"),
    ("Capital of Turkey?", "Ankara", "Istanbul"),
    ("Capital of Canada?", "Ottawa", "Toronto"),
    ("Capital of Brazil?", "Brasilia", "Rio de Janeiro"),
    ("Capital of Nigeria?", "Abuja", "Lagos"),
    ("Capital of Myanmar?", "Naypyidaw", "Yangon"),
    ("Capital of New Zealand?", "Wellington", "Auckland"),
    ("Capital of Kazakhstan (2026)?", "Astana", "Almaty"),
]


def build_quiz() -> list[dict]:
    """Deterministic quiz: items 1-8 are the planted key errors, 9-100 are fine."""
    items = []
    for i in range(N):
        if i < len(MYTH_ITEMS):
            q, truth, myth = MYTH_ITEMS[i]
            items.append({"id": f"q{i + 1:03d}", "q": q, "truth": truth, "myth": myth,
                          "key_v1": myth, "key_v2": truth})
        else:
            items.append({"id": f"q{i + 1:03d}", "q": f"(generic item {i + 1})", "truth": f"T{i + 1}",
                          "myth": f"M{i + 1}", "key_v1": f"T{i + 1}", "key_v2": f"T{i + 1}"})
    return items


def build_answers(items: list[dict]) -> dict:
    """Model K: right on 80 items, incl. 7 of the 8 myth items.
    Model P: right on 76 items, incl. 2 myth items; repeats the myth on the other 6."""
    k, p = {}, {}
    # myth items
    for i, it in enumerate(items[:8]):
        k[it["id"]] = it["truth"] if i < 7 else "Other"
        p[it["id"]] = it["truth"] if i in (0, 1) else it["myth"]
    # generic items: K right on 73 of 92, P right on 74 of 92
    for j, it in enumerate(items[8:]):
        k[it["id"]] = it["truth"] if j < 73 else "wrong-K"
        p[it["id"]] = it["truth"] if (j + 10) % 92 < 74 else "wrong-P"
    return {"K": k, "P": p}


def score(answers: dict, items: list[dict], key: str) -> int:
    return sum(answers[it["id"]] == it[key] for it in items)


def wilson(x: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def write_csv(path: Path, items: list[dict], answers: dict, key: str) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "cluster_id", "model", "condition", "repeat", "language", "split",
                    "answerable", "label", "source_status", "response"])
        for m in ("K", "P"):
            for it in items:
                label = "correct" if answers[m][it["id"]] == it[key] else "wrong"
                w.writerow([it["id"], "C-" + it["id"], m, "plain", 1, "en", "main", "true", label,
                            STATUS, f"ILLUSTRATIVE answer {answers[m][it['id']]}"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-csv", action="store_true", help="write key-v1.csv / key-v2.csv next to this file")
    a = ap.parse_args()
    items = build_quiz()
    ans = build_answers(items)

    print(f"# {STATUS}: fictional models, planted key errors, no model was called\n")
    print("1) SCOREBOARD (accuracy, out of 100)")
    for key, label in (("key_v1", "key v1 (8 myth errors)"), ("key_v2", "key v2 (adjudicated)")):
        sk, sp = score(ans["K"], items, key), score(ans["P"], items, key)
        win = "K" if sk > sp else "P" if sp > sk else "tie"
        print(f"   {label:<26} K={sk:>3}  P={sp:>3}  leader={win}")
    print("   K = knows more, P = repeats popular beliefs\n")

    print("2) SAME 8 ERRORS, BUT RANDOM TYPOS (key matches nobody)")
    typo = [dict(it) for it in items]
    for it in typo[:8]:
        it["key_v1"] = "typo"
    sk, sp = score(ans["K"], typo, "key_v1"), score(ans["P"], typo, "key_v1")
    print(f"   K={sk}  P={sp}  -> a wrong key only takes points from those who answered RIGHT")
    print("   expected loss per model ~= its accuracy x key error rate; the stronger model pays more\n")

    print("3) AUDIT: THE DENOMINATOR DECIDES WHAT THE NUMBER MEANS")
    suspicious = [it for it in items if ans["K"][it["id"]] != it["key_v1"] or ans["P"][it["id"]] != it["key_v1"]]
    bad_s = sum(it["key_v1"] != it["truth"] for it in suspicious)
    print(f"   audit only items where a model disagreed with the key: {bad_s}/{len(suspicious)} wrong keys"
          f" = {bad_s / len(suspicious):.0%}  (NOT the error rate of the whole key)")
    rng = random.Random(8)
    sample = rng.sample(items, 30)
    bad_r = sum(it["key_v1"] != it["truth"] for it in sample)
    lo, hi = wilson(bad_r, 30)
    print(f"   random audit of 30 items (seed 8): {bad_r}/30 wrong keys, 95% Wilson interval {lo:.0%} to {hi:.0%}")
    print(f"   true planted rate in this toy: 8/100 = 8%\n")

    print("4) ADJUDICATION LOG (two blind reviewers on the 8 planted items + 4 clean items)")
    review = [(it["id"], it["q"], "error", "error" if i != 5 else "ok") for i, it in enumerate(items[:8])]
    review += [(it["id"], it["q"], "ok", "ok") for it in items[8:12]]
    agree = sum(r[2] == r[3] for r in review)
    for rid, q, r1, r2 in review[:8]:
        flag = "" if r1 == r2 else "  <- disagreement: resolve with primary source, log reason"
        print(f"   {rid} {q:<30} R1={r1:<5} R2={r2:<5}{flag}")
    print(f"   raw agreement {agree}/{len(review)}; disagreements are resolved by evidence, not by vote\n")

    if a.write_csv:
        here = Path(__file__).resolve().parent
        write_csv(here / "key-v1.csv", items, ans, "key_v1")
        write_csv(here / "key-v2.csv", items, ans, "key_v2")
        print(f"wrote {here / 'key-v1.csv'} and {here / 'key-v2.csv'} (bluff_lab format, ILLUSTRATIVE)")


if __name__ == "__main__":
    main()
