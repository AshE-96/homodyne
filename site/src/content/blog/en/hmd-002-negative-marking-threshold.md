---
title: "Negative marking in AI evals: the k/(k+1) threshold"
description: "Score right +1, I don't know 0, wrong −k, and a model should answer only above k/(k+1) confidence. The algebra, and how to reproduce the SimpleQA flip."
lang: en
translationKey: hmd-002-deep-dive
hmd: HMD-002
kind: deep-dive
date: 2026-11-27
tags: ["benchmarks", "negative marking", "SimpleQA", "calibration", "rescoring", "hallucination"]
sources:
  - title: "Kalai, Nachum, Vempala, Zhang · Why Language Models Hallucinate · arXiv 2509.04664"
    url: "https://arxiv.org/abs/2509.04664"
  - title: "OpenAI · Why Language Models Hallucinate (5 Sep 2025)"
    url: "https://openai.com/index/why-language-models-hallucinate/"
  - title: "SimpleQA Verified · arXiv 2509.07968"
    url: "https://arxiv.org/abs/2509.07968"
  - title: "Adding Error Bars to Evals · arXiv 2411.00640"
    url: "https://arxiv.org/abs/2411.00640"
datasets:
  - title: "SimpleQA results table in OpenAI's post (5 Sep 2025, from the GPT-5 System Card)"
    url: "https://openai.com/index/why-language-models-hallucinate/"
  - title: "SimpleQA Verified (1,000 prompts)"
    url: "https://arxiv.org/abs/2509.07968"
---

Under the rule "right +1, I don't know 0, wrong −k", a model that maximises its expected score should answer only when its probability of being right exceeds t = k/(k+1). Rescoring applies such a rule to answers that are already fixed. On the SimpleQA table OpenAI published, the winner flips at k = 0.0408, a rule whose implied confidence target is just 3.9%.

> **Key Takeaways**
> - The indifference threshold t = k/(k+1) comes from comparing the expected score of answering with the certain zero of abstaining. Inverted, k = t/(1−t).
> - A model's score per 100 questions is correct − k × wrong, a straight line in k. Two models cross at k* = (correct_A − correct_B) / (wrong_A − wrong_B).
> - For o4-mini and gpt-5-thinking-mini on SimpleQA, k* = 0.0408 (t* = 3.9%).
> - Kalai et al. print "t = 0.75 (penalty 2)" in one example, but their own formula gives 3.
> - Rescoring does not measure behaviour: the models were never told about the penalty.

This is the technical layer behind the [HMD-002 companion post](/en/blog/hmd-002-same-answers-new-winner/). The story is told in the [episode](/en/episodes/hmd-002/), and the Persian version of this deep dive is [here](/fa/blog/hmd-002-negative-marking-threshold/).

## Where does the indifference threshold come from?

It comes from comparing the expected score of answering with the guaranteed score of silence. Suppose a model would be right on a given question with probability p. If it answers, its expected score is:

```text
E[answer]  = p × 1 + (1 − p) × (−k) = p − k(1 − p)
E[abstain] = 0
```

Answering pays when p − k + kp > 0, that is, when p(1 + k) > k:

```text
answer  ⇔  p > k / (k + 1) = t
k = t / (1 − t)
```

We call t the indifference threshold because at p = t answering and abstaining are worth exactly the same. In section 4.2 of [Why Language Models Hallucinate](https://arxiv.org/abs/2509.04664), Kalai et al. propose this as an "explicit confidence target": state the threshold in the instructions and apply the matching penalty.

| t (confidence target) | k = t/(1−t) | Meaning |
|---:|---:|---|
| 0 | 0 | Plain accuracy; every guess pays |
| 0.25 | 1/3 | The Konkur rule |
| 0.5 | 1 | A wrong answer costs as much as a right one earns |
| 0.75 | 3 | |
| 0.9 | 9 | |

### Where does the Konkur rule sit in this algebra?

Konkur, Iran's national university entrance exam, gives +3 for a right answer and −1 for a wrong one. Divide by 3 and you have "right +1, wrong −1/3", so k = 1/3 and t = (1/3) ÷ (4/3) = 0.25. On a four-option question, a fully blind guess is also right with probability 0.25. That is why a blind guess has an expected score of zero: ¼ × 1 − ¾ × ⅓ = 0. The rule is tuned so blind guessing neither helps nor hurts, and any knowledge that lifts the probability above 0.25 makes answering worthwhile.

### An erratum in the paper

In the version we read (HTML, checked 2 November 2026), the paper prints "t = 0.75 (penalty 2)" in one example. Its own formula, k = t/(1−t), gives 0.75 ÷ 0.25 = 3. A direct check agrees: with k = 3 and p = 0.75, the expected score is 0.75 − 3 × 0.25 = 0, which is indifference; with k = 2 it is 0.25, which is not. The "2" looks like a typo. This post and `two_scores.py` follow the formula.

## What exactly does rescoring do?

Rescoring recomputes recorded answers under a different rule without asking the model anything again. Because "+1, 0, −k" is linear, you do not need per-question answers; three aggregate shares (right, wrong, abstained) are enough. Per 100 questions:

```text
S(k) = correct − k × wrong
```

The abstention share does not appear in the formula because "I don't know" is worth zero. It is still there implicitly, since correct + wrong + abstained = 100.

For each model, S(k) is a straight line whose slope is minus its wrong-answer share. Two such lines cross at most once:

```text
k* = (correct_A − correct_B) / (wrong_A − wrong_B)
t* = k* / (1 + k*)
```

A crossover only exists when k* is positive, meaning the model with more right answers also has more wrong ones. If one model has both more right answers and fewer wrong ones, no non-negative penalty can make it lose, and the script says so.

Keep the two thresholds apart. t is a single model's decision line on a single question. t* is the point at which two models swap places in a table. The first is about behaviour; the second is about rank.

### What can rescoring not compute?

Non-linear metrics, such as calibration error, need the model's stated confidence on every question; three aggregate percentages cannot give you that. More importantly, rescoring assumes the answers stay fixed. A model told that wrong answers are penalised might guess less, or might hold back even when it knows. Measuring that takes a new experiment.

## What is the SimpleQA data, and what are its limits?

The table comes from OpenAI's post [Why Language Models Hallucinate](https://openai.com/index/why-language-models-hallucinate/) (5 September 2025), and originates in the GPT-5 System Card. Values are percentages of all questions:

| Model | Abstained | Correct | Wrong | Total |
|---|---:|---:|---:|---:|
| gpt-5-thinking-mini | 52 | 22 | 26 | 100 |
| OpenAI o4-mini | 1 | 24 | 75 | 100 |

Homodyne's five-question benchmark card reads SimpleQA like this:

- **Claim:** short-form factual knowledge.
- **Task:** short questions with one verifiable answer, no search.
- **Metric:** correct, incorrect or not attempted, as a percentage of questions.
- **Blind spot:** says almost nothing about long answers, summaries or grounded (RAG) answering.
- **Life:** after label noise was found, a revised set, [SimpleQA Verified](https://arxiv.org/abs/2509.07968), was built with 1,000 prompts. Homodyne's lifecycle map (dated 29 September 2026) marks the original SimpleQA as "compromised" for noisy labels, topical bias and redundancy.

Two gaps, stated plainly. The size and licence of the original SimpleQA set are not recorded in the sources checked for this episode, so we give no figures for them. And because the number of questions behind these percentages is not in our source, we computed no confidence intervals. [Adding Error Bars to Evals](https://arxiv.org/abs/2411.00640) is the reminder that a gap between models should be judged with its uncertainty, and the episode's six-question card adds that overlapping separate intervals are not a decision rule for paired differences.

## How do you reproduce the crossover yourself?

`two_scores.py` is read-only, needs no network and no model, and runs in a fraction of a second. From the repository root:

```bash
python3 parts/02-benchmarking/e01-is-a-higher-score-better/artifact/two_scores.py
```

For five confidence targets (0, 0.25, 0.5, 0.75, 0.9) it builds k = t/(1−t) and prints each model's points per 100 questions:

| t | k | OpenAI o4-mini | gpt-5-thinking-mini | Winner |
|---:|---:|---:|---:|---|
| 0.00 | 0.000 | 24.0 | 22.0 | OpenAI o4-mini |
| 0.25 | 0.333 | -1.0 | 13.3 | gpt-5-thinking-mini |
| 0.50 | 1.000 | -51.0 | -4.0 | gpt-5-thinking-mini |
| 0.75 | 3.000 | -201.0 | -56.0 | gpt-5-thinking-mini |
| 0.90 | 9.000 | -651.0 | -212.0 | gpt-5-thinking-mini |

and ends with:

```text
Crossover: k = 0.0408 points per wrong answer (confidence target t = 3.9%).
A wrong answer costing 1/24.5 of a right one is enough to flip the winner.
```

By hand: k* = (24 − 22) ÷ (75 − 26) = 2 ÷ 49 = 0.0408, and t* = 2 ÷ 51, or 3.9%. Put simply, even a rule that asks for only 3.9% confidence reverses the order of these two models. At k = 1 both models are below zero (−51.0 and −4.0): under that rule, both do worse than a model that answers "I don't know" to everything.

### Plug in your own numbers

Swap either model with `--a` and `--b`. The order is name, % correct, % wrong, % abstained. For example, the episode's two teaching assistants (**ILLUSTRATIVE**, not real models):

```bash
python3 parts/02-benchmarking/e01-is-a-higher-score-better/artifact/two_scores.py \
  --a "assistant A" 60 30 10 --b "assistant B" 50 5 45
```

Their crossover is k = 0.4: (60 − 50) ÷ (30 − 5). The script warns if a model's three shares miss 100 by more than 1.5 points, a margin for rounding in published percentages. Its final line always repeats that this is re-scoring, not re-running.

## Why do accuracy-only leaderboards reward guessing?

An accuracy-only table sets k = 0, and therefore t = 0. With a zero threshold, any question with a non-zero chance of being right is worth answering, and "I don't know" is never the best move. A model trained or tuned to do well on such tables learns never to abstain.

Kalai et al. illustrate this with the birthday example: for a stranger, "I don't know" scores zero for certain, while a random date has about a 1 in 365 chance. In Table 2 they then review ten widely used evaluations: GPQA, MMLU-Pro, IFEval, Omni-MATH, WildBench, BBH, MATH L5, MuSR, SWE-bench and HLE. Only WildBench gives partial credit for "I don't know"; the other nine give none. Their summary is that most popular evaluations use "binary grading".

The paper's remedy is not another hallucination benchmark but a change to how mainstream evaluations score, with the threshold stated in the prompt. Two caveats belong beside it. The authors offer this as one explanation for persistent hallucination, not the only cause. And a stated threshold only works if the model estimates its own confidence well (calibration) and actually acts on it. Rescoring tests neither.

## What this does not show

- **No change in behaviour.** Rescoring recomputes fixed answers. The models did not know about any penalty. Homodyne's Bluff experiment, designed to measure what happens when the penalty is stated to the model, **has not run yet**, and nothing in this post comes from it.
- **No current ranking.** The table is from September 2025 and covers one test.
- **No universal k.** k is the cost of an error in a specific task; insurance support and brainstorming do not share one.
- **No uncertainty estimate.** Without the item count, we cannot say how stable a two-point accuracy gap is.
- **No calibration measurement.** The published table does not include per-answer confidence.

## Further reading

- [Kalai et al., arXiv 2509.04664](https://arxiv.org/abs/2509.04664): section 4.2 for explicit confidence targets, Table 2 for the evaluation survey.
- [SimpleQA Verified](https://arxiv.org/abs/2509.07968): the revised set of 1,000 prompts.
- [Adding Error Bars to Evals](https://arxiv.org/abs/2411.00640): how to report a gap between models with its uncertainty.
- On Homodyne: [HMD-004](/en/episodes/hmd-004/) on which benchmark answers your question, and [HMD-010](/en/episodes/hmd-010/) on whether negative marking actually makes a model more careful.
