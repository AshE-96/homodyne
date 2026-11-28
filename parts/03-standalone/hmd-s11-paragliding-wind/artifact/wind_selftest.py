"""wind_selftest.py · HMD-S11 · offline checks (no network, no keys). Run: python3 -I artifact/wind_live.py --selftest"""
import math
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grib2_point as gp  # noqa: E402
import wind_core as wc  # noqa: E402

FAILS = []


def check(name, ok, detail=''):
    print(('ok    ' if ok else 'FAIL  ') + name + (f'  ({detail})' if detail else ''))
    if not ok:
        FAILS.append(name)


def close(a, b, tol):
    return a is not None and b is not None and abs(a - b) <= tol


def units():
    check('12 mph = 19.3 km/h (USHPA P2 base wind)', close(wc.mph_to_kmh(12), 19.31, 0.01))
    check('15 / 18 mph = 24.1 / 29.0 km/h', close(wc.mph_to_kmh(15), 24.14, 0.01) and close(wc.mph_to_kmh(18), 28.97, 0.01))
    check('10 kt = 18.52 km/h; 1 m/s = 3.6 km/h', close(wc.kt_to_kmh(10), 18.52, 1e-9) and close(wc.ms_to_kmh(1), 3.6, 1e-12))
    check('200 / 500 fpm = 1.02 / 2.54 m/s', close(200 * 0.3048 / 60, 1.016, 0.001) and close(500 * 0.3048 / 60, 2.54, 0.001))
    t = wc.THRESHOLDS
    check('thresholds match the converted USHPA numbers (rounded)',
          t['wind']['amber'] == round(wc.mph_to_kmh(12)) and t['wind']['red'] == round(wc.mph_to_kmh(15))
          and t['gust']['amber'] == round(wc.mph_to_kmh(15)) and t['gust']['red'] == round(wc.mph_to_kmh(18)))


def components():
    u, v = wc.uv_from(36, 270)                    # westerly 36 km/h = 10 m/s, blowing towards the east
    check('wind from 270° -> u = +10 m/s, v = 0', close(u, 10, 1e-9) and close(v, 0, 1e-9), f'{u:.3f}, {v:.3f}')
    check('round trip speed / direction (8 directions)',
          all(close(wc.speed_kmh(*wc.uv_from(20, d)), 20, 1e-9) and close(wc.direction_from(*wc.uv_from(20, d)), d % 360, 1e-6)
              for d in range(0, 360, 45)))
    h, c = wc.takeoff_components(20, 180, 180)
    check('straight up a south-facing slope: all headwind', close(h, 20, 1e-9) and close(c, 0, 1e-9))
    h, c = wc.takeoff_components(20, 225, 180)
    check('45° off: head = cross = 14.1 km/h, cross from the right', close(h, 14.14, 0.01) and close(c, 14.14, 0.01))
    h, _ = wc.takeoff_components(20, 0, 180)
    check('from behind the slope: headwind -20 (tailwind)', close(h, -20, 1e-9))
    check('angle_diff wraps: 350° vs 10° = 20°', wc.angle_diff(350, 10) == 20)


def gusts():
    check('gust factor 30 / 20 = 1.5', close(wc.gust_factor(30, 20), 1.5, 1e-12))
    check('gust factor undefined in calm air', wc.gust_factor(10, 0.5) is None)
    check('gust spread 30 - 20 = 10; never negative', wc.gust_spread(30, 20) == 10 and wc.gust_spread(15, 20) == 0)


def profile():
    lv = [dict(p=850, gh=1500.0, u=2.0, v=0.0, t=15.0), dict(p=700, gh=3100.0, u=10.0, v=0.0, t=2.0),
          dict(p=600, gh=4350.0, u=14.0, v=4.0, t=-6.0)]
    col = wc.column(lv, 1850, u10=1.0, v10=0.0, t2=20.0, td2=4.0)
    check('levels below the model ground are dropped', [l['p'] for l in col] == ['10m', 700, 600])
    w = wc.wind_at(col, 2325)
    want = (1 + (2325 - 1860) / (3100 - 1860) * 9) * 3.6     # u linear in height between 10 m point and 700 hPa
    check('height interpolation of u between the 10 m point and 700 hPa', close(w['speed'], want, 0.06), f'{w["speed"]} vs {want:.2f}')
    s = wc.shear(col, 2325, 3325)
    check('shear is the vector change, not the speed change', s is not None and s['vector'] > 0)
    check('time interpolation: halfway is the mean; none outside',
          wc.interp_time([(3, 10.0), (6, 16.0)], [4.5, 7]) == [13.0, None])


def thermals():
    check('cloud base: 16 K spread -> 2,000 m above ground', close(wc.cloudbase(20, 4, 1850), 3850, 1e-9))
    col = [dict(p='10m', gh=1860, t=20.0), dict(p=750, gh=2500.0, t=13.0), dict(p=700, gh=3100.0, t=6.0),
           dict(p=600, gh=4350.0, t=-2.0)]
    top = wc.thermal_top(20.0, 1850, col)
    par = lambda z: 20 - 9.8 * (z - 1852) / 1000  # noqa: E731
    d1, d2 = 6.0 - par(3100), -2.0 - par(4350)          # buoyant at 700 hPa, not at 600 hPa
    want = 3100 + (0 - d1) / (d2 - d1) * 1250
    check('dry-parcel thermal top between 700 and 600 hPa', close(top, want, 1.0), f'{top} vs {want:.0f} m')
    stable = [dict(p='10m', gh=1860, t=5.0), dict(p=750, gh=2300.0, t=6.0), dict(p=700, gh=3100.0, t=0.0)]
    check('inversion right above the ground: thermal top = ground', close(wc.thermal_top(5.0, 1850, stable), 1852, 1e-9))
    coarse = [dict(p='10m', gh=1860, t=20.0), dict(p=700, gh=3100.0, t=2.0), dict(p=600, gh=4350.0, t=-6.0)]
    check('first level 1,250 m above the ground: no thermal top (too coarse)', wc.thermal_top(20.0, 1850, coarse) is None)
    ws = wc.w_star(200.0, 1500.0, 25.0, 800.0)
    rho = 80000 / (287.053 * 298.15)
    want = (9.80665 / 298.15 * 200 / (rho * 1004) * 1500) ** (1 / 3)
    check('Deardorff w*: 200 W/m2, zi 1,500 m -> about 2.1 m/s', close(ws, want, 1e-9) and 1.9 < ws < 2.3, f'{ws:.2f}')
    check('w* = 0 when the surface cools the air', wc.w_star(-20, 300, 5, 850) == 0.0)


def indicator():
    calm = wc.indicator(dict(wind=10, dir=185, gust=14, aloft=15, shear=8, w_star=0.6, cape=50), 180)
    check('light wind straight up the slope -> inside', calm['label'] == 'inside', str(calm['reasons']))
    strong = wc.indicator(dict(wind=26, dir=180, gust=34, aloft=30, shear=10, w_star=1.2, cape=0), 180)
    check('26 km/h with 34 gusts -> no', strong['label'] == 'no')
    tail = wc.indicator(dict(wind=12, dir=0, gust=15, aloft=15, shear=5, w_star=0.5, cape=0), 180)
    check('tailwind on launch -> no', tail['label'] == 'no')
    gappy = wc.indicator(dict(wind=10, dir=180), 180)
    check('missing inputs are reported, not treated as fine', set(gappy['missing']) >= {'gust', 'cape', 'thermal'})
    check('no label is ever "safe"', 'safe' not in wc.LABELS)


def stats():
    e = wc.errors([(10, 8), (12, 14), (20, 10)])
    check('bias / MAE / RMSE', e == dict(n=3, bias=3.3, mae=4.7, rmse=6.0), str(e))
    check('lag-1 autocorrelation of an alternating series is negative', wc.lag1_autocorr([1, -1, 1, -1, 1, -1]) < 0)
    check('effective n: 30 samples with r = 0.5 count as 10', wc.effective_n(30, 0.5) == 10.0)


def grib():
    """Template 5.0 (simple packing) on a synthetic 4x3 field, through the HMD-S06 decoder."""
    ni, nj, vals = 4, 3, [float(k) for k in range(12)]
    sec3 = bytearray(72)
    struct.pack_into('>IB', sec3, 0, 72, 3)
    struct.pack_into('>H', sec3, 12, 0)
    struct.pack_into('>II', sec3, 30, ni, nj)
    struct.pack_into('>ii', sec3, 46, 36_000_000, 50_000_000)
    struct.pack_into('>ii', sec3, 55, 35_500_000, 50_750_000)
    struct.pack_into('>II', sec3, 63, 250_000, 250_000)
    sec3[71] = 0
    nbits = 8
    s5 = struct.pack('>IBIHfhhBB', 21, 5, 12, 0, 0.0, 0, 0, nbits, 0)
    s6 = struct.pack('>IBB', 6, 6, 255)
    data = bytes(int(v) for v in vals)
    s7 = struct.pack('>IB', 5 + len(data), 7) + data
    body = bytes(sec3) + s5 + s6 + s7 + b'7777'
    msg = b'GRIB' + b'\x00\x00' + bytes([0, 2]) + struct.pack('>Q', 16 + len(body)) + body
    r = gp.read_points(msg, [(35.75, 50.25), (35.875, 50.375)])
    v = [p['value'] for p in r['points']]
    check('GRIB2 5.0 decode: exact grid point and a bilinear midpoint', close(v[0], 5.0, 1e-9) and close(v[1], 3.5, 1e-9), str(v))


def saved_eval():
    """The committed evaluation file: its statistics must follow from its own pairs (no network)."""
    import json
    import wind_eval as we
    p = HERE / 'derived' / 'eval-2025-04.json'
    if not p.exists():
        check('saved evaluation present', False, 'derived/eval-2025-04.json missing')
        return
    e = json.loads(p.read_text(encoding='utf-8'))
    again = we.stats(e['pairs'])
    check('saved evaluation: statistics recompute from its pairs',
          json.dumps(again, sort_keys=True) == json.dumps(e['stats'], sort_keys=True))
    check('saved evaluation: 30 days x 2 times, every case observed', len(e['pairs']) == 60
          and all(x['obs']['wind'] is not None for x in e['pairs']))


def run():
    for f in (units, components, gusts, profile, thermals, indicator, stats, grib, saved_eval):
        try:
            f()
        except Exception as e:  # a crash is a failure, with its reason
            check(f.__name__ + ' raised', False, repr(e))
    print('selftest ' + ('ok' if not FAILS else f'FAILED ({len(FAILS)})'))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(run())
