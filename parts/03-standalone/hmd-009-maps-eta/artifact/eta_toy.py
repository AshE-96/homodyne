#!/usr/bin/env python3
"""Homodyne HMD-009 - toy ETA lab (ILLUSTRATIVE synthetic traffic).

What this is:
    A tiny, fully synthetic road graph (a 6-segment commute route plus side
    streets) with made-up traffic: a morning rush that spills back upstream from
    a downstream bottleneck, day-to-day variation, and random incidents that
    start on side streets and leak into the route.

    Four ETA predictors are compared on a TIME-BASED split (train on the first
    weeks, test on the last weeks, no shuffling):
      1. constant    - one average speed for the whole route (from training data)
      2. historical  - per-segment average travel time for that time of day
      3. live-now    - (extra baseline) freeze the speeds observed at departure
      4. neighbour   - historical average + a learned correction from the live
                       state of each segment AND its neighbours, aggregated in two
                       message-passing rounds (shared weights, per horizon)

What this is NOT:
    Not Google's model, not Google data, not Tehran data. The numbers only show
    how the *idea* behaves on a toy we built. Change the seed or the traffic
    rules and the numbers change.

Standard library only. Run:  python3 eta_toy.py            (prints a report)
                             python3 eta_toy.py --json      (machine-readable)
                             python3 eta_toy.py --seed 7    (robustness check)
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics

STATUS = "ILLUSTRATIVE synthetic traffic - not Google Maps, not Tehran data"

# ---------------------------------------------------------------- road graph
# Route segments R1..R8 (home -> office); D is the downstream bottleneck.
# Side streets S* feed into route segments (on-ramps).
SEGMENTS = {
    # name: (length_km, free_flow_kmh)
    "R1": (1.6, 60), "R2": (1.4, 60), "R3": (1.5, 60), "R4": (1.5, 60),
    "R5": (1.4, 60), "R6": (1.6, 60), "R7": (1.5, 60), "R8": (1.5, 60),
    "D":  (0.8, 50),
    "S3": (0.6, 30), "S5": (0.6, 30), "S7": (0.5, 30), "S8": (0.5, 30),
}
ROUTE = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
EDGES = [  # undirected adjacency used for message passing
    ("R1", "R2"), ("R2", "R3"), ("R3", "R4"), ("R4", "R5"), ("R5", "R6"),
    ("R6", "R7"), ("R7", "R8"), ("R8", "D"),
    ("S3", "R3"), ("S5", "R5"), ("S7", "R7"), ("S8", "R8"),
]
NEIGHBOURS = {s: [] for s in SEGMENTS}
for a, b in EDGES:
    NEIGHBOURS[a].append(b)
    NEIGHBOURS[b].append(a)

# Position of each route segment, counted from the bottleneck (D = 0).
UPSTREAM_RANK = {"D": 0, "R8": 1, "R7": 2, "R6": 3, "R5": 4, "R4": 5, "R3": 6, "R2": 7, "R1": 8}
RAMP_OF = {"S3": "R3", "S5": "R5", "S7": "R7", "S8": "R8"}

DAY_START = 6 * 60          # 06:00, minutes after midnight
DAY_END = 12 * 60           # simulate until 11:00 so late trips can finish
DEPART_FIRST = 6 * 60 + 30  # first departure 06:30
DEPART_LAST = 9 * 60 + 30   # last departure 09:30
DEPART_STEP = 5
HORIZONS = list(range(0, 75, 5))  # minutes ahead (bucketed)


def bump(t: float, centre: float, width: float) -> float:
    """Smooth 0..1 bump."""
    return math.exp(-0.5 * ((t - centre) / width) ** 2)


# ---------------------------------------------------------------- synthetic world
def simulate_day(rng: random.Random, weekday: int) -> dict:
    """Return {segment: [congestion 0..1 for each minute DAY_START..DAY_END]}."""
    minutes = range(DAY_START, DAY_END + 1)
    peak_centre = 8 * 60 + rng.gauss(0, 15) - (10 if weekday == 0 else 0)
    peak_amp = min(1.0, max(0.35, rng.gauss(0.75, 0.15)))
    spill_lag = rng.uniform(3.0, 6.0)   # minutes per segment for the queue to grow upstream

    # incidents: (segment, start_minute, duration, strength)
    incidents = []
    if rng.random() < 0.45:
        seg = rng.choice(["S3", "S5", "S7", "S8", "D"])
        start = rng.uniform(6 * 60 + 40, 9 * 60 + 20)
        incidents.append((seg, start, rng.uniform(20, 50), rng.uniform(0.5, 0.95)))

    cong = {}
    for s in SEGMENTS:
        series = []
        for t in minutes:
            c = 0.0
            if s in UPSTREAM_RANK:   # route + bottleneck: rush hour spills back upstream
                lag = spill_lag * UPSTREAM_RANK[s]
                c += peak_amp * bump(t, peak_centre + lag, 28) * (1.0 - 0.04 * UPSTREAM_RANK[s])
            else:                    # side streets: their own, weaker rush
                c += 0.5 * peak_amp * bump(t, peak_centre - 5, 30)
            series.append(c)
        cong[s] = series

    # incidents propagate: side street -> its route segment -> upstream route segments
    for seg, start, dur, strength in incidents:
        chain = []
        if seg in RAMP_OF:
            chain.append((seg, 0.0))
            root = RAMP_OF[seg]
        else:
            chain.append((seg, 0.0))
            root = "R8"
        base_rank = UPSTREAM_RANK[root]
        for r in ROUTE:
            if UPSTREAM_RANK[r] >= base_rank:
                delay = 4.0 + 4.0 * (UPSTREAM_RANK[r] - base_rank)
                chain.append((r, delay))
        for s, delay in chain:
            for i, t in enumerate(minutes):
                if start + delay <= t <= start + delay + dur:
                    fade = 1.0 - 0.12 * (delay / 4.0)
                    cong[s][i] = max(cong[s][i], strength * max(0.2, fade))

    # measurement-free "truth" plus small minute-level noise
    for s in SEGMENTS:
        cong[s] = [min(0.97, max(0.0, c + rng.gauss(0, 0.03))) for c in cong[s]]
    return {"cong": cong, "incident": bool(incidents)}


def seg_time(s: str, c: float) -> float:
    """Travel time (minutes) of segment s at congestion c."""
    length, v_free = SEGMENTS[s]
    speed = v_free * (1.0 - 0.85 * c)
    return 60.0 * length / speed


def tt_series(day: dict) -> dict:
    return {s: [seg_time(s, c) for c in day["cong"][s]] for s in SEGMENTS}


def idx(t: float) -> int:
    return max(0, min(DAY_END - DAY_START, int(round(t)) - DAY_START))


def actual_trip(tts: dict, t0: float) -> float:
    t = t0
    for s in ROUTE:
        t += tts[s][idx(t)]
    return t - t0


# ---------------------------------------------------------------- predictors
def walk(t0: float, seg_tt_at) -> float:
    """Sequential ETA: each segment's time is looked up at the predicted entry time."""
    t = t0
    for s in ROUTE:
        t += seg_tt_at(s, t, t - t0)
    return t - t0


def fit_least_squares(X: list, y: list, ridge: float = 1e-3) -> list:
    """Solve (X'X + ridge I) w = X'y with plain Gaussian elimination."""
    p = len(X[0])
    A = [[0.0] * p for _ in range(p)]
    b = [0.0] * p
    for row, target in zip(X, y):
        for i in range(p):
            b[i] += row[i] * target
            for j in range(p):
                A[i][j] += row[i] * row[j]
    for i in range(p):
        A[i][i] += ridge
    for col in range(p):  # elimination with partial pivoting
        piv = max(range(col, p), key=lambda r: abs(A[r][col]))
        A[col], A[piv] = A[piv], A[col]
        b[col], b[piv] = b[piv], b[col]
        for r in range(col + 1, p):
            f = A[r][col] / A[col][col]
            for c in range(col, p):
                A[r][c] -= f * A[col][c]
            b[r] -= f * b[col]
    w = [0.0] * p
    for i in reversed(range(p)):
        w[i] = (b[i] - sum(A[i][j] * w[j] for j in range(i + 1, p))) / A[i][i]
    return w


def horizon_bucket(h: float) -> int:
    return min(HORIZONS, key=lambda x: abs(x - h))


def features(tts: dict, hist: dict, s: str, t0: float) -> list:
    """Own deviation + two rounds of neighbour messages (mean of neighbour deviations)."""
    i0 = idx(t0)
    dev = {n: tts[n][i0] / hist[n][i0] - 1.0 for n in SEGMENTS}
    msg1 = {n: statistics.fmean(dev[m] for m in NEIGHBOURS[n]) for n in SEGMENTS}
    msg2 = {n: statistics.fmean(msg1[m] for m in NEIGHBOURS[n]) for n in SEGMENTS}
    return [1.0, dev[s], msg1[s], msg2[s]]


def build(seed: int) -> dict:
    rng = random.Random(seed)
    n_days, n_train = 60, 45   # 12 working weeks; train weeks 1-9, test weeks 10-12
    days = [simulate_day(rng, d % 5) for d in range(n_days)]
    series = [tts_series for tts_series in (tt_series(d) for d in days)]
    train, test = range(n_train), range(n_train, n_days)

    # (1) constant speed from training trips
    dist = sum(SEGMENTS[s][0] for s in ROUTE)
    train_trips = [(d, t0) for d in train for t0 in range(DEPART_FIRST, DEPART_LAST + 1, DEPART_STEP)]
    mean_trip = statistics.fmean(actual_trip(series[d], t0) for d, t0 in train_trips)
    const_speed = dist / (mean_trip / 60.0)

    # (2) historical per-segment, per-minute-of-day average over training days
    length = DAY_END - DAY_START + 1
    hist = {s: [statistics.fmean(series[d][s][i] for d in train) for i in range(length)] for s in SEGMENTS}

    # (4) neighbour model: one shared weight vector per horizon bucket
    X = {h: [] for h in HORIZONS}
    Y = {h: [] for h in HORIZONS}
    for d in train:
        for t0 in range(DEPART_FIRST, DEPART_LAST + 1, DEPART_STEP):
            for s in ROUTE:
                f = features(series[d], hist, s, t0)
                for h in HORIZONS:
                    target = series[d][s][idx(t0 + h)] / hist[s][idx(t0 + h)] - 1.0
                    X[h].append(f)
                    Y[h].append(target)
    W = {h: fit_least_squares(X[h], Y[h]) for h in HORIZONS}

    def predict_all(d: int, t0: float) -> dict:
        tts = series[d]
        feats = {s: features(tts, hist, s, t0) for s in ROUTE}
        return {
            "constant": dist / const_speed * 60.0,
            "historical": walk(t0, lambda s, t, h: hist[s][idx(t)]),
            "live-now": walk(t0, lambda s, t, h: tts[s][idx(t0)]),
            "neighbour": walk(t0, lambda s, t, h: hist[s][idx(t)] * (1.0 + sum(
                w * x for w, x in zip(W[horizon_bucket(h)], feats[s])))),
        }

    rows = []
    for d in test:
        for t0 in range(DEPART_FIRST, DEPART_LAST + 1, DEPART_STEP):
            rows.append({"day": d, "t0": t0, "incident": days[d]["incident"],
                         "actual": actual_trip(series[d], t0), **predict_all(d, t0)})
    return {"rows": rows, "weights": W, "const_speed": const_speed, "dist": dist,
            "n_train_days": n_train, "n_test_days": n_days - n_train}


def mae(rows: list, key: str) -> float:
    return statistics.fmean(abs(r[key] - r["actual"]) for r in rows) if rows else float("nan")


def share_off(rows: list, key: str, minutes: float = 5.0) -> float:
    return sum(abs(r[key] - r["actual"]) > minutes for r in rows) / len(rows) if rows else float("nan")


def hhmm(m: float) -> str:
    return f"{int(m) // 60:02d}:{int(m) % 60:02d}"


def report(seed: int) -> dict:
    res = build(seed)
    rows = res["rows"]
    rush = [r for r in rows if 7 * 60 + 15 <= r["t0"] <= 8 * 60 + 45]
    inc = [r for r in rows if r["incident"]]
    calm = [r for r in rows if not r["incident"]]
    keys = ["constant", "historical", "live-now", "neighbour"]
    out = {
        "status": STATUS,
        "seed": seed,
        "split": f"train days 1-{res['n_train_days']}, test days {res['n_train_days'] + 1}-{res['n_train_days'] + res['n_test_days']} (time-based, no shuffle)",
        "route_km": round(res["dist"], 1),
        "test_trips": len(rows),
        "mean_actual_trip_min": round(statistics.fmean(r["actual"] for r in rows), 1),
        "mae_min": {k: round(mae(rows, k), 2) for k in keys},
        "mae_rush_0715_0845_min": {k: round(mae(rush, k), 2) for k in keys},
        "mae_incident_days_min": {k: round(mae(inc, k), 2) for k in keys},
        "mae_calm_days_min": {k: round(mae(calm, k), 2) for k in keys},
        "share_off_by_more_than_5min": {k: round(share_off(rows, k), 3) for k in keys},
        "n_rush": len(rush), "n_incident_trips": len(inc),
    }
    out["mean_actual_rush_trip_min"] = round(statistics.fmean(r["actual"] for r in rush), 1)
    out["max_actual_trip_min"] = round(max(r["actual"] for r in rows), 1)
    # two example trips for the story: where freezing "now" under- and over-shoots most
    under = min(rush, key=lambda r: r["live-now"] - r["actual"])
    over = max(rush, key=lambda r: r["live-now"] - r["actual"])
    for name, ex in (("example_jam_building", under), ("example_jam_clearing", over)):
        out[name] = {"day": ex["day"] + 1, "depart": hhmm(ex["t0"]),
                     **{k: round(ex[k], 1) for k in ["actual"] + keys}}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--seeds", type=int, default=0, help="also run N extra seeds for a robustness summary")
    a = ap.parse_args()
    out = report(a.seed)
    if a.seeds:
        wins = []
        for s in range(1, a.seeds + 1):
            m = report(a.seed + s)["mae_min"]
            wins.append(min(m, key=m.get))
        out["robustness"] = {"extra_seeds": a.seeds, "best_model_counts": {k: wins.count(k) for k in sorted(set(wins))}}
    if a.json:
        print(json.dumps(out, indent=2))
        return
    print(f"# {STATUS}")
    print(f"seed={out['seed']}  route={out['route_km']} km  {out['split']}")
    print(f"test trips={out['test_trips']}  mean actual trip={out['mean_actual_trip_min']} min\n")
    print(f"{'predictor':<12}{'MAE all':>9}{'rush':>8}{'incident':>10}{'calm':>8}{'>5 min off':>12}")
    for k in ["constant", "historical", "live-now", "neighbour"]:
        print(f"{k:<12}{out['mae_min'][k]:>9.2f}{out['mae_rush_0715_0845_min'][k]:>8.2f}"
              f"{out['mae_incident_days_min'][k]:>10.2f}{out['mae_calm_days_min'][k]:>8.2f}"
              f"{out['share_off_by_more_than_5min'][k] * 100:>11.1f}%")
    print(f"\nrush-hour trips: mean actual {out['mean_actual_rush_trip_min']} min; longest test trip {out['max_actual_trip_min']} min")
    for name in ("example_jam_building", "example_jam_clearing"):
        e = out[name]
        print(f"{name}: test day {e['day']}, depart {e['depart']} -> actual {e['actual']} min | "
              + " | ".join(f"{k} {e[k]}" for k in ["constant", "historical", "live-now", "neighbour"]))
    if "robustness" in out:
        print(f"robustness over {a.seeds} extra seeds, best MAE counts: {out['robustness']['best_model_counts']}")
    print("\nMAE = mean absolute error in minutes. ILLUSTRATIVE: numbers describe this toy only.")


if __name__ == "__main__":
    main()
