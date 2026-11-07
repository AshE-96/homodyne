---
title: "Choosing an AI eval: style control, contamination, audits"
description: "How LMArena's style control extends a Bradley-Terry model, a map of 16 benchmark families, the SWE-bench Verified and Pro audits, and a checklist."
lang: en
translationKey: hmd-004-deep-dive
hmd: HMD-004
kind: deep-dive
date: 2026-12-11
tags: ["benchmarks", "style control", "Bradley-Terry", "LMArena", "SWE-bench", "contamination", "benchmark saturation"]
sources:
  - title: "LMSYS · Does style matter? Disentangling style and substance in Chatbot Arena (29 Aug 2024)"
    url: "https://lmsys.org/blog/2024-08-28-style-control/"
  - title: "OpenAI · Why we no longer evaluate SWE-bench Verified (23 Feb 2026)"
    url: "https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/"
  - title: "OpenAI · Separating signal from noise in coding evaluations (8 Jul 2026)"
    url: "https://openai.com/index/separating-signal-from-noise-coding-evaluations/"
  - title: "SimpleQA Verified · arXiv 2509.07968"
    url: "https://arxiv.org/abs/2509.07968"
  - title: "BetterBench · arXiv 2411.12990"
    url: "https://arxiv.org/abs/2411.12990"
datasets:
  - title: "Chatbot Arena (LMArena) pairwise votes, style-control analysis"
    url: "https://lmsys.org/blog/2024-08-28-style-control/"
  - title: "SWE-bench Verified (no longer reported by OpenAI, Feb 2026)"
    url: "https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/"
  - title: "SWE-bench Pro (recommendation retracted, Jul 2026)"
    url: "https://openai.com/index/separating-signal-from-noise-coding-evaluations/"
  - title: "SimpleQA Verified (1,000 prompts)"
    url: "https://arxiv.org/abs/2509.07968"
---

Choosing an eval takes three checks: does the test measure the error that is expensive for you, what statistical model built its ranking, and where is the test in its life? LMArena's style control showed that adding style covariates to a Bradley-Terry model moved GPT-4o-mini from rank 6 to 11 in an August 2024 analysis. OpenAI's 2026 audits showed that even a reference coding benchmark and its successor can be broken.

> **Key Takeaways**
> - LMArena estimates each model's strength from pairwise votes with a Bradley-Terry model. Style control adds the style differences between the two answers as covariates in the same regression.
> - In the LMSYS analysis, length was the dominant style factor and markdown second-order. The authors call the analysis "observational".
> - Contamination (the test leaked) and saturation (the test no longer separates good models) are different problems; neither implies the other.
> - OpenAI audited 138 SWE-bench Verified problems and found at least 59.4% with flawed tests. For SWE-bench Pro it estimated about 30% of tasks broken.
> - Selection starts from "decision, costly failure, required evidence, family", not from a benchmark's name.

This is the technical layer behind the [HMD-004 companion post](/en/blog/hmd-004-top-model-for-you/). The full story is in the [episode](/en/episodes/hmd-004/), and the Persian version of this deep dive is [here](/fa/blog/hmd-004-choosing-an-eval/).

## How does style control work statistically?

Style control is Arena's usual ranking model with a few extra columns. Each LMArena vote is a pairwise comparison: a user sees anonymous answers from models i and j and picks one. A Bradley-Terry model gives every model a latent strength β and builds the win probability from the difference:

```text
P(i beats j) = σ(β_i − β_j),   σ(x) = 1 / (1 + e^(−x))
```

In practice this is a logistic regression. Each vote is a row; model i's column gets +1, model j's gets −1, and the outcome is 1 if i won. The fitted coefficients are the βs, and sorting them gives the ranking.

Style control adds a vector Z of style differences between the two answers to the same regression:

```text
P(i beats j) = σ(β_i − β_j + γ · Z)
```

The [LMSYS post](https://lmsys.org/blog/2024-08-28-style-control/) defines the style features as answer length in tokens and counts of three markdown elements (headers, list items and bold text). Each feature enters as a normalised difference between the two answers: (A − B) ÷ (A + B), so 500 against 520 tokens counts as close while 20 against 40 does not. The coefficients γ show how much each style feature moves votes. The new βs estimate each model's strength holding style fixed, and the style-controlled ranking comes from sorting them.

### What did that analysis find?

- "Length was the dominant style factor"; markdown was a second-order effect.
- In the overall category, GPT-4o-mini moved from rank 6 to 11 with markdown controlled, or with both controlled.
- Claude 3 Opus moved from rank 16 to 10 with both controlled.

### What the adjusted ranking does not tell you

The authors say plainly that the analysis is "still observational". That has three consequences. If a longer answer really is more complete, controlling for length removes some genuine quality too. The feature list is a choice; unmeasured stylistic features remain inside β. And the controlled rank answers a counterfactual ("if style were equal, which model would people prefer?"), not a question about correctness. Both versions of the ranking still measure human preference.

## What does a map of benchmark families look like?

Homodyne's selection tool sorts benchmarks into 16 families in 4 groups. It is our working map, not an official taxonomy, and many benchmarks sit between two families. The column worth learning is the blind spot:

| Group | Families | One example blind spot |
|---|---|---|
| Capability | knowledge, reasoning, mathematics, coding, multimodal, multilingual_cultural | Coding: an incomplete test suite cannot see a real defect |
| System | retrieval_rag, agents_tool_use, robustness | Agents: the environment and scaffold are part of the result |
| Trust | factuality, calibration_abstention, safety_security, bias_fairness | Abstention: a system that refuses everything has zero errors; read it next to accuracy |
| Value | human_preference, efficiency, product_business | Preference: preference is not truth |

Two axes help as well. The first is the environment: controlled and static, or live and interactive. The second is where the right answer comes from: a reference answer known in advance, or human, judge or outcome-based judgement. On this map, agents_tool_use, human_preference and product_business sit in the live, judged corner; the rest sit in the static, reference-answer corner. Neither corner is better. The static corner is cheap and repeatable but can drift from real use; the live corner is closer to real use but costs more, varies more and depends on who judges.

## How do contamination and saturation differ?

Contamination means the test's questions or answers were in a model's training data, so a high score may reflect memory rather than ability. Saturation means good models have reached the ceiling and the test can no longer tell them apart. A test can be saturated and clean, or contaminated and still hard.

Homodyne's lifecycle map has six states. They are dated claims about a benchmark, not properties of it, and they need not occur in sequence:

| State | Meaning |
|---|---|
| Fresh | Released; frontier models are far from the ceiling |
| Discriminating | Supports decision-relevant distinctions under an appropriate paired analysis |
| Saturating | Top scores are rising fast toward the ceiling |
| Saturated | Weak discrimination near the ceiling; one non-significant comparison does not prove saturation |
| Compromised | Contamination or flawed items are documented |
| Retired | Its maintainer or a major reporter has stopped using it |

A few entries from the dated inventory (as of 29 September 2026; re-check before citing): MMLU saturated, with MMLU-Pro as successor; SWE-bench Verified retired; SimpleQA compromised for noisy labels, topical bias and redundancy; SimpleQA Verified discriminating. SimpleQA Verified is public, so contamination is a risk to manage, not a reason to discard it.

## What did the SWE-bench Verified and Pro audits find?

On 23 February 2026, in [Why we no longer evaluate SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/), OpenAI said it would stop reporting the benchmark. It audited 138 problems its model consistently failed, with at least six engineers reviewing each problem. At least 59.4% of those problems had flawed tests that rejected correct solutions. OpenAI also reported signs of contamination and pointed to SWE-bench Pro as the successor.

### Why 59.4% is not the whole benchmark's failure rate

Because the sample was selected on failure. If a problem's tests reject correct solutions, even a model that solved it is recorded as failing, so flawed problems are over-represented among "problems the model keeps failing". The figure describes that subset and should not be generalised to the full set. Its real message lies elsewhere: on the hard problems where leaderboards compete, a large share of "failures" may be failures of the test rather than the model.

### The successor needs an audit too

On 8 July 2026, in [Separating signal from noise in coding evaluations](https://openai.com/index/separating-signal-from-noise-coding-evaluations/), OpenAI wrote "we retract our earlier recommendation" to adopt SWE-bench Pro. It estimated that about 30% of Pro's tasks were broken, from two separate estimates: 27.4% from an automated pipeline and 34.1% from human annotators. The gap between them is a reminder that "broken" is itself a measurement with error. Homodyne's tool endorses no automatic successor to Verified.

## A checklist for picking an eval

1. **Write the decision.** Which real choice will this evidence inform?
2. **Write the costly failure.** Which mistake can you not afford? If you cannot write it, you are not ready.
3. **Define the required evidence.** What observation would catch that mistake?
4. **Let the family fall out of the chain**, and write its blind spot beside it.
5. **Write the exclusions.** Which famous leaderboards do not answer this decision, and why?
6. **Open the benchmark with five questions:** claim, task, metric, blind spot, life.
7. **Read the scoring rule.** What does a wrong answer cost, and how is "I don't know" counted? ([HMD-002](/en/blog/hmd-002-same-answers-new-winner/) showed this alone can flip the winner.)
8. **Read the ranking method.** If it is vote-based, look at the style-controlled view too.
9. **Check the lifecycle state, with its date.** Look for audits, corrections or retirement, for the successor as well.
10. **Check contamination.** Is the test public? Does it have a holdout or fresh items?
11. **Check language and population.** If your users write Persian, is there a Persian slice, ideally with natively sourced items?
12. **Ask for uncertainty.** Is the gap between two models reported with a paired confidence interval?

## How do you reproduce the selection tool's results?

`m2bench families` runs without network access and makes no model calls. It belongs to the M2Lab benchmarking framework, which lives in its own repository, not in the Homodyne repository. From the root of that framework:

```bash
python3 -m m2bench families \
  --decision "customer support bot for my online shop" \
  --failure  "tells customers the wrong refund policy"
```

Closest example: agents_tool_use, safety_security and robustness, excluding knowledge and reasoning. For a bot that only answers, that advice is wrong.

```bash
python3 -m m2bench families \
  --decision "question answering assistant for my online shop" \
  --failure  "a confident wrong answer about refunds"
```

This time: calibration_abstention, factuality and multilingual_cultural, with knowledge as diagnostic only, excluding human_preference, reasoning and agents_tool_use. These outputs were run and recorded on 2 November 2026.

The difference comes from `select()` in `m2bench/families.py`: it compares the words longer than four letters in your sentences with those in a set of worked examples and returns the closest one. Words such as "customer" and "wrong" in the first wording pulled it toward an example about automated customer work. The tool is deliberately simple so that it shows the chain and the exclusions rather than making the decision.

Two more commands print the map and the lifecycle:

```bash
python3 -m m2bench families --map
python3 -m m2bench families --lifecycle
```

The second prints the six states dated "as of 2026-09-29". Both read `framework/00-landscape/benchmark-families.yaml`.

## What this does not show

- **Style control does not produce a correctness ranking.** Both rankings, with and without control, measure human preference. The Arena numbers come from the August 2024 analysis, not today's ranks.
- **We do not say vote-based leaderboards are useless**, or which model is best today.
- **The family map and lifecycle states are Homodyne's working map**, not an official taxonomy or a fixed timeline. States are dated, and not all were re-audited at the same time.
- **59.4% is not SWE-bench Verified's overall failure rate.** It describes 138 problems the model kept failing.
- **The roughly 30% for Pro is OpenAI's own estimate**, not an independent audit.
- **The selection tool only matches words.**

## Further reading

- [LMSYS: Does style matter?](https://lmsys.org/blog/2024-08-28-style-control/) for the model and the style features.
- [OpenAI, February 2026](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) and [OpenAI, July 2026](https://openai.com/index/separating-signal-from-noise-coding-evaluations/) for the two audits.
- [SimpleQA Verified](https://arxiv.org/abs/2509.07968): a benchmark rebuilt after its flaws were found.
- [BetterBench](https://arxiv.org/abs/2411.12990): assessing benchmark quality across the whole lifecycle.
- On Homodyne: the [HMD-002 deep dive](/en/blog/hmd-002-negative-marking-threshold/) on how a scoring rule changes the winner, and [HMD-005](/en/episodes/hmd-005/) on how models read Persian.
