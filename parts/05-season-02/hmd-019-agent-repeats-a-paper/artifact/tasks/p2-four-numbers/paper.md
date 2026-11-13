# "Fewer errors" needs a denominator: four numbers side by side

*A one-page replication paper. Homodyne HMD-006 (Benchmark Lab E03), rewritten as a spec. Results are withheld: you must compute them.*

## Abstract

A claim like "this assistant makes fewer errors" can be true for an assistant that simply answers less. We report four numbers together for every model so that no single number hides the trade-off: accuracy, coverage, risk and a penalised score.

## Data

`data/labels.csv`, one row per (question, model). Teaching data (ILLUSTRATIVE): two made-up models, A and B, on the same ten questions. Columns:

| column | meaning |
|---|---|
| `item_id` | question id, q01 to q10 |
| `model` | A or B |
| `language` | `en` or `fa` (Persian) |
| `answerable` | whether the question has a known answer |
| `label` | `correct`, `wrong` or `abstain` (the model said "I don't know") |

## Method

For one model on a set of N questions, let C = number of `correct`, W = number of `wrong`, and answered = C + W.

| number | definition | unit |
|---|---|---|
| accuracy | C / N | percent |
| coverage | answered / N | percent |
| risk | W / answered (undefined if answered = 0) | percent |
| score(k) | (C − k × W) / N | points per question |

The default penalty is k = 3 (a confidence target of 75%). Abstentions count in N but not in "answered". Unless a request says otherwise, N is all ten questions of that model.

A request may restrict the set, for example to one language. Then N, C and W are counted on that subset only.

## What to report

The request you receive names one of the numbers above, for one model and possibly one subset. Compute it from `data/labels.csv` with a script. Report it as a plain number in the unit the request asks for.

## Results

Withheld for this replication exercise.

## Limits

Ten made-up questions. The numbers teach the definitions; they say nothing about any real model.
