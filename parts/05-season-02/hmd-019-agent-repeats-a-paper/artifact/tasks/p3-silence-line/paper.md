# The silence line: when does answering pay?

*A one-page replication paper. Homodyne HMD-010 (Benchmark Lab E05), rewritten as a spec. Results are withheld: you must compute them.*

## Abstract

Under a penalty k for wrong answers, answering pays on average only when the chance of being right is above t = k / (k + 1). We simulate two answerers that follow the rule "answer only if your confidence is above t": one whose confidence is honest (calibrated) and one that is surer than it should be (overconfident). The overconfident answerer keeps answering and drops below the silence line, the zero score of an assistant that always says "I don't know".

## Data

`data/params.json` holds every parameter: the random seed, the number of questions, the Beta distribution, the clipping bounds, the overconfidence shift and the list of penalties.

## Method (exact; the order of random draws matters)

Use Python 3's standard library: `rng = random.Random(seed)`. Then, for each of `n_questions` questions, in this order:

1. `p = rng.betavariate(beta_a, beta_b)`, then clip: `p = min(p_max, max(p_min, p))`. This is the true chance that the answer is right.
2. `correct = rng.random() < p`
3. The overconfident answerer's stated confidence is `min(stated_max, p + overconfidence_shift)`. The calibrated answerer's stated confidence is `p` itself. No other random numbers are drawn.

Generate the questions once and use the same questions for every penalty and both answerers.

For a penalty k, let `t = k / (k + 1)`. An answerer answers a question only if its stated confidence is strictly greater than t; otherwise it says "I don't know". Over all `n_questions`:

| number | definition |
|---|---|
| score | (right − k × wrong) / n_questions, in points per question |
| coverage | answered / n_questions, in percent |
| risk | wrong / answered, in percent |

## What to report

The request you receive names one number for one answerer and one penalty. Compute it with a script that follows the method exactly. Report it as a plain number in the unit the request asks for.

## Results

Withheld for this replication exercise.

## Limits

Simulated answerers (ILLUSTRATIVE). Whether a real model changes its behaviour when it is told the penalty is not simulated here.
