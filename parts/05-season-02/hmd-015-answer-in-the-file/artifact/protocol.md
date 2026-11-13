# HMD-015 · experiment protocol (fixed before any model call)

Written 13 Nov 2026, before the API stage. The local retrieval stage was run on the same day.
Everything here is **ILLUSTRATIVE**: the company *Dayereh*, its documents and its questions are invented.

## Question

For a pack of company documents of this size and these question types, which of three ways of answering has the
lowest **cost per acceptable answer**, and when an answer is wrong, did the system **never find** the passage or
**find it and misuse it**?

## Fixed design

| Item | Value |
|---|---|
| Documents | 7 invented files, 53 passages, about 2,300 words ("short pack") |
| Long pack | the same 53 + an old 1402 FAQ (12 passages with outdated values) + 160 generated filler passages, about 9,500 words |
| Versions | handbook 1403 → amendment 1 (1404-07-01) → amendment 2 (1405-01-01); insurance 1404 → insurance 1405; FAQ 1402 (long pack only) |
| Test questions | 50, frozen: 42 with a gold answer and gold passage IDs, 8 whose answer is not in any document |
| Dev questions | 10, used only to check the tokenizer and the reply format. Never used to choose a setting |
| Types (test) | lookup 12 · version ("latest") 12 · condition 8 · paraphrase 7 · compute 3 · not in documents 8 |
| Arms | `full` (whole pack), `rag` (word BM25, top 5), `hybrid` (word BM25 + character 4-gram BM25, reciprocal rank fusion, top 5) |
| Retrieval settings | BM25 k1 = 1.2, b = 0.75 (textbook defaults); RRF k = 60 (Cormack et al. 2009); top-k = 5. Chosen before any run, not tuned |
| Position control | `full` only: the pack is shuffled with seed 15, then the decisive gold passage is moved to the start, the middle or the end. Every answerable question is asked at all three positions |
| Model | one model for every arm (`HOMODYNE_MODEL`), same system prompt, same `max_tokens` = 1000, effort as set in `tools/llm.py` |
| Reply | JSON `{answer, passage_ids, not_in_docs}` |
| Grading | exact gold answer: normalised whole-token match against the accepted forms; an answer that also contains an older value counts as wrong. No LLM judge |
| Failure labels | retrieval_miss · stale_version · false_abstain · misread · invented · format_error (see `answer_in_file.py`) |
| Citation support | share of correct answers whose `passage_ids` include a gold passage |
| Cost | tokens × the prices in `prices.json` (owner fills, with the date checked). No prompt caching, no batch discount |
| Latency | median seconds per call, as measured by `tools/llm.py` (cached replies keep the first measurement) |
| Position test | paired: questions wrong only in the middle vs right only in the middle; exact two-sided sign test |

## Known weaknesses (said on screen or in the description)

- The author wrote the documents, the questions and the "overlap" labels, and knew how BM25 works. The questions
  were written before the first retrieval run, but nobody outside can verify that.
- After the first local run, one cosmetic fix changed the generated filler: document dates were capped at today's
  date. That re-drew the random filler. Recall@5 did not change; long-pack BM25 Recall@3 moved from 0.79 to 0.76.
  Both outputs are in this note; the committed results are the second run.
- The "hybrid" here is a standard-library stand-in (word + character n-grams). Production hybrids usually pair BM25
  with an embedding model; this one does not.
- 42 answerable questions are few: differences of a few questions are noise. The report prints counts, not only percentages.
- Persian text, one invented domain, one model per run, one date. Nothing here generalises to other documents,
  languages or models without testing them.
- The old "Lost in the Middle" paper (Liu et al., TACL 2024) motivates the position test. It tested 2023 models and does
  not predict what today's models do.
