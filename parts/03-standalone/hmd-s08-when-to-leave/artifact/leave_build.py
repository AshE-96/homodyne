#!/usr/bin/env python3
"""leave_build.py · HMD-S08 · raw NYC TLC yellow-taxi parquet -> artifact/derived/weekday_trips.csv

    python3 -I artifact/leave_build.py --raw <folder with yellow_tripdata_2026-03/04.parquet>

Needs the installed duckdb Python module (used at 1.5.5). Everything else in this artifact is standard
library only and reads the committed CSV, so you never need this script to record the episode.

The raw files are the same two monthly files HMD-009 uses (sha256 in derived/SOURCE.txt). If you do not
have them, download them (no key) into artifact/cache/tlc/ (git-ignored):
  https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-03.parquet
  https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-04.parquet

Output: one row per kept weekday (Mon-Fri) trip, pickups 2026-03-02 .. 2026-04-30:
  route   short code (see ROUTES)
  date    pickup date, YYYY-MM-DD
  dep     pickup clock time in whole minutes after midnight (meter engaged = "leaving")
  min     trip minutes, meter engaged -> disengaged, one decimal
"""
import argparse
import csv
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'derived' / 'weekday_trips.csv'
MIDTOWN = (161, 162, 163, 164, 230)          # same five zones as HMD-009
# code: (label, origin zones, destination zones, miles lo-hi, minutes lo-hi)
ROUTES = {
    'jfk':  ('Midtown -> JFK Airport', MIDTOWN, (132,), (12, 25), (10, 180)),
    'lga':  ('Midtown -> LaGuardia Airport', MIDTOWN, (138,), (6, 18), (5, 150)),
    'ewr':  ('Midtown -> Newark Airport', MIDTOWN, (1,), (12, 30), (10, 180)),
    'fidi': ('Upper East Side -> Financial District', (236, 237), (87, 88, 261, 13, 12), (4, 12), (5, 120)),
}
SHA = {'yellow_tripdata_2026-03.parquet': 'd7af794a7ac06cbbb5afb4d1df9e86d84f2e878584de708ff2ffca4bd7d234d9',
       'yellow_tripdata_2026-04.parquet': 'e03b82d5722a6b21d4fbce011afd8837495202c0b5db77ff0d8d15dd80834ba8'}


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def build(raw: Path):
    import duckdb  # only this step needs it
    files = [raw / n for n in SHA]
    for f in files:
        if not f.exists():
            sys.exit(f'missing {f}')
        if sha256(f) != SHA[f.name]:
            sys.exit(f'sha256 mismatch for {f.name}: the file changed upstream; see derived/SOURCE.txt')
    con = duckdb.connect()
    con.execute("""create table t as
        select tpep_pickup_datetime pu, trip_distance dist, PULocationID a, DOLocationID b,
               date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) / 60.0 dur
        from read_parquet(?) where tpep_pickup_datetime >= '2026-03-01' and tpep_pickup_datetime < '2026-05-01'
          and dayofweek(tpep_pickup_datetime) between 1 and 5""", [[str(f) for f in files]])
    rows, report = [], []
    for code, (label, o, d, (m0, m1), (t0, t1)) in ROUTES.items():
        os_, ds = ','.join(map(str, o)), ','.join(map(str, d))
        n_all = con.execute(f'select count(*) from t where a in ({os_}) and b in ({ds})').fetchone()[0]
        got = con.execute(f"""select pu, dur from t where a in ({os_}) and b in ({ds})
            and dist between {m0} and {m1} and dur between {t0} and {t1} order by pu""").fetchall()
        for pu, dur in got:
            rows.append((code, pu.strftime('%Y-%m-%d'), pu.hour * 60 + pu.minute, round(dur, 1)))
        report.append(f'{code:5} {label:40} kept {len(got):6} of {n_all:6} weekday records')
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['route', 'date', 'dep', 'min'])
        w.writerows(rows)
    print('\n'.join(report))
    print(f'wrote {OUT.relative_to(HERE.parent)}  ({len(rows)} rows, sha256 {sha256(OUT)})')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--raw', type=Path, default=HERE / 'cache' / 'tlc')
    build(ap.parse_args().raw)
