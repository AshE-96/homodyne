# bluff-v1 · Stage 0 · Family selection

*Homodyne Part 02 · E02 — "Which benchmark answers your question?" · as of 2026-09-29*

Produced with the selection rule in
[`framework/00-landscape/benchmark-families.yaml`](../../../../framework/00-landscape/benchmark-families.yaml) v2.0.0:

```bash
python3 -m m2bench families \
  --decision "which model behind a question answering feature where a confident wrong answer costs more" \
  --failure  "fabricated answer stated with confidence"
```

## The chain

| Link | bluff-v1 |
|---|---|
| **Decision** | Which model can sit behind a question-answering feature where a confident wrong answer costs more than "I don't know" — in English and in Persian? |
| **Costly failure** | A fabricated answer, stated with confidence, that a user acts on. Worse in a language the team cannot check. |
| **Required evidence** | Answer-or-abstain behaviour on verifiable and unanswerable questions, under a penalty the model is told, in English and Persian. |
| **Families** | `calibration_abstention` · `factuality` · `multilingual_cultural` |
| **Diagnostic only** | `knowledge` — accuracy cannot see bluffing (E01), so it is reported beside the primary metric, never as it |

## The exclusions — the useful half

| Family | Why it does not answer this decision |
|---|---|
| `human_preference` | Votes reward length and confident style (Arena style control, 2024) — the behaviour under test. A preference win is not evidence of abstaining when unsure. |
| `reasoning` | A high reasoning score says nothing about abstaining; reasoning fine-tuning lowered abstention by 24% on average (AbstentionBench, 2025). |
| `agents_tool_use` | Measures finishing work in an environment. bluff-v1 excludes tools on purpose; grounded answering is a different construct. |

## Lifecycle check on the anchor data

| Benchmark | State (2026-09-29) | What we do about it |
|---|---|---|
| SimpleQA | compromised — noisy labels, topical bias, redundancy | Not used |
| SimpleQA Verified | discriminating · public | 200-item stratified sample as the English anchor and for Persian translation. Public, so contamination is managed, not assumed away: native Persian items, unanswerable items and a 30% holdout are added (E04) |
| AA-Omniscience | discriminating | Not our data; used for a convergent-validity check (E03 spec, checked in E08) |

## What this selection commits us to

Carried into [`examples/bluff-v1/spec.yaml`](../../../../examples/bluff-v1/spec.yaml) (E03):

- the decision and the cost of being wrong, word for word;
- the exclusions as `scope.exclusions`;
- the lifecycle rule as `governance.retirement_condition` — bluff-v1 retires itself when it saturates,
  when contamination passes 10% of items, or when the answer key's audited error rate passes 5%.
