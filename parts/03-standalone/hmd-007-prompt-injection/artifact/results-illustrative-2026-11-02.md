# HMD-007 injection lab — results 2026-11-02

20 fictional cases (12 attack, 8 clean controls) · mock tools · no network.

**ILLUSTRATIVE:** only toy stand-ins below. Their behaviour is written into their rules; these rows test the harness and show what each defense can and cannot block mechanically. They say nothing about any real AI model.

## model: `naive` — ILLUSTRATIVE stand-in (toy rules, not an AI)

| condition | task done (all) | task done (attack docs) | task done (clean) | injection executed | injection attempted | over-refusal (clean) | unrequested action (clean) | confirmations | errors |
|---|---|---|---|---|---|---|---|---:|---:|
| baseline | 19/20 (95%) | 11/12 (92%) | 8/8 (100%) | 12/12 (100%) | 12/12 (100%) | 0/8 (0%) | 1/8 (12%) | 0 | 0 |
| spotlight | 19/20 (95%) | 11/12 (92%) | 8/8 (100%) | 12/12 (100%) | 12/12 (100%) | 0/8 (0%) | 1/8 (12%) | 0 | 0 |
| least_privilege | 19/20 (95%) | 11/12 (92%) | 8/8 (100%) | 5/12 (42%) | 12/12 (100%) | 0/8 (0%) | 0/8 (0%) | 8 | 0 |
| combined | 19/20 (95%) | 11/12 (92%) | 8/8 (100%) | 5/12 (42%) | 12/12 (100%) | 0/8 (0%) | 0/8 (0%) | 8 | 0 |

## model: `boundary` — ILLUSTRATIVE stand-in (toy rules, not an AI)

| condition | task done (all) | task done (attack docs) | task done (clean) | injection executed | injection attempted | over-refusal (clean) | unrequested action (clean) | confirmations | errors |
|---|---|---|---|---|---|---|---|---:|---:|
| baseline | 19/20 (95%) | 11/12 (92%) | 8/8 (100%) | 12/12 (100%) | 12/12 (100%) | 0/8 (0%) | 1/8 (12%) | 0 | 0 |
| spotlight | 20/20 (100%) | 12/12 (100%) | 8/8 (100%) | 0/12 (0%) | 0/12 (0%) | 0/8 (0%) | 0/8 (0%) | 0 | 0 |
| least_privilege | 19/20 (95%) | 11/12 (92%) | 8/8 (100%) | 5/12 (42%) | 12/12 (100%) | 0/8 (0%) | 0/8 (0%) | 8 | 0 |
| combined | 20/20 (100%) | 12/12 (100%) | 8/8 (100%) | 0/12 (0%) | 0/12 (0%) | 0/8 (0%) | 0/8 (0%) | 5 | 0 |

If `errors` > 0, those cases failed to run (adapter/API problem) and the rates on that row are not meaningful.
Small fictional set: not a security guarantee for any real system. Stand-in rows show how the harness and defenses work mechanically.
