# Same answers, two scoring rules, two winners

*A one-page replication paper. Homodyne HMD-002 (Benchmark Lab E01), rewritten as a spec. Results are withheld: you must compute them.*

## Abstract

Benchmarks usually report accuracy: the share of questions answered correctly. Accuracy treats a confident wrong answer and an honest "I don't know" the same: both earn zero. We re-score two published model outcomes under a rule that charges for wrong answers and show that the price of a wrong answer decides which model ranks first.

## Data

`data/table.csv`, one row per model. Columns:

| column | meaning |
|---|---|
| `model` | model name as published |
| `accuracy_pct` | % of all questions answered correctly |
| `error_pct` | % of all questions answered wrongly |
| `abstention_pct` | % of all questions where the model declined to answer |

The rows come from the SimpleQA table that OpenAI published on 5 Sep 2025 ("Why Language Models Hallucinate"). The three columns of a row add up to 100 (within rounding).

## Method

1. **Scoring rule.** A correct answer earns +1. An abstention earns 0. A wrong answer earns −k. The score of a model, in points per 100 questions, is

   `score(k) = accuracy_pct − k × error_pct`

2. **Penalty from a confidence target.** Instead of choosing k directly, choose a confidence target t: "answer only if you are at least t sure". The matching penalty is

   `k = t / (1 − t)`

   so t = 0.25 gives k = 1/3 (the Iranian Konkur rule: three wrong answers cancel one right answer), t = 0.5 gives k = 1 and t = 0.75 gives k = 3.

3. **Crossover.** For two models P and Q, the crossover penalty is the k ≥ 0 at which both scores are equal:

   `k* = (accuracy_P − accuracy_Q) / (error_P − error_Q)`

   Below k* one model wins; above it, the other.

## What to report

The request you receive names one quantity defined above. Compute it from `data/table.csv` with a script, not by hand. Report it as a plain number in the units the request asks for.

## Results

Withheld for this replication exercise.

## Limits

This is re-scoring: the models were not told about the penalty when they answered, so it says nothing about how they would behave under it.
