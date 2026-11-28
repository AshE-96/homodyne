#!/usr/bin/env python3
"""chalus_fixture.py · HMD-S07 · a SYNTHETIC hourly table for rehearsal and the selftest. Never real 141 data.

    python3 -I artifact/chalus_fixture.py            # writes artifact/fixture/SYNTHETIC_chalus_hourly.csv (seed 1405)
    python3 -I artifact/chalus_fixture.py --days 200 --out /tmp/x.csv

What it imitates (shape only, invented numbers): one counter on a two-lane mountain road, one lane per direction;
weekday and holiday surges (out on the eve, back on the last day); summer high, winter low; a queue that carries over
from hour to hour when demand exceeds capacity, which makes the counter count FEWER cars at low speed; and police
one-way plans on return days (the closed direction counts almost nothing, the open one gets both lanes).
The calendar (Jalali dates, official holidays from holidays.csv) is real; every traffic number is made up.
"""
import argparse
import csv
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chalus_core as cc  # noqa: E402

OUT = HERE / 'fixture' / 'SYNTHETIC_chalus_hourly.csv'
START = cc.j2g(1403, 12, 1)                       # 24 months: 1 Esfand 1403 … 30 Bahman 1405
END = cc.j2g(1405, 11, 30)
CAP = 1300.0                                      # invented capacity, vehicles per hour per lane
VFREE = 72.0                                      # invented free-flow mean speed at the counter, km/h

# invented base demand by hour (vehicles/hour) on a plain winter-free weekday
BASE = {'N': [40, 25, 18, 15, 20, 45, 110, 190, 260, 300, 310, 300, 280, 260, 250, 250, 260, 270, 250, 200, 150, 110, 80, 55],
        'S': [45, 30, 20, 15, 18, 40, 100, 170, 230, 260, 270, 270, 260, 260, 270, 290, 310, 320, 300, 250, 190, 140, 95, 60]}
SEASON = [1.10, 1.45, 0.95, 0.70]                 # spring, summer, autumn, winter (Jalali quarters)


def surge(dirn, h, cal):
    """Multiplier on base demand from the calendar: out on the eve and first day, back on the last day."""
    m = 1.0
    nz = cal['nz']
    if dirn == 'N':
        if cal['dow'] == 4 and h >= 13:                    # Wednesday afternoon, leaving for the weekend
            m *= 1.7
        if cal['dow'] == 5 and 5 <= h <= 13:               # Thursday morning
            m *= 2.3
        if cal['eve'] == 1 and h >= 12:
            m *= 2.2
        if cal['off'] and cal['pos'] == 2 and 5 <= h <= 14:
            m *= 2.6
        if -2 <= nz <= 1 and 6 <= h <= 20:
            m *= 2.4
    else:
        if cal['dow'] == 6 and 12 <= h <= 23:              # Friday afternoon, the return
            m *= 2.2
        if cal['off'] and cal['pos'] in (1, 4) and 11 <= h <= 23:
            m *= 2.4
        if nz in (12, 13) and 10 <= h <= 23:
            m *= 2.8
    if 1 <= nz <= 11:
        m *= 1.25
    return m


def simulate(days, holidays, seed=1405):
    rng = cc.seeded(seed)
    rows = []
    queue = {'N': 0.0, 'S': 0.0}
    snow = {START + dt.timedelta(days=rng.randrange(300, 330))}           # one invented snow closure in winter 1404
    d = START
    while d < START + dt.timedelta(days=days):
        cal = cc.day_features(d, holidays)
        day_noise = {x: cc.lognormal(rng, 0.10) for x in cc.DIRS}
        for h in range(24):
            demand = {x: BASE[x][h] * SEASON[cal['season']] * surge(x, h, cal) * day_noise[x] * cc.lognormal(rng, 0.08)
                      for x in cc.DIRS}
            closed = {x: False for x in cc.DIRS}
            # police one-way plan: on a heavy return, shut the northbound lane 15–24 and give both lanes to the south
            if queue['S'] > 900 and h >= 14 and (cal['dow'] == 6 or (cal['off'] and cal['pos'] in (1, 4)) or cal['nz'] in (12, 13)):
                closed['N'] = True
            if queue['N'] > 1200 and 7 <= h <= 18 and (cal['nz'] in range(-2, 2) or cal['pos'] == 2):
                closed['S'] = True
            if d in snow:
                closed = {'N': True, 'S': True}
            for x in cc.DIRS:
                other = 'S' if x == 'N' else 'N'
                if closed[x]:
                    queue[x] += demand[x] * 0.3                  # most drivers give up or wait off the road
                    served = rng.randrange(0, 12)                # residents and emergency vehicles
                    speed = None if served < 3 else round(30 + 20 * rng.random(), 1)
                else:
                    cap = CAP * (2 if closed[other] and d not in snow else 1)
                    want = demand[x] + queue[x]
                    jammed = queue[x] > 0.15 * cap
                    eff = cap * (0.82 if jammed else 1.0)       # capacity drop inside a queue
                    served = min(want, eff)
                    queue[x] = max(0.0, want - served) * 0.92    # a few leave the queue every hour
                    ratio = served / cap
                    if queue[x] > 0.15 * cap:
                        speed = max(6.0, 34.0 - queue[x] / 120.0)
                    else:
                        speed = VFREE * (1 - 0.35 * ratio ** 2)
                    speed = round(speed * cc.lognormal(rng, 0.05), 1)
                    served = int(served)
                missing = rng.random() < 0.015
                rows.append(dict(date=d.isoformat(), jalali=cc.jstr(d), hour=h, dir=x,
                                 count='' if missing else served, speed='' if missing or speed is None else speed,
                                 closed=int(closed[x]), synthetic=1))
        d += dt.timedelta(days=1)
    return rows


def write(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write('# SYNTHETIC FIXTURE · HMD-S07 · made by chalus_fixture.py · NOT real 141.ir data · for rehearsal and tests only\n')
        f.write('# counter: invented, one point on a two-lane mountain road · N = Karaj→Chalus, S = Chalus→Karaj · closed=1: police one-way (simulated)\n')
        w = csv.DictWriter(f, fieldnames=['date', 'jalali', 'hour', 'dir', 'count', 'speed', 'closed', 'synthetic'])
        w.writeheader()
        w.writerows(rows)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--days', type=int, default=(END - START).days + 1)
    ap.add_argument('--seed', type=int, default=1405)
    ap.add_argument('--out', type=Path, default=OUT)
    a = ap.parse_args()
    rows = simulate(a.days, cc.load_holidays(), a.seed)
    write(rows, a.out)
    print(f'wrote {a.out} · {len(rows)} rows · {a.days} days from {START} ({cc.jstr(START)}) · SYNTHETIC')
