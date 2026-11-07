---
title: "Refutable AI results: SHA-256 manifest, anchor and log"
description: "A checkable bundle for a benchmark score: recompute vs rerun, a SHA-256 manifest, an outside anchor, versioning and the recompute_check.py commands."
lang: en
translationKey: hmd-018-deep-dive
hmd: HMD-018
kind: deep-dive
date: 2027-03-26
tags: ["reproducibility", "SHA-256", "manifest", "correction log", "versioning", "benchmarks"]
sources:
  - title: "NeurIPS 2026 Paper Checklist Guidelines (read 7 November 2026)"
    url: "https://neurips.cc/public/guides/PaperChecklist"
  - title: "NeurIPS blog (4 May 2026). MLRC 2026: Reproducibility as an Official Track at NeurIPS"
    url: "https://blog.neurips.cc/2026/05/04/mlrc-2026-reproducibility-as-an-official-track-at-neurips/"
  - title: "NIST FIPS 180-4, Secure Hash Standard (August 2015)"
    url: "https://csrc.nist.gov/pubs/fips/180-4/upd1/final"
  - title: "Liang et al. (2022; TMLR 2023). Holistic Evaluation of Language Models. arXiv 2211.09110"
    url: "https://arxiv.org/abs/2211.09110"
  - title: "Mitchell et al. (2018; FAT* 2019). Model Cards for Model Reporting. arXiv 1810.03993"
    url: "https://arxiv.org/abs/1810.03993"
  - title: "Gebru et al. (2018; CACM 2021). Datasheets for Datasets. arXiv 1803.09010"
    url: "https://arxiv.org/abs/1803.09010"
  - title: "COPE Retraction Guidelines"
    url: "https://publicationethics.org/guidance/guideline/retraction-guidelines"
  - title: "Retraction Watch (4 September 2025). New COPE retraction guidelines"
    url: "https://retractionwatch.com/2025/09/04/new-cope-retraction-guidelines-address-paper-mills-third-parties-and-more/"
  - title: "OpenAI (23 February 2026). Why we no longer evaluate SWE-bench Verified"
    url: "https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/"
  - title: "AI Weekly: OpenAI drops SWE-Bench Verified after flaw audit (secondary source)"
    url: "https://aiweekly.co/alerts/openai-drops-swe-bench-verified-backs-pro-after-flaw-audit"
datasets:
  - title: "recompute_check.py (Homodyne, HMD-018)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e09-how-do-you-publish-a-refutable-result/artifact/recompute_check.py"
    license: "MIT (repository LICENSE.md)"
  - title: "bluff-demo.csv: 20 rows, two fictional models (ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff-demo.csv"
    license: "Homodyne repository; see LICENSE.md"
  - title: "bluff_lab.py: the course scorer"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff_lab.py"
    license: "MIT (repository LICENSE.md)"
  - title: "HELM (Stanford CRFM), evaluation code"
    url: "https://github.com/stanford-crfm/helm"
    license: "Apache 2.0"
---

A refutable result is one any reader can check without trusting the publisher, and point to the error if there is one. For a benchmark score, that means a bundle with the labelled answers, the method, the scoring code, the published score and a correction log; a SHA-256 manifest of all of them; and an "anchor", the hash of the manifest itself, published outside the bundle with a date. This post covers the bundle layout, the checks, four tampering cases and the reproduction commands for `recompute_check.py`. All data is a teaching file (ILLUSTRATIVE).

> **Key Takeaways**
> - A recompute is deterministic: the same bytes and the same code must give exactly the same number. A rerun has no such guarantee.
> - The manifest catches any changed file, the recompute catches a score that disagrees with the answers, and only an outside anchor catches a complete, consistent swap of the bundle.
> - A public correction is the same edit as the fraud, plus a new version, a log entry and a new anchor next to the old one.
> - `recompute_check.py` uses only the Python standard library and calls no model.

This is the technical layer of [episode HMD-018](/en/episodes/hmd-018/). If you have not watched it, start with the [companion post](/en/blog/hmd-018-check-an-ai-score/), which also recaps the whole benchmark course.

## Which data and tools does this episode use?

| Data or tool | What it contains | Size | Licence |
|---|---|---|---|
| `tools/bluff-demo.csv` | 10 questions × 2 fictional models, condition t75 | 20 rows; SHA-256 starts `35ceaaf4` | Homodyne repository |
| `recompute_check.py` | Demo-bundle builder and reader's checker | 299 lines, stdlib only | MIT |
| `tools/bluff_lab.py` | The course's shared scorer (`summaries()`) | — | MIT |
| HELM (Liang et al.) | Evaluation framework that publishes raw prompts and completions | 30 models, 42 scenarios in the paper | Apache 2.0 |

Licences were read from the repositories on 7 November 2026. The demo file is the same teaching file used earlier in the course, copied byte for byte into the bundle, so its hash equals the `input_sha256` that `bluff_lab.py score` prints.

## What exactly does a recompute guarantee?

A recompute is a deterministic function of three inputs: the bytes of `results.csv`, the version of the scoring code, and the scoring rule. If those stay fixed, the output must too. The checker rounds the score to the number of decimals declared in `published.json` (`decimals: 3`) and compares it with the published score.

A rerun has no such guarantee. Models usually sample their answers, and services may change a model version without notice. This episode explains those causes but does not measure them. That is why a bundle must keep the raw answers: a recompute is only possible on stored answers.

## Which files are in the bundle?

```text
bundle/
  results.csv       # item_id,cluster_id,model,condition,repeat,language,split,answerable,label,source_status,response
  METHOD.md         # rule +1 / 0 / −k, condition t75, k = 3, scorer, who labelled
  published.json    # bundle_version, date, condition, penalty_k, decimals, unit, scorer, scores
  CHANGELOG.md      # newest entry first: version, date, item, reason, effect
  MANIFEST.sha256   # "<64 hex>  <filename>" for the four files above
```

The manifest uses the format standard tools expect, so it can be checked without our program. On our demo bundle, `shasum -a 256 -c MANIFEST.sha256` reported `OK` for all four files. The checker also rejects any file that sits in the folder but is not listed in the manifest, so nothing can be added quietly.

In this demo the scoring code is not inside the bundle; it is read from `tools/bluff_lab.py` in the repository. In a real bundle, either list the code in the manifest or record its exact version (for example a commit ID) in `METHOD.md`. This is a deliberate limitation of the demo.

## What does SHA-256 prove, and what not?

SHA-256 is defined in [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) and produces 256 bits, written as 64 hexadecimal characters. Changing one label in the demo file moves the hash from `35ceaaf427d7…` to `0fb34f0c362b…`.

A hash proves a file has not changed since it was hashed. It does not prove that the labels are right, that the data is complete, or that the hash was made on the date claimed. Only something outside the bundle can answer that last question: the anchor.

## In what order does the checker work?

Three checks in sequence; the first mismatch is reported:

1. **Manifest:** if `--anchor` is given, the hash of `MANIFEST.sha256` must equal it. Then every listed file must exist with a matching hash, and no unlisted file may be present.
2. **Correction log:** `bundle_version` in `published.json` must be the first `## v…` heading in `CHANGELOG.md`.
3. **Recompute:** each model's score is computed from `results.csv` with `bluff_lab.summaries()` and compared with the published score, or with a value the user supplies via `--claim`.

The output is PASS or FAIL with exit code 0 or 1, so it also works in scripts and CI.

## Which check catches each tampering case?

In the demo, the published v0.1 scores are −0.100 for A and +0.100 for B (condition t75, k = 3, 10 questions). Every tampering case shares one edit: question q06, model A, Persian, from `wrong` to `correct`. Its effect on A is (1 − (−3)) / 10 = 0.4, from −0.100 to +0.300, which reverses the order of A and B. Output of `--selftest` (run 7 November 2026, ILLUSTRATIVE):

| Case | No anchor | With anchor | First mismatch |
|---|---|---|---|
| `original` | PASS | PASS | — |
| `tamper-csv` (label only) | FAIL | FAIL | hash of `results.csv`: manifest `35ceaaf4…`, file `0fb34f0c…` |
| `tamper-csv-manifest` (+ new manifest) | FAIL | FAIL | no anchor: A published −0.100, recomputed +0.300; with anchor: manifest `55734e42…` |
| `tamper-all` (+ published score) | **PASS** | FAIL | with anchor: manifest `3013a118…` instead of `e6db5cb8…` |
| `correction` (v0.2 + log + new anchor) | PASS | PASS (anchor `57772828…`) | — |

`--selftest` runs one more check: a viewer types the +0.300 they saw on a screenshot for A (`--claim A=0.3`), and the checker FAILs on the original bundle with "claimed +0.300, recomputed −0.100".

The point of the `tamper-all` row is that every internal check measures only whether the bundle agrees with itself. A bundle rebuilt completely and consistently cannot be detected without an outside reference.

## Where and how should the anchor be published?

The anchor is the hash of the manifest: `sha256(MANIFEST.sha256)`. The demo's v0.1 anchor starts `e6db5cb88679`. On release day this string goes, with a date, somewhere that is not the bundle. The test for a good place is whether the publisher can change it silently:

- **A video description or the publisher's own web page:** easy to find, but the publisher can edit it. Weak on its own.
- **A commit in a public git repository:** each commit contains the hash of the one before, so changing the past changes the whole chain. The owner can rewrite their repository's history, but clones other people already made keep the old one.
- **An archived copy, or other people quoting it:** places the publisher does not control.

An anchor makes a silent swap hard, not impossible. Two or three independent places are better than one.

## How do versioning and the correction log work?

The demo's correction adds an entry at the top of `CHANGELOG.md`: version v0.2, a date, the corrected item (q06, model A, Persian), the reason (a reader report: the answer key accepted only one spelling of a name), the effect (A from −0.100 to +0.300; B unchanged), and a commitment that the v0.1 files and anchor stay public next to the entry. The checker only verifies that the published version is the newest entry; whether the reason is convincing needs human judgement.

COPE's retraction guidelines say the main purpose is to correct the record rather than to punish authors, and ask that the notice state the reason. The 2019 guidelines were updated in September 2025 ([Retraction Watch](https://retractionwatch.com/2025/09/04/new-cope-retraction-guidelines-address-paper-mills-third-parties-and-more/)). For a reader's error report, three fields are enough: item ID, evidence and proposed fix.

## What about questions that cannot be published?

Held-out questions, personal data and data without a licence to redistribute can be committed rather than published: release only the hash of the file today and the file itself later. On the day of release, anyone can check that the questions are the ones locked at the start. One caution: if the content is short or guessable, a bare hash can be broken by guessing and testing candidates. Adding a secret random string to the file before hashing, and revealing it with the questions, reduces that risk.

The [NeurIPS 2026 checklist](https://neurips.cc/public/guides/PaperChecklist) formalises the same logic. It includes questions on "Experimental Result Reproducibility", "Open Access to Data and Code", "Experimental Setting/Details", "Experiment Statistical Significance" and "Licenses"; papers without the checklist are desk rejected; and answering "no" or "n/a" is not in itself grounds for rejection. The MLRC reproducibility challenge is an official NeurIPS 2026 track, with its first review stage at the journal TMLR ([NeurIPS blog](https://blog.neurips.cc/2026/05/04/mlrc-2026-reproducibility-as-an-official-track-at-neurips/)).

## A real case: SWE-bench Verified

On 23 February 2026 OpenAI stopped reporting SWE-bench Verified (500 problems). According to secondary sources, of 138 of the hardest problems it audited, about 27.6% of the set, 59.4% had material issues in test design or the problem description ([AI Weekly](https://aiweekly.co/alerts/openai-drops-swe-bench-verified-backs-pro-after-flaw-audit)). That sample was not random, so 59.4% cannot be generalised to all 500 problems. The second reason was training-data contamination. In July 2026 OpenAI also withdrew its recommendation for a replacement. Both cases show that without published answers and tests, such errors surface late.

## How do you reproduce all of this?

From the repository root, with Python 3 only:

```bash
A=parts/02-benchmarking/e09-how-do-you-publish-a-refutable-result/artifact
python3 $A/recompute_check.py --selftest                          # five bundles, each without and with the anchor
python3 $A/recompute_check.py --demo /tmp/b                       # v0.1 bundle; prints the anchor
python3 $A/recompute_check.py /tmp/b --anchor e6db5cb88679bd980353f1188a716a1a34b6d07eb03f3ccc2e6206677eb0ad2b   # PASS
(cd /tmp/b && shasum -a 256 -c MANIFEST.sha256)                   # the same check, without our program
python3 $A/recompute_check.py --demo /tmp/t --variant tamper-all  # the clean fraud
python3 $A/recompute_check.py /tmp/t                              # PASS without an anchor
python3 $A/recompute_check.py /tmp/t --anchor e6db5cb88679bd980353f1188a716a1a34b6d07eb03f3ccc2e6206677eb0ad2b   # FAIL
python3 $A/recompute_check.py /tmp/b --claim A=0.3                # a number from a screenshot: FAIL
python3 $A/recompute_check.py --demo /tmp/c --variant correction  # v0.2 with anchor 577728283b70…
```

`--demo` deletes and recreates the target folder if it exists, so give it an empty or temporary path. `--variant` accepts `original`, `tamper-csv`, `tamper-csv-manifest`, `tamper-all` and `correction`. If `tools/bluff-demo.csv` ever changes, every hash in this post changes too; and if model A's q06 row is no longer in it, the tamper builder stops with an error.

## What this does not show

- A recompute shows the arithmetic is right, not the labels. Wrong judging with correct arithmetic is still wrong.
- It does not show that rerunning a model gives the same answers; we explained the causes of differences but did not measure them.
- An anchor makes a silent swap hard, not impossible, and its strength depends on where it was published.
- The demo bundle is a teaching file: ten questions and two fictional models (ILLUSTRATIVE). No real Bluff result appears here.
- OpenAI's and COPE's pages would not load for our tools; the SWE-bench Verified figures come from consistent secondary sources, and the COPE points from the 2019 text as shown in search results. We quote no figures on SWE-bench Pro or on "the share of irreproducible papers".

## Further reading

- [NeurIPS 2026 Paper Checklist](https://neurips.cc/public/guides/PaperChecklist), especially the reproducibility and open-access items.
- Liang et al., *Holistic Evaluation of Language Models*, [arXiv 2211.09110](https://arxiv.org/abs/2211.09110); code on [GitHub](https://github.com/stanford-crfm/helm).
- Mitchell et al., *Model Cards for Model Reporting*, [arXiv 1810.03993](https://arxiv.org/abs/1810.03993); Gebru et al., *Datasheets for Datasets*, [arXiv 1803.09010](https://arxiv.org/abs/1803.09010).
- [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final), the definition of SHA-256.
- The [HMD-016 deep dive](/en/blog/hmd-016-risk-coverage-preregistration/), on data locks and preregistration for the same test.

*Persian original: [نتیجهٔ ابطال‌پذیر: مانیفست SHA-256، لنگر و دفتر اصلاحیه](/fa/blog/hmd-018-recompute-manifest-anchor/)*
