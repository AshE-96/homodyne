---
title: "AI error rates: what does 'fewer mistakes' hide?"
description: "An AI error rate means nothing without its denominator. One SimpleQA table shows 26% vs 75% errors, largely bought with 52% 'I don't know' answers."
lang: en
translationKey: hmd-006-companion
hmd: HMD-006
kind: companion
date: 2026-12-25
tags: ["error rate", "hallucination", "abstention", "benchmarks", "SimpleQA"]
sources:
  - title: "OpenAI (September 2025): Why language models hallucinate"
    url: "https://openai.com/index/why-language-models-hallucinate/"
  - title: "Kalai et al. (2025): Why Language Models Hallucinate, arXiv 2509.04664"
    url: "https://arxiv.org/abs/2509.04664"
  - title: "AA-Omniscience (Artificial Analysis, November 2025), arXiv 2511.13029"
    url: "https://arxiv.org/abs/2511.13029"
  - title: "Vectara Hallucination Leaderboard (updated 22 October 2026)"
    url: "https://github.com/vectara/hallucination-leaderboard"
  - title: "Kirichenko et al. (2025): AbstentionBench, arXiv 2506.09038"
    url: "https://arxiv.org/abs/2506.09038"
  - title: "Bean et al. (NeurIPS 2025): Measuring what Matters, arXiv 2511.04703"
    url: "https://arxiv.org/abs/2511.04703"
---

When someone says an AI model "makes fewer mistakes", they usually leave out two things: what the error was divided by (the denominator), and how often the model declined to answer at all. A model can lower its error rate simply by saying "I don't know" more often, without giving a single extra correct answer. Treat any error percentage as incomplete until you know its numerator, its denominator and its share of abstentions.

This post accompanies [Homodyne episode HMD-006](/en/episodes/hmd-006/) and is written for readers who have not watched it. The [Persian version](/fa/blog/hmd-006-error-rate-denominator/) is the original.

> **Key Takeaways**
> - Every answer is correct, wrong or "I don't know". Each error rate divides those three in a particular way.
> - In a SimpleQA table published by OpenAI, error rates of 26% vs 75% sit next to abstention rates of 52% vs 1%. Accuracy was 22% vs 24%.
> - Two figures both called "hallucination rate", 1.8% and 81%, use different tasks, formulas and models. They cannot be compared.
> - Before trusting an error rate, ask: how many out of how many? And how many were never answered?

## Why can one set of answers have three correct error rates?

Because an error rate is a fraction, and each report picks its own denominator. Suppose an assistant answers ten questions: five correct, two wrong, three "I don't know". These ten cards are made up for teaching (**ILLUSTRATIVE**), but the arithmetic is real.

You can write this assistant's error rate in at least three ways, and all three are arithmetically right:

| Question | Numerator | Denominator | Result |
|---|---|---|---|
| Of all questions, how many were wrong? | 2 | 10 | 20% |
| Of the answers it gave, how many were wrong? | 2 | 7 | about 29% |
| Of the questions it did not get right, how many did it answer wrongly instead of abstaining? | 2 | 5 | 40% |

The third fraction is not our invention. The AA-Omniscience benchmark defines its "hallucination rate" exactly this way: wrong answers divided by all answers that were not correct, meaning wrong, partially correct and abstained ([AA-Omniscience, section 2.4.3](https://arxiv.org/abs/2511.13029)).

So "error rate" on its own is a number without an owner. The first question is always: how many, out of how many?

## What does the SimpleQA table hide?

The abstention row. In September 2025, in a post titled "Why language models hallucinate", OpenAI compared two of its models on SimpleQA, a test of short, fact-seeking questions ([OpenAI](https://openai.com/index/why-language-models-hallucinate/)). Each column of the table sums to 100:

| | gpt-5-thinking-mini | o4-mini |
|---|---|---|
| Abstention ("I don't know") | 52% | 1% |
| Accuracy (correct out of all questions) | 22% | 24% |
| Error rate (wrong out of all questions) | 26% | 75% |

Read only the last row and the newer model makes almost three times fewer mistakes. Yet the older model gave slightly more correct answers: 24% against 22%. Most of the gap comes from the row headlines tend to skip: the newer model abstained on 52% of questions, the older one on 1%.

Now change the denominator and count only the questions each model actually answered. This is our arithmetic on the table's own numbers: the newer model was wrong on 26 of 48 answers, about 54%; the older model on 75 of 99, about 76%. The newer model is still wrong less often when it does answer, but the gap is nowhere near threefold.

## Is "fewer errors through silence" good or bad?

It depends on what a wrong answer costs you. If you are asking about a drug dose or a contract clause, an honest "I don't know" is far better than a confident wrong answer. If you want name ideas for a café, a bad guess costs little.

The authors of the paper behind OpenAI's post, Kalai and colleagues, argue that tests counting only correct answers reward guessing. In their words, under binary grading "abstaining is strictly sub-optimal" ([arXiv 2509.04664](https://arxiv.org/abs/2509.04664)). It is like a multiple-choice exam with no negative marking: a guess might score, silence never does.

There are two extremes to watch. An assistant that answers everything with "I don't know" has zero errors and zero usefulness. Its risk, wrong answers divided by answers given, is zero divided by zero: undefined, not zero. A table that prints zero instead of "undefined" makes the most useless assistant look like the best. Under a score that penalises wrong answers and gives zero for "I don't know", that assistant scores exactly zero. We call this the "line of silence": a model below it did worse than an assistant that never speaks.

The other extreme is a model that almost never abstains. AbstentionBench tested 20 models on 20 datasets and reported that reasoning fine-tuning reduced abstention by 24% on average ([arXiv 2506.09038](https://arxiv.org/abs/2506.09038)). That is a finding of that study, not a law for every model.

## Why can't two "hallucination rates" be compared?

Because they may not count the same thing. Take two real figures, both labelled "hallucination rate": 1.8% and 81%. "Which model is more reliable?" has no answer here.

- **1.8%** is the lowest figure on the Vectara leaderboard (updated 22 October 2026). A model is given a document and asked to summarise it. An evaluator model, HHEM-2.3, judges whether each summary is consistent with the document, and the hallucination rate is 100 minus the percentage of consistent summaries ([Vectara](https://github.com/vectara/hallucination-leaderboard)).
- **81%** is the hallucination rate of GPT-5 (high) on AA-Omniscience. No document is given; questions are answered from memory. The formula is the third fraction above. In the same paper Grok 4 also has 39% accuracy but a 64% hallucination rate: two models with equal accuracy filled different shares of what they did not know with wrong answers rather than abstentions.

Faithfulness to a given text is one property; answering correctly from memory is another. Both have been called "hallucination". Neither benchmark is bad, and both publish their definitions. The trouble starts when two definitions are compared under one name.

This is not one table's problem. A NeurIPS 2025 study used 29 expert reviewers to examine 445 language-model benchmarks and concluded that common patterns in how phenomena are defined and scored undermine the validity of the claims made with them ([Measuring what Matters](https://arxiv.org/abs/2511.04703)).

## What should you ask before believing a "fewer errors" claim?

The episode's tool is a one-page "construct card". The construct is what you actually want to know, such as "can I rely on this answer". What gets counted, such as "wrong divided by answered", is only a proxy for it. A thermometer measures temperature precisely, but a normal temperature does not mean you are healthy.

For any "makes fewer mistakes" claim, write four lines:

1. What do we want? For example, an answer you can rely on.
2. What was counted? For example, wrong answers to short questions with no supporting document.
3. What are the numerator and denominator? Wrong out of all, out of answered, or out of not-correct?
4. What can this number not see? For example, the abstention share, long answers, or languages other than English.

A fifth line is worth adding: which date and which model version does the number belong to? If you cannot answer one of these, the number is not complete yet. Formulas, data and reproduction commands are in the [deep dive for this episode](/en/blog/hmd-006-abstention-metrics/).

## What this does not show

- It does not show that OpenAI's newer model is better or worse than o4-mini. It shows only that a "three times fewer errors" headline leaves out a row.
- It does not show that Vectara or AA-Omniscience are bad benchmarks.
- It does not show that a model saying "I don't know" actually knows that it does not know. We see behaviour, not the model's internals.
- The SimpleQA figures date from September 2025 and that one test. They are not today's model rankings.
- The ten cards here are ILLUSTRATIVE. Homodyne's own benchmark, Bluff, has not been run yet, and no result from it is reported.

## The short answer

When people say an AI makes fewer mistakes, they usually do not say out of how many, or at the cost of how many "I don't know" answers. If you ever compare two models yourself, put four numbers side by side: accuracy, coverage, risk, and a score that announces its penalty for wrong answers in advance.
