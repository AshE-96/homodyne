---
title: "A correct table that misleads: Simpson, best-of-N, audits"
description: "Subset weights in Simpson's paradox, the penalty crossover, best-of-N inflation, holdouts, Wilson intervals and UNKNOWN, reproduced with mislead_lab.py."
lang: en
translationKey: hmd-014-deep-dive
hmd: HMD-014
kind: deep-dive
date: 2027-02-26
tags: ["Simpson's paradox", "selective reporting", "best-of-N", "holdout", "Wilson interval", "data contamination", "benchmarks"]
sources:
  - title: "Singh et al. (2025). The Leaderboard Illusion. arXiv 2504.20879 (v1 29 April 2025; v2 12 May 2025)"
    url: "https://arxiv.org/abs/2504.20879"
  - title: "BetaKit (2 May 2025). Cohere Labs head calls \"unreliable\" AI leaderboard rankings a \"crisis\" in the field (secondary source)"
    url: "https://betakit.com/cohere-labs-head-calls-unreliable-ai-leaderboard-rankings-a-crisis-in-the-field/"
  - title: "Bickel, Hammel, O'Connell (1975). Sex Bias in Graduate Admissions: Data from Berkeley. Science 187(4175):398–404"
    url: "https://www.science.org/doi/10.1126/science.187.4175.398"
  - title: "Wikipedia, Simpson's paradox (UC Berkeley gender bias section; secondary source)"
    url: "https://en.wikipedia.org/wiki/Simpson%27s_paradox"
  - title: "Zhang et al. (2024). A Careful Examination of Large Language Model Performance on Grade School Arithmetic. arXiv 2405.00332 v4"
    url: "https://arxiv.org/html/2405.00332v4"
  - title: "Reuel et al. (2024). BetterBench. NeurIPS 2024, arXiv 2411.12990"
    url: "https://arxiv.org/abs/2411.12990"
  - title: "Miller (2024). Adding Error Bars to Evals. arXiv 2411.00640"
    url: "https://arxiv.org/abs/2411.00640"
datasets:
  - title: "mislead_lab.py: a correct table with four headlines, penalty k, best-of-N, holdout and PASS/BREACH/UNKNOWN audit (Python standard library; ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py"
    license: "MIT (repository LICENSE.md)"
  - title: "bluff_lab.py: scoring and audit status for unanswerable questions"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff_lab.py"
    license: "MIT (repository LICENSE.md)"
  - title: "bluff-demo.csv: 20 made-up labelled rows (ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/tools/bluff-demo.csv"
    license: "MIT (repository LICENSE.md)"
  - title: "GSM8K (OpenAI): about 7.5K training and 1K test problems"
    url: "https://github.com/openai/grade-school-math"
    license: "MIT"
  - title: "GSM1k (Scale AI), Hugging Face copy: 1,205 test rows"
    url: "https://huggingface.co/datasets/ScaleAI/gsm1k"
    license: "Not stated on the dataset card (checked 7 November 2026)"
---

A table with correct numbers has three ways to mislead: unequal subset weights when results are pooled (Simpson's paradox), a choice of metric or penalty that decides the winner, and selective reporting of the best attempt. This post works through all three with formulas, shows where a holdout and an audit with Wilson intervals help and where they do not, and reproduces every number in the episode with `mislead_lab.py` (seed 7). No model was called.

> **Key Takeaways**
> - Overall accuracy is a weighted average of subset accuracies, and each system sets its own weights by choosing which questions to answer. With equal weights, A's lead returns.
> - The penalty crossover is k* = (C_A − C_B)/(W_A − W_B); in our table, 216/124 ≈ 1.74.
> - Of ten equally skilled versions (70%), the best averages 74.9%; with twenty, 76.0%. On a holdout the average falls back to about 70% (ILLUSTRATIVE).
> - With zero errors, the Wilson upper bound is z²/(n + z²); reaching 5% takes at least 73 checks.
> - Bluff has not been run, and no number in this post belongs to a real model.

This is the technical layer of [episode HMD-014](/en/episodes/hmd-014/). If you have not watched it, start with the [companion post](/en/blog/hmd-014-correct-table-misleads/).

## Where exactly does Simpson's paradox come from in a benchmark table?

From the weights. For the whole table, "accuracy on answered questions" is a weighted average of subset accuracies:

```text
acc_all = Σ_s w_s · acc_s        w_s = answered_s / answered_all
```

In the teaching table (section 1 of the output, **ILLUSTRATIVE**), A is 95.0% accurate on easy questions and 60.0% on hard ones; B is 94.1% and 55.0%. But the weight of hard questions is 390/990 (39%) for A and 60/650 (9%) for B. B put most of its weight on the group where everyone scores high, so its overall figure is 90.5% against A's 81.2%.

That is the condition for a reversal: one side is better in every group, but the other side's share of the easy group is large enough. The usual fix is standardisation: combine each group's accuracy with the **same** weights for both systems, for instance each group's share of all questions (600 and 400 of 1,000). Using the table's counts, our arithmetic gives A 0.6 × 570/600 + 0.4 × 234/390 = 81.0% and B 0.6 × 555/590 + 0.4 × 33/60 ≈ 78.4%. A's lead returns. This is not complete either: B's 55.0% on hard questions rests on only 60 answers, and we know nothing about the 340 it skipped. That is why an honest report puts coverage (the share of questions answered) next to accuracy for every subset.

### Berkeley, 1973

In autumn 1973, Berkeley's 12,763 graduate applicants included 8,442 men (about 44% admitted) and 4,321 women (about 35%) ([Wikipedia](https://en.wikipedia.org/wiki/Simpson%27s_paradox)). Bickel et al. (*Science*, 1975) showed that women had applied more often to more selective departments, and that the pooled data, weighted by department, showed "a small but statistically significant bias in favor of women". Four departments showed significant bias against women and six against men; Wikipedia notes that the main conclusion did not rest on those counts. We could not access the *Science* page, so these figures come from a secondary source.

## How do you calculate where a penalty flips the winner?

Under +1 for a right answer, 0 for "I don't know" and −k for a wrong one, a system's score over N questions is:

```text
S(k) = (C − k · W) / N
```

where C is the number of correct answers and W the number of wrong ones. The two lines S_A(k) and S_B(k) meet at:

```text
k* = (C_A − C_B) / (W_A − W_B) = (804 − 588) / (186 − 62) = 216 / 124 ≈ 1.74
```

A has more right answers and more wrong ones. Below k* the extra right answers are worth more; above it the extra wrong answers cost more. The reasoning behind choosing k is in the [HMD-010 deep dive](/en/blog/hmd-010-silence-line-calibration/). The point here is that anyone can compute k* from two numbers in a table and see how close the choice of penalty sits to the choice of winner.

<figure>
<svg viewBox="0 0 640 300" role="img" aria-labelledby="hmd014en-title hmd014en-desc" style="max-width:100%;height:auto;direction:ltr" font-family="system-ui, sans-serif" font-size="12" fill="currentColor">
<title id="hmd014en-title">Points per 100 questions for A and B as the penalty k grows; the winner flips at k = 1.74; ILLUSTRATIVE</title>
<desc id="hmd014en-desc">A: 80.4, 61.8, 43.2 and 24.6 for k from 0 to 3. B: 58.8, 52.6, 46.4 and 40.2. The lines cross at k = 1.74.</desc>
<text x="80" y="22" opacity="0.7">ILLUSTRATIVE · mislead_lab.py section 3 · points per 100 questions</text>
<g stroke="currentColor" stroke-opacity="0.15"><line x1="80" y1="63.3" x2="580" y2="63.3"/><line x1="80" y1="110" x2="580" y2="110"/><line x1="80" y1="156.7" x2="580" y2="156.7"/><line x1="80" y1="203.3" x2="580" y2="203.3"/><line x1="80" y1="250" x2="580" y2="250" stroke-opacity="0.6"/></g>
<g font-size="11" text-anchor="end" opacity="0.7"><text x="70" y="67.3">80</text><text x="70" y="114">60</text><text x="70" y="160.7">40</text><text x="70" y="207.3">20</text><text x="70" y="254">0</text></g>
<line x1="370" y1="40" x2="370" y2="250" stroke="currentColor" stroke-opacity="0.5" stroke-dasharray="4 3"/>
<text x="376" y="48" font-size="11">k = 1.74</text>
<polyline points="80,62.4 246.7,105.8 413.3,149.2 580,192.6" fill="none" stroke="#E8A33D" stroke-width="3"/>
<polyline points="80,112.8 246.7,127.3 413.3,141.7 580,156.2" fill="none" stroke="currentColor" stroke-width="2"/>
<g fill="#E8A33D"><circle cx="80" cy="62.4" r="4"/><circle cx="246.7" cy="105.8" r="4"/><circle cx="413.3" cy="149.2" r="4"/><circle cx="580" cy="192.6" r="4"/></g>
<g><circle cx="80" cy="112.8" r="3.5"/><circle cx="246.7" cy="127.3" r="3.5"/><circle cx="413.3" cy="141.7" r="3.5"/><circle cx="580" cy="156.2" r="3.5"/></g>
<g font-size="11" font-weight="bold"><text x="88" y="56" fill="#E8A33D">A 80.4</text><text x="88" y="132">B 58.8</text><text x="586" y="196" fill="#E8A33D">24.6</text><text x="586" y="160">40.2</text></g>
<g text-anchor="middle" font-size="11"><text x="80" y="270">k = 0</text><text x="246.7" y="270">1</text><text x="413.3" y="270">2</text><text x="580" y="270">3</text></g>
<text x="330" y="292" text-anchor="middle" font-size="11" opacity="0.7">penalty k per wrong answer</text>
</svg>
<figcaption>Points per 100 questions under +1 / 0 / −k; the amber line is A, the other B. ILLUSTRATIVE; data from section 3 of the mislead_lab.py output.</figcaption>
</figure>

## How much does selective disclosure inflate a score?

Each version's score on n questions is a noisy estimate of its true skill p, with standard deviation √(p(1 − p)/n). At p = 0.70 and n = 200 that is about 3.2 points. If N versions are tested and only the maximum is published, the published number is the maximum of N random variables, and its average rises with N and with each version's noise, even though no version's skill has changed.

Sections 4 and 5 of the output (**ILLUSTRATIVE**):

| Setting | Published in this run | Average best over 2,000 repeats | Holdout over 2,000 repeats |
|---|---|---|---|
| 10 versions, seed 7 | 74.5% | 74.9% | 69.9% |
| 10 versions, seed 11 | 78.5% | 74.9% | 70.0% |
| 20 versions, seed 7 | 74.5% | 76.0% | 70.0% |

A holdout works because fresh questions are not tied to how the version was chosen: the luck that made it the winner does not repeat on them. But a single holdout is itself a 200-question sample with the same noise. With seed 7 the chosen version scored 74.0% on the holdout, and 76.0% in the 20-version run; with seed 11 it went from 78.5% to 69.5%. The lesson is in the average, not in one run. It is the point of [episode HMD-012](/en/episodes/hmd-012/): every score, holdout scores included, carries a margin of error ([Miller, arXiv 2411.00640](https://arxiv.org/abs/2411.00640)).

### What did The Leaderboard Illusion measure?

The paper's abstract (v2) says undisclosed private testing let a few providers test several variants before release, and that their ability to "choose the best score" led to biased Arena scores. The authors identify 27 private variants tested by Meta in the lead-up to the Llama 4 release. The abstract also reports data asymmetry: Google and OpenAI received an estimated 19.2% and 20.4% of all Arena data, against 29.7% for 83 open-weight models combined, and even limited additional data can yield relative gains of up to 112% on the Arena distribution ([arXiv 2504.20879](https://arxiv.org/abs/2504.20879)). LMArena denied unfair treatment, listed what it called "factual errors" in the paper, and said its pre-release testing policy had been public ([BetaKit](https://betakit.com/cohere-labs-head-calls-unreliable-ai-leaderboard-rankings-a-crisis-in-the-field/)). We did not read LMArena's original post directly.

### Contamination and GSM1k

Version 4 of Zhang et al. (22 November 2024) says GSM1k consists of 1,205 problems, written by human annotators without using language models, and withheld to prevent contamination; the authors planned to release it when three open-source models from different pre-trained lineages reached 95% accuracy, or in June 2025, whichever came first. Findings: accuracy drops of up to 8%, systematic overfitting in families such as Phi and Mistral, and few signs of it in many frontier models ([arXiv 2405.00332v4](https://arxiv.org/html/2405.00332v4)). A copy with 1,205 test rows is now on Hugging Face as ScaleAI/gsm1k, but its dataset card is empty and states no licence. Earlier versions of the paper gave a different figure for the drop; we use only the v4 number.

## When can a small audit say "pass"?

When the upper bound of its confidence interval is below the limit. `mislead_lab.py` and `bluff_lab.py` both compute a two-sided 95% Wilson interval for x errors in n checks:

```text
p̂ = x/n
center = (p̂ + z²/2n) / (1 + z²/n)
half   = z · √(p̂(1 − p̂)/n + z²/4n²) / (1 + z²/n)
```

and return three states: PASS if the upper bound ≤ the limit, BREACH if the lower bound > the limit, UNKNOWN otherwise. With x = 0 the upper bound simplifies to z²/(n + z²). At a 5% limit (a design choice, not a standard), the smallest error-free n that earns PASS is 73. Section 6 of the output:

| Errors / checked | 95% interval | Status |
|---|---|---|
| 0 / 2 | 0.0% to 65.8% | UNKNOWN |
| 0 / 20 | 0.0% to 16.1% | UNKNOWN |
| 0 / 100 | 0.0% to 3.7% | PASS |
| 3 / 20 | 5.2% to 36.0% | BREACH |

On the sample data under condition t75, `bluff_lab.py score` reports for both made-up models `n_u_completed` 2, `fabrication_count` 0 and `ci95_wilson` [0.0, 0.6576]: UNKNOWN. The design deliberately stops a result without enough evidence from turning green.

## What does BetterBench say about benchmark quality?

Reuel et al. (NeurIPS 2024) built a framework of 46 best practices across a benchmark's life cycle and assessed 24 AI benchmarks against it. They found large quality differences, and that most benchmarks do not report the statistical significance of their results or make replication easy ([arXiv 2411.12990](https://arxiv.org/abs/2411.12990)). This is our only quantitative claim about the quality of real benchmarks.

## How do you reproduce everything?

From the repository root, with only the Python standard library (3.8 or later):

```bash
python3 parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py --selftest
python3 parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py               # seed 7, the numbers in this post
python3 parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py --seed 11     # stability check
python3 parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/artifact/mislead_lab.py --variants 20  # more private attempts
python3 tools/bluff_lab.py score tools/bluff-demo.csv --condition t75 --max-fabrication 0.05
```

`--selftest` should print `selftest: OK (reversal, metric flip, penalty flip, best-of-N inflation, Wilson, audit states)`. Other options: `--n-test` and `--n-holdout` (test and holdout sizes), `--true-acc` (true skill), `--reps` (number of repeats) and `--limit` (audit limit). We ran all of these commands on 7 November 2026, and the seed-7 output matched the episode's numbers. Seed 7 was chosen before the run and was not changed after seeing the holdout result.

## Limitations and what this does not show

- The A and B table was built by hand to produce the reversal. It shows the reversal is **possible**, not how common it is in real tables.
- Equal-weight standardisation restores A's lead but knows nothing about the questions B skipped. No weighting replaces full coverage.
- The best-of-N simulation assumes independent versions of identical skill. Real versions differ in skill and are correlated, so inflation can be smaller or larger.
- On Chatbot Arena we report only the paper's findings and LMArena's response, via a news report; we show neither cheating by anyone nor which side is right.
- The Wilson interval assumes independent checks. If unanswerable questions come in clusters, the real interval is wider. The 5% limit is a design choice.
- Bluff has not been run. The GitHub links to this episode's `artifact/` files go live when the repository is published.

## Further reading

- Singh et al., *The Leaderboard Illusion*, [arXiv 2504.20879](https://arxiv.org/abs/2504.20879).
- Zhang et al., *A Careful Examination of Large Language Model Performance on Grade School Arithmetic*, [arXiv 2405.00332](https://arxiv.org/abs/2405.00332).
- Reuel et al., *BetterBench*, [arXiv 2411.12990](https://arxiv.org/abs/2411.12990).
- The [HMD-012 deep dive](/en/blog/hmd-012-power-paired-clusters/) on statistical power and clustered errors.

*Persian original: [جدول درست و گمراه‌کننده: سیمپسون، best-of-N و ممیزی](/fa/blog/hmd-014-mislead-lab-methods/)*
