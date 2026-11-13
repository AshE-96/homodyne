# HMD-015 artifact · the answer is in the file

Public copy: https://github.com/AshE-96/homodyne/tree/main/parts/05-season-02/hmd-015-answer-in-the-file/artifact

**ILLUSTRATIVE.** The company *Dayereh* (دایره), its documents and its questions are invented for this experiment.

One pack of Persian company documents, 50 frozen questions, three ways to answer:

| Arm | What the model sees |
|---|---|
| `full` | every passage of the pack |
| `rag` | "search, then answer": the 5 passages word-level BM25 ranks highest |
| `hybrid` | word BM25 + character 4-gram BM25, merged by reciprocal rank fusion, top 5 |

Each wrong answer gets one label, so **never found it** (`retrieval_miss`) is kept apart from **found it and misused it**
(`stale_version`, `false_abstain`, `misread`). Questions whose answer is not in the documents count `invented` answers;
that is the bridge to HMD-016.

## Files

| Path | What |
|---|---|
| `answer_in_file.py` | everything: `retrieval`, `estimate`, `run`, `report`, `--selftest` (standard library + `tools/llm.py`) |
| `protocol.md` | the fixed design, written before the API stage, and its known weaknesses |
| `pack/docs/*.md` | the documents, one passage per `## ID · title` block |
| `pack/questions.json` | 50 test + 10 dev questions with gold answers, gold passage IDs and older ("stale") values |
| `pack/generated/pack-short.txt`, `pack-long.txt` | both packs as plain text, to paste into any chatbot yourself |
| `prices.json` | **owner fills**: USD per million tokens and the date checked |
| `results/retrieval-local.{txt,json}`, `retrieval-per-question.csv` | the local run (13 Nov 2026), committed |
| `runs/<model>/` | created by `run`: `rows.jsonl`, `summary.json` and the answer cache (re-running costs nothing) |

## Stage A · local, free, already run

```bash
python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py retrieval
```

Result on the 42 answerable test questions (deterministic; `results/retrieval-local.txt`):

| Pack | Passages | Words | BM25 Recall@5 | Hybrid Recall@5 | Older version of the rule in BM25's top 5 |
|---|---:|---:|---:|---:|---|
| short | 53 | 2,296 | 40/42 (0.95) | 40/42 (0.95) | 12 of 13 version questions; ranked **above** the current one in 10 |
| long | 225 | 9,464 | 34/42 (0.81) | 38/42 (0.91) | 12 of 14; ranked above the current one in 10 |

- Every miss is a question worded differently from the document (colloquial or a synonym). In the long pack, BM25
  found 4 of 12 of these, hybrid 8 of 12. High- and medium-overlap questions: 30/30 in every condition.
- The glasses question (`L01`, the hook): in the long pack, BM25 ranks the 1402 FAQ first, the 1404 contract second
  and the valid 1405 contract third. Recall@5 says "found". The model still has to pick the right one.
- Shuffling the pack five times leaves every top 5 unchanged: the retriever is blind to position. So any position
  effect in stage B belongs to the reading model, not to the search.

## Stage B · API, designed, NOT RUN YET

```bash
# recommended: put ONE line such as ANTHROPIC_API_KEY=... in private/keys.env (git-ignored; tools/llm.py reads it)
# or, for this shell only:
export ANTHROPIC_API_KEY=...            # or GEMINI_API_KEY / OPENAI_API_KEY, see tools/llm.py
python3 tools/llm.py check
python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py estimate
python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py run --limit 3     # look at 3 first
python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py run
# fill prices.json (price per million tokens + checked_on date), then:
python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py report
```

`run` makes 468 calls: per pack, `full` asks the 42 answerable questions at 3 positions plus the 8 unanswerable ones
(134), `rag` and `hybrid` ask all 50 once each. `estimate` puts the input at roughly 3.9 M tokens, almost all of it
`full` on the long pack (about 22 k tokens per call at 2.5 Persian characters per token; measure with `--limit 3`).
Cut it with `--packs long`, `--positions middle` or `--arms rag hybrid`.

`report` prints, per pack and arm: correct / answerable, retrieval misses, read errors, stale-version answers,
invented answers on the 8 unanswerable questions, citation support, tokens and dollars per 100 acceptable answers,
median latency; the `full` arm by position with a paired sign test; then **the Persian spoken lines for the [RUN]
beats 10, 11, 12 and the optional line in 15**, numbers written out as the narrator says them.

## Self-test (no key, no network, no cost)

```bash
HOMODYNE_MODEL=mock:echo python3 parts/05-season-02/hmd-015-answer-in-the-file/artifact/answer_in_file.py --selftest
```

A fake reader answers perfectly when the gold passage is in its prompt, "loses" passages in the middle of the long
prompt and invents answers for half the unanswerable questions. The test checks the grader, the position control,
that `rag` accuracy equals the local Recall@5 for a perfect reader, the report and its spoken lines. Nothing is written
outside a temporary folder.

## Claim boundary

No method wins everywhere. The result will hold for this invented pack, these 50 questions, one model and one date.
The hybrid here is a standard-library stand-in, not an embedding model. "Lost in the Middle" (Liu et al., TACL 2024)
motivates the position test; it does not tell us how today's models behave.
