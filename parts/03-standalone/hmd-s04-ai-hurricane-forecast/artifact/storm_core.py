"""storm_core.py · HMD-S04 · ATCF deck parsing, great-circle distance and NHC-style verification. Standard library only.

ATCF a-deck  (aalNNYYYY.dat): one line per model × initial time × lead time (×wind-radius threshold); forecasts.
ATCF b-deck  (balNNYYYY.dat): the post-season best track, one line per synoptic time (×wind-radius threshold).
Format: https://www.nrlmry.navy.mil/atcf_web/docs/database/new/abrdeck.html (columns used below are 1-based there).

Verification rules follow the NHC report (Cangialosi et al. 2026, §1): a forecast counts only if the system is a tropical
or subtropical cyclone in the final best track at BOTH the initial time and the valid time; track error is the
great-circle distance to the best-track position; intensity error is |forecast − best-track| maximum wind (kt).
A homogeneous comparison uses only the (storm, initial time, lead time) cases that every model in the set has.
"""
import gzip
import math
import random
from collections import defaultdict

R_EARTH_KM = 6371.0          # mean Earth radius (IUGG R1 = 6371.0088 km; 6371.0 is the usual rounding)
KM_PER_NMI = 1.852           # international nautical mile, exact by definition
TC_TYPES = {'TD', 'TS', 'HU', 'TY', 'ST', 'TC', 'SD', 'SS'}   # best-track "TY" column: tropical or subtropical
LEADS = (12, 24, 36, 48, 60, 72, 96, 120)


def gc_km(lat1, lon1, lat2, lon2):
    """Great-circle distance on a sphere (haversine), degrees in, km out."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH_KM * math.asin(min(1.0, math.sqrt(a)))


def parse_latlon(s):
    """ATCF position in tenths of a degree: '300N' → 30.0, '576W' → −57.6, '1231E' → 123.1."""
    s = s.strip()
    if not s or s[:-1] == '':
        return None
    v = int(s[:-1]) / 10.0
    return -v if s[-1] in 'SW' else v


def _cols(line):
    return [c.strip() for c in line.split(',')]


def read_lines(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='latin-1') as f:
        return f.read().splitlines()


def parse_bdeck(lines):
    """Best track → {'YYYYMMDDHH': dict(lat, lon, vmax, ty, name)}; the first line per time wins (radii lines repeat it)."""
    out = {}
    for ln in lines:
        c = _cols(ln)
        if len(c) < 11 or c[4] != 'BEST':
            continue
        t = c[2]
        if t in out:
            continue
        lat, lon = parse_latlon(c[6]), parse_latlon(c[7])
        if lat is None or lon is None:
            continue
        out[t] = dict(lat=lat, lon=lon, vmax=int(c[8] or 0), ty=c[10], name=c[27] if len(c) > 27 else '')
    return out


def parse_adeck(lines, models=None):
    """Forecasts → {model: {init: {tau: (lat, lon, vmax)}}}; first line per (model, init, tau) wins."""
    out = defaultdict(lambda: defaultdict(dict))
    for ln in lines:
        c = _cols(ln)
        if len(c) < 9:
            continue
        tech = c[4]
        if models and tech not in models:
            continue
        try:
            tau = int(c[5])
        except ValueError:
            continue
        init = c[2]
        if tau in out[tech][init]:
            continue
        lat, lon = parse_latlon(c[6]), parse_latlon(c[7])
        if lat is not None and lon is not None and lat == 0 and lon == 0:
            lat = lon = None                      # intensity-only aids (e.g. IVCN) carry no position
        vmax = int(c[8]) if c[8].lstrip('-').isdigit() else 0
        if lat is None and vmax <= 0:
            continue
        out[tech][init][tau] = (lat, lon, vmax)
    return out


def add_hours(t, h):
    """'YYYYMMDDHH' + h hours (proleptic Gregorian, UTC)."""
    import datetime as dt
    d = dt.datetime.strptime(t, '%Y%m%d%H') + dt.timedelta(hours=h)
    return d.strftime('%Y%m%d%H')


def cases(storms, models, leads=LEADS, kind='track', homogeneous=True, require=('OFCL',)):
    """List of verification cases. storms: {storm_id: dict(best=..., fc=...)}.
    Each case: dict(storm, init, tau, err={model: km or kt}). Only synoptic initial times (00/06/12/18 UTC).
    require: models that must exist for a case to be considered at all (NHC verifies the official forecast's cycles)."""
    out = []
    for sid, s in storms.items():
        best, fc = s['best'], s['fc']
        inits = sorted({i for m in models for i in fc.get(m, {})})
        for init in inits:
            if init[-2:] not in ('00', '06', '12', '18'):
                continue
            b0 = best.get(init)
            if not b0 or b0['ty'] not in TC_TYPES:
                continue
            for tau in leads:
                bv = best.get(add_hours(init, tau))
                if not bv or bv['ty'] not in TC_TYPES:
                    continue
                err = {}
                for m in models:
                    f = fc.get(m, {}).get(init, {}).get(tau)
                    if not f:
                        continue
                    if kind == 'track':
                        if f[0] is not None:
                            err[m] = gc_km(f[0], f[1], bv['lat'], bv['lon'])
                    elif f[2] > 0 and bv['vmax'] > 0:
                        err[m] = abs(f[2] - bv['vmax'])
                if any(r not in err for r in require):
                    continue
                if homogeneous and len(err) < len(models):
                    continue
                if err:
                    out.append(dict(storm=sid, init=init, tau=tau, err=err))
    return out


def mean(xs):
    return sum(xs) / len(xs) if xs else float('nan')


def table(cs, models, leads=LEADS, unit=1.0):
    """{tau: {'n': n, model: mean error / unit}}."""
    t = {}
    for tau in leads:
        sel = [c for c in cs if c['tau'] == tau]
        row = {'n': len(sel)}
        for m in models:
            row[m] = mean([c['err'][m] / unit for c in sel if m in c['err']])
        t[tau] = row
    return t


def boot_diff(cs, a, b, tau, reps=2000, seed=1, block='storm', unit=1.0):
    """Bootstrap 95% interval of mean(err_a − err_b) at one lead time.
    block='storm' resamples whole storms (consecutive forecasts of one storm are not independent);
    block='case' resamples single forecasts (too optimistic; shown only for contrast)."""
    sel = [c for c in cs if c['tau'] == tau and a in c['err'] and b in c['err']]
    if not sel:
        return None
    d = [(c['storm'], (c['err'][a] - c['err'][b]) / unit) for c in sel]
    rng = random.Random(seed)
    if block == 'storm':
        groups = defaultdict(list)
        for s, x in d:
            groups[s].append(x)
        keys = sorted(groups)
        stats = []
        for _ in range(reps):
            pick = [rng.choice(keys) for _ in keys]
            xs = [x for k in pick for x in groups[k]]
            stats.append(mean(xs))
    else:
        xs0 = [x for _, x in d]
        stats = [mean([rng.choice(xs0) for _ in xs0]) for _ in range(reps)]
    stats.sort()
    lo, hi = stats[int(0.025 * reps)], stats[int(0.975 * reps) - 1]
    return dict(n=len(sel), storms=len({s for s, _ in d}), mean=mean([x for _, x in d]), lo=lo, hi=hi,
                share_better=sum(1 for _, x in d if x < 0) / len(d))


def closest_approach(track, lat, lon):
    """Smallest great-circle distance (km) from a list of points [(time, lat, lon, ...)] to a place, and when."""
    best = min(track, key=lambda p: gc_km(p[1], p[2], lat, lon))
    return gc_km(best[1], best[2], lat, lon), best[0]
