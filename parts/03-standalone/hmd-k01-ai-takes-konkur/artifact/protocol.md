# HMD-K01 · experiment protocol (locked before any paid run)

Written 27 Nov 2026, before any model has seen a real question. `konkur_run.py run` stores the sha256 of this file,
`kcore.py`, `konkur_run.py` and `models.json` (plus the git commit) in `meta.json`; `run` warns on resume and the
report prints the fingerprints if any of them changed. **Commit this folder before the paid pilot** so the commit
appears on the report.

## Question

Five current AI models sit Iran's national entrance exam (کنکور سراسری), groups تجربی and ریاضی, years 1403, 1404
and 1405, under the exam's own scoring rule. Who scores higher, who answers faster, who spends fewer tokens and
dollars, and does anything change on 1405, the sitting held after most of the models' training cutoffs?

## 1. Models (exact IDs chosen on run day, then fixed)

| Slot | What | ID |
|---|---|---|
| `gemini` | Google's current flagship | written into `models.json` on run day |
| `claude` | Anthropic's current flagship | same |
| `gpt` | OpenAI's current flagship | same |
| `open1`, `open2` | two open-weight models **that accept images**, from two different labs, via OpenRouter | same |

- `models.json` gets `chosen_on` (date) and the five IDs before the pilot. They are not changed after the pilot starts.
- Each call records the ID the provider says it served (`model_served`), Claude's server-side fallback (`fell_back`)
  and, on OpenRouter, the upstream provider (`upstream`). OpenRouter may route one model to different hosts (and
  quantisations) from call to call; the report lists every upstream host per slot. If the pilot shows more than one,
  say so on screen or choose a model with a single host. Recommended: `HOMODYNE_NO_FALLBACK=1`, so a Claude refusal is recorded as
  a refusal and not answered by another model.
- Training cutoffs are copied from each model card on run day into `sources.md` (R-numbers), with the date read.

## 2. Questions

- **Source:** the official booklets and the **final** answer keys (کلید نهایی) from Sanjesh, downloaded by the owner
  into `private/konkur/raw/` (git-ignored). Years 1403, 1404, 1405 · groups تجربی (booklet subjects: زیست، فیزیک،
  شیمی، ریاضی، زمین‌شناسی) and ریاضی (ریاضی، فیزیک، شیمی). General subjects are not in the exam since 1402.
- **Which sitting:** 1403 and 1404 had two sittings each; we use the **first sitting** (نوبت اول) of each, written in
  `exam.booklet`. 1405 had one. If only one booklet code (دفترچه) is available, it is recorded; the key must match it.
- **Schema** (one file per exam, `private/konkur/questions/<year>-<group>.json`, checked by `konkur_prep.py validate`):
  `exam {year, group, booklet, key_source, key_version, transcribed_by, checked_by_owner, notes}` and
  `questions[] {id, year, group, subject, number, stem, options[4], figures[{path, role, crop{pdf, page, dpi, box}}],
  key [accepted options], key_status final|preliminary|cancelled, notes}`. Formulas in LaTeX between `$…$`.
- **Cancelled questions** (حذف‌شده) are asked but not scored. If Sanjesh accepted two options, both are in `key`.
- **Transcription (Claude, two passes):** pass A from the 150-dpi page images; pass B in a fresh context from a
  200-dpi re-render, without seeing A; `konkur_prep.py diff A B` lists every differing field (after digit and
  whitespace folding); each difference is settled against the page image and noted. The key is typed twice from the
  key PDF and diffed the same way (`konkur_prep.py keys`). The owner spot-checks 25 random questions
  (`konkur_prep.py sample --n 25`, seed 1405) against the booklet before the pilot; any error found → the whole
  subject is re-checked.
- **Figures:** any figure, graph, table drawn as an image, or structural formula is cropped from the page
  (`konkur_prep.py crop`) and sent **as an image** with that question. Text that can be typed is typed.
- **Copyright:** no question text, option text or figure goes into git, the deck or the video except what the
  owner explicitly clears (short quotation for commentary). Results files contain only ids and numbers.

## 3. Prompt and answer (identical for every model)

- **System prompt** (`kcore.SYSTEM`, Persian): the exam setting; one right option out of four; the rule «پاسخ درست
  سه نمرهٔ مثبت، پاسخ غلط یک نمرهٔ منفی… سؤال بی‌پاسخ صفر»; **leaving a question blank is allowed**; no internet,
  tools or calculator; reply with JSON only.
- **User turn** (`kcore.prompt_for`): exam, group, subject, booklet number, stem, the four options as «۱) … ۴) …»,
  and a note when images are attached.
- **Schema:** `{"choice": 1|2|3|4|null}` via each provider's native structured output. If a provider rejects the
  schema in the pilot, that slot alone gets `"no_schema": true` in `models.json` (plain JSON in text; parsed by
  `kcore.parse_choice`) and the report marks it «(no schema)». The global `--no-schema` flag is for debugging only.
- **Parsing:** JSON `choice` 1–4 → answer; `null` → blank; anything else → `unparsed`, **scored as blank** and counted
  separately. No retry for a bad answer; a retry is only for API errors (429/5xx), handled by `tools/llm.py`.

## 4. Running

- One question per call. No conversation history, no examples, no "think step by step".
- All five models start at the same instant (a barrier), each answers its questions in booklet order, one at a time.
  The same wall clock therefore applies to all; provider load at that hour is part of what is measured (§6).
- Settings: `max_tokens` 16000 (a reply that hits it is `truncated`); HTTP reply timeout 900 s
  (`HOMODYNE_HTTP_TIMEOUT`; a slower reply is an error, not retried, and is asked again on resume); Claude effort `medium` (`HOMODYNE_EFFORT`);
  every other model at its provider's default reasoning setting; temperature not set (reasoning models reject it).
  These are fixed for the whole run and printed in `meta.json`.
- Order: mock rehearsal → **paid pilot `--limit 10`** (spread over exams and subjects) → read the pilot report
  (schema accepted? images received? refusals? $ per question) → full run. Pilot answers are reused by the full run
  (same cache), so the pilot is not wasted and not repeated.
- One sitting. No repeats per question (cost). Resume after a crash continues; the first measured latency is kept.

## 5. What is recorded (per call, `private/konkur/runs/<run>/<slot>.jsonl`)

choice, parse flag, label (correct / wrong / abstain / not scored), latency (whole call incl. retries) and the last
attempt's duration, number of attempts, input / output tokens, **reasoning tokens** when the provider reports them
(OpenAI, OpenRouter: `reasoning_tokens`; Gemini: thought tokens; Claude: inside output tokens, not separable;
in every case they are already counted in output tokens and billed as output),
input and output characters, the $ OpenRouter reports, stop reason, refusal category, fallback, served model,
number of images, and the first 400 characters of the reply. `events-N.jsonl` keeps the timeline for replay.

## 6. Metrics and what they can and cannot carry

- **درصد** per subject, exactly as Konkur: (3 × right − wrong) / (3 × scored) × 100; ranges from −33.3 to 100.
  Also raw accuracy (right / scored) and the number of blanks. Exam-level score = درصدهای weighted by the published
  exam coefficients (تجربی 12/9/7/7/1 · ریاضی 12/9/7; 1404/1405 assumed unchanged, see `tables/SOURCE.txt`).
- **Speed:** total time per exam and median seconds per question over first-attempt, uncached calls (Claude's SDK
  retries internally and does not report attempts, so its median can include a retried call). Caveat: this
  is the provider's service at that hour, not the model's "thinking speed"; retries and queueing are in it.
- **Tokens are not comparable across models:** each uses its own tokenizer, and hidden reasoning is reported
  differently or not at all. So the report also gives input **characters** (identical for all), input tokens per
  1000 characters on text-only questions (a tokenizer effect, the bridge to HMD-005), and **dollars** at prices read
  on one date (or OpenRouter's own per-call cost).
- **Contamination check:** per model and group, mean points per question on 1405 minus 1403+1404, with a 95%
  bootstrap interval over questions (4000 resamples, seed 1405). Dates: 1403 first sitting ≈ Ordibehesht 1403
  (spring 2024), 1404 first sitting Ordibehesht 1404 (spring 2025), 1405 on 29–30 Mordad 1405 (20–21 Aug 2026).
  On run day, place each model's stated cutoff on this line: a model whose cutoff is **after** Aug 2026 has no
  "unseen" year and is reported as such; a model whose cutoff is **before** spring 2025 has two unseen years, and
  its 1405-minus-older number mixes seen and unseen. A stated cutoff is not proof of what was in the data. A drop is **not** proof of contamination: 1405 may
  simply be harder, and there is no human anchor for year difficulty in public data. If all models drop together,
  the year is the likelier cause; if only the older-cutoff models drop, that is a hint, not a proof.
- **Rank:** `rank_estimate.py`, always labelled ESTIMATE. Public evidence supports only a coarse range next to a few
  unverified published rows, and only under the assumption of near-full school records (60% of the final score in
  1404/1405); with average grades no range is given. No admission to any university is claimed.
- **Uncertainty:** one sitting of each exam; a few hundred questions per model. Differences between models smaller
  than about the width of the intervals in the report are called "too close to call".

## 7. Fairness caveats (said on screen)

1. A model may have seen 1403/1404 questions and keys during training; that is the point of the 1405 comparison.
2. Time limits: models have no clock; humans have one. We never say a model "finished within the exam time" unless
   the official time per booklet is cited and every model's total is under it.
3. Transcription is ours; a typo can make a question unanswerable. Two passes + diff + owner spot-check.
4. Figures as images favour models with better vision; that is part of the exam, not a bias to remove.
5. Provider load, region and rate limits affect latency; all run at the same time to share the same hour.
6. Structured output may change behaviour (no visible working space). Reasoning models think internally;
   non-reasoning open models do not. Written as a condition of the test, not hidden.
