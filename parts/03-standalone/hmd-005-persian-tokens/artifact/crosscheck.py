#!/usr/bin/env python3
"""Homodyne HMD-005 — cross-check the 50-pair result on public, real text.

What it does
  1. Our 50 self-written pairs (corpus/pairs.jsonl), counted again with the
     nine tokenizers of count_tokens.py PLUS three "what if Persian gets room"
     tokenizers:
       Qwen3.5      the next generation after Qwen3 (bigger vocabulary)
       PersianMind  University of Tehran: Llama-2's tokenizer + 10,000 Persian
                    tokens (arXiv 2401.06466, section 3.1)
       gpt-oss      OpenAI's open-weight model (o200k family; control)
  2. FLORES-200 devtest: 1,012 Wikipedia sentences professionally translated
     into Persian (pes_Arab) and English (eng_Latn). CC BY-SA 4.0. This is the
     corpus Petrov et al. (NeurIPS 2023) used. Text is counted exactly as
     published (no orthography changes). Read straight from the tarball; nothing
     is extracted to disk.
  3. OpenAI's own example sentence from "Hello GPT-4o" (13 May 2024), where
     OpenAI says Persian went "from 61 to 32" tokens. We count it ourselves.

Outputs (in artifact/derived/ unless --out-dir is given)
  crosscheck-YYYY-MM-DD.csv   one row per tokenizer (small; committed)
  crosscheck-YYYY-MM-DD.json  same plus run metadata

Usage
  python3 -I crosscheck.py --flores data/flores200/flores200_dataset.tar.gz
  python3 -I crosscheck.py --flores … --offline      # local caches only
  python3 -I crosscheck.py --selftest                # fast, offline, no tokenizers

Download (once, ~25 MB, CC BY-SA 4.0):
  https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz
Requirements: as count_tokens.py (tiktoken; transformers for the HF tokenizers).
Claim boundary: token counts only. Nothing here measures quality or speed.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import platform
import statistics
import sys
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # our own sibling module (works under python3 -I)

FLORES_MEMBERS = {"fa": "flores200_dataset/devtest/pes_Arab.devtest",
                  "en": "flores200_dataset/devtest/eng_Latn.devtest"}
# Copied from https://openai.com/index/hello-gpt-4o/ (section "Language tokenization"), fetched 2026-11-26.
GPT4O_FA = "سلام، اسم من جی پی تی-۴او است. من یک نوع جدیدی از مدل زبانی هستم، از ملاقات شما خوشبختم!"
GPT4O_EN = "Hello, my name is GPT-4o. I'm a new type of language model, it's nice to meet you!"
GPT4O_CLAIM = {"from": 61, "to": 32, "factor": 1.9}

# Extra tokenizers (label, kind, id, revision, note); same shape as count_tokens.TOKENIZERS.
EXTRA = [
    ("Qwen3.5", "hf", "Qwen/Qwen3.5-9B", "c202236235762e1c871ad0ccb60c8ee5ba337b9a",
     "next generation after Qwen3; Apache-2.0"),
    ("PersianMind", "hf", "universitytehran/PersianMind-v1.0", "af603eeb074138e2a613fbc95d89f018afbd3041",
     "Llama-2 tokenizer + 10k Persian BPE tokens (arXiv 2401.06466 §3.1)"),
    ("gpt-oss", "hf", "openai/gpt-oss-20b", "6cee5e81ee83917806bbde320786a8fb61efebee",
     "OpenAI open-weight, o200k family; control"),
]


def q(values, p):
    v = sorted(values)
    k = (len(v) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def ratio_stats(fa_counts, en_counts):
    """Per-item ratios fa/en -> median, IQR, corpus ratio. Items with en == 0 are skipped."""
    r = [f / e for f, e in zip(fa_counts, en_counts) if e]
    return {"n": len(r), "median": statistics.median(r), "p25": q(r, .25), "p75": q(r, .75),
            "corpus_ratio": sum(fa_counts) / sum(en_counts),
            "fa_tokens": sum(fa_counts), "en_tokens": sum(en_counts),
            "share_fa_more": sum(x > 1 for x in r) / len(r)}


def read_flores(tar_path):
    """Return (fa_lines, en_lines) from the FLORES-200 tarball without extracting it."""
    out = {}
    with tarfile.open(tar_path) as t:
        names = {m.name.lstrip("./"): m for m in t.getmembers() if m.isfile()}
        for lang, member in FLORES_MEMBERS.items():
            m = names.get(member)
            if m is None or m.size > 5_000_000:
                raise SystemExit(f"FLORES member missing or too big: {member}")
            out[lang] = t.extractfile(m).read().decode("utf-8").splitlines()
    if len(out["fa"]) != len(out["en"]):
        raise SystemExit("FLORES fa/en line counts differ")
    return out["fa"], out["en"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def measure(tok, pairs, flores):
    fa_p = [tok.count(p["fa"]) for p in pairs]
    en_p = [tok.count(p["en"]) for p in pairs]
    row = {"label": tok.label, "version": tok.version, "vocab": tok.vocab, "note": tok.note,
           "pairs": ratio_stats(fa_p, en_p),
           "gpt4o_fa": tok.count(GPT4O_FA), "gpt4o_en": tok.count(GPT4O_EN)}
    if flores:
        fa_f = [tok.count(x) for x in flores[0]]
        en_f = [tok.count(x) for x in flores[1]]
        row["flores"] = ratio_stats(fa_f, en_f)
    return row


CSV_COLS = ["label", "version", "vocab", "pairs_median", "pairs_p25", "pairs_p75",
            "flores_median", "flores_p25", "flores_p75", "flores_corpus_ratio",
            "flores_fa_tokens", "flores_en_tokens", "gpt4o_fa", "gpt4o_en"]


def csv_rows(rows):
    for r in rows:
        f = r.get("flores", {})
        yield {"label": r["label"], "version": r["version"], "vocab": r["vocab"],
               "pairs_median": f"{r['pairs']['median']:.2f}", "pairs_p25": f"{r['pairs']['p25']:.2f}",
               "pairs_p75": f"{r['pairs']['p75']:.2f}",
               "flores_median": f"{f['median']:.2f}" if f else "", "flores_p25": f"{f['p25']:.2f}" if f else "",
               "flores_p75": f"{f['p75']:.2f}" if f else "",
               "flores_corpus_ratio": f"{f['corpus_ratio']:.2f}" if f else "",
               "flores_fa_tokens": f.get("fa_tokens", ""), "flores_en_tokens": f.get("en_tokens", ""),
               "gpt4o_fa": r["gpt4o_fa"], "gpt4o_en": r["gpt4o_en"]}


def write_outputs(out_dir, date, meta, rows):
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = sorted(rows, key=lambda r: r["pairs"]["median"])
    with open(out_dir / f"crosscheck-{date}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS)
        w.writeheader()
        w.writerows(csv_rows(rows))
    (out_dir / f"crosscheck-{date}.json").write_text(
        json.dumps({**meta, "tokenizers": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    return rows


def print_table(rows, flores):
    print(f"{'tokenizer':<14}{'vocab':>9}{'pairs':>7}" + (f"{'FLORES':>8}{'(IQR)':>12}" if flores else "")
          + f"{'gpt4o fa/en':>13}")
    for r in rows:
        line = f"{r['label']:<14}{r['vocab']:>9,}{r['pairs']['median']:>7.2f}"
        if flores:
            f = r["flores"]
            line += f"{f['median']:>8.2f}  {f['p25']:.2f}–{f['p75']:.2f}"
        print(line + f"{r['gpt4o_fa']:>8}/{r['gpt4o_en']}")


def selftest():
    # 1. stats
    s = ratio_stats([3, 4, 6], [2, 2, 2])
    assert s["median"] == 2.0 and abs(s["corpus_ratio"] - 13 / 6) < 1e-9 and s["share_fa_more"] == 1.0
    assert q([1, 2, 3, 4], .5) == 2.5
    # 2. tarball reader on an in-memory tar with the real member names
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for lang, text in (("fa", "سلام دنیا\nخداحافظ"), ("en", "hello world\nbye")):
            data = text.encode("utf-8")
            ti = tarfile.TarInfo("./" + FLORES_MEMBERS[lang])
            ti.size = len(data)
            t.addfile(ti, io.BytesIO(data))
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d) / "flores.tar.gz"
        tmp.write_bytes(buf.getvalue())
        fa, en = read_flores(tmp)
        assert fa == ["سلام دنیا", "خداحافظ"] and en == ["hello world", "bye"]
        assert len(sha256(tmp)) == 64

    # 3. measure + outputs with a fake tokenizer (characters = tokens)
    class Fake:
        label, version, vocab, note = "chars", "fake", 0, "selftest"

        @staticmethod
        def count(text):
            return len(text)
    pairs = [{"fa": "ابپ", "en": "ab"}, {"fa": "ت", "en": "abcd"}]
    row = measure(Fake, pairs, (fa, en))
    assert row["pairs"]["n"] == 2 and row["flores"]["fa_tokens"] == 16 and row["gpt4o_fa"] == len(GPT4O_FA)
    rows = list(csv_rows([row]))
    assert rows[0]["pairs_median"] == f"{statistics.median([1.5, 0.25]):.2f}"
    assert set(rows[0]) == set(CSV_COLS)
    # 4. config sanity: pinned revisions, unique labels across both lists
    import count_tokens
    labels = [t[0] for t in count_tokens.TOKENIZERS + EXTRA]
    assert len(labels) == len(set(labels))
    assert all(len(t[3]) == 40 for t in EXTRA)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--flores", help="path to flores200_dataset.tar.gz (omit to skip FLORES)")
    ap.add_argument("--corpus", default=str(HERE / "corpus" / "pairs.jsonl"))
    ap.add_argument("--out-dir", default=str(HERE / "derived"))
    ap.add_argument("--offline", action="store_true", help="only use local caches")
    ap.add_argument("--only", nargs="*", help="labels to run")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    import count_tokens
    pairs = count_tokens.load_pairs(Path(a.corpus))
    flores = read_flores(a.flores) if a.flores else None
    rows, skipped = [], []
    for spec in count_tokens.TOKENIZERS + EXTRA:
        if a.only and spec[0] not in a.only:
            continue
        try:
            tok = count_tokens.Tok(*spec, offline=a.offline)
        except Exception as e:  # graceful skip, like count_tokens.py
            skipped.append({"label": spec[0], "reason": f"{type(e).__name__}: {str(e)[:140]}"})
            print(f"SKIPPED {spec[0]}: {type(e).__name__}", file=sys.stderr)
            continue
        rows.append(measure(tok, pairs, flores))
        print(f"done    {spec[0]}", file=sys.stderr)
    if not rows:
        sys.exit("no tokenizer could be loaded")
    meta = {"date": a.date, "python": platform.python_version(), "n_pairs": len(pairs),
            "flores": {"file": Path(a.flores).name, "sha256": sha256(a.flores),
                       "members": FLORES_MEMBERS, "n_sentences": len(flores[0])} if flores else None,
            "gpt4o_sentence": {"fa": GPT4O_FA, "en": GPT4O_EN, "openai_claim": GPT4O_CLAIM,
                               "source": "https://openai.com/index/hello-gpt-4o/"},
            "skipped": skipped}
    rows = write_outputs(Path(a.out_dir), a.date, meta, rows)
    print_table(rows, flores)


if __name__ == "__main__":
    main()
