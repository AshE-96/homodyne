---
title: "Can negative marking make an AI more careful?"
description: "Negative marking sets a silence line at t = k/(k+1). It makes an AI more careful only if the model changes its answers and its confidence is honest."
lang: en
translationKey: hmd-010-companion
hmd: HMD-010
kind: companion
date: 2027-01-22
tags: ["negative marking", "AI hallucination", "calibration", "benchmarks", "abstention"]
sources:
  - title: "Kalai, Nachum, Vempala, Zhang (2025). Why Language Models Hallucinate. arXiv 2509.04664 v1"
    url: "https://arxiv.org/abs/2509.04664"
  - title: "OpenAI (2025). Why language models hallucinate"
    url: "https://openai.com/index/why-language-models-hallucinate/"
  - title: "AA-Omniscience. arXiv 2511.13029 (November 2025)"
    url: "https://arxiv.org/abs/2511.13029"
  - title: "Zoomit: calculating Konkur test percentages and negative marking (October 2026, secondary source, Persian)"
    url: "https://www.zoomit.ir/websites/469821-calculate-test-percentage-negative-score/"
---

On paper, yes. A penalty for wrong answers creates a "silence line": if each wrong answer costs k points, answering only pays on average when your chance of being right is above k/(k+1). But an AI only becomes more careful in practice if two things hold: the model actually changes its answers when told the rule, and its confidence matches reality. The experiment that tests both on a real model has not been run yet.

> **Key Takeaways**
> - Under the common Konkur rule (+3 right, −1 wrong), a blind guess on a four-option question is worth exactly zero on average.
> - The silence line is t = k/(k+1): 50% for a penalty of 1, 75% for 3, 90% for 9. Most AI benchmarks have no penalty, so their silence line is zero.
> - In our simulation (ILLUSTRATIVE), an overconfident answerer followed the rule exactly and still scored below zero.
> - The four-condition test on a real model has not run. Its design and three possible outcomes are below.

This post accompanies [Homodyne episode HMD-010](/en/episodes/hmd-010/). The full derivation, calibration, and a guide to running the experiment are in the [deep dive for this episode](/en/blog/hmd-010-silence-line-calibration/).

## What is a blind guess worth in the Konkur?

Zero. The Konkur is Iran's national university entrance exam, and its multiple-choice sections are known for negative marking. Under the commonly reported rule, a correct answer earns +3 and a wrong one costs −1, so three wrong answers cancel one right one ([Zoomit, in Persian](https://www.zoomit.ir/websites/469821-calculate-test-percentage-negative-score/)). Guess blindly among four options and you win 3 points one time in four and lose 1 point three times in four. Three minus three is zero.

Informed guessing still pays. Rule out one option with confidence and guess among three, and the expected value is one ninth of a correct answer; rule out two and be genuinely torn between the last two, and it is one third. So the Konkur penalty does not forbid guessing; it makes uninformed guessing worthless.

These are averages, and they assume you really are as torn as you think. That assumption becomes the main problem below.

## What is the silence line, and where does it come from?

The silence line is the lowest probability of being right at which answering pays on average. Score a correct answer +1, "I don't know" 0, and a wrong answer −k. If your chance of being right is p, the expected value of answering is p − k(1 − p). That beats the zero you get for staying silent only when p is greater than k/(k+1).

| Penalty per wrong answer (k) | Silence line (t) |
|---|---|
| 0 (most AI benchmarks) | 0% |
| 1/3 (Konkur, in units of one correct answer) | 25% |
| 1 | 50% |
| 3 | 75% |
| 9 | 90% |

The Konkur silence line is exactly 25%, the chance of a blind guess among four options, which is why the blind guess is worth zero. The higher the penalty, the more sure you need to be before answering.

## Why do language models guess?

Because most tests used to rank them have no penalty: right is 1, wrong is 0, and "I don't know" is also 0. The silence line of that rule is zero, so guessing is never worse than staying silent, even when the model has no idea.

Kalai, Nachum, Vempala and Zhang make exactly this comparison in "Why Language Models Hallucinate" (September 2025): language models, like students facing a hard exam question, guess under uncertainty because standard grading rewards it ([arXiv 2509.04664](https://arxiv.org/abs/2509.04664)).

Their proposal is to state the rule in the prompt itself, with an instruction such as "Answer only if you are > t confident, since mistakes are penalized t/(1 − t) points". The penalty t/(1 − t) is just k; solve for t and you get t = k/(k+1) again. The paper's proposal is the silence line written from the other side.

One small slip: version 1 of the paper (4 September 2025, still the only arXiv version as of 7 November 2026) gives the example "t = 0.75 (penalty 2)", but its own formula gives 0.75 / 0.25 = 3. The typo takes nothing from the idea. It is a reminder to recompute printed numbers when you can, the lesson of [episode HMD-008 on wrong answer keys](/en/episodes/hmd-008/).

## How is rescoring different from instructing?

Rescoring takes answers a model has already given and scores them again under a penalty rule. That can change who tops a leaderboard, as [episode HMD-002](/en/episodes/hmd-002/) showed, but the model did nothing; only the ruler changed. Instructing tells the model the rule before the question and collects fresh answers. Only that shows whether behaviour changes.

The channel's lab tool, `tools/bluff_lab.py`, records the difference explicitly: the condition with no rule in the prompt (`plain`) is only rescored at k = 3 for comparison. "More careful" means the behaviour changes, not just the number.

## What happens if the model's confidence is not honest?

Then the rule does not help. To see this we built two simulated answerers (**ILLUSTRATIVE**: they are not language models and no model was called). On 1,000 made-up questions, the first is calibrated: its confidence equals the true probability of being right. The second knows exactly as much but always believes it is 0.25 more certain than it is. Both answer only above the silence line. Results with a penalty of 3 (silence line 75%), seed 5:

| Answerer (ILLUSTRATIVE) | Points per question | Coverage | Risk |
|---|---|---|---|
| Calibrated, answers only above the line | 0.130 | 29% | 14% |
| Overconfident, answers only above the line | −0.054 | 59% | 27% |
| Calibrated, always answers | −0.792 | 100% | not reported |

Coverage is the share of questions answered; risk is the share of given answers that were wrong. The calibrated answerer turned a negative score into a positive one by following the rule. The overconfident one followed the same rule exactly, but with inflated confidence it answered about twice as many questions and finished below zero. With seed 11 the direction was the same (0.125, −0.012 and −0.764).

The same arithmetic gives a simple test of honest confidence. Someone who answers only when more than 75% sure, and whose confidence is right, should on average get fewer than 25% of their answers wrong. The overconfident answerer's 27% crosses that line. The rule is fine; the compass is broken.

## What would a test on a real model look like?

This test has not been run, and no numbers from it exist. The design: one model, one fixed question set, four prompts; one with no rule (`plain`) and three stating a silence line of 50%, 75% and 90% (`t50`, `t75`, `t90`). Each prompt gets fresh answers, labelled with one shared adjudication guide as correct, wrong, or "I don't know". Then coverage, risk and the penalised score go side by side.

Before looking at any results, "more careful" gets a written definition: the error rate falls without correct answers falling by the same amount. With that definition, each possible outcome has a clear meaning:

1. **Errors fall and correct answers mostly stay.** The model heard the rule and became more careful.
2. **Nothing changes.** You can change the score with a new rule, but not the behaviour with this prompt.
3. **"I don't know" rises and correct answers fall with it.** That is not caution; it is just saying less.

Whatever the result, it will be published in a separate video with the model name, version and run date. Meanwhile, a small exercise: end your next real question to a chatbot with "If you are less than 90% sure, say you don't know" and see whether the answer changes. One try proves nothing.

## Who decides the right penalty?

The cost of a mistake in the task at hand, not the maths or the model: a wrong answer in movie trivia is funny, while one about a shop's return deadline causes real trouble. Benchmarks make different choices too. AA-Omniscience uses an index from −100 to 100 in which zero means a model answered as many questions wrong as right ([arXiv 2511.13029](https://arxiv.org/abs/2511.13029)); our reading is that this works out to k = 1. k is a product decision, not a universal constant.

## What this does not show

- It does not show whether today's models are calibrated. We make no claim about any specific model.
- The simulated answerers are not language models, and their numbers are ILLUSTRATIVE. They show the mechanism, not how any chatbot behaves.
- Rescoring old answers never replaces a fresh run. The effect of telling a real model the rule is unknown until the follow-up run.
- The Konkur +3/−1 rule comes from several consistent secondary sources; we did not read the official booklet directly.
- Expected value is not a guarantee; it describes the average over many decisions, not the outcome of one question.

*Persian original: [نمرهٔ منفی می‌تواند هوش مصنوعی را محتاط‌تر کند؟](/fa/blog/hmd-010-negative-marking-ai/)*
