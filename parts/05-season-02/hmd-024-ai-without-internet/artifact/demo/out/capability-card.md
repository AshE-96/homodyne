# DEMO — fake server and mock model, NOT a result · Offline AI Capability Card · HMD-024

Device: MacBookAir10,1 · Apple M1 · 8 GB · macOS 27.2 · Ollama 0.0.0-demo · run 2026-11-24
Offline verified before and after every local run: demo-small:q4 yes, demo-big:q4 yes

| Task category | demo-small:q4 | demo-big:q4 | mock:echo | Decision (chosen local model) |
|---|---|---|---|---|
| Summarise to N points | ~ 3/5 (fa 2/3 · en 1/2) | ✓ 5/5 (fa 3/3 · en 2/2) | ✓ 5/5 (fa 3/3 · en 2/2) | offline |
| Extract fields to JSON | ~ 3/5 (fa 1/2 · en 2/3) | ✓ 4/5 (fa 1/2 · en 3/3) | ✓ 5/5 (fa 2/2 · en 3/3) | offline |
| Answer from a passage | ~ 3/5 (fa 2/3 · en 1/2) | ✓ 4/5 (fa 2/3 · en 2/2) | ✓ 5/5 (fa 3/3 · en 2/2) | offline |
| Translate fa↔en | ✓ 4/5 (fa 2/2 · en 2/3) auto | ✓ 4/5 (fa 1/2 · en 3/3) owner+auto | ✓ 5/5 (fa 2/2 · en 3/3) auto | offline |
| Classify tone or topic | ✓ 4/5 (fa 2/3 · en 2/2) | ✓ 5/5 (fa 3/3 · en 2/2) | ✓ 5/5 (fa 3/3 · en 2/2) | offline |
| No-go: multi-step / long text | ✗ 2/5 (fa 0/2 · en 2/3) | ~ 3/5 (fa 1/2 · en 2/3) | ✓ 4/5 (fa 2/2 · en 2/3) | offline + human check |
| All 30 tasks | 19/30 (fa 9/15 · en 10/15) | 25/30 (fa 11/15 · en 14/15) | 29/30 (fa 15/15 · en 14/15) |  |
| Median time to first token | 0.0 s | 0.1 s | not streamed |  |
| Median total time per task | 0.1 s | 0.2 s | 0.0 s |  |
| Tokens per second (median) | 50 | 23 | n/a |  |
| Peak memory (RSS / Ollama) | 0.1 GB / 1.5 GB | 0.1 GB / 3.6 GB | — |  |
| Swap growth during run | 0.0 GB | 0.1 GB | — |  |
| On disk · quantization | 1.3 GB · Q4_K_M | 3.1 GB · Q4_K_M | cloud |  |
| Cold load (first request) | 0.2 s | 0.4 s | — |  |

✓ 4–5 of 5 pass → keep offline · ~ 3 of 5 (or ✓ but median over 30 s) → offline + a person checks · ✗ 0–2 of 5 → stronger model.
"auto" on translation = required-terms check only; the owner's blind sheet replaces it.
Rules written 2026-11-23 · sha256 at run: rules.json 6e742626da5c · task_bank.py 768aa87fc282 · graders.py 709ca55cf040 · not committed when run
Online: mock:echo, max_tokens 1024, effort low, provider-default temperature; 0 row(s) with a retry left out of the median time.
Boundary: one laptop, 30 synthetic tasks, these models, this date. Offline is not the same as secure. Online timing includes the network.
