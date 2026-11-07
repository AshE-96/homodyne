# E01 · Sources

Checked 28 September 2026. Numbers from papers are quoted with the paper's date; anything taken
from a live leaderboard is re-checked on the recording day.

## Primary — at the centre of the episode

1. **Kalai, A. T., Nachum, O., Vempala, S. S., Zhang, E. et al.** *Why Language Models Hallucinate.*
   OpenAI, 5 September 2025. arXiv [2509.04664](https://arxiv.org/abs/2509.04664) ·
   [OpenAI post](https://openai.com/index/why-language-models-hallucinate/)
   — SimpleQA table (gpt-5-thinking-mini: abstention 52%, accuracy 22%, error 26%;
   OpenAI o4-mini: 1%, 24%, 75%; from the GPT-5 System Card) · birthday example ·
   Table 2 (10 evaluations, only WildBench gives partial credit for IDK) ·
   §4.2 explicit confidence targets, penalty t/(1−t) · "behavioral calibration".

2. **Artificial Analysis.** *AA-Omniscience: Evaluating Cross-Domain Knowledge Reliability in Large
   Language Models.* November 2025. arXiv [2511.13029](https://arxiv.org/abs/2511.13029)
   — 6,000 questions, 42 topics, 36 models; Omniscience Index = 100·(c − i)/(c + p + i + a);
   Grok 4 and GPT-5 (high) 39% accuracy with 64% / 81% hallucination rate; Claude 4.1 Opus
   highest index (4.8) at 36% accuracy; three models above zero.

3. **Bean, A. M., Kearns, R. O., Romanou, A. et al.** *Measuring what Matters: Construct Validity in
   Large Language Model Benchmarks.* NeurIPS 2025 Datasets & Benchmarks. arXiv
   [2511.04703](https://arxiv.org/abs/2511.04703)
   — 445 benchmarks, 29 reviewers; 16.0% used uncertainty estimates or statistical tests to compare
   results; eight recommendations.

## Computed by us

- `artifact/two_scores.py` — re-scores the published SimpleQA table under a wrong-answer penalty.
  Crossover at k = 2/49 ≈ 0.041 (t ≈ 3.9%); at k = 1: −51 vs −4 per 100 questions.
  **Re-scoring, not re-running.**

## Background — used for the course question

- Wei, J. et al. *Measuring short-form factuality in large language models* (SimpleQA). OpenAI, 2024.
  arXiv [2411.04368](https://arxiv.org/abs/2411.04368)
- Haas, L. et al. *SimpleQA Verified.* Google DeepMind, 2025. arXiv [2509.07968](https://arxiv.org/abs/2509.07968)
- Kirichenko, P. et al. *AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions.* 2025.
  arXiv [2506.09038](https://arxiv.org/abs/2506.09038)
- *MSQA: A Natively Sourced Multilingual and Multicultural SimpleQA Benchmark.* July 2026.
  arXiv [2607.00724](https://arxiv.org/abs/2607.00724) — 11 languages, no Persian.
- *PerHalluEval: Persian Hallucination Evaluation Benchmark.* LREC 2026.
  arXiv [2509.21104](https://arxiv.org/abs/2509.21104) — hallucination detection, not answering behaviour.
- NIST CAISI. *NIST AI 800-2 ipd: Practices for Automated Benchmark Evaluations of Language Models.*
  January 2026. [PDF](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf)

"We did not find a published benchmark that tests explicit confidence targets on native Persian
items" — true as of the date above, from the searches listed; not a claim to be first.
