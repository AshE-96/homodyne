# E03 · Sources

Checked 29 September 2026. The Vectara leaderboard is live — re-check on the recording day.

## Primary — at the centre of the episode

1. **Bean, A. M., Kearns, R. O., Romanou, A. et al.** *Measuring what Matters: Construct Validity in
   Large Language Model Benchmarks.* NeurIPS 2025 D&B. arXiv [2511.04703](https://arxiv.org/abs/2511.04703)
   — 445 benchmarks, 29 reviewers; 78.2% define the phenomenon; of those 47.8% contested or undefined
   (reasoning 18.5% of benchmarks, alignment 8.1%); 53.4% justify construct validity; 16.0% use
   statistical tests; eight recommendations (define the phenomenon · measure only it · representative
   dataset · limits of reuse · prepare for contamination · statistics · error analysis · justify validity).

2. **Jacobs, A. Z. & Wallach, H.** *Measurement and Fairness.* FAccT 2021. arXiv [1912.05511](https://arxiv.org/abs/1912.05511)
   — measurement models link unobservable constructs to observable properties; construct reliability
   (test–retest) and seven aspects of construct validity: face, content, convergent, discriminant,
   predictive, hypothesis, consequential.

3. **Kalai, A. T. et al.** *Why Language Models Hallucinate.* OpenAI, 2025. arXiv [2509.04664](https://arxiv.org/abs/2509.04664)
   — §4.2: explicit confidence targets, penalty t/(1−t); "behavioral calibration" — answer only when at
   least t confident; observed behaviour rather than a stated probability.

## The three "hallucination rates"

- **Vectara.** *Hallucination Leaderboard*, HHEM-2.3. Updated 11 May 2026.
  [GitHub](https://github.com/vectara/hallucination-leaderboard/) — summarisation of a given document;
  rate = 100 − factual-consistency rate; lowest 1.8%, highest 24.2% among listed models.
- **OpenAI / Kalai et al. 2025** — SimpleQA: o4-mini error 75% of all questions (GPT-5 System Card).
- **Artificial Analysis.** *AA-Omniscience.* Nov 2025. arXiv [2511.13029](https://arxiv.org/abs/2511.13029)
  — hallucination rate = i / (p + i + a); Grok 4 and GPT-5 (high) at 39% accuracy with 64% and 81%;
  three of 36 models above zero on the Omniscience Index.

## Neighbours and "why not simpler"

- **OpenAI.** *GPT-4 Technical Report.* 2023. arXiv [2303.08774](https://arxiv.org/abs/2303.08774) — Fig. 8:
  "the pre-trained model is highly calibrated … after the post-training process, the calibration is reduced" (MMLU subset).
- **Kirichenko, P., Ibrahim, M., Chaudhuri, K., Bell, S. J.** *AbstentionBench: Reasoning LLMs Fail on
  Unanswerable Questions.* 2025. arXiv [2506.09038](https://arxiv.org/abs/2506.09038) — 20 datasets, 20 models;
  reasoning fine-tuning degrades abstention by 24% on average; scale helps little.
- **Salaudeen, O. et al.** *Measurement to Meaning: A Validity-Centered Framework for AI Evaluation.* 2025.
  arXiv [2505.10573](https://arxiv.org/abs/2505.10573) — background reading: math-test score vs "ability to reason".

## Framework

- `framework/schemas/benchmark-spec.schema.json` — `known_gaps` minItems 1; new optional
  `system_selection` and `validity_argument` (Part 02 v2).
- `examples/bluff-v1/spec.yaml` — validates against the schema with 0 errors (29 Sep 2026).
