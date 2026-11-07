# Construct card — name what you measure, and what you don't

*Homodyne Part 02 · E03 · one page · fill one for any benchmark you build or trust*

> If you can't name what your proxy misses, you don't know what you measure.

## Same word, three constructs: "hallucination rate"

| Construct | Who | Setup | Formula | Published range |
|---|---|---|---|---|
| Faithfulness to a given source | Vectara leaderboard (HHEM-2.3) | Summarise a document you are given | 100 − % of summaries consistent with the document | 1.8% – 24.2% (11 May 2026) |
| Error rate | SimpleQA (OpenAI) | Short questions, no document | wrong ÷ all questions | o4-mini: 75% (Sep 2025) |
| Hallucination rate | AA-Omniscience | Short questions, no document | wrong ÷ (wrong + partial + abstain) | GPT-5 (high): 81% (Nov 2025) |

Different models in each row. Compare the formulas, not the numbers.

## The card

| Field | Your benchmark | bluff-v1 |
|---|---|---|
| **Construct** — the quality you want | | Behavioural calibration under a stated penalty |
| **Definition** — one sentence | | Answer only when P(correct) > t; abstain otherwise; move the line when t changes (Kalai et al. 2025) |
| **Proxies** — what you count | | Penalised score at t = 0.75; accuracy, abstention, hallucination rate; abstention slope across t; fabrication on unanswerable items; en–fa gap |
| **Known gaps** — what the proxies miss (≥ 3) | | Internal/verbalised calibration · long answers · "doesn't know" vs "asked badly" · constructed unanswerables may be easier · stated penalties are not current practice · our Persian sources |
| **Neighbours it is not** | | Knowledge (accuracy — diagnostic only) · stated calibration · faithfulness to a source |
| **Why not simpler** | | Accuracy can't see it (E01); reasoning fine-tuning cut abstention 24% (AbstentionBench) |
| **Baseline** | | Always abstain = 0 at every t — the line of silence |
| **How it could be wrong** | | Six validity checks, each with a falsification condition (`spec.yaml → validity_argument`) |

## Seven kinds of validity evidence (Jacobs & Wallach 2021)

face · content · convergent · discriminant · predictive · hypothesis · consequential — plus reliability
(test–retest). You will not have all of them. Write the ones you can check, and what result would
count against you.

Sources: Bean et al., NeurIPS 2025 · Jacobs & Wallach, FAccT 2021 · Kalai et al. 2025 · Vectara ·
AA-Omniscience · AbstentionBench. Licence: CC BY-NC-SA 4.0 · Homodyne — Mohammad Mehdi Ghanbari
