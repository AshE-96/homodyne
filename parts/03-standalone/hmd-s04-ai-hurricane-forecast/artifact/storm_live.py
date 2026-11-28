#!/usr/bin/env python3
"""storm_live.py · HMD-S04 · the live page for recording, standard library only.

    python3 -I artifact/storm_live.py              # build artifact/storm_live.html from storm_page.html + derived/*.json
    python3 -I artifact/storm_live.py --serve      # build, then serve on http://127.0.0.1:8766/storm_live.html
    python3 -I artifact/storm_live.py --selftest   # offline checks (great-circle maths, rules, our rebuild of NHC tables)
    python3 -I artifact/storm_build.py --fetch     # (once, needs network) download the public decks and re-derive

Three views (keys 1 2 3):
  1 · replay   a 2025 storm: best track, each model's forecast from one initial time, the NHC cone, errors live
  2 · errors   mean track / intensity error by lead time over a homogeneous sample, computed live from the case table
  3 · Gonu & Shaheen   the two Arabian Sea cyclones from IBTrACS, closest approach to Chabahar, Jask and Muscat
URL fixes a state for a take: ?view=replay&storm=AL13&init=2025102500&m=OFCL,GDMI · ?view=errors&kind=track&sample=nhc
"""
import argparse
import functools
import http.server
import json
import math
import random
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import storm_core as sc  # noqa: E402
import storm_build as sb  # noqa: E402

DER = HERE / 'derived'
PAGE, TEMPLATE = HERE / 'storm_live.html', HERE / 'storm_page.html'


def load(name):
    return json.loads((DER / name).read_text(encoding='utf-8'))


def build():
    data = dict(replay=load('replay-2025.json'), cases=load('cases-2025.json'), verify=load('verify-2025.json'),
                ni=load('north-indian.json'), land=load('land.json'))
    html = TEMPLATE.read_text(encoding='utf-8').replace('/*DATA*/', 'const DATA = ' + json.dumps(data, separators=(',', ':')) + ';')
    PAGE.write_text(html, encoding='utf-8')
    return PAGE


# ── selftest ─────────────────────────────────────────────────────────────────
FIX_B = """AL, 99, 2025090100,   , BEST,   0, 200N,  600W,  50, 1000, TS,  34
AL, 99, 2025090100,   , BEST,   0, 200N,  600W,  50, 1000, TS,  50
AL, 99, 2025090200,   , BEST,   0, 210N,  620W,  65,  990, HU,  34
AL, 99, 2025090300,   , BEST,   0, 230N,  650W,  45, 1000, EX,  34
AL, 99, 2025090106,   , BEST,   0, 202N,  605W,  55,  998, TS,  34
AL, 99, 2025090206,   , BEST,   0, 213N,  625W,  60,  995, HU,  34""".splitlines()
FIX_A = """AL, 99, 2025090100, 03, OFCL,  24, 211N,  621W,  60,    0, HU,  34
AL, 99, 2025090100, 03, OFCL,  24, 211N,  621W,  60,    0, HU,  50
AL, 99, 2025090100, 03, GDMI,  24, 210N,  620W,  70,    0,   ,  34
AL, 99, 2025090100, 03, OFCL,  48, 230N,  650W,  40,    0, EX,  34
AL, 99, 2025090100, 03, GDMI,  48, 231N,  651W,  40,    0,   ,  34
AL, 99, 2025090106, 03, OFCL,  24, 215N,  628W,  60,    0, HU,  34
AL, 99, 2025090103, 03, OFCL,  24, 215N,  628W,  60,    0, HU,  34
AL, 99, 2025090100, 03, IVCN,  24,   0N,    0W,  58,    0,   ,  34""".splitlines()


def check(cond, msg, fails):
    print(('ok    ' if cond else 'FAIL  ') + msg)
    if not cond:
        fails.append(msg)


def selftest():
    f = []
    # 1 · great-circle maths against values that follow from the definition of the sphere (R = 6371 km)
    q = math.pi / 2 * sc.R_EARTH_KM
    check(abs(sc.gc_km(0, 0, 0, 90) - q) < 1e-6 and abs(q - 10007.543) < 1e-3, f'quarter of the equator = {q:.3f} km', f)
    check(abs(sc.gc_km(0, 0, 90, 0) - q) < 1e-6, 'equator to pole = quarter circle', f)
    check(abs(sc.gc_km(10, 20, -10, -160) - 2 * q) < 1e-3, f'antipodes = {2 * q:.3f} km', f)
    d1 = sc.gc_km(0, 0, 1, 0)
    check(abs(d1 - 111.195) < 1e-3, f'1 degree of latitude = {d1:.3f} km', f)
    arcmin = sc.gc_km(20, -60, 20 + 1 / 60, -60)
    check(abs(arcmin - sc.KM_PER_NMI) / sc.KM_PER_NMI < 0.001, f'1 arc-minute = {arcmin:.4f} km ≈ 1 n mi (1.852)', f)
    eq = sc.gc_km(0, 0, 0, 1)
    p60 = sc.gc_km(60, 0, 60, 1)
    check(abs(p60 - eq * math.cos(math.radians(60))) < 0.02, f'1° of longitude at 60°N ({p60:.2f} km) ≈ half of the equator\'s', f)
    rng, worst = random.Random(7), 0.0
    for _ in range(2000):        # haversine against the spherical law of cosines (fine away from tiny distances)
        a, b, c, d = rng.uniform(-60, 60), rng.uniform(-180, 180), rng.uniform(-60, 60), rng.uniform(-180, 180)
        p1, p2 = math.radians(a), math.radians(c)
        cos_ = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(math.radians(d - b))
        lc = sc.R_EARTH_KM * math.acos(max(-1, min(1, cos_)))
        if lc > 50:
            worst = max(worst, abs(lc - sc.gc_km(a, b, c, d)))
    check(worst < 1e-6, f'haversine = law of cosines on 2000 random pairs (worst {worst:.1e} km)', f)
    check(abs(sc.gc_km(25.29, 60.64, 25.64, 57.77) - sc.gc_km(25.64, 57.77, 25.29, 60.64)) < 1e-9, 'symmetric', f)
    # 2 · ATCF parsing and the NHC verification rules on a hand-made storm
    check(sc.parse_latlon('300N') == 30.0 and sc.parse_latlon('576W') == -57.6 and sc.parse_latlon('1231E') == 123.1
          and sc.parse_latlon('45S') == -4.5, 'ATCF tenths: 300N, 576W, 1231E, 45S', f)
    best, fc = sc.parse_bdeck(FIX_B), sc.parse_adeck(FIX_A)
    check(len(best) == 5 and best['2025090200']['ty'] == 'HU', 'b-deck: one record per time (radii lines dropped)', f)
    check(fc['IVCN']['2025090100'][24] == (None, None, 58), 'intensity-only aid kept without a position', f)
    st = {'AL99': dict(best=best, fc=fc)}
    cs = sc.cases(st, ['OFCL', 'GDMI'])
    check(len(cs) == 1 and cs[0]['tau'] == 24, 'only 00Z+24h counts: 48h verifies on an extratropical point; 03Z is not synoptic; '
          '06Z has no GDMI (homogeneous)', f)
    exp = sc.gc_km(21.1, -62.1, 21.0, -62.0)
    check(abs(cs[0]['err']['OFCL'] - exp) < 1e-9 and cs[0]['err']['GDMI'] == 0.0, f'OFCL 24 h error {exp:.2f} km, GDMI 0', f)
    ci = sc.cases(st, ['OFCL', 'GDMI', 'IVCN'], kind='intensity')
    check(len(ci) == 1 and ci[0]['err'] == {'OFCL': 5, 'GDMI': 5, 'IVCN': 7}, 'intensity error = |forecast − best| kt', f)
    check(len(sc.cases(st, ['OFCL', 'GDMI'], homogeneous=False)) == 2, 'heterogeneous sample keeps the 06Z OFCL case', f)
    # 3 · our rebuild of NHC Tables 2 and 4 from the committed case table
    C, V = load('cases-2025.json'), load('verify-2025.json')
    again = sb.analyse(C['track'], C['intensity'])
    check(json.loads(json.dumps(again)) == V, 'verify-2025.json reproduces exactly from cases-2025.json', f)
    check(again['ours_t2']['n'] == sb.NHC_T2['n'], f'track sample size per lead = NHC Table 2: {sb.NHC_T2["n"]}', f)
    check(again['ours_t4']['n'] == sb.NHC_T4['n'], f'intensity sample size per lead = NHC Table 4: {sb.NHC_T4["n"]}', f)
    check(again['maxdiff_t2'] <= 2.5, f'track means within {again["maxdiff_t2"]:.1f} n mi of NHC (GDMI differs most)', f)
    other = max(abs(a - b) for m in sb.TRACK_SET if m != 'GDMI' for a, b in zip(again['ours_t2'][m], sb.NHC_T2[m]))
    check(other <= 1.05, f'every aid except GDMI within {other:.1f} n mi of NHC', f)
    check(again['maxdiff_t4'] <= 0.5, f'intensity means within {again["maxdiff_t4"]:.1f} kt of NHC', f)
    k = again['track_km']['t2']
    check(k['GDMI'][5] < k['OFCL'][5] and k['GDMI'][7] > k['OFCL'][7], f'72 h: GDMI {k["GDMI"][5]} < OFCL {k["OFCL"][5]} km; '
          f'120 h: GDMI {k["GDMI"][7]} > OFCL {k["OFCL"][7]} km', f)
    b = again['track_km']['t2_boot_storm']
    check(b[24]['lo'] < 0 < b[24]['hi'] and b[72]['hi'] < 0, '24 h storm-bootstrap interval includes zero; 72 h does not', f)
    # 4 · Gonu / Shaheen closest approaches recomputed from the committed track
    N = load('north-indian.json')
    g = round(sc.closest_approach(N['gonu']['track'], *sb.PLACES['Jask'])[0])
    check(g == N['gonu']['nearest']['Jask']['km'], f'Gonu passes {g} km from Jask (recomputed)', f)
    check(N['gonu']['peak_usa'][1] == 145 and N['gonu']['peak_imd'][2] == 'SUCS', 'Gonu peak: JTWC 145 kt, IMD super cyclonic storm', f)
    # 5 · the page: built, self-contained, and its JavaScript gives the same numbers as Python
    html = build().read_text(encoding='utf-8')
    check('const DATA = ' in html and '<script src' not in html and 'https://' not in html.split('<script>')[0],
          f'page built ({len(html) // 1024} KB), no external scripts or styles', f)
    node = shutil.which('node')
    if node:
        core = html.split('<script id="core">')[1].split('</script>')[0]
        chosen = ['OFCL', 'GDMI', 'EMXI']
        js = core + f"""
const C = {json.dumps(C)};
const r = homogMeans(C.track, C.track_models, {json.dumps(chosen)});
console.log(JSON.stringify({{n: r.n, g: r.GDMI, d: gcKm(25.29, 60.64, 25.64, 57.77)}}));"""
        out = json.loads(subprocess.run([node, '-e', js], capture_output=True, text=True, timeout=60).stdout)
        cs = sb.homog(sb.unpack(C['track'], sb.TRACK_SET), chosen)
        t = sc.table(cs, chosen)
        same = out['n'] == [t[x]['n'] for x in sc.LEADS] and all(abs(a - t[x]['GDMI']) < 1e-9 for a, x in zip(out['g'], sc.LEADS))
        check(same and abs(out['d'] - sc.gc_km(25.29, 60.64, 25.64, 57.77)) < 1e-9, f'page JavaScript = Python (node {node})', f)
    else:
        print('skip  node not found: JavaScript cross-check')
    print('selftest ok' if not f else f'selftest FAILED: {len(f)}')
    return 0 if not f else 1


def serve(port):
    build()
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    print(f'http://127.0.0.1:{port}/storm_live.html   (Ctrl-C to stop)')
    http.server.ThreadingHTTPServer(('127.0.0.1', port), h).serve_forever()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--serve', action='store_true')
    ap.add_argument('--port', type=int, default=8766)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.serve:
        return serve(a.port)
    print('built', build())
    return 0


if __name__ == '__main__':
    sys.exit(main())
