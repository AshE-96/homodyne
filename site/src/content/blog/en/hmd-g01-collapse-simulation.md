---
title: "Model collapse simulated: tails, drift and how to rerun it"
description: "Why tails die first in model collapse: log-width drift, Wright–Fisher drift, three data regimes, and exact commands to rerun Homodyne's toy simulation."
lang: en
translationKey: hmd-g01-deep-dive
hmd: HMD-G01
kind: deep-dive
date: 2027-01-29
tags: ["model collapse", "genetic drift", "Wright–Fisher", "synthetic data", "simulation", "reproducibility"]
sources:
  - title: "Shumailov et al. (2024). AI models collapse when trained on recursively generated data. Nature 631, 755–759"
    url: "https://www.nature.com/articles/s41586-024-07566-y"
  - title: "Same paper, PMC version"
    url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC11269175/"
  - title: "Shumailov et al. The Curse of Recursion (preprint, arXiv 2305.17493)"
    url: "https://arxiv.org/abs/2305.17493"
  - title: "Gerstgrasser et al. (2024). Is Model Collapse Inevitable? arXiv 2404.01413"
    url: "https://arxiv.org/abs/2404.01413"
  - title: "Villalobos et al., Epoch AI (2024). Will we run out of data?"
    url: "https://epoch.ai/blog/will-we-run-out-of-data-limits-of-llm-scaling-based-on-human-generated-data"
  - title: "Graphite (May 2026). AI Now Writes as Many Online Articles as Humans"
    url: "https://graphite.io/research/ai-now-writes-as-many-online-articles-as-humans-do"
  - title: "Graphite (October 2025). AI Content in Search and LLMs"
    url: "https://graphite.io/research/ai-content-in-search-and-llms"
  - title: "Graphite (2025). More Articles Are Now Created by AI Than Humans (earlier report, superseded)"
    url: "https://graphite.io/five-percent/more-articles-are-now-created-by-ai-than-humans"
datasets:
  - title: "collapse_lab.py: collapse simulator (Python standard library only)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/04-global/hmd-g01-model-collapse/artifact/collapse_lab.py"
    license: "Repository licence (LICENSE.md)"
  - title: "results-seed2026.json: full output of the 3 November 2026 run (ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/04-global/hmd-g01-model-collapse/artifact/results-seed2026.json"
    license: "Repository licence (LICENSE.md)"
  - title: "results-seed2026.md: tables from the same run"
    url: "https://github.com/AshE-96/homodyne/blob/main/parts/04-global/hmd-g01-model-collapse/artifact/results-seed2026.md"
    license: "Repository licence (LICENSE.md)"
  - title: "Common Crawl (basis of Graphite's estimate; not used directly)"
    url: "https://commoncrawl.org/"
    license: "Common Crawl Terms of Use"
  - title: "WikiText (wikitext2; used in the Nature paper, not by us)"
    url: "https://huggingface.co/datasets/Salesforce/wikitext"
    license: "See the dataset card"
---

In our toy simulation, collapse runs on two exact mechanisms. For the bell curve, the log of the fitted width shrinks by about 1/n per generation on average (n is the sample size per generation), so the median width after t generations is roughly e^(−t/n); and because tail mass falls exponentially with width, the tails die long before the curve does. For words, it is Wright–Fisher genetic drift, where zero is a state you never leave. Keeping or accumulating real data changes that maths, and the whole thing reproduces with one command in about 90 seconds.

> **Key Takeaways**
> - Every simulation number here comes from `results-seed2026.json` and is ILLUSTRATIVE: synthetic data, not web data, not a language model.
> - The simple prediction e^(−t/n) for median width, with n = 100, lands almost on the simulated values: 0.37 at generation 100.
> - In the word experiment, a word seen once vanishes in the next generation with probability about e^(−1), roughly a third.
> - keep10 behaves like migration in population genetics: a stable but narrower equilibrium. accumulate makes each generation's jolt smaller and smaller.
> - A full run overwrites the committed result files unless you redirect it; `--quick` gives slightly different numbers.

This is the technical layer of [episode HMD-G01](/en/episodes/hmd-g01/). If you have not watched it, start with the [companion post](/en/blog/hmd-g01-model-collapse/).

## What data do these results rest on?

Two kinds: synthetic data the script generates itself, and external data behind the episode's news figures.

| Data | What it is | Size | Licence | Updates |
|---|---|---|---|---|
| Synthetic Gaussian (experiment 1) | Draws from N(0, 1) | 100 points per generation, 200 runs, 1,000 generations | Repository licence | Fixed; reproducible by seed |
| Synthetic Zipf corpus (experiment 2) | 5,000 possible words, s = 1.0 | 20,000 tokens, 3,172 distinct words, 20 runs, 100 generations | Repository licence | Fixed; reproducible by seed |
| Common Crawl (via Graphite) | Public web archive | Graphite's sample: 55.4k URLs | Common Crawl Terms of Use | Periodic crawls; we did not use it directly |
| wikitext2 (Nature paper) | Text corpus the OPT-125m model was fine-tuned on | Not recorded in our sources | See the [dataset card](https://huggingface.co/datasets/Salesforce/wikitext) | We did not use it |

Two methodological notes on the web figures. First, Graphite's May 2026 report averages three detectors (Pangram, GPTZero and Copyleaks), while its earlier 2025 report, on 43k URLs, used the Surfer detector with a 4.2% false-positive rate; that page itself says it has been superseded. Second, Epoch AI's estimate (about 300 trillion tokens, fully used between 2026 and 2032 at 80% confidence) covers public text only, and we found no newer version.

## Why does the bell curve narrow?

Because a width estimated from a finite sample is systematically a little too small, and that shortfall multiplies across generations. Each generation fits the mean and standard deviation by maximum likelihood:

```text
σ̂² = (1/n) · Σ (x_i − x̄)²
n·σ̂² / σ² ~ χ²(n − 1)
E[σ̂²] = σ² · (n − 1)/n
```

So the expected variance is multiplied by (n − 1)/n every generation. For the width of a typical run, look at the logarithm instead:

```text
log σ_(t+1) = log σ_t + ½ · log( χ²(n − 1) / n )
```

The second term is an independent random variable each generation with a slightly negative mean, about −1/n. So log σ is a random walk drifting downwards, and the median σ after t generations is roughly e^(−t/n). With n = 100, against the median of 200 runs in the result file:

| Generation t | Prediction e^(−t/100) | Simulated median (replace) |
|---|---|---|
| 50 | ≈ 0.61 | 0.599 |
| 100 | ≈ 0.37 | 0.371 |
| 200 | ≈ 0.14 | 0.139 |
| 500 | ≈ 0.007 | 0.007 |

Because it is a random walk, the spread across runs grows too. The share of runs whose width fell below 0.5 was 37% at generation 50, 67% at 100, 92.5% at 200, 99.5% at 500 and 100% at 1,000. One important consequence: collapse speed scales with 1/n. The 100-point sample was chosen small on purpose so the effect shows within a few hundred generations.

## Why do the tails die before the rest of the curve?

Because tail mass is an exponential function of 1/σ². The mass that N(0, σ) places outside the original −2 to 2 range is 2·Φ(−2/σ), where Φ is the Gaussian cumulative distribution function, and it shrinks roughly like e^(−2/σ²). A moderate loss of width causes a large loss of tail.

The result file shows exactly that. Between generations 10 and 50 the median width went from 0.904 to 0.599, a drop of about a third; over the same span the tail mass went from 3.67% to 0.37%, about ten times smaller. The generation-0 tail mass (4.71%) sits slightly above the true 4.55% because even the first fit uses a 100-point sample. This is the Nature paper's "early stage": rare things are effectively gone before the curve as a whole collapses.

## What do words have to do with genetic drift?

The word experiment is the Wright–Fisher model. Each generation samples N tokens (here 20,000) from the previous generation's frequencies. A word with count c becomes a Binomial(N, c/N) count in the next generation. Its expected frequency does not change, so there is no "selection", but the variance accumulates and zero is absorbing: a word that hits zero is never generated again.

The probability that a word with count c disappears in one generation:

```text
P(lost in one generation) = (1 − c/N)^N ≈ e^(−c)
```

A word seen once is gone in the next generation with probability about e^(−1), close to 37%; a word seen three times, about 5%. In a Zipf corpus a large share of the vocabulary appears only once or twice, which is why the very first generation already took 622 words (3,172 to 2,550). In neutral population genetics, the chance that a variant eventually takes over the whole population equals its current frequency, so for a rare word the chance of eventual loss is almost one.

A subtle point: Simpson diversity (the probability that two random tokens are different words) is multiplied on average by only (1 − 1/N) per generation, which for N = 20,000 is very close to one. The structure of common words changes slowly while the count of distinct words crashes. The "effective vocabulary" (the exponential of entropy), which sits between these two views, fell from 417 at generation 0 to 99 at generation 100 under replace. Which diversity index you pick gives a different picture of the same collapse.

## How do replace, keep10 and accumulate differ?

The three regimes differ only in what each generation trains on:

| At generation 100 (unless stated) | replace | keep10 | accumulate |
|---|---|---|---|
| Median width (original = 1) | 0.37 | 0.92 | 0.98 |
| Median width, generation 1,000 | 0.00 | 0.93 | 0.98 |
| Tail mass (original 4.55%) | 0.00% | 3.42% | 4.31% |
| Words alive (of 3,172) | 220 | 1,774 | 3,172 |
| Rarest half alive (of 1,586) | 36 | 573 | 1,586 |

**replace** is pure drift: each generation sees only the previous output, and the maths of the last two sections runs unchecked.

**keep10** takes 10% of each generation's data from the original real data: in the Gaussian experiment, 10 points drawn from the original 100 plus 90 synthetic points; in the word experiment, 2,000 real tokens plus 18,000 synthetic ones. In population-genetics terms this resembles migration from a mainland population onto an island: drift removes variants, migration reintroduces them, and the two reach a balance. The result is stable but narrower than the original: from generation 10 on, the width moved between 0.92 and 0.95, tail mass stayed between 3.4% and 4.2% (original 4.55%), and the word count settled between 1,760 and 1,774 from generation 20 onward.

**accumulate** fits each generation on all data so far (real plus every synthetic generation). Generation t adds only n new points to a pool of about (t+1)·n, so each new generation's weight is about 1/(t+1). The random jolt each generation gives the width is proportional to that weight, so its variance shrinks like 1/t²; the sum of those variances is finite, and the width "freezes" near its starting value. That intuition matches what Gerstgrasser et al. proved for a linear model: the error has a finite upper bound ([arXiv 2404.01413](https://arxiv.org/abs/2404.01413)). In the result file the width stayed between 0.981 and 0.986 from generation 10 to 1,000. All 3,172 words surviving, however, is by design: the original text is always in the pool.

<figure>
<svg viewBox="0 0 640 320" role="img" aria-labelledby="g01en-title g01en-desc" style="max-width:100%;height:auto" font-family="system-ui, sans-serif" font-size="12">
<title id="g01en-title">Median fitted width (σ) per generation for the replace, keep10 and accumulate regimes; toy simulation, ILLUSTRATIVE, seed 2026</title>
<desc id="g01en-desc">Under replace the width falls from about 1 to zero by generation 1,000; keep10 stays near 0.93 and accumulate near 0.98. Generations are unevenly spaced on the horizontal axis.</desc>
<text x="70" y="24" fill="currentColor" opacity="0.7">ILLUSTRATIVE · toy simulation · seed 2026 · median of 200 runs</text>
<g stroke="currentColor" stroke-opacity="0.2">
<line x1="70" y1="60" x2="610" y2="60"/>
<line x1="70" y1="160" x2="610" y2="160"/>
<line x1="70" y1="260" x2="610" y2="260"/>
</g>
<g fill="currentColor" text-anchor="end">
<text x="62" y="64">1.0</text>
<text x="62" y="164">0.5</text>
<text x="62" y="264">0</text>
</g>
<g fill="currentColor" text-anchor="middle">
<text x="70" y="280">0</text>
<text x="147.1" y="280">1</text>
<text x="224.3" y="280">10</text>
<text x="301.4" y="280">50</text>
<text x="378.6" y="280">100</text>
<text x="455.7" y="280">200</text>
<text x="532.9" y="280">500</text>
<text x="610" y="280">1000</text>
<text x="340" y="306">generation (uneven spacing)</text>
</g>
<text x="18" y="160" fill="currentColor" text-anchor="middle" transform="rotate(-90 18 160)">median σ</text>
<polyline fill="none" stroke="currentColor" stroke-width="2" points="70,62 147.1,61.6 224.3,63.3 301.4,63.7 378.6,63.2 455.7,62.8 532.9,63.1 610,63.1"/>
<polyline fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="6 4" points="70,63 147.1,65.2 224.3,70 301.4,71.7 378.6,75.7 455.7,70.9 532.9,73.1 610,73.5"/>
<polyline fill="none" stroke="#E8A33D" stroke-width="2.5" points="70,59.4 147.1,63.1 224.3,79.2 301.4,140.3 378.6,185.9 455.7,232.3 532.9,258.5 610,260"/>
<g fill="#E8A33D">
<circle cx="301.4" cy="140.3" r="3.5"/>
<circle cx="378.6" cy="185.9" r="3.5"/>
<circle cx="455.7" cy="232.3" r="3.5"/>
<circle cx="610" cy="260" r="3.5"/>
</g>
<text x="610" y="50" fill="currentColor" text-anchor="end">accumulate ≈ 0.98</text>
<text x="610" y="94" fill="currentColor" text-anchor="end">keep10 ≈ 0.93 (dashed)</text>
<text x="250" y="172" fill="#E8A33D" text-anchor="end">replace</text>
</svg>
<figcaption>Median width of the fitted Gaussian across 200 runs, for three data regimes. ILLUSTRATIVE toy simulation; data from results-seed2026.json. Generations are unevenly spaced on the horizontal axis.</figcaption>
</figure>

## How do you reproduce everything yourself?

The script needs only the Python 3.9+ standard library. All commands run from the repository root.

```bash
# Full run (about 90 seconds): 200 Gaussian runs, 20 word runs
python3 parts/04-global/hmd-g01-model-collapse/artifact/collapse_lab.py --out-dir /tmp/hmd-g01
diff /tmp/hmd-g01/results-seed2026.md parts/04-global/hmd-g01-model-collapse/artifact/results-seed2026.md
```

Without `--out-dir`, a full run overwrites `results-seed2026.md` and `.json` inside `artifact/` itself; point it elsewhere if you want the committed files untouched. We expect `diff` to show no differences; if it does, report your Python version along with it.

```bash
# Quick demo (about 15 seconds, writes nothing)
python3 parts/04-global/hmd-g01-model-collapse/artifact/collapse_lab.py --quick
```

**A warning about `--quick`:** its numbers differ slightly from the result file. According to the episode's package notes, this mode gave 217 words at generation 100 instead of 220, and 3,229 starting words instead of 3,172. The reason is in the code: both experiments draw from one random stream, and the word corpus is built after the Gaussian runs. `--quick` cuts the Gaussian runs from 200 to 20 and the word runs from 20 to 5, so even the starting corpus changes. The pattern holds; the exact numbers do not.

```bash
# Robustness check with another seed
python3 parts/04-global/hmd-g01-model-collapse/artifact/collapse_lab.py --quick --seed 7

# Change the sample size (theory predicts collapse about 10 times slower)
python3 parts/04-global/hmd-g01-model-collapse/artifact/collapse_lab.py --quick --n 1000

# Word experiment on your own text
python3 parts/04-global/hmd-g01-model-collapse/artifact/collapse_lab.py --text my.txt --out-dir /tmp/hmd-g01
```

The `--quick --seed 7` control gave the same pattern: width 0.37 and 228 words at generation 100. The `--n 1000` prediction follows from the maths in "Why does the bell curve narrow?" and we have not run it; testing it is a good exercise.

A note for non-Latin text with `--text`: the script splits words with the regular expression `\w+`. In Python that matches Persian or Arabic letters, but not the zero-width non-joiner (ZWNJ) used inside many Persian words, so a word like «می‌شود» is split into two pieces. Normalise ZWNJ before running, or keep the split in mind when reading the results.

## What this does not show

- No large language model was trained, and no published model is called "collapsed". The models are a Gaussian and a word-count table.
- The size of the real-world effect was not measured. Collapse speed scales with 1/n, and n = 100 is deliberately small.
- The reported numbers are medians; single runs vary a lot, as the share of runs below width 0.5 shows.
- In keep10, the "real" data is itself finite: it is resampled from the same original 100 points or 20,000 tokens, not from a fresh source.
- All words surviving under accumulate is by design, not a discovery.
- "About half the web" is a detector estimate. The main run uses one seed, and the seed-7 control was run only in `--quick` mode.

## Further reading

- Shumailov et al., *AI models collapse when trained on recursively generated data*, [Nature 631](https://www.nature.com/articles/s41586-024-07566-y) and [PMC version](https://pmc.ncbi.nlm.nih.gov/articles/PMC11269175/); preprint *The Curse of Recursion*, [arXiv 2305.17493](https://arxiv.org/abs/2305.17493).
- Gerstgrasser et al., *Is Model Collapse Inevitable?*, [arXiv 2404.01413](https://arxiv.org/abs/2404.01413); replace versus accumulate.
- Villalobos et al., Epoch AI, [Will we run out of data?](https://epoch.ai/blog/will-we-run-out-of-data-limits-of-llm-scaling-based-on-human-generated-data).
- Graphite, [May 2026 report](https://graphite.io/research/ai-now-writes-as-many-online-articles-as-humans-do) and [October 2025 study](https://graphite.io/research/ai-content-in-search-and-llms).
- Hartl and Clark, *Principles of Population Genetics*; a standard textbook for the Wright–Fisher model and migration–drift balance.
- [Episode HMD-005](/en/episodes/hmd-005/), on how models split Persian text into tokens.

*Persian original: [فروریزی مدل در شبیه‌سازی: ریاضی دنباله‌ها و بازتولید](/fa/blog/hmd-g01-collapse-simulation/)*
