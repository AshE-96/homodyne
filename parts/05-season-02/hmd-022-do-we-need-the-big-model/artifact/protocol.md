# HMD-022 · experiment protocol (fixed before any model call)

Written 24 Nov 2026, before the API stage. The task set was generated and frozen on the same day (`tasks/tasks.json`,
seed 22). **ILLUSTRATIVE:** the texts, people, shops and the three medicines are invented; the leaflets are fictional
and are not medical advice.

## Question

For this mix of requests, does a router between a small and a big model save enough money to pay for the quality it
loses and for the extra moving parts it adds? Which requests must never be routed to the small model?

## Fixed design

| Item | Value |
|---|---|
| Requests | 200, Persian and English half each; five categories of 40: `lookup` (stable facts, hand-written), `convert` (units, Toman/Rial, number words), `extract` (a field from a short text with distractor numbers), `multistep` (word problems), `highrisk` (dose questions answered from a fictional leaflet) |
| Split | per category and language: 8 dev + 12 test, drawn with seed 22 -> 80 dev, 120 test. No prompt appears twice |
| Use of dev | only to choose router thresholds (on its 64 non-medication items). Test is frozen: never looked at to choose anything. `run --limit N` takes dev items only |
| Models | big = role `main`, small = role `small` in `tools/llm.py` (provider defaults or `HOMODYNE_MODEL` / `HOMODYNE_MODEL_SMALL`). The served model id is recorded per call |
| Calls per request | small model three times (sample 1 = plain prompt; samples 2 and 3 add "(independent attempt k)" so the cache keeps them apart), big model once. Same system prompt, `max_tokens` 2000, effort as set in `tools/llm.py` |
| Reply | JSON `{answer, confidence}`; confidence 0-100 is the model's own estimate. Other forms are converted and flagged ("85%" → 85; a fraction such as 0.85 → 85; outside 0-100 or text → unparsed, which escalates). The report gives the format counts, the unparsed share and the distribution |
| Main metric | correct by truth: normalised exact match (numbers: one distinct value, tolerance 0.005; text: an accepted alias as whole words; yes/no). **No LLM judge** for the main metric. Hedges with two values are wrong |
| Cost | input and output tokens from each call's `Result` x the prices in `prices.json` (owner fills, with the date read) |
| Latency | seconds per call as measured by `tools/llm.py` on the first, uncached call; cascade samples are counted as sent together (max of three), escalation adds the big call |
| Routers | always-small · always-big · rule-category (multistep and highrisk to big; written now, not tuned) · rule-length (prompt characters > L, L tuned) · confidence (escalate below t, t tuned) · cascade (escalate if fewer than m of the three small samples agree with the first, m tuned) · oracle (cheapest model that was right; upper bound, not a product) |
| Quality budget | on dev, non-risk categories (64 items): at most **2 percentage points** below always-big, which here means at most one item |
| Selection rule | for each tuned router, among thresholds within the budget on dev, the lowest cost per successful task |
| Risk category | **not routed.** Policy: always the big model plus a human check, whatever the curve says. The report shows what each router *would* have let through, as the reason |
| Complexity price | a router is worth switching on only if it cuts the **cost per successful task** by at least **30%** against always-big on test and stays within the budget on test. Below that, two models, a verifier, two price lists and the extra monitoring are not worth it (a product judgement, written down before the run) |
| Uncertainty | paired bootstrap over test items (2,000 resamples, seed 22): 95% interval of the accuracy difference (points) and of the ratio of cost per successful task vs always-big. If the interval includes zero, the report says so |
| "Near" (beat 11) | in one category, the small model is at most the quality budget behind the big one, in whole items: with 24 test items, not behind at all |
| Refusals | run with `HOMODYNE_NO_FALLBACK=1`, so a refusal is recorded (stop reason, refusal category, model served) rather than answered by Claude's fallback model. A refusal counts as not correct, and the report lists it apart from wrong answers, with fallback and truncated counts per model |
| Lock | `plan` and `run` record the sha256 of `grade.py`, `routers.py`, `tasks/tasks.json`, `protocol.md` and the git commit; `report` flags any file changed since the run started |

## Metrics

- correct per category, small and big (test)
- cost per successful task = total cost / number correct
- p95 latency (nearest rank: the slowest one in every twenty)
- escalation rate = share of requests sent to the big model
- router errors: **missed** (kept on small, small wrong, big right) and **wasted** (escalated although small was right)

## Known weaknesses

- The author wrote the categories, the templates and the rule-category rule, and knows which categories are hard.
  The category is given to rule-category for free; a real product would need a classifier for it.
- On this task set, prompt length almost equals the category (characters: lookup 18-88, convert 19-59, multistep
  110-157, extract 149-200, highrisk 443-496), so rule-length measures nothing beyond rule-category here.
- Generated items are cleaner than real traffic. Real traffic has a different mix of easy and hard requests, and the
  mix decides the saving. These 200 items are not a sample of any real service.
- 96 non-risk and 24 risk test items: differences of a few items are noise. The report prints counts and intervals.
- Three small-model samples cost money even when nobody escalates; that cost is counted.
- Self-reported confidence is the model's own number, not a calibrated probability.
- One pair of models, one date, one set of prices. Prices change; the result does not transfer to other models.
- RouteLLM (Ong et al., ICLR 2025) and FrugalGPT (Chen et al., TMLR 2024) report savings on their own benchmarks and
  models. Their numbers are not a prediction for this test, and we do not train a router as they do.
