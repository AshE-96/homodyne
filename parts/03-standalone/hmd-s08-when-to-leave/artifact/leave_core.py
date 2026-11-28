"""leave_core.py · HMD-S08 · the arithmetic of "arrive by", standard library only.

Data: artifact/derived/weekday_trips.csv (NYC TLC yellow taxi, weekday pickups Mar-Apr 2026; see SOURCE.txt).
A trip's pickup time is "when I leave", its meter minutes are "how long it took".

Definitions used everywhere (episode, deck, study notes):
  sample(t)        trips that left within +-HALF minutes of clock time t, on TRAIN weekdays
  Q_c(t)           the c-quantile of that sample (linear interpolation, numpy/Excel "inclusive" rule)
  leave-by(D, c)   the latest t on a 5-minute grid with t + Q_c(t) <= D: "on time with confidence c"
  mean rule        the latest t with t + mean(t) <= D: what you get by trusting one average ETA
  backtest         on each TEST weekday, trips that really left within +-BT_HALF minutes of the chosen t;
                   a trip is late if t + its minutes > D
  buffer index     (P95 - mean) / mean                 FHWA, Travel Time Reliability (Dec 2005)
  planning index   P95 / free-flow                     FHWA; free-flow here = our proxy, P5 of all train trips
  newsvendor q*    c_late / (c_late + c_early)          per-minute costs; argmin of expected cost
"""
import csv
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / 'derived' / 'weekday_trips.csv'
SPLIT = '2026-04-13'          # same split day as HMD-009: train Mar 2 .. Apr 10, test Apr 13 .. Apr 30
HALF = 15                     # departure window for the distribution: +-15 min
BT_HALF = 10                  # backtest window: trips that left within +-10 min of the chosen time
STEP = 5
HORIZON = 240                 # look back at most 4 hours before the deadline
MIN_N = 20                    # fewer trips than this in a window: no estimate
ROUTES = {
    'jfk': ('Midtown → JFK Airport', 'میدتاون ← فرودگاه JFK'),
    'lga': ('Midtown → LaGuardia Airport', 'میدتاون ← فرودگاه لاگواردیا'),
    'ewr': ('Midtown → Newark Airport', 'میدتاون ← فرودگاه نیوآرک'),
    'fidi': ('Upper East Side → Financial District', 'آپر ایست ساید ← محلهٔ مالی'),
}


def load(path=DATA):
    """route -> list of (date str, dep minute, minutes)."""
    out = defaultdict(list)
    with open(path, newline='') as f:
        for r in csv.DictReader(f):
            out[r['route']].append((r['date'], int(r['dep']), float(r['min'])))
    return dict(out)


def split(trips, day=SPLIT):
    return [x for x in trips if x[0] < day], [x for x in trips if x[0] >= day]


def quantile(xs_sorted, q):
    """Linear interpolation between order statistics (type 7; numpy default, Excel PERCENTILE.INC)."""
    n = len(xs_sorted)
    if n == 0:
        return None
    h = (n - 1) * q
    lo = math.floor(h)
    hi = min(lo + 1, n - 1)
    return xs_sorted[lo] + (h - lo) * (xs_sorted[hi] - xs_sorted[lo])


def mean(xs):
    return sum(xs) / len(xs) if xs else None


class Index:
    """Durations bucketed by departure minute, so a window query is a sum over 2*HALF+1 buckets."""

    def __init__(self, trips):
        self.by_min = defaultdict(list)
        for _, dep, m in trips:
            self.by_min[dep].append(m)

    def sample(self, t, half=HALF):
        xs = []
        for d in range(t - half, t + half + 1):
            if 0 <= d < 1440:
                xs.extend(self.by_min.get(d, ()))
        xs.sort()
        return xs


def stats(xs):
    if len(xs) < MIN_N:
        return None
    return dict(n=len(xs), mean=mean(xs), p50=quantile(xs, .5), p80=quantile(xs, .8),
                p90=quantile(xs, .9), p95=quantile(xs, .95), p05=quantile(xs, .05))


def profile(idx, t0=0, t1=1435, step=STEP):
    return {t: stats(idx.sample(t)) for t in range(t0, t1 + 1, step)}


def leave_by(idx, deadline, conf, step=STEP, horizon=HORIZON):
    """Latest departure t (grid) with t + Q_conf(t) <= deadline; None if no window qualifies."""
    t = deadline - (deadline % step)
    while t >= deadline - horizon:
        xs = idx.sample(t)
        if len(xs) >= MIN_N and t + quantile(xs, conf) <= deadline:
            return t
        t -= step
    return None


def leave_by_mean(idx, deadline, step=STEP, horizon=HORIZON):
    t = deadline - (deadline % step)
    while t >= deadline - horizon:
        xs = idx.sample(t)
        if len(xs) >= MIN_N and t + mean(xs) <= deadline:
            return t
        t -= step
    return None


def on_time_share(xs, slack):
    """Share of the sample with duration <= slack minutes."""
    return sum(1 for x in xs if x <= slack) / len(xs) if xs else None


def backtest(test_trips, t, deadline, half=BT_HALF):
    """Leave at t on each held-out weekday; real trips that left within +-half minutes stand in for 'you'."""
    per_day = defaultdict(lambda: [0, 0])
    for d, dep, m in test_trips:
        if abs(dep - t) <= half:
            per_day[d][0] += 1
            per_day[d][1] += (t + m > deadline)
    n = sum(v[0] for v in per_day.values())
    late = sum(v[1] for v in per_day.values())
    days = sorted(per_day)
    return dict(trips=n, late=late, late_share=(late / n if n else None), days=len(days),
                days_with_late=sum(1 for d in days if per_day[d][1] > 0),
                worst_day=max(days, key=lambda d: per_day[d][1] / per_day[d][0]) if days else None,
                per_day={d: per_day[d] for d in days})


def reliability(idx_all_trips, t):
    """FHWA buffer index and planning time index for departures around t (free-flow = our P5 proxy)."""
    xs = idx_all_trips.sample(t)
    if len(xs) < MIN_N:
        return None
    allx = sorted(m for v in idx_all_trips.by_min.values() for m in v)
    ff = quantile(allx, .05)
    p95, mu = quantile(xs, .95), mean(xs)
    return dict(mean=mu, p95=p95, free_flow=ff, buffer_index=(p95 - mu) / mu, planning_time_index=p95 / ff,
                travel_time_index=mu / ff)


def critical_q(cost_late, cost_early):
    """Newsvendor critical fractile for per-minute costs."""
    return cost_late / (cost_late + cost_early)


def expected_cost(xs, budget, cost_late, cost_early):
    """Mean cost of allowing `budget` minutes when the trip takes x: early (budget-x)*ce, late (x-budget)*cl."""
    return sum(cost_early * (budget - x) if x <= budget else cost_late * (x - budget) for x in xs) / len(xs)


def best_budget(xs, cost_late, cost_early):
    """Brute-force argmin over the observed durations (the minimum of a piecewise-linear cost sits on one)."""
    return min(xs, key=lambda b: expected_cost(xs, b, cost_late, cost_early))


def hhmm(t):
    return None if t is None else f'{int(t) // 60:02d}:{int(t) % 60:02d}'


def weekday_name(d):
    return date.fromisoformat(d).strftime('%a')
