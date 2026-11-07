# E02 · Sources

Checked 29 September 2026. Lifecycle states are dated claims; re-check on the recording day.

## Primary — at the centre of the episode

1. **OpenAI.** *Why SWE-bench Verified no longer measures frontier coding capabilities.* 23 February 2026.
   [openai.com](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)
   — 138 failing tasks audited; 59.4% with material issues in tests or descriptions (35.5% narrow
   tests, 18.8% wide tests, 5.1% other); models reproduced gold patches; recommends SWE-bench Pro.

2. **Akhtar, M. et al.** *When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation.* 2026.
   arXiv [2602.16763](https://arxiv.org/abs/2602.16763)
   — 60 text-based LLM benchmarks; 29 with high or very high saturation (14 very high); saturation
   42.9% for benchmarks under 24 months old vs 54.5% for those over 60 months; no meaningful
   difference between public and private test sets; recommends lifecycle criteria for retirement.

3. **Stanford HAI.** *AI Index Report 2026*, Chapter 2 — Technical Performance. April 2026.
   [PDF](https://hai.stanford.edu/assets/files/ai_index_report_2026_chapter_2_technical.pdf)
   — "Evaluations intended to be challenging for years are saturated in months" (p. 71); HLE from
   under 10% to 38.3% between 2024 and 2025 (p. 95).

## Evidence used on screen

- **LMSYS.** *Does style matter? Disentangling style and substance in Chatbot Arena.* 29 Aug 2024.
  [lmsys.org](https://www.lmsys.org/blog/2024-08-28-style-control/) — length the dominant style
  factor; with style control GPT-4o-mini rank 6 → 11, Claude 3 Opus 16 → 10. Style control made the
  default leaderboard view in 2025 ([LMArena on X](https://x.com/arena/status/1923398953468678529)).
- **Zhang, H. et al.** *A Careful Examination of LLM Performance on Grade School Arithmetic* (GSM1k).
  NeurIPS 2024 D&B. arXiv [2405.00332](https://arxiv.org/abs/2405.00332) (v3: drops up to 8%; v1 said 13%).
- **Wang, Y. et al.** *MMLU-Pro.* NeurIPS 2024 D&B. arXiv [2406.01574](https://arxiv.org/abs/2406.01574)
  — 10 options; 16–33% lower accuracy than MMLU; prompt sensitivity 4–5% → 2%.
- **Haas, L. et al.** *SimpleQA Verified.* Google DeepMind, 2025. arXiv [2509.07968](https://arxiv.org/abs/2509.07968)
  — 1,000 prompts; fixes noisy labels, topical bias, redundancy.
- **Wei, J. et al.** *SimpleQA.* OpenAI, 2024. arXiv [2411.04368](https://arxiv.org/abs/2411.04368)
- **Phan, L. et al.** *Humanity's Last Exam.* 2025. arXiv [2501.14249](https://arxiv.org/abs/2501.14249)

## Behind the two new families

- **Singh, S. et al.** *Global-MMLU.* Cohere, 2024. arXiv [2412.03304](https://arxiv.org/abs/2412.03304)
  — 28% of MMLU questions culturally sensitive; 84.9% of geography questions North America/Europe; 42 languages incl. Persian.
- *MSQA: A Natively Sourced Multilingual and Multicultural SimpleQA Benchmark.* 2026.
  arXiv [2607.00724](https://arxiv.org/abs/2607.00724) — 11 languages, no Persian.
- **Kirichenko, P. et al.** *AbstentionBench.* 2025. arXiv [2506.09038](https://arxiv.org/abs/2506.09038)
- **Artificial Analysis.** *AA-Omniscience.* 2025. arXiv [2511.13029](https://arxiv.org/abs/2511.13029)

## Held for later episodes (not used here, on purpose)

- *The Leaderboard Illusion* (Singh et al. 2025) — Arena private testing → **E07**.
- *Fantastic Bugs and Where to Find Them in AI Benchmarks* (Truong et al., NeurIPS 2025; invalid
  question rates from 2% to 42% per AI Index 2026) and the FutureHouse HLE audit → **E04**.
