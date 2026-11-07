---
title: "Statistical power, paired tests and clusters in AI evals"
description: "The MDE formula for a paired test, the design effect for clustered questions, exact McNemar, many comparisons, and how to rerun HMD-012 with power_lab.py."
lang: en
translationKey: hmd-012-deep-dive
hmd: HMD-012
kind: deep-dive
date: 2027-02-12
tags: ["statistical power", "minimum detectable effect", "design effect", "clustered standard errors", "McNemar test", "preregistration", "benchmarks"]
sources:
  - title: "Miller (2024). Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations. arXiv 2411.00640 v1"
    url: "https://arxiv.org/abs/2411.00640"
  - title: "Anthropic (19 November 2024). A statistical approach to model evaluations"
    url: "https://www.anthropic.com/research/statistical-approach-to-model-evals"
  - title: "Card et al. (2020). With Little Power Comes Great Responsibility. EMNLP 2020, arXiv 2010.06595"
    url: "https://arxiv.org/abs/2010.06595"
  - title: "McNemar (1947). Psychometrika 12(2):153–157"
    url: "https://doi.org/10.1007/BF02295996"
  - title: "Bowman & Dahl (2021). What Will it Take to Fix Benchmarking in Natural Language Understanding? NAACL 2021, arXiv 2104.02145"
    url: "https://arxiv.org/abs/2104.02145"
  - title: "Cameron & Miller (2015). A Practitioner's Guide to Cluster-Robust Inference. Journal of Human Resources 50(2):317–372"
    url: "https://escholarship.org/uc/item/1jq5d0pq"
  - title: "Nosek et al. (2018). The preregistration revolution. PNAS 115(11):2600–2606"
    url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500"
datasets:
  - title: "power_lab.py: power, MDE, exact McNemar, repeats, clusters and many comparisons (Python standard library; ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/power_lab.py"
    license: "MIT (repository LICENSE.md)"
  - title: "power_lab-output.txt: output of the seed-12 run, 7 November 2026"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/power_lab-output.txt"
    license: "CC BY-NC-SA 4.0 (repository LICENSE.md)"
  - title: "fair-run-card.md: fair-run card and preregistration sheet (blank template)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/fair-run-card.md"
    license: "CC BY-NC-SA 4.0 (repository LICENSE.md)"
  - title: "bluff_lab.py: the plan command for the Bluff sample-size scenario"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff_lab.py"
    license: "MIT (repository LICENSE.md)"
  - title: "DROP (Dua et al., NAACL 2019; in Miller's table 4, not used by us)"
    url: "https://huggingface.co/datasets/ucinlp/drop"
    license: "CC BY-SA 4.0"
---

To know whether a benchmark can detect the difference between two models, you need three calculations: the minimum detectable effect (MDE) for a paired comparison, the design effect when questions come in clusters, and a correction for many comparisons. This post works through all three with formulas, rebuilds the numbers from Miller (2024) and Card et al. (2020) with `power_lab.py`, and shows how to regenerate every figure from the repository root. No model was called.

> **Key Takeaways**
> - For a paired comparison at two-sided 5% and 80% power: MDE = (1.96 + 0.84) · SD(d) / √n. With disagreement rate r, SD(d) = √(r − Δ²).
> - For clusters of m questions with intra-cluster correlation ρ, the design effect is 1 + (m − 1)ρ, and the effective n is n divided by it.
> - Miller's formula with ω² = 1/9 and a 3-point gap gives 969 questions; `power_lab.py` reproduces it.
> - In simulation (ILLUSTRATIVE, seed 12), a naive count on 50 questions × 20 repeats declared a winner 52.8% of the time with no real difference; the clustered test, 5.3%.
> - The `bluff_lab.py plan` scenario for Bluff is a normal approximation, not a validated power analysis. Bluff has not been run.

This is the technical layer of [episode HMD-012](/en/episodes/hmd-012/). If you have not watched it, start with the [companion post](/en/blog/hmd-012-thousand-tests-trust/).

## What exactly does a paired comparison measure?

The difference between two models' scores on each question. If each question scores right (1) or wrong (0), the paired difference for question i takes three values:

```text
d_i = +1   A right, B wrong     (probability p10)
d_i = −1   A wrong, B right     (probability p01)
d_i =  0   both right or both wrong
```

The disagreement rate is r = p10 + p01 and the true gap is Δ = p10 − p01. So p10 = (r + Δ)/2, p01 = (r − Δ)/2, and the standard deviation of the difference is:

```text
SD(d) = √(r − Δ²)
```

With no true gap, SD(d) is exactly √r; for small gaps it is close. The key point is that SD depends on how often the models disagree, not on either model's accuracy. Two models that agree on 90% of questions produce a low-variance difference.

Miller says the same in variance terms: ω² = Var(x_A) + Var(x_B) − 2Cov(x_A, x_B). The more correlated the two models' scores, the larger the covariance term and the smaller the variance of the difference. He calls this a "free" reduction in variance ([arXiv 2411.00640](https://arxiv.org/abs/2411.00640), section 4.2).

## What is the MDE formula for a paired test?

With n independent questions, the standard error of the mean difference is SD(d)/√n. For a two-sided test at level α with power 1 − β:

```text
MDE = (z_{1−α/2} + z_{1−β}) · SD(d) / √n
n   = ((z_{1−α/2} + z_{1−β}) · SD(d) / Δ)²
```

At α = 0.05 and 80% power the z values sum to 1.96 + 0.84 = 2.80. Miller does this calculation in section 5 with ω² = 1/9 and δ = 0.03:

```text
n = (z_0.025 + z_0.20)² · (1/9) / 0.03² ≈ 969
```

and suggests new evals should contain at least 1,000 questions. `power_lab.py` reproduces the 969. Section 2 of its output gives the full MDE table for four disagreement rates (**ILLUSTRATIVE**, accuracy points):

| Independent questions | Disagree 5% | Disagree 10% | Disagree 20% | Disagree 30% |
|---|---|---|---|---|
| 100 | 6.3 | 8.9 | 12.5 | 15.3 |
| 500 | 2.8 | 4.0 | 5.6 | 6.9 |
| 1,000 | 2.0 | 2.8 | 4.0 | 4.9 |
| 4,000 | 1.0 | 1.4 | 2.0 | 2.4 |

### Paired versus unpaired

Comparing only two overall accuracies gives a difference variance of pA(1 − pA) + pB(1 − pB) and throws away the correlation between models. In section 3 of the output, with 500 questions, A at 72%, B at 70% and 10% disagreement, the unpaired MDE is 8.0 points and the paired MDE is 4.0.

### Repeating each question

When a model's answers are random, you can ask each question K times. Miller's equation 10:

```text
MDE = (z_{α/2} + z_β) · √((ω² + σ²_A/K_A + σ²_B/K_B) / n)
```

With n = 198, ω² = 1/9 and σ²_A = σ²_B = 1/6, the paper reports that going from K = 1 to K = 10 lowers the MDE from 13.2% to 7.5%. Our run gives 13.3% and 7.6% (the gap comes from rounding the z values), plus 10.5% at K = 2 and 6.7% at K = 100. As K goes to infinity the σ²/K terms vanish and only ω² remains: a floor of 6.6%. Repeats reduce noise within a question; only new questions reduce variation between questions.

## McNemar's test and rebuilding Card et al.

McNemar's test ([McNemar, 1947](https://doi.org/10.1007/BF02295996)) counts only discordant pairs. If m questions are discordant and b of them favour A, then under the null hypothesis b follows Bin(m, 0.5). `power_lab.py` implements the exact version.

In appendix C of their paper, Card et al. describe a scenario: 500 questions, Δ = 0.02, 90% agreement (6% only the new model right, 4% the reverse). Their result: power "approximately 0.25" and a Type-M exaggeration factor of 1.9; with 2,000 questions, "nearly 80%" and 1.1 ([arXiv 2010.06595](https://arxiv.org/abs/2010.06595)). Section 1 of our output:

| Questions | Analytic power | Simulated power (exact McNemar) | Exaggeration when "significant" |
|---|---|---|---|
| 500 | 29% | 24% | ×1.9 |
| 2,000 | 81% | 78% | ×1.1 |

The gap between analytic and simulated power at 500 questions is expected: the exact test is discrete and more conservative than the normal approximation. The Type-M factor is the average ratio of the observed gap to the true gap, among significant runs only. An underpowered test "succeeds" only when noise happens to favour the gap, so the gaps it reports are inflated.

## What is the design effect for clustered questions?

When questions come in clusters of m with intra-cluster correlation ρ (the ICC), the variance of the mean grows by the design effect:

```text
DEFF  = 1 + (m − 1) · ρ
n_eff = n / DEFF
```

The practical way to compute the standard error is Miller's equation 8: sum the differences within each cluster first, then compute the variance across clusters:

```text
SE_clustered = (1/n) · √( Σ_c Σ_i Σ_j (d_{i,c} − d̄)(d_{j,c} − d̄) )
```

In table 4 of the same paper, on real DROP data with Anthropic models, the clustered standard error is 1.34 against a naive 0.44, a ratio of 3.05. For RACE-H the ratio is 1.10 and for MGSM 1.88, so the size of the effect varies from benchmark to benchmark.

Section 4 of `power_lab.py` builds the same 1,000 rows in three shapes with ρ = 0.5 (assumed). The "no real difference" columns are the rate of declared winners over 2,000 simulations; the correct value is about 5%.

| Shape | DEFF | Effective n | Clustered MDE | "Winner", naive | "Winner", clustered | Power for a 3-point gap |
|---|---|---|---|---|---|---|
| 1000 × 1 | 1.00 | 1000 | 2.8 | 4.7% | 4.7% | 86.2% |
| 250 × 4 | 2.50 | 400 | 4.4 | 23.1% | 5.5% | 50.6% |
| 50 × 20 | 10.50 | 95 | 9.1 | 52.8% | 5.3% | 17.5% |

With seed 11 the pattern held: naive 5.3%, 21.5% and 54.8%; clustered power 84.0%, 47.1% and 17.5%.

<figure>
<svg viewBox="0 0 640 290" role="img" aria-labelledby="hmd012en-title hmd012en-desc" style="max-width:100%;height:auto;direction:ltr" font-family="system-ui, sans-serif" font-size="12" fill="currentColor">
<title id="hmd012en-title">Rate of false winners when there is no real difference, for three shapes of 1,000 rows; naive count versus clustered test; ILLUSTRATIVE, seed 12</title>
<desc id="hmd012en-desc">Naive count: 4.7%, 23.1% and 52.8%. Clustered test: 4.7%, 5.5% and 5.3%. The dashed line marks the 5% level.</desc>
<text x="70" y="22" opacity="0.7">ILLUSTRATIVE · power_lab.py · seed 12 · ICC 0.5 assumed · 2000 runs per bar</text>
<g stroke="currentColor" stroke-opacity="0.15"><line x1="70" y1="40" x2="620" y2="40"/><line x1="70" y1="106.7" x2="620" y2="106.7"/><line x1="70" y1="173.3" x2="620" y2="173.3"/><line x1="70" y1="240" x2="620" y2="240" stroke-opacity="0.6"/></g>
<line x1="70" y1="223.3" x2="620" y2="223.3" stroke="currentColor" stroke-opacity="0.6" stroke-dasharray="4 3"/>
<g font-size="11" text-anchor="end" opacity="0.7"><text x="62" y="44">60%</text><text x="62" y="110.7">40%</text><text x="62" y="177.3">20%</text><text x="62" y="227.3">5%</text></g>
<g fill="#E8A33D"><rect x="130" y="224.3" width="50" height="15.7"/><rect x="310" y="163" width="50" height="77"/><rect x="490" y="64" width="50" height="176"/></g>
<g fill="currentColor" fill-opacity="0.45"><rect x="185" y="224.3" width="50" height="15.7"/><rect x="365" y="221.7" width="50" height="18.3"/><rect x="545" y="222.3" width="50" height="17.7"/></g>
<g text-anchor="middle" font-weight="bold"><text x="155" y="218">4.7</text><text x="210" y="218">4.7</text><text x="335" y="157">23.1</text><text x="390" y="215">5.5</text><text x="515" y="58">52.8</text><text x="570" y="216">5.3</text></g>
<g text-anchor="middle"><text x="182" y="260">1000 × 1</text><text x="362" y="260">250 × 4</text><text x="542" y="260">50 × 20</text></g>
<g font-size="11"><rect x="300" y="272" width="12" height="10" fill="#E8A33D"/><text x="317" y="281">naive count</text><rect x="420" y="272" width="12" height="10" fill="currentColor" fill-opacity="0.45"/><text x="437" y="281">clustered test</text></g>
</svg>
<figcaption>Share of simulations that declared a "winner" when the two models had no real difference. ILLUSTRATIVE; data from section 4 of power_lab-output.txt (seed 12).</figcaption>
</figure>

One caution: with 50 clusters a z-test is slightly liberal, and a t-test or cluster bootstrap is safer. Cameron and Miller (2015) explain in their standard guide that default standard errors on clustered data overstate precision, and that with few clusters the cluster correction itself needs adjusting.

## How do you control many comparisons?

With m independent tests at level α and no real difference anywhere, the chance of at least one false "significant" result is:

```text
FWER = 1 − (1 − α)^m
```

Six models give m = 15 pairs and FWER = 53.7%. The pairs share models, so they are not independent; the figure is an order of magnitude, not an exact value. Two common remedies: choose one or a few primary comparisons before the run and report the rest as exploratory, or adjust the level, for example by dividing α by m (Bonferroni) or with Holm's step-down procedure. Either must be written down before seeing the data. Nosek et al. (PNAS, 2018) set out the reasoning: keep decisions made before the data apart from explanations made after it.

Bowman and Dahl (NAACL 2021) also list adequate statistical power as one of four criteria for a good natural language understanding benchmark, noting that for a 1% improvement "a few thousand examples" would suffice under typical conditions ([arXiv 2104.02145](https://arxiv.org/abs/2104.02145), section 3.3).

## How many questions does Bluff need?

We do not know yet. The current design of Bluff, the channel's own benchmark, has 650 prompts, but the Persian and English versions of one base question share a `cluster_id`, so there are at most 450 independent clusters. Each prompt is also scored between −3 and +1 under the k = 3 penalty from [episode HMD-010](/en/episodes/hmd-010/), so the accuracy formula above does not apply directly. `bluff_lab.py plan` produces a scenario (run 7 November 2026):

| SD of cluster differences | Clusters | MDE (points per prompt) | Clusters needed for Δ = 0.10 |
|---|---|---|---|
| 1 | 450 | 0.132 | 785 |
| 2 | 450 | 0.264 | 3,140 |

The tool itself warns that this is a normal approximation, not a validated power analysis for the full unequal-weight clustered design. Only a pilot can estimate the real SD.

## How do you reproduce everything?

All commands run from the repository root and need only the Python standard library. The default run takes about ten seconds.

```bash
python3 parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/power_lab.py              # seed 12, the numbers in this post
python3 parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/power_lab.py --seed 11    # stability check
python3 parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/power_lab.py --icc 0.2    # a different intra-cluster correlation
python3 parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/artifact/power_lab.py --selftest   # 16 formula checks
python3 tools/bluff_lab.py plan --sd 1 --n 450 --delta 0.10
python3 tools/bluff_lab.py plan --sd 2 --n 450 --delta 0.10
```

The seed-12 output should match `artifact/power_lab-output.txt`; we reran it on 7 November 2026 and found no difference. `--selftest` checks the formulas against Miller (section 5) and Card (appendix C) and returns "16/16 checks pass".

For your own study, fill in `artifact/fair-run-card.md`: one run card per model and condition, and a preregistration sheet with ten fields (primary comparison, practical difference, questions and clusters, assumed spread and its source, MDE, test, secondary comparisons and their correction, failure policy, stopping rule, changes after registration). Date-stamp the file with a commit or a public timestamp before you look at the results.

## Limitations and what this does not show

- No model was called. The 10% disagreement rate and ρ = 0.5 are teaching assumptions; real values differ by benchmark.
- The MDE formulas are normal approximations. With small n or very low disagreement, simulation with an exact test (as in section 1) is more reliable.
- The cluster model in `power_lab.py` assumes equal-sized clusters with the same correlation. Real benchmarks have unequal clusters.
- The ratios in Miller's table 4 (DROP, RACE-H, MGSM) belong to that paper's data and do not generalise.
- "Significant" means probably real, not important. Define the practical difference separately, before the run.
- Bluff has not been run. The `plan` scenario does not replace a pilot.
- The GitHub links to this episode's `artifact/` files go live when the repository is published; until then the commands work on a local copy of the repository.

## Further reading

- Miller, *Adding Error Bars to Evals*, [arXiv 2411.00640](https://arxiv.org/abs/2411.00640); section 4 for paired comparisons, section 5 for power, appendix C for the clustered versions.
- Card et al., *With Little Power Comes Great Responsibility*, [arXiv 2010.06595](https://arxiv.org/abs/2010.06595); appendix C and the accompanying notebooks.
- Cameron and Miller, *A Practitioner's Guide to Cluster-Robust Inference*, [open copy](https://escholarship.org/uc/item/1jq5d0pq); section VI on few clusters.
- [Episode HMD-014](/en/episodes/hmd-014/): when a table with correct numbers still misleads.

*Persian original: [توان آماری، آزمون جفتی و خوشه‌ها در بنچمارک AI](/fa/blog/hmd-012-power-paired-clusters/)*
