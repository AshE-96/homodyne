# HMD-024 · artifact · Offline AI Capability Card

**Question:** does AI really work without the internet? **Answer format:** a card of which everyday tasks one
laptop model can do offline (✓), can do with a human check (~), or should hand to a stronger model (✗), next to
speed, memory and cost.

Everything below runs from this folder or from the repo root. Standard library, plus `psutil` (memory; falls
back to `ps`) and `matplotlib` (PNGs; optional).

```bash
A=parts/05-season-02/hmd-024-ai-without-internet/artifact
python3 $A/offline_lab.py --selftest   # no Ollama, no key, no network use; ~25 s; everything labelled DEMO
python3 $A/offline_lab.py --selftest --net   # also the real probes + a refused `run --local` (OLLAMA_HOST=127.0.0.1:1, temp folder)
python3 $A/offline_lab.py plan         # device, models, tasks, rules, what is still empty
python3 $A/offline_lab.py doctor       # Ollama installed? running? which models pulled? exact commands
python3 $A/offline_lab.py check --watch    # the red → green moment for camera
python3 $A/offline_lab.py run --local      # refuses unless offline
python3 $A/offline_lab.py run --online     # refuses unless online; estimate first, then [y/N]
python3 $A/offline_lab.py blind            # owner's blind sheet (translations + summaries)
python3 $A/offline_lab.py report           # results/: card .md + .png, quality.png, speed-memory.png, spoken-fa.txt
```

## Protocol

| | |
|---|---|
| Device | the owner's MacBook Air (M1, 2020, `MacBookAir10,1`), 8 GB unified memory. `run` records `hw.model`, chip, memory and macOS itself. |
| Runtime | Ollama (macOS 14+). Ollama started on llama.cpp; since May 2025 newer models run on Ollama's own engine, built on the same GGML tensor library ([blog](https://ollama.com/blog/multimodal-models)). Models are GGUF files. |
| Models | `qwen3.5:2b-q4_K_M` (1.9 GB), `qwen3.5:4b-q4_K_M` (3.3 GB), `gemma3:4b-it-q4_K_M` (3.4 GB). Details, language claims and licences in `models.json` (checked on ollama.com, 23 Nov 2026). Explicit tags on purpose: on Apple silicon a short tag may resolve to an MLX build. |
| Options | `temperature 0, seed 42, num_ctx 8192, num_predict 1024`, `think:false` only for models whose `/api/show` lists the thinking capability. Same system prompt for every arm. |
| Warm-up | each model is unloaded (`keep_alive 0`), then one tiny request measures the cold load. That number is reported on its own; the 30 timed tasks run warm. |
| Online arm | `tools/llm.py` (whatever key/model it resolves), `max_tokens 1024` (same cap as local), `HOMODYNE_EFFORT=low` unless you set it (Claude only), provider-default temperature (llm.py does not set it); a retried request is timed on its last attempt (Gemini/OpenAI) or dropped from the median if over 3× the median (Anthropic SDK, attempts unknown), cached in `runs/online-*/cache/`. Not streamed: only total time, which includes the network. |
| Tasks | `task_bank.py`: 30 synthetic tasks (15 fa, 15 en), 5 per category. Written by Homodyne for this episode before any run; invented names, shops, prices. No outside text, so nothing to license. |

### Offline check (`offline_check.py`)

`run --local` first refuses any `OLLAMA_HOST` that is not 127.0.0.1, localhost or ::1. Then offline means **every**
probe fails: system DNS for two public names, a raw DNS query over UDP straight to 1.1.1.1, 8.8.8.8 and
2606:4700:4700::1111 (so a cached answer cannot fake a pass), and TCP to port 443 on 1.1.1.1, 9.9.9.9 and
2001:4860:4860::8888. It tries a handful of well-known addresses; it is a strong practical check, not a proof. `run --local` checks before the first model, every 10 tasks and at the end; if the network came back,
the run is flagged *not verified offline*. Ollama listens on 127.0.0.1, so it keeps working. The check tests the
public internet, which a cloud service needs; it does not test a local network, and it is **not** a security check.

### Grading (`graders.py`) — the main number is automatic except translation

| Category | Pass means |
|---|---|
| summarise | exactly N bullet lines **and** every required key point (word groups after normalising Persian digits, ی/ك, half-spaces). If the owner fills the blind sheet, a summary marked "adds something not in the text" fails. |
| extract | one JSON object; every field equals the key (numbers without separators, Persian digits allowed, dates compared as dates, names token by token). "300 میلیون" for 300000000 is a fail: we asked for a whole number. |
| qa | the accepted answer appears as a whole token. For the 2 unanswerable questions the reply must be `NOT_IN_TEXT`; anything else is counted as an **invented answer**. |
| translate | **owner's blind checklist**: meaning kept, numbers and names kept, reads naturally — all three yes. Until the sheet is filled, an automatic required-terms + right-language check stands in, and the card says `auto`. |
| classify | exactly one allowed label, and it is the right one. |
| nogo | the `ANSWER:` line matches (the model may reason first). Two reasoning puzzles, one Persian long-context lookup (160 log lines), one English long-context sum of two needles (220 lines). |

No LLM judge is used anywhere. Short answers and `ANSWER:` lines must commit to exactly one candidate: «۷٫۹ یا ۸٫۲» fails.

Blind sheet: `runs/blind/sheet.csv`; the key is in `runs/.key/blind-key.json`, outside the folder you open while
scoring. Code fences and a leading "Here is the translation:" line are stripped from what you see. Blind, but not
perfectly: some models have a recognisable style.

### Rule lock (`locks.py`)

`run` records the sha256 of `rules.json`, `task_bank.py` and `graders.py`, plus the git commit if those files are
committed and clean. `report` refuses to build a card if any file changed since a run (or `--allow-changed-rules`,
which prints a warning on the card and at the top of `spoken-fa.txt`). The card prints the hashes and commit.

A local run whose offline check failed before, during or after is shown on the card as NOT VERIFIED OFFLINE, left
out of the model choice and of the spoken lines, with a blocking warning at the top of `spoken-fa.txt`.

### Measures (`ollama_client.py`)

- **time to first token** (request → first non-empty `message.content` chunk) and **total time**, wall clock, from Ollama's native streaming `/api/chat`;
- **tokens per second** = `eval_count / eval_duration` from Ollama's final chunk;
- **memory**, sampled every 0.1 s: peak RSS of the Ollama runner process, Ollama's own `/api/ps` `size` and `size_vram` for the loaded model, lowest available system memory, highest swap. On Apple silicon the GPU shares RAM and Metal buffers may not all show as RSS, so the card shows RSS and Ollama's number side by side;
- **model size on disk and quantization** from `/api/tags` and `/api/show`;
- **energy and cost** are assumptions in `cost.json`, not measurements:
  `energy_kWh = watts × busy_seconds / 3,600,000` · `energy_cost = kWh × tariff` (marginal: the laptop is already bought) · `depreciation = price / (years × hours_per_year) × busy_hours` (a share of the laptop). For a measured wattage: `sudo powermetrics --samplers cpu_power,gpu_power -i 1000` in a second terminal during `run --local` (optional; needs sudo).

### Decision rules (`rules.json`, locked 23 Nov 2026, before any run)

✓ = 4–5 of 5 → offline · ~ = 3 of 5, or ✓ with a median above 30 s → offline + a person checks · ✗ = 0–2 of 5 → stronger model, unless the text is confidential (then redact or do it by hand) · ✗ where the online model also has ≤ 2/5 → "hard for both", a person does it. The chosen local model is the one that fits (swap growth ≤ 1 GB, fully on GPU) with the most ✓; ties go to the smaller file.

## Files

| File | What |
|---|---|
| `offline_lab.py` | CLI: plan · doctor · check · run --local/--online · blind · report · --selftest |
| `task_bank.py` | the 30 tasks and keys; `python3 task_bank.py` lists them with prompt hashes |
| `graders.py` | the graders above |
| `offline_check.py` | DNS + TCP probes; `--watch` for camera |
| `ollama_client.py` | streaming chat, show/tags/ps, unload, memory sampler |
| `report.py`, `lines_fa.py`, `spoken.py` | card, charts, summary, Persian spoken lines (numbers as words) |
| `demo.py`, `selftest.py` | fake Ollama server on 127.0.0.1 + mock answers; the self-test (no network unless `--net`) |
| `locks.py` | sha256 of rules.json, task_bank.py, graders.py (+ git commit if clean) at `run`; `report` refuses on mismatch |
| `models.json`, `rules.json`, `cost.json`, `prices.json` | models (verified), locked rules, cost assumptions (owner fills), online prices (owner fills) |
| `selftest-output.txt`, `demo/` | real self-test output and its DEMO card/charts. **Not results.** |

## Safety and privacy

- Nothing here installs software or pulls a model; `doctor` prints the commands for the owner.
- The fake server binds 127.0.0.1 only and is stopped at the end of the self-test (the test checks the port is closed).
- Model names ending in `:cloud` run on Ollama's servers and are refused for the local arm. For recording, `OLLAMA_NO_CLOUD=1` turns off Ollama's cloud features (docs.ollama.com/faq).
- Keys stay in `private/keys.env`, read by `tools/llm.py` only. The online arm asks y/N before any paid call.
