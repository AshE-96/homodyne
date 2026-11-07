#!/usr/bin/env python3
"""Homodyne HMD-018 / Benchmark E09 - "where did this AI score come from? check it yourself".

A reader's checker for a published benchmark score. It does three things and
prints PASS or FAIL with the FIRST mismatch it finds:

  1. MANIFEST   every file listed in MANIFEST.sha256 exists and has that SHA-256;
                no unlisted file sits in the bundle; optionally the manifest itself
                matches an ANCHOR hash published somewhere else (video description,
                pinned comment) on a known date.
  2. LOG        the version in published.json is the newest entry in CHANGELOG.md.
  3. RECOMPUTE  the scores are recomputed from the labelled answers in results.csv
                with the course's own scorer (tools/bluff_lab.py) and compared with
                the published scores (or with --claim MODEL=SCORE you saw on screen).

RECOMPUTE IS NOT RERUN. No model is called. We recompute a number from stored,
labelled answers. Asking a model again (a rerun) can give different answers.

The demo bundle is ILLUSTRATIVE: it is the course's teaching file
tools/bluff-demo.csv (10 prompts x 2 models, condition t75, penalty k=3).
No model was called to make it.

Standard library only.
  python3 recompute_check.py --demo DIR [--variant original|tamper-csv|tamper-csv-manifest|tamper-all|correction]
  python3 recompute_check.py DIR [--anchor SHA256] [--claim A=-0.1]
  python3 recompute_check.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
STATUS = "ILLUSTRATIVE (teaching bundle; no model was called)"
VARIANTS = ["original", "tamper-csv", "tamper-csv-manifest", "tamper-all", "correction"]
CHECKED = ["results.csv", "published.json", "METHOD.md", "CHANGELOG.md"]


def load_bluff_lab():
    path = ROOT/"tools"/"bluff_lab.py"
    spec = importlib.util.spec_from_file_location("bluff_lab", path)
    if spec is None or not path.exists():
        sys.exit(f"error: course scorer not found at {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- bundle maker

METHOD = """# METHOD (ILLUSTRATIVE teaching bundle)

- Rule: correct +1, abstain 0, wrong / invalid / api_error -k.
- Condition t75, k = 3. Score = points per prompt, not a percentage.
- Scorer: tools/bluff_lab.py (summaries), repeats averaged within prompt.
- Labels were assigned by a human before scoring. No model is called here.
- Recompute = same labelled answers + same code -> same number.
- Rerun = asking the model again -> answers may differ (sampling, version).
"""

CHANGELOG_V01 = """# CHANGELOG

## v0.1 - 2026-11-07
- First publication. Condition t75, k=3. ILLUSTRATIVE.
"""

CHANGELOG_V02 = """# CHANGELOG

## v0.2 - 2026-11-14
- Correction: item q06 (model A, Persian) relabelled wrong -> correct.
- Reason: reader report; the answer key accepted only one spelling of the name.
- Effect: A -0.100 -> +0.300 points per prompt. B unchanged (+0.100).
- The published verdict changes: A now scores above B on this teaching file.
- v0.1 files and the v0.1 anchor stay public next to this entry.

## v0.1 - 2026-11-07
- First publication. Condition t75, k=3. ILLUSTRATIVE.
"""


def relabel_q06(csv_text: bytes) -> bytes:
    """The one-row edit used by both the tamper and the honest correction."""
    old = b"q06,M-03,A,t75,1,fa,main,true,wrong,ILLUSTRATIVE,ILLUSTRATIVE labelled outcome wrong"
    new = b"q06,M-03,A,t75,1,fa,main,true,correct,ILLUSTRATIVE,ILLUSTRATIVE labelled outcome correct"
    if old not in csv_text:
        sys.exit("error: tools/bluff-demo.csv changed; row q06/A not found")
    return csv_text.replace(old, new)


def score_csv(csv_path: Path, condition: str, decimals: int) -> dict[str, float]:
    bl = load_bluff_lab()
    rows = bl.read_rows(csv_path, condition)
    penalty = bl.CONDITIONS[condition]
    return {m: round(v["score_points_per_prompt"], decimals)
            for m, v in bl.summaries(rows, penalty).items()}


def write_manifest(folder: Path) -> str:
    lines = [f"{sha256(folder/name)}  {name}" for name in CHECKED]
    (folder/"MANIFEST.sha256").write_text("\n".join(lines)+"\n", encoding="utf-8")
    return sha256(folder/"MANIFEST.sha256")


def published(version: str, date: str, scores: dict[str, float]) -> str:
    return json.dumps({
        "bundle_version": version, "date": date, "source_status": "ILLUSTRATIVE",
        "condition": "t75", "penalty_k": 3, "decimals": 3,
        "unit": "points per prompt", "scorer": "tools/bluff_lab.py summaries()",
        "scores": scores}, indent=2)+"\n"


def make_demo(folder: Path, variant: str = "original") -> dict[str, str]:
    """Write a bundle. Returns {'anchor_v01': ..., 'anchor_now': ...}."""
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    csv_text = (ROOT/"tools"/"bluff-demo.csv").read_bytes()   # byte copy: same SHA-256 as bluff_lab prints
    (folder/"results.csv").write_bytes(csv_text)
    (folder/"METHOD.md").write_text(METHOD, encoding="utf-8")
    (folder/"CHANGELOG.md").write_text(CHANGELOG_V01, encoding="utf-8")
    scores = score_csv(folder/"results.csv", "t75", 3)
    (folder/"published.json").write_text(published("0.1", "2026-11-07", scores), encoding="utf-8")
    anchor_v01 = write_manifest(folder)

    if variant == "original":
        pass
    elif variant == "tamper-csv":            # edit one label, touch nothing else
        (folder/"results.csv").write_bytes(relabel_q06(csv_text))
    elif variant == "tamper-csv-manifest":   # edit label, regenerate manifest, keep claim
        (folder/"results.csv").write_bytes(relabel_q06(csv_text))
        write_manifest(folder)
    elif variant == "tamper-all":            # edit label, rewrite claim and manifest; no log entry
        (folder/"results.csv").write_bytes(relabel_q06(csv_text))
        new = score_csv(folder/"results.csv", "t75", 3)
        (folder/"published.json").write_text(published("0.1", "2026-11-07", new), encoding="utf-8")
        write_manifest(folder)
    elif variant == "correction":            # same edit, done in public: v0.2 + log + new anchor
        (folder/"results.csv").write_bytes(relabel_q06(csv_text))
        new = score_csv(folder/"results.csv", "t75", 3)
        (folder/"published.json").write_text(published("0.2", "2026-11-14", new), encoding="utf-8")
        (folder/"CHANGELOG.md").write_text(CHANGELOG_V02, encoding="utf-8")
        write_manifest(folder)
    else:
        sys.exit(f"error: unknown variant {variant}")
    return {"anchor_v01": anchor_v01, "anchor_now": sha256(folder/"MANIFEST.sha256")}


# ---------------------------------------------------------------- the checker

def check(folder: Path, anchor: str | None = None, claims: dict[str, float] | None = None):
    """Return (ok, lines, first_mismatch or None)."""
    lines: list[str] = []

    def fail(msg):
        lines.append(f"  FAIL  {msg}")
        return False, lines, msg

    # 1. manifest
    mf = folder/"MANIFEST.sha256"
    if not mf.exists():
        return fail("no MANIFEST.sha256 in bundle")
    manifest_hash = sha256(mf)
    if anchor:
        if manifest_hash != anchor.lower():
            return fail(f"manifest anchor: published {anchor[:12]}..., bundle has {manifest_hash[:12]}...")
        lines.append(f"  ok    manifest matches the published anchor {anchor[:12]}...")
    else:
        lines.append(f"  warn  no --anchor given; manifest {manifest_hash[:12]}... is only self-consistent")
    listed = {}
    for raw in mf.read_text(encoding="utf-8").splitlines():
        m = re.fullmatch(r"([0-9a-f]{64})  (\S+)", raw.strip())
        if not m:
            return fail(f"unreadable manifest line: {raw!r}")
        listed[m.group(2)] = m.group(1)
    for name, digest in listed.items():
        p = folder/name
        if not p.exists():
            return fail(f"file listed in manifest is missing: {name}")
        got = sha256(p)
        if got != digest:
            return fail(f"hash mismatch in {name}: manifest {digest[:12]}..., file {got[:12]}...")
        lines.append(f"  ok    {name:<15} {got[:12]}...")
    extra = sorted(p.name for p in folder.iterdir() if p.is_file() and p.name not in listed and p.name != "MANIFEST.sha256")
    if extra:
        return fail(f"file not in manifest: {extra[0]}")

    # 2. correction log
    pub = json.loads((folder/"published.json").read_text(encoding="utf-8"))
    log = (folder/"CHANGELOG.md").read_text(encoding="utf-8")
    versions = re.findall(r"^## v(\S+)", log, re.M)
    if not versions or versions[0] != pub["bundle_version"]:
        return fail(f"published version v{pub['bundle_version']} is not the newest CHANGELOG entry ({versions[:1]})")
    lines.append(f"  ok    version v{pub['bundle_version']} is the newest of {len(versions)} log entr{'y' if len(versions) == 1 else 'ies'}")

    # 3. recompute (NOT rerun)
    recomputed = score_csv(folder/"results.csv", pub["condition"], pub["decimals"])
    target = dict(pub["scores"])
    source = {m: "published" for m in target}
    if claims:
        target.update(claims)
        source.update({m: "claimed" for m in claims})
    for model in sorted(target):
        got = recomputed.get(model)
        want = round(float(target[model]), pub["decimals"])
        if got is None:
            return fail(f"model {model} is claimed but has no rows in results.csv")
        if got != want:
            return fail(f"score of {model}: {source[model]} {want:+.3f}, recomputed {got:+.3f}")
        lines.append(f"  ok    {model}: {source[model]} {want:+.3f} == recomputed {got:+.3f}")
    return True, lines, None


def report(folder: Path, anchor=None, claims=None) -> bool:
    print(f"# {STATUS}")
    print(f"bundle: {folder}")
    ok, lines, first = check(folder, anchor, claims)
    print("\n".join(lines))
    print("RESULT: PASS" if ok else f"RESULT: FAIL  (first mismatch: {first})")
    print("note: recomputed from stored labels; no model was rerun.")
    return ok


# ---------------------------------------------------------------- self-test

def selftest() -> int:
    print(f"# {STATUS}")
    print("# selftest: one original bundle, three tampered ones, one public correction")
    print("# every bundle is checked twice: without and with the anchor published outside it\n")
    expected = {  # (no anchor, with anchor)
        "original": (True, True), "tamper-csv": (False, False),
        "tamper-csv-manifest": (False, False), "tamper-all": (True, False),
        "correction": (True, True)}
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        v01 = make_demo(base/"original", "original")["anchor_v01"]
        print(f"anchor v0.1 = sha256(MANIFEST.sha256) = {v01}\n")
        for variant in VARIANTS:
            a = make_demo(base/variant, variant)
            # the reader uses the anchor that is public for that version
            anchor = a["anchor_now"] if variant == "correction" else v01
            results = []
            for use in (None, anchor):
                ok, lines, first = check(base/variant, use)
                results.append(ok)
                tag = "no anchor  " if use is None else f"anchor {use[:8]}"
                print(f"[{variant:<19}] {tag} -> {'PASS' if ok else 'FAIL'}" + (f"  first mismatch: {first}" if first else ""))
                if use and variant in ("original", "correction"):
                    print("\n".join(lines))
            if tuple(results) != expected[variant]:
                failures += 1
                print(f"   !! expected {expected[variant]}")
            print()
        ok, _, first = check(base/"original", v01, {"A": 0.3})
        print(f"[original, viewer types A=+0.300 from a screenshot] -> {'PASS' if ok else 'FAIL'}  first mismatch: {first}")
        failures += ok
    print(f"\nselftest: {'all expectations met' if not failures else f'{failures} unexpected result(s)'}")
    return 1 if failures else 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bundle", nargs="?", type=Path, help="bundle folder to check")
    ap.add_argument("--demo", type=Path, metavar="DIR", help="write an ILLUSTRATIVE bundle to DIR")
    ap.add_argument("--variant", choices=VARIANTS, default="original")
    ap.add_argument("--anchor", help="SHA-256 of MANIFEST.sha256 as published outside the bundle")
    ap.add_argument("--claim", action="append", default=[], metavar="MODEL=SCORE",
                    help="a score you saw on screen, e.g. A=-0.1")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.demo:
        anchors = make_demo(a.demo, a.variant)
        print(f"# {STATUS}\nwrote {a.variant} bundle to {a.demo}")
        print(f"v0.1 anchor: {anchors['anchor_v01']}\ncurrent manifest: {anchors['anchor_now']}")
        return
    if not a.bundle:
        ap.error("give a bundle folder, --demo DIR, or --selftest")
    claims = {}
    for c in a.claim:
        model, _, val = c.partition("=")
        claims[model] = float(val)
    sys.exit(0 if report(a.bundle, a.anchor, claims or None) else 1)


if __name__ == "__main__":
    main()
