# HMD-020 artifact · Structured Output Testbench

**ILLUSTRATIVE.** The shop «سبد محله», its catalog, prices and all 128 chat messages are invented. The right answer to
every message is known because the record was created first and the message written from it.

Three independent lights for every order record an AI produces:

| Light | Question | Where it exists |
|---|---|---|
| **Structure** | Does it parse as JSON, and does it fit `schema.json`? | everywhere |
| **Rule** | Does it obey the shop's business rules (price × quantity, delivery window, units, caps, amount or payment mentioned)? | everywhere |
| **Meaning** | Is it what the customer asked for? | only in the lab, with an answer key |

A **silent error** is a record with a green Structure light and a red Meaning light.

## Files

| Path | What |
|---|---|
| `testbench.py` | CLI: `generate`, `local`, `plan`, `run` (`--yes` skips the y/N question), `report`, `--selftest` (standard library + `tools/llm.py`) |
| `local_stage.py` | the local stage: answer key, fault injection, demo extractor, rule-5 before/after |
| `checks.py` | the three lights and the routing decision (auto / repair once / person) |
| `world.py` | catalog, Jalali ↔ Gregorian conversion (Borkowski algorithm, as in jalaali-js), message generator |
| `demo_extractor.py` | **DEMO EXTRACTOR**: a deliberately simple regex program, not an AI model; its shortcuts are listed in its docstring |
| `report.py`, `stats.py` | metrics, Wilson intervals, paired bootstrap, exact McNemar, spoken Persian numbers |
| `schema.json` | the data contract (same schema in the prompt and in native structured output) |
| `protocol.md` | the fixed design, locked rules and acceptance threshold, change log |
| `data/test.jsonl` | 100 frozen test messages with answer keys (`data/FROZEN.json` = SHA-256) |
| `data/dev.jsonl` | 28 development messages (prompts and rules 1–4 were written on these; rule 5 was added after seeing the demo on the test set, see `protocol.md`) |
| `data/catalog.json` | the invented catalog |
| `results/local.txt`, `local.json`, `demo-per-record.jsonl` | the local run, committed (24 Nov 2026) |
| `selftest-output.txt` | the self-test output (24 Nov 2026) |
| `prices.json` | **owner fills**: USD per million tokens and the date read |
| `runs/<model>/` | created by `run`: `rows-test.jsonl` and the answer cache |

## Stage A · local, free, already run

```bash
python3 parts/05-season-02/hmd-020-valid-json-wrong-answer/artifact/testbench.py local
```

Result (deterministic; `results/local.txt`):

- **Answer key through the lights:** 100/100 schema-valid and correct; 87 recorded automatically, 13 go to a person
  (9 missing values, 2 over the household cap, 2 deposits). That is the cost of the rules even for perfect answers.
- **Fault injection** (one known error into each of the 87 automatically recordable correct records):

  | fault | n | caught by structure | caught by rule | silent |
  |---|---:|---:|---:|---:|
  | amount ×10 (rial read as toman) | 87 | 0 | 87 | 0 |
  | amount ÷1000 («۴۵۰ تومن» read literally) | 87 | 0 | 87 | 0 |
  | Jalali date in the ISO slot (1406-01-25) | 87 | 0 | 87 | 0 |
  | **date one day early** | 87 | 0 | 0 | **87** |
  | kg written as g | 45 | 0 | 45 | 0 |
  | item size read as quantity | 19 | 0 | 19 | 0 |
  | **missing value invented** (9 missing-value records) | 9 | 0 | 0 | **9** |
  | amount as text | 87 | 87 | 0 | 0 |
  | reply cut off | 87 | 87 | 0 | 0 |
  | field renamed | 87 | 87 | 0 | 0 |

- **Demo extractor (not AI):** 100/100 valid JSON and schema-valid; 37/100 fully correct; 63 tidy but wrong, of
  which rules and the missing-value check stopped 61. 29 recorded automatically, 2 of them wrong: both «پس‌فردا»
  read as «فردا» (the only two «پس‌فردا» messages in the test set).
- **Rule 5 was fitted after seeing the demo on the test set** (no model output existed). Without it the demo has
  23/100 orders recorded automatically and wrong (spoken amounts 10, colloquial «تومن» 6, rial 5, relative dates 2);
  with it 2/100. Dev alone shows the same hole: 3/28 → 0/28. Beat 9 says this aloud.

## Stage B · model arms, designed, NOT RUN YET

```bash
# put ONE key line in private/keys.env (git-ignored), e.g. ANTHROPIC_API_KEY=...   (see tools/llm.py)
python3 tools/llm.py check
python3 parts/05-season-02/hmd-020-valid-json-wrong-answer/artifact/testbench.py plan
python3 parts/05-season-02/hmd-020-valid-json-wrong-answer/artifact/testbench.py run --limit 3     # look first
python3 parts/05-season-02/hmd-020-valid-json-wrong-answer/artifact/testbench.py run               # asks y/N (--yes skips)
# fill prices.json (price per million tokens + date_read), then:
python3 parts/05-season-02/hmd-020-valid-json-wrong-answer/artifact/testbench.py report
```

`run` makes 300 calls (3 arms × 100 messages) plus at most 100 repair calls, only for `native` records the rules
reject. `plan` estimates about 0.52 M input tokens (characters ÷ 2.5) and, at an assumed 800 output tokens per call
including reasoning, 0.32 M output tokens; measure with `--limit 3`. While `prices.json` has no price for the model,
`plan` and `run` print an UPPER BOUND from the dated conservative fallback price (not an official price) with every
call using all 8,000 output tokens (400 × 8,000 = 3.2 M): about $248 for a Claude model at the fallback price. `run`
and `report` abort if `data/test.jsonl` no longer matches `data/FROZEN.json`; every row stores the hash. The repair
call names the broken rule in words and never the catalog total (the catalog prices are in every prompt, so price
repairs are still easier than in a shop without a price list). `run --split dev` runs the 28 dev messages.
`report` prints the per-arm table with denominators, Wilson intervals, paired differences (bootstrap and exact
McNemar), the routing of arm 4, cost per correct record, and **the Persian spoken lines for beats 10, 11 and 12** with
numbers written as words; it picks the branch.

The `native` arm uses the optional `schema=` parameter of `tools/llm.py`: Anthropic `output_config.format`
(json_schema), Gemini `responseMimeType` + `responseJsonSchema`, OpenAI-compatible `response_format` json_schema with
`strict: true`. For Claude, keywords the API rejects (minimum, maximum, …) are moved into descriptions; our schema
uses none of them.

## Self-test (no key, no network, no cost, about 2 s)

```bash
HOMODYNE_MODEL=mock:echo python3 parts/05-season-02/hmd-020-valid-json-wrong-answer/artifact/testbench.py --selftest
```

Checks the Jalali conversion, the frozen data hash, the schema validator, rules, grader, parser, the `schema=`
plumbing in `tools/llm.py`, the fault matrix, a full mock run of all arms with repairs, the routing totals and the
report. The mock imitates plumbing only (the demo extractor's values with arm-shaped format noise); it says nothing
about any model.

## Claim boundary

A schema checks types and some constraints; syntactic validity does not imply real-world correctness. The price rule
works because the shop has a catalog; there is no such check for names or addresses. Synthetic data, 100 messages,
one model, one prompt, one date.
