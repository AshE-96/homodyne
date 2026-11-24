# HMD-023 · simulated service results

**SIMULATED SERVICE (ILLUSTRATIVE)**

- date: 2026-11-24T04:09:58
- target: fake_server.py on 127.0.0.1
- hardware: {'chip': 'Apple M1', 'ram_gb': 8, 'os': 'macOS-27.2-arm64-arm-64bit', 'python': '3.11.7', 'power': "Now drawing from 'AC Power'"}
- load pattern: {"in_range": [80, 240], "out_range": [40, 200], "think": 20.0, "duration": 120.0, "ramp": 10.0, "timeout": 30.0, "slo_ttft": 3.0, "sample_every": 0.5}

- simulated service parameters: {"slots": 4, "prefill_tps": 600.0, "decode_tps": 80.0, "contention": 0.1, "cold_load": 4.0, "max_queue": 512, "degrade_at": 0, "degrade_tokens": 40}
- timescale: 0.25

## Cold vs warm (first word, seconds)

| try | cold | warm |
|---|---|---|
| 1 | 4.23 | 0.22 |
| 2 | 4.23 | 0.23 |
| 3 | 4.23 | 0.22 |

cold (try 1) 4.23 s · median warm 0.22 s · on a real laptop only try 1 is truly cold from disk; tries 2-3 may hit the OS file cache

## Closed loop: virtual users

| load | sent | ok | timeout (of which first word seen) | busy 503 | first word p50 | p95 | full answer p50 | p95 | within SLO | SLO | answers/s (real span) | span s | mean waiting | max streaming |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 users | 6 | 6 | 0 (0) | 0 | 0.24 | 0.39 | 1.59 | 2.16 | 100% | kept | 0.06 | 108.94 | 0.02 | 1 |
| 10 users | 59 | 59 | 0 (0) | 0 | 0.32 | 0.43 | 2.15 | 3.08 | 100% | kept | 0.48 | 122.74 | 0.15 | 4 |
| 25 users | 164 | 164 | 0 (0) | 0 | 0.38 | 4.27 | 2.42 | 6.39 | 90% | broken | 1.36 | 120.25 | 1.45 | 4 |
| 50 users | 224 | 224 | 0 (0) | 0 | 11.05 | 15.95 | 13.12 | 18.20 | 5% | broken | 1.73 | 129.50 | 17.69 | 4 |
| 100 users | 317 | 226 | 91 (70) | 0 | 26.14 | >timeout | 27.95 | >timeout | 3% | broken | 1.52 | 148.93 | 50.63 | 4 |

## Open loop: requests per second

| load | sent | ok | timeout (of which first word seen) | busy 503 | first word p50 | p95 | full answer p50 | p95 | within SLO | SLO | answers/s (real span) | span s | mean waiting | max streaming |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 req/s | 66 | 66 | 0 (0) | 0 | 0.33 | 0.99 | 1.97 | 3.40 | 100% | kept | 0.55 | 121.09 | 0.17 | 4 |
| 1 req/s | 121 | 121 | 0 (0) | 0 | 0.33 | 2.45 | 2.22 | 4.78 | 96% | kept | 0.99 | 122.15 | 0.66 | 4 |
| 1.25 req/s | 150 | 150 | 0 (0) | 0 | 0.35 | 3.00 | 2.29 | 5.63 | 95% | kept | 1.26 | 118.87 | 1.03 | 4 |
| 1.5 req/s | 184 | 184 | 0 (0) | 0 | 0.93 | 4.17 | 3.00 | 6.38 | 86% | broken | 1.51 | 121.61 | 2.02 | 4 |
| 1.75 req/s | 208 | 208 | 0 (0) | 0 | 2.14 | 4.74 | 3.87 | 6.81 | 66% | broken | 1.71 | 121.70 | 3.75 | 4 |
| 2 req/s | 229 | 229 | 0 (0) | 0 | 6.54 | 12.46 | 8.25 | 14.56 | 9% | broken | 1.81 | 126.63 | 12.20 | 4 |

Highest arrival rate that kept the SLO: 1.25 req/s

Little's law check (L = lambda x W, over each stage window):

| load | L measured | lambda x W |
|---|---|---|
| 0.5 req/s | 1.08 | 1.11 |
| 1 req/s | 2.39 | 2.39 |
| 1.25 req/s | 3.34 | 3.32 |
| 1.5 req/s | 4.88 | 4.90 |
| 1.75 req/s | 6.91 | 6.91 |
| 2 req/s | 15.62 | 15.66 |

## 100 users, four policies (chosen by us; the fake service and its slot contention are a model, not a measurement)

| policy | sent | ok | busy 503 | timeout (of which first word seen) | within SLO | first word p95 | first word p95, answered only | answers/s (real span) | mean answer tokens | shortened | slot-seconds per success |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 317 | 225 | 0 | 92 (71) | 3% | >timeout | 28.24 | 1.51 | 117.37 | 0% | 2.65 |
| bounded queue (4) | 625 | 218 | 407 | 0 (0) | 31% | >timeout | 3.23 | 1.76 | 121.75 | 0% | 2.27 |
| bounded queue + short answers | 626 | 376 | 250 | 0 (0) | 60% | >timeout | 2.07 | 3.07 | 62.41 | 71% | 1.30 |
| double slots, same hardware (sim) | 375 | 365 | 0 | 10 (10) | 3% | 25.51 | 23.79 | 2.71 | 121.71 | 0% | 2.96 |
