---
title: "What happens when AI learns from AI-written text?"
description: "If each generation learns only from the last one's output, rare things vanish first, then everything narrows. Keeping human data stopped it in our test."
lang: en
translationKey: hmd-g01-companion
hmd: HMD-G01
kind: companion
date: 2027-01-29
tags: ["model collapse", "synthetic data", "training data", "simulation", "AI-generated content"]
sources:
  - title: "Shumailov et al. (2024). AI models collapse when trained on recursively generated data. Nature 631, 755–759"
    url: "https://www.nature.com/articles/s41586-024-07566-y"
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
  - title: "Wikipedia: Low-background steel"
    url: "https://en.wikipedia.org/wiki/Low-background_steel"
---

If each generation of models learns only from the previous generation's output, rare things disappear first and then the whole distribution collapses into something narrow and repetitive; researchers call this "model collapse". But when human data stays alongside the synthetic data, the collapse did not happen in our toy simulation, and published research points the same way. The more likely risk is a slow narrowing, not a sudden crash.

> **Key Takeaways**
> - Detector-based estimates put about half of new English web articles as mainly AI-written: an estimate, not a count.
> - A 2024 Nature paper showed that recursive training removes rare things first.
> - In our simulation (ILLUSTRATIVE), when each generation threw away the previous data, 220 of 3,172 words were left by generation 100.
> - Keeping or accumulating real data stopped the collapse, although with only 10% real data some rare words were still lost.

This post accompanies [Homodyne episode HMD-G01](/en/episodes/hmd-g01/). The maths of vanishing tails, genetic drift, and the commands to reproduce everything are in the [deep dive for this episode](/en/blog/hmd-g01-collapse-simulation/).

## How much of the web is machine-written?

About half of new English articles, by Graphite's latest estimate. The company took 55.4k URLs from Common Crawl, a public web archive, and averaged the verdicts of three AI-text detectors. According to its May 2026 report, the share of mainly AI-written articles reached 35.9% twelve months after ChatGPT launched and 48% after twenty-four months, and has stayed near 50% since: 50.9% in Q4 2025 and 49.9% in Q1 2026 ([Graphite, May 2026](https://graphite.io/research/ai-now-writes-as-many-online-articles-as-humans-do)).

That figure is detector output, and detectors make mistakes, so it is an estimate rather than a count. In a separate October 2025 study using the Surfer detector, the same company found that 86% of articles ranking in Google, and 82% of articles cited by ChatGPT and Perplexity, were human-written ([Graphite, October 2025](https://graphite.io/research/ai-content-in-search-and-llms)). The web is full of machine text, but machine text is seen less. The two studies differ in method and detector, so their numbers are not directly comparable.

## Is human-written text running out?

Epoch AI estimates the stock of quality public human text at about 300 trillion tokens, with a 90% interval of 100 to 1,000 trillion. If current trends continue, they project it will be fully used somewhere between 2026 and 2032 (an 80% interval) ([Epoch AI, 2024](https://epoch.ai/blog/will-we-run-out-of-data-limits-of-llm-scaling-based-on-human-generated-data)).

The estimate covers public text only, not images, video or private data. Still, it puts two trends side by side: fresh human text is limited, and the machine-written share has risen.

## What exactly is model collapse?

It is the gradual degradation of models that learn, generation after generation, from each other's output. Shumailov and colleagues demonstrated it in *Nature* (vol. 631, July 2024) across three model families: Gaussian mixture models (GMMs), variational autoencoders (VAEs) and language models ([Nature](https://www.nature.com/articles/s41586-024-07566-y)). In the words of their preprint, the "tails of the original content distribution disappear".

Their finding has two stages. Early on, the tails go: rare words, unusual situations, minority voices. Later, the whole distribution collapses to something narrow. Their language-model experiment fine-tuned OPT-125m on wikitext2. One detail matters a lot: in the setting where 10% of the original data was kept, they saw only minor degradation.

## What happened in our simulation?

We trained two tiny models, generation after generation, on their own output. This is a **toy simulation** (ILLUSTRATIVE): synthetic data, not web data, and not a large language model; run with seed 2026 on 3 November 2026.

**Experiment 1, a bell curve.** The model knows only the curve's centre and width (the standard deviation). Each generation draws 100 points from the previous curve and fits a new one to them (200 runs, 1,000 generations, medians). The width starts at 1. It fell to 0.60 at generation 50, 0.37 at generation 100, and zero at generation 1,000. The tail mass, the share the curve places outside the original −2 to 2 range (4.55% for the true curve), went from 4.71% at generation 0 to 0.37% at generation 50 and effectively zero (0.004%) at generation 100. The tails died long before the curve as a whole.

**Experiment 2, words.** We generated a synthetic 20,000-token text with the shape of real language (a few very common words and thousands of rare ones), containing 3,172 distinct words. The model only knows how often each word appeared, and it generates a new text of the same length. After one generation 2,550 words were left, after ten 1,076, and after a hundred 220. Of the rarest half of the vocabulary (1,586 words), only 36 were still alive at generation 100.

## Why do rare things disappear first?

Because each generation sees only a finite sample, and something rare may simply not appear in it. When it does not, the next model no longer produces it. It is a small error that is never undone and piles up over generations.

This is exactly the maths biologists call genetic drift, described by the Wright–Fisher model. In a small population, rare gene variants are lost by chance alone, with no natural selection involved, and a variant that is lost does not come back. In the word experiment, each word plays the role of a gene variant and each generation of text is a generation of the population.

## What if human data is not thrown away?

Then, in our test, collapse did not happen. The experiments above were deliberately pessimistic: each generation discarded all previous data. Real labs do not do that. Gerstgrasser and colleagues (2024) showed that replacing data leads to collapse, while accumulating synthetic data alongside real data prevents it, and in a linear model the error has a finite upper bound ([arXiv 2404.01413](https://arxiv.org/abs/2404.01413)).

We ran both alternatives. With **accumulation** (all real data plus every synthetic generation, pooled), the curve's width after 1,000 generations was about 0.98, and all 3,172 words survived. With **10% real data kept** in each generation, the width held at about 0.93. One fair caveat: under accumulation the original text always stays in the pool, so no word can ever disappear. That result comes from the design of the experiment, not from a discovery.

## So where is the real risk?

Probably in slow narrowing rather than a sudden crash. With 10% real data the curve did not collapse, but the vocabulary did not survive intact: the word count settled at about 1,774 of 3,172, and only 573 of the rarest 1,586 words survived, roughly a third. The system still works, but it gradually becomes more ordinary.

Who are the tails of the web's distribution? Low-resource languages, dialects, smaller cultures. Persian, the main language of this channel, is arguably part of that tail (on how models handle Persian, see [episode HMD-005 on Persian tokens](/en/episodes/hmd-005/)). That is a hypothesis, not something this episode measured.

Some people compare pre-2022 text to "low-background steel", steel made before nuclear testing and used in sensitive radiation detectors ([Wikipedia](https://en.wikipedia.org/wiki/Low-background_steel)). If the analogy holds, verified human data becomes more valuable, for statistical reasons rather than sentimental ones.

## What this does not show

- It does not show that ChatGPT or any other real model is collapsing; our models were a curve and a word-count table.
- It does not measure the real-world effect size. Collapse speed depends on sample size, and ours was deliberately small (100 points per generation).
- "About half the web" is an estimate from imperfect detectors, not a count.
- That low-resource languages or Persian would be hit harder is a hypothesis and was not measured.

## Try it yourself

The companion script needs only the Python standard library. From the repository root:

```bash
python3 parts/04-global/hmd-g01-model-collapse/artifact/collapse_lab.py --text my.txt
```

This runs the word experiment on your own text so you can see which of your words die first. Run details and the maths behind the results are in the [deep dive](/en/blog/hmd-g01-collapse-simulation/).

*Persian original: [وقتی AI از نوشته‌های AI یاد بگیرد چه می‌شود؟](/fa/blog/hmd-g01-model-collapse/)*
