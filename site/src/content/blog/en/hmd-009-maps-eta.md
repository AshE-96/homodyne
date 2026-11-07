---
title: "How does Google Maps know when you will arrive?"
description: "A Google Maps ETA is a forecast, not a snapshot: it mixes historical patterns, live speeds and news from neighbouring road segments."
lang: en
translationKey: hmd-009-companion
hmd: HMD-009
kind: companion
date: 2027-01-15
tags: ["Google Maps", "ETA prediction", "traffic forecasting", "graph neural networks", "DeepMind"]
sources:
  - title: "DeepMind: Traffic prediction with advanced Graph Neural Networks (3 Sep 2020)"
    url: "https://deepmind.google/blog/traffic-prediction-with-advanced-graph-neural-networks/"
  - title: "Derrow-Pinion et al. 2021, ETA Prediction with Graph Neural Networks in Google Maps (arXiv 2108.11482, CIKM 2021)"
    url: "https://arxiv.org/abs/2108.11482"
---

The arrival time Google Maps shows you is not a picture of traffic right now; it is a forecast of the traffic you will meet when you reach each stretch of your route. According to the explanation DeepMind and the Google Maps team published in 2020, that forecast combines live traffic with historical patterns, and a graph neural network lets each road segment take its neighbours' state into account.

This post accompanies [Homodyne episode HMD-009](/en/episodes/hmd-009/) and is written for readers who have not watched it. The maths of message passing, the public datasets used in traffic research and the commands to rerun our simulation are in the [deep dive for this episode](/en/blog/hmd-009-traffic-forecasting-data/). The [Persian original](/fa/blog/hmd-009-maps-eta/) is the canonical version.

> **Key takeaways**
> - An ETA is a forecast: you reach the last stretches of your route minutes from now, and their current speed says little about that moment.
> - DeepMind reported that Google Maps ETAs were already accurate "for over 97% of trips"; the graph model improved live ETA accuracy "by up to 50%" in several cities.
> - "Up to 50%" is the best reported case in a few cities, not a global average, and the published explanation dates from 2020.
> - In our toy city (ILLUSTRATIVE), the neighbour-aware method cut mean error to 0.56 minutes versus 1.13 for "current speed only". We built that world so that neighbours matter.

## Why isn't the current speed enough to predict arrival time?

Because you reach each part of the route at a different time. The street outside your door may be empty at half past seven, but by the time you reach the junctions further on, the queue may have backed up to meet you. Adding up today's speeds assumes traffic stays frozen for your whole trip, and that assumption is wrong at exactly the moments that matter most: when a jam is forming and when it is clearing.

DeepMind says this outright: live traffic data does not show the traffic you will face 10, 20 or even 50 minutes into your drive. A good ETA has to predict what each road segment will look like at the moment you arrive there, then add those predictions up in order.

## What has Google reported about ETA accuracy?

In a post published on 3 September 2020, DeepMind wrote that Google Maps ETAs were already "consistently accurate for over 97% of trips". The room for improvement was that small remaining share: the mornings when the forecast was off and you arrived late.

According to the same post, the new model "improve[d] the accuracy of real time ETAs by up to 50%" in cities such as Berlin, Jakarta, São Paulo, Sydney, Tokyo and Washington D.C. A year later, Derrow-Pinion and colleagues published "ETA Prediction with Graph Neural Networks in Google Maps" at CIKM 2021. Its abstract reports a 40+% reduction in negative ETA outcomes in cities such as Sydney, relative to the previous production system.

Read these numbers with three caveats. "Up to 50%" is the best reported case in some cities, not an average across all of them. Google defines what counts as "accurate". And the explanation is from 2020; the architecture of today's system has not been published.

## Why does traffic move backwards?

A traffic queue spreads backwards like a wave. When a motorway exit narrows, cars slow down there. The cars behind catch up and slow down too, and each minute the end of the queue creeps further back, towards the direction you are coming from.

That means the best clue to a road segment's state a few minutes from now is not always the segment itself. The current state of the segments downstream, or of a side street pouring cars into it, often tells you more. A road's future is partly written in its neighbours' present.

## How does a graph neural network listen to the neighbours?

You can treat the map as a graph: each node is a road segment, and each edge says two segments connect. In message passing, every node collects its direct neighbours' state in the first round and combines it with its own. In the second round, the neighbours pass on news from their own neighbours. A graph neural network (GNN) is a model that learns how to combine those messages.

For Google Maps, DeepMind grouped adjacent segments that share significant traffic volume into "supersegments". The DeepMind post also says the model was not easy to build: GNNs proved sensitive to the training curriculum, and the team used a technique called MetaGradients to adjust the learning rate during training. The idea is simple; engineering it for real trips is not.

## What did our toy city show?

To see the mechanism, we built a fully synthetic city. Every number in this section is **ILLUSTRATIVE** and comes from neither Google data nor any real city's traffic. A 12 km commute is split into 8 segments, 4 side streets feed into it, and there is a bottleneck at the end. Each morning a rush hour starts at the bottleneck and spreads backwards, with timing and strength that vary from day to day. On 45% of days an incident on a side street or at the bottleneck leaks into the main route.

We simulated 60 working days. The predictors learned on the first 45 and were tested on the last 15, with no shuffling, so no method could see the future. Departures every 5 minutes from 06:30 to 09:30 gave 555 test trips averaging 15.8 minutes. Four methods competed:

1. **Constant speed:** one average speed for the whole route.
2. **Historical:** each segment's average travel time at that minute of the day, over the training days.
3. **Live-now:** each segment's speed at departure, assumed to stay the same for the whole trip.
4. **Neighbour-aware:** the historical average, corrected using the segment's current deviation plus two rounds of messages from its neighbours, with correction weights learned on the training days.

<figure>
<svg role="img" aria-labelledby="hmd009-mae-en" viewBox="0 0 560 200" width="100%" style="max-width:560px" xmlns="http://www.w3.org/2000/svg">
<title id="hmd009-mae-en">ILLUSTRATIVE: mean absolute ETA error in minutes over 555 synthetic test trips: constant speed 3.43, historical 1.72, live-now 1.13, neighbour-aware 0.56</title>
<g font-size="14" fill="currentColor">
<text x="130" y="37" text-anchor="end">Constant speed</text>
<rect x="140" y="20" width="377" height="24" fill="currentColor" opacity="0.35"/>
<text x="523" y="37">3.43</text>
<text x="130" y="77" text-anchor="end">Historical</text>
<rect x="140" y="60" width="189" height="24" fill="currentColor" opacity="0.35"/>
<text x="335" y="77">1.72</text>
<text x="130" y="117" text-anchor="end">Live-now</text>
<rect x="140" y="100" width="124" height="24" fill="currentColor" opacity="0.35"/>
<text x="270" y="117">1.13</text>
<text x="130" y="157" text-anchor="end">Neighbour-aware</text>
<rect x="140" y="140" width="62" height="24" fill="#E8A33D"/>
<text x="208" y="157">0.56</text>
</g>
<text x="140" y="190" font-size="12" fill="currentColor" opacity="0.8">ILLUSTRATIVE · synthetic traffic · seed 2026</text>
</svg>
<figcaption>Mean absolute error (MAE) of the arrival-time prediction, in minutes, over 555 test trips in the toy city. Source: <code>parts/03-standalone/hmd-009-maps-eta/artifact/results-seed2026.json</code>, the saved output of <code>eta_toy.py</code> (seed 2026). ILLUSTRATIVE.</figcaption>
</figure>

The neighbour-aware method came first with a mean error of 0.56 minutes, less than half the live-now error of 1.13. In the 07:15 to 08:45 rush, the gap widened: 1.84 minutes for live-now against 0.85 for neighbour-aware. To check it was not luck, we reran the whole experiment with 20 other random seeds; the neighbour-aware method had the lowest error all 20 times.

The most instructive part is two mornings from the test days. On day 54 at 07:45, a jam was forming: the real trip took 24.0 minutes and live-now predicted 18.1, because it treated still-empty streets as if they would stay empty. On day 60 at 08:30, the jam was clearing: the real trip took 22.6 minutes and live-now said 29.9, worse than the constant-speed guess of 16.6, because it counted traffic that would be gone by the time you got there. "Now" errs in both directions. Our best method was not perfect either: on the first morning it said 20.6 minutes, still short of the real time.

## What this does not show

- It does not show how Google Maps works today. The published explanation is from 2020 and the current architecture is not public.
- It contains no data from Tehran, where Homodyne is made, or from any Iranian navigation or ride-hailing app, and we make no claim about them.
- "Halving the error" belongs to our toy city only. We wrote that world so traffic spreads from neighbours, so the neighbour-aware method's advantage is partly built in.
- Our neighbour-aware method is a simple linear correction, not a real graph neural network. The toy shows why the idea can work, not how well it works in the real world; only measurement on real trips can show that.

## What can you do with this?

Try a five-day exercise. Each time you set off, note the app's ETA; when you arrive, note the real time. Then see when the biggest errors happened: on trips that started just as the rush was building, or on trips at its tail end. If our toy taught the right lesson, those are the hardest moments to predict.

One more thing: a navigation app never says "I don't know"; it always gives a number. Its mistakes cost minutes. An AI that gives a wrong answer with the same confidence can cost more. The next episode, [HMD-010](/en/episodes/hmd-010/), asks whether negative marking can make an AI more careful.
