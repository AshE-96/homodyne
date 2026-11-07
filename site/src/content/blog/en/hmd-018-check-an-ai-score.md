---
title: "Where did this AI score come from? Check it yourself"
description: "A score is a result when a stranger can recompute it without its publisher: four files and a hash anchored outside the bundle. Plus a course recap."
lang: en
translationKey: hmd-018-companion
hmd: HMD-018
kind: companion
date: 2027-03-26
tags: ["reproducibility", "SHA-256", "correction log", "benchmarks", "benchmark course", "AI scores"]
sources:
  - title: "NeurIPS 2026 Paper Checklist Guidelines (read 7 November 2026)"
    url: "https://neurips.cc/public/guides/PaperChecklist"
  - title: "NeurIPS blog (4 May 2026). MLRC 2026: Reproducibility as an Official Track at NeurIPS"
    url: "https://blog.neurips.cc/2026/05/04/mlrc-2026-reproducibility-as-an-official-track-at-neurips/"
  - title: "Liang et al. (2022). Holistic Evaluation of Language Models (HELM). arXiv 2211.09110"
    url: "https://arxiv.org/abs/2211.09110"
  - title: "Mitchell et al. (2018). Model Cards for Model Reporting. arXiv 1810.03993"
    url: "https://arxiv.org/abs/1810.03993"
  - title: "Gebru et al. (2018). Datasheets for Datasets. arXiv 1803.09010"
    url: "https://arxiv.org/abs/1803.09010"
  - title: "OpenAI (23 February 2026). Why we no longer evaluate SWE-bench Verified"
    url: "https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/"
  - title: "AI Weekly: OpenAI drops SWE-Bench Verified after flaw audit (secondary source)"
    url: "https://aiweekly.co/alerts/openai-drops-swe-bench-verified-backs-pro-after-flaw-audit"
  - title: "OpenAI (July 2026). Separating signal from noise in coding evaluations"
    url: "https://openai.com/index/separating-signal-from-noise-coding-evaluations/"
  - title: "COPE Retraction Guidelines"
    url: "https://publicationethics.org/guidance/guideline/retraction-guidelines"
---

An AI model's score is a result when a stranger can recompute it without trusting whoever published it. That takes four files: the labelled answers, the method, the scoring code and a correction log, plus a list of the files' fingerprints whose own fingerprint is published outside the bundle, with a date. Without those, the number is still a claim, not a result.

> **Key Takeaways**
> - Recomputing means scoring the same answers with the same code, and it must give exactly the same number. Rerunning means asking the model again, and it may not.
> - A SHA-256 fingerprint reveals that a file changed, not that it is wrong.
> - In our demo (ILLUSTRATIVE), a fraud that rebuilds the whole bundle passes every internal check; only an "anchor" published outside the bundle catches it.
> - A public correction and a fraud can be the same edit. The difference is a public, dated record.

This post accompanies [episode HMD-018](/en/episodes/hmd-018/), the last episode of the benchmark course. The technical details of the manifest, the anchor and the reproduction commands are in the [deep dive for this episode](/en/blog/hmd-018-recompute-manifest-anchor/). At the end of this post the whole course is summed up in nine lines.

## Why isn't "they said so" enough?

A screenshot gets passed around: "This model ranked first on such-and-such test." Someone asks "How do you know?" and the only answer is "They said so." That is the same answer we have for a rumour, including for numbers Homodyne itself showed during this course.

The useful question is not whether the publisher is trustworthy. It is whether the number can be checked without trusting them.

## What does serious research do with this question?

It treats it as part of the result. NeurIPS, one of the largest machine-learning conferences, requires a checklist from every 2026 paper, and papers without one are desk rejected. One question asks whether the code, data and instructions needed to reproduce the main results are provided. Answering "no" is not in itself grounds for rejection, but the answer must be justified ([NeurIPS 2026 Paper Checklist](https://neurips.cc/public/guides/PaperChecklist)).

There is also a community effort, the Machine Learning Reproducibility Challenge (MLRC), which started at ICLR 2018 and has researchers re-test the results of published papers. According to the NeurIPS blog, at NeurIPS 2026 it became an official part of the conference for the first time in its history ([NeurIPS blog, 4 May 2026](https://blog.neurips.cc/2026/05/04/mlrc-2026-reproducibility-as-an-official-track-at-neurips/)).

## What is the difference between recomputing and rerunning?

You can add up a restaurant bill again on your phone; the same items at the same prices must give exactly the same total. Order the same dish tomorrow, though, and it may taste different because the cook has changed.

In a benchmark, the first is a **recompute**: score the stored, labelled answers again with the same code, and the number must match exactly. The second is a **rerun**: ask the model the questions again. The answers may differ, because models sample their outputs or because a version changed without notice. A difference on rerun is not necessarily cheating; a difference on recompute means something is wrong.

## Which files does a stranger need?

Four files, plus a fifth:

1. **Answers with their labels:** each row is one question, one model, and right, wrong or "I don't know".
2. **Method:** the scoring rule, the model version and the run date.
3. **The scoring code.**
4. **A correction log:** anything changed after publication, with a date and a reason.
5. **A manifest:** the fingerprint of each file next to its name.

None of this is new. Stanford's HELM evaluation project released all raw model prompts and completions for others to analyse ([arXiv 2211.09110](https://arxiv.org/abs/2211.09110)). Model cards ([Mitchell et al.](https://arxiv.org/abs/1810.03993)) and datasheets for datasets ([Gebru et al.](https://arxiv.org/abs/1803.09010)) were both proposed in 2018.

Not everything can be published: public test questions eventually leak into later models' training data, and some data is personal or cannot be redistributed. A middle path is to publish the fingerprint of held-out questions today and the questions later. Wherever something is withheld, say plainly what and why.

## How do fingerprints and an anchor stop a silent swap?

SHA-256 reads a whole file and returns a 64-character string. The same file always gives the same string, and changing one word changes the string completely. This episode's small program, `recompute_check.py`, checks three things: each file's fingerprint against the manifest, that the published version is the newest entry in the correction log, and the score itself, recomputed from the answers with the course's own scorer. No model is run again.

The test data is the course's teaching file: 10 questions, two fictional models A and B, a penalty of 3 per wrong answer (**ILLUSTRATIVE**; no model was called). Published scores: A at −0.100 and B at +0.100 points per question. Change just one of A's labels from "wrong" to "correct" and A rises to +0.300, overtaking B. It is the lesson of [episode HMD-008](/en/blog/hmd-008-wrong-answer-key/): one label can change the winner.

| Tampering (ILLUSTRATIVE) | Without anchor | With the release-day anchor |
|---|---|---|
| Change only that label | FAIL: the answer file's fingerprint does not match the manifest | FAIL |
| Change the label and rebuild the manifest | FAIL: A published −0.100, recomputed +0.300 | FAIL |
| Rewrite the label, the published score and the manifest | **PASS** | FAIL: the manifest does not match the anchor |

The third row matters most. A fraud that rebuilds the bundle completely and consistently passes every internal check, because those checks only ask "is this bundle consistent with itself?" and never "is this the bundle that was published on day one?"

The answer is an **anchor**: the fingerprint of the manifest itself, placed on release day somewhere outside the bundle, with a date, such as a public code repository's history or an archived copy. An anchor is only strong if the publisher cannot change it silently. A video description can be edited by its owner; a git history, or text that other people have quoted, is much harder to rewrite unnoticed.

## How is a public correction different from fraud?

Suppose the label really was wrong: a viewer reports that model A answered correctly and the answer key only accepted one spelling of a name. The right move is exactly the same edit, done in public. The version goes from v0.1 to v0.2; the correction log records which question, why, and the effect (A from −0.100 to +0.300, and the winner changes); and the new anchor is published **next to** the old one, not in its place. The checker passes with the new anchor.

Scientific publishing works the same way. COPE's retraction guidelines (the Committee on Publication Ethics) say the main purpose of a retraction is to correct the record, not to punish authors, and ask that the notice state the reason. A useful error report needs three things: the item ID, the evidence and a proposed fix.

A real case: on 23 February 2026, OpenAI announced it would no longer report scores on SWE-bench Verified, a 500-problem coding benchmark. According to published reports, of 138 of the hardest problems it audited, 59.4% had material issues in test design or the problem description ([AI Weekly](https://aiweekly.co/alerts/openai-drops-swe-bench-verified-backs-pro-after-flaw-audit)); that share applies to those 138 only, not to all 500. The second reason was training-data contamination. In July 2026 OpenAI also publicly withdrew its own recommendation for a replacement. Public correction is a normal part of science, including for the one doing the correcting.

## The whole benchmark course in nine lines

This is the last episode of Homodyne's benchmark course. One line per episode:

1. **E01:** "Better" means better under a scoring rule ([How can the same answers crown a different AI winner?](/en/blog/hmd-002-same-answers-new-winner/)).
2. **E02:** A model has a profile, not a rank ([Is the top model on the leaderboard the best one for you?](/en/blog/hmd-004-top-model-for-you/)).
3. **E03:** "Fewer errors" means nothing without its denominator ([AI error rates: what does "fewer mistakes" hide?](/en/blog/hmd-006-error-rate-denominator/)).
4. **E04:** A wrong answer key only takes points from whoever answered correctly ([If a benchmark's answer key is wrong, which AI loses?](/en/blog/hmd-008-wrong-answer-key/)).
5. **E05:** Negative marking only makes a model careful if its confidence is honest ([Can negative marking make an AI more careful?](/en/blog/hmd-010-negative-marking-ai/)).
6. **E06:** "Enough" is a relationship, not a magic number ([We tested an AI model 1,000 times. Can we trust it?](/en/blog/hmd-012-thousand-tests-trust/)).
7. **E07:** A correct table can still mislead through the evidence it selects ([Every number in this AI table is right. Why does it mislead?](/en/blog/hmd-014-correct-table-misleads/)).
8. **E08:** Saying "I don't know" at the right time means reading coverage and risk together, and locking the comparison rule before seeing the data ([Which AI says "I don't know" at the right time?](/en/blog/hmd-016-ai-says-i-dont-know/)).
9. **E09:** A result that leaves no way to refute it is not yet a result.

The course's last exercise: next time you see an AI score, ask just one question: "Where is the answer file?"

## What this does not show

- Checkability shows the arithmetic is right, not that the labels are. A recompute says the sums are correct, not the judging.
- It does not show that rerunning a model gives the same answers; we explained why reruns differ, but did not measure it.
- An anchor makes a silent swap hard, not impossible, and only if it sits somewhere the publisher does not control alone.
- The demo bundle is a teaching file: ten questions and two fictional models (ILLUSTRATIVE). No real Bluff result appears in this post.
- The SWE-bench Verified figures come from consistent secondary sources; OpenAI's page would not load for our tools. We quote no figures about SWE-bench Pro or model rankings.

*Persian original: [این نمرهٔ AI از کجا آمده؟ خودتان بررسی کنید](/fa/blog/hmd-018-check-an-ai-score/)*
