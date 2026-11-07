---
title: "Which AI says \"I don't know\" at the right time?"
description: "Abstaining on time means reading coverage and risk together under a rule that prices mistakes. Our Bluff method; results follow the data lock."
lang: en
translationKey: hmd-016-companion
hmd: HMD-016
kind: companion
date: 2027-03-12
tags: ["abstention", "I don't know", "risk-coverage", "preregistration", "benchmarks", "AI hallucination"]
sources:
  - title: "Kirichenko, Ibrahim, Chaudhuri, Bell (2025). AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions. arXiv 2506.09038 v1"
    url: "https://arxiv.org/abs/2506.09038"
  - title: "El-Yaniv and Wiener (2010). On the Foundations of Noise-free Selective Classification. JMLR 11:1605–1641"
    url: "https://www.jmlr.org/papers/v11/el-yaniv10a.html"
  - title: "Nosek, Ebersole, DeHaven, Mellor (2018). The preregistration revolution. PNAS 115(11):2600–2606"
    url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/"
  - title: "Miller (2024). Adding Error Bars to Evals. arXiv 2411.00640"
    url: "https://arxiv.org/abs/2411.00640"
  - title: "Kalai, Nachum, Vempala, Zhang (2025). Why Language Models Hallucinate. arXiv 2509.04664"
    url: "https://arxiv.org/abs/2509.04664"
---

A model says "I don't know" at the right time when it does two things at once: it answers a large share of questions (high coverage) and few of those answers are wrong (low risk), judged under a scoring rule that reflects what a mistake costs. Which real model does this best is what Homodyne's Bluff test is built to answer, but that run has not been done or locked yet, and results will only be published after the data lock. This post explains the method and how to read the result, using data that is openly made up.

> **Key Takeaways**
> - "At the right time" has two halves: coverage (how often it answers) and risk (how often its answers are wrong). Either one alone misleads.
> - Under "right +1, I don't know 0, wrong −3", an assistant that always stays silent scores exactly 0, so 0 is the baseline.
> - The analysis rule and the single confirmatory comparison are written down before the run, and the answer file is locked with a SHA-256 hash.
> - Every number here comes from fictional models (ILLUSTRATIVE). None is attributed to any real model.

This post accompanies [episode HMD-016](/en/episodes/hmd-016/). The formulas, the bootstrap and the commands to reproduce everything are in the [deep dive for this episode](/en/blog/hmd-016-risk-coverage-preregistration/).

## Why does "I don't know" matter?

Picture a staged scene: you ask "When was this author's third book translated?" and the author only ever wrote two. The answer arrives without hesitation, complete with a year, a translator and a publisher. The problem is not only that it is wrong. A made-up answer arrives in the same confident tone as a right one, and tone gives you no way to tell them apart.

A model that says "I don't know" or "that premise is wrong" at that moment answers less often, but its answers are worth more. The episode's question is which models find that line in the right place.

## What are the two halves of "at the right time"?

Two numbers that only make sense together:

- **Coverage:** the share of questions the model answered.
- **Risk:** of the answers it gave, the share that were wrong.

Optimising either alone is easy. A model that always says "I don't know" is never wrong; a model that always answers is never silent. The real question is a trade: would you rather have an assistant that answers everything and is wrong a third of the time, or one that answers half the questions and is almost never wrong?

The tension is old. In 2010 El-Yaniv and Wiener, writing about classifiers allowed to reject inputs, named it the "risk-coverage (RC) trade-off" ([JMLR 2010](https://www.jmlr.org/papers/v11/el-yaniv10a.html)).

## Can today's models do it?

One recent study says not yet. In June 2025, researchers at FAIR (Meta) released AbstentionBench: 20 datasets of questions with unknown answers, missing information, false premises, subjective framing or outdated facts, run against 20 frontier models ([arXiv 2506.09038](https://arxiv.org/abs/2506.09038)). The abstract's summary is that abstention is still an unsolved problem and that scaling models up has helped little.

A second finding is more surprising. According to the abstract, reasoning fine-tuning made abstention worse by 24% on average. The paper does not make clear whether that is a relative change or percentage points, and it applies to that study only. The authors also report that a carefully written system prompt helps somewhat but does not fix the underlying difficulty of reasoning about uncertainty.

## What does the scoring rule do?

To read coverage and risk as one number, we reuse the rule from [episode HMD-010](/en/blog/hmd-010-negative-marking-ai/): right +1, "I don't know" 0, wrong −3. Under this rule, answering only pays on average when you are more than 75% sure; that is the silence line k/(k+1).

Two points are often missed. First, the score is not a percentage. It is the average points per question and runs from −3 to +1. Second, an assistant that always stays silent scores exactly 0. That makes 0 the baseline: a model below 0 did worse than saying nothing at all. Technical errors and invalid outputs also count −3, so no failure quietly drops out of the table.

## How do you stop the result from being steered?

The judge in this test is Homodyne itself, and the channel benefits from an exciting winner. The main risk is not open cheating. It is the small choices that look reasonable after seeing the data: which condition counts as primary, how to treat technical errors, which two models to compare. Each one can nudge the result.

The standard fix is preregistration. Nosek and colleagues define it as committing to analysis steps "without advance knowledge of the research outcomes" ([PNAS 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/)). For Bluff, these are written before the run: the primary condition (penalty 3), the primary metric (points per question), exactly **one** confirmatory comparison, a practical-difference threshold, and a cap on made-up answers. Any other comparison is exploratory.

Next comes the data lock. A SHA-256 fingerprint of the answer-and-label file is computed and published: a 64-character string that changes completely if the file changes at all. In this episode's teaching file the hash starts `a39e3469`. Change a single label in one of 1,050 rows from "wrong" to "correct" and the new hash starts `2ce360be`. A hash proves the file did not change after it was locked. It does not prove the labels were judged correctly.

## What does the method show on made-up data?

For practice, the whole method was run on an **ILLUSTRATIVE** file: three fictional models (A, B and C), 350 questions each, including 50 that deliberately have no answer. No real model was called.

| Fictional model (ILLUSTRATIVE) | Coverage | Risk | Points per question |
|---|---|---|---|
| Model-A | 96% | 34% | −0.331 |
| Model-B | 67% | 17% | +0.203 |
| Model-C | 52% | 7% | +0.383 |

<svg viewBox="0 0 640 320" width="100%" role="img" aria-labelledby="hmd016-en-chart-title" font-size="13" fill="currentColor">
<title id="hmd016-en-chart-title">ILLUSTRATIVE: coverage against risk for three fictional models, output of abstain_report.py --demo</title>
<g stroke="currentColor" stroke-opacity="0.2"><line x1="70" y1="260" x2="600" y2="260"/><line x1="70" y1="30" x2="70" y2="260"/><line x1="70" y1="116.25" x2="600" y2="116.25" stroke-dasharray="4 4" stroke-opacity="0.6"/></g>
<text x="596" y="110" font-size="11" text-anchor="end">risk 25%: score 0 at k = 3</text>
<g fill="#E8A33D"><circle cx="578.8" cy="64.5" r="7"/><circle cx="425.1" cy="162.25" r="7"/><circle cx="345.6" cy="219.75" r="7"/></g>
<g font-weight="bold"><text x="566" y="50" text-anchor="end">Model-A −0.331</text><text x="413" y="150" text-anchor="end">Model-B +0.203</text><text x="333" y="208" text-anchor="end">Model-C +0.383</text></g>
<g font-size="11" text-anchor="middle" fill-opacity="0.7"><text x="70" y="278">0%</text><text x="335" y="278">50%</text><text x="600" y="278">100%</text><text x="335" y="300">coverage (answered / completed)</text></g>
<g font-size="11" text-anchor="end" fill-opacity="0.7"><text x="62" y="264">0%</text><text x="62" y="149">20%</text><text x="62" y="34">40%</text></g>
<text x="20" y="145" font-size="11" fill-opacity="0.7" transform="rotate(-90 20 145)" text-anchor="middle">risk</text>
<text x="70" y="18" font-size="11" fill-opacity="0.7">ILLUSTRATIVE · fictional models · no model was called</text>
</svg>

Model A answers almost everything, but a third of its answers are wrong and it ends below zero. With a penalty of 3, the quietest model leads. Under this rule any model with risk above 25% scores below zero whatever its coverage (the dashed line; our calculation). If mistakes cost you less, a different rule fits, and the order may change.

The confirmatory comparison in the teaching plan was B against A. Question by question, B's score minus A's averaged +0.534, with a 95% interval from +0.330 to +0.738. Zero is outside the interval, and the whole interval sits above the practical threshold written in advance (+0.10). [Miller](https://arxiv.org/abs/2411.00640) recommends exactly this paired analysis when models answer the same questions.

B against C, which was not preregistered, came out at −0.180 with an interval from −0.343 to −0.020. It is tempting to say C is better. We do not. Six models give fifteen possible pairs, and if there were no real differences and the tests were independent, the chance that at least one interval wrongly excludes zero would be about 54%. That comparison is a lead, not a finding.

On the 50 unanswerable questions, the cap set in advance is 5% made-up answers: a design choice, not a safety standard. Model A invented an answer for 37 of 50: BREACH. Model C invented none, yet its verdict is UNKNOWN, because with 50 questions the Wilson interval reaches about 7%. Zero errors in a small sample is not yet proof of safety.

## How should the real result be read?

After the data lock, the same table and the same confirmatory comparison will run on real answers, with model names and versions, run dates and the published hash. Each possible outcome has a meaning fixed in advance:

1. **Interval above zero and above the practical threshold:** in this test, with this penalty, one of the two models said "I don't know" at better moments. It is not an overall ranking for every task.
2. **Interval covers zero:** the test found no clear difference. That does not mean "equal"; it means the data could not separate them.
3. **A validity problem:** if judging, data or technical errors are compromised, no verdict is given, and that decision is logged next to the same hash.

If no model ends above zero, that is a finding too: with a penalty of 3, silence beat all of them. How to publish a checkable result is the subject of [episode HMD-018](/en/episodes/hmd-018/).

## What this does not show

- No Bluff result exists yet. The data has not been run or locked, and no number in this post belongs to a real model.
- Model-A, Model-B and Model-C are fictional and their numbers are ILLUSTRATIVE; they show the mechanism only.
- The real result will also apply only to those short questions, those model versions and that date.
- We measure output, not what a model internally "knows". More silence is not necessarily more understanding.
- A hash proves a file did not change, not that it was judged correctly. Failing to detect a difference is not evidence of equality.
- AbstentionBench findings apply to that study; we quote no ranking from it.

*Persian original: [کدام AI به‌موقع می‌گوید «نمی‌دانم»؟ روش آزمون ما](/fa/blog/hmd-016-ai-says-i-dont-know/)*
