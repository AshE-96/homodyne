#!/usr/bin/env python3
"""Homodyne HMD-009 - four ETA predictors raced on REAL New York taxi trips.

Data: NYC Taxi & Limousine Commission (TLC) yellow-taxi trip records, March and
April 2026. Route: Midtown Manhattan (TLC zones 161, 162, 163, 164, 230) to JFK
Airport (zone 132). Every number this script prints is OUR computation on the
TLC records, not a Google or TLC figure. TLC: "makes no representations as to
the accuracy of these data".

Two steps:

  build  (needs the raw monthly parquet files + the installed duckdb module)
         python3 -I nyc_eta.py build --raw cache/tlc --out derived
         writes derived/midtown_jfk_trips.csv and derived/hourly_profile.csv

  race   (standard library only, works offline from the committed CSV)
         python3 nyc_eta.py race                  # human report
         python3 nyc_eta.py race --json           # writes derived/results.json too
         python3 nyc_eta.py race --split 2026-04-06   # robustness: other split day
         python3 nyc_eta.py race --ablation       # which live signals carry the gain

  python3 nyc_eta.py --selftest                   # fast offline test, no data needed

Predictors (all fitted on trips that STARTED before the split day, tested after):
  1. constant   - one number: the median trip time of all training trips
  2. history    - median training trip time for the same day type (weekday or
                  weekend) and the same half hour of departure
  3. live-now   - median time of the same-route trips that ARRIVED at JFK in the
                  30 minutes before you leave (history if fewer than 3)
  4. neighbours - history x (1 + learned correction) from three live signals:
                  the live-now ratio, and how slow (vs. usual for that half hour)
                  the taxis were that in the last 15 minutes finished a trip
                  (a) that started in Midtown, going anywhere else, and
                  (b) that ended at JFK, coming from anywhere else.
                  Weights: least squares on the training trips only.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from bisect import bisect_left
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIDTOWN = (161, 162, 163, 164, 230)
JFK = (132,)
DEFAULT_SPLIT = "2026-04-13"
LIVE_WINDOW_MIN = 30
NBR_WINDOW_MIN = 15
STATUS = ("REAL data: NYC TLC yellow-taxi trips, Mar-Apr 2026, Midtown -> JFK. "
          "Predictors and errors are Homodyne's own computation, not Google's.")

# ---------------------------------------------------------------- build (raw -> derived)
BUILD_SQL = """
create table t as
select tpep_pickup_datetime pu, tpep_dropoff_datetime dof, trip_distance dist,
       PULocationID a, DOLocationID b,
       date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) / 60.0 dur
from read_parquet(?) where tpep_pickup_datetime >= '2026-03-01' and tpep_pickup_datetime < '2026-05-01'
"""


def build(raw: Path, out: Path, origin=MIDTOWN, dest=JFK, name="midtown_jfk") -> None:
    import duckdb  # only the build step needs it

    files = sorted(str(p) for p in raw.glob("yellow_tripdata_2026-0[34].parquet"))
    if len(files) != 2:
        sys.exit(f"expected yellow_tripdata_2026-03/04.parquet in {raw}")
    con = duckdb.connect()
    con.execute(BUILD_SQL, [files])
    o, d = ",".join(map(str, origin)), ",".join(map(str, dest))
    # route trips: plausible distance (12-25 mi) and duration (10-180 min)
    route = con.execute(f"""select pu, dur from t where a in ({o}) and b in ({d})
        and dist between 12 and 25 and dur between 10 and 180 order by pu""").fetchall()
    # neighbour trips (not on the route), as (dropoff, mph)
    nbr_out = con.execute(f"""select dof, dist / (dur / 60) from t where a in ({o}) and b not in ({d})
        and dist between 0.5 and 30 and dur between 2 and 120 order by dof""").fetchall()
    nbr_in = con.execute(f"""select dof, dist / (dur / 60) from t where b in ({d}) and a not in ({o})
        and dist between 0.5 and 40 and dur between 2 and 150 order by dof""").fetchall()
    n_all = con.execute(f"select count(*) from t where a in ({o}) and b in ({d})").fetchone()[0]

    def window_median(rows, times, t):
        lo, hi = bisect_left(times, t - timedelta(minutes=NBR_WINDOW_MIN)), bisect_left(times, t)
        v = [r[1] for r in rows[lo:hi]]
        return (round(statistics.median(v), 2), len(v)) if v else ("", 0)

    t_out, t_in = [r[0] for r in nbr_out], [r[0] for r in nbr_in]
    out.mkdir(parents=True, exist_ok=True)
    with open(out / f"{name}_trips.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pickup", "minutes", "nbr_out_mph", "nbr_out_n", "nbr_in_mph", "nbr_in_n"])
        for pu, dur in route:
            w.writerow([pu.strftime("%Y-%m-%d %H:%M:%S"), round(dur, 2),
                        *window_median(nbr_out, t_out, pu), *window_median(nbr_in, t_in, pu)])
    prof = con.execute(f"""select hour(pu), count(*), quantile_cont(dur, .1), median(dur), quantile_cont(dur, .9)
        from t where a in ({o}) and b in ({d}) and dist between 12 and 25 and dur between 10 and 180
        and dayofweek(pu) between 1 and 5 group by 1 order by 1""").fetchall()
    with open(out / "hourly_profile.csv" if name == "midtown_jfk" else out / f"{name}_hourly.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["weekday_departure_hour", "trips", "p10_min", "median_min", "p90_min"])
        for h, n, p10, med, p90 in prof:
            w.writerow([h, n, round(p10, 1), round(med, 1), round(p90, 1)])
    print(f"route trips kept {len(route)} of {n_all}; neighbour trips {len(nbr_out)} out, {len(nbr_in)} in")


# ---------------------------------------------------------------- race (stdlib only)
def load(path: Path) -> list[dict]:
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            pu = datetime.strptime(r["pickup"], "%Y-%m-%d %H:%M:%S")
            m = float(r["minutes"])
            rows.append({"pu": pu, "min": m, "arr": pu + timedelta(minutes=m),
                         "out": float(r["nbr_out_mph"]) if r["nbr_out_mph"] else None,
                         "in": float(r["nbr_in_mph"]) if r["nbr_in_mph"] else None})
    rows.sort(key=lambda r: r["pu"])
    return rows


def slot(t: datetime) -> tuple[int, int]:
    """(1 if weekend else 0, half hour of the day 0..47)."""
    return int(t.weekday() >= 5), t.hour * 2 + t.minute // 30


def median_by_slot(rows, key, min_n=5):
    groups: dict = {}
    for r in rows:
        if r[key] is not None:
            groups.setdefault(slot(r["pu"]), []).append(r[key])
    return {k: statistics.median(v) for k, v in groups.items() if len(v) >= min_n}


def solve(a, b):
    """Solve the n x n linear system a x = b (Gaussian elimination with pivoting)."""
    n = len(b)
    m = [row[:] + [bb] for row, bb in zip(a, b)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[p] = m[p], m[c]
        for r in range(n):
            if r != c and m[c][c]:
                f = m[r][c] / m[c][c]
                m[r] = [x - f * y for x, y in zip(m[r], m[c])]
    return [m[i][n] / m[i][i] if m[i][i] else 0.0 for i in range(n)]


solve3 = solve  # older name, kept for the selftest


def fit(train, feats):
    """Least-squares weights for history x (1 + sum w_i f_i), training trips only."""
    ata = [[sum(r[i] * r[j] for r in train) for j in feats] for i in feats]
    atb = [sum(r[i] * (r["min"] / r["hist"] - 1) for r in train) for i in feats]
    return solve(ata, atb)


# ablation: which live signals the neighbours predictor may use (history alone = no signal)
ABLATIONS = (("history only", ()), ("history + own-route live ratio", ("f_live",)),
             ("history + 2 neighbour signals", ("f_out", "f_in")),
             ("history + all 3 (= neighbours)", ("f_live", "f_out", "f_in")))


def race(rows: list[dict], split: datetime, ablation: bool = False) -> dict:
    train = [r for r in rows if r["pu"] < split]
    test = [r for r in rows if r["pu"] >= split]
    if len(train) < 20 or len(test) < 5:
        raise ValueError("not enough trips on one side of the split")
    const = statistics.median(r["min"] for r in train)
    hist_tab = median_by_slot(train, "min")
    day_med = {d: statistics.median([r["min"] for r in train if slot(r["pu"])[0] == d] or [const]) for d in (0, 1)}
    hist = lambda t: hist_tab.get(slot(t), day_med[slot(t)[0]])
    base_out, base_in = median_by_slot(train, "out"), median_by_slot(train, "in")

    by_arr = sorted(rows, key=lambda r: r["arr"])
    arr_t = [r["arr"] for r in by_arr]
    n_fallback = 0
    for r in rows:  # features known at the moment of departure
        r["hist"] = hist(r["pu"])
        lo = bisect_left(arr_t, r["pu"] - timedelta(minutes=LIVE_WINDOW_MIN))
        hi = bisect_left(arr_t, r["pu"])
        recent = by_arr[lo:hi]
        if len(recent) >= 3:
            r["live"] = statistics.median(x["min"] for x in recent)
            r["f_live"] = statistics.median(x["min"] / hist(x["pu"]) for x in recent) - 1
        else:
            r["live"], r["f_live"] = r["hist"], 0.0
            n_fallback += r["pu"] >= split
        k = slot(r["pu"])
        r["f_out"] = base_out[k] / r["out"] - 1 if r["out"] and k in base_out else 0.0
        r["f_in"] = base_in[k] / r["in"] - 1 if r["in"] and k in base_in else 0.0

    feats = ("f_live", "f_out", "f_in")
    w = fit(train, feats)
    for r in rows:
        r["const"] = const
        r["nbr"] = r["hist"] * (1 + sum(wi * r[f] for wi, f in zip(w, feats)))

    names = ("const", "hist", "live", "nbr")
    mae = lambda rs, p: round(statistics.fmean(abs(r[p] - r["min"]) for r in rs), 2)
    rush = [r for r in test if r["pu"].weekday() < 5 and 13 <= r["pu"].hour <= 17]
    bias_hours = {}
    for h0, h1, label in ((14, 15, "14:00-15:59"), (18, 19, "18:00-19:59")):
        rs = [r for r in test if r["pu"].weekday() < 5 and h0 <= r["pu"].hour <= h1]
        bias_hours[label] = {"trips": len(rs), **{p: round(statistics.fmean(r[p] - r["min"] for r in rs), 1) for p in names[1:]}}
        # the trip whose live-now error is closest to the median live-now error of that window
        errs = sorted(r["live"] - r["min"] for r in rs)
        med = errs[len(errs) // 2]
        ex = min(rs, key=lambda r: (abs(r["live"] - r["min"] - med), r["pu"]))
        bias_hours[label]["typical_trip"] = {"depart": ex["pu"].strftime("%a %d %b %Y %H:%M"), "actual": round(ex["min"], 1),
                                             **{p: round(ex[p], 1) for p in names}}
    abl = {}
    if ablation:
        for label, fs in ABLATIONS:
            wa = fit(train, fs) if fs else []
            abl[label] = {"weights": dict(zip(fs, (round(x, 3) for x in wa))),
                          "mae_min": round(statistics.fmean(abs(r["hist"] * (1 + sum(wi * r[f] for wi, f in zip(wa, fs)))
                                                                 - r["min"]) for r in test), 2)}
    by_hour = {}
    for r in test:
        if r["pu"].weekday() < 5:
            by_hour.setdefault(r["pu"].hour, []).append(r)
    return {
        "status": STATUS,
        "split": f"train: trips that started {rows[0]['pu']:%Y-%m-%d} .. {split - timedelta(days=1):%Y-%m-%d}; "
                 f"test: {split:%Y-%m-%d} .. {rows[-1]['pu']:%Y-%m-%d}",
        "train_trips": len(train), "test_trips": len(test),
        "mean_test_trip_min": round(statistics.fmean(r["min"] for r in test), 1),
        "constant_min": round(const, 1),
        "mae_min": {p: mae(test, p) for p in names},
        "mae_weekday_13_18_min": {p: mae(rush, p) for p in names}, "n_weekday_13_18": len(rush),
        "mean_signed_error_min": {p: round(statistics.fmean(r[p] - r["min"] for r in test), 1) for p in names},
        "share_too_short": {p: round(sum(r[p] < r["min"] for r in test) / len(test), 3) for p in names},
        "share_off_by_more_than_15min": {p: round(sum(abs(r[p] - r["min"]) > 15 for r in test) / len(test), 3) for p in names},
        "neighbour_weights": dict(zip(feats, (round(x, 3) for x in w))),
        "live_now_fallbacks_in_test": n_fallback,
        "signed_error_by_window_min": bias_hours,
        "live_now_mean_signed_error_by_weekday_hour": {h: round(statistics.fmean(r["live"] - r["min"] for r in rs), 1)
                                                       for h, rs in sorted(by_hour.items()) if len(rs) >= 20},
        **({"ablation_mae_min": abl} if ablation else {}),
    }


def report(res: dict) -> str:
    lab = {"const": "1 constant", "hist": "2 history", "live": "3 live-now", "nbr": "4 neighbours"}
    out = [res["status"], res["split"],
           f"train {res['train_trips']} trips · test {res['test_trips']} trips · mean test trip {res['mean_test_trip_min']} min",
           "", f"{'predictor':<14}{'MAE all':>9}{'MAE wkday 13-18h':>18}{'off >15 min':>13}"]
    for p, name in lab.items():
        out.append(f"{name:<14}{res['mae_min'][p]:>9.2f}{res['mae_weekday_13_18_min'][p]:>18.2f}"
                   f"{100 * res['share_off_by_more_than_15min'][p]:>12.1f}%")
    out.append("mean signed error (minus = too short): " + " · ".join(f"{lab[p][2:]} {v:+}" for p, v in res["mean_signed_error_min"].items()))
    out.append("")
    for win, b in res["signed_error_by_window_min"].items():
        ex = b["typical_trip"]
        out.append(f"weekday {win} ({b['trips']} test trips) mean signed error: history {b['hist']:+}, "
                   f"live-now {b['live']:+}, neighbours {b['nbr']:+} min")
        out.append(f"   typical trip {ex['depart']}: actual {ex['actual']} · constant {ex['const']} · history {ex['hist']}"
                   f" · live-now {ex['live']} · neighbours {ex['nbr']}")
    out.append(f"neighbour weights {res['neighbour_weights']} · live-now fell back to history {res['live_now_fallbacks_in_test']}x")
    if "ablation_mae_min" in res:
        out.append("")
        out.append("ablation (same fit, fewer live signals), test MAE:")
        for label, a in res["ablation_mae_min"].items():
            out.append(f"   {label:<32}{a['mae_min']:>6.2f}  weights {a['weights']}")
    return "\n".join(out)


# ---------------------------------------------------------------- selftest (offline, synthetic)
def _synthetic_rows():
    """Two weeks of fake trips: slow 15:00-18:00 on weekdays, worse on two Wednesdays; neighbours slow exactly when the route is."""
    rows, t = [], datetime(2026, 1, 5, 0, 0)
    while t < datetime(2026, 1, 19):
        jam = t.weekday() < 5 and 15 <= t.hour < 18
        extra = 20.0 if jam else 0.0
        if t.day in (7, 14) and jam:
            extra = 45.0  # one bad day in training, one in test: only live signals can know
        m = 40.0 + extra
        rows.append({"pu": t, "min": m, "arr": t + timedelta(minutes=m),
                     "out": 12.0 * 40 / m, "in": 30.0 * 40 / m})
        t += timedelta(minutes=10)
    return rows


def selftest() -> None:
    assert slot(datetime(2026, 4, 18, 7, 45)) == (1, 15)   # Saturday 07:45
    assert slot(datetime(2026, 4, 13, 0, 10)) == (0, 0)
    x = solve3([[2, 0, 0], [0, 4, 0], [1, 0, 1]], [2, 8, 3])
    assert [round(v, 6) for v in x] == [1, 2, 2], x
    res = race(_synthetic_rows(), datetime(2026, 1, 12))
    m = res["mae_min"]
    assert res["train_trips"] == 7 * 144 and res["test_trips"] == 7 * 144, res
    assert m["hist"] < m["const"], m          # history knows the daily jam
    assert m["nbr"] < m["hist"], m            # live neighbours catch the bad Wednesday
    ab = race(_synthetic_rows(), datetime(2026, 1, 12), ablation=True)["ablation_mae_min"]
    assert ab["history only"]["mae_min"] == m["hist"], ab
    assert ab["history + all 3 (= neighbours)"]["mae_min"] == m["nbr"], ab
    assert res["constant_min"] == 40.0
    # live-now lags: when the jam starts it is too low, when it ends too high
    lt = res["live_now_mean_signed_error_by_weekday_hour"]
    assert lt[15] < 0 < lt[18], lt
    # a CSV round trip keeps the rows
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.csv"
        with open(p, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["pickup", "minutes", "nbr_out_mph", "nbr_out_n", "nbr_in_mph", "nbr_in_n"])
            w.writerow(["2026-04-13 08:00:00", 61.5, 9.1, 40, "", 0])
        r = load(p)[0]
        assert r["min"] == 61.5 and r["out"] == 9.1 and r["in"] is None
        assert r["arr"] == datetime(2026, 4, 13, 9, 1, 30)
    print("selftest ok")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("build", help="raw TLC parquet -> derived CSV (needs duckdb)")
    b.add_argument("--raw", type=Path, default=HERE / "cache/tlc")
    b.add_argument("--out", type=Path, default=HERE / "derived")
    b.add_argument("--reverse", action="store_true", help="JFK -> Midtown instead (robustness; not committed)")
    r = sub.add_parser("race", help="run the four predictors on the derived CSV")
    r.add_argument("--csv", type=Path, default=HERE / "derived/midtown_jfk_trips.csv")
    r.add_argument("--split", default=DEFAULT_SPLIT)
    r.add_argument("--json", action="store_true", help="print JSON and write derived/results.json (default split only)")
    r.add_argument("--ablation", action="store_true", help="also report MAE with subsets of the live signals")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    if a.cmd == "build":
        if a.reverse:
            build(a.raw, a.out, JFK, MIDTOWN, "jfk_midtown")
        else:
            build(a.raw, a.out)
        return 0
    if a.cmd == "race":
        res = race(load(a.csv), datetime.strptime(a.split, "%Y-%m-%d"), a.ablation)
        if a.json:
            text = json.dumps(res, indent=2, ensure_ascii=False)
            print(text)
            if a.split == DEFAULT_SPLIT and a.csv == HERE / "derived/midtown_jfk_trips.csv" and not a.ablation:
                (HERE / "derived/results.json").write_text(text + "\n")
        else:
            print(report(res))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
