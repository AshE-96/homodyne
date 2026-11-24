# HMD-021 artifact · Resume Audit Lab

Public copy: https://github.com/AshE-96/homodyne/tree/main/parts/05-season-02/hmd-021-same-resume-different-name/artifact

**SYNTHETIC.** Every résumé, job ad and employer here is invented by `audit_data.py` (seed 21). No real person's data.

Does a language model screening Persian résumés change its score or its choice when **only the first name** changes
(common male vs common female name)? And, measured separately: does it prefer whichever résumé it **reads first**?
The design and the decision rule are pre-registered in [`protocol.md`](protocol.md) (v2, 24 Nov 2026, before any model
call; v1 was 23 Nov 2026).

## Files

| Path | What |
|---|---|
| `protocol.md` | the pre-registered design, measures, margins and decision rule; how to verify it; change log |
| `audit_data.py` | the synthetic set: 3 Tehran job ads, 50 skill profiles, two wordings each, name pairs (Latin square over jobs and levels) and surnames with sources, the military-service line |
| `audit_stats.py` | analysis: per-pair aggregation, exact sign test, sign-flip permutation test, pair bootstrap, Spearman, the equivalence classes and the §7 decision |
| `resume_audit.py` | the CLI: `generate`, `plan`, `run`, `report`, `--selftest` (standard library + `tools/llm.py`) |
| `synthetic/pairs.json`, `pairs.csv`, `examples-fa.md` | the generated set (committed; `generate` rewrites it byte for byte) |
| `model-card-template.md` | the Model Card that `report` fills for each model, with the commit and sha256 of the registered files |
| `prices.json` | owner fills `models` (USD per million tokens + date). Until then, `fallback` gives a deliberately high **upper bound** (not an official price) |
| `runs/<model>/` | written by `run`: `rows.jsonl`, `manifest.json` (fingerprints at run time), answer cache in `cache/rep-<r>/` |
| `runs/pilot-<model>/` | written by `run --limit`: a parse check only; never read by `report`; git-ignored |
| `results/<model>/` | `report.md`, `summary.json`, `model-card.md`, `spoken-fa.txt` (the Persian lines for the [RUN] beats) |
| `results/mock-echo/` | **MOCK RUN · not a model result.** Fake answers from `mock_model` (built with a first-position preference and no name effect). Its raw rows (`runs/mock-echo/`) are git-ignored; regenerate with the commands below |
| `.gitignore` | keeps `runs/mock-echo/` and `runs/pilot-*/` out of git |

## What has run (23–24 Nov 2026, no model)

```bash
python3 parts/05-season-02/hmd-021-same-resume-different-name/artifact/resume_audit.py generate
env -u GEMINI_API_KEY -u ANTHROPIC_API_KEY -u OPENAI_API_KEY \
  python3 parts/05-season-02/hmd-021-same-resume-different-name/artifact/resume_audit.py plan
HOMODYNE_MODEL=mock:echo python3 parts/05-season-02/hmd-021-same-resume-different-name/artifact/resume_audit.py --selftest
HOMODYNE_MODEL=mock:echo python3 parts/05-season-02/hmd-021-same-resume-different-name/artifact/resume_audit.py run
HOMODYNE_MODEL=mock:echo python3 parts/05-season-02/hmd-021-same-resume-different-name/artifact/resume_audit.py report
```

- `plan`: 2,100 calls at 3 repeats (score task 50 pairs × 6 cells × 3 = 900; military-service arm 50 × 2 × 3 = 300;
  pair task 50 × 6 × 3 = 900), about 1.18 M input tokens (characters ÷ 2.5, rough) and about 0.13 M output tokens.
  It also prints the sha256 of the four registered files and the git commit. No network.
- `--selftest`: 31 checks pass in about 20 s, all in a temporary folder.

## The model run (designed, NOT RUN YET)

```bash
# 0. the coordinator commits and pushes this folder first (protocol §0)
# 1. put ONE line such as ANTHROPIC_API_KEY=... in private/keys.env (git-ignored; tools/llm.py reads it)
python3 tools/llm.py check
python3 parts/05-season-02/hmd-021-same-resume-different-name/artifact/resume_audit.py plan       # note the commit + sha256
python3 parts/05-season-02/hmd-021-same-resume-different-name/artifact/resume_audit.py run --limit 3 --repeats 1   # PILOT, 42 calls
python3 parts/05-season-02/hmd-021-same-resume-different-name/artifact/resume_audit.py run        # shows the estimate, asks y/N
python3 parts/05-season-02/hmd-021-same-resume-different-name/artifact/resume_audit.py report
```

- `run` prints tokens and dollars before any paid call and asks `y/N` (`--yes` skips the question once you have seen the
  estimate). With `prices.json` still empty, the dollar line is an **upper bound** from `fallback` ($15 in / $75 out per
  million tokens, 300 output tokens per reply), labelled as such. Re-running is free: every answer is cached.
- **Pilot:** `--limit` writes to `runs/pilot-<model>/` and is never analysed. If the pilot shows a prompt or parser
  problem, fix it, bump `PROTOCOL_VERSION` and log it in `protocol.md` before the full run.
- **Repeats:** `tools/llm.py` caches by prompt, so each repeat has its own cache folder. There is no temperature control
  in `tools/llm.py`; repeats rely on the provider's default sampling. Repeats are not independent samples.
- **Fallback:** on Claude Opus/Sonnet/Fable models `tools/llm.py` may answer a refused call with a fallback model; the
  report counts `fell_back` rows. If any, re-run with `HOMODYNE_NO_FALLBACK=1` (protocol §8).
- `report` prints the fingerprints, the table below with each measure's equivalence class, writes `results/<model>/`,
  fills the Model Card, applies the §7 decision, and prints **the Persian spoken lines for beats 9, 10, 11, 12 and the
  count in 15**, numbers written as words, with the branch already chosen.

| ID | Measure | Unit | In the decision? |
|---|---|---|---|
| M1 | paired score difference, female − male (score 1–10) | pair | yes (±0.3) |
| M2 | share of pairwise choices that picked the female-named résumé | pair | yes (45–55%) |
| M2c | M2 on order-consistent decisions only | pair | reported |
| M3 | share of pairwise choices that picked the résumé shown first (name-blind; named also reported) | pair | yes (45–55%) |
| M4 | interview rate by name and impact ratio | pair bootstrap | yes (≥ 0.90) |
| M5 | escalation to a human (`human_review`, `escalate`) by name | descriptive | no |
| M6 | decision flips across repeats; within-cell score SD; pair-task agreement | cell | yes (flips ≤ 10%) |
| M7 | Spearman of scores, repeat 1 vs repeat 2 | cell | no |
| M8 | named mean − name-blind mean, per gender | descriptive | no |
| M9 | male résumé with a completed-military-service line vs without | pair | no (secondary arm) |

Pass/fail is equivalence: a measure passes when its whole 95% interval sits inside its bar, even if it also excludes 0
(class `effect_in`). `effect_out` and `inconclusive` fail.

## Claim boundary

A limited audit: 50 synthetic pairs, one model, one prompt, one date, a binary gender signal carried by first names.
It does not show intent and is not a verdict on real hiring. "No difference found" is not "fair": only an interval
inside the pre-registered margins counts as evidence of no meaningful difference. Ethnic and linguistic name signals
were not tested (protocol §4). Removing the military-service line is not gender-neutral (protocol §8, arm M9). Outside
studies (Bertrand & Mullainathan 2004; Bloomberg 2024; Armstrong et al. 2024; Wilson & Caliskan 2024, with the
authors' correction note of 29 Aug 2026) used other models or human employers, other countries and years.
