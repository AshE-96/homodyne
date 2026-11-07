# E03 · What exactly are we measuring?

`HMD-006` · Homodyne Part 02 (v2) · Episode 03 of 9 · airs Thu 5 Nov 2026 (14 Aban 1405), 18:00 Tehran · Stage 1

> **If you can't name what your proxy misses, you don't know what you measure.**

Two published "hallucination rates": 1.8% and 81%. Both are right — they are three different
formulas sharing one word (faithfulness to a given document; wrong ÷ all questions; wrong ÷
not-correct). Of 445 LLM benchmarks, 47.8% of those that define their phenomenon picked one with no
agreed definition, and only 53.4% argued that their number means what they claim.

This episode writes the first real file of `bluff-v1`: the specification. Decision, construct
(behavioural calibration under a stated penalty, after Kalai et al. 2025), the three neighbours it
is not, known gaps, task, unit, scope, the line of silence as baseline, a rule for choosing models
before their names are known, a six-part validity argument with falsification conditions, and the
claim boundary — frozen before any item exists.

| File | What it is |
|---|---|
| [`script-fa.md`](script-fa.md) | Recording script (Persian), 18 beats, continuity table, clips, packaging, fact-check |
| [`deck.html`](deck.html) | Recording deck, Editorial v2, 18 frames + thumbnail · `→`/`←` · `N` script · `G` safe areas · `A` whole frame · `F` full screen |
| [`sources.md`](sources.md) | Primary sources, checked 29 Sep 2026 |
| [`artifact/construct-card.md`](artifact/construct-card.md) | One page: name the construct, its proxies, its gaps, its neighbours |
| [`../../../examples/bluff-v1/spec.yaml`](../../../examples/bluff-v1/spec.yaml) | The spec itself — schema-valid, `draft` until the freeze on 22 Oct 2026 |
| [`../../../examples/bluff-v1/claim-boundary.md`](../../../examples/bluff-v1/claim-boundary.md) | What the result will and will not support, written now |

**Framework changes made for this episode:** `benchmark-spec.schema.json` and the Stage 1 template
gain two optional sections — `system_selection` (the rule before the names) and
`validity_argument` (claim · check · when · falsified_if). Existing specs stay valid.

**Recording gate:** record only after `spec.yaml` is `frozen` and tagged `spec-v0.1`, and after the
pilot (29 Oct). Any change the pilot forces is spoken as a change-log entry in beat 16.

**Previous:** [E02 · Which benchmark answers your question?](../e02-which-benchmark-answers-your-question/) ·
**Next:** E04 · Who decides the right answer? — the sampling grid, the pilot, and auditing the answer key.
