"""storm_build.py · HMD-S04 · download the public decks once, then derive the small files the live page and selftest use.

    python3 -I artifact/storm_build.py --fetch     # NHC ATCF 2025 Atlantic a/b-decks, IBTrACS NI, Natural Earth → artifact/data/
    python3 -I artifact/storm_build.py             # artifact/data/ → artifact/derived/*.json (needs --fetch once)

artifact/data/ is git-ignored (raw downloads, ~40 MB). artifact/derived/ is committed; see derived/SOURCE.txt.
"""
import argparse
import csv
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import storm_core as sc  # noqa: E402

DATA, DERIVED = HERE / 'data', HERE / 'derived'
ATCF = 'https://ftp.nhc.noaa.gov/atcf/archive/2025/'
IBTRACS = ('https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/'
           'v04r01/access/csv/ibtracs.NI.list.v04r01.csv')
NE_LAND = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_50m_land.geojson'
STORMS = ['AL%02d' % i for i in range(1, 14)]

# NHC report Table 2 (track) and Table 4 (intensity): the early models in its homogeneous comparison.
# In ATCF, NHC's "GFSI" is AVNI. A 12-h-old interpolated run (…2) stands in when the 6-h one (…I) is missing,
# because the report "makes no distinction between 6- and 12-h interpolated models".
TRACK_SET = ['OFCL', 'OCD5', 'HFAI', 'HFBI', 'HWFI', 'HMNI', 'GDMI', 'AVNI', 'EMXI', 'CMCI', 'AEMI', 'HCCA', 'FSSE', 'TVCA']
INTEN_SET = ['OFCL', 'OCD5', 'HFAI', 'HFBI', 'HWFI', 'HMNI', 'DSHP', 'LGEM', 'GDMI', 'AVNI', 'EMXI', 'FSSE', 'HCCA',
             'NNIC', 'IVCN']
REPLAY_SET = ['OFCL', 'GDMI', 'EMXI', 'AVNI', 'HFAI', 'HCCA']
REPLAY_TAUS = (0, 12, 24, 36, 48, 60, 72, 96, 120)

# Printed in Cangialosi et al. (2026), NHC Forecast Verification Report, 2025 season, Tables 2 and 4 (n mi / kt).
NHC_T2 = {'n': [193, 170, 155, 135, 117, 103, 78, 59],
          'OFCL': [20.4, 31.1, 41.9, 49.2, 62.2, 81.4, 113.9, 168.5], 'OCD5': [41.0, 88.8, 141.5, 191.0, 241.9, 293.5, 377.2, 428.8],
          'HFAI': [27.4, 45.1, 60.7, 71.9, 87.2, 107.1, 145.3, 180.2], 'HFBI': [28.1, 45.9, 63.7, 73.6, 86.8, 107.7, 155.2, 203.6],
          'HWFI': [27.1, 44.1, 62.0, 79.5, 103.9, 134.8, 208.4, 311.1], 'HMNI': [26.0, 42.8, 61.3, 76.8, 96.6, 123.6, 173.6, 247.0],
          'GDMI': [19.6, 26.4, 34.8, 41.4, 50.8, 66.5, 111.7, 173.1], 'AVNI': [26.8, 46.0, 64.3, 78.9, 96.7, 128.6, 221.3, 362.3],
          'EMXI': [22.4, 37.8, 53.0, 65.2, 83.6, 102.7, 126.2, 174.5], 'CMCI': [28.0, 48.6, 72.8, 91.7, 109.7, 126.1, 150.4, 179.9],
          'AEMI': [24.5, 40.1, 57.0, 68.4, 81.2, 100.4, 146.4, 192.3], 'HCCA': [20.5, 31.3, 43.2, 52.5, 66.3, 87.4, 118.4, 162.4],
          'FSSE': [22.1, 35.0, 47.9, 58.5, 73.2, 95.7, 145.9, 229.3], 'TVCA': [23.0, 36.2, 51.0, 60.1, 76.0, 98.8, 139.6, 189.7]}
NHC_T4 = {'n': [195, 174, 156, 137, 119, 104, 78, 59],
          'OFCL': [6.1, 9.3, 11.7, 13.1, 14.1, 14.6, 17.2, 20.4], 'OCD5': [8.4, 13.7, 18.9, 22.9, 27.8, 31.0, 35.0, 37.3],
          'HFAI': [7.2, 10.7, 13.9, 15.5, 16.3, 16.2, 20.6, 21.8], 'HFBI': [7.4, 10.3, 13.2, 15.6, 16.7, 17.5, 21.2, 20.9],
          'HWFI': [8.2, 12.5, 17.3, 18.8, 19.6, 18.9, 19.1, 25.9], 'HMNI': [7.6, 11.6, 14.8, 16.7, 19.2, 19.5, 20.1, 20.0],
          'DSHP': [7.7, 11.1, 13.7, 17.0, 19.8, 23.0, 26.6, 25.8], 'LGEM': [8.1, 11.8, 14.6, 17.2, 19.2, 22.4, 25.7, 26.8],
          'GDMI': [7.1, 9.4, 11.2, 12.3, 13.5, 14.6, 17.3, 21.9], 'AVNI': [8.2, 12.8, 16.8, 20.2, 23.1, 25.8, 30.5, 32.2],
          'EMXI': [9.2, 14.8, 19.6, 24.3, 28.1, 29.6, 32.2, 35.3], 'FSSE': [6.7, 9.0, 11.9, 14.2, 15.4, 16.5, 18.3, 21.6],
          'HCCA': [7.0, 9.2, 12.4, 14.9, 16.7, 17.7, 19.5, 21.3], 'NNIC': [7.1, 9.2, 12.3, 14.5, 15.2, 15.9, 22.4, 21.6],
          'IVCN': [6.8, 9.6, 12.7, 15.0, 16.5, 17.5, 20.2, 21.2]}

# Places for the Arabian Sea view (coordinates rounded to 0.01°, GeoNames).
PLACES = {'Chabahar': (25.29, 60.64), 'Jask': (25.64, 57.77), 'Muscat': (23.59, 58.41), 'Ras al Hadd': (22.53, 59.80)}
NI_STORMS = {'gonu': '2007151N14072', 'shaheen': '2021267N18094'}
BOXES = {'atl': (5, 50, -100, -5), 'ni': (8, 32, 48, 80)}       # lat0, lat1, lon0, lon1


def fetch():
    DATA.mkdir(exist_ok=True)
    jobs = [(ATCF + f'{p}al{s[2:]}2025.dat.gz', DATA / f'{p}al{s[2:]}2025.dat.gz') for s in STORMS for p in 'ab']
    jobs += [(IBTRACS, DATA / 'ibtracs.NI.list.v04r01.csv'), (NE_LAND, DATA / 'ne_50m_land.geojson')]
    for url, dst in jobs:
        if dst.exists():
            continue
        print('get', url)
        req = urllib.request.Request(url, headers={'User-Agent': 'homodyne-s04-verification/1.0'})
        with urllib.request.urlopen(req, timeout=300) as r:
            dst.write_bytes(r.read())
    with open(DATA / 'SHA256SUMS', 'w') as f:
        for p in sorted(DATA.glob('*')):
            if p.name != 'SHA256SUMS':
                f.write(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n')


def load_atlantic(models):
    want = set(models) | {m[:-1] + '2' for m in models if m.endswith('I')}
    out = {}
    for s in STORMS:
        fc = sc.parse_adeck(sc.read_lines(DATA / f'aal{s[2:]}2025.dat.gz'), want)
        for m in list(fc):
            mi = m[:-1] + 'I'
            if m.endswith('2') and mi in models:
                for init, d in fc[m].items():
                    fc[mi].setdefault(init, d)
        out[s] = dict(best=sc.parse_bdeck(sc.read_lines(DATA / f'bal{s[2:]}2025.dat.gz')),
                      fc={m: dict(fc[m]) for m in models if m in fc})
    return out


def r1(x):
    return None if x is None else round(x, 1)


def build_cases(storms, models, kind):
    unit = 1.0
    cs = sc.cases(storms, models, kind=kind, homogeneous=False)
    return [[c['storm'], c['init'], c['tau']] + [r1(c['err'].get(m)) for m in models] for c in cs]


def unpack(rows, models):
    return [dict(storm=r[0], init=r[1], tau=r[2], err={m: v for m, v in zip(models, r[3:]) if v is not None}) for r in rows]


def homog(cs, models):
    return [c for c in cs if all(m in c['err'] for m in models)]


def analyse(track_rows, inten_rows):
    """Everything the script quotes, from the committed case tables (so --selftest can redo it offline)."""
    tr, it = unpack(track_rows, TRACK_SET), unpack(inten_rows, INTEN_SET)
    out = {'leads': list(sc.LEADS), 'units': {'track': 'n mi (tables) / km (cases)', 'intensity': 'kt'}}
    t2 = sc.table(homog(tr, TRACK_SET), TRACK_SET, unit=sc.KM_PER_NMI)
    t4 = sc.table(homog(it, INTEN_SET), INTEN_SET)
    out['ours_t2'] = {m: [round(t2[x][m], 1) for x in sc.LEADS] for m in TRACK_SET} | {'n': [t2[x]['n'] for x in sc.LEADS]}
    out['ours_t4'] = {m: [round(t4[x][m], 1) for x in sc.LEADS] for m in INTEN_SET} | {'n': [t4[x]['n'] for x in sc.LEADS]}
    out['nhc_t2'], out['nhc_t4'] = NHC_T2, NHC_T4
    out['maxdiff_t2'] = max(abs(a - b) for m in TRACK_SET for a, b in zip(out['ours_t2'][m], NHC_T2[m]))
    out['maxdiff_t4'] = max(abs(a - b) for m in INTEN_SET for a, b in zip(out['ours_t4'][m], NHC_T4[m]))
    km = {}
    for name, cs in (('t2', homog(tr, TRACK_SET)), ('pair', homog(tr, ['OFCL', 'GDMI']))):
        t = sc.table(cs, ['OFCL', 'GDMI', 'EMXI', 'AVNI', 'HFAI', 'HCCA'] if name == 't2' else ['OFCL', 'GDMI'])
        km[name] = {m: [round(t[x][m]) for x in sc.LEADS] for m in t[12] if m != 'n'} | {'n': [t[x]['n'] for x in sc.LEADS]}
        km[name + '_boot_storm'] = {x: sc.boot_diff(cs, 'GDMI', 'OFCL', x, block='storm') for x in (24, 48, 72, 120)}
        km[name + '_boot_case'] = {x: sc.boot_diff(cs, 'GDMI', 'OFCL', x, block='case') for x in (24, 48, 72, 120)}
    out['track_km'] = km
    ci = homog(it, INTEN_SET)
    out['inten_boot_storm'] = {x: sc.boot_diff(ci, 'GDMI', 'OFCL', x, block='storm') for x in (24, 48, 72, 120)}
    # per storm, 72 h, in the Table-2 sample: who was closer, storm by storm
    per = {}
    for c in homog(tr, TRACK_SET):
        if c['tau'] == 72:
            p = per.setdefault(c['storm'], [0, 0.0, 0.0])
            p[0] += 1
            p[1] += c['err']['OFCL']
            p[2] += c['err']['GDMI']
    out['per_storm_72'] = {s: dict(n=v[0], OFCL=round(v[1] / v[0]), GDMI=round(v[2] / v[0])) for s, v in sorted(per.items())}
    # how much of the Table-2 sample each storm is (at 12 h)
    cnt = {}
    for c in homog(tr, TRACK_SET):
        if c['tau'] == 12:
            cnt[c['storm']] = cnt.get(c['storm'], 0) + 1
    out['share_12'] = cnt
    return out


def replay(storms):
    out = {}
    for s, d in storms.items():
        best = sorted(d['best'].items())
        name = next((b['name'] for _, b in reversed(best) if b['name'] and b['name'] not in ('INVEST',)), s)
        fc = {}
        for m in REPLAY_SET:
            for init, taus in d['fc'].get(m, {}).items():
                if init[-2:] in ('00', '06', '12', '18') and init in d['best']:
                    pts = [[t] + [r1(v) if i < 2 else v for i, v in enumerate(taus[t])] for t in REPLAY_TAUS
                           if t in taus and taus[t][0] is not None]
                    if len(pts) > 1:
                        fc.setdefault(m, {})[init] = pts
        out[s] = dict(name=name, best=[[t, b['lat'], b['lon'], b['vmax'], b['ty']] for t, b in best], fc=fc)
    return out


def north_indian():
    rows = list(csv.reader(open(DATA / 'ibtracs.NI.list.v04r01.csv', encoding='utf-8')))
    h = rows[0]
    ix = {k: i for i, k in enumerate(h)}
    out = {}
    for key, sid in NI_STORMS.items():
        pts = []
        for r in rows[2:]:
            if r[0] != sid:
                continue
            g = lambda k: r[ix[k]].strip()  # noqa: E731
            num = lambda k: int(float(g(k))) if g(k) else None  # noqa: E731
            pts.append([g('ISO_TIME')[:16], float(g('LAT')), float(g('LON')), num('USA_WIND'), num('NEWDELHI_WIND'),
                        g('NEWDELHI_GRADE') or None, g('NATURE'), num('DIST2LAND')])
        near = {p: dict(zip(('km', 'when'), (round(sc.closest_approach(pts, *ll)[0]),
                                                sc.closest_approach(pts, *ll)[1]))) for p, ll in PLACES.items()}
        peak_usa = max(pts, key=lambda p: p[3] or 0)
        peak_imd = max(pts, key=lambda p: p[4] or 0)
        out[key] = dict(sid=sid, name=rows[[r[0] for r in rows].index(sid)][ix['NAME']], track=pts, nearest=near,
                        peak_usa=[peak_usa[0], peak_usa[3]], peak_imd=[peak_imd[0], peak_imd[4], peak_imd[5]])
    out['places'] = PLACES
    return out


def clip_ring(ring, box):
    """Sutherland–Hodgman clip of one polygon ring to a lon/lat rectangle."""
    lat0, lat1, lon0, lon1 = box
    edges = [(lambda p: p[0] >= lon0, lambda a, b: (lon0, a[1] + (b[1] - a[1]) * (lon0 - a[0]) / (b[0] - a[0]))),
             (lambda p: p[0] <= lon1, lambda a, b: (lon1, a[1] + (b[1] - a[1]) * (lon1 - a[0]) / (b[0] - a[0]))),
             (lambda p: p[1] >= lat0, lambda a, b: (a[0] + (b[0] - a[0]) * (lat0 - a[1]) / (b[1] - a[1]), lat0)),
             (lambda p: p[1] <= lat1, lambda a, b: (a[0] + (b[0] - a[0]) * (lat1 - a[1]) / (b[1] - a[1]), lat1))]
    pts = ring
    for inside, cut in edges:
        if not pts:
            break
        res, prev = [], pts[-1]
        for cur in pts:
            if inside(cur):
                if not inside(prev):
                    res.append(cut(prev, cur))
                res.append(cur)
            elif inside(prev):
                res.append(cut(prev, cur))
            prev = cur
        pts = res
    return pts


def land():
    gj = json.load(open(DATA / 'ne_50m_land.geojson', encoding='utf-8'))
    out = {}
    for key, box in BOXES.items():
        polys = []
        for f in gj['features']:
            g = f['geometry']
            for poly in (g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]):
                ring = clip_ring([tuple(p) for p in poly[0]], box)
                simp = []
                for x, y in ring:
                    q = [round(x, 2), round(y, 2)]
                    if not simp or abs(q[0] - simp[-1][0]) + abs(q[1] - simp[-1][1]) >= (0.15 if key == 'atl' else 0.06):
                        simp.append(q)
                if len(simp) >= 3:
                    polys.append(simp)
        out[key] = dict(box=box, polys=polys)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fetch', action='store_true')
    a = ap.parse_args()
    if a.fetch:
        fetch()
    if not (DATA / 'bal132025.dat.gz').exists():
        sys.exit('no raw data: run  python3 -I artifact/storm_build.py --fetch  first')
    DERIVED.mkdir(exist_ok=True)
    allm = sorted(set(TRACK_SET) | set(INTEN_SET))
    st = load_atlantic(allm)
    tr = build_cases(st, TRACK_SET, 'track')
    it = build_cases(st, INTEN_SET, 'intensity')
    dump = lambda name, obj: (DERIVED / name).write_text(json.dumps(obj, separators=(',', ':')), encoding='utf-8')  # noqa
    dump('cases-2025.json', dict(note='error per case; track km (great circle), intensity kt; null = model missing',
                                 track_models=TRACK_SET, track=tr, intensity_models=INTEN_SET, intensity=it))
    dump('verify-2025.json', analyse(tr, it))
    dump('replay-2025.json', dict(models=REPLAY_SET, storms=replay(st)))
    dump('north-indian.json', north_indian())
    dump('land.json', land())
    for p in sorted(DERIVED.glob('*.json')):
        print(f'{p.name:22} {p.stat().st_size:>8} bytes')


if __name__ == '__main__':
    main()
