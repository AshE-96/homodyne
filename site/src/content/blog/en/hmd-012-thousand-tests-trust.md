---
title: "We tested an AI model 1,000 times. Can we trust it?"
description: "Not always. Trusting \"model A beats B\" depends on independent questions, a question-by-question comparison and the smallest gap the test could detect."
lang: en
translationKey: hmd-012-companion
hmd: HMD-012
kind: companion
date: 2027-02-12
tags: ["benchmarks", "sample size", "statistical power", "paired comparison", "preregistration", "LLM evaluation"]
sources:
  - title: "Miller (2024). Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations. arXiv 2411.00640"
    url: "https://arxiv.org/abs/2411.00640"
  - title: "Anthropic (19 November 2024). A statistical approach to model evaluations"
    url: "https://www.anthropic.com/research/statistical-approach-to-model-evals"
  - title: "Card, Henderson, Khandelwal, Jia, Mahowald, Jurafsky (2020). With Little Power Comes Great Responsibility. EMNLP 2020, arXiv 2010.06595"
    url: "https://arxiv.org/abs/2010.06595"
  - title: "McNemar (1947). Note on the sampling error of the difference between correlated proportions or percentages. Psychometrika 12(2):153–157"
    url: "https://doi.org/10.1007/BF02295996"
  - title: "Nosek, Ebersole, DeHaven, Mellor (2018). The preregistration revolution. PNAS 115(11):2600–2606"
    url: "https://doi.org/10.1073/pnas.1708274114"
---

Not on its own. A thousand rows of results are a thousand pieces of evidence only if they come from a thousand independent questions. Whether you can trust "model A beats model B" depends on three things: how many independent questions you have, whether the two models were compared question by question or only by their totals, and whether anyone worked out, before the run, the smallest gap the test could detect.

> **Key Takeaways**
> - Repeating a question does not replace a new one. In Miller's example with 198 questions, asking each question 10 times instead of once lowers the minimum detectable effect from 13.2% to 7.5%; by our calculation, even infinite repeats cannot push it below 6.6%.
> - A paired comparison on the same data detects smaller gaps: in our simulation (ILLUSTRATIVE), 4.0 points instead of 8.0.
> - Card et al. calculated that with 500 questions, a real 2-point improvement is detected only about 25% of the time.
> - If the 1,000 rows are really 50 questions repeated 20 times, and there is no real difference, a naive count declared a "winner" 52.8% of the time in our simulation.
> - No model was called for this episode, and the channel's Bluff benchmark has not been run.

This post accompanies [Homodyne episode HMD-012](/en/episodes/hmd-012/). Formulas, reproduction commands and limitations are in the [deep dive for the same episode](/en/blog/hmd-012-power-paired-clusters/).

## Why are 1,000 rows not always 1,000 pieces of evidence?

Because rows can be echoes of each other. Suppose you want to know which bakery your neighbourhood prefers. Ask one person twenty times and you have twenty answers, but still one person's opinion. Ask twenty people and you have learned something about the neighbourhood.

Language models work the same way. Repeating a question tells you how much the model's answer to that question varies. That is useful, but it says nothing about the questions you never asked. Evan Miller of Anthropic gives a worked example in *Adding Error Bars to Evals* (November 2024): with 198 questions, asking each one 10 times instead of once moves the minimum detectable effect from 13.2% to 7.5% ([arXiv 2411.00640](https://arxiv.org/abs/2411.00640), section 5). We ran the same formula with infinite repeats and got 6.6%. The number of questions sets the floor, not the number of repeats.

The paper's central line is short: "Fundamentally, evaluations are experiments." A benchmark's questions are a sample of all the questions that could have been asked, so the score, like any poll result, has a margin of error.

## What does a paired comparison change?

When two models answer the same questions, the questions both get right, or both get wrong, say nothing about which model is better. The information sits only in the questions where they disagree. The classic test that counts only those discordant pairs is McNemar's test ([McNemar, 1947](https://doi.org/10.1007/BF02295996)).

The effect is large. In our simulation (**ILLUSTRATIVE**), two models answer the same 500 questions; A is 72% accurate, B is 70%, and they disagree on 10% of questions. Compare only the two totals and the smallest detectable gap is 8.0 points. Compare question by question and it is 4.0 points: the same data, half the threshold. Miller calls pairing a "free" reduction in variance, provided the two models' scores are correlated across questions.

## What does a small test miss?

Most real differences. Card et al. (EMNLP 2020) worked through this scenario: a 500-question benchmark, a new model that is truly 2 points better, and two models that agree on 90% of questions. The chance that McNemar's test detects the real improvement is "approximately 0.25" ([arXiv 2010.06595](https://arxiv.org/abs/2010.06595), appendix C). Three times out of four, a real improvement goes unseen.

The same appendix has a worse point. In the runs where the difference does come out "significant", it is exaggerated by a factor of 1.9 on average. With 2,000 questions, power reaches "nearly 80%" and the exaggeration shrinks to 1.1.

We simulated the same scenario 2,000 times with our own code (**ILLUSTRATIVE**, seed 12): 24% power and 1.9× exaggeration at 500 questions; 78% power and 1.1× at 2,000.

## How many questions are enough?

It depends on the gap you want to see. Two terms help. **Power** is the probability of detecting a real difference; 80% is the usual target. The **minimum detectable effect** (MDE) is the smallest difference your number of questions can detect with that same 80% power.

Miller calculates that, under his example's assumptions, detecting a 3-point difference needs about 969 independent questions, and suggests new evals should contain at least 1,000. But that 1,000 answers one specific question. The table below comes from `power_lab.py` (**ILLUSTRATIVE**, paired comparison, models that disagree on 10% of questions):

| Independent questions | MDE (accuracy points) |
|---|---|
| 100 | 8.9 |
| 250 | 5.6 |
| 500 | 4.0 |
| 1,000 | 2.8 |
| 2,000 | 2.0 |
| 4,000 | 1.4 |

A thousand questions can see a gap of about 3 points; seeing 1.4 points takes four thousand. "How many questions?" has no answer without "to detect what gap?"

## What do grouped questions do to the arithmetic?

Many benchmarks build questions in groups: one passage with several questions about it, or one question translated into several languages. These are not separate witnesses. If a model misreads the passage, it will probably miss all its questions together. Miller shows this on real data: on the DROP reading benchmark, with Anthropic models, the clustered standard error is 1.34 against a naive 0.44, a ratio of 3.05 (table 4 of the paper).

To see the consequence, `power_lab.py` built the same 1,000 rows in three shapes and deliberately put no real difference between the two models (**ILLUSTRATIVE**; the intra-cluster correlation of 0.5 is assumed):

| Shape of 1,000 rows | "Winner" by naive count | "Winner" by clustered test | Power for a real 3-point gap |
|---|---|---|---|
| 1,000 questions × 1 | 4.7% | 4.7% | 86.2% |
| 250 questions × 4 | 23.1% | 5.5% | 50.6% |
| 50 questions × 20 | 52.8% | 5.3% | 17.5% |

The clustered test removes the fake winners and brings the error rate back to about 5%. It cannot create questions that were never asked: with 50 questions repeated 20 times, a real 3-point gap is detected only 17.5% of the time.

## What does a fair run mean?

That every difference in how the models were run is written down and declared in advance. If model A gets a careful prompt and three retries while model B gets a plain prompt and one attempt, you cannot tell whether a gap comes from the model or from the run. The episode's run card (`artifact/fair-run-card.md`) records, for each model: the exact version and run date, the prompt, sampling settings, allowed tools, answer budget, retry rule and what happens on service errors. "Fair" does not always mean identical settings. It means a clear policy, declared beforehand, for everyone.

## Why lock the plan before seeing results?

Because many comparisons manufacture chance winners. Six models give 15 pairs. If there is no real difference anywhere and each pair is tested separately at the 5% level, then, treating the tests as independent, the chance that at least one comes out "significant" is 53.7%. The pairs share models, so they are not truly independent; the figure only shows the order of magnitude.

The fix is preregistration: before seeing results, write down and date the primary comparison, the difference that would matter in practice, the number of questions and independent groups, the test, and what you will do with failed runs. Nosek et al. explain in PNAS (2018) how preregistration separates prediction made before the data from explanation made after it ([doi 10.1073/pnas.1708274114](https://doi.org/10.1073/pnas.1708274114)). It does not forbid changing the plan; it requires each change to be logged with a date and a reason.

## Three questions before you believe "X% better"

Next time you read a headline like "our new model is 3% better", ask:

1. **How many independent questions?** Not rows: count translations, repeats and questions about the same passage as one.
2. **Was it paired?** Both models on the same questions, compared question by question?
3. **What was the smallest detectable gap?** If the test's MDE is 4 points, read a 3-point gap with caution.

The same habit helped in [episode HMD-002](/en/episodes/hmd-002/), where the scoring rule flipped the winner. Here, sample size decides whether any winner can be declared at all.

## What this does not show

- It does not show that any particular real model or benchmark is underpowered. No model was called for this episode.
- The simulated numbers are ILLUSTRATIVE: the 10% disagreement rate and the 0.5 intra-cluster correlation are teaching assumptions, not measurements. Only a small pilot run can estimate the real values.
- The 3.05 ratio belongs to DROP and the models in Miller's paper; it does not carry over to other benchmarks.
- The channel's Bluff benchmark has not been run; this post contains no results from it.
- "Significant" means a difference is probably real, not that it matters for your use.

*Persian original: [هزار بار آزمودن یک مدل هوش مصنوعی برای اعتماد کافی است؟](/fa/blog/hmd-012-thousand-tests-trust/)*
