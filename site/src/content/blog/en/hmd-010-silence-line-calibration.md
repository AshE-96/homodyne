---
title: "Negative marking and AI calibration: math and test plan"
description: "Deriving the silence line k/(k+1), calibration and ECE, the Kalai et al. bound, and how to run the four-condition test with bluff_lab.py (not run yet)."
lang: en
translationKey: hmd-010-deep-dive
hmd: HMD-010
kind: deep-dive
date: 2027-01-22
tags: ["calibration", "negative marking", "ECE", "benchmarks", "AI hallucination", "abstention"]
sources:
  - title: "Kalai, Nachum, Vempala, Zhang (2025). Why Language Models Hallucinate. arXiv 2509.04664 v1"
    url: "https://arxiv.org/abs/2509.04664"
  - title: "OpenAI (2025). Why language models hallucinate"
    url: "https://openai.com/index/why-language-models-hallucinate/"
  - title: "Adding Error Bars to Evals. arXiv 2411.00640"
    url: "https://arxiv.org/abs/2411.00640"
  - title: "AA-Omniscience. arXiv 2511.13029"
    url: "https://arxiv.org/abs/2511.13029"
  - title: "Guo, Pleiss, Sun, Weinberger (2017). On Calibration of Modern Neural Networks. arXiv 1706.04599"
    url: "https://arxiv.org/abs/1706.04599"
  - title: "Zoomit: calculating Konkur test percentages and negative marking (October 2026, secondary source, Persian)"
    url: "https://www.zoomit.ir/websites/469821-calculate-test-percentage-negative-score/"
datasets:
  - title: "penalty_threshold.py: silence line, Konkur arithmetic, simulated answerers (ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e05-how-do-you-penalise-a-bluff/artifact/penalty_threshold.py"
    license: "MIT (repository LICENSE.md)"
  - title: "bluff_lab.py: Bluff teaching lab for scoring labelled answers"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff_lab.py"
    license: "MIT (repository LICENSE.md)"
  - title: "bluff-demo.csv: 20 made-up labelled rows (ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff-demo.csv"
    license: "MIT (repository LICENSE.md)"
  - title: "README-bluff-lab.md: labels, CSV columns and scoring rules for bluff_lab.py"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/README-bluff-lab.md"
    license: "MIT (repository LICENSE.md)"
---

To know whether negative marking makes a language model more careful, you need three things: the maths of the silence line t = k/(k+1), a way to check whether the model's confidence matches reality (calibration), and a fresh run that gives the model the same questions under four different prompts. The first two are covered in full here. The third, the four-condition run on a real model, has not been done yet; this post sets out its protocol, the exact commands, and what each possible outcome would mean.

> **Key Takeaways**
> - The silence line comes from a one-line inequality, and Kalai et al.'s proposed penalty of t/(1 − t) is the same line.
> - Calibration means "80% sure" is right about 80% of the time; reliability diagrams and ECE are the usual ways to measure it.
> - A simple check: if a model answers only above t and is calibrated, the share of wrong answers among its answers must stay below 1 − t.
> - `tools/bluff_lab.py` computes score, coverage and risk from a hand-labelled CSV. It calls no model and has no automatic judge.
> - The `plain`, `t50`, `t75` and `t90` run on a real model has not happened, and no numbers from it exist.

This is the technical layer of [episode HMD-010](/en/episodes/hmd-010/). If you have not watched it, start with the [companion post](/en/blog/hmd-010-negative-marking-ai/).

## How exactly is the silence line derived?

From one inequality. Write the scoring rule as: correct +1, "I don't know" 0, wrong −k. If the probability that an answer is right is p, the expected value of answering is:

```text
E[answer] = p·1 − (1 − p)·k = p(1 + k) − k
```

Answering beats silence when this is above zero:

```text
p(1 + k) − k > 0   ⇔   p > k / (k + 1) = t
```

Kalai et al. write the same thing from the other side. Their proposed instruction says to answer only if more than t confident, because mistakes cost t/(1 − t). Solve k = t/(1 − t) for t: k(1 − t) = t, so t = k/(k+1). The two forms are identical.

For the Konkur, Iran's national university entrance exam, the commonly reported rule is +3 for a right answer and −1 for a wrong one ([Zoomit](https://www.zoomit.ir/websites/469821-calculate-test-percentage-negative-score/), a secondary source in Persian). Divide by 3 to measure in units of one correct answer: k = 1/3 and t = 1/4. Three familiar cases:

| Situation | p | Expected value (units of one correct answer) |
|---|---|---|
| Blind guess, 4 options | 1/4 | 1/4 − (3/4)(1/3) = 0 |
| One option ruled out, 3 left | 1/3 | 1/3 − (2/3)(1/3) = 1/9 |
| Two ruled out, 2 left | 1/2 | 1/2 − (1/2)(1/3) = 1/3 |

The same inequality has a side result that matters later. If someone answers only when p > t, and their p is real, every answer they give has less than a 1 − t chance of being wrong. So the average "risk", the share of wrong answers among the answers given, must also stay below 1 − t. This condition is necessary, not sufficient, but it is cheap and testable.

### What is wrong in the paper's example?

Section 4.2 of version 1 of the paper (arXiv 2509.04664 v1, 4 September 2025) gives three examples: t = 0.5 with penalty 1, t = 0.9 with penalty 9, and "t = 0.75 (penalty 2)". The paper's own formula gives 0.75/0.25 = 3 for t = 0.75. As of 7 November 2026, v1 was the only version on arXiv. The episode's script prints this note in its first section of output.

## What does the Kalai et al. paper actually prove?

Its central claim is that generation errors can be tied to a simpler problem: deciding whether a given output is valid. The authors call this binary problem "Is-It-Valid" (IIV). The main bound, in its simplified form (Corollary 1), is:

```text
err ≥ 2·err_iiv − |V|/|E| − δ
```

In plain terms: err is the model's generation error rate and err_iiv is the misclassification rate on the valid-or-not problem. V is the set of valid outputs and E the set of plausible errors; when possible errors vastly outnumber correct answers, |V|/|E| is small. δ is a calibration term that the paper defines precisely. The message: if telling right from wrong is hard for some class of facts, the generation error rate on that class is at least roughly twice the classification error rate, minus these correction terms.

Another part of the paper asks why such errors survive post-training, and points to the binary grading used by most benchmarks, which rewards guessing. The proposal is to put explicit confidence targets in the prompt. The paper also discusses "behavioral calibration"; our reading is that a model should answer only when its confidence exceeds t. Our four-condition test measures exactly that. All quotes here come from the arXiv version.

## What is calibration, and how is it measured?

An answerer is calibrated if, among all the answers it gives with "80% confidence", about 80% are right. Calibration is about honest confidence, not the amount of knowledge: an answerer that knows little, and knows it, can be perfectly calibrated.

### Reliability diagrams

Sort answers into bins by stated confidence, say 0 to 10%, 10 to 20%, and so on up to 100%. For each bin compute two numbers: the mean stated confidence and the actual accuracy. If the points sit on the diagonal, the answerer is calibrated. Points below the diagonal mean overconfidence: it says 80 but is right less often. The overconfident answerer in our simulation, which always adds 0.25 to its confidence, would trace a curve parallel to and below the diagonal (except near its 0.99 cap).

### Expected calibration error (ECE)

ECE compresses that diagram into one number: the gap between accuracy and confidence in each bin, weighted by how many answers fall in the bin.

```text
ECE = Σ_b (n_b / N) · |acc_b − conf_b|
```

n_b is the number of answers in bin b, N the total, acc_b the accuracy and conf_b the mean confidence in that bin. An ECE of zero means perfect calibration under that binning. Guo et al. (2017) popularised the measure in deep learning ([arXiv 1706.04599](https://arxiv.org/abs/1706.04599)).

Three cautions. First, ECE depends on the binning; different bin counts give different values. Second, a low ECE means confidences are honest on average, not that the model separates right from wrong answers well. Third, for the silence-line rule, calibration across the whole range is not what matters; what changes the decision is honesty around t. A model can have a good overall ECE and still be overconfident right around 75%.

### Where does a language model's confidence come from?

Common routes, each with its own assumptions: ask the model to state a number; use token probabilities if the API exposes them; or ask the same question several times and measure agreement. The four-condition test deliberately depends on none of these and measures behaviour only: does the model abstain when told t, and does its risk stay below 1 − t?

## What does penalty_threshold.py simulate?

The script uses only the Python standard library and calls no model (**ILLUSTRATIVE**). It creates 1,000 made-up questions. Each question's probability of being answered correctly is drawn from a Beta(1.6, 1.2) distribution and clipped to between 0.01 and 0.99. The calibrated answerer's confidence equals that probability; the overconfident answerer adds 0.25, capped at 0.99. Both answer only when their confidence exceeds t.

Results at k = 3, seed 5 (run 2 November 2026):

| Answerer (ILLUSTRATIVE) | Points per question | Coverage | Risk |
|---|---|---|---|
| Calibrated | 0.130 | 29% | 14% |
| Overconfident | −0.054 | 59% | 27% |
| Calibrated, always answers | −0.792 | 100% | not reported |

The score is in points per question, ranging from −k to +1, not a percentage. With seed 11 the direction held: 0.125, −0.012 and −0.764. The calibrated answerer's 14% risk is below the 25% (1 − t) bound, and the overconfident answerer's 27% crosses it.

Section 4 of the script's output shows the gap between rescoring and changing behaviour. The "answers frozen" column is the calibrated answerer always answering and simply being scored under the new rule; "answers filtered by t" is the same answerer acting on the rule. At k = 3 these are the −0.792 and 0.130 above. Only a change in behaviour buys the gap between them.

## How do you run the four-condition test with bluff_lab.py?

`tools/bluff_lab.py` is a small teaching lab, separate from the older m2bench pipeline. It calls no API and has no automatic judge: its input is a CSV of answers labelled by people. The four conditions have fixed penalties: `plain` at k = 3 (rescored for comparison only), `t50` at k = 1, `t75` at k = 3, and `t90` at k = 9. Scores are points per prompt, between −k and 1.

Try the tool on the sample data first. All commands run from the repository root:

```bash
python3 parts/02-benchmarking/e05-how-do-you-penalise-a-bluff/artifact/penalty_threshold.py            # seed 5, the numbers above
python3 parts/02-benchmarking/e05-how-do-you-penalise-a-bluff/artifact/penalty_threshold.py --seed 11  # stability check
python3 tools/bluff_lab.py demo
python3 tools/bluff_lab.py score tools/bluff-demo.csv --condition t75
python3 tools/bluff_lab.py compare tools/bluff-demo.csv --a A --b B --condition t75
python3 -m unittest discover -s tools -p 'test_bluff_lab.py'
```

`bluff-demo.csv` has 20 made-up rows: two imaginary models, A and B, ten questions, condition `t75` only. So `--condition plain` on it fails with "No rows match selection". The `demo` command scores two imaginary models at k = 0, 1, 3 and 9 (A with 60 correct, 30 wrong, 10 abstentions; B with 50 correct, 5 wrong, 45 abstentions), so you can watch their order change with k.

For a real run, these steps follow the lab's [README](https://github.com/AshE-96/homodyne/blob/main/tools/README-bluff-lab.md) and the channel's draft scoring guide (31 October 2026, not yet in the public repository):

1. **Fix the question set.** Answerable questions plus unanswerable ones with a false premise (the U items). Persian and English versions of one question share a `cluster_id`.
2. **Write and lock four prompts:** `plain`, `t50`, `t75` and `t90`, each over the same questions.
3. **Collect fresh answers**, by hand or with an external runner. Log the exact model version, full prompt, raw response, time and errors.
4. **Label** each answer `correct`, `wrong`, `abstain`, `invalid` or `api_error`. A hedged but concrete wrong answer is still `wrong`. On U items nothing is `correct`; a sound correction of the false premise is `abstain`. Settle edge cases on a separate pilot set before the main run, and keep reviewers blind to model identity where possible.
5. **Build the CSV** with columns `item_id,cluster_id,model,condition,repeat,language,split,answerable,label,source_status,response`. Marking rows `EMPIRICAL` is a declaration, not proof of provenance.
6. **Score each condition separately:**

```bash
python3 tools/bluff_lab.py score my-runs.csv --condition plain
python3 tools/bluff_lab.py score my-runs.csv --condition t50
python3 tools/bluff_lab.py score my-runs.csv --condition t75
python3 tools/bluff_lab.py score my-runs.csv --condition t90 --max-fabrication 0.05
```

The JSON output gives, per model, `score_points_per_prompt`, `coverage_among_completed`, `risk_among_answered`, and the shares of correct, wrong and abstain over all prompts. The 0.05 in `--max-fabrication` is an example design choice, not a safety standard: the tool computes a two-sided 95% Wilson interval on the U items and reports PASS only if the upper bound does not exceed the threshold, BREACH if the lower bound exceeds it, and UNKNOWN otherwise.

Know two limits of the tool. `compare` contrasts two **models** within one condition using a paired cluster bootstrap; it does not contrast two **conditions** for one model. A paired t75-versus-plain comparison for a single model is currently outside the tool and needs the same logic (per-question score differences, resampling whole clusters) written separately. [Adding Error Bars to Evals](https://arxiv.org/abs/2411.00640) is the background for that paired design. The `plan` command is only a normal-approximation sample-size scenario, not a validated power analysis for the full design.

## How do you tell the three outcomes apart?

"More careful" is defined before seeing data: the error rate falls without correct answers falling by the same amount. Using the shares that `score` reports, compare each t condition against `plain`:

| Outcome | Wrong, over all prompts | Correct, over all prompts | Abstain | Meaning |
|---|---|---|---|---|
| A | Falls | Roughly unchanged | Rises | The rule was heard; real caution |
| B | No change beyond the uncertainty | Unchanged | Unchanged | The score can change, the behaviour did not with this prompt |
| C | Falls | Falls as much or more | Rises | Saying less, not caution |

There is a second check: compare risk in each condition with 1 − t. If a model answers under `t75` and its risk is above 25%, either it did not apply the rule or its confidence around 75% is not honest. Behaviour alone cannot separate those two, but both answer "no" to the episode's question.

## What this does not show

- The four-condition run on a real model has not been done. No number in this post is attributed to any commercial model.
- The answerers in `penalty_threshold.py` and models A and B in `bluff-demo.csv` are made up (ILLUSTRATIVE).
- The Kalai et al. bound is a lower bound, not a prediction of any specific model's error rate. Our description of its terms is simplified; see the paper for exact definitions.
- A low ECE does not show that a model separates right from wrong well, and a high ECE does not prove the silence-line rule will fail.
- The Konkur rule comes from consistent secondary sources; the official exam booklet was not read directly.

## Further reading

- Kalai, Nachum, Vempala and Zhang, *Why Language Models Hallucinate*, [arXiv 2509.04664](https://arxiv.org/abs/2509.04664); section 4.2 for the confidence-target instruction.
- Guo et al., *On Calibration of Modern Neural Networks*, [arXiv 1706.04599](https://arxiv.org/abs/1706.04599); for reliability diagrams and ECE.
- *Adding Error Bars to Evals*, [arXiv 2411.00640](https://arxiv.org/abs/2411.00640); for paired designs and uncertainty.
- *AA-Omniscience*, [arXiv 2511.13029](https://arxiv.org/abs/2511.13029); an example of a benchmark that penalises wrong answers.
- [Episode HMD-002](/en/episodes/hmd-002/), on how rescoring alone can change a winner.

*Persian original: [نمرهٔ منفی و کالیبراسیون AI: ریاضی و طرح آزمایش](/fa/blog/hmd-010-silence-line-calibration/)*
