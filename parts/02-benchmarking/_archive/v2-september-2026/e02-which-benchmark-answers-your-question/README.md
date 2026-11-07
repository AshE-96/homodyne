# E02 · Which benchmark answers your question?

`HMD-004` · Homodyne Part 02 (v2) · Episode 02 of 9 · airs Thu 22 Oct 2026 (30 Mehr 1405), 18:00 Tehran · Stage 0

> **A model has a profile, not a rank — and every benchmark has a shelf life.**

Humanity's Last Exam launched in January 2025 with frontier models under 10%; a year later the
AI Index reported 38.3% and wrote that "evaluations intended to be challenging for years are
saturated in months." This episode answers the two questions E01 left open: which benchmark
answers *your* question, and why some of them expire.

Two lenses: **what it measures** (16 families on two axes, each with its blind spot) and
**where it is in its life** (fresh → discriminating → saturating → saturated · compromised →
retired). Evidence: Arena's own style-control analysis, 29 of 60 benchmarks saturated, OpenAI
retiring SWE-bench Verified, GSM1k, MMLU-Pro. Then the selection rule —
*decision → costly failure → required evidence → family* — run on the course question, with the
exclusions that matter most.

| File | What it is |
|---|---|
| [`script-fa.md`](script-fa.md) | Recording script (Persian), 17 beats, continuity table, clips, packaging, fact-check |
| [`deck.html`](deck.html) | Recording deck, Editorial v2, 17 frames + thumbnail · `→`/`←` · `N` script · `G` safe areas · `A` whole frame · `F` full screen |
| [`sources.md`](sources.md) | Primary sources, checked 29 Sep 2026 |
| [`artifact/landscape-card.md`](artifact/landscape-card.md) | Five questions, two axes, six lifecycle states — one page |
| [`artifact/family-selection-bluff.md`](artifact/family-selection-bluff.md) | Stage 0 for `bluff-v1`: the chain, the exclusions, the lifecycle check on the anchor data |

**Framework changes made for this episode:** `framework/00-landscape/benchmark-families.yaml`
v2.0.0 — two new families (`calibration_abstention`, `multilingual_cultural`), a fifth dissection
question, a dated `lifecycle` block, and the bluff-v1 worked example. New command:
`python3 -m m2bench families --lifecycle`.

**Claim boundary.** The map is a mental model, not a taxonomy. Lifecycle states are dated
(29 Sep 2026). A saturated benchmark is not useless — it just cannot choose between today's
frontier systems.

**Previous:** [E01 · Is a higher score a better model?](../e01-is-a-higher-score-better/) ·
**Next:** [E03 · What exactly are we measuring?](../e03-what-exactly-are-we-measuring/) — the spec,
frozen as `spec-v0.1` on the day this episode airs.
