# HMD-022 artifact · Model Routing Simulator

**ILLUSTRATIVE.** The 200 requests are generated for this experiment. Bank messages, shops, invoices and people are
invented. The three medicines (Zelvorin, Tamirex, Orvadin) do not exist, and their leaflets are not medical advice.

The question: does every request need the biggest, most expensive model? We answer 200 requests with a small model and
a big one, put routers between them, and choose each router's threshold on one set (dev, 80) before testing it on
another (test, 120). The main metric is correct against the truth, never a model's opinion.

## Files

| Path | What |
|---|---|
| `routing_lab.py` | the CLI: `plan`, `run`, `report`, `simulate`, `--selftest` (standard library + `tools/llm.py`; matplotlib for the chart) |
| `taskset.py` | the generator and loader: five categories x two languages x 20, truth computed by code (lookups hand-written) |
| `grade.py` | truth graders: normalised number, alias and yes/no matching; Persian digits and «میلیون»-style words |
| `routers.py` | the routers, the threshold choice on dev, the test evaluation, the bootstrap; **the simulator** |
| `plot.py` | the cost/quality chart (`curve.png`) and its data (`curve.csv`) |
| `spoken.py` | the Persian [RUN] lines for beats 11-13, numbers written as words, at most two per sentence |
| `runmeta.py` | the dollar bound before [y/N], the design fingerprints, and call health (refused, fallback, truncated, confidence formats) |
| `protocol.md` | the fixed design, written before any model call, and its known weaknesses |
| `tasks/tasks.json` | the frozen task set (seed 22): prompt, category, language, split, truth |
| `prices.json` | **owner fills**: USD per million tokens for both models, the date read, the page |
| `results/plan.txt` | the plan, run locally on 24 Nov 2026 with no key (no model called) |
| `results/MOCK-selftest/` | **MOCK** output of the self-test: a fake model and fake prices. It shows the shape of the report and the chart. It is not a result |
| `runs/<small>__<big>/` | created by `run`: `items.jsonl` (every call: reply, tokens, latency, model served), `meta.json`, the answer cache |
| `results/<small>__<big>/` | created by `report`: `report.txt`, `curve.png`, `curve.csv`, `per-item.csv`, `summary.json` |

## What runs now (no key, nothing spent)

```bash
python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/taskset.py          # rebuild tasks.json, print stats
python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py plan
HOMODYNE_MODEL=mock:echo python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py --selftest
```

The self-test (about 5 s) checks the graders on 20 cases, the task set (sizes, no duplicates, no dev/test overlap,
fictional label on every leaflet), runs all 800 calls against a mock model, checks that the oracle beats both models,
that the extreme thresholds equal always-small and always-big, and that **scrambling the test set does not change any
threshold** (they come from dev only). Then it writes `results/MOCK-selftest/`.

## The API run (designed, NOT RUN YET)

```bash
# put ONE line such as ANTHROPIC_API_KEY=... in private/keys.env (git-ignored), then:
export HOMODYNE_NO_FALLBACK=1          # record refusals instead of letting a fallback model answer them
python3 tools/llm.py check
python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py plan
python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py run --limit 5     # $ bound, [y/N], 5 DEV items
python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py run               # 200 items, 800 calls
# fill prices.json (both models, checked_on = the day you read the pricing page), then:
python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py report
```

`run` makes 800 calls (three small samples and one big call per request), about 110 k input tokens by a rough
character count. Before [y/N], `plan` and `run` print dollars: at your prices once `prices.json` is filled, and always a
**CONSERVATIVE UPPER BOUND, NOT AN OFFICIAL PRICE** from its `fallback` block, with every call at its 2,000-token output
cap (HMD-021's convention). `run --limit N` only ever takes dev items, so a trial never shows a frozen test answer.
`plan` prints, and `run` stores in `meta.json`, the sha256 of `grade.py`, `routers.py`, `tasks/tasks.json`, `protocol.md` and the git
commit; `report` flags any of them that changed after the run started. Set `HOMODYNE_NO_FALLBACK=1` before the first
run: the answer cache does not know about it. Answers are cached under `runs/`, so re-running costs nothing. The latency kept is the first,
uncached measurement. With the Anthropic defaults, big = `claude-opus-5-5` and small = `claude-haiku-5-5`; set
`HOMODYNE_MODEL` / `HOMODYNE_MODEL_SMALL` for another pair. If Claude's server-side fallback answers a call,
`model_served` records it and `report` counts it.

`report` prints, on the test set: correct, cost per 1,000 tasks and per 1,000 successes, escalation rate, p95 latency,
missed and wasted escalations for every router; paired bootstrap intervals against always-big; correct by category;
what each router would have done on the risk category; refused, fallback and truncated calls per model, with the
big model's errors split into refusals and wrong answers; how the small model wrote its confidence (0-100, "85%",
0.85, missing) and the unparsed share; then the **Persian spoken lines for beats 11, 12 and 13**.

## Bring your own table

```bash
python3 parts/05-season-02/hmd-022-do-we-need-the-big-model/artifact/routing_lab.py simulate --table my-items.csv
```

Any CSV with the columns in `routers.COLUMNS` (per request: split, category, whether each model was right, its cost,
latency, the small model's confidence and how many of three samples agreed) gets the same curves and threshold choice.

## Claim boundary

One task set, one pair of models, one date, one price list. Prices change. The categories, templates and the rule
router were written by the author, who knows which categories are hard. The oracle is an upper bound, not a product.
RouteLLM (Ong et al., ICLR 2025) reports its savings on MT Bench, MMLU and GSM8K with GPT-4 and Mixtral 8x7B; FrugalGPT
(Chen et al., TMLR 2024) on its own datasets and APIs. Neither number is a prediction for this test.

Code: MIT (repository `LICENSE.md`). RouteLLM's code is Apache-2.0; none of it is used here.
