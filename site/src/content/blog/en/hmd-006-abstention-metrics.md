---
title: "Error, risk and abstention metrics: formulas and data"
description: "Formulas for accuracy, coverage, risk, penalised score and three 'hallucination rates', plus the data and commands to reproduce them."
lang: en
translationKey: hmd-006-deep-dive
hmd: HMD-006
kind: deep-dive
date: 2026-12-25
tags: ["error rate", "abstention", "hallucination", "evaluation method", "reproducibility"]
sources:
  - title: "OpenAI (September 2025): Why language models hallucinate"
    url: "https://openai.com/index/why-language-models-hallucinate/"
  - title: "Kalai et al. (2025): Why Language Models Hallucinate, arXiv 2509.04664"
    url: "https://arxiv.org/abs/2509.04664"
  - title: "AA-Omniscience (Artificial Analysis, November 2025), arXiv 2511.13029"
    url: "https://arxiv.org/abs/2511.13029"
  - title: "Vectara Hallucination Leaderboard (updated 22 October 2026)"
    url: "https://github.com/vectara/hallucination-leaderboard"
  - title: "Kirichenko et al. (2025): AbstentionBench, arXiv 2506.09038"
    url: "https://arxiv.org/abs/2506.09038"
  - title: "Bean et al. (NeurIPS 2025): Measuring what Matters, arXiv 2511.04703"
    url: "https://arxiv.org/abs/2511.04703"
datasets:
  - title: "SimpleQA (OpenAI, simple-evals repository)"
    url: "https://github.com/openai/simple-evals"
    license: "MIT (simple-evals repository)"
  - title: "AA-Omniscience-Public (Artificial Analysis, 600-question public subset)"
    url: "https://huggingface.co/datasets/ArtificialAnalysis/AA-Omniscience-Public"
    license: "Apache 2.0 (public subset, per its dataset card)"
  - title: "Vectara Hallucination Leaderboard (HHEM-2.3)"
    url: "https://github.com/vectara/hallucination-leaderboard"
    license: "Apache 2.0 (repository)"
  - title: "bluff_lab.py and bluff-demo.csv (Homodyne, ILLUSTRATIVE data)"
    url: "https://github.com/AshE-96/homodyne/tree/main/tools"
    license: "Homodyne repository; see LICENSE.md"
  - title: "Construct card (construct-card.md, Homodyne)"
    url: "https://github.com/AshE-96/homodyne/tree/main/parts/02-benchmarking/e03-what-exactly-are-we-measuring/artifact"
    license: "CC BY-NC-SA 4.0"
---

Every error figure is a fraction, and common metrics differ precisely in what they put above and below the line. This post sets out exact formulas for accuracy, coverage, risk, penalised score and three different "hallucination rates", describes the data used in [episode HMD-006](/en/episodes/hmd-006/), and shows how to reproduce the episode's teaching numbers with one command.

If you have not seen the episode, start with the [companion post](/en/blog/hmd-006-error-rate-denominator/). The [Persian version of this deep dive](/fa/blog/hmd-006-abstention-metrics/) is the original.

> **Key Takeaways**
> - Three counts, c (correct), w (wrong) and a (abstained), yield at least six different metrics. None is sufficient alone.
> - "Hallucination rate" in SimpleQA, AA-Omniscience and Vectara means three different formulas on three different tasks.
> - A penalty of k = t/(1−t) makes answering worthwhile only when the probability of being right exceeds t. An always-abstaining assistant scores zero at every t.
> - The episode's teaching numbers reproduce with `bluff_lab.py` and the Python standard library. Bluff itself has not been run.

## Which data does the episode use?

Three published sources and one teaching file. The table shows what each measures and how stable it is.

| Data | What it measures | Version and size used here | Licence | Update cadence |
|---|---|---|---|---|
| SimpleQA (OpenAI) | Short fact-seeking questions, no document | Only the two-model table in OpenAI's post (September 2025); the table is not in the arXiv paper | MIT (simple-evals repository) | Fixed set; table tied to one date |
| AA-Omniscience | Knowledge questions without a document, abstention allowed | arXiv 2511.13029, November 2025; a 600-question public subset is on [Hugging Face](https://huggingface.co/datasets/ArtificialAnalysis/AA-Omniscience-Public) | Public subset: Apache 2.0 (dataset card) | Paper version; results updated on Artificial Analysis's site |
| Vectara leaderboard | Consistency of short summaries with a given document | Live table; last updated 22 October 2026, range 1.8% to 24.2% | Apache 2.0 (repository) | Live, continuous |
| `tools/bluff-demo.csv` | Ten questions for two fictional models, A and B | 20 rows, **ILLUSTRATIVE** | Homodyne repository (see LICENSE.md) | Fixed |

Licences are as each project states them (checked 7 November 2026); check the project page again before redistributing data. The Vectara table is live and its figures may change after this post is published.

## How is each rate defined?

Take N questions, each answered in one of these ways: c correct, w wrong, a abstained, and, in AA-Omniscience only, a fourth category p (partially correct). So c + w + a + p = N.

```text
accuracy            = c / N
error_all           = w / N                 # "error rate" in OpenAI's SimpleQA table
coverage            = (c + w) / N
risk                = w / (c + w)           # undefined when c + w = 0
hallucination_AA    = w / (w + p + a)       # AA-Omniscience, section 2.4.3
hallucination_Vect  = 100 - consistency_%   # Vectara, judged by HHEM-2.3
score(k)            = (c - k * w) / N       # abstain = 0
```

**Accuracy** counts only correct answers and treats abstaining and being wrong alike. **Error over all questions** is what the SimpleQA table calls "error rate"; it falls as a rises, even if c stays flat. **Coverage** is the share of questions the model answered. **Risk** measures errors only among answers given. It is undefined for a model that never answers and must not be reported as zero.

**AA-Omniscience's hallucination rate** restricts the denominator to not-correct responses and asks what share of what the model did not know it filled with a wrong answer. **Vectara's hallucination rate** is something else: the denominator is summaries, and the numerator is summaries that the evaluator model HHEM-2.3 judged inconsistent with the source. The figure therefore includes the evaluator's own errors.

`bluff_lab.py` adds two details. Invalid output (`invalid`) counts as answered and receives the k penalty. A technical failure (`api_error`) is also penalised by k, but its rate is reported separately so it is never confused with a hallucination. Repeated runs of a prompt are averaged within the prompt first, and every prompt carries equal weight.

## What does the SimpleQA table say under three denominators?

OpenAI's table has three rows (abstention, accuracy, error) and each column sums to 100. With no partial category, p = 0, so all three fractions can be computed from the same numbers. The first row is published; the other three are **our arithmetic** on that table.

| | gpt-5-thinking-mini | o4-mini |
|---|---|---|
| Error over all, w/N (published) | 26% | 75% |
| Coverage, (c+w)/N | 48% | 99% |
| Risk, w/(c+w) | about 54% | about 76% |
| AA-style, w/(w+a) | about 33% | about 99% |

One table, three stories. Over all questions the gap is nearly threefold; over answers given it shrinks a lot; over not-correct responses it widens again, because o4-mini almost never abstained. None of these is "the true error rate". Each answers a different question.

AA-Omniscience shows the same pattern: GPT-5 (high) and Grok 4 both have 39% accuracy, but hallucination rates of 81% and 64%. Equal accuracy, different behaviour when the model does not know.

## How does a penalised score relate to a confidence threshold?

Kalai and colleagues propose that a test state an explicit confidence threshold t: answer only if the probability of being correct exceeds t, otherwise abstain ([arXiv 2509.04664](https://arxiv.org/abs/2509.04664)). If a correct answer scores +1, an abstention 0 and a wrong answer −k, then setting k = t/(1−t) makes that rule exactly the best strategy:

```text
E[answer] = P - (1 - P) * k  >= 0   <=>   P >= k / (1 + k) = t
```

`bluff_lab.py` defines its conditions this way: `t50` means k = 1, `t75` means k = 3 and `t90` means k = 9. The `plain` condition (no penalty stated in the prompt) is rescored at k = 3 as a diagnostic only. An assistant that always abstains scores exactly zero at every t: the "line of silence". The tool itself warns that stating t does not make a model calibrated; it only makes the rules explicit.

Why it matters: under binary grading (k = 0) every guess has positive value, and in Kalai and colleagues' phrase abstaining is "strictly sub-optimal". AbstentionBench, across 20 models and 20 datasets, reports that reasoning fine-tuning reduced abstention by 24% on average ([arXiv 2506.09038](https://arxiv.org/abs/2506.09038)). A metric that cannot see abstention cannot see that shift either.

## How do I reproduce the episode's numbers?

Python 3.10 or later, standard library only. From the root of the Homodyne repository:

```bash
python3 tools/bluff_lab.py score tools/bluff-demo.csv --condition t75
python3 -m unittest discover -s tools -p 'test_bluff_lab.py'
```

The first command prints JSON. In the sample file, model A is the episode's ten cards (five correct, two wrong, three abstained) and model B has four correct, one wrong and five abstained. Everything is **ILLUSTRATIVE**; no model was called. Output from the 2 November 2026 run, main fields:

| Output field | A | B |
|---|---|---|
| `accuracy_all_prompts` | 0.5 | 0.4 |
| `coverage_among_completed` | 0.7 | 0.5 |
| `risk_among_answered` | about 0.286 | 0.2 |
| `score_points_per_prompt` (k = 3) | −0.1 | +0.1 |

Model A is more accurate, yet under a heavy penalty it falls below the line of silence while B stays above it. The score is in points per prompt, between −k and 1, not a percentage. The output also includes a SHA-256 hash of the input file and a "guardrail" block for unanswerable (U) items; with only two U items in this file that block is a teaching aid and certifies nothing.

For your own data, the CSV needs these columns: `item_id, cluster_id, model, condition, repeat, language, split, answerable, label, source_status, response`. Labels are `correct`, `wrong`, `abstain`, `invalid` and `api_error`. Translations of one base question must share a `cluster_id`. The tool refuses to mix ILLUSTRATIVE and EMPIRICAL rows, but an EMPIRICAL label is only the user's declaration, not proof of provenance.

## How do I fill in a construct card for a claim?

The card lives at `parts/02-benchmarking/e03-what-exactly-are-we-measuring/artifact/construct-card.md` and has these fields:

1. **Construct:** the quality you actually want.
2. **Definition:** one sentence.
3. **Proxies:** what you count.
4. **Known gaps:** at least three things the proxies miss.
5. **Neighbours it is not:** for example knowledge, stated calibration, faithfulness to a source.
6. **Why not simpler:** why accuracy alone is not enough.
7. **Baseline:** for Bluff, always abstaining, which scores zero at every t.
8. **How it could be wrong:** a result that would count against the claim.

The card's example column fills these in for the Bluff design: the construct is "behavioural calibration under a stated penalty", and the gaps include long answers, "doesn't know" versus "asked badly", and our Persian sources. That is a design, not a result; Bluff has not been run. The card's Vectara row is dated 11 May 2026; the 22 October 2026 table shows the same 1.8% to 24.2% range.

## What are the limits of this method?

- **SimpleQA table:** two models, one date, and only in OpenAI's blog post rather than the paper. The table gives no question count or confidence interval.
- **Vectara:** an evaluator model decides the rate, so evaluator error is inside the number. The task is short summarisation and says nothing about questions without a document.
- **AA-Omniscience:** what counts as partial or abstained depends on the benchmark's grading. We use its figures only to compare measurement philosophies, not as a live ranking.
- **Surface abstention:** these metrics count outward behaviour. A verbal refusal, genuine uncertainty and the correction of a false premise must be separated by an explicit rule before scoring.
- **Sample data:** ten questions are enough to teach the formulas and nothing more. No meaningful confidence interval comes out of them.

## What this does not show

- It does not show which model is better. The formulas teach how to read a number, not how to rank models.
- It does not show that an abstaining model "knows that it does not know". Behavioural calibration is not internal knowledge.
- The A and B figures are not experimental results; they are ILLUSTRATIVE.
- There are no Bluff numbers here, because Bluff has not been run.

## Further reading

- Kalai et al. on why binary grading rewards guessing: [arXiv 2509.04664](https://arxiv.org/abs/2509.04664).
- Full metric definitions for AA-Omniscience: [arXiv 2511.13029](https://arxiv.org/abs/2511.13029).
- 445 benchmarks reviewed by 29 experts, with eight recommendations: [Measuring what Matters](https://arxiv.org/abs/2511.04703).
- Abstention across 20 models and 20 datasets: [AbstentionBench](https://arxiv.org/abs/2506.09038).
