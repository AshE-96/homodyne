# HMD-020 · sources

Every external claim in the script, deck, hooks and package, with the page opened and the date checked. Numbers that
come from our own runs are listed at the end with the file that produced them.

| ID | Source | Opened | What we use | Where |
|---|---|---|---|---|
| R01 | Anthropic, *Structured outputs* — https://platform.claude.com/docs/en/build-with-claude/structured-outputs | 23 Nov 2026 | JSON outputs via `output_config.format` (`type: json_schema`), no beta header; "constrained decoding"; guarantees cover schema conformance ("Always valid", "Type safe"), not the correctness of values; **not supported:** numerical constraints (`minimum`, `maximum`, `multipleOf`), string length constraints; the raw API returns 400 for unsupported features, the SDK helpers move them into descriptions | beat 5 deck tag (minimum/maximum not supported), beat 6, `tools/llm.py` `schema=` |
| R02 | OpenAI, *Structured Outputs* guide — https://developers.openai.com/api/docs/guides/structured-outputs (redirected from platform.openai.com) | 23 Nov 2026 | strict mode: all fields `required`, `additionalProperties: false`, optional values as a union with `null`; supports `minimum`/`maximum`, `pattern`, `format`, `enum`, `anyOf`; the guide tells developers to validate business rules the schema does not express | beat 6, hook 5, `tools/llm.py` |
| R02b | OpenAI API reference, Chat Completions `response_format` — https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create | 23 Nov 2026 | `{type: "json_schema", json_schema: {name, schema, strict}}` | `tools/llm.py` |
| R02c | openai-python `src/openai/types/chat/completion_create_params.py` (main) — https://github.com/openai/openai-python | 24 Nov 2026 | `max_tokens` "is now deprecated in favor of `max_completion_tokens`, and is not compatible with o-series models" | `tools/llm.py` |
| R02d | Ollama, *OpenAI compatibility* — https://raw.githubusercontent.com/ollama/ollama/main/docs/api/openai-compatibility.mdx | 24 Nov 2026 | supports `max_tokens` and `response_format` | `tools/llm.py` |
| R03 | Google, *Improving Structured Outputs in the Gemini API*, 5 Nov 2025 — https://blog.google/technology/developers/gemini-api-structured-outputs/ | 23 Nov 2026 | JSON Schema support for all actively supported Gemini models; keywords including `anyOf`, `minimum`/`maximum`, `type: 'null'`; structured outputs "guarantee adherence to a specific schema" (structure only) | beat 6 («سه شرکت بزرگ»), `tools/llm.py` |
| R03b | Google Cloud, Vertex AI *Structured output* — https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/control-generated-output | 23 Nov 2026 | `responseMimeType` + schema; fields outside the supported list are ignored; recommends a client-side validator with retry | context only |
| R03c | googleapis/python-genai source (`types.py`, `_models.py`), main branch — https://github.com/googleapis/python-genai | 23 Nov 2026 | REST field names `generationConfig.responseMimeType` and `generationConfig.responseJsonSchema` (the SDK's `response_json_schema`); `usageMetadata.thoughtsTokenCount` ("tokens that were part of the model's generated thoughts"); `generationConfig.thinkingConfig.thinkingBudget` (checked 24 Nov 2026). ai.google.dev pages returned HTTP 403 to our fetcher, so the field name was confirmed from the official SDK source | `tools/llm.py` |
| R04 | JSON Schema, *Understanding JSON Schema* — https://json-schema.org/understanding-json-schema/reference/type | 23 Nov 2026 | "By default, `format` is just an annotation and does not affect validation"; our validator asserts `format: date` on purpose | `checks.py`, package |
| R05 | Tam, Wu, Tsai, Lin, Lee, Chen, *Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models*, arXiv 2408.02442 (v1 Aug 2024, v3 Oct 2024) — https://arxiv.org/abs/2408.02442 | 23 Nov 2026 | "a significant decline in LLMs reasoning abilities under format restrictions", on models of 2024; used only as a reason the question is open | beat 6 |
| R06 | Rudaw, Guardian Council approves removing four zeros, 8 Nov 2025 — https://www.rudaw.net/english/middleeast/iran/08112025 | 23 Nov 2026 | bill to remove four zeros approved; multi-year transition overseen by the central bank. Rudaw calls the new unit the "new toman" (= 10,000 rials); other reports say the name stays rial — the script does not name the unit | beat 4, pre-record check |
| R06b | The National, 11 Aug 2025 — https://www.thenationalnews.com/business/money/2025/08/11/iran-approves-plan-to-remove-four-zeroes-from-national-currency | 23 Nov 2026 | one new rial = 10,000 current rials; still needed parliament and Guardian Council approval at that date | background |
| R06c | Wikipedia, *Iranian rial* — https://en.wikipedia.org/wiki/Iranian_rial | 23 Nov 2026 | the toman (10 rials) is "the primary colloquial denomination"; parliament voted on 5 Oct 2025 to redenominate | beat 4 («ما به تومن حرف می‌زنیم، بعضیا ریال می‌نویسن»), data |
| R07 | SURFIRAN, *Nowruz 2027* (last updated 2 Nov 2026) — https://surfiran.com/mag/?p=8966 | 23 Nov 2026 | 1 Farvardin 1406 = Sunday 21 March 2027 (equinox ≈ 23:54 Iran time on 20 March, after noon) | `world.py` check; so 18 Farvardin = Wed 7 Apr 2027 and 19 Farvardin = Thu 8 Apr 2027 (beat 12, release date) |
| R08 | jalaali-js — https://github.com/jalaali/jalaali-js (MIT) | 23 Nov 2026 | Borkowski algorithm; our `world.py` re-implements the same arithmetic in Python (no code copied) and is checked against 1399/12/30 = 2021-03-20, 1403/01/01 = 2024-03-20, 1406/01/01 = 2027-03-21 | `world.py`, selftest |

## Our own numbers (not external claims)

| Number | Where it comes from |
|---|---|
| 100 test + 28 dev messages, 11 groups | `artifact/data/*.jsonl`, `data/FROZEN.json` (generated 24 Nov 2026) |
| answer key: 87 automatic, 13 to a person (9 missing, 2 over cap, 2 deposits) | `artifact/results/local.txt` §1 (24 Nov 2026) |
| fault injection: ×10 → rule 87/87; Jalali in ISO slot → rule 87/87; one day early → silent 87/87; invented missing → silent 9/9; amount as text / cut-off / renamed → structure 87/87 | `artifact/results/local.txt` §2 |
| demo extractor (not AI): 100/100 valid JSON; 37/100 fully right; 63 tidy but wrong, 61 stopped; 2 auto and wrong, both «پس‌فردا» (with rule 5) | `artifact/results/local.txt` §3, `demo-per-record.jsonl` |
| rule 5 effect on the demo: test 23/100 → 2/100 auto-recorded and wrong; dev 3/28 → 0/28 (rule 5 added after seeing the test demo, before any model output) | `artifact/results/local.txt` §4 |
| all model numbers (beats 10–12) | **NOT RUN YET** — `testbench.py report` after `run` |
| prices in the invented catalog (rice 300,000 toman/kg …) | invented, ILLUSTRATIVE; not market prices |

## Licences

All data, messages, prices and the catalog are written by Homodyne for this episode. No third-party dataset, image or
code is redistributed. jalaali-js (MIT) is cited as the algorithm reference only. Illustrations (bank slip, grocery
shelf, chat bubble) must be our own drawings or commercially licensed (CC0 or purchased); no real bank, shop or app
logos; nothing under a non-commercial licence (hard pre-publish gate, `package-fa.md` checklist).
