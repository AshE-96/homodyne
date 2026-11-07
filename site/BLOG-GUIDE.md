# Homodyne blog: writing guide

Every recorded episode gets two posts, each in Persian and English (4 files):

| kind | What it is | Length (fa) |
|---|---|---|
| `companion` | The episode's question, answered in writing for someone who has not watched it. Answer first, then the mechanism, the claim boundary, and sources. | 900–1,400 words |
| `deep-dive` | The layer the video skips: datasets (link, licence, size, update cadence), method and statistics, how to reproduce with the episode's `artifact/` (exact commands), limitations, further reading. | 1,300–2,200 words |

Persian is canonical and written natively, in **written (formal-light) Persian**, not the colloquial voice of the video. English is an adaptation for a global reader, not a literal translation; Iranian-specific references get one line of context.

## Files

```
site/src/content/blog/fa/<slug>.md
site/src/content/blog/en/<slug>.md      # same <slug>, same translationKey
```

`<slug>`: short English kebab case starting with the episode, e.g. `hmd-005-persian-token-tax`, `hmd-005-tokenizer-methods`.

## Frontmatter

```yaml
---
title: "…"                 # ≤ 60 characters, keyword first, question form welcome
description: "…"           # 120–155 characters, answers the question
lang: fa                   # fa | en
translationKey: hmd-005-companion   # identical in the fa and en twin
hmd: HMD-005
kind: companion            # companion | deep-dive
date: 2026-12-18           # the episode's release date (see table below)
tags: ["tokenizer", "…"]
sources:                   # every source cited in the body, primary first
  - title: "…"
    url: "https://…"
datasets:                  # deep-dive: every dataset/tool used (optional for companion)
  - title: "…"
    url: "https://…"
    license: "CC BY 4.0"
---
```

Posts are scheduled: a post appears on the site when its `date` has arrived and the site is rebuilt, so run `make deploy` on each release day.

| HMD | date | | HMD | date |
|---|---|---|---|---|
| 002 | 2026-11-27 | | 007 | 2027-01-01 |
| 003 | 2026-12-04 | | 008 | 2027-01-08 |
| 004 | 2026-12-11 | | 009 | 2027-01-15 |
| 005 | 2026-12-18 | | 010 | 2027-01-22 |
| 006 | 2026-12-25 | | G01 | 2027-01-29 |

## Rules (non-negotiable)

1. **Every number comes from the episode's `sources.md`, a real artifact result file, or a link you verified.** Never invent, round differently, or "update" a number. Nothing tagged `[RUN]`/`[VERIFY]`, nothing from an experiment that has not run (007 real-model run, 010 four-condition run, 008 pilot audit, 003 FIRMS timeline): say plainly it has not run yet.
2. Simulated or made-up data is labelled **ILLUSTRATIVE** in the text and in any chart.
3. Every post has a **claim-boundary** section ("What this does not show" / «این چه چیزی را نشان نمی‌دهد»).
4. Answer-first: the first paragraph answers the title question in 2–3 sentences.
5. H2s are real sub-questions; no keyword stuffing; no hype words (revolutionary, game-changing, انقلابی، باورنکردنی).
6. Internal links: the episode page `/<lang>/episodes/<hmd-slug>/` (e.g. `/fa/episodes/hmd-005/`), the twin post, and where natural one other Homodyne post or episode.
7. Code blocks are runnable from the repo root, e.g. `python3 parts/03-standalone/hmd-005-persian-tokens/artifact/count_tokens.py`.
8. Charts only from real result files (e.g. `results-*.json`), as small inline `<svg>` with `role="img"` and `<title>`; colours `#E8A33D` (accent) and `currentColor`. Optional; at most one per post.
9. Quote sources only in short phrases (under 15 words).
