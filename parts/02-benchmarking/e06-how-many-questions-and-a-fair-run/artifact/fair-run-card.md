# Fair-run card + pre-registration sheet · HMD-012 / Benchmark E06

Fill one **run card** per model and one **pre-registration sheet** per study, and
date-stamp both (a commit hash or a public timestamp) **before** looking at the
primary result. Blank fields are allowed; hidden differences are not.
Template only: nothing below describes a run that has happened.

## A. Run card (one per model × condition)

| Field | Model A | Model B | Note |
|---|---|---|---|
| Provider · model name · exact version string | | | as returned by the API, not the marketing name |
| Date(s) of the run (UTC) | | | versions behind one name can change |
| Prompt / system text (file + hash) | | | identical unless a difference is declared below |
| Sampling settings (temperature, top-p, max tokens, reasoning effort) | | | "default" is a value: write what it was |
| Tools allowed (search, code, files) | | | |
| Answer budget (max length / time) | | | |
| Repeats per question (K) and how they are combined | | | repeats are averaged within a question, never counted as new questions |
| Retry rule (when, how many, which answer is kept) | | | e.g. retry only on `api_error`, at most 2, keep the first valid one |
| Failure rule (`api_error`, `invalid`, refusals) | | | Bluff primary: observed `api_error`/`invalid` score −k, also reported separately |
| Question set (file + hash), same for both models? | | | paired analysis needs the SAME items |
| Item order | | | randomised per model with a recorded seed, or fixed |
| Declared differences and why | | | "fair" ≠ identical; "fair" = declared in advance |

## B. Pre-registration sheet (one per study)

1. **Primary comparison** (one pair, one condition, one language): …
2. **Practical difference** that would change a decision (in the score's own unit, e.g. points per prompt): …
3. **Questions, clusters, repeats:** N items = …, K independent base clusters = …, repeats per item = …
4. **Assumed spread** (paired difference SD or disagreement rate) and where it comes from (pilot, earlier data): …
5. **MDE / power** at that N and spread (`python3 artifact/power_lab.py`, `python3 tools/bluff_lab.py plan`): …
6. **Test:** paired; standard error clustered on base question (Miller 2024, eq. 8) or cluster bootstrap; α = 0.05 two-sided.
7. **Secondary comparisons** and how many: … · correction for many comparisons: …
8. **Failure policy:** what happens to missing, invalid and errored items: …
9. **Stopping rule:** the run is complete when …; no peeking-and-extending.
10. **Changes after registration:** each with date and reason (append below; never edit above).

Signed / timestamped: ………… · Hash of this file: …………

## Why these fields

- Paired + clustered analysis, power, MDE: Miller 2024, *Adding Error Bars to Evals*, arXiv 2411.00640.
- Small test sets miss real gaps and exaggerate the ones they find: Card et al. 2020, EMNLP, arXiv 2010.06595.
- Pre-registration: Nosek et al. 2018, PNAS, doi 10.1073/pnas.1708274114.
