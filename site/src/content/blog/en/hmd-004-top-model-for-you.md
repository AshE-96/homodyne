---
title: "Is the top model on the leaderboard the best one for you?"
description: "Not necessarily. A rank answers only the question its leaderboard measures. Start from the error you cannot afford, and check whether the test has expired."
lang: en
translationKey: hmd-004-companion
hmd: HMD-004
kind: companion
date: 2026-12-11
tags: ["benchmarks", "LMArena", "style control", "SWE-bench", "model selection", "LLM evaluation"]
sources:
  - title: "LMSYS · Does style matter? Disentangling style and substance in Chatbot Arena (29 Aug 2024)"
    url: "https://lmsys.org/blog/2024-08-28-style-control/"
  - title: "OpenAI · Why we no longer evaluate SWE-bench Verified (23 Feb 2026)"
    url: "https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/"
  - title: "OpenAI · Separating signal from noise in coding evaluations (8 Jul 2026)"
    url: "https://openai.com/index/separating-signal-from-noise-coding-evaluations/"
  - title: "SimpleQA Verified · arXiv 2509.07968"
    url: "https://arxiv.org/abs/2509.07968"
---

Not necessarily. A leaderboard rank answers only the question its builders measured. In an August 2024 analysis by the LMSYS team, separating out the effect of answer style (length and markdown formatting) moved GPT-4o-mini from rank 6 to rank 11. The top model is the best one for you only if that leaderboard measures the error that is expensive for you, and only if its test is still valid.

> **Key Takeaways**
> - Vote-based leaderboards such as LMArena measure which answer people preferred. Preferred is not the same as correct.
> - A model has a profile, not a rank. Your task should set the weight of each column, not the leaderboard's builder.
> - The right test falls out of a chain: decision, costly failure, required evidence, and only then a benchmark family.
> - Benchmarks expire. OpenAI stopped reporting SWE-bench Verified in February 2026, then retracted its recommendation of the successor in July 2026.

This post accompanies the [HMD-004 episode](/en/episodes/hmd-004/). For the statistics behind style control, the benchmark family map and a selection checklist, read the [deep dive on choosing an eval](/en/blog/hmd-004-choosing-an-eval/).

## What does a vote-based leaderboard actually count?

It counts which answer looked better to people. In Chatbot Arena, now called LMArena, a user types a question, sees two anonymous answers and votes for the one they like more. Ranks are built from those votes.

In August 2024 the LMSYS team asked how much answer style moves those votes, in ["Does style matter?"](https://lmsys.org/blog/2024-08-28-style-control/). Their main finding: "length was the dominant style factor", with markdown formatting a second-order effect. When those effects were controlled for, in that analysis GPT-4o-mini fell from rank 6 to 11 and Claude 3 Opus rose from 16 to 10.

The authors add a caution of their own: their analysis is "still observational". Longer answers are sometimes genuinely better, and controlling for style can strip out some real quality. The lesson is not that vote-based leaderboards are worthless. They measure something real but narrow: what people prefer in open conversation. They do not directly test whether an answer to a specific question is correct, whether a document summary is faithful, or whether a booking gets changed properly.

## Why does a model have a profile rather than a rank?

Because different tasks need different skills, and a single rank adds them up with weights you did not choose. Think of a school report card: a final grade hides the separate marks for maths, biology and literature, and you open the card when you choose what to study next.

Models work the same way. In the episode's teaching example (**ILLUSTRATIVE**, hypothetical models X and Y), X leads on general knowledge, Y invents less when answering from a document, and on tool use they swap places again. Squash all of that into one number and the winner depends on how much each column weighs, a weighting usually chosen by whoever built the table.

## How do you find a test that answers your question?

Do not start from a famous name. Start from the error you cannot afford. The chain has four links:

1. **Decision:** which model should sit behind a shop's question-answering assistant?
2. **Costly failure:** stating the refund policy wrongly, and confidently.
3. **Required evidence:** a test that checks answers against a reference and sees whether the model abstains when unsure.
4. **Family:** factuality plus calibration and abstention, and a Persian slice if your users write in Persian.

The useful half of this chain is the exclusions. For this assistant a vote-based leaderboard does not help, because length and style move votes. Agent and tool-use benchmarks do not help either: they measure finishing actions in an environment, and this assistant only answers. A high reasoning score says nothing about abstaining at the right moment.

### Even a selection tool is sensitive to your wording

Homodyne put this chain into a small, transparent tool. When we described the need as a "customer support bot for my online shop" whose failure "tells customers the wrong refund policy", the tool suggested agent, safety and robustness benchmarks: the wrong advice for a bot that only answers. We rewrote the same need as a "question answering assistant" with the failure "a confident wrong answer about refunds". This time it suggested calibration and abstention, factuality and multilingual testing, and explicitly excluded vote-based preference, reasoning and agent benchmarks.

The tool deliberately matches words and does not decide for you. The lesson is that the quality of your evidence starts with how carefully you write down the decision and the failure.

## Is the test you picked still valid?

Finding the right family is not enough; you also need to know whether the test is still alive. SWE-bench Verified is a clear example. It was a reference coding benchmark whose score appeared in many model launches. On 23 February 2026 OpenAI [announced](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) that it would no longer report it. It audited 138 problems its model consistently failed, and at least 59.4% of them had flawed tests that rejected correct solutions. It also reported signs of contamination, meaning signs that the answers had been in models' training data.

A caution: those 138 problems were not a random sample of the benchmark. They were the ones the model was stuck on. So 59.4% is not the failure rate of SWE-bench Verified as a whole.

The proposed fix was a successor, SWE-bench Pro. On 8 July 2026, in ["Separating signal from noise in coding evaluations"](https://openai.com/index/separating-signal-from-noise-coding-evaluations/), the same company retracted its earlier recommendation to adopt Pro. Its own estimate was that about 30% of Pro's tasks were broken too. Renaming the test does not fix validity; the successor needs an audit as well.

Homodyne keeps a dated lifecycle state for each well-known benchmark: fresh, discriminating, saturating, saturated, compromised and retired. "Saturated" means good models can no longer be told apart; "compromised" means the test itself is flawed or leaked. One does not imply the other, and the states do not have to come in that order.

SimpleQA went down a similar path. After label noise was found, a revised set, [SimpleQA Verified](https://arxiv.org/abs/2509.07968), was built with 1,000 prompts.

## What this does not show

- **It does not say vote-based leaderboards are useless.** They measure real human preference; preference is just not correctness.
- **It does not say which model is best today.** The Arena numbers come from the August 2024 analysis, not today's ranks.
- **The family map is not an official taxonomy.** It is Homodyne's working map, and many benchmarks sit between two families.
- **Lifecycle states are dated claims.** They may change next month; re-check before citing.
- **The selection tool does not decide.** It matches words against worked examples.

## The four-box card: before you trust a leaderboard

Draw four boxes and fill them in:

| Box | Ask | Shop assistant example |
|---|---|---|
| Task | What exactly will the model do? | Answer customers' questions about orders and returns |
| Costly failure | Which mistake can you not afford? | A wrong refund policy, stated confidently |
| Evidence | What observation would catch it? | Correctness against a reference answer, plus abstaining when unsure |
| Test | Which family produces that evidence? | Factuality + calibration/abstention (+ a Persian slice) |

If you cannot fill the Evidence box, you are not ready to pick a model.

This episode follows [HMD-002](/en/episodes/hmd-002/), which showed that with the same answers a scoring rule can change the winner. The Persian version of this post is [here](/fa/blog/hmd-004-top-model-for-you/).
