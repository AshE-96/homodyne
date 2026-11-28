# HMD-S05 · protocol for the live session (fixed before any paid run)

Written 28 Nov 2026, before the run. Changing anything here after seeing outputs means starting a new run folder.

## 1. What is tested
- IMO 2025 Problem 1 (default) and optionally Problem 6, official English statements, downloaded at run time from
  imo-official.org (`python3 imo_live.py --fetch-problems`) into `artifact/data/problems/` (git-ignored). Not bundled:
  IMO copyright, no reuse licence published.
- **Contamination:** the problems and many solutions have been public since July 2025, including OpenAI's and
  Google DeepMind's published proofs and the IMO 2025 Shortlist. Any model trained after that may have seen them.
  So a correct final answer means almost nothing; only the written proof is graded, and even a good proof is not
  evidence of olympiad-level ability under contest conditions.

## 2. Models and settings
- Five slots in `models.json` (Gemini, Claude, GPT, two open-weight models). Exact model IDs written on run day.
- Same system prompt for all (`imo_core.SYSTEM`), same user prompt (`imo_core.prompt_for`): the statement and
  "Write your full solution". No hints, no curated solutions, no examples, no tools, no code execution, no web.
- One attempt per model per problem. No best-of-n, no re-asking, no picking. A transport error is shown on the lane
  and recorded in `events.jsonl`; a retry, if any, is a new attempt and is reported as such.
- Output cap 32,000 tokens; provider-default reasoning settings, recorded (`HOMODYNE_EFFORT`, temperature unset).
- `HOMODYNE_HTTP_TIMEOUT=1800`. Wall time, input/output/reasoning tokens and $ are recorded per answer.
  $ = provider-reported cost (OpenRouter) or `prices.json` filled from official price pages on run day; while a price
  is missing the page shows "$ —", never an invented number.

## 3. Grading (by people, after the run)
- `python3 imo_live.py --grade-sheet RUN` writes `grade-sheet.md` with answers under blind IDs (model and vendor
  names redacted) and the rubric, plus an empty `grades.json`. The key is in `blind-key.json`; graders do not open it.
- Rubrics: `rubrics/2025-P1.json`, `rubrics/2025-P6.json`. They are **Homodyne rubrics in the style of an IMO marking
  scheme, not the official IMO 2025 marking schemes** (approved by the Jury, not published).
- At least one grader; two if possible (an adult with olympiad grading experience is ideal). Each grader writes a
  score 0–7, the rubric items awarded and notes. Disagreement: discuss and record both scores and the agreed one.
- The page shows a grade only when `grades.json` has a score and a grader name. Until then each lane says
  «نمره‌نخورده». No script ever labels an answer correct or solved.

## 4. What we compare and what we do not
- We compare our five answers with each other, under one fixed protocol, graded by the same person.
- We do not compare them with Gemini Deep Think's or OpenAI's 2025 scores (different models, compute, time, grader)
  or with human contestants (4.5 hours, pen and paper, unseen problems, official coordination).
