# HMD-S02 · experiment protocol (locked before any paid run)

Written 28 Nov 2026, before any model has played a move. `chess_run.py run` stores the sha256 of this file,
`chess_core.py`, `chess_run.py` and `models.json` (plus the git commit) in `meta.json`, and `report` prints them.
**Commit this folder before the paid pilot** so the commit appears on the report. Anything changed after the pilot
is written in §8 with the date and the reason.

## Question

When five current language models play chess against each other with nothing but text (no engine, no tools, no
list of legal moves), how often is the move they write legal, what kind of mistake is an illegal move, does that
change once the game leaves the known openings, and how good are the legal moves by an engine's measure?

## 1. Models (exact IDs chosen on run day, then fixed)

| Slot | What | ID |
|---|---|---|
| `gemini` | Google's current flagship | written into `models.json` on run day |
| `claude` | Anthropic's current flagship | same |
| `gpt` | OpenAI's current flagship | same |
| `open1`, `open2` | two open-weight models from two different labs, via OpenRouter | same |

- `models.json` gets `chosen_on` and the five IDs before the pilot. They are not changed after the pilot starts.
- Each call records the ID the provider says it served (`served`). Recommended: `HOMODYNE_NO_FALLBACK=1`, so a
  Claude refusal is recorded as a refusal, not answered by another model.

## 2. Pairings and colours

- Round-robin, circle method: every pair plays **two games, one with each colour** (5 models → 10 pairs → 20 games;
  each model plays 8, four as White, four as Black). Game ids G01…G20 in `chess_run.py schedule`.
- Up to 4 games run at the same time (`--parallel 4`); a model may be in two games at once. Calls are independent.
- Pilot (`--pilot`): G01 and G02 only, 20 plies each. Pilot answers are cached per game and reused by the full run
  **when both use the same `--run NAME`**: a game that ended only at the pilot's lower ply cap is not treated as
  finished; the full run replays it from its cache and plays on.

## 3. Prompt and answer (identical for every model, every move)

- **System prompt** (`chess_core.SYSTEM`, English, because chess notation is English): playing chess; the position
  as FEN and the full history in SAN; choose one legal move; no tools, engine or legal-move list; reply with JSON only
  `{"move": "<SAN>"}`; UCI (e.g. `g1f3`) also accepted.
- **User turn** (`chess_core.prompt_for`): game id, colour, `Position (FEN): …`, `Moves so far: 1. e4 e5 2. Nf3 …`,
  the move number. Nothing else: no evaluation, no hint, no legal moves, no previous replies.
- **Schema:** `{"move": string}` via each provider's native structured output. If a provider rejects it in the
  pilot, that slot alone gets `"no_schema": true` in `models.json` and the report marks it.
- **Parsing** (`chess_core.judge`): JSON `move` first, else the first notation-like token. Normalised: move numbers,
  `+ # ! ?`, `e.p.`, `0-0` → `O-O`, `×` → `x`. Then SAN (python-chess), else UCI. Anything else is illegal.

## 4. Illegal moves, limits, end of game

- **Retry rule:** the first illegal (or unparseable) reply gets **one** retry with a fixed note: «Your previous reply
  "…" was not a legal move in this position. This is your last chance: a second illegal move loses the game.» No
  reason is given. A second illegal reply = **forfeit** (loss). Every illegal reply is diagnosed (`chess_core.KINDS`):
  `ghost_piece`, `unreachable`, `leaves_king_in_check`, `castling_illegal`, `ambiguous`, `bad_notation`, `no_answer`.
- **API errors** (after `tools/llm.py`'s own retries): two more tries 10 and 20 s apart, then the game is *aborted*
  (not scored) and replayed from its cache on resume. An API error is never counted as an illegal move.
- **Game end:** checkmate, stalemate, insufficient material, threefold repetition (claimed automatically), 50/75-move
  rule (python-chess `outcome(claim_draw=True)`).
- **Move cap:** 80 plies (40 moves each; `--max-plies`, default 80). Stockfish is required for the full paid run (the runner refuses without it unless `--no-engine`). Then: with Stockfish, |eval| ≥ 400 cp → win for that side
  («adjudicated: engine ≥ 4 pawns»); otherwise a draw («adjudicated: move cap»). Written in the result.
- **Time:** no chess clock. HTTP reply timeout 900 s (`HOMODYNE_HTTP_TIMEOUT`); a slower reply is an API error.
- **Truncation:** a reply cut off by `max_tokens` (stop = `max_tokens`/`length`) still counts as illegal
  (`no_answer`), but each attempt stores its stop reason and the report counts truncations per model separately.
- **Settings fixed for the run:** `max_tokens` 16000; Claude effort `medium` (`HOMODYNE_EFFORT`); every other model at
  its provider's default reasoning setting; temperature not set. Printed in `meta.json`.
- **Cost cap:** `--max-usd` is required for a paid run. Before every call the running total is compared with it; the
  total uses OpenRouter's reported cost, else `prices.json`, else the deliberately high fallback bound. The total is
  cumulative over every session of the same run (pilot included). At the cap, all games stop and are marked
  *aborted: cost cap* (resumable with a higher cap). Calls already in flight finish, so with `--parallel 4` the total
  can pass the cap by up to four calls.
- Order: mock rehearsal → `plan` → **paid pilot** (`run --pilot --max-usd 3`) → read the pilot (schema accepted?
  $ per move? truncations?) → full run.

## 5. What is recorded

Per call (`data/runs/<run>/events-N.jsonl`): the exact prompt, the reply (first 300 characters), latency, input and
output tokens, reasoning tokens when reported, $ (exact or unknown), cached flag, served model, stop reason.
Per move (`games.jsonl`): SAN, UCI, attempts with their diagnosis, whether the position before the move was in the
opening book, the opening name reached, and with Stockfish: eval before and after, centipawn loss, accuracy, judgement.

## 6. Metrics and what they can and cannot carry

- **First-try legal %** = legal first replies / all first replies (one per decision). **Recovered %** = of the
  decisions whose first reply was illegal, how many were saved by the retry. Illegal replies by kind.
- **Book:** a position is «in book» if it occurs in any named line of `derived/openings.tsv` (Lichess
  chess-openings, CC0, 3,865 lines). Illegal % is reported separately for decisions made in book and out of book.
  This shows *where* errors happen; it does not prove memorisation (book positions are also simpler).
- **Engine:** Stockfish at fixed depth 12 (`--engine-depth`), one thread, evals clipped to ±1000 cp (mate = ±1000).
  Centipawn loss (CPL) = eval before (best play) − eval after, from the mover's side, ≥ 0. ACPL = mean CPL.
  Accuracy and judgement use the Lichess formulas in `chess_core.py`; our game accuracy is a plain mean of move
  accuracies (Lichess uses a weighted and harmonic blend, so its number differs). ACPL depends on depth and on the
  positions: compare models only within this run.
- **Results:** points (win 1, draw ½), W-D-L, forfeits, crosstable. **No Elo is computed.** Eight games per model give
  a 95% interval of about ±35 percentage points of score (±2.8 points of 8); the gap between two models has an
  interval of roughly ±4 points of 8, so gaps of two or three points are «too close to call».
- **Comparison with public boards** (Kaggle chess-text, Epoch chess puzzles): only the order, with dates; their
  harness, prompt and model versions differ from ours.

## 7. Fairness caveats (said on screen)

1. Text only: models see FEN and history, never a picture of the board. Another input format can change results.
2. No legal-move list: that is the point; boards that give one (some harnesses do) measure something else.
3. Reasoning models think before answering; non-reasoning open models do not. A condition of the test, not hidden.
4. One run, on one day; models change monthly. Date on screen.
5. Caching: each game has its own cache, so a resumed game repeats its own answers, never another game's.

## 8. Changes after locking

(none yet)
