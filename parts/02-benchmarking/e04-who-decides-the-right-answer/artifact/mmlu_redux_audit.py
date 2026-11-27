#!/usr/bin/env python3
"""Homodyne HMD-008 / Benchmark E04 - REAL answer-key errors in MMLU, from MMLU-Redux 2.0.

MMLU-Redux (Gema et al. 2024, "Are We Done with MMLU?", arXiv 2406.04127, NAACL 2025) is
5,700 MMLU questions (100 random questions in each of the 57 subjects) re-checked by hand.
Each question carries an error_type: ok, bad_question_clarity, bad_options_clarity,
no_correct_answer, multiple_correct_answers, wrong_groundtruth, or expert (= the annotator
was not sure and says an expert is needed).

Data: https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux-2.0  (CC BY 4.0;
questions and keys come from MMLU, cais/mmlu, MIT licence). No model is called.
All counts and intervals printed here are OUR computation on that data, except the block
marked "transcribed", which copies numbers from the papers' own tables.

    python3 mmlu_redux_audit.py              # read derived/*.csv|json (offline, stdlib only)
    python3 mmlu_redux_audit.py --selftest   # fast offline checks
    python3 mmlu_redux_audit.py --build DIR  # rebuild derived/ from the raw HF arrow files in DIR
                                             # (DIR/<subject>/data-00000-of-00001.arrow; needs pyarrow)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DERIVED = HERE / "derived"
COUNTS = DERIVED / "mmlu_redux_subject_counts.csv"
ITEMS = DERIVED / "mmlu_redux_wrong_key_items.json"
TYPES = ["ok", "bad_question_clarity", "bad_options_clarity", "no_correct_answer",
         "multiple_correct_answers", "wrong_groundtruth", "expert"]
LETTERS = "ABCD"

# Items shown on screen in the episode: (subject, row index in the HF file)
SHOWN = [("virology", 88), ("virology", 96), ("anatomy", 73)]

# Transcribed, not recomputed. Gema et al. 2024 (arXiv 2406.04127v3), Table 2, Virology column:
# exact-match score and rank on all MMLU-Redux Virology questions -> on the "correct" (error-free) ones.
GEMA_TABLE2_VIROLOGY = [
    ("Claude 3.5 Sonnet (20240620)", 0.60, 1, 0.91, 5),
    ("Claude 3 Opus (20240229)", 0.58, 12, 0.88, 8),
    ("Llama 3.1 Instruct Turbo (405B)", 0.57, 16, 0.93, 1),
    ("GPT-4o (2024-05-13)", 0.60, 3, 0.91, 5),
    ("Gemini 1.5 Pro (001)", 0.55, 28, 0.91, 5),
    ("GPT-4 (0613)", 0.60, 3, 0.86, 10),
    ("Qwen2 Instruct (72B)", 0.56, 24, 0.88, 8),
    ("GPT-4 Turbo (2024-04-09)", 0.60, 1, 0.93, 1),
    ("Gemini 1.5 Pro (0409 preview)", 0.58, 10, 0.93, 1),
    ("Llama 3.1 Instruct Turbo (70B)", 0.58, 12, 0.93, 1),
]
# Transcribed, not recomputed. Northcutt, Athalye, Mueller 2021 (arXiv 2103.14749v4), Table 1, "% error".
NORTHCUTT_TABLE1 = [("MNIST", 0.15), ("CIFAR-10", 0.54), ("AudioSet", 1.35), ("20news", 1.09),
                    ("Caltech-256", 1.54), ("IMDB", 2.90), ("Amazon Reviews", 3.90),
                    ("ImageNet (val)", 5.83), ("CIFAR-100", 5.85), ("QuickDraw", 10.12)]


def wilson(x: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for x successes out of n."""
    if n <= 0:
        return (float("nan"), float("nan"))
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def tally(rows: list[dict]) -> dict[str, dict[str, int]]:
    """rows: dicts with 'subject' and 'error_type' -> {subject: {type: count, 'n': total}}."""
    out: dict[str, dict[str, int]] = {}
    for r in rows:
        et = r["error_type"]
        if et not in TYPES:
            raise ValueError(f"unknown error_type {et!r}")
        s = out.setdefault(r["subject"], {t: 0 for t in TYPES} | {"n": 0})
        s[et] += 1
        s["n"] += 1
    return out


def bad(s: dict[str, int]) -> int:
    """Questions NOT labelled ok (this includes 'expert', as in the 57% / 6.49% figures)."""
    return s["n"] - s["ok"]


# ---------------------------------------------------------------- build from raw (pyarrow)
def read_raw(raw: Path) -> list[dict]:
    import pyarrow as pa  # only needed for --build; installed in this environment
    rows = []
    files = sorted(raw.glob("*/data-00000-of-00001.arrow"))
    if len(files) != 57:
        raise SystemExit(f"expected 57 subject files under {raw}, found {len(files)}")
    for f in files:
        with pa.memory_map(str(f)) as src:
            table = pa.ipc.open_stream(src).read_all()
        for i, r in enumerate(table.to_pylist()):
            r["subject"], r["index"] = f.parent.name, i
            rows.append(r)
    return rows


def build(raw: Path) -> None:
    rows = read_raw(raw)
    t = tally(rows)
    DERIVED.mkdir(exist_ok=True)
    with COUNTS.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["subject", "n"] + TYPES)
        for subj in sorted(t):
            w.writerow([subj, t[subj]["n"]] + [t[subj][k] for k in TYPES])
    items = []
    for r in rows:
        if r["error_type"] != "wrong_groundtruth":
            continue
        items.append({"subject": r["subject"], "index": r["index"], "question": r["question"],
                      "choices": list(r["choices"]), "mmlu_key": LETTERS[r["answer"]],
                      "redux_correct_answer": r["correct_answer"], "source": r["source"],
                      "potential_reason": r["potential_reason"]})
    ITEMS.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {COUNTS.name} ({len(t)} subjects, {len(rows)} questions) and "
          f"{ITEMS.name} ({len(items)} wrong-key items)")


# ---------------------------------------------------------------- read derived (stdlib)
def load() -> tuple[dict[str, dict[str, int]], list[dict]]:
    if not COUNTS.exists() or not ITEMS.exists():
        raise SystemExit(f"missing {COUNTS} or {ITEMS}; run --build first (see derived/SOURCE.txt)")
    t = {}
    with COUNTS.open() as f:
        for r in csv.DictReader(f):
            t[r["subject"]] = {k: int(r[k]) for k in ["n"] + TYPES}
    return t, json.loads(ITEMS.read_text())


def letter_of(item: dict) -> str:
    """Redux suggestion may be a letter, a digit index or a float like 3.0; return a letter."""
    v = item["redux_correct_answer"]
    if v is None:
        return "?"
    v = str(v).strip()
    if v[:1].upper() in LETTERS and len(v) == 1:
        return v.upper()
    try:
        return LETTERS[int(float(v))]
    except (ValueError, IndexError):
        return "?"


def bar(x: float, width: int = 40) -> str:
    return "#" * round(x * width)


def report(t: dict[str, dict[str, int]], items: list[dict]) -> None:
    n = sum(s["n"] for s in t.values())
    nb = sum(bad(s) for s in t.values())
    ne = sum(s["expert"] for s in t.values())
    print("# MMLU-Redux 2.0 (Gema et al.; CC BY 4.0). Counts below are OUR computation on that data.\n")
    print("1) HOW MANY QUESTIONS HAVE A PROBLEM?")
    print(f"   re-checked: {n} questions = {len(t)} subjects x 100 random questions")
    print(f"   not 'ok':   {nb}/{n} = {nb / n:.2%}   (incl. {ne} marked 'expert' = annotator unsure)")
    print(f"   paper's own estimate for all of MMLU: 6.49%")
    tot = {k: sum(s[k] for s in t.values()) for k in TYPES}
    for k in TYPES[1:]:
        print(f"     {k:<26}{tot[k]:>4}")
    print()

    print("2) WORST SUBJECTS (share of the 100 checked questions that are not 'ok')")
    ranked = sorted(t.items(), key=lambda kv: (-bad(kv[1]), kv[0]))
    for subj, s in ranked[:8]:
        print(f"   {subj:<22}{bad(s):>3}/100  {bar(bad(s) / 100)}  (wrong key: {s['wrong_groundtruth']})")
    print(f"   {'ALL 57 SUBJECTS':<22}{nb / n:>7.2%}  {bar(nb / n)}\n")

    print("3) THE DENOMINATOR DECIDES WHAT THE NUMBER MEANS")
    v = t["virology"]
    lo, hi = wilson(bad(v), v["n"])
    print(f"   virology only:          {bad(v)}/{v['n']} = {bad(v) / v['n']:.0%}  (95% Wilson {lo:.0%} to {hi:.0%})")
    top5 = ranked[:5]
    b5, n5 = sum(bad(s) for _, s in top5), sum(s["n"] for _, s in top5)
    print(f"   5 worst subjects:       {b5}/{n5} = {b5 / n5:.0%}   ({', '.join(k for k, _ in top5)})")
    print(f"   all 57 subjects:        {nb}/{n} = {nb / n:.2%}")
    print("   same data, three denominators: picking where errors cluster inflates the rate\n")

    print("4) REAL QUESTIONS WHOSE OFFICIAL MMLU KEY IS WRONG (MMLU-Redux label: wrong_groundtruth)")
    by = {(i["subject"], i["index"]): i for i in items}
    for subj, idx in SHOWN:
        it = by.get((subj, idx))
        if not it:
            print(f"   ({subj} #{idx} not found)")
            continue
        print(f"   [{subj} #{idx}] {it['question']}")
        for L, c in zip(LETTERS, it["choices"]):
            mark = "  <- MMLU key" if L == it["mmlu_key"] else ("  <- MMLU-Redux" if L == letter_of(it) else "")
            print(f"      {L}. {c}{mark}")
    print()

    print("5) WHERE THE VIROLOGY WRONG KEYS CAME FROM (annotators' 'source' column)")
    vir = [i for i in items if i["subject"] == "virology"]
    src = {}
    for i in vir:
        src[i["source"] or "(none)"] = src.get(i["source"] or "(none)", 0) + 1
    for s, c in sorted(src.items(), key=lambda kv: -kv[1]):
        print(f"   {c:>3}  {s}")
    print("   paper: errors 'may stem from problems parsing the original datasets'\n")

    print("6) TRANSCRIBED (not recomputed): Gema et al. Table 2, Virology, score (rank)")
    print("   all questions -> only error-free questions")
    for name, a, ra, c, rc in GEMA_TABLE2_VIROLOGY:
        print(f"   {name:<32}{a:.2f} ({ra:>2}) -> {c:.2f} ({rc:>2})")
    print("   Northcutt et al. 2021, Table 1, test-set label errors (%):")
    print("   " + " · ".join(f"{d} {p}" for d, p in NORTHCUTT_TABLE1))


# ---------------------------------------------------------------- selftest
def selftest() -> None:
    lo, hi = wilson(57, 100)
    assert abs(lo - 0.472) < 0.002 and abs(hi - 0.662) < 0.002, (lo, hi)
    assert wilson(0, 30)[0] == 0.0
    rows = [{"subject": "a", "error_type": "ok"}] * 3 + [{"subject": "a", "error_type": "expert"},
                                                         {"subject": "b", "error_type": "wrong_groundtruth"}]
    t = tally(rows)
    assert t["a"]["n"] == 4 and bad(t["a"]) == 1 and bad(t["b"]) == 1
    try:
        tally([{"subject": "a", "error_type": "nope"}])
        raise AssertionError("unknown type accepted")
    except ValueError:
        pass
    for v, want in (("C", "C"), ("3.0", "D"), ("0", "A"), (None, "?"), ("maybe", "?")):
        assert letter_of({"redux_correct_answer": v}) == want, v
    assert len(GEMA_TABLE2_VIROLOGY) == 10 and len(NORTHCUTT_TABLE1) == 10
    if COUNTS.exists() and ITEMS.exists():  # committed derived files must keep their known totals
        t, items = load()
        assert len(t) == 57 and sum(s["n"] for s in t.values()) == 5700
        assert sum(bad(s) for s in t.values()) == 370 and bad(t["virology"]) == 57
        assert t["virology"]["wrong_groundtruth"] == 33 and len(items) == 106
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--build", metavar="RAW_DIR", type=Path, help="rebuild derived/ from raw arrow files")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.build:
        build(a.build)
    else:
        report(*load())


if __name__ == "__main__":
    sys.exit(main())
