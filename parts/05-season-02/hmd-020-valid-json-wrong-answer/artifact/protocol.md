# HMD-020 · protocol (fixed before any model call)

Written 24 Nov 2026, after the local stage and before the first model call. Changes after the first model call must be
added at the bottom with a date and a reason, and the report must say the result was produced after the change. Branch rule for beat 11: "loud errors became silent"
is said only if native has more schema-valid replies than free AND the paired 95% interval of (native − free)
silent errors is above zero.

## Question

When an AI turns a Persian chat order into a JSON record for an API, how many records are **tidy but wrong**, and
which of three independent checks catches which error?

## Data (ILLUSTRATIVE)

- Invented shop «سبد محله», 12 products, invented prices (`world.py`, `data/catalog.json`). "Today" is Wednesday
  2027-04-07 (18 Farvardin 1406). Delivery window: today to today + 14 days.
- Each order is created as a structured record first and then written as a Persian message from templates, so the
  answer key is known by construction. One main trap per message; the rest of the message is easy.
- `data/test.jsonl`: 100 messages, frozen (`data/FROZEN.json` holds its SHA-256). 11 groups: clean 12, digits 10
  (Arabic-Indic digits, dot thousands separator, slash decimal), rial 12, colloquial «تومن» without «هزار» 8,
  amounts in words 10, relative dates 12, Jalali dates 10, sizes and ranges 6, units 6, missing values 6,
  boundary orders 8 (over the household cap, deposits, exactly at the cap or the window edge).
- `data/dev.jsonl`: 28 messages from another seed. The prompts and rules 1–4 were written against dev only.
  **Rule 5 was not:** it was added after seeing the demo extractor's results on the **test** set (see change log).
- Known weaknesses: template messages are cleaner and more regular than real chat; one main trap per message;
  the invented customers always transfer the exact catalog total (except the 2 deposit messages), which makes the
  price rule stronger here than in a real shop.

## Contract (`schema.json`)

Five fields: `product` (catalog id), `quantity` and `unit` (as the customer stated them), `paid_toman` (integer, toman;
null = pay on delivery), `delivery_date` (Gregorian YYYY-MM-DD; null if not given). The schema uses only keywords all
three providers accept in strict/native mode (type, enum, anyOf with null, required, additionalProperties: false,
format: date). Ranges, prices and the window are business rules, not schema.

## Three lights (`checks.py`)

1. **Structure.** The reply parses as one JSON object (a surrounding code fence is tolerated, other text is not) and
   validates against `schema.json` (our validator asserts `format: date`). A record that fails gets no correct field.
2. **Rule.** Five business rules on schema-valid records: unit sold for that product; quantity > 0, ≤ household cap,
   whole for pieces and packs; date inside the window; paid within ±5% of catalog price × quantity; and (rule 5)
   if the message mentions an amount or a payment (تومان/تومن/ریال/میلیون, «کارت به کارت»، «واریز»، «ریختم»),
   `paid_toman` must not be null. Null `quantity`, `unit` or
   `delivery_date` is not a rule violation: it routes to a person ("ask the customer").
3. **Meaning (lab only).** Field-by-field comparison with the answer key: product, quantity with its unit (750 g =
   0.75 kg), paid, date. A null in the key must be null. Full record correct = all four.

**Silent error** = passes Structure, fails Meaning. The headline metric.

## Arms

Same system prompt (catalog, today in both calendars, the contract in words), same 100 messages, same model, same date.

| Arm | Format request |
|---|---|
| `free` | "Reply with the order as JSON with the keys …" |
| `schema_prompt` | the full JSON Schema pasted into the prompt |
| `native` | the same prompt as `schema_prompt` + provider-native schema-constrained decoding (`tools/llm.py schema=`) |
| `native_rules` | `native` + rules: pass → auto; rule failure → one repair call → pass → auto, else person; schema failure or missing value → person. The repair call names the broken rule in words (`checks.REPAIR_HINTS`) and never states the catalog total or the ratio. The catalog prices are still in the system prompt of every arm, so a model can recompute the total; repairs of price errors are therefore easier here than in a shop without a price list |

Model: whatever `tools/llm.py` resolves (`HOMODYNE_MODEL`), one model per run, default effort. `max_tokens` 8000 so a
reasoning model is not cut off. Answers are cached; re-running costs nothing.

## Metrics (all with counts and denominators, per arm, n = 100)

Parse rate; schema pass; field accuracy (of 400); full-record accuracy with a 95% Wilson interval; silent errors;
rule catch rate (silent errors flagged by rules or missing-value check ÷ silent errors); correct-but-stopped
(excluding the 13 orders the answer key itself sends to a person); for
`native_rules`: routes, auto-recorded, auto-recorded and wrong (Wilson interval out of 100), repairs that pass and are correct,
repairs that pass but are still wrong, human-review count; tokens and cost per correct record (cost per correct
auto-recorded order for arm 4). Paired comparisons between arms on the same messages: paired bootstrap 95% interval
of the difference (4,000 resamples over messages, seed 20) and an exact McNemar test.

## Locked decision rules

- Never record a record that fails Structure. Missing value → ask the customer; the model may not guess.
- Rule failure → exactly one repair call, then a person.
- Every automatic record is echoed to the customer in their terms (Jalali date, toman amount) before it is final,
  because a one-day date error passes every light (local fault injection: 87 of 87).
- **Acceptance:** automatic recording is accepted for this run only if at most **2 of the 100** test orders are
  recorded automatically and wrong (denominator: all 100 orders, in the protocol and in `report.py`). Even exactly
  2/100 has a 95% Wilson interval of about 0.6–7.0%, so passing the cap is not proof of a low error rate; the report
  prints the interval and the script says it aloud. Otherwise the group with the most such errors goes to a person.

## Change log

- 24 Nov 2026 (before any model call): **rule 5 added after seeing the demo extractor's results on the frozen
  test set.** A missed amount became `null`, which the contract reads as "pay on delivery", so a wrong record looked
  like a correct one. Effect on the demo (`results/local.txt` §4): test 23/100 recorded automatically and wrong
  without rule 5 (spoken 10, colloquial 6, rial 5, relative date 2), 2/100 with it; dev 3/28 → 0/28, so the dev set
  alone would have shown the same hole. No model output existed at that point. This is disclosed in beat 9.
- 24 Nov 2026 (before any model call, after review): rule 5 widened to payment verbs and «میلیون» (amounts written
  without a unit); the frozen numbers above did not change. Repair prompts changed to name the rule without the
  catalog total. `run` and `report` now abort if `data/test.jsonl` does not match `data/FROZEN.json`, and every row
  stores the hash.
- 24 Nov 2026: fault injection restricted to the 87 records whose correct version is recorded automatically, so a
  catch is caused by the injected fault and not by an unrelated boundary or missing value.

## Claim boundary

A schema checks types and some constraints; syntactic validity does not imply real-world correctness. The price rule
works only because a catalog exists; names and addresses have no such check. Synthetic data, 100 messages, one
model, one prompt, one date.
