# HMD-011 · storm_replay results

Event: UT day with max planetary Kp >= 5- (4.667), NOAA G1 or stronger; truth = GFZ definitive Kp.  
Fit: 1996-01-01 .. 2017-12-31 (base rates only).  Test: 2018-01-01 .. 2025-12-31.

Scored test days: 2844 of 2922 (dropped 78 without all three NOAA leads). Storm days: 315 (11.1%). Fit-period storm rate: 14.4%. Storm episodes (runs of storm days): 191.

## Brier score (lower is better) and skill vs climatology

| forecaster | Brier | skill | mean forecast |
|---|---:|---:|---:|
| climatology | 0.0996 | +0.000 | 0.144 |
| always_warn | 0.8892 | -7.928 | 1.000 |
| recurrence_27d | 0.0964 | +0.032 | 0.138 |
| persistence_d1 | 0.0913 | +0.083 | 0.134 |
| persistence_d2 | 0.1000 | -0.004 | 0.139 |
| persistence_d3 | 0.1003 | -0.007 | 0.141 |
| noaa_d3 | 0.0908 | +0.089 | 0.096 |
| noaa_d2 | 0.0887 | +0.110 | 0.112 |
| noaa_d1 | 0.0845 | +0.152 | 0.124 |

## Block bootstrap of Brier skill (95% interval)

| comparison | skill | 95% interval |
|---|---:|---|
| noaa_d1_vs_climatology | +0.152 | +0.110 .. +0.198 |
| noaa_d1_vs_persistence_d1 | +0.075 | +0.028 .. +0.125 |
| noaa_d3_vs_persistence_d3 | +0.095 | +0.060 .. +0.134 |
| noaa_d3_vs_climatology | +0.089 | +0.053 .. +0.129 |

## Reliability: when the forecast said p, how often did it happen?

**noaa_d1**

| forecast bin | days | mean forecast | observed |
|---|---:|---:|---:|
| 0-9% | 1688 | 4.0% | 3.8% |
| 10-19% | 598 | 12.7% | 12.0% |
| 20-29% | 152 | 23.5% | 21.1% |
| 30-39% | 202 | 31.1% | 28.2% |
| 40-59% | 126 | 45.3% | 34.9% |
| 60-100% | 78 | 69.7% | 59.0% |

**noaa_d2**

| forecast bin | days | mean forecast | observed |
|---|---:|---:|---:|
| 0-9% | 1780 | 4.0% | 4.8% |
| 10-19% | 604 | 12.9% | 15.1% |
| 20-29% | 140 | 23.5% | 22.1% |
| 30-39% | 158 | 31.0% | 25.9% |
| 40-59% | 101 | 45.0% | 31.7% |
| 60-100% | 61 | 67.5% | 55.7% |

**noaa_d3**

| forecast bin | days | mean forecast | observed |
|---|---:|---:|---:|
| 0-9% | 1904 | 4.0% | 6.5% |
| 10-19% | 570 | 12.8% | 14.2% |
| 20-29% | 132 | 23.6% | 17.4% |
| 30-39% | 134 | 31.0% | 30.6% |
| 40-59% | 70 | 44.3% | 37.1% |
| 60-100% | 34 | 62.5% | 58.8% |

**persistence_d1**

| forecast bin | days | mean forecast | observed |
|---|---:|---:|---:|
| 10-19% | 2555 | 10.1% | 8.1% |
| 40-59% | 289 | 42.8% | 37.4% |

## Warnings at threshold 30.0%

| forecaster | hits | misses | false alarms | hit rate | false-alarm ratio | warning days/yr | false alarms/yr |
|---|---:|---:|---:|---:|---:|---:|---:|
| noaa_d1 | 147 | 168 | 259 | 46.7% | 63.8% | 52.1 | 33.3 |
| noaa_d2 | 107 | 208 | 213 | 34.0% | 66.6% | 41.1 | 27.4 |
| noaa_d3 | 87 | 228 | 151 | 27.6% | 63.4% | 30.6 | 19.4 |
| persistence_d1 | 108 | 207 | 181 | 34.3% | 62.6% | 37.1 | 23.2 |
| recurrence_27d | 81 | 234 | 228 | 25.7% | 73.8% | 39.7 | 29.3 |
| always_warn | 315 | 0 | 2529 | 100.0% | 88.9% | 365.2 | 324.8 |

### noaa d1 by threshold

| threshold | hits | misses | false alarms | hit rate | false alarms/yr | missed storm days/yr |
|---:|---:|---:|---:|---:|---:|---:|
| 5.0% | 296 | 19 | 1717 | 94.0% | 220.5 | 2.4 |
| 10.0% | 251 | 64 | 905 | 79.7% | 116.2 | 8.2 |
| 20.0% | 179 | 136 | 379 | 56.8% | 48.7 | 17.5 |
| 30.0% | 147 | 168 | 259 | 46.7% | 33.3 | 21.6 |
| 50.0% | 61 | 254 | 51 | 19.4% | 6.5 | 32.6 |

### noaa d3 by threshold

| threshold | hits | misses | false alarms | hit rate | false alarms/yr | missed storm days/yr |
|---:|---:|---:|---:|---:|---:|---:|
| 5.0% | 274 | 41 | 1621 | 87.0% | 208.2 | 5.3 |
| 10.0% | 191 | 124 | 749 | 60.6% | 96.2 | 15.9 |
| 20.0% | 110 | 205 | 260 | 34.9% | 33.4 | 26.3 |
| 30.0% | 87 | 228 | 151 | 27.6% | 19.4 | 29.3 |
| 50.0% | 29 | 286 | 20 | 9.2% | 2.6 | 36.7 |

## Lead time: was the first day of each storm episode warned 1, 2, 3 days ahead?

| NOAA threshold | episodes | warned 3 days ahead | 2 days ahead | 1 day ahead |
|---:|---:|---:|---:|---:|
| 10.0% | 191 | 51.8% | 66.5% | 71.2% |
| 30.0% | 191 | 21.5% | 25.7% | 35.1% |

### Episodes that reached Kp >= 8- (G4 or stronger)

| first storm day | days | peak Kp | NOAA p, 3 days ahead | 2 days | 1 day |
|---|---:|---:|---:|---:|---:|
| 2023-03-23 | 2 | 8.0 | 2.0% | 11.0% | 45.0% |
| 2023-04-23 | 2 | 8.333 | 11.0% | 11.0% | 40.0% |
| 2024-03-23 | 3 | 8.333 | 2.0% | 2.0% | 2.0% |
| 2024-05-10 | 4 | 9.0 | 11.0% | 40.0% | 40.0% |
| 2024-06-28 | 1 | 7.667 | 2.0% | 25.0% | 25.0% |
| 2024-08-11 | 2 | 8.0 | 55.0% | 55.0% | 55.0% |
| 2024-10-10 | 3 | 8.667 | 6.0% | 6.0% | 80.0% |
| 2025-01-01 | 2 | 8.0 | 35.0% | 35.0% | 35.0% |
| 2025-04-14 | 3 | 7.667 | 11.0% | 11.0% | 11.0% |
| 2025-06-01 | 4 | 7.667 | 30.0% | 30.0% | 95.0% |
| 2025-11-12 | 2 | 8.667 | 60.0% | 70.0% | 75.0% |

## Three users (ILLUSTRATIVE cost-loss ratios)

Relative economic value: 1 = perfect forecast, 0 = no better than the best fixed policy, below 0 = worse.

| user | C/L = threshold | needs lead | value: NOAA at that lead | NOAA day 1 | persistence | recurrence | climatology | always warn |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| aurora photographer | 0.25 | 1 d | 0.19 | 0.19 | 0.151 | 0.016 | 0.0 | -1.676 |
| satellite operator | 0.1 | 3 d | 0.263 | 0.414 | 0.0 | 0.0 | 0.0 | 0.0 |
| power-grid operator | 0.05 | 2 d | 0.173 | 0.178 | 0.0 | 0.0 | 0.0 | 0.0 |

Value of the NOAA forecast if the same user could decide 1, 2 or 3 days ahead (a forecast issued later than the user can act on is worth nothing to that user):

| user | C/L | NOAA 1 day ahead | 2 days | 3 days |
|---|---:|---:|---:|---:|
| aurora photographer | 0.25 | 0.19 | 0.122 | 0.091 |
| satellite operator | 0.1 | 0.414 | 0.364 | 0.263 |
| power-grid operator | 0.05 | 0.178 | 0.173 | 0.051 |

| user | NOAA lead used | hits | misses | false alarms | warning days/yr | false alarms/yr |
|---|---:|---:|---:|---:|---:|---:|
| aurora photographer | 1 d | 172 | 143 | 336 | 65.2 | 43.2 |
| satellite operator | 3 d | 191 | 124 | 749 | 120.7 | 96.2 |
| power-grid operator | 2 d | 293 | 22 | 1674 | 252.6 | 215.0 |

## Fairness check: NOAA against its own target (Fredericksburg K >= 5)

Days: 2778; event rate 6.1%; skill vs in-period climatology: d1 -0.036, d2 -0.030, d3 -0.029.

| forecast bin | days | mean forecast | observed |
|---|---:|---:|---:|
| 0-9% | 1652 | 4.0% | 1.7% |
| 10-19% | 585 | 12.7% | 6.8% |
| 20-29% | 147 | 23.5% | 11.6% |
| 30-39% | 198 | 31.1% | 13.6% |
| 40-59% | 122 | 45.5% | 19.7% |
| 60-100% | 74 | 69.7% | 44.6% |

## May 2024

| day | GFZ max Kp | NOAA p 3 days ahead | 2 days | 1 day |
|---|---:|---:|---:|---:|
| 2024-05-10 | 8.667 | 11.0% | 40.0% | 40.0% |
| 2024-05-11 | 9.0 | 60.0% | 85.0% | 95.0% |
| 2024-05-12 | 7.0 | 65.0% | 65.0% | 95.0% |

NOAA probability here = middle-latitude "minor storm" + "major-severe storm" from the RSGA report. This is an educational replay, not an official verification and not a warning service.
