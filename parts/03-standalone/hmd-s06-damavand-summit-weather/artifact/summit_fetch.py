"""summit_fetch.py · HMD-S06 · get the latest forecasts for the summit and Bargah-e Sevom, standard library only.

Licence-clean sources (fetched by default):
  ifs    ECMWF IFS 0.25°, open data, CC BY 4.0      data.ecmwf.int/forecasts/<date>/<hh>z/ifs/0p25/oper/
  aifs   ECMWF AIFS Single 0.25°, open data, CC BY 4.0   …/aifs-single/0p25/oper/
  gfs    NOAA GFS 0.25°, US government work (public domain), NOMADS grib filter with a 2°x2° subregion
Optional, only with --openmeteo (the owner's licence decision; free API is non-commercial only):
  om     Open-Meteo forecast API: ICON and the others on equal footing, plus its own elevation downscaling
  ens    Open-Meteo ensemble API: ECMWF ENS (51), GEFS (31), ICON-EPS (40) members at 400–700 hPa

Only a handful of grid points is decoded (grib2_point.py); the raw GRIB is never written to disk.
"""
import concurrent.futures as cf
import datetime as dt
import http.client
import json
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grib2_point as gp  # noqa: E402
import summit_core as sc  # noqa: E402

UA = {'User-Agent': 'homodyne-summit-demo/1.0 (educational; stdlib urllib)'}
LEVELS = (400, 500, 600, 700)
STEPS = tuple(range(0, 73, 6))
ECMWF = 'https://data.ecmwf.int/forecasts'
ECMWF_DIR = {'ifs': 'ifs', 'aifs': 'aifs-single'}
PTS = [(s['lat'], s['lon']) for s in sc.SITES.values()]
SITE_KEYS = list(sc.SITES)


def get(url, rng=None, timeout=60, tries=4):
    """GET with an optional byte range; retries politely (the open-data servers drop busy connections)."""
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


# ── ECMWF open data ───────────────────────────────────────────────────────────
def ecmwf_run(model, now=None):
    """Latest run whose +72 h file is published (probe back in 6 h steps)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    t = now.replace(minute=0, second=0, microsecond=0, hour=now.hour - now.hour % 6)
    for _ in range(10):
        stamp = t.strftime('%Y%m%d%H0000')
        url = f'{ECMWF}/{t:%Y%m%d}/{t:%H}z/{ECMWF_DIR[model]}/0p25/oper/{stamp}-72h-oper-fc.index'
        try:
            if get(url, timeout=30, tries=1):
                return t
        except Exception:
            pass
        t -= dt.timedelta(hours=6)
    raise RuntimeError(f'no recent {model} run found')


def get_ranges(url, ranges):
    """One HTTP request for many byte ranges (multipart/byteranges); returns {offset: bytes}."""
    h = dict(UA, Range='bytes=' + ','.join(f'{o}-{o + n - 1}' for o, n in ranges))
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120) as r:
                ctype, body = r.headers.get('Content-Type', ''), r.read()
            break
        except (OSError, http.client.HTTPException):
            if k == 3:
                raise
            time.sleep(2 * (k + 1))
    if 'multipart/byteranges' not in ctype:          # a single range comes back as plain content
        return {ranges[0][0]: body}
    boundary = b'--' + ctype.split('boundary=')[1].strip().strip('"').encode()
    out = {}
    for part in body.split(boundary)[1:]:
        head, sep, data = part.partition(b'\r\n\r\n')
        if not sep:
            continue
        cr = [l for l in head.decode('latin-1').split('\r\n') if l.lower().startswith('content-range')]
        if not cr:
            continue
        lo, hi = cr[0].split('bytes')[1].strip().split('/')[0].split('-')
        out[int(lo)] = data[:int(hi) - int(lo) + 1]
    return out


PREFIX = 0.5   # Damavand sits about 30% down a north-to-south field: half of each message is (almost) always enough


def _decode(blob):
    try:
        return [p['value'] for p in gp.read_points(blob, PTS)['points']]
    except ValueError:
        return None   # prefix too short: fetched again in full


def ecmwf_fetch(model, run, steps=STEPS, log=print):
    base = f'{ECMWF}/{run:%Y%m%d}/{run:%H}z/{ECMWF_DIR[model]}/0p25/oper/{run:%Y%m%d%H0000}'
    hum = 'r' if model == 'ifs' else 'q'

    def one_step(step):
        idx = [json.loads(l) for l in get(f'{base}-{step}h-oper-fc.index').decode().splitlines() if l.strip()]
        want = {('2t', None), ('10u', None), ('10v', None), ('tp', None), ('tcc', None)}
        if step == 0:
            want.add(('z', None))
        want |= {(prm, str(p)) for p in LEVELS for prm in ('gh', 't', 'u', 'v', hum)}
        sel = {}
        for l in idx:
            key = (l['param'], l.get('levelist') if l['levtype'] == 'pl' else None)
            if key in want and l['levtype'] in ('pl', 'sfc'):
                sel[(step,) + key] = (l['_offset'], l['_length'])
        url = f'{base}-{step}h-oper-fc.grib2'
        parts = get_ranges(url, sorted((o, max(65536, int(n * PREFIX))) for o, n in sel.values()))
        return {k: (parts[o], url, o, n) for k, (o, n) in sel.items()}

    blobs = {}
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for d in ex.map(one_step, steps):
            blobs.update(d)
    mb = sum(len(b[0]) for b in blobs.values()) / 1e6
    log(f'  {model}: run {run:%Y-%m-%d %H}Z, {len(blobs)} fields ({mb:.0f} MB of message prefixes), decoding')
    with cf.ProcessPoolExecutor(max_workers=6) as ex:
        vals = dict(zip(blobs, ex.map(_decode, [b[0] for b in blobs.values()], chunksize=4)))
    retry = [k for k, v in vals.items() if v is None]
    for k in retry:
        _, url, o, n = blobs[k]
        vals[k] = _decode(get(url, (o, o + n - 1)))
    if retry:
        log(f'  {model}: {len(retry)} fields needed the full message')
    return vals


def ecmwf_series(model, run, vals):
    zs = vals.get((0, 'z', None))
    oro = [v / sc.G0 for v in zs] if zs else [None, None]
    hum = 'r' if model == 'ifs' else 'q'
    series, prev_tp = [], None
    for step in sorted({k[0] for k in vals}):
        tp = vals.get((step, 'tp', None))
        pr = None
        if tp is not None:
            acc = [x * (1000 if model == 'ifs' else 1) for x in tp]   # IFS tp in m, AIFS tp in kg m-2 (= mm)
            pr = [max(0.0, a - (b if prev_tp else 0)) for a, b in zip(acc, prev_tp or acc)] if step else [0.0, 0.0]
            prev_tp = acc
        row = dict(step=step, valid=(run + dt.timedelta(hours=step)).strftime('%Y-%m-%dT%H:%MZ'))
        for i, site in enumerate(SITE_KEYS):
            levels = []
            for p in LEVELS:
                g = lambda prm: (vals.get((step, prm, str(p))) or [None, None])[i]  # noqa: E731
                lv = dict(p=p, gh=g('gh'), t=None if g('t') is None else g('t') - 273.15, u=g('u'), v=g('v'))
                if hum == 'r':
                    lv['rh'] = g('r')
                elif g('q') is not None and g('t') is not None:
                    lv['rh'] = sc.rh_from_q(g('q'), g('t'), p)
                levels.append(lv)
            row[site] = site_row(site, levels, oro[i], (vals.get((step, '2t', None)) or [None, None])[i],
                                 (vals.get((step, '10u', None)) or [None, None])[i],
                                 (vals.get((step, '10v', None)) or [None, None])[i],
                                 None if pr is None else pr[i], (vals.get((step, 'tcc', None)) or [None, None])[i])
        series.append(row)
    return dict(orography={s: None if o is None else round(o) for s, o in zip(SITE_KEYS, oro)}, series=series)


def site_row(site, levels, z_model, t2k, u10, v10, precip=None, tcc=None):
    z = sc.SITES[site]['z']
    fa = sc.free_air(levels, z)
    t2 = None if t2k is None else t2k - 273.15
    out = dict(fa=fa, raw2t=None if t2 is None else round(t2, 1),
               lapse=None if t2 is None or z_model is None else round(sc.lapse_correct(t2, z_model, z), 1),
               wind10=None if u10 is None else round(sc.speed_kmh(u10, v10), 1),
               precip=None if precip is None else round(precip, 1),
               tcc=None if tcc is None else round(100 * tcc if tcc <= 1.0 else tcc),
               levels=[{k: (round(v, 1) if isinstance(v, float) else v) for k, v in l.items()} for l in levels])
    out['flags'] = sc.step_flags(fa, precip)
    return out


# ── NOAA GFS via the NOMADS grib filter ───────────────────────────────────────
GFS_FILTER = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl'
GFS_IDS = {(0, 3, 5): 'gh', (0, 0, 0): 't', (0, 2, 2): 'u', (0, 2, 3): 'v', (0, 1, 1): 'rh'}


def gfs_url(run, step):
    q = [('dir', f'/gfs.{run:%Y%m%d}/{run:%H}/atmos'), ('file', f'gfs.t{run:%H}z.pgrb2.0p25.f{step:03d}')]
    q += [(f'var_{v}', 'on') for v in ('HGT', 'TMP', 'UGRD', 'VGRD', 'RH')]
    q += [(f'lev_{p}_mb', 'on') for p in LEVELS]
    q += [('lev_2_m_above_ground', 'on'), ('lev_10_m_above_ground', 'on'), ('lev_surface', 'on'),
          ('subregion', ''), ('toplat', '37'), ('leftlon', '51'), ('rightlon', '53'), ('bottomlat', '35')]
    return GFS_FILTER + '?' + urllib.parse.urlencode(q)


def gfs_run(now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    t = now.replace(minute=0, second=0, microsecond=0, hour=now.hour - now.hour % 6)
    for _ in range(8):
        try:
            if get(gfs_url(t, 72), timeout=60)[:4] == b'GRIB':
                return t
        except Exception:
            pass
        t -= dt.timedelta(hours=6)
    raise RuntimeError('no recent GFS run found')


def gfs_fetch(run, steps=STEPS, log=print):
    log(f'  gfs: run {run:%Y-%m-%d %H}Z, {len(steps)} subregion files')
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        blobs = dict(zip(steps, ex.map(lambda s: get(gfs_url(run, s)), steps)))
    series, oro = [], [None, None]
    for step in steps:
        f = {}
        for m in gp.messages(blobs[step]):
            disc, cat, num, lt, lv = gp.product(m)
            f[(disc, cat, num, lt, lv)] = [p['value'] for p in gp.read_points(m, PTS)['points']]
        hs = f.get((0, 3, 5, 1, 0xFFFFFFFF)) or f.get((0, 3, 5, 1, 0))
        if hs:
            oro = hs
        row = dict(step=step, valid=(run + dt.timedelta(hours=step)).strftime('%Y-%m-%dT%H:%MZ'))
        for i, site in enumerate(SITE_KEYS):
            levels = []
            for p in LEVELS:
                lv = dict(p=p)
                for ids, name in GFS_IDS.items():
                    v = f.get(ids + (100, p * 100))
                    lv[name] = None if v is None else v[i]
                if lv.get('t') is not None:
                    lv['t'] -= 273.15
                levels.append(lv)
            t2 = f.get((0, 0, 0, 103, 2))
            u10, v10 = f.get((0, 2, 2, 103, 10)), f.get((0, 2, 3, 103, 10))
            row[site] = site_row(site, levels, oro[i], t2 and t2[i], u10 and u10[i], v10 and v10[i])
        series.append(row)
    return dict(orography={s: round(o) for s, o in zip(SITE_KEYS, oro)}, series=series)


# ── Open-Meteo (optional; owner's licence decision) ───────────────────────────
OM_MODELS = {'ecmwf_ifs025': 'om-ifs', 'gfs_seamless': 'om-gfs', 'icon_seamless': 'om-icon'}
# GEFS and ICON-EPS return no pressure-level members on Open-Meteo (tested 28 Nov 2026), so only ECMWF ENS
ENS_MODELS = {'ecmwf_ifs025': 'ECMWF ENS'}


def om_fetch(log=print):
    s = sc.SITES['summit']
    pl = [f'{v}_{p}hPa' for p in LEVELS for v in ('temperature', 'wind_speed', 'wind_direction',
                                                  'relative_humidity', 'geopotential_height')]
    base = dict(latitude=s['lat'], longitude=s['lon'], forecast_days=3, wind_speed_unit='kmh',
                models=','.join(OM_MODELS), timezone='GMT')
    raw = json.loads(get('https://api.open-meteo.com/v1/forecast?' + urllib.parse.urlencode(
        dict(base, elevation='nan', hourly=','.join(pl + ['temperature_2m', 'wind_speed_10m', 'wind_gusts_10m'])))))
    down = json.loads(get('https://api.open-meteo.com/v1/forecast?' + urllib.parse.urlencode(
        dict(base, elevation=s['z'], hourly='temperature_2m,wind_speed_10m,wind_gusts_10m'))))
    ens = json.loads(get('https://ensemble-api.open-meteo.com/v1/ensemble?' + urllib.parse.urlencode(
        dict(base, elevation='nan', models=','.join(ENS_MODELS),
             hourly=','.join(f'{v}_{p}hPa' for p in LEVELS for v in ('temperature', 'wind_speed', 'geopotential_height'))))))
    log(f'  open-meteo: forecast grid-cell height {raw.get("elevation")} m, ensemble keys {len(ens["hourly"])}')
    return dict(raw=raw, down=down, ens=ens, fetched=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'))


def om_series(om):
    """Open-Meteo deterministic models through the same free-air step as the GRIB models."""
    h, d = om['raw']['hourly'], om['down']['hourly']
    out = {}
    for m, name in OM_MODELS.items():
        rows = []
        for k, t in enumerate(h['time']):
            if k % 6:
                continue
            levels = []
            for p in LEVELS:
                g = lambda v: h.get(f'{v}_{p}hPa_{m}', [None] * (k + 1))[k]  # noqa: E731
                ws, wd = g('wind_speed'), g('wind_direction')
                u = v = None
                if ws is not None and wd is not None:
                    import math
                    u = -ws / 3.6 * math.sin(math.radians(wd))
                    v = -ws / 3.6 * math.cos(math.radians(wd))
                levels.append(dict(p=p, gh=g('geopotential_height'), t=g('temperature'), u=u, v=v,
                                   rh=g('relative_humidity')))
            fa = sc.free_air(levels, sc.SITES['summit']['z'])
            rows.append(dict(valid=t + 'Z', step=k, summit=dict(
                fa=fa, flags=sc.step_flags(fa), raw2t=h.get(f'temperature_2m_{m}', [None] * (k + 1))[k],
                wind10=h.get(f'wind_speed_10m_{m}', [None] * (k + 1))[k],
                om_down=dict(t2=d.get(f'temperature_2m_{m}', [None] * (k + 1))[k],
                             gust=d.get(f'wind_gusts_10m_{m}', [None] * (k + 1))[k]))))
        gusts = [x for x in d.get(f'wind_gusts_10m_{m}', []) if x is not None]
        out[name] = dict(series=rows, gust_max_72h=max(gusts) if gusts else None,
                         grid_height=om['raw'].get('elevation'))
    return out


def ens_members(om):
    """Summit free-air wind for every ensemble member, every 6 h."""
    h = om['ens']['hourly']
    z = sc.SITES['summit']['z']
    out = {}
    for m, label in ENS_MODELS.items():
        tag = {'ecmwf_ifs025': 'ecmwf_ifs025_ensemble', 'gfs025': 'ncep_gefs025', 'icon_global': 'icon_global_eps'}[m]
        if not any(k.endswith(tag) for k in h):
            continue
        members = sorted({k.split('_member')[1].split('_')[0] for k in h if '_member' in k and k.endswith(tag)})
        steps = []
        for k, t in enumerate(h['time']):
            if k % 6:
                continue
            winds, temps = [], []
            for mem in [''] + [f'_member{x}' for x in members]:
                lv = [dict(p=p, gh=h.get(f'geopotential_height_{p}hPa{mem}_{tag}', [None] * (k + 1))[k],
                           w=h.get(f'wind_speed_{p}hPa{mem}_{tag}', [None] * (k + 1))[k],
                           t=h.get(f'temperature_{p}hPa{mem}_{tag}', [None] * (k + 1))[k]) for p in LEVELS]
                w, _ = sc.interp_height(lv, z, 'w')
                tt, _ = sc.interp_height(lv, z, 't')
                if w is not None and tt is not None:
                    winds.append(round(w, 1))
                    temps.append(round(tt, 1))
            steps.append(dict(valid=t + 'Z', winds=winds, temps=temps))
        if any(st['winds'] for st in steps):
            out[label] = dict(n=len(members) + 1, steps=steps)
    return out
