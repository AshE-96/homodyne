---
title: "How can the same answers crown a different AI winner?"
description: "Better always means better under a scoring rule. Re-scoring OpenAI's SimpleQA table with a wrong-answer penalty flips the winner. Here is how and why."
lang: en
translationKey: hmd-002-companion
hmd: HMD-002
kind: companion
date: 2026-11-27
tags: ["benchmarks", "negative marking", "SimpleQA", "hallucination", "LLM evaluation"]
sources:
  - title: "OpenAI · Why Language Models Hallucinate (5 Sep 2025)"
    url: "https://openai.com/index/why-language-models-hallucinate/"
  - title: "Kalai, Nachum, Vempala, Zhang · Why Language Models Hallucinate · arXiv 2509.04664"
    url: "https://arxiv.org/abs/2509.04664"
  - title: "Adding Error Bars to Evals · arXiv 2411.00640"
    url: "https://arxiv.org/abs/2411.00640"
---

Because "better" always means better under some scoring rule. Keep two models' answers exactly as they are, change only the price of a wrong answer, and the winner can flip. In the SimpleQA table OpenAI published on 5 September 2025, the model that leads on accuracy drops below zero under a familiar exam penalty, and its rival takes first place.

> **Key Takeaways**
> - Accuracy counts only right answers. To accuracy, a wrong answer and "I don't know" are worth the same.
> - Under the rule "right +1, I don't know 0, wrong −k", the penalty k decides which model is better.
> - On OpenAI's SimpleQA table, a wrong answer costing just 1/24.5 of a right one is enough to flip the winner.
> - This is re-scoring, not a new experiment: the models did not know about the penalty and might have answered differently.

This post accompanies the [HMD-002 episode](/en/episodes/hmd-002/). For the algebra and exact reproduction steps, read the [deep dive on negative marking](/en/blog/hmd-002-negative-marking-threshold/).

## What does OpenAI's SimpleQA table actually show?

In ["Why Language Models Hallucinate"](https://openai.com/index/why-language-models-hallucinate/) (5 September 2025), OpenAI set two of its own models side by side on SimpleQA, a test of short questions that each have one clear correct answer. The numbers are percentages of all questions:

| Model | Abstained ("I don't know") | Correct | Wrong |
|---|---:|---:|---:|
| gpt-5-thinking-mini | 52 | 22 | 26 |
| OpenAI o4-mini | 1 | 24 | 75 |

On accuracy, o4-mini leads with 24%. Yet it answered 75% of questions wrongly: of the answers it gave, roughly three in four were wrong. The other model left more than half the questions unanswered and got 26% wrong.

One caution up front: this table is from September 2025 and covers one test. It is not a ranking of today's models.

## How does the price of a wrong answer enter the score?

A scoring rule fits on one line: each right answer earns 1 point, each "I don't know" earns 0, and each wrong answer costs k. The number k is the price of a wrong answer, measured in right answers. With k = 0 you get plain accuracy, where being wrong is free.

A teaching example makes the effect visible. The numbers below are **ILLUSTRATIVE** and belong to no real model. Two hypothetical shop assistants answer the same 100 customer questions. Assistant A gets 60 right, 30 wrong and says "I don't know" 10 times. Assistant B gets 50 right, 5 wrong and abstains 45 times.

| k (price per wrong answer) | Score A | Score B | Winner |
|---:|---:|---:|---|
| 0 | 60 | 50 | A |
| 1 | 30 | 45 | B |
| 3 | −30 | 35 | B |
| 9 | −210 | 5 | B |

The winner changes where the two scores meet: (60 − 50) ÷ (30 − 5) = 0.4. If a wrong answer costs you more than 40% of what a right answer is worth, B is the better hire.

Negative scores mean something too. An assistant that never answers scores zero, so a negative score says that, under this rule, the assistant did more harm by answering than total silence would have. You can produce this table yourself from the root of the Homodyne repository:

```bash
python3 tools/bluff_lab.py demo
```

## Who wins under Konkur's negative marking?

Under Konkur rules, the guess-happy model scores −1.0 and the cautious one scores 13.3. Konkur is Iran's national university entrance exam; on its four-option questions a right answer earns +3 and a wrong answer −1, so three wrong answers cancel one right one and k = 1/3. Applied to OpenAI's table:

- OpenAI o4-mini: 24 − (75 ÷ 3) = −1.0
- gpt-5-thinking-mini: 22 − (26 ÷ 3) = 13.3

Same answers, different rule, different winner. The episode's `two_scores.py` does this re-scoring:

```bash
python3 parts/02-benchmarking/e01-is-a-higher-score-better/artifact/two_scores.py
```

Its last lines hold a stranger number: the crossover sits at k = 0.0408. In plain terms, if a wrong answer costs only 1/24.5 of a right one, the winner flips. The order of these two models depends more on the scoring rule than on their two-point accuracy gap.

## Why do common leaderboards reward guessing?

When a wrong answer costs nothing, guessing always beats "I don't know". The authors of the [full paper](https://arxiv.org/abs/2509.04664) (Kalai et al., 2025) give a simple example. Ask a model for the birthday of someone it does not know. "I don't know" scores zero for certain; a random date has about a 1 in 365 chance of being right.

The same incentive runs through popular model comparisons. In Table 2 the paper reviews ten widely used evaluations (GPQA, MMLU-Pro, IFEval, Omni-MATH, WildBench, BBH, MATH L5, MuSR, SWE-bench and HLE). Nine give no credit at all for "I don't know"; only WildBench gives partial credit. In the authors' words, most popular evaluations use "binary grading".

The authors present this as one explanation for why hallucinations persist, not as the only cause.

## Why is Konkur's penalty exactly one third?

One third is the penalty at which a completely blind guess on a four-option question breaks even on average: ¼ × 1 − ¾ × ⅓ = 0.

Kalai et al. generalise the idea. If you tell a model "answer only if you are at least t confident", the matching penalty is k = t/(1−t). For t = 0.25, k = 1/3, which is the Konkur rule. For 0.5 you get 1, for 0.75 you get 3, and for 0.9 you get 9.

The paper proposes stating that threshold explicitly in the instructions. Stating it is not enough on its own: the model also has to estimate its own confidence honestly. That match between stated confidence and actual correctness is called calibration.

## What this does not show

- **It does not show changed behaviour.** We only swapped the accountant. The models did not know a penalty existed when they answered, and a candidate who knows about negative marking answers differently. Measuring that change is the job of Homodyne's Bluff experiment, which **has not run yet**.
- **It does not say which model is better today.** The table is from September 2025 and covers one test.
- **It does not say accuracy is worthless**, or that one k is right for every task. The cost of an error in your task sets your k.
- **It does not measure uncertainty.** A gap between two models should be read with its error bars ([Adding Error Bars to Evals](https://arxiv.org/abs/2411.00640)). This re-scoring used only the published percentages, so we did not compute confidence intervals.

## What should you ask before trusting a score?

Next to any big number on a leaderboard, ask six questions. They are on a one-page card in the episode package:

1. **Decision:** which real choice will this evidence inform?
2. **Task:** what does the benchmark actually ask the model to do?
3. **Data:** which items, from which sources, in which languages?
4. **Run:** which versions, prompts, tools and budgets, and how many repeats?
5. **Score:** what are the numerator and denominator, what does a wrong answer cost, and how is "I don't know" counted?
6. **Boundary:** which population and use does the claim cover, and with what uncertainty?

This post only played with question five, and that was enough to flip the winner.

A one-line exercise: for your own work, write down how many right answers one confident wrong answer from an AI would wipe out. That number is your k. The next episode in the benchmark course, [HMD-004](/en/episodes/hmd-004/), asks whether the top model on a leaderboard is the best one for your task. The Persian version of this post is [here](/fa/blog/hmd-002-same-answers-new-winner/).
