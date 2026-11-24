# AI Load Lab · HMD-023

*What happens when a hundred people ask the AI at once?* This folder loads **only services on this computer**, measures how the wait grows, and checks the result against a capacity contract (the SLO).

| Tier | What | Status |
|---|---|---|
| 1 · `simulate` | A fake LLM service (`fake_server.py`) with 4 "slots" and a queue, on 127.0.0.1. No model. | **Ran** 24 Nov 2026 → `results/simulated/` · **SIMULATED SERVICE (ILLUSTRATIVE)** |
| 2 · `run --target ollama` | A real small model (`qwen2.5:1.5b`) through Ollama on the owner's laptop. | **[RUN]** — not run yet; the owner runs it |
| 3 · cloud API | Not included (see "Why no cloud arm"). | — |

## The SLO (capacity contract)

> 95% of requests see the first word of the answer within 3 s, and fewer than 1 in 100 requests fail.

- Denominator: **every request sent** in a stage. A timeout or a "busy" (503) is a miss, not a missing row.
- p95 is the nearest-rank 95th percentile over all sent requests. With n < 20 it is basically the maximum, so `n` is printed next to every number.
- k6 users would write the same contract as thresholds: `ttft: ['p(95)<3000']`, `failed: ['rate<0.01']` (R04 in `../sources.md`).

## Commands (from the repository root)

```bash
A=parts/05-season-02/hmd-023-hundred-users-at-once/artifact
python3 $A/load_lab.py --selftest            # fake service only, about 15 s
python3 $A/load_lab.py plan                  # what will run; is Ollama reachable? (loads nothing)
python3 $A/load_lab.py simulate              # about 9 min at --timescale 0.25; writes results/simulated/
python3 $A/load_lab.py simulate --replot     # redraw the PNGs from results/simulated/, no new run
python3 $A/load_lab.py simulate --timescale 1 --users 1,10,50,100 --skip-policies --out /tmp/hmd023-film
                                             # real time, live dashboard: the screen recording for beats 5 and 7
python3 $A/load_lab.py run --target fake --users 1,10 --duration 30 --yes   # rehearse the real-run flow
python3 $A/load_lab.py run --target ollama --num-parallel 4                 # [RUN] about 12 min
python3 $A/load_lab.py report                # Persian spoken lines for beats 10 and 11, numbers as words
```

Python 3.9+, standard library. matplotlib is optional (PNG charts); CSV is always written.

## Files

| File | What |
|---|---|
| `load_lab.py` | CLI: `plan` · `simulate` · `run` · `report` · `--selftest` |
| `fake_server.py` | The simulated service. Speaks Ollama's streaming `/api/chat`, so one client measures both. Binds 127.0.0.1; started and stopped by the lab. `GET /metrics` shows queue, busy slots, rejected, cancelled and wasted slot-seconds |
| `loadgen.py` | Streaming client (time to first word, time to the whole answer), closed-loop users and open-loop arrivals, localhost-only guard |
| `metrics.py` | Percentiles, SLO share, failure rate, throughput, Little's law check, cost per successful request |
| `dashboard.py` | Live terminal dashboard, plain ANSI (no curses). Amber only where the SLO breaks |
| `charts.py` | CSV + matplotlib PNG |
| `experiments.py` | The experiments and the Ollama preflight (prints the setup steps if Ollama is missing) |
| `spoken.py` | Numbers as spoken Persian; the [RUN] lines of beats 10 and 11 |
| `protocol.json` | The locked real-run protocol and its SHA-256 (commit before the laptop run) |
| `selftest.py` | 30 checks: fake service on 127.0.0.1 and a temporary folder only; never the network, never `results/runs/` |
| `selftest-output.txt` | Real selftest output (SIMULATED; never used in the video) |
| `results/simulated/` | `summary.md`, `results.json`, `meta.json`, `stages.csv`, `policies.csv`, `timeline.csv`, `requests.csv`, `cold.csv`, `charts/*.png` |
| `results/runs/<date>-ollama-<model>/` | Created by `run`; same files plus the hardware and Ollama settings |

## What the simulation is (and is not)

The fake service is a teaching device. Every number in `results/simulated/` follows from parameters we chose (`meta.json`):
4 slots · prefill 600 tokens/s · decode 80 tokens/s per slot, 10% slower for every other busy slot · cold load 4 s · queue up to 512 (the Ollama default) · input 80–240 tokens, output 40–200 tokens · users think about 20 s between questions · 120 s per stage · client timeout 30 s.

**Modelling assumption, not a sourced fact:** each stream slows 10% for every other busy slot (`contention 0.10`), so extra slots on the same hardware are not free. The "double slots, same hardware (sim)" policy result follows directly from this choice. The four policies and their thresholds (queue cap 4; shorter answers once 2 are waiting) were chosen by us.

It shows **shapes** that hold for any queue: waiting stays near zero, then jumps once arrivals approach what the slots can finish; a closed-loop crowd slows itself down; Little's law L = λW holds over each stage window. It does **not** say how fast any real model or product is.

`--timescale 0.25` runs the simulation four times faster than real time; the server schedules tokens on an absolute clock so sleep overhead does not pile up, and every reported duration is converted back to service seconds.

## Load patterns: users are not requests per second

- **Closed loop** (`users`): each virtual user sends, waits for the whole answer, thinks (exponential, mean 20 s), and sends again. When the service slows, users send less. Users start at random moments in the first 10 s of a stage: the "9 a.m." burst.
- **Open loop** (`rates`): Poisson arrivals at a fixed rate, whatever the service is doing. The same seed at every rate (common random numbers), so the curve compares like with like.
- Always say both: *N users with think time Z and answers of about T tokens* is not comparable with *R requests per second*.

## Cold and warm

The first request after a (re)start waits for the model to load. `simulate` restarts the fake server three times; `run --target ollama` unloads the model (`keep_alive: 0`) three times. Each time: one cold request, then one warm request. Cold numbers are never mixed into the stage statistics; every stage starts after a discarded warm-up request.

## The real run ([RUN]) — what the owner prepares

1. Install Ollama for macOS: https://ollama.com/download (the owner installs it; this lab never downloads anything).
2. Concurrency (R07): `launchctl setenv OLLAMA_NUM_PARALLEL 4`, then quit and reopen the Ollama app. Pass the same number to `--num-parallel` so it is recorded. Do **not** set `OLLAMA_HOST` to `0.0.0.0`; the lab only loads 127.0.0.1.
3. Model (R09): `ollama pull qwen2.5:1.5b` — 986 MB, Q4_K_M, 1.54B parameters, Apache 2.0. Why this one: text-only with standard attention, so `OLLAMA_NUM_PARALLEL` behaves as the FAQ documents; no thinking mode, so time to first word is clean; Apache 2.0; small enough for an M1 with 8 GB and 4 parallel requests. Avoid `qwen2.5:3b`: the Ollama page says the 3B and 72B sizes are under the Qwen (research) license.
4. Charger plugged in, heavy apps closed. Then `run --target ollama --num-parallel 4` (asks y/N first), then `report`.
5. Paste the `report` lines into beats 10 and 11 of `../script-fa.md`, the numbers into `../deck.src.html` (replace "—", drop NOT RUN YET), rebuild the decks.

`run` records: date, Ollama version, model and digest, `OLLAMA_NUM_PARALLEL`, chip, RAM, macOS, power source, every load parameter, every request.

**Locked protocol, pinned in git.** `protocol.json` holds `experiments.RUN_PROTOCOL` and its SHA-256 (`plan` prints it; `plan --write-protocol` rewrites the file). Commit and push it before the laptop run; the commit pins what the script's lines were written for. The lock covers the SLO, the stages, think and timeout, `max_tokens`, `no_think`, the prompt template (request number first + «حدود صد و پنجاه کلمه جواب بده») and the SHA-256 of the 16 prompts. The [RUN] lines of beats 10 and 11 were written for `experiments.RUN_PROTOCOL` (1, 10, 50, 100 users · 120 s · think 20 s · ramp 10 s · timeout 30 s · 160 tokens · 3 cold tries · `qwen2.5:1.5b` · the SLO above). `run` stores the protocol it actually used, its SHA-256, the protocol's SHA-256 and the prompts' SHA-256 in `meta.json`. `report` also compares against `protocol.json`, recomputes the hashes and refuses to print spoken lines (exit 2) if the run differs or `meta.json` was edited; `--allow-mismatch` overrides, and then the script's hedges must be rewritten by hand. `simulate` stores `config_sha256` the same way.

**Cost before y/N.** `run --target ollama` prints an upper-bound estimate before asking: $0.00 in API fees (nothing but 127.0.0.1 is called); electricity and wear are not counted.
Prompts: 16 everyday Persian questions, each starting with its request number so no two share a prefix the server could reuse; `num_predict` 160.

## Verifying concurrency

The lab cannot read the server's real `OLLAMA_NUM_PARALLEL`. It records the value you pass with `--num-parallel`, and it measures the most answers that were streaming at the same moment (`max_streaming`, sampled every 0.5 s). If the two differ, `run` and `report` print a warning, and the spoken line in beat 10 uses the measured number, never the typed one.

## Throughput and "no answer"

- Throughput = successful answers ÷ the stage's real span (stage start to the last answer or hang-up). Answers keep finishing during the drain, so dividing by the 120 s of arrivals would overstate it.
- A timeout is not "no answer": most timed-out requests had already shown a first word. `summary.md` counts both (`timeout (of which first word seen)`), and the script says "no full answer".

## Cold tries

Only the first cold try on the laptop is truly cold from disk; tries 2–3 may hit the OS file cache. `report` speaks try 1 as "the first time" and keeps all three in `cold` in `results.json`.

## Cost per successful request

- Simulation: slot-seconds reserved during the stage's real span ÷ successful answers.
- Laptop: laptop-seconds of the stage's real span ÷ successful answers. No electricity price is assumed.
Work spent on requests the client abandoned (timeouts) is wasted; the fake server counts it (`wasted_slot_s`).

## Why no cloud arm

`tools/llm.py` retries 429 and 5xx errors inside the call, so a rate limit would be invisible from outside; showing it honestly would need a vendor-specific streaming client. And load-testing a service we do not own is out of bounds for this episode, even at 5 concurrent requests.

## Safety

- Targets other than 127.0.0.1 / localhost / ::1 are refused, including `OLLAMA_HOST=0.0.0.0` or a LAN address (`loadgen.parse_ollama_host`).
- The fake server binds 127.0.0.1 and runs in its own process; the lab always terminates it (the selftest checks the port is closed afterwards).
- No API keys are read, no cloud calls are made, nothing is downloaded.
