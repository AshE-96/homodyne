# HMD-G01 collapse lab - seed 2026

**ILLUSTRATIVE.** Synthetic toy data. Shows the mechanism, not the size of any real-world effect.

## Experiment 1 - Gaussian (n = 100 per generation, 200 runs, medians)

True std = 1.000 · true mass beyond |x| > 2 = 4.55%

| generation | replace std | keep10 std | accumulate std | replace tail % | keep10 tail % | accumulate tail % |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1.003 | 0.985 | 0.990 | 4.71 | 4.39 | 4.39 |
| 1 | 0.984 | 0.974 | 0.992 | 4.39 | 4.15 | 4.45 |
| 10 | 0.904 | 0.950 | 0.984 | 3.67 | 3.99 | 4.32 |
| 50 | 0.599 | 0.941 | 0.981 | 0.37 | 4.24 | 4.30 |
| 100 | 0.371 | 0.922 | 0.984 | 0.00 | 3.42 | 4.31 |
| 200 | 0.139 | 0.946 | 0.986 | 0.00 | 3.83 | 4.34 |
| 500 | 0.007 | 0.935 | 0.984 | 0.00 | 3.84 | 4.30 |
| 1000 | 0.000 | 0.933 | 0.985 | 0.00 | 3.56 | 4.32 |

Share of runs whose fitted std fell below 0.5: replace 100%, keep10 0%, accumulate 0% (generation 1000).

## Experiment 2 - word frequencies (synthetic Zipf corpus (vocab 5000, 20000 tokens, s=1.0), 20 runs, medians)

Original distinct words: 3172 · rarest half = 1586 words

| generation | replace words | keep10 words | accumulate words | replace rare alive | keep10 rare alive | accumulate rare alive | replace eff. vocab | keep10 eff. vocab | accumulate eff. vocab |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 3172 | 3172 | 3172 | 1586 | 1586 | 1586 | 417 | 417 | 417 |
| 1 | 2550 | 2554 | 3172 | 1053 | 1058 | 1586 | 384 | 386 | 408 |
| 5 | 1535 | 1918 | 3172 | 470 | 662 | 1586 | 310 | 331 | 400 |
| 10 | 1076 | 1800 | 3172 | 278 | 604 | 1586 | 257 | 313 | 399 |
| 20 | 706 | 1760 | 3172 | 158 | 580 | 1586 | 206 | 304 | 397 |
| 50 | 370 | 1761 | 3172 | 68 | 574 | 1586 | 136 | 305 | 396 |
| 100 | 220 | 1774 | 3172 | 36 | 573 | 1586 | 99 | 310 | 396 |
