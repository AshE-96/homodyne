# Bluff teaching lab v0.1

This is a small, inspectable analysis tool for the revised scripts. It is
**separate from m2bench**: the older pipeline's metric IDs and JSON schema do not
implement Bluff's factual-answer labels or its four conditions end to end.
Do not use the old synthetic Deep Research report as a Bluff result.

Python 3.10+, standard library only for bluff_lab. If recording the legacy `m2bench families` or schema-validation commands, first install `python3 -m pip install -r requirements-production.txt` in a virtual environment. Those legacy commands require PyYAML and jsonschema.

The v3 deck/runtime verifier is `python3 scripts/check-production-v3.py`; it requires Node for JavaScript syntax checking.

 From the repository root:

```bash
python3 tools/bluff_lab.py demo
python3 tools/bluff_lab.py plan --sd 1.0 --n 450 --delta 0.10
python3 tools/bluff_lab.py score tools/bluff-demo.csv --condition t75
python3 tools/bluff_lab.py compare tools/bluff-demo.csv --a A --b B --condition t75
python3 -m unittest discover -s tools -p 'test_bluff_lab.py'
```

The demo CSV is **ILLUSTRATIVE**. No model was called. `EMPIRICAL` is a
user-supplied declaration, not proof of provenance. Before an empirical report,
reconcile with a preregistered expected-run manifest, inspect response logs,
check model versions and adjudications, then hash the whole approved bundle.
The tool hashes only the input CSV, not a research data lock.

CSV columns: `item_id,cluster_id,model,condition,repeat,language,split,answerable,label,source_status,response`.
English and Persian translations of one base question MUST share `cluster_id`.
Repeats are averaged within prompt before comparing systems. The overall score
weights prompts equally; paired bootstrap samples whole base clusters and keeps
their translations together. The proposed 650-prompt design has at most 450
independent base clusters if its 100 U items are distinct, not 650 independent
facts. Reuse of U facts across languages reduces that count further.

Labels: `correct`, `wrong`, `abstain`, `invalid`, `api_error`. A clear correction
of an unanswerable question's false premise is `abstain`, not a factual answer
to a fabricated question. Hedging with a concrete wrong answer is still `wrong`.
Humans must resolve ambiguity before the lock. No free-form LLM judge is
implemented here. The tool rejects duplicate runs, mixed provenance, differing
item sets between models and inconsistent item metadata.

Scores are **points per prompt** in [-k,1], not percentages. On observed API
errors and invalid output the primary uses the conservative, declared -k rule;
also report those rates separately. Check completely absent runs against your
manifest: CSV alone cannot reveal a missing planned item. `plain` is rescored
at k=3 as a diagnostic, not labelled as a penalty-prompt treatment.

The U interval uses first-repeat outcomes only and a two-sided 95% Wilson
interval. `--max-fabrication 0.05` is an EXAMPLE design choice, not a safety
standard. PASS requires the interval's upper bound to be at most the threshold,
BREACH requires the lower bound above it; otherwise UNKNOWN. API errors or
shared U base clusters force UNKNOWN. This deliberately avoids certifying a
small, uncertain sample as safe.

`compare` gives ONE pointwise 95% interval for a preregistered pair, not an
automatic ranking or a multiplicity-adjusted leaderboard. For six models there
are 15 possible pairwise comparisons. Preselect a few confirmatory comparisons
or implement a justified familywise correction before publication. For an
English–Persian comparison within one model, build one score difference per
base question and use paired resampling; the command does not infer that task
automatically. Do not pretend `--language fa` calculates a language gap: it
filters a model-vs-model comparison to Persian.

`plan` is an explicit normal-approximation SCENARIO for independent equally
weighted cluster differences. Its SD is the paired DIFFERENCE SD, not the SD
of one model's accuracy. It is not a simulation of the full design and does not
establish the old claimed 5/9-point MDE. Use the disjoint pilot to estimate score
variance, retain language/repeat structure, simulate the final estimator, and
record sensitivity before protocol lock.

Before E08: build and audit real questions; finalize permissions, sampling and
annotation; implement expected-run reconciliation and API collection; choose
versions/budget; calibrate judges by language and class; preregister comparisons,
practical effect and failure policy; finish language-gap and multiple-comparison
analysis; freeze outputs and labels; inspect and publish the evidence bundle.
