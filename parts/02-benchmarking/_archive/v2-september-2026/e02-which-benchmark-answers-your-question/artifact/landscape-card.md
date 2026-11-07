# Landscape card — read any benchmark in five questions

*Homodyne Part 02 · E02 · one page · the fuller map lives in
[`benchmark-families.yaml`](../../../../framework/00-landscape/benchmark-families.yaml) and
`python3 -m m2bench families --map | --lifecycle`*

## Five questions

| # | Ask | Example — SimpleQA |
|---:|---|---|
| 1 | **Claim** — what does it say it measures? | Short-form factual knowledge |
| 2 | **Task** — what is actually inside it? | Short questions with one verifiable answer, no search |
| 3 | **Metric** — what does it emit, in what unit? | Correct / incorrect / not attempted, % of questions |
| 4 | **Blind spot** — what can it not see? | Long answers, summaries, grounded (RAG) answering |
| 5 | **Life** — can it still separate today's systems? | Revised as SimpleQA Verified (2025) after label noise |

## Two axes

|  | Controlled / static | Live / interactive |
|---|---|---|
| **Reference answer** | knowledge · reasoning · mathematics · coding · multimodal · multilingual_cultural · retrieval_rag · robustness · factuality · calibration_abstention · safety_security · bias_fairness · efficiency | — |
| **Human / judge / outcome** | — | agents_tool_use · human_preference · product_business |

No corner is better. Top-left is cheap and repeatable and can drift from real use; bottom-right is
closer to real use and costs more, varies more and depends on who judges.

## Six lifecycle states

`fresh` → `discriminating` → `saturating` → `saturated` · `compromised` → `retired`

A benchmark past *discriminating* can still describe the past. It cannot choose between today's
systems. States are dated claims — re-check before citing.

## The selection rule

**Decision → Costly failure → Required evidence → Family.** Write the exclusions too: knowing
which famous benchmark does not answer your question is worth more than a shortlist.

Licence: CC BY-NC-SA 4.0 · Homodyne — Mohammad Mehdi Ghanbari
