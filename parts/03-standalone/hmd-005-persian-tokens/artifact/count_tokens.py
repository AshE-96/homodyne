#!/usr/bin/env python3
"""Homodyne HMD-005 — count tokens for paired Persian/English texts.

What it does
  * Reads corpus/pairs.jsonl (50 self-written fa/en pairs, 7 domains).
  * Counts tokens with every tokenizer it can load (tiktoken encodings and
    open Hugging Face tokenizers). A tokenizer that cannot be loaded is SKIPPED
    and listed as skipped; the run does not fail.
  * Reports, per tokenizer: median fa/en token ratio, quartiles, p10/p90,
    min/max, whole-corpus ratio, per-domain medians.
  * Runs three orthographic controls on the Persian side only:
      zwnj_space   ZWNJ (U+200C, nim-fasele) typed as a normal space
      zwnj_none    ZWNJ deleted (letters joined)
      arabic_yk    Persian yeh/kaf (U+06CC/U+06A9) replaced by Arabic ي/ك
      latin_digits Persian digits ۰-۹ replaced by 0-9
      arabic_digits Persian digits replaced by Arabic-Indic ٠-٩
    and reports the median % change in Persian token count on the rows the
    control actually changes.
  * Prints how one demo sentence is split, token by token.

Outputs (written next to this file unless --out-dir is given)
  results-YYYY-MM-DD.md    human-readable report (used in the episode)
  results-YYYY-MM-DD.json  every count, for re-analysis

Usage
  python3 count_tokens.py                 # all tokenizers it can load
  python3 count_tokens.py --offline       # only use local caches
  python3 count_tokens.py --only o200k_base cl100k_base

Requirements: Python 3.10+, tiktoken (tested 0.9.0). Optional: transformers +
tokenizers (tested 4.49.0 / 0.21.0) for the open tokenizers. Some HF repos
below are community mirrors of the original tokenizer files (the originals are
gated); they are pinned to an exact commit so the run is reproducible.

Claim boundary: more tokens is not lower quality, and the ratio depends on the
tokenizer and the text. This corpus is small and self-written.
"""
import argparse
import datetime as dt
import json
import os
import platform
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ZWNJ = "\u200c"
FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"
DEMO = "می‌خواهم اشتراکم را لغو کنم و هزینه‌ی ماه آخر را پس بگیرم."
DEMO_EN = "I want to cancel my subscription and get a refund for the last month."

# (label, kind, id, revision, note). HF revisions = the exact commits used on 2026-11-02.
TOKENIZERS = [
    ("o200k_base", "tiktoken", "o200k_base", None,
     "tiktoken map: gpt-4o, o1, o3"),
    ("cl100k_base", "tiktoken", "cl100k_base", None,
     "tiktoken map: gpt-4, gpt-3.5-turbo"),
    ("gpt2 (r50k)", "tiktoken", "gpt2", None,
     "GPT-2 era, historical baseline"),
    ("Llama-2", "hf", "NousResearch/Llama-2-7b-hf",
     "8efe6c9b93655b934e27bd9981e3ec13e55aee9d", "32k SentencePiece; mirror"),
    ("Llama-3.2", "hf", "unsloth/Llama-3.2-1B-Instruct",
     "5a8abab4a5d6f164389b1079fb721cfab8d7126c", "128k BPE; mirror"),
    ("Gemma-3", "hf", "unsloth/gemma-3-1b-it", "5b11413a10db4e486ef16a20101fd028f8f2499c", "262k SentencePiece; mirror"),
    ("Qwen3", "hf", "Qwen/Qwen3-8B", "b968826d9c46dd6066d109eabc6255188de91218", "151k BPE"),
    ("DeepSeek-V3", "hf", "deepseek-ai/DeepSeek-V3", "e815299b0bcbac849fa540c768ef21845365c9eb", "128k BPE"),
    ("Mistral-Nemo", "hf", "mistralai/Mistral-Nemo-Instruct-2407", "04d8a90549d23fc6bd7f642064003592df51e9b3",
     "131k BPE (Tekken)"),
]


def load_pairs(path):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for r in rows:  # canonical Persian orthography
        r["fa"] = r["fa"].replace("\u064a", "\u06cc").replace("\u0643", "\u06a9")
    return rows


def variants(fa):
    return {
        "zwnj_space": fa.replace(ZWNJ, " "),
        "zwnj_none": fa.replace(ZWNJ, ""),
        "arabic_yk": fa.replace("\u06cc", "\u064a").replace("\u06a9", "\u0643"),
        "latin_digits": fa.translate(str.maketrans(FA_DIGITS, "0123456789")),
        "arabic_digits": fa.translate(str.maketrans(FA_DIGITS, AR_DIGITS)),
    }


class Tok:
    def __init__(self, label, kind, ident, revision, note, offline):
        self.label, self.kind, self.ident, self.note = label, kind, ident, note
        self.version = ""
        if kind == "tiktoken":
            import tiktoken
            self.enc = tiktoken.get_encoding(ident)
            self.version = f"tiktoken {tiktoken.__version__}"
            self.vocab = self.enc.n_vocab
        else:
            os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
            from transformers import AutoTokenizer
            import transformers
            kw = {"local_files_only": offline}
            if revision:
                kw["revision"] = revision
            self.enc = AutoTokenizer.from_pretrained(ident, **kw)
            sha = revision or self._sha(ident, offline)
            self.version = f"{ident}@{sha[:12] if sha else 'unknown'} · transformers {transformers.__version__}"
            self.vocab = len(self.enc)

    @staticmethod
    def _sha(ident, offline):
        try:
            from huggingface_hub import hf_hub_download
            p = hf_hub_download(ident, "tokenizer_config.json", local_files_only=offline)
            parts = Path(p).parts
            return parts[parts.index("snapshots") + 1]
        except Exception:
            return ""

    @staticmethod
    def _hex(piece):
        """Show a partial-UTF-8 token as hex bytes (byte-level BPE or <0xNN> byte fallback)."""
        if piece.startswith("<0x") and piece.endswith(">"):
            return piece[3:-1].lower()
        bs = list(range(33, 127)) + list(range(161, 173)) + list(range(174, 256))
        cs, n = bs[:], 0
        for b in range(256):
            if b not in bs:
                bs.append(b)
                cs.append(256 + n)
                n += 1
        inv = {chr(c): b for b, c in zip(bs, cs)}
        try:
            return bytes(inv[ch] for ch in piece).hex()
        except KeyError:
            return piece

    def ids(self, text):
        if self.kind == "tiktoken":
            return self.enc.encode(text)
        return self.enc.encode(text, add_special_tokens=False)

    def count(self, text):
        return len(self.ids(text))

    def pieces(self, text):
        out = []
        if self.kind == "tiktoken":
            for i in self.ids(text):
                b = self.enc.decode_single_token_bytes(i)
                try:
                    out.append(b.decode("utf-8"))
                except UnicodeDecodeError:
                    out.append("<" + b.hex() + ">")
        else:
            for i in self.ids(text):
                s = self.enc.decode([i])
                out.append(s if "\ufffd" not in s else "<" + self._hex(self.enc.convert_ids_to_tokens(i)) + ">")
        return out


def q(values, p):
    v = sorted(values)
    k = (len(v) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def summarise(ratios):
    return {
        "median": statistics.median(ratios), "p10": q(ratios, .10), "p25": q(ratios, .25),
        "p75": q(ratios, .75), "p90": q(ratios, .90), "min": min(ratios), "max": max(ratios),
        "share_fa_more": sum(r > 1 for r in ratios) / len(ratios),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--corpus", default=str(HERE / "corpus" / "pairs.jsonl"))
    ap.add_argument("--out-dir", default=str(HERE))
    ap.add_argument("--offline", action="store_true", help="only use local caches")
    ap.add_argument("--only", nargs="*", help="labels or ids to run")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    a = ap.parse_args()

    pairs = load_pairs(Path(a.corpus))
    toks, skipped = [], []
    for spec in TOKENIZERS:
        if a.only and spec[0] not in a.only and spec[2] not in a.only:
            continue
        try:
            toks.append(Tok(*spec, offline=a.offline))
            print(f"loaded  {spec[0]}", file=sys.stderr)
        except Exception as e:  # graceful skip
            skipped.append({"label": spec[0], "id": spec[2], "reason": f"{type(e).__name__}: {str(e)[:140]}"})
            print(f"SKIPPED {spec[0]}: {type(e).__name__}", file=sys.stderr)
    if not toks:
        sys.exit("no tokenizer could be loaded")

    data = {"date": a.date, "python": platform.python_version(), "corpus": Path(a.corpus).name,
            "n_pairs": len(pairs), "tokenizers": [], "skipped": skipped, "rows": []}
    for r in pairs:
        row = {"id": r["id"], "domain": r["domain"], "fa_chars": len(r["fa"]), "en_chars": len(r["en"]),
               "fa_words": len(r["fa"].replace(ZWNJ, "").split()), "en_words": len(r["en"].split()),
               "counts": {}}
        v = variants(r["fa"])
        for t in toks:
            c = {"fa": t.count(r["fa"]), "en": t.count(r["en"])}
            for name, text in v.items():
                if text != r["fa"]:
                    c[name] = t.count(text)
            row["counts"][t.label] = c
        data["rows"].append(row)

    domains = sorted({r["domain"] for r in pairs})
    controls = ["zwnj_space", "zwnj_none", "arabic_yk", "latin_digits", "arabic_digits"]
    for t in toks:
        rows = data["rows"]
        ratios = [x["counts"][t.label]["fa"] / x["counts"][t.label]["en"] for x in rows]
        fa_sum = sum(x["counts"][t.label]["fa"] for x in rows)
        en_sum = sum(x["counts"][t.label]["en"] for x in rows)
        no_digit_rows = [x for x in rows if "latin_digits" not in x["counts"][t.label]]
        latin_ratio = [x["counts"][t.label].get("latin_digits", x["counts"][t.label]["fa"]) / x["counts"][t.label]["en"] for x in rows]
        ctrl = {}
        for cname in controls:
            ch = [(x["counts"][t.label][cname] - x["counts"][t.label]["fa"]) / x["counts"][t.label]["fa"]
                  for x in rows if cname in x["counts"][t.label]]
            if ch:
                ctrl[cname] = {"n_rows": len(ch), "median_change": statistics.median(ch),
                               "mean_change": statistics.mean(ch), "min": min(ch), "max": max(ch),
                               "total_change": sum(x["counts"][t.label][cname] for x in rows if cname in x["counts"][t.label])
                               / sum(x["counts"][t.label]["fa"] for x in rows if cname in x["counts"][t.label]) - 1}
        data["tokenizers"].append({
            "label": t.label, "version": t.version, "vocab": t.vocab, "note": t.note,
            "ratio": summarise(ratios), "corpus_ratio": fa_sum / en_sum, "fa_tokens": fa_sum, "en_tokens": en_sum,
            "ratio_latin_digits_median": statistics.median(latin_ratio),
            "ratio_no_number_rows_median": statistics.median(
                [x["counts"][t.label]["fa"] / x["counts"][t.label]["en"] for x in no_digit_rows]),
            "fa_chars_per_token": sum(x["fa_chars"] for x in rows) / fa_sum,
            "en_chars_per_token": sum(x["en_chars"] for x in rows) / en_sum,
            "domain_median": {d: statistics.median([x["counts"][t.label]["fa"] / x["counts"][t.label]["en"]
                                                    for x in rows if x["domain"] == d]) for d in domains},
            "controls": ctrl,
            "demo": {"fa": t.pieces(DEMO), "en": t.pieces(DEMO_EN)},
        })

    rows = data["rows"]
    data["char_ratio_median"] = statistics.median([x["fa_chars"] / x["en_chars"] for x in rows])
    data["word_ratio_median"] = statistics.median([x["fa_words"] / x["en_words"] for x in rows])
    out = Path(a.out_dir)
    (out / f"results-{a.date}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / f"results-{a.date}.md").write_text(report(data, domains, controls), encoding="utf-8")
    print(report(data, domains, controls))


def pct(x):
    return f"{x*100:+.1f}%"


def report(d, domains, controls):
    L = [f"# HMD-005 token count — results {d['date']}", "",
         f"Corpus: `{d['corpus']}` · {d['n_pairs']} self-written fa/en pairs · Python {d['python']}.",
         "Ratio = Persian tokens ÷ English tokens for the SAME pair (>1 = Persian needs more tokens).",
         "Special tokens (BOS/EOS) are not counted. Canonical Persian: Persian ی/ک, ZWNJ, Persian digits.",
         f"Median character ratio fa/en: {d['char_ratio_median']:.2f} · median word ratio fa/en: {d['word_ratio_median']:.2f}.",
         "", "**Claim boundary:** more tokens ≠ lower quality. Ratios depend on the tokenizer and the text. "
         "Small, self-written corpus; not a representative sample of Persian.", "",
         "## 1. Persian ÷ English token ratio per tokenizer", "",
         "| tokenizer | version / revision | vocab | median | IQR (p25–p75) | p10–p90 | min–max | corpus total | fa > en |",
         "|---|---|---:|---:|---|---|---|---:|---:|"]
    for t in sorted(d["tokenizers"], key=lambda t: t["ratio"]["median"]):
        r = t["ratio"]
        L.append(f"| {t['label']} | {t['version']} | {t['vocab']:,} | **{r['median']:.2f}** | {r['p25']:.2f}–{r['p75']:.2f} | "
                 f"{r['p10']:.2f}–{r['p90']:.2f} | {r['min']:.2f}–{r['max']:.2f} | {t['corpus_ratio']:.2f} "
                 f"({t['fa_tokens']}/{t['en_tokens']}) | {r['share_fa_more']*100:.0f}% |")
    L += ["", "## 2. Median ratio by domain", "",
          "| tokenizer | " + " | ".join(domains) + " |", "|---|" + "---:|" * len(domains)]
    for t in sorted(d["tokenizers"], key=lambda t: t["ratio"]["median"]):
        L.append(f"| {t['label']} | " + " | ".join(f"{t['domain_median'][x]:.2f}" for x in domains) + " |")
    L += ["", "## 3. Orthography controls (Persian side only)", "",
          "Median % change in the Persian token count on the rows the control changes (n rows in header).", ""]
    ns = {c: next((t["controls"][c]["n_rows"] for t in d["tokenizers"] if c in t["controls"]), 0) for c in controls}
    L += ["| tokenizer | " + " | ".join(f"{c} (n={ns[c]})" for c in controls) + " |", "|---|" + "---:|" * len(controls)]
    for t in sorted(d["tokenizers"], key=lambda t: t["ratio"]["median"]):
        L.append(f"| {t['label']} | " + " | ".join(
            f"{pct(t['controls'][c]['median_change'])} ({pct(t['controls'][c]['min'])}…{pct(t['controls'][c]['max'])})"
            if c in t["controls"] else "—" for c in controls) + " |")
    L += ["", "Sensitivity: median fa/en ratio if Persian digits are typed as Latin digits, and on rows without numbers.", "",
          "| tokenizer | canonical | Latin digits | rows without digits | chars/token fa | chars/token en |", "|---|---:|---:|---:|---:|---:|"]
    for t in sorted(d["tokenizers"], key=lambda t: t["ratio"]["median"]):
        L.append(f"| {t['label']} | {t['ratio']['median']:.2f} | {t['ratio_latin_digits_median']:.2f} | "
                 f"{t['ratio_no_number_rows_median']:.2f} | {t['fa_chars_per_token']:.2f} | {t['en_chars_per_token']:.2f} |")
    L += ["", "## 4. One sentence, token by token", "", f"fa: `{DEMO}`", f"en: `{DEMO_EN}`",
          "[ZWNJ] marks the invisible half-space; <hex> marks a token that is only part of a character (raw UTF-8 bytes).", ""]
    for t in d["tokenizers"]:
        L.append(f"- **{t['label']}** fa {len(t['demo']['fa'])} · en {len(t['demo']['en'])}: "
                 + " | ".join(x.replace(ZWNJ, "[ZWNJ]") for x in t["demo"]["fa"]))
    L += ["", "## 5. Cost as a formula (no prices asserted)", "",
          "input_cost = tokens_in × price_in_per_token; output_cost = tokens_out × price_out_per_token.",
          "For the same content and the same price list, Persian input cost ≈ ratio × English input cost.",
          "Prices: [VERIFY] on the provider's official pricing page on the day of use; output tokens are priced separately.", ""]
    if d["skipped"]:
        L += ["## Skipped tokenizers", ""] + [f"- {s['label']} (`{s['id']}`): {s['reason']}" for s in d["skipped"]] + [""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
