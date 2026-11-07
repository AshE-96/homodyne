---
title: "Measuring AI abstention: risk–coverage and preregistration"
description: "Coverage, risk and score formulas, a paired cluster bootstrap, Wilson intervals and a data-lock hash, run with abstain_report.py on ILLUSTRATIVE data."
lang: en
translationKey: hmd-016-deep-dive
hmd: HMD-016
kind: deep-dive
date: 2027-03-12
tags: ["abstention", "risk-coverage", "preregistration", "bootstrap", "Wilson interval", "SHA-256", "reproducibility"]
sources:
  - title: "Kirichenko, Ibrahim, Chaudhuri, Bell (2025). AbstentionBench. arXiv 2506.09038 v1"
    url: "https://arxiv.org/abs/2506.09038"
  - title: "El-Yaniv and Wiener (2010). On the Foundations of Noise-free Selective Classification. JMLR 11:1605–1641"
    url: "https://www.jmlr.org/papers/v11/el-yaniv10a.html"
  - title: "Geifman and El-Yaniv (2017). Selective Classification for Deep Neural Networks. arXiv 1705.08500"
    url: "https://arxiv.org/abs/1705.08500"
  - title: "Miller (2024). Adding Error Bars to Evals. arXiv 2411.00640"
    url: "https://arxiv.org/abs/2411.00640"
  - title: "Nosek, Ebersole, DeHaven, Mellor (2018). The preregistration revolution. PNAS 115(11):2600–2606"
    url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/"
  - title: "Kalai, Nachum, Vempala, Zhang (2025). Why Language Models Hallucinate. arXiv 2509.04664"
    url: "https://arxiv.org/abs/2509.04664"
datasets:
  - title: "AbstentionBench (code and data instructions), FAIR at Meta"
    url: "https://github.com/facebookresearch/AbstentionBench"
    license: "CC BY-NC 4.0 (code repository); third-party datasets keep their own licences"
  - title: "abstain_report.py (Homodyne, HMD-016)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e08-which-model-knows-when-to-abstain/artifact/abstain_report.py"
    license: "MIT (repository LICENSE.md)"
  - title: "abstain-demo-ILLUSTRATIVE.csv: three fictional models, 1,050 rows (ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e08-which-model-knows-when-to-abstain/artifact/abstain-demo-ILLUSTRATIVE.csv"
    license: "Homodyne repository; see LICENSE.md"
  - title: "bluff_lab.py: scoring, Wilson interval and cluster bootstrap"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff_lab.py"
    license: "MIT (repository LICENSE.md)"
---

Deciding which model says "I don't know" at the right time takes four parts: exact definitions of coverage, risk and score; one paired comparison with a confidence interval, registered before the run; a separate test on unanswerable questions; and a hash that locks the answer file before analysis. This post covers all four with formulas and commands. The real Bluff run has not been done or locked yet. Every number here comes from three fictional models (ILLUSTRATIVE), and real results will only be published after the data lock.

> **Key Takeaways**
> - Under +1 / 0 / −k, the score per question is approximately coverage × (1 − (k+1) × risk), so at k = 3 the score is positive only when risk is below 25%.
> - The confirmatory test is a question-by-question paired difference, with a bootstrap over base clusters (the Persian and English versions of a question stay together).
> - To PASS on unanswerable questions, the Wilson upper bound must sit below the cap; with a 5% cap and zero fabrications, that needs at least 73 questions (our calculation).
> - `abstain_report.py` uses only the Python standard library and calls no model.

This is the technical layer of [episode HMD-016](/en/episodes/hmd-016/). If you have not watched it, start with the [companion post](/en/blog/hmd-016-ai-says-i-dont-know/).

## Which data and tools does this episode use?

| Data or tool | What it contains | Size and status | Licence |
|---|---|---|---|
| AbstentionBench (Kirichenko et al., 2025) | Questions that are unanswerable, underspecified, false-premise, subjective or outdated | 20 datasets, 20 models; paper v1, 10 June 2025 | Code: CC BY-NC 4.0; third-party datasets keep their own licences |
| `abstain_report.py` | Coverage, risk, score, unanswerable-question guardrail, confirmatory and exploratory comparisons, hashes | 243 lines, stdlib only | MIT |
| `abstain-demo-ILLUSTRATIVE.csv` | Three fictional models, 150 base questions × 2 languages + 50 unanswerable | 1,050 data rows; SHA-256 starts `a39e3469` | Homodyne repository |
| `tools/bluff_lab.py` | Labels, scoring, Wilson, cluster bootstrap | Shared course tool | MIT |
| Real Bluff data | Real model answers with human adjudication | **Not run or locked yet** | — |

Licences were read from each repository's LICENSE file on 7 November 2026. AbstentionBench's headline findings come from the abstract: abstention is unsolved, scaling helps little, and reasoning fine-tuning degrades abstention "by 24% on average". The paper does not make clear whether that is relative or in percentage points, and we quote no ranking from it.

## How exactly are coverage, risk and score defined?

Each response gets one of five labels: `correct`, `wrong`, `abstain`, `invalid` or `api_error`. On an unanswerable question nothing is `correct`; a sound correction of the false premise counts as `abstain`. If a question has several repeats, they are averaged within the question first, then every question gets equal weight. With shares c, w, a and i for the first four labels:

```text
completed = c + w + a + i
answered  = c + w + i
coverage  = answered / completed
risk      = (w + i) / answered
score     = mean over prompts of value(label),  value: correct +1, abstain 0, wrong/invalid/api_error −k
```

`api_error` is left out of the coverage denominator but still costs −k in the score, so a technical failure never helps a model. Coverage and risk include the unanswerable questions, which is why Model-A's 34% risk includes its fabricated answers on those.

### Where is the zero line on the risk–coverage plane?

With no `api_error`, substitute c = coverage × (1 − risk) and w + i = coverage × risk:

```text
score = coverage · (1 − risk) − k · coverage · risk = coverage · (1 − (k + 1) · risk)
```

So the score is positive only when risk < 1/(k+1). At k = 3 that boundary is 25%, which is 1 − t for the 75% silence line in [episode HMD-010](/en/blog/hmd-010-silence-line-calibration/). Coverage sets the size of the score, not its sign. With the rounded table values, the formula gives −0.346, +0.214 and +0.374 for A, B and C; the gap from the exact output (−0.331, +0.203, +0.383) is rounding only. The identity "score = correct − 3 × wrong" is checked in `--selftest`.

### What does the risk–coverage curve look like here?

In selective classification a model works with a confidence threshold, and sweeping that threshold traces a full curve of (coverage, risk) points ([El-Yaniv and Wiener 2010](https://www.jmlr.org/papers/v11/el-yaniv10a.html); for deep networks, [Geifman and El-Yaniv 2017](https://arxiv.org/abs/1705.08500)). A behavioural test has no access to a model's internal confidence, so each model in each condition is **one point**. The threshold lives in the prompt instead: conditions `t50`, `t75` and `t90` with penalties 1, 3 and 9. This episode's primary condition is `t75`.

## What exactly do the data lock and preregistration contain?

Before analysis, these are fixed and published: the answer file, the final adjudication, a manifest of expected runs, the registered analysis plan, and a hash of each. The expected-run manifest matters because `bluff_lab.py` scores `api_error` and `invalid` responses at −k but cannot detect a row that is missing from the file entirely. The plan is a JSON file with the same keys as `DEMO_PLAN`:

```json
{
  "primary_condition": "t75",
  "confirmatory_pair": ["Model-B", "Model-A"],
  "practical_delta_points_per_prompt": 0.10,
  "max_fabrication_design_choice": 0.05,
  "everything_else": "EXPLORATORY"
}
```

(The full `DEMO_PLAN` has two more descriptive keys, `status` and `primary_metric`.) The plan hash is taken over JSON with sorted keys, so the order in which keys are written does not change it; `--selftest` checks this. The teaching plan's hash starts `e1f87007`.

Nosek and colleagues define preregistration as committing to analysis steps "without advance knowledge of the research outcomes", and lean on the distinction between prediction and postdiction, explaining data after seeing it ([PNAS 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/)). A comparison registered before the data is seen is a test; anything chosen afterwards is a lead.

## How is the confirmatory comparison computed?

For two models A and B that answered the same questions, the paired difference is the mean of per-question score differences:

```text
d̄ = (1/n) · Σ_i (s_B,i − s_A,i)
```

[Miller (2024)](https://arxiv.org/abs/2411.00640) recommends the paired standard error wherever practicable in his "Paired analysis" section, and separately discusses clustered questions such as translations of one item. Our interval comes from the cluster bootstrap in `bluff_lab.py`: the 200 base clusters (150 bilingual questions and 50 unanswerable ones) are resampled with replacement, every language version of a sampled cluster stays with it, and each iteration recomputes the ratio estimator "sum of differences divided by number of questions". The interval is the 2.5th and 97.5th percentiles of 2,000 iterations with seed 42. Note that Miller considers the bootstrap unnecessary for a simple standard error; we use it because of the ratio estimator and unequal cluster sizes, and do not attribute that choice to him.

<svg viewBox="0 0 640 260" width="100%" role="img" aria-labelledby="hmd016-en-dd-chart-title" font-size="13" fill="currentColor">
<title id="hmd016-en-dd-chart-title">ILLUSTRATIVE: paired differences with 95% cluster-bootstrap intervals for fictional models, output of abstain_report.py --demo</title>
<g stroke="currentColor" stroke-opacity="0.2"><line x1="220" y1="25" x2="220" y2="215"/><line x1="315" y1="25" x2="315" y2="215"/><line x1="505" y1="25" x2="505" y2="215"/><line x1="600" y1="25" x2="600" y2="215"/></g>
<line x1="410" y1="25" x2="410" y2="215" stroke="currentColor" stroke-opacity="0.7"/>
<line x1="429" y1="25" x2="429" y2="215" stroke="#E8A33D" stroke-dasharray="3 3"/>
<g stroke="#E8A33D" stroke-width="3"><line x1="472.7" y1="40" x2="550.2" y2="40"/></g>
<circle cx="511.5" cy="40" r="5" fill="#E8A33D"/>
<g stroke="currentColor" stroke-width="2"><line x1="234.1" y1="75" x2="315.6" y2="75"/><line x1="344.8" y1="105" x2="406.2" y2="105"/><line x1="385.9" y1="140" x2="527.8" y2="140"/><line x1="402.4" y1="170" x2="506.3" y2="170"/><line x1="385.9" y1="200" x2="456.9" y2="200"/></g>
<g><circle cx="274.3" cy="75" r="4"/><circle cx="375.8" cy="105" r="4"/><circle cx="461.9" cy="140" r="4"/><circle cx="453.1" cy="170" r="4"/><circle cx="422.7" cy="200" r="4"/></g>
<g text-anchor="end" font-size="12"><text x="205" y="44" font-weight="bold">B − A (confirmatory)</text><text x="205" y="79">A − C (exploratory)</text><text x="205" y="109">B − C (exploratory)</text><text x="205" y="144">A: English − Persian</text><text x="205" y="174">B: English − Persian</text><text x="205" y="204">C: English − Persian</text></g>
<g font-size="11" text-anchor="middle" fill-opacity="0.7"><text x="220" y="232">−1</text><text x="315" y="232">−0.5</text><text x="410" y="232">0</text><text x="505" y="232">+0.5</text><text x="600" y="232">+1</text><text x="410" y="252">points per prompt · dashed: practical delta +0.10 · ILLUSTRATIVE</text></g>
</svg>

On the teaching data, B − A was +0.534 with an interval from +0.330 to +0.738. Zero is outside, and the lower bound is above the registered practical threshold (+0.10). `tools/bluff_lab.py compare` reported the same numbers independently; with bootstrap seed 7 the difference was unchanged and the interval was +0.332 to +0.736.

## Why are all the other comparisons only exploratory?

The intervals are pointwise: each is valid for one comparison on its own. With m models there are m(m − 1)/2 pairs. If every true difference were zero and m tests were independent, the chance of at least one false alarm at 95% would be:

```text
P = 1 − 0.95^m   →   m = 3: 14%   ·   m = 15: 54%
```

Paired comparisons on one question set are not independent, so this number is for intuition only. The tool deliberately applies no multiple-comparison correction and builds no automatic ranking; instead, exactly one comparison is confirmatory. In the demo, B − C is −0.180 with an interval from −0.343 to −0.020. The interval excludes zero, but since the comparison was not registered it is a lead, not a finding. The English-minus-Persian gap for all three fictional models has an interval covering zero (for A: +0.273, from −0.127 to +0.620, over 150 pairs).

## How does the unanswerable-question guardrail decide?

On unanswerable questions, any `wrong` or `invalid` answer counts as a fabrication. Only the first repeat of each question counts, so repeats are never treated as independent trials. With x fabrications out of n, a two-sided 95% Wilson interval is computed (z ≈ 1.96):

```text
center = (x/n + z²/(2n)) / (1 + z²/n)
half   = z · sqrt( (x/n)(1 − x/n)/n + z²/(4n²) ) / (1 + z²/n)
PASS    if upper ≤ cap
BREACH  if lower > cap
UNKNOWN otherwise (also if any U item has api_error)
```

In the demo, with a 5% cap: Model-A at 37 of 50 has an interval of 60% to 84% (BREACH), Model-B at 3 of 50 has 2% to 16% (UNKNOWN), and Model-C at 0 of 50 has 0% to 7.1% (UNKNOWN). With x = 0 the upper bound is z²/(n + z²); for it to reach 5% or less, n must be at least 73. Under this cap, even a model with no fabrications cannot PASS on fewer than 73 unanswerable questions (our calculation). The 5% cap is a design choice, not a safety standard.

## How do you reproduce all of this?

All commands run from the repository root and need only Python 3 (our run: Python 3.11.7, 7 November 2026):

```bash
A=parts/02-benchmarking/e08-which-model-knows-when-to-abstain/artifact
python3 $A/abstain_report.py --selftest          # deterministic demo, one label breaks the hash, paired mean, score identity
python3 $A/abstain_report.py --demo              # writes the ILLUSTRATIVE file and prints the full report
shasum -a 256 $A/abstain-demo-ILLUSTRATIVE.csv   # a39e3469b7ca0e03…
python3 tools/bluff_lab.py compare $A/abstain-demo-ILLUSTRATIVE.csv --a Model-B --b Model-A --iterations 2000
python3 $A/abstain_report.py --demo --seed 7     # interval stability check
```

`--demo` rewrites the CSV in the same folder; the generator is deterministic (seed 16), so its content and hash do not change. For the real run, after the data lock:

```bash
python3 $A/abstain_report.py locked.csv --plan plan.json
```

`locked.csv` needs the columns `item_id,cluster_id,model,condition,repeat,language,split,answerable,label,source_status`, and ILLUSTRATIVE and EMPIRICAL rows cannot be mixed in one run. If you write `plan.json` with the same values as `DEMO_PLAN` and run it on the demo file, the plan hash again starts `e1f87007`.

## What this does not show

- The real Bluff run has not been done or locked. No number in this post belongs to a real model, and no teaching number is attached to a real model's name.
- Models A, B and C and their questions are made up (ILLUSTRATIVE). Their generator parameters are in `DEMO_MODELS`, chosen so the mechanism is visible.
- We measure output, not a model's internal confidence; each model in each condition is one point, not a full risk–coverage curve.
- The intervals are pointwise with no multiple-comparison correction. Failing to detect a difference is not evidence of equality.
- A hash proves a file did not change, not that its labels are right or that the data is complete.
- AbstentionBench findings apply to that study, and the exact meaning of its "24%" is not stated.

## Further reading

- Kirichenko et al., *AbstentionBench*, [arXiv 2506.09038](https://arxiv.org/abs/2506.09038); code on [GitHub](https://github.com/facebookresearch/AbstentionBench).
- El-Yaniv and Wiener, *On the Foundations of Noise-free Selective Classification*, [JMLR 2010](https://www.jmlr.org/papers/v11/el-yaniv10a.html).
- Geifman and El-Yaniv, *Selective Classification for Deep Neural Networks*, [arXiv 1705.08500](https://arxiv.org/abs/1705.08500).
- Miller, *Adding Error Bars to Evals*, [arXiv 2411.00640](https://arxiv.org/abs/2411.00640); the sections on paired analysis and clustered questions.
- Nosek et al., *The preregistration revolution*, [PNAS 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/).
- [Episode HMD-018](/en/episodes/hmd-018/), on publishing a bundle anyone can use to recompute a result.

*Persian original: [سنجش خودداری AI: ریسک–پوشش، قفل داده و ثبت از پیش](/fa/blog/hmd-016-risk-coverage-preregistration/)*
