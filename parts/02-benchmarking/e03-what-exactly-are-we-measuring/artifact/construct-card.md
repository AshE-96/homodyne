# Construct card — name what you measure, and what you don't

*Homodyne Part 02 · E03 · one page · fill one for any benchmark you build or trust*

> If you can't name what your proxy misses, you don't know what you measure.

## Same word, three constructs: "hallucination rate"

| Construct | Who | Setup | Formula | Published numbers |
|---|---|---|---|---|
| Faithfulness to a given source | Vectara leaderboard (HHEM-2.3) | Summarise a document you are given | 100 − % of summaries consistent with the document | 1.8% – 24.2% across 117 models (24 Nov 2026) |
| Error rate | SimpleQA (OpenAI) | Short questions, no document | wrong ÷ all questions | o4-mini: 75% (Sep 2025) |
| Hallucination rate | AA-Omniscience | Short questions, no document | wrong ÷ (wrong + partial + abstain) | GPT-5 (high): 81% (Nov 2025) |

**One model, two definitions** (real numbers, our join — `derived/same_model_two_definitions.csv`):

| Model, as each source names it | Vectara | AA-Omniscience |
|---|---:|---:|
| `gpt-5-high-2025-08-07` / GPT-5 (high) | 15.1% | 81% |
| `claude-haiku-4-5-20251001` / Claude 4.5 Haiku | 9.8% | 26% |

Different task, different formula. Compare the formulas, not the numbers. (AA does not print the model snapshot date.)

## The card

| Field | Your benchmark | Worked example: "2,338 court cases" | bluff-v1 |
|---|---|---|---|
| **Construct** — the quality you want | | How often AI hands over made-up material in legal work | Behavioural calibration under a stated penalty |
| **Definition** — one sentence | | — (the database does not claim one) | Answer only when P(correct) > t; abstain otherwise; move the line when t changes (Kalai et al. 2025) |
| **Proxies** — what you count | | Decisions where a court found or implied reliance on hallucinated content, found by one researcher (Charlotin database, 25 Nov 2026) | Penalised score at t = 0.75; accuracy, abstention, hallucination rate; abstention slope across t; fabrication on unanswerable items; en–fa gap |
| **Numerator / denominator** | | Numerator only. Nobody knows how many filings used AI | Stated per metric in `spec.yaml` |
| **Known gaps** — what the proxies miss (≥ 3) | | Fakes nobody caught · decisions not yet found · growth in AI use and in attention look the same as growth in error | Internal/verbalised calibration · long answers · "doesn't know" vs "asked badly" · constructed unanswerables may be easier · stated penalties are not current practice · our Persian sources |
| **Neighbours it is not** | | An error rate · a usage rate | Knowledge (accuracy — diagnostic only) · stated calibration · faithfulness to a source |
| **Why not simpler** | | — | Accuracy can't see it (E01); reasoning fine-tuning cut abstention 24% (AbstentionBench) |
| **Baseline** | | — | Always abstain = 0 at every t — the line of silence (on AA-Omniscience it would rank 4th of 36) |
| **How it could be wrong** | | — | Six validity checks, each with a falsification condition (`spec.yaml → validity_argument`) |

## Seven kinds of validity evidence (Jacobs & Wallach 2021)

face · content · convergent · discriminant · predictive · hypothesis · consequential — plus reliability
(test–retest). You will not have all of them. Write the ones you can check, and what result would
count against you.

Sources: Bean et al., NeurIPS 2025 · Jacobs & Wallach, FAccT 2021 · Kalai et al. 2025 · Vectara
(Apache-2.0) · AA-Omniscience (CC BY 4.0) · AbstentionBench · AI Hallucination Cases Database, Damien Charlotin
(CC BY 4.0). Licence of this card: CC BY-NC-SA 4.0 · Homodyne — Mohammad Mehdi Ghanbari
