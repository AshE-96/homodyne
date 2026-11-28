"""wind_fetch.py · HMD-S11 · forecasts and observations for the takeoff-wind demo, standard library only.

Licence-clean sources only (no Open-Meteo here; see ../prep-fa.md §1):
  ECMWF IFS and AIFS Single 0.25°, open data, CC BY 4.0
      live:     data.ecmwf.int/forecasts/<date>/<hh>z/{ifs,aifs-single}/0p25/oper/
      archive:  storage.googleapis.com/ecmwf-open-data/<same path>   (Google Cloud public-data mirror; the AWS
                mirror ecmwf-forecasts.s3.eu-central-1.amazonaws.com has the same files but answered 503 SlowDown
                to most requests on 28 Nov 2026). Both mirrors accept one byte range per request only.
  NOAA GFS 0.25°, US public domain, NOMADS grib filter with a small subregion (hourly steps)
  METAR from the Iowa Environmental Mesonet ASOS/METAR archive (free, no key)

get() and get_ranges() are copied from HMD-S06 (summit_fetch.py); the GRIB decoding is grib2_point.py,
also copied from HMD-S06. Only a few grid points are decoded; no raw GRIB is written to disk.
"""
import concurrent.futures as cf
import csv
import datetime as dt
import http.client
import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grib2_point as gp  # noqa: E402
import wind_core as wc  # noqa: E402

UA = {'User-Agent': 'homodyne-wind-demo/1.0 (educational; stdlib urllib)'}
ECMWF_LIVE = 'https://data.ecmwf.int/forecasts'
ECMWF_ARCHIVE = 'https://storage.googleapis.com/ecmwf-open-data'
ECMWF_ARCHIVE_AWS = 'https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com'
ECMWF_DIR = {'ifs': 'ifs', 'aifs': 'aifs-single'}
EC_LEVELS = (1000, 925, 850, 700, 600, 500)
GFS_LEVELS = (900, 850, 800, 750, 700, 650, 600, 500)
SFC = {'10u': 'u10', '10v': 'v10', '10fg': 'gust', '2t': 't2', '2d': 'td2', 'sp': 'sp', 'mucape': 'cape', 'z': 'zsfc'}
PL = {'gh': 'gh', 't': 't', 'u': 'u', 'v': 'v', 'r': 'rh', 'q': 'q'}


# ── HTTP (from HMD-S06) ───────────────────────────────────────────────────────
def get(url, rng=None, timeout=60, tries=5):
    """GET with an optional byte range; retries politely (S3 answers 503 SlowDown when busy)."""
    h = dict(UA)
    if rng:
        h['Range'] = f'bytes={rng[0]}-{rng[1]}'
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (403, 404) or k == tries - 1:
                raise
        except (OSError, http.client.HTTPException):
            if k == tries - 1:
                raise
        time.sleep(1.5 * (k + 1))


def get_ranges(url, ranges):
    """One HTTP request for many byte ranges (multipart/byteranges); returns {offset: bytes}."""
    h = dict(UA, Range='bytes=' + ','.join(f'{o}-{o + n - 1}' for o, n in ranges))
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=180) as r:
                ctype, body = r.headers.get('Content-Type', ''), r.read()
            break
        except (OSError, http.client.HTTPException):
            if k == 4:
                raise
            time.sleep(2 * (k + 1))
    if 'multipart/byteranges' not in ctype:
        return {ranges[0][0]: body}
    boundary = b'--' + ctype.split('boundary=')[1].strip().strip('"').encode()
    out = {}
    for part in body.split(boundary)[1:]:
        head, sep, data = part.partition(b'\r\n\r\n')
        if not sep:
            continue
        cr = [l for l in head.decode('latin-1').split('\r\n') if l.lower().startswith('content-range')]
        if cr:
            lo, hi = cr[0].split('bytes')[1].strip().split('/')[0].split('-')
            out[int(lo)] = data[:int(hi) - int(lo) + 1]
    return out


# ── ECMWF open data (live or AWS archive) ─────────────────────────────────────
PREFIX = 0.42   # Tehran is about 30% down a north-to-south global field; the decoder stops there


def _points(blob, pts):
    try:
        return [p['value'] for p in gp.read_points(blob, pts)['points']]
    except ValueError:
        return None


def ecmwf_base(model, run, archive=False):
    root = ECMWF_ARCHIVE if archive else ECMWF_LIVE
    return f'{root}/{run:%Y%m%d}/{run:%H}z/{ECMWF_DIR[model]}/0p25/oper/{run:%Y%m%d%H0000}'


def ecmwf_latest(model, need_step, now=None):
    """Latest 00Z/12Z run whose need_step file is already published."""
    now = now or dt.datetime.now(dt.timezone.utc)
    t = now.replace(minute=0, second=0, microsecond=0, hour=now.hour - now.hour % 12)
    for _ in range(6):
        try:
            if get(f'{ecmwf_base(model, t)}-{need_step}h-oper-fc.index', timeout=30, tries=1):
                return t
        except Exception:
            pass
        t -= dt.timedelta(hours=12)
    raise RuntimeError(f'no recent {model} run with step {need_step}')


def ecmwf_points(model, run, steps, pts, sfc=None, levels=EC_LEVELS, archive=False, workers=6):
    """{(step, name, level or None): [value per point]} for the wanted fields of one run."""
    base = ecmwf_base(model, run, archive)
    sfc = set(sfc or SFC)

    def one(step):
        idx = [json.loads(l) for l in get(f'{base}-{step}h-oper-fc.index').decode().splitlines() if l.strip()]
        sel = {}
        for l in idx:
            if l['levtype'] == 'sfc' and l['param'] in sfc:
                sel[(step, SFC[l['param']], None)] = (l['_offset'], l['_length'])
            elif l['levtype'] == 'pl' and l['param'] in PL and int(l['levelist']) in levels:
                sel[(step, PL[l['param']], int(l['levelist']))] = (l['_offset'], l['_length'])
        url = f'{base}-{step}h-oper-fc.grib2'
        want = sorted((o, max(65536, int(n * PREFIX))) for o, n in sel.values())
        if archive:                                   # cloud mirrors: one range per request, a few in parallel
            with cf.ThreadPoolExecutor(max_workers=6) as ex:
                parts = dict(zip([o for o, _ in want], ex.map(lambda r: get(url, (r[0], r[0] + r[1] - 1)), want)))
        else:
            parts = get_ranges(url, want)
        return {k: (parts.get(o), url, o, n) for k, (o, n) in sel.items()}

    blobs = {}
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for d in ex.map(one, steps):
            blobs.update(d)
    keys = list(blobs)
    with cf.ProcessPoolExecutor(max_workers=workers) as ex:
        vals = dict(zip(keys, ex.map(_points, [blobs[k][0] or b'' for k in keys], [pts] * len(keys), chunksize=4)))
    for k in [k for k, v in vals.items() if v is None]:          # prefix too short: fetch the whole message
        _, url, o, n = blobs[k]
        vals[k] = _points(get(url, (o, o + n - 1)), pts)
    return vals


def ecmwf_rows(vals, run, site_keys):
    """Turn decoded fields into [{valid, step, <site>: {sfc..., levels: [...]}}] in common units."""
    rows = []
    zsfc = {k[1]: v for k, v in vals.items() if k[1] == 'zsfc'}
    for step in sorted({k[0] for k in vals}):
        row = dict(step=step, valid=(run + dt.timedelta(hours=step)).strftime('%Y-%m-%dT%H:%MZ'))
        for i, site in enumerate(site_keys):
            g = lambda name, lev=None: (vals.get((step, name, lev)) or [None] * len(site_keys))[i]  # noqa: E731
            c = lambda x, f: None if x is None else f(x)  # noqa: E731
            levels = []
            for p in EC_LEVELS:
                t = g('t', p)
                rh = g('rh', p)
                if rh is None and g('q', p) is not None and t is not None:
                    rh = rh_from_q(g('q', p), t, p)
                levels.append(dict(p=p, gh=g('gh', p), t=c(t, lambda x: x - 273.15), u=g('u', p), v=g('v', p), rh=rh))
            row[site] = dict(u10=g('u10'), v10=g('v10'), gust=c(g('gust'), wc.ms_to_kmh),
                             t2=c(g('t2'), lambda x: x - 273.15), td2=c(g('td2'), lambda x: x - 273.15),
                             sp=c(g('sp'), lambda x: x / 100), cape=g('cape'), levels=levels)
        rows.append(row)
    return rows, {s: (None if not zsfc else round(zsfc['zsfc'][i] / wc.G0)) for i, s in enumerate(site_keys)}


def rh_from_q(q, t_k, p_hpa):
    import math
    e = q * p_hpa / (0.622 + 0.378 * q)
    tc = t_k - 273.15
    return max(0.0, min(100.0, 100 * e / (6.112 * math.exp(17.67 * tc / (tc + 243.5)))))


# ── NOAA GFS via the NOMADS grib filter (hourly) ──────────────────────────────
GFS_FILTER = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl'
GFS_SFC = {(0, 2, 2, 103, 10): 'u10', (0, 2, 3, 103, 10): 'v10', (0, 2, 22, 1, 0): 'gust', (0, 0, 0, 103, 2): 't2',
           (0, 0, 6, 103, 2): 'td2', (0, 3, 0, 1, 0): 'sp', (0, 7, 6, 1, 0): 'cape', (0, 3, 196, 1, 0): 'hpbl',
           (0, 0, 11, 1, 0): 'shf', (0, 3, 5, 1, 0): 'zsfc'}
GFS_PL = {(0, 3, 5): 'gh', (0, 0, 0): 't', (0, 2, 2): 'u', (0, 2, 3): 'v', (0, 1, 1): 'rh'}


def gfs_url(run, step):
    q = [('dir', f'/gfs.{run:%Y%m%d}/{run:%H}/atmos'), ('file', f'gfs.t{run:%H}z.pgrb2.0p25.f{step:03d}')]
    q += [(f'var_{v}', 'on') for v in ('HGT', 'TMP', 'UGRD', 'VGRD', 'RH', 'HPBL', 'GUST', 'CAPE', 'SHTFL', 'DPT', 'PRES')]
    q += [(f'lev_{p}_mb', 'on') for p in GFS_LEVELS]
    q += [('lev_2_m_above_ground', 'on'), ('lev_10_m_above_ground', 'on'), ('lev_surface', 'on'),
          ('subregion', ''), ('toplat', '36.5'), ('leftlon', '50.5'), ('rightlon', '52'), ('bottomlat', '35')]
    return GFS_FILTER + '?' + urllib.parse.urlencode(q)


def gfs_latest(need_step, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    t = now.replace(minute=0, second=0, microsecond=0, hour=now.hour - now.hour % 6)
    for _ in range(8):
        try:
            if get(gfs_url(t, need_step), timeout=60, tries=1)[:4] == b'GRIB':
                return t
        except Exception:
            pass
        t -= dt.timedelta(hours=6)
    raise RuntimeError('no recent GFS run found')


def gfs_rows(run, steps, pts, site_keys):
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        blobs = dict(zip(steps, ex.map(lambda s: get(gfs_url(run, s)), steps)))
    rows, zs = [], {}
    for step in steps:
        f = {}
        for m in gp.messages(blobs[step]):
            pr = gp.product(m)
            key = pr if pr in GFS_SFC else None
            name = GFS_SFC.get(key) if key else None
            vals = [p['value'] for p in gp.read_points(m, pts)['points']]
            if name:
                f[name] = vals
            elif pr[3] == 100 and pr[:3] in GFS_PL:
                f[(GFS_PL[pr[:3]], int(pr[4] / 100))] = vals
        row = dict(step=step, valid=(run + dt.timedelta(hours=step)).strftime('%Y-%m-%dT%H:%MZ'))
        for i, site in enumerate(site_keys):
            g = lambda k: (f.get(k) or [None] * len(site_keys))[i]  # noqa: E731
            c = lambda x, fn: None if x is None else fn(x)  # noqa: E731
            if g('zsfc') is not None:
                zs[site] = round(g('zsfc'))
            row[site] = dict(u10=g('u10'), v10=g('v10'), gust=c(g('gust'), wc.ms_to_kmh), t2=c(g('t2'), lambda x: x - 273.15),
                             td2=c(g('td2'), lambda x: x - 273.15), sp=c(g('sp'), lambda x: x / 100), cape=g('cape'),
                             hpbl=g('hpbl'), shf=g('shf'),
                             levels=[dict(p=p, gh=g(('gh', p)), t=c(g(('t', p)), lambda x: x - 273.15), u=g(('u', p)),
                                          v=g(('v', p)), rh=g(('rh', p))) for p in GFS_LEVELS])
        rows.append(row)
    return rows, zs


# ── METAR (Iowa Environmental Mesonet archive) ────────────────────────────────
IEM = 'https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py'


def iem_metar(station, t0, t1):
    """Rows {valid (UTC ISO), wind km/h, dir, gust km/h or None, t, td, metar} between two UTC datetimes."""
    q = [('station', station)] + [('data', d) for d in ('sknt', 'drct', 'gust', 'tmpc', 'dwpc', 'metar')]
    q += [('year1', t0.year), ('month1', t0.month), ('day1', t0.day), ('year2', t1.year), ('month2', t1.month),
          ('day2', t1.day), ('tz', 'Etc/UTC'), ('format', 'onlycomma'), ('missing', 'M'), ('trace', 'T'),
          ('direct', 'no'), ('report_type', '3'), ('report_type', '4')]
    text = get(IEM + '?' + urllib.parse.urlencode(q), timeout=120).decode('utf-8', 'replace')
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        num = lambda k: None if r.get(k) in (None, '', 'M') else float(r[k])  # noqa: E731
        out.append(dict(valid=r['valid'].replace(' ', 'T') + 'Z', wind=wc.kt_to_kmh(num('sknt')), dir=num('drct'),
                        gust=wc.kt_to_kmh(num('gust')), t=num('tmpc'), td=num('dwpc'), metar=r.get('metar', '')))
    return out


def awc_metar(ids=('OIII', 'OIIE'), hours=48):
    """Live METAR from aviationweather.gov; returns (http status, raw text). Iranian stations may be empty."""
    url = 'https://aviationweather.gov/api/data/metar?' + urllib.parse.urlencode(dict(ids=','.join(ids), hours=hours))
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except Exception as e:
        return getattr(e, 'code', 0), str(e)
