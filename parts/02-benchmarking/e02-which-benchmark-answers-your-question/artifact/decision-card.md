# Decision card · from your costly failure to a benchmark

*Homodyne HMD-004 · Benchmark Lab E02 · one page. Fill it before you trust a leaderboard.*

## The four boxes

| Box | Ask | Shop assistant (worked example) | Yours |
|---|---|---|---|
| **Task** | What exactly will the model do? Answer, summarise, act with a tool? | Answer customers' questions about orders and returns | |
| **Costly failure** | Which mistake can you not afford? | A wrong refund policy, stated confidently | |
| **Evidence** | What observation would catch that mistake? | Correctness against a reference answer, plus whether it abstains when unsure | |
| **Test** | Which benchmark family produces that evidence? | Factuality + calibration/abstention (+ Persian slice if your users write Persian) | |

If you cannot fill **Evidence**, you are not ready to pick a model.

## The useful half: exclusions

| Famous evidence | Why it does not answer the shop decision |
|---|---|
| A vote-based leaderboard | Measures which answer people preferred; length and style move votes (LMSYS style-control analysis, Aug 2024). |
| Agent / tool-use benchmarks | Measure finishing actions in an environment; this assistant only answers. |
| Reasoning benchmarks | A high score says nothing about abstaining when unsure. |

## Try the selection tool — and watch the wording

From the repository root (no network, no model calls):

```bash
python3 -m m2bench families \
  --decision "customer support bot for my online shop" \
  --failure  "tells customers the wrong refund policy"
#  -> agents_tool_use, safety_security, robustness   (wrong for a bot that only answers)

python3 -m m2bench families \
  --decision "question answering assistant for my online shop" \
  --failure  "a confident wrong answer about refunds"
#  -> calibration_abstention, factuality, multilingual_cultural
#     NOT human_preference, reasoning, agents_tool_use
```

Same need, different words, different family. The tool is deliberately keyword-based
(`m2bench/families.py`, `select()`): it surfaces the chain and the exclusions; it does not decide.

## Before you trust the benchmark you picked

Five questions (see [landscape-card.md](landscape-card.md)): **Claim · Task · Metric · Blind spot · Life**.
For *Life*, check the date and any audit or retraction. Example: SWE-bench Verified was dropped by
OpenAI in Feb 2026 after an audit of 138 failing problems (at least 59.4% with flawed tests); its
suggested successor's recommendation was retracted in Jul 2026. Lifecycle states are dated claims.

Outputs shown above were checked on 2 Nov 2026.
