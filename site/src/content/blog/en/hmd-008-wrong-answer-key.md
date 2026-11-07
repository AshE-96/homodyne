---
title: "If a benchmark's answer key is wrong, which AI loses?"
description: "A wrong answer key only takes points from models that answered correctly, so key errors can flip a leaderboard. Evidence from MMLU-Redux and a toy demo."
lang: en
translationKey: hmd-008-companion
hmd: HMD-008
kind: companion
date: 2027-01-08
tags: ["answer key", "label errors", "benchmarks", "audit", "MMLU"]
sources:
  - title: "Gema et al. (2024): Are We Done with MMLU?, arXiv 2406.04127"
    url: "https://arxiv.org/abs/2406.04127"
  - title: "Northcutt, Athalye, Mueller (NeurIPS 2021): Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks, arXiv 2103.14749"
    url: "https://arxiv.org/abs/2103.14749"
  - title: "SimpleQA Verified, arXiv 2509.07968 (v2, 10 March 2026)"
    url: "https://arxiv.org/abs/2509.07968"
  - title: "Global MMLU, arXiv 2412.03304"
    url: "https://arxiv.org/abs/2412.03304"
  - title: "Mehr News (1 Shahrivar 1405 / August 2026): preliminary Konkur key and objections (Persian)"
    url: "https://www.mehrnews.com/news/6925042"
  - title: "Etemad Online (6 Mordad 1400 / July 2021): Sanjesh head on removing two questions (Persian)"
    url: "https://www.etemadonline.com/%D8%A8%D8%AE%D8%B4-%D8%A7%D8%AC%D8%AA%D9%85%D8%A7%D8%B9%DB%8C-23/507687-%D8%B3%D9%88%D8%A7%D9%84-%D8%B1%DB%8C%D8%A7%D8%B6%DB%8C-%D8%A7%D8%B2-%DA%A9%D9%86%DA%A9%D9%88%D8%B1-%D8%AD%D8%B0%D9%81"
  - title: "National Capital Authority: Canberra"
    url: "https://www.nca.gov.au/"
  - title: "Eurasianet: Kazakhstan capital reverts to Astana"
    url: "https://eurasianet.org/kazakhstan-capital-reverts-to-astana-ending-brief-stint-as-nur-sultan"
---

When a benchmark's answer key is wrong, the model that usually loses is the one that answered correctly, because a wrong key can only take points away from correct answers. If the key error repeats a popular misconception, it gets worse: a model that shares the misconception actually gains points. Key errors are not neutral noise. They can change who wins a comparison unless the key is audited with a clear denominator and disputes are settled by evidence.

This post accompanies [Homodyne episode HMD-008](/en/episodes/hmd-008/). The [Persian version](/fa/blog/hmd-008-wrong-answer-key/) is the original.

> **Key Takeaways**
> - A wrong key only penalises whoever answered correctly, so the more capable model pays a larger share of the key's errors.
> - Researchers re-read 5,700 MMLU questions and estimated that 6.49% of MMLU questions contain errors; in the Virology subset, 57% of the questions they analysed did.
> - In our ILLUSTRATIVE toy experiment, eight wrong keys out of a hundred questions were enough to flip the winner.
> - A key error rate only means something with a random sample and a stated denominator. Homodyne's own Bluff pilot audit has not been run yet.

## Why does a wrong key only hurt correct answers?

Take one question whose key is wrong. There are four cases:

| | Model answered correctly | Model answered wrongly |
|---|---|---|
| **Key correct** | Scores | Does not score |
| **Key wrong** | Loses the point | Loses nothing |

If the model was wrong to begin with, it would not have scored under a correct key either, so a wrong key takes nothing from it. If it was right, it is now marked wrong. The conclusion is simple: a wrong key only removes points from correct answers.

If key errors are random, which model suffers more? The one that answers correctly more often. Each model's expected loss is roughly its accuracy multiplied by the key's error rate. Key errors therefore compress the gap between a strong model and an average one and lower the test's ceiling, which the better models hit first.

## How common are answer-key errors in real benchmarks?

Common enough to appear in famous tests. MMLU is one of the best-known language-model benchmarks: multiple-choice questions across 57 subjects. Gema and colleagues manually re-annotated 5,700 of its questions across all 57 subjects and called the result MMLU-Redux. They estimate that 6.49% of MMLU questions contain errors, and in the Virology subset 57% of the questions they analysed had problems ([arXiv 2406.04127](https://arxiv.org/abs/2406.04127)).

It is not the only evidence. In 2021 Northcutt and colleagues examined the test sets of ten widely used machine-learning datasets spanning images, text and audio. They estimate an average of at least 3.3% label errors, and at least 6% in the ImageNet validation set ([arXiv 2103.14749](https://arxiv.org/abs/2103.14749)).

So the useful question is not whether a key has errors, but whom those errors hurt.

## Why is a "popular myth" error worse than a typo?

Because real key errors are rarely random. Keys are written by people or scraped from the web, and misconceptions common among people slip in more easily. Many people think Australia's capital is Sydney; it is Canberra ([National Capital Authority](https://www.nca.gov.au/)). A model trained on web text that repeats the same belief does not lose under such a key. It scores.

To see the effect, we built a 100-question quiz with two fictional models. Everything is **ILLUSTRATIVE**; no real model was called. Model K knows more; model P repeats popular beliefs. In the key, we deliberately wrote eight answers as those popular beliefs:

| Key | K | P | Leader |
|---|---|---|---|
| Key v1, with eight "popular myth" errors | 73 | 80 | P |
| Adjudicated key v2 | 80 | 76 | K |
| Same eight errors as random typos | 73 | 74 | P |

Under the broken key P leads; under the corrected key K does. Even when the same eight errors are typos that match no model's answer, the order flips in this close race, because K loses seven correct answers and P only two.

Published research has seen an effect of the same kind. Northcutt and colleagues showed that on ImageNet with corrected labels, if the share of originally mislabelled test examples rises by just 6%, ResNet-18 outperforms ResNet-50. That finding concerns image classifiers, not chatbots, but the lesson carries over: "which model is better" depends on the quality of the key.

## Where do key errors come from?

Four usual places:

1. **Popular belief:** Sydney instead of Canberra.
2. **Time:** Kazakhstan's capital, Astana, was renamed Nur-Sultan in March 2019 and became Astana again in September 2022 ([Eurasianet](https://eurasianet.org/kazakhstan-capital-reverts-to-astana-ending-brief-stint-as-nur-sultan)). A key written in 2020 is wrong today. A question whose answer changes over time needs a date.
3. **Spelling:** "Brasília" and "Brasilia" are the same answer. The key must list acceptable forms or correct answers get marked wrong.
4. **Translation:** translation can add a clue or create an ambiguity. The Global-MMLU study found that 28% of MMLU questions require culturally sensitive knowledge and 84.9% of its geography questions focus on North America or Europe ([arXiv 2412.03304](https://arxiv.org/abs/2412.03304)). Sometimes the "right" answer depends on who wrote the question and for whom, which matters to Homodyne because much of our audience asks in Persian.

## How do you audit a key without fooling yourself?

With a clear denominator, two independent reviewers and evidence-based adjudication. The first temptation is to re-read only the questions where models disagreed with the key. In our toy experiment there were 36 of those, and eight had wrong keys. The report would say "22% of keys are wrong", while the planted rate is 8%. That approach is excellent for finding errors and useless for saying what share of the whole key is wrong.

A random sample of 30 questions from the same quiz finds three errors, with a 95% Wilson confidence interval of about 3% to 26%: wide, but honest, and it contains the true 8%.

Then comes adjudication. Voting reintroduces the popular-belief problem: if most people say Sydney, the vote says Sydney. A better approach is two reviewers working separately, blind to which model gave which answer. Where they disagree, a primary source decides and the reason is logged. If no source can be found, that does not mean no answer exists; rewrite or drop the question rather than filling the key with a guess.

Iran's national university entrance exam, the Konkur, works on this logic. A preliminary key is published, and according to Mehr News (August 2026) objections are accepted only through an electronic response system ([Mehr News](https://www.mehrnews.com/news/6925042)). Then a final key follows, sometimes with a corrected answer and sometimes with a question removed. In 2021 the head of Iran's testing organisation (Sanjesh) announced that two questions would be removed ([Etemad Online](https://www.etemadonline.com/%D8%A8%D8%AE%D8%B4-%D8%A7%D8%AC%D8%AA%D9%85%D8%A7%D8%B9%DB%8C-23/507687-%D8%B3%D9%88%D8%A7%D9%84-%D8%B1%DB%8C%D8%A7%D8%B6%DB%8C-%D8%A7%D8%B2-%DA%A9%D9%86%DA%A9%D9%88%D8%B1-%D8%AD%D8%B0%D9%81)). Many AI leaderboards have no such objection window.

## Where does Homodyne's own audit stand?

It has not been run. For our own benchmark, Bluff, we are preparing a 60-question pilot in which every question has a file: text, acceptable answers, source and date checked. The key audit for this pilot has not been carried out, and no number from it appears here; the real result will be published separately.

We are not alone in this. SimpleQA Verified is a rebuilt version of a short-answer question benchmark, with 1,000 prompts, created to fix noisy and incorrect labels, topical bias and redundancy ([arXiv 2509.07968](https://arxiv.org/abs/2509.07968)). A good benchmark, like an exam key, has a preliminary and a final version. The step-by-step audit protocol and reproduction commands are in the [deep dive for this episode](/en/blog/hmd-008-answer-key-audit/).

## What this does not show

- It does not show that any real model's ranking today is wrong. Our experiment used fictional models and planted errors (ILLUSTRATIVE).
- The 6.49% figure is one research group's estimate for MMLU, not an error rate for all benchmarks.
- The ResNet result concerns image models and does not transfer directly to chatbots.
- Failing to find a source in a search does not mean no answer exists.
- The Bluff pilot audit has not been run.

## What should you ask before trusting a leaderboard?

Three questions. Has anyone audited this test's answer key? If so, on how many questions, and how were they chosen? And which version of the key produced the result? If none of these is clear, read that "ranked first" as a preliminary key, not a final one. It is the same logic as the [HMD-006 post on numerators and denominators in error rates](/en/blog/hmd-006-error-rate-denominator/), applied this time to the answer key itself.
