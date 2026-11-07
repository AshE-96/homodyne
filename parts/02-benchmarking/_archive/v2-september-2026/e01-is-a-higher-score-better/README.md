# E01 · Is a higher score a better model?

`HMD-002` · Homodyne Part 02 (v2) · Episode 01 of 9 · airs Thu 8 Oct 2026 (16 Mehr 1405), 18:00 Tehran

> **Same answers, two scoring rules, two winners.**

On SimpleQA, OpenAI's o4-mini answers 24% of questions correctly and gpt-5-thinking-mini 22%.
o4-mini "wins" — while getting 75% of questions wrong against 26%, because it almost never says
"I don't know". Penalise a wrong answer by just **0.04 points** and the winner flips.

The episode uses that one table to take apart what a benchmark is: not a score, but a
measurement contract of six parts — decision, construct, items, protocol, scoring rule and claim
boundary. It ends by opening the course's question, built in public over nine episodes:

> **When an AI doesn't know, does it say so — or does it bluff?** *…and does it bluff more in Persian?*

| File | What it is |
|---|---|
| [`script-fa.md`](script-fa.md) | Recording script (Persian), 16 beats, timings, clips, packaging, fact-check appendix |
| [`deck.html`](deck.html) | Recording deck, Homodyne Editorial v2, 16 frames + thumbnail. `→`/`←` step · `N` script · `G` safe areas · `F` full screen |
| [`sources.md`](sources.md) | Primary sources, checked 28 Sep 2026 |
| [`artifact/claim-check-card.md`](artifact/claim-check-card.md) | Six questions before you believe a score — one page |
| [`artifact/two_scores.py`](artifact/two_scores.py) | Re-scores published results under a wrong-answer penalty; finds the crossover |

**Claim boundary.** This episode does not say which model is better today, does not say accuracy
is useless, and does not say there is one correct scoring rule. Re-scoring published answers is
not the same as running models that were told the rule — that is what `bluff-v1` measures.

**Next:** [E02 · Which benchmark answers your question?](../e02-which-benchmark-answers-your-question/)
