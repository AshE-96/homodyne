---
title: "Traffic forecasting on graphs: data, method, reproduction"
description: "Message passing on road graphs, supersegments, the METR-LA and PEMS-BAY benchmarks, why historical averages are hard to beat, and how to rerun HMD-009."
lang: en
translationKey: hmd-009-deep-dive
hmd: HMD-009
kind: deep-dive
date: 2027-01-15
tags: ["traffic forecasting", "graph neural networks", "message passing", "METR-LA", "PEMS-BAY", "ETA prediction"]
sources:
  - title: "Derrow-Pinion et al. 2021, ETA Prediction with Graph Neural Networks in Google Maps (arXiv 2108.11482, CIKM 2021)"
    url: "https://arxiv.org/abs/2108.11482"
  - title: "DeepMind: Traffic prediction with advanced Graph Neural Networks (3 Sep 2020)"
    url: "https://deepmind.google/blog/traffic-prediction-with-advanced-graph-neural-networks/"
  - title: "Li et al., Diffusion Convolutional Recurrent Neural Network: Data-Driven Traffic Forecasting (DCRNN, arXiv 1707.01926)"
    url: "https://arxiv.org/abs/1707.01926"
datasets:
  - title: "METR-LA: 207 Los Angeles County highway loop detectors, 1 March to 30 June 2012 (distributed via the DCRNN repository)"
    url: "https://github.com/liyaguang/DCRNN"
    license: "No data licence stated; see the DCRNN repository (its code is MIT)"
  - title: "PEMS-BAY: 325 Bay Area sensors from Caltrans PeMS, 1 January to 31 May 2017 (distributed via the DCRNN repository)"
    url: "https://github.com/liyaguang/DCRNN"
    license: "No data licence stated; see the DCRNN repository (its code is MIT)"
  - title: "HMD-009 eta_toy.py and results-seed2026.json (synthetic traffic, ILLUSTRATIVE)"
    url: "https://github.com/AshE-96/homodyne/tree/main/parts/03-standalone/hmd-009-maps-eta/artifact"
    license: "see the repository's LICENSE.md"
---

This post opens the layer the HMD-009 video skipped: how an ETA is built from segment-by-segment forecasts, what message passing on a road graph actually computes, which public datasets researchers outside Google use, and how to rerun the episode's simulation. Google Maps trip data is not public, so independent testing relies on datasets such as METR-LA and PEMS-BAY, and they teach one recurring lesson: the longer the forecast horizon, the harder it is to beat a plain historical average.

If you have not seen the video or the [companion post](/en/blog/hmd-009-maps-eta/), start there. The [HMD-009 episode page](/en/episodes/hmd-009/) and the [Persian original of this post](/fa/blog/hmd-009-traffic-forecasting-data/) are also available.

> **Key takeaways**
> - An ETA is the sum of each segment's predicted travel time at the moment you enter it; segments near the end of the route have longer forecast horizons.
> - In message passing, every node gathers its neighbours' state each round and combines it with its own; per the 2020 explanation, Google Maps does this over "supersegments".
> - The two common public datasets, METR-LA (207 sensors) and PEMS-BAY (325 sensors), forecast speed at sensors, not trip time.
> - In Table 1 of the DCRNN paper on METR-LA, the historical average scores an MAE of 4.16 at every horizon; DCRNN gets 2.77 at 15 minutes and 3.60 at 60 minutes, and ARIMA gets 6.90 at 60 minutes.
> - Our simulation is synthetic and ILLUSTRATIVE, and reruns with one command from the repository root.

## How do you write an ETA down precisely?

Say you leave at time `t0` and your route crosses segments `s1` to `sn`. If `τ(s, t)` is the predicted travel time of segment `s` for someone entering it at time `t`, each entry time follows from the previous one:

`t_k = t_(k-1) + τ(s_k, t_(k-1))`  and  `ETA = t_n - t0`

The recursion is the whole point. For the first segment the forecast horizon is zero; for the last ones it is however long it takes to get there. An ETA is really a chain of forecasts with different horizons. The live-now method sets `τ(s, t)` to the segment's travel time at `t0` and ignores the horizon. In the episode's code, the `walk` function in `eta_toy.py` implements exactly this recursion.

## What does message passing on a road graph compute?

In a road graph, each node `v` is a segment with a state vector `h_v`, for example its current speed, its usual speed at this hour and its length. In each round of message passing, every node gathers messages from its neighbours `N(v)` and combines them with its own state:

`h_v' = UPDATE( h_v , AGG{ MESSAGE(h_u) : u ∈ N(v) } )`

After `k` rounds, each node has information from nodes up to `k` edges away. In a graph neural network, `MESSAGE` and `UPDATE` are small learned networks, and `AGG` is usually a sum or mean.

The DeepMind post and the paper by Derrow-Pinion et al. (arXiv 2108.11482) describe Google Maps applying this idea to "supersegments": groups of adjacent segments that share significant traffic volume. The DeepMind post records two engineering difficulties: the network's sensitivity to the training curriculum, and the use of MetaGradients to adapt the learning rate during training. The paper's abstract reports a 40+% reduction in negative ETA outcomes in cities such as Sydney, compared with the previous production system.

Our toy version implements the same structure in a much simpler way. For each segment, it computes the relative deviation from the historical average at departure: `dev = observed / historical - 1`. The first-round message is the mean `dev` of the neighbours, and the second-round message is the mean of the neighbours' first-round messages. The final correction is linear: `w0 + w1·dev + w2·msg1 + w3·msg2`. The weights are shared across segments, fitted separately for each 5-minute horizon by least squares (with a small ridge term) on the training days, and the predicted time is `historical × (1 + correction)`. The aggregation is a fixed mean and nothing in it is learned, so this is linear message passing, not a GNN.

## Which public data can test the idea?

Google Maps trip data has not been released, so Google's results cannot be rerun outside Google. Academic traffic-forecasting research usually works with two public datasets released with the DCRNN paper (Li et al., arXiv 1707.01926):

| Property | METR-LA | PEMS-BAY |
|---|---|---|
| Area | Los Angeles highways | California's Bay Area |
| Sensors | 207 | 325 |
| Period | March to June 2012 | January to May 2017 |
| Forecast target | traffic speed at each sensor | traffic speed at each sensor |
| Updates | fixed historical snapshot; not updated | fixed historical snapshot; not updated |
| Licence | none stated for the data; see the [DCRNN repository](https://github.com/liyaguang/DCRNN) | none stated for the data; see the [DCRNN repository](https://github.com/liyaguang/DCRNN) |

Two differences from the ETA problem matter. First, the nodes are sensors, not street segments, and the graph is built from distances between sensors along the road network. Second, the target is the speed at a point, not the duration of a whole trip. The files are distributed through the DCRNN authors' public code repository, [github.com/liyaguang/DCRNN](https://github.com/liyaguang/DCRNN), via Google Drive and Baidu links in its README. That repository carries an MIT licence for its code, but neither the README nor the paper states a licence for the data files. Check the terms of the original sources (the Los Angeles County loop detectors for METR-LA, Caltrans PeMS for PEMS-BAY) before you reuse them.

## Why is the historical average a tough baseline at long horizons?

Table 1 of the DCRNN paper on METR-LA gives this picture (MAE of speed, not trip time):

| Method | 15-minute horizon | 60-minute horizon |
|---|---|---|
| Historical average (HA) | 4.16 | 4.16 |
| ARIMA with Kalman filter | 3.99 | 6.90 |
| DCRNN | 2.77 | 3.60 |

The historical average ignores recent observations, so its error does not change with the horizon: 4.16 at every horizon. Methods that learn from the recent past have a large advantage at short horizons, but that advantage shrinks as the horizon grows. At 60 minutes DCRNN still beats the historical average, by a much smaller margin than at 15 minutes. ARIMA (here with a Kalman filter), a classic time-series model, does worse than the historical average at 60 minutes.

The practical lesson: any claim that a model forecasts better should report the historical average as a baseline, separately for each horizon. A single number averaged over all horizons can hide where the advantage actually comes from.

<!-- UNIQUE INSIGHT: links the DCRNN horizon pattern to the toy-city result; short trips mean short horizons. -->
The same pattern explains why live-now (1.13) beat the historical average (1.72) in our toy city. Trips are short, averaging 15.8 minutes with a maximum of 27.4, so most segments are forecast at short horizons where live information is valuable. Yet the morning of day 60 showed that the same live information, frozen without regard to horizon, can do worse than a constant speed. The neighbour-aware method keeps the historical average as an anchor and learns the weight of the live correction separately for each horizon.

## What exactly does the HMD-009 simulation do?

Everything is in `artifact/eta_toy.py`: Python 3.10 or later, standard library only. Every number in this section is **ILLUSTRATIVE**.

- **Graph:** a 12 km route split into 8 segments (R1 to R8), 4 side streets (S3, S5, S7, S8) feeding the segments with matching numbers, and a bottleneck D at the end.
- **Synthetic traffic:** each day has a morning peak with random timing and strength that spreads backwards from the bottleneck; side streets have their own weaker peak. On 45% of days an incident on a side street or at the bottleneck leaks, with a delay, into the upstream segments. Small minute-level noise sits on top.
- **Split:** 60 working days; training on days 1 to 45, testing on days 46 to 60, no shuffling.
- **Trips:** departures every 5 minutes from 06:30 to 09:30, giving 555 test trips.
- **Predictors:** constant speed, per-segment historical average for each minute of the day, live-now, and neighbour-aware (the message-passing section above).
- **Metric:** mean absolute error (MAE) of trip time in minutes, plus the share of trips off by more than 5 minutes.

## How do you reproduce the results?

Run these from the repository root:

```bash
# text report with seed 2026 plus a robustness check over 20 more seeds
python3 parts/03-standalone/hmd-009-maps-eta/artifact/eta_toy.py --seeds 20

# the same result as JSON, to compare with the saved file
python3 parts/03-standalone/hmd-009-maps-eta/artifact/eta_toy.py --json --seeds 20

# a different seed, to see how much the numbers move
python3 parts/03-standalone/hmd-009-maps-eta/artifact/eta_toy.py --seed 7
```

Compare the second command's output with `parts/03-standalone/hmd-009-maps-eta/artifact/results-seed2026.json`, the saved output of the 2 November 2026 run (`eta_toy.py --seeds 20`). Full results with seed 2026:

| Predictor | MAE, all trips | Rush 07:15 to 08:45 | Incident days | Calm days | Off by more than 5 min |
|---|---|---|---|---|---|
| Constant speed | 3.43 | 3.16 | 3.48 | 3.40 | 9.9% |
| Historical | 1.72 | 2.44 | 1.80 | 1.67 | 4.5% |
| Live-now | 1.13 | 1.84 | 1.23 | 1.07 | 1.4% |
| Neighbour-aware | 0.56 | 0.85 | 0.73 | 0.45 | 0.2% |

*ILLUSTRATIVE. 555 test trips; mean actual trip 15.8 minutes, mean rush-hour trip 18.5, longest trip 27.4.*

Over 20 other seeds (2027 to 2046), the neighbour-aware method had the lowest MAE all 20 times. With seed 7, the four methods' MAEs were 3.36, 2.09, 1.16 and 0.66 minutes: the numbers move, the order does not. The output also records two example trips: day 54 at 07:45 (actual 24.0; constant 16.6, historical 21.1, live-now 18.1, neighbour-aware 20.6) and day 60 at 08:30 (actual 22.6; constant 16.6, historical 19.8, live-now 29.9, neighbour-aware 24.8).

A suggested test you can run yourself: weaken the backward-spreading rule in `simulate_day` and see how much of the neighbour-aware advantage survives. We have not run this test.

## What are the method's limitations?

- **The design favours neighbours.** Traffic was written to spread from the bottleneck and the side streets, so part of the neighbour-aware advantage is built in.
- **One route, one direction.** The graph is tiny and has none of a real city's junctions, signals or alternative routes.
- **The model is linear.** The aggregation is a fixed mean, and no message or update function is learned.
- **Perfect sensors.** The predictors see every segment's true state at departure without error; real data is patchy and noisy.
- **One metric.** MAE counts arriving early and arriving late the same, while for a traveller, late is usually more costly.

## What this does not show

- It does not show how Google Maps works today; the published explanation is from 2020 and the current architecture is not public.
- The simulation numbers describe no real city or app, including Tehran, where Homodyne is produced.
- The DCRNN numbers are speed errors at highway sensors and cannot be compared with trip-time MAE in our toy city or with Google's figures.
- It does not settle the data licence of METR-LA and PEMS-BAY: the DCRNN repository's MIT licence covers its code, and no licence is stated for the data.

## Further reading

- [Derrow-Pinion et al., ETA Prediction with Graph Neural Networks in Google Maps](https://arxiv.org/abs/2108.11482): architecture, supersegments and evaluation in Google Maps (CIKM 2021).
- [DeepMind, Traffic prediction with advanced Graph Neural Networks](https://deepmind.google/blog/traffic-prediction-with-advanced-graph-neural-networks/): a non-technical account of the same work.
- [Li et al., DCRNN](https://arxiv.org/abs/1707.01926): introduces METR-LA and PEMS-BAY and the baseline comparison table.

The next episode, [HMD-010](/en/episodes/hmd-010/), moves from traffic forecasts to predictions that never say "I don't know", and asks whether negative marking can make an AI more careful.
