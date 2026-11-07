# Claim Check — six questions before you believe a score

*Homodyne · Part 02 · E01 · print on one page, keep next to your screen*

> A score is the output. The benchmark is the contract that produced it.
> If you can't answer one of these, you don't know what the number says — you know that you don't know.

| # | Ask | What a good answer names | Red flag |
|---:|---|---|---|
| 1 | **Decision** — which decision is this number meant to inform? | A user, a task, a choice between options | "General capability", "overall intelligence" |
| 2 | **Construct** — what quality is claimed, and what does the proxy miss? | The quality (e.g. *reliability*) and the proxy's known gaps | The benchmark's name used as the definition |
| 3 | **Items** — which questions, from where, in which language — and could the model have seen them? | Source, sampling, language, date, contamination checks | Public items, no canary, no date, English only presented as "multilingual" |
| 4 | **Protocol** — how was it run, how many times, who graded? | Prompt, settings, repeats, grader and its agreement with humans | "Best of N" hidden, different prompts per model, unvalidated LLM judge |
| 5 | **Scoring** — what earns a point, what costs one, and is "I don't know" worth anything? | The rule, written down before the run | Accuracy only, in a setting where a confident wrong answer is expensive |
| 6 | **Uncertainty & boundary** — how big is the error bar, and what does the result *not* show? | Interval or test; an explicit list of non-claims | Ranks without intervals; a headline broader than the items |

---

**Fill-in**

```
Benchmark / table:                          Date read:
Decision it claims to inform:
1 Decision      ☐ answered  ☐ unclear  ☐ missing
2 Construct     ☐ answered  ☐ unclear  ☐ missing
3 Items         ☐ answered  ☐ unclear  ☐ missing
4 Protocol      ☐ answered  ☐ unclear  ☐ missing
5 Scoring       ☐ answered  ☐ unclear  ☐ missing
6 Uncertainty   ☐ answered  ☐ unclear  ☐ missing
What I will and will not conclude from it:
```

Do not add up the boxes. `unclear` and `missing` are not failures and not passes — they are the
parts of the claim you are being asked to take on trust.

---

Sources behind the questions: Kalai et al., *Why Language Models Hallucinate* (2025) — scoring ·
Bean et al., *Measuring what Matters* (NeurIPS 2025) — construct, items, statistics ·
NIST AI 800-2 ipd (2026) — protocol and reporting. Full list: [`../sources.md`](../sources.md)

Licence: CC BY-NC-SA 4.0 · Homodyne — Mohammad Mehdi Ghanbari
