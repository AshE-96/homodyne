---
title: "How to audit a benchmark answer key: data and protocol"
description: "MMLU-Redux, label-error research and SimpleQA Verified, plus a reproducible toy demo and a step-by-step protocol for auditing a benchmark answer key."
lang: en
translationKey: hmd-008-deep-dive
hmd: HMD-008
kind: deep-dive
date: 2027-01-08
tags: ["answer key", "label errors", "audit", "Wilson interval", "reproducibility"]
sources:
  - title: "Gema et al. (2024): Are We Done with MMLU?, arXiv 2406.04127"
    url: "https://arxiv.org/abs/2406.04127"
  - title: "Northcutt, Athalye, Mueller (NeurIPS 2021): Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks, arXiv 2103.14749"
    url: "https://arxiv.org/abs/2103.14749"
  - title: "SimpleQA Verified, arXiv 2509.07968 (v2, 10 March 2026)"
    url: "https://arxiv.org/abs/2509.07968"
  - title: "Global MMLU, arXiv 2412.03304"
    url: "https://arxiv.org/abs/2412.03304"
  - title: "BetterBench, arXiv 2411.12990"
    url: "https://arxiv.org/abs/2411.12990"
  - title: "Mehr News (1 Shahrivar 1405 / August 2026): preliminary Konkur key and objections (Persian)"
    url: "https://www.mehrnews.com/news/6925042"
  - title: "Etemad Online (6 Mordad 1400 / July 2021): Sanjesh head on removing two questions (Persian)"
    url: "https://www.etemadonline.com/%D8%A8%D8%AE%D8%B4-%D8%A7%D8%AC%D8%AA%D9%85%D8%A7%D8%B9%DB%8C-23/507687-%D8%B3%D9%88%D8%A7%D9%84-%D8%B1%DB%8C%D8%A7%D8%B6%DB%8C-%D8%A7%D8%B2-%DA%A9%D9%86%DA%A9%D9%88%D8%B1-%D8%AD%D8%B0%D9%81"
datasets:
  - title: "MMLU (Hendrycks et al.)"
    url: "https://github.com/hendrycks/test"
    license: "MIT"
  - title: "MMLU-Redux 2.0 (Gema et al.), Hugging Face dataset card"
    url: "https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux-2.0"
    license: "CC BY 4.0"
  - title: "SimpleQA Verified, Hugging Face dataset card"
    url: "https://huggingface.co/datasets/google/simpleqa-verified"
    license: "MIT"
  - title: "Global MMLU, Hugging Face dataset card"
    url: "https://huggingface.co/datasets/CohereLabs/Global-MMLU"
    license: "Apache 2.0"
  - title: "key_audit_demo.py, key-v1.csv and key-v2.csv (Homodyne, ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/tree/main/parts/02-benchmarking/e04-who-decides-the-right-answer/artifact"
    license: "Homodyne repository; see LICENSE.md"
  - title: "bluff_lab.py (Homodyne)"
    url: "https://github.com/AshE-96/homodyne/tree/main/tools"
    license: "Homodyne repository; see LICENSE.md"
---

Auditing an answer key means re-checking a sample of it against sources, so that you both find errors and can say what share of the whole key is wrong. Those two goals need different methods: to find errors, read the suspicious items; to estimate the error rate, you need a random sample with a stated denominator. This post collects the data and research behind [episode HMD-008](/en/episodes/hmd-008/), a formula for how key errors move scores, the commands to reproduce the episode's demo, and a step-by-step audit protocol.

If you have not seen the episode, start with the [companion post](/en/blog/hmd-008-wrong-answer-key/). The [Persian version of this deep dive](/fa/blog/hmd-008-answer-key-audit/) is the original.

> **Key Takeaways**
> - Observed score = true score, minus correct answers the wrong key throws away, plus answers that happen to match the wrong key.
> - An audit of suspicious items only measures a detector's yield, not an error rate: 8 of 36 (22%) in our demo against a planted rate of 8%.
> - For a rate, report a random sample with a Wilson interval; use two blind reviewers; settle disagreements with evidence and a logged reason.
> - All demo numbers are ILLUSTRATIVE. The Bluff pilot audit has not been run.

## Which data and studies does this episode rely on?

| Data or study | What it contains | Size and version | Licence |
|---|---|---|---|
| MMLU | Multiple-choice questions across 57 subjects | Fixed set | MIT ([LICENSE](https://github.com/hendrycks/test/blob/master/LICENSE)) |
| MMLU-Redux (Gema et al., 2024) | Manual re-annotation | 5,700 questions across all 57 subjects | CC BY 4.0 ([dataset card](https://huggingface.co/datasets/edinburgh-dawg/mmlu-redux-2.0)) |
| Northcutt et al. (NeurIPS 2021) | Label errors in test sets | Ten datasets; images, text and audio | Paper only; no data reused here |
| SimpleQA Verified | Rebuilt short-answer QA benchmark | 1,000 prompts; v2, 10 March 2026 | MIT ([dataset card](https://huggingface.co/datasets/google/simpleqa-verified)) |
| Global MMLU | Multilingual version and cultural-dependence analysis | 42 languages | Apache 2.0 ([dataset card](https://huggingface.co/datasets/CohereLabs/Global-MMLU)) |
| `key_audit_demo.py` | 100-question quiz with two fictional models | 100 items, 8 planted errors; **ILLUSTRATIVE** | Homodyne repository |

Headline findings, from these sources' abstracts: MMLU-Redux estimates that 6.49% of MMLU questions contain errors, and in Virology 57% of the analysed questions had errors ([arXiv 2406.04127](https://arxiv.org/abs/2406.04127)). Northcutt and colleagues report an average of at least 3.3% label errors across ten datasets and at least 6% in the ImageNet validation set. They also show that on corrected labels, a rise of just 6% in the share of originally mislabelled examples lets ResNet-18 outperform ResNet-50 ([arXiv 2103.14749](https://arxiv.org/abs/2103.14749)). Global MMLU finds that 28% of questions require culturally sensitive knowledge and 84.9% of geography questions focus on North America or Europe ([arXiv 2412.03304](https://arxiv.org/abs/2412.03304)).

Licences above were read from each dataset card or repository on 7 November 2026. They can change; check each project's dataset card or repository before republishing any question. The episode shows no questions from SimpleQA Verified.

## How much can a key error move a score?

For model m on N questions, let B be the set of questions whose key is wrong:

```text
observed_m = true_m - R_m + M_m

R_m = items in B that model m answered correctly       (points lost)
M_m = items in B where m's answer equals the wrong key  (points gained)

random key errors at rate e, independent of difficulty:
E[R_m] ≈ true_m × e        and   M_m ≈ 0 for typos
```

The first term is the episode's "first rule": R comes only from correct answers, so a model with a higher true score loses more on average. The second term, M, is positive only when the key error matches what the model says, which is exactly the "popular myth" case.

The demo makes this decomposition visible (ILLUSTRATIVE). On the 92 clean questions, K answers 73 correctly and P answers 74. On the eight planted questions, K gets seven right and P gets two, answering the other six with the popular myth:

| | True score | R (lost) | M (gained) | Observed score |
|---|---|---|---|---|
| K, "popular myth" key | 80 | 7 | 0 | 73 |
| P, "popular myth" key | 76 | 2 | 6 | 80 |
| K, "typo" key | 80 | 7 | 0 | 73 |
| P, "typo" key | 76 | 2 | 0 | 74 |

The true gap is four points in K's favour. Under the "popular myth" key it becomes seven points in P's favour, and under the "typo" key one point in P's favour. The planted items are deliberately ones K mostly knows; in a real benchmark we do not know how key errors are distributed, which is the reason to audit.

## How do I reproduce the episode's demo?

Python 3, standard library only. From the root of the Homodyne repository:

```bash
python3 parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/key_audit_demo.py
python3 tools/bluff_lab.py score parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/key-v1.csv --condition plain
python3 tools/bluff_lab.py score parts/02-benchmarking/e04-who-decides-the-right-answer/artifact/key-v2.csv --condition plain
```

The first command prints four sections. `key-v1.csv` and `key-v2.csv` are already in the artifact folder; the script's `--write-csv` flag would overwrite them, so you do not need it to reproduce these numbers. The quiz is deterministic and the audit sample uses a fixed seed (8), so the output should match the run recorded on 2 November 2026:

| Output section | Expected value |
|---|---|
| 1. Scoreboard | key v1: K=73, P=80, leader P · key v2: K=80, P=76, leader K |
| 2. Same eight errors as typos | K=73, P=74 |
| 3. Audit | suspicious only: 8/36 = 22% · random 30: 3/30, 95% Wilson interval 3% to 26% · planted rate 8% |
| 4. Adjudication log | raw agreement 11/12 |

In the `bluff_lab.py` output, read `accuracy_all_prompts`: 0.73 and 0.80 for K and P under key v1, and 0.80 and 0.76 under key v2. The `plain` condition means a prompt that stated no penalty; the tool rescores it at k = 3 only as a diagnostic, so `score_points_per_prompt` is not the point of this demo.

## Why does the audit denominator change everything?

Because there are two different questions. "Where are the errors?" is answered by a targeted search. "What share of the key is wrong?" can only be answered by a sample in which every item's chance of selection is known.

In the demo, the suspicious set is every question where at least one model disagreed with the key: the eight planted items plus 28 clean items that one of the models got wrong. Eight of 36 is 22%; that is the detector's precision, not the prevalence of errors. The method also has a blind spot: if every model repeats the same myth as the key, no one disagrees and that error never enters the suspicious list.

For prevalence, draw a random sample and report a confidence interval. The Wilson interval for x errors in n items:

```text
p = x / n,  z = 1.96
center = (p + z²/(2n)) / (1 + z²/n)
half   = z × sqrt(p(1 - p)/n + z²/(4n²)) / (1 + z²/n)
CI95   = [center - half, center + half]
```

With x = 3 and n = 30, the interval runs from about 3% to 26%. It is wide because thirty items is a small sample, but it is honest and contains the true 8%. If you want both a targeted search and a prevalence estimate, stratify: sample the suspicious set and the remaining items separately and weight each stratum by its size.

## What steps should a key audit follow?

This protocol draws on the Bluff scoring guide (`examples/bluff-v1/production-v3/scoring-guide.md`) and the episode's reasoning. It is a draft and has not been tested on a pilot.

1. **Freeze and version the key.** Publish v1 with a hash and never edit it in place.
2. **Give every question a file:** text, accepted answers and alternative spellings, primary source, date checked, and for time-sensitive questions an "as of" date.
3. **Lock normalisation rules before seeing results.** Merge safe spelling variants, but never erase units, dates or meaningful negation.
4. **Estimate prevalence with a random sample.** Report the seed, selection method, n and Wilson interval; stratify by language or subject if you have several.
5. **Report targeted searches separately,** as "found out of reviewed", never as an error rate.
6. **Use two independent, blind reviewers.** Neither should know which model gave which answer. Look at the disagreement matrix, not only raw agreement.
7. **Resolve disagreements with evidence, not votes.** Log the decision, the source and the reason.
8. **Do not fill a missing source with a guess.** Rewrite or remove the question and mark it.
9. **Check translations separately:** added clues, new ambiguities and cultural dependence.
10. **Publish v2 with a changelog:** question, old key, new key or removal, evidence and reason. Score every model under both versions and report both.
11. **Keep an objection window open.** Iran's national university entrance exam, the Konkur, runs this cycle: a preliminary key is published, objections are accepted only through an electronic system (Mehr News, August 2026), and the final key sometimes removes questions; in 2021 the head of the testing organisation announced that two questions would be removed ([Etemad Online](https://www.etemadonline.com/%D8%A8%D8%AE%D8%B4-%D8%A7%D8%AC%D8%AA%D9%85%D8%A7%D8%B9%DB%8C-23/507687-%D8%B3%D9%88%D8%A7%D9%84-%D8%B1%DB%8C%D8%A7%D8%B6%DB%8C-%D8%A7%D8%B2-%DA%A9%D9%86%DA%A9%D9%88%D8%B1-%D8%AD%D8%B0%D9%81)).

In the demo, the adjudication log covers the eight planted items and four clean ones. The reviewers agree on 11 of 12, and the disagreement is on the capital of Myanmar, exactly where step 7 sends you to a primary source. These 12 items are not a representative sample, so 11 of 12 says nothing about reviewer quality in a real audit.

SimpleQA Verified is a published example of this cycle: a benchmark rebuilt to fix noisy and incorrect labels, topical bias and redundancy ([arXiv 2509.07968](https://arxiv.org/abs/2509.07968)). BetterBench likewise treats versioning and maintenance as part of benchmark lifecycle quality ([arXiv 2411.12990](https://arxiv.org/abs/2411.12990)).

## What are the limits of this method?

- **The demo:** 100 questions, two fictional models and errors chosen to show the mechanism. It tells you nothing about the real distribution of key errors in any benchmark.
- **The MMLU-Redux estimate** depends on that group's annotation protocol and sampling; the 57% refers to analysed Virology questions, not all of MMLU.
- **Northcutt's figures** are lower bounds ("at least") and concern classification models, not chatbots.
- **The Wilson interval** assumes independent items. Translations of one question are not independent and should be sampled together.
- **Blind reviewers** can still share a misconception; blinding does not replace evidence.
- **Konkur** is a process analogy only; we have no figures on Konkur key error rates.

## What this does not show

- It does not show that any real model's ranking today is wrong, or what share of key errors any specific benchmark has today.
- The 6.49% figure is one research group's estimate for MMLU, not a rate for all benchmarks.
- Failing to find a source in a search does not mean no answer exists.
- The 60-question Bluff pilot audit has not been run. No number from it appears here; the real result will be published separately.

## Further reading

- MMLU-Redux and its re-annotation method: [Are We Done with MMLU?](https://arxiv.org/abs/2406.04127).
- Label errors across ten test sets: [Pervasive Label Errors in Test Sets](https://arxiv.org/abs/2103.14749).
- Rebuilding a short-answer QA benchmark: [SimpleQA Verified](https://arxiv.org/abs/2509.07968).
- Cultural dependence in benchmark questions: [Global MMLU](https://arxiv.org/abs/2412.03304).
- Reading the numerator and denominator of a model's own error rates: [HMD-006 deep dive](/en/blog/hmd-006-abstention-metrics/).
