---
title: "Every number in this AI table is right. Why does it mislead?"
description: "Because each correct number answers a chosen question: which subset, which metric, which attempts. One error-free table can crown two different winners."
lang: en
translationKey: hmd-014-companion
hmd: HMD-014
kind: companion
date: 2027-02-26
tags: ["benchmarks", "Simpson's paradox", "leaderboards", "selective reporting", "holdout", "LLM evaluation"]
sources:
  - title: "Singh et al. (2025). The Leaderboard Illusion. arXiv 2504.20879 (v2, 12 May 2025)"
    url: "https://arxiv.org/abs/2504.20879"
  - title: "BetaKit (2 May 2025). Cohere Labs head calls \"unreliable\" AI leaderboard rankings a \"crisis\" in the field (secondary source)"
    url: "https://betakit.com/cohere-labs-head-calls-unreliable-ai-leaderboard-rankings-a-crisis-in-the-field/"
  - title: "Bickel, Hammel, O'Connell (1975). Sex Bias in Graduate Admissions: Data from Berkeley. Science 187(4175):398–404"
    url: "https://www.science.org/doi/10.1126/science.187.4175.398"
  - title: "Wikipedia, Simpson's paradox (UC Berkeley gender bias section; secondary source)"
    url: "https://en.wikipedia.org/wiki/Simpson%27s_paradox"
  - title: "Zhang et al. (2024). A Careful Examination of Large Language Model Performance on Grade School Arithmetic. arXiv 2405.00332 v4"
    url: "https://arxiv.org/abs/2405.00332"
  - title: "Reuel et al. (2024). BetterBench: Assessing AI Benchmarks, Uncovering Issues, and Establishing Best Practices. arXiv 2411.12990"
    url: "https://arxiv.org/abs/2411.12990"
---

Because each correct number answers only one question, and whoever built the table chose that question: which slice of the data, which metric, and which attempts to report. In this episode's teaching table no cell is wrong, yet the same table can crown model A or model B. And where the evidence is thin, "unknown" is more honest than a green tick.

> **Key Takeaways**
> - In our teaching table (ILLUSTRATIVE), B is 90.5% accurate on the questions it answered and A is 81.2%, yet A leads on both the easy and the hard questions.
> - The reason is simple: A answered 390 of 400 hard questions, B only 60. This reversal is called Simpson's paradox.
> - With a penalty of one point per wrong answer A wins; with three, B wins. The winner flips at k = 1.74.
> - If ten equally skilled versions are tested and only the best is published, the published score in our simulation averages 74.9% against a true skill of 70%.
> - Zero errors in 20 checks means the real rate could still be up to 16.1%; that result is "unknown", not "pass".

This post accompanies [Homodyne episode HMD-014](/en/episodes/hmd-014/). Formulas, reproduction commands and limitations are in the [deep dive for the same episode](/en/blog/hmd-014-mislead-lab-methods/).

## How can an error-free table have two winners?

The table below is section 1 of the output of `mislead_lab.py` (**ILLUSTRATIVE**: we built the counts by hand so every cell can be checked, and no model was called). A thousand questions, 600 easy and 400 hard, and two systems, A and B. "Answered" means the system gave an answer instead of "I don't know".

| System | Subset | Questions | Answered | Correct | Accuracy on answered |
|---|---|---|---|---|---|
| A | easy | 600 | 600 | 570 | 95.0% |
| A | hard | 400 | 390 | 234 | 60.0% |
| A | all | 1,000 | 990 | 804 | 81.2% |
| B | easy | 600 | 590 | 555 | 94.1% |
| B | hard | 400 | 60 | 33 | 55.0% |
| B | all | 1,000 | 650 | 588 | 90.5% |

Four true headlines come out of this one table: "overall accuracy: B wins" (90.5% vs 81.2%); "accuracy on easy questions: A wins" (95.0% vs 94.1%); "accuracy on hard questions: A wins" (60.0% vs 55.0%); and "correct out of all 1,000 questions: A wins" (80.4% vs 58.8%). All four are accurate. They do not agree on the winner.

## Why does pooling the groups reverse the trend?

Because the denominators differ. Of 400 hard questions, A answered 390 and B only 60; B said "I don't know" to the rest. So 39% of A's answers came from hard questions, against just 9% of B's. Pooling everything mixes two different things: how much each system knows, and which questions it chose to attempt. B is not more accurate. It picked an easier exam for itself.

This reversal is called Simpson's paradox: a trend that holds in every group flips when the groups are combined. The name sounds alarming, but the cause is usually just this: the groups carry different weights on the two sides of the comparison.

## What was the classic real case?

The best-known one comes from graduate admissions at the University of California, Berkeley, in autumn 1973. Of 8,442 men who applied, about 44% were admitted; of 4,321 women, about 35% ([Wikipedia, citing the original paper](https://en.wikipedia.org/wiki/Simpson%27s_paradox)). The total pointed to bias against women. Bickel, Hammel and O'Connell, writing in *Science* (1975), looked department by department. Women had applied more often to departments that were more selective for everyone, and once department was taken into account the pooled data showed "a small but statistically significant bias in favor of women". It is the same mechanism as A and B, with "hard department" in place of "hard question".

## How do the choice of metric and penalty change the winner?

"Accuracy on answered questions" rewards a system that answers little; "correct out of all questions" rewards one that always answers. [Episode HMD-006](/en/episodes/hmd-006/) made the same point about the denominator of an error rate: the assistant with the fewest errors is the one that answers nothing.

A third ruler is the negative marking built in [episode HMD-010](/en/episodes/hmd-010/): +1 for a right answer, 0 for "I don't know", −k for a wrong one. A has 186 wrong answers, B only 62. Section 3 of the output (points per 100 questions, **ILLUSTRATIVE**):

| Penalty k | A | B | Winner |
|---|---|---|---|
| 0 | 80.4 | 58.8 | A |
| 1 | 61.8 | 52.6 | A |
| 2 | 43.2 | 46.4 | B |
| 3 | 24.6 | 40.2 | B |

The winner flips at exactly k = 1.74. Whoever picks k is, in effect, picking the winner.

## What does reporting only the best attempt do?

It inflates the score without a single fake number. `mislead_lab.py` creates ten versions of a model, all with a true skill of exactly 70%, and tests each on 200 questions (**ILLUSTRATIVE**, seed 7). Scores ranged from 65.0% to 74.5% and averaged 69.9%, but only the best, 74.5%, was published. Over 2,000 repeats of this game, the published best averaged 74.9% against a true skill of 70%. The 74.5% was really obtained; the other nine tests were simply never reported.

In the real world, *The Leaderboard Illusion* (April 2025) highlighted this mechanism at Chatbot Arena, a leaderboard where users compare answers from two anonymous models side by side and vote for one. The authors, from Cohere, Cohere Labs and several universities, write that a few providers could test several variants privately, and that their ability to "choose the best score" leads to biased Arena scores. In one case they counted 27 private variants tested by Meta before the Llama 4 release ([arXiv 2504.20879](https://arxiv.org/abs/2504.20879)). LMArena, which runs the leaderboard, denied treating providers unfairly, listed what it called "factual errors" in the paper, and said its pre-release testing policy had been public ([BetaKit, 2 May 2025](https://betakit.com/cohere-labs-head-calls-unreliable-ai-leaderboard-rankings-a-crisis-in-the-field/)). We are not judging that dispute; we built the mechanism and saw how easily it works.

## How does a holdout help, and where does it fall short?

A holdout means testing the chosen version on questions it has never seen. If its high score came from luck, that shows up there. In the seed-7 run the chosen version scored 74.0% on 200 fresh questions: a single holdout run is noisy too, and this one again came out above the true skill. We did not change the seed to get a tidier run, because that is exactly the behaviour this episode is about. The lesson is in the average: over 2,000 repeats, the published best scored 74.9% and the same version scored 69.9% on the holdout, back where it belongs.

A holdout has a second purpose: contamination, the chance that a public test's questions were already in a model's training data. In 2024 a team at Scale AI built GSM1k: 1,205 new maths problems in the style of the well-known GSM8k test, written by human annotators and kept unpublished so that it would not itself be contaminated. Some models' accuracy dropped by up to 8%, and families such as Phi and Mistral showed signs of overfitting at almost every size; but many models, especially frontier ones, showed few signs of it ([arXiv 2405.00332](https://arxiv.org/abs/2405.00332), version 4). Not finding signs of contamination is still different from proving a model clean.

## Why is "unknown" more honest than a green tick?

Because "we found no errors" is not the same as "there are no errors". Suppose the rule is that a system must invent answers to no more than 5% of unanswerable questions (the 5% is a design choice, not a standard). Section 6 of the output, with 95% Wilson intervals:

| Errors / checked | 95% interval | Status |
|---|---|---|
| 0 of 2 | 0 to 65.8% | unknown |
| 0 of 20 | 0 to 16.1% | unknown |
| 0 of 100 | 0 to 3.7% | pass |
| 3 of 20 | 5.2 to 36.0% | breach |

With zero errors, at least 73 checked questions are needed before "pass" is justified. The channel's `bluff_lab.py` tool reports exactly this on its sample data, with two unanswerable questions and zero errors: UNKNOWN.

## Three questions for any table

1. **Which subset?** Put the overall figure next to each group's figure, and check how many questions from each group each system answered.
2. **Which metric?** If only one metric is reported, ask why that one. If there is a penalty, ask who chose k, and when.
3. **What was not shown?** How many versions, prompts, attempts? Is there a holdout? Where evidence was thin, does the table say "unknown", or is it green?

These are not personal preferences. The BetterBench study assessed 24 AI benchmarks against a framework of 46 best practices, found large quality differences, and reported that most do not report the statistical significance of their results ([arXiv 2411.12990](https://arxiv.org/abs/2411.12990)). How many questions a gap needs before it can be seen at all was the subject of [episode HMD-012](/en/episodes/hmd-012/).

## What this does not show

- The numbers for A and B are teaching numbers (ILLUSTRATIVE) and belong to no real model or company.
- It does not show that Chatbot Arena, Meta or any specific table or company cheated. On Arena we report only the paper's findings and LMArena's response, with dates.
- We do not say whether Berkeley discriminated; only that the overall and the per-department numbers told different stories. The Berkeley figures come from consistent secondary sources; we did not read the *Science* paper directly.
- We do not claim that all or most tables mislead; the only quantitative claim about benchmark quality comes from BetterBench.
- A small error-free audit does not prove safety, and a single holdout run is a noisy sample too.

*Persian original: [جدولی که همهٔ عددهایش درست است چطور گمراه می‌کند؟](/fa/blog/hmd-014-correct-table-misleads/)*
