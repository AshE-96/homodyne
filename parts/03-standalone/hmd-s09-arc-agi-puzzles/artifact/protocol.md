# HMD-S09 · locked protocol for the model run (written 28 Nov 2026, before any paid call)

This file is fingerprinted (sha256) into every run's `meta.json`. If it changes after a run starts, the run is
a different experiment.

## 1. Models

- Five slots, as in HMD-K01: `gemini`, `claude`, `gpt`, `open1`, `open2` (`models.json`).
- On run day the owner writes the exact ID of each provider's current flagship (and two open-weight models from two
  different labs on OpenRouter), copied from the provider's own model list that day, with the date in `chosen_on`.
- The ID each provider reports it served is stored per call (`model_served`). If Claude falls back to another
  model (`fell_back`), the report counts it.

## 2. Tasks

- The five puzzles of the episode (`arc_core.PUZZLES`): four ARC-AGI-1 training tasks (also inside the ARC-AGI-2
  training set) and one ARC-AGI-2 public evaluation task. 7 test inputs in all (task `1ae2feb7` has three).
- All five are **public**. They may have been in any model's training data. This run says nothing about the
  semi-private or private sets, and it is not an ARC Prize score.

## 3. One call

- One call per test input. The prompt is `arc_core.prompt_for(task, i)`: the fixed English instruction
  `PROMPT_HEAD`, every demonstration pair, then the test input; every grid as text, one line per row, cells
  separated by a space (`arc_core.grid_text`). No images, no tools, no code execution.
- The reply is JSON with two attempts, `{"attempt_1": grid, "attempt_2": grid}`, requested through the provider's
  structured output (`SCHEMA` in `arc_run.py`). If the pilot shows a slot rejects the schema, set
  `"no_schema": true` on that slot only; parsing is the same.
- `max_tokens` 16000; provider default sampling; Claude effort `medium` (`tools/llm.py` default); HTTP timeout 900 s.
- Answers are cached (`runs/<run>/cache/`): re-running costs nothing and gives the same numbers.

## 4. Scoring

- A test input is solved if **either** attempt matches the true output **exactly** (same height, same width, every
  cell). No partial credit (as in ARC Prize: two trials per test input, exact match).
- A puzzle is solved only if every one of its test inputs is solved.
- Reported per model: puzzles solved (of 5), test inputs solved (of 7), wall time, tokens in/out, and dollars
  (reported by OpenRouter, or tokens × the owner's prices in `prices.json`; otherwise a labelled UPPER BOUND).

## 5. Timing and cost cap

- All five slots start at the same instant (a barrier); each answers in puzzle order.
- `--max-usd` (default 25): before the run, the plan shows the dollar bound; during the run, a running cost
  bound is kept, and once it passes the cap no new call is made (`capped` events).

## 6. Known weaknesses (say these on camera if asked)

- Five public puzzles are an illustration, not a benchmark: one wrong answer moves a model by 20 points.
- Text grids are one choice of format; ARC Prize's own harnesses also send text, but other formats (images) can
  change the result.
- A single reply with two attempts is not the same as two independent samples.
