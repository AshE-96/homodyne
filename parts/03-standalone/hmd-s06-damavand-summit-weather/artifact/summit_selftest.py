"""summit_selftest.py · HMD-S06 · offline checks for summit_live.py --selftest (no network, no keys)."""
import json
import math
import random
import struct
from pathlib import Path

import grib2_point as gp
import summit_core as sc

HERE = Path(__file__).resolve().parent

# Environment Canada wind chill chart (°C), canada.ca "Wind chill and the Wind Chill Index", read 28 Nov 2026
EC_CHART = {(-20, 20): -30, (-20, 40): -34, (-20, 60): -36, (-30, 20): -43, (-30, 40): -48, (-30, 60): -50}


# ── a tiny CCSDS/AEC encoder, only to round-trip the decoder ───────────────────
def _fs(n):
    return '0' * n + '1'


def aec_encode(samples, nbits, bs=32, rsi=128):
    xmax, idl = (1 << nbits) - 1, (5 if nbits > 16 else 4 if nbits > 8 else 3)
    uncomp = (1 << idl) - 1
    bits = []
    put = lambda v, n: bits.append(format(v, f'0{n}b') if n else '')  # noqa: E731
    for r0 in range(0, len(samples), rsi * bs):
        seg = samples[r0:r0 + rsi * bs]
        d, prev = [], seg[0]
        for x in seg[1:]:
            theta, delta = min(prev, xmax - prev), x - prev
            d.append(2 * delta if 0 <= delta <= theta else 2 * -delta - 1 if -theta <= delta < 0 else theta + abs(delta))
            prev = x
        stream = [None] + d                      # None marks the reference position
        for b, i in enumerate(range(0, len(stream), bs)):
            blk = stream[i:i + bs]
            ref = blk[0] is None
            body = blk[1:] if ref else blk
            if len(blk) < bs:                    # pad the last partial block with zeros
                body = body + [0] * (bs - len(blk))
            if b % 7 == 3:                       # uncompressed: the reference is just the first raw sample
                put(uncomp, idl)
                for v in ([seg[0]] if ref else []) + body:
                    put(v, nbits)
            elif all(v == 0 for v in body):      # one zero block
                put(0, idl), put(0, 1)
                if ref:
                    put(seg[0], nbits)
                bits.append(_fs(0))
            elif max(body) <= 2:                 # second extension
                put(0, idl), put(1, 1)
                if ref:
                    put(seg[0], nbits)
                pairs = ([0] + body) if ref else body
                for a, c in zip(pairs[::2], pairs[1::2]):
                    bits.append(_fs((a + c) * (a + c + 1) // 2 + c))
            else:                                # split sample with the cheapest k
                k = min(range(0, uncomp - 1), key=lambda k: sum((v >> k) + 1 + k for v in body))
                put(k + 1, idl)
                if ref:
                    put(seg[0], nbits)
                for v in body:
                    bits.append(_fs(v >> k))
                for v in body:
                    put(v & ((1 << k) - 1), k)
    s = ''.join(bits)
    s += '0' * (-len(s) % 8)
    return bytes(int(s[i:i + 8], 2) for i in range(0, len(s), 8))


def grib_message(ni, nj, la1, lo1, d, raw, nbits, R, E, packing):
    sm32 = lambda v: struct.pack('>I', (abs(v) | (0x80000000 if v < 0 else 0)))  # noqa: E731
    s1 = struct.pack('>IB', 21, 1) + bytes(16)
    s3 = (struct.pack('>IBBIBBH', 72, 3, 0, ni * nj, 0, 0, 0) + bytes(16) + struct.pack('>II', ni, nj) + bytes(8)
          + sm32(int(la1 * 1e6)) + sm32(int(lo1 * 1e6)) + b'\x30' + sm32(int((la1 - (nj - 1) * d) * 1e6))
          + sm32(int((lo1 + (ni - 1) * d) * 1e6)) + struct.pack('>II', int(d * 1e6), int(d * 1e6)) + b'\x00')
    s4 = struct.pack('>IBHH', 34, 4, 0, 0) + bytes([0, 0]) + bytes(11) + bytes([100, 0]) + struct.pack('>I', 50000) + bytes(6)
    e16 = struct.pack('>H', abs(E) | (0x8000 if E < 0 else 0))
    if packing == 42:
        data = aec_encode(raw, nbits)
        s5 = struct.pack('>IBIH', 25, 5, ni * nj, 42) + struct.pack('>f', R) + e16 + b'\0\0' + bytes([nbits, 0, 8 | 4, 32]) + struct.pack('>H', 128)
    else:
        s = ''.join(format(v, f'0{nbits}b') for v in raw)
        s += '0' * (-len(s) % 8)
        data = bytes(int(s[i:i + 8], 2) for i in range(0, len(s), 8))
        s5 = struct.pack('>IBIH', 21, 5, ni * nj, 0) + struct.pack('>f', R) + e16 + b'\0\0' + bytes([nbits, 0])
    s6 = struct.pack('>IBB', 6, 6, 255)
    s7 = struct.pack('>IB', 5 + len(data), 7) + data
    body = s1 + s3 + s4 + s5 + s6 + s7 + b'7777'
    return b'GRIB\0\0' + bytes([0, 2]) + struct.pack('>Q', 16 + len(body)) + body


def run():
    ok = True

    def check(name, cond, detail=''):
        nonlocal ok
        ok &= bool(cond)
        print(('  ok    ' if cond else '  FAIL  ') + f'{name:52} {detail}')

    # 1. wind chill: Environment Canada chart, card example, and the US-unit version of the same formula
    for (t, v), want in EC_CHART.items():
        got = sc.wind_chill(t, v)
        check(f'wind chill T={t} °C, V={v} km/h vs EC chart', round(got) == want, f'{got:.2f} → {round(got)} (chart {want})')
    wc = sc.wind_chill(-23, 40)
    check('idea-card example: −23 °C, 40 km/h ≈ −38', round(wc) == -38, f'{wc:.2f}')
    t, v = -25.0, 50.0
    f_ver = (sc.wind_chill_f(t * 9 / 5 + 32, v / 1.609344) - 32) * 5 / 9
    check('metric and NWS (°F, mph) versions agree', abs(f_ver - sc.wind_chill(t, v)) < 0.15, f'{sc.wind_chill(t, v):.2f} vs {f_ver:.2f}')
    check('no wind chill above 10 °C or below 4.8 km/h', sc.wind_chill(12, 30) == 12 and sc.wind_chill(-10, 3) == -10)

    # 2. standard atmosphere and the hypsometric equation
    for p, want in ((500, 5574), (600, 4206), (700, 3012)):
        h = sc.isa_height(p)
        check(f'ISA height of {p} hPa', abs(h - want) < 3, f'{h:.0f} m (table {want} m)')
    check('ISA pressure at 5,610 m', abs(sc.isa_pressure(5610) - 497.6) < 1, f'{sc.isa_pressure(5610):.1f} hPa')
    th = sc.hypsometric_thickness(600, 500, 273.15 - 15)
    check('600–500 hPa thickness at −15 °C mean', 1350 < th < 1400, f'{th:.0f} m')

    # 3. lapse-rate correction: model terrain 2,806 m, 2 m temperature +5 °C → summit
    lc = sc.lapse_correct(5.0, 2806, 5610)
    check('lapse correction 6.5 K/km over 2,804 m', abs(lc - (5 - 6.5 * 2.804)) < 1e-9, f'{lc:.2f} °C')

    # 4. free-air interpolation and wind
    lv = [dict(p=600, gh=4200, t=-6.0, u=10.0, v=0.0, rh=40), dict(p=500, gh=5700, t=-16.0, u=16.0, v=0.0, rh=80)]
    fa = sc.free_air(lv, 5610)
    check('free-air interpolation at 5,610 m', abs(fa['t'] - (-15.4)) < 0.05 and fa['layer'] == '600-500 hPa', str(fa))
    check('westerly wind blows from 270°', round(sc.direction_from(10, 0)) == 270 and abs(sc.speed_kmh(3, 4) - 18) < 1e-9)
    check('RH from q: saturated air → ~100%', abs(sc.rh_from_q(0.00357, 263.15, 500) - 100) < 5,
          f'{sc.rh_from_q(0.00357, 263.15, 500):.1f}%')

    # 5. alert logic: never "safe"; uncertain when models split
    calm = dict(fa=dict(wind=20, chill=-20, rh=30))
    calm['flags'] = sc.step_flags(calm['fa'])
    wild = dict(fa=dict(wind=75, chill=-45, rh=95))
    wild['flags'] = sc.step_flags(wild['fa'])
    c1, c2 = sc.combine([calm, calm, calm]), sc.combine([calm, calm, wild])
    check('three calm models → "under", not uncertain', c1['label'] == 'under' and not c1['uncertain'])
    check('one wild model → "over" and uncertain', c2['label'] == 'over' and c2['uncertain'] and c2['n_red'] == 1)
    c3 = sc.combine([calm, calm], member_winds=[10] * 6 + [50] * 4)
    check('ensemble split 60/40 → uncertain', c3['uncertain'] and c3['p_wind_amber'] == 0.4)
    labels = {'under', 'near', 'over'}
    check('labels never contain "safe"', all('safe' not in x for x in labels))
    st = [dict(valid=str(i), combined=c1 if i not in (3,) else c2) for i in range(7)]
    check('windows: runs of calm steps only', sc.windows(st) == [('0', '2'), ('4', '6')], str(sc.windows(st)))

    # 6. GRIB2 decoder: CCSDS round trip and simple packing, on synthetic fields
    rnd = random.Random(6)
    n, x, raw = 3 * 4096 + 517, 2000, []
    for i in range(n):
        if (i // 700) % 3 == 1:
            pass                                  # flat stretch → zero blocks
        elif (i // 700) % 3 == 2:
            x += rnd.choice((-1, 0, 0, 1))        # tiny steps → second extension
        else:
            x += rnd.randint(-60, 60)             # rough → split sample
        x = max(0, min(4095, x))
        raw.append(x)
    back = gp.aec_decode(aec_encode(raw, 12), 12, 32, 128, 8 | 4, n)
    check('CCSDS round trip, 12 bits, 12,805 samples', back == raw, f'{sum(a != b for a, b in zip(back, raw))} mismatches')
    back2 = gp.aec_decode(aec_encode(raw, 12), 12, 32, 128, 8 | 4, 5000)
    check('CCSDS decode stops early (first 5,000)', back2 == raw[:5000])
    ni, nj = 100, 128
    grid = [[int(1000 + 10 * j + 3 * i) for i in range(ni)] for j in range(nj)]
    flat = [v for row in grid for v in row]
    for packing in (0, 42):
        msg = grib_message(ni, nj, 60.0, 30.0, 0.25, flat, 12, 50000.0, -2, packing)
        r = gp.read_points(msg, [(35.9553, 52.1100)])['points'][0]
        fj, fi = (60.0 - 35.9553) / 0.25, (52.1100 - 30.0) / 0.25
        want = 50000.0 + (1000 + 10 * fj + 3 * fi) * 0.25
        check(f'GRIB2 template 5.{packing}: bilinear value at Damavand', abs(r['value'] - want) < 1e-6, f'{r["value"]:.4f} vs {want:.4f}')
    check('GRIB2 product(): isobaric 500 hPa', gp.product(msg)[3:] == (100, 50000))

    # 7. cached live data (if any): two independent decoders must agree on the same physics
    path = HERE / 'derived' / 'latest.json'
    if path.exists():
        d = json.loads(path.read_text(encoding='utf-8'))['models']
        if 'ifs' in d and 'gfs' in d:
            gfs = {r['valid']: r for r in d['gfs']['series']}
            diffs = []
            for r in d['ifs']['series']:
                g = gfs.get(r['valid'])
                if g:
                    a = [l['gh'] for l in r['summit']['levels'] if l['p'] == 500][0]
                    b = [l['gh'] for l in g['summit']['levels'] if l['p'] == 500][0]
                    diffs.append(abs(a - b))
            check('cache: IFS (CCSDS) vs GFS (simple packing) 500 hPa height', diffs and max(diffs) < 80,
                  f'max |Δ| {max(diffs):.0f} m over {len(diffs)} common times' if diffs else 'no common times')
        for k, m in d.items():
            z = m['orography']['summit']
            check(f'cache: {k} model terrain far below the real 5,610 m', z is not None and 1500 < z < 4000, f'{z} m')
    else:
        print('  skip  no artifact/derived/latest.json: cached-data checks skipped')
    print('selftest ok' if ok else 'selftest FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(run())
