#!/usr/bin/env python3
"""wind_live.py · HMD-S11 · tomorrow's takeoff wind for a Tehran flying site, standard library only.

    python3 -I artifact/wind_live.py                 # fetch ECMWF IFS + AIFS (open data) + NOAA GFS + METAR (2–5 min), build the page
    python3 -I artifact/wind_live.py --offline       # no network: build from artifact/derived/latest.json
    python3 -I artifact/wind_live.py --replay derived/replay-2026-11-28.json   # a saved run, labelled REPLAY
    python3 -I artifact/wind_live.py --facing 135    # another slope direction (the club decides which takeoff)
    python3 -I artifact/wind_live.py --serve         # build, then serve http://127.0.0.1:8767/wind_live.html
    python3 -I artifact/wind_live.py --selftest      # offline checks: units, components, gust factor, interpolation, thermals
    python3 -I artifact/wind_eval.py                 # (separate) forecast vs METAR for April 2025 -> derived/eval-2025-04.json

Views (keys 1–5): 1 takeoff window · 2 wind by height + hodograph · 3 boundary layer and thermals ·
4 forecast vs observation · 5 the indicator's logic.
A teaching tool. It is not a flying-weather service and it never says it is safe to fly.
"""
import argparse
import datetime as dt
import http.server
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wind_core as wc  # noqa: E402

DERIVED = HERE / 'derived'
LATEST = DERIVED / 'latest.json'
EVAL = DERIVED / 'eval-2025-04.json'
CASE = DERIVED / 'case-2025-04-17.json'
PAGE = HERE / 'wind_live.html'
TEHRAN = dt.timedelta(hours=3, minutes=30)        # Iran has kept UTC+3:30 all year since 2022 [VERIFY]
SITE_KEYS = ['shahran', 'oiii']
PTS = [(wc.SITES[s]['lat'], wc.SITES[s]['lon']) for s in SITE_KEYS]
HOURS_UTC = range(3, 16)
FACINGS = range(0, 360, 45)                      # the page can switch the slope direction                         # 06:30–18:30 Tehran time
MODELS = {
    'gfs': dict(label='NOAA GFS 0.25° (hourly)', licence='US public domain · NOAA/NCEP NOMADS'),
    'ifs': dict(label='ECMWF IFS 0.25° (3-hourly)', licence='CC BY 4.0 · ECMWF open data'),
    'aifs': dict(label='ECMWF AIFS 0.25° (AI, 6-hourly)', licence='CC BY 4.0 · ECMWF open data'),
}


def iso(t):
    return t.strftime('%Y-%m-%dT%H:%MZ')


def fetch(log=print):
    import wind_fetch as wf
    now = dt.datetime.now(dt.timezone.utc)
    day = (now + TEHRAN).date() + dt.timedelta(days=1)            # "tomorrow" in Tehran
    first = dt.datetime.combine(day, dt.time(min(HOURS_UTC)), dt.timezone.utc)
    last = dt.datetime.combine(day, dt.time(max(HOURS_UTC)), dt.timezone.utc)
    out = dict(made=iso(now), target_local_date=str(day), models={})
    for key, every in (('ifs', 3), ('aifs', 6)):
        try:
            run = wf.ecmwf_latest(key, int((last - now).total_seconds() // 3600 // every * every + 2 * every))
            lo = int((first - run).total_seconds() // 3600) // every * every
            hi = -(-int((last - run).total_seconds() // 3600) // every) * every
            steps = sorted({0} | set(range(lo, hi + 1, every)))
            vals = wf.ecmwf_points(key, run, steps, PTS)
            rows, zs = wf.ecmwf_rows(vals, run, SITE_KEYS)
            out['models'][key] = dict(MODELS[key], run=run.strftime('%Y-%m-%d %HZ'), zsfc=zs,
                                      rows=[r for r in rows if r['step'] in steps[1:]])
            log(f'  {key}: run {run:%Y-%m-%d %H}Z, steps {steps}')
        except Exception as e:
            log(f'  {key}: FAILED ({e})')
    try:
        run = wf.gfs_latest(int((last - now).total_seconds() // 3600) + 6)
        steps = [int((dt.datetime.combine(day, dt.time(h), dt.timezone.utc) - run).total_seconds() // 3600) for h in HOURS_UTC]
        rows, zs = wf.gfs_rows(run, steps, PTS, SITE_KEYS)
        out['models']['gfs'] = dict(MODELS['gfs'], run=run.strftime('%Y-%m-%d %HZ'), zsfc=zs, rows=rows)
        log(f'  gfs: run {run:%Y-%m-%d %H}Z, steps {steps[0]}–{steps[-1]}')
    except Exception as e:
        log(f'  gfs: FAILED ({e})')
    try:
        obs = wf.iem_metar('OIII', now - dt.timedelta(days=3), now + dt.timedelta(days=1))
        status, text = wf.awc_metar()
        out['metar'] = dict(iem_last=obs[-1] if obs else None, iem_n_72h=len(obs), awc_status=status,
                            awc_text=text.strip()[:400], checked=iso(now))
        log(f'  metar: IEM {len(obs)} reports in 72 h; aviationweather.gov HTTP {status}')
    except Exception as e:
        out['metar'] = dict(error=str(e), checked=iso(now))
    DERIVED.mkdir(exist_ok=True)
    LATEST.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    log(f'wrote {LATEST.relative_to(HERE.parent)}')
    return out


def hour_view(model, row, zg, site, facing):
    """Everything the page needs for one model, one valid time, one site."""
    s = row[site]
    z = wc.SITES[site]['z']
    if zg is None and s.get('sp') is not None:                 # model ground from surface pressure (if no z field)
        zg = height_of_pressure(s['levels'], s['sp'])
    col = wc.column(s['levels'], zg or 0, s.get('u10'), s.get('v10'), s.get('t2'), s.get('td2'))
    w10 = None if s.get('u10') is None else dict(speed=round(wc.speed_kmh(s['u10'], s['v10']), 1),
                                                   dir=round(wc.direction_from(s['u10'], s['v10'])))
    at = wc.wind_at(col, max(z, (zg or 0) + 10))
    gf = wc.gust_factor(s.get('gust'), w10['speed']) if w10 and w10['speed'] >= 5 else None
    spread10 = wc.gust_spread(s.get('gust'), w10 and w10['speed'])
    gust_to = None if spread10 is None or at is None else round(at['speed'] + spread10, 1)   # carry the spread up, not the factor
    top = wc.thermal_top(s.get('t2'), zg or 0, col)
    ws = wc.w_star(s.get('shf'), s.get('hpbl'), s.get('t2'), s.get('sp')) if model == 'gfs' else None
    aloft = wc.wind_at(col, z + 1000)
    sh = wc.shear(col, max(z, (zg or 0) + 10), z + 1000)
    hv = dict(valid=row['valid'], zg=zg, w10=w10, takeoff=None if at is None else dict(speed=at['speed'], dir=at['dir'], how=at['how']),
              gust10=None if s.get('gust') is None else round(s['gust'], 1), gust_factor=None if gf is None else round(gf, 2),
              gust_takeoff=gust_to, aloft=None if aloft is None else dict(speed=aloft['speed'], dir=aloft['dir']),
              shear=sh, t2=s.get('t2'), td2=s.get('td2'), cape=None if s.get('cape') is None else round(s['cape']),
              hpbl=None if s.get('hpbl') is None else round(zg + s['hpbl']), shf=s.get('shf'),
              w_star=None if ws is None else round(ws, 2),
              thermal_top=None if top is None else round(top), cloudbase=None if wc.cloudbase(s.get('t2'), s.get('td2'), zg or 0) is None
              else round(wc.cloudbase(s['t2'], s['td2'], zg or 0)),
              ti_takeoff_plus_1000=wc.thermal_index(s.get('t2'), zg or 0, col, z + 1000),
              profile=[dict(p=l['p'], gh=round(l['gh']), t=None if l.get('t') is None else round(l['t'], 1),
                            speed=round(wc.speed_kmh(l['u'], l['v']), 1), dir=round(wc.direction_from(l['u'], l['v'])),
                            u=round(l['u'] * 3.6, 1), v=round(l['v'] * 3.6, 1))
                       for l in col if l.get('u') is not None and l.get('v') is not None])
    inp = dict(wind=at and at['speed'], dir=at and at['dir'], gust=gust_to, aloft=aloft and aloft['speed'],
               shear=sh and sh['vector'], w_star=ws, cape=s.get('cape'))
    hv['indicator'] = {str(f): wc.indicator(inp, f) for f in FACINGS}
    return hv


def height_of_pressure(levels, p):
    """Height (m) where the pressure is p, by log-pressure interpolation between levels (model ground from sp)."""
    import math
    lv = sorted((l for l in levels if l.get('gh') is not None), key=lambda l: -l['p'])
    for a, b in zip(lv, lv[1:]):
        if a['p'] >= p >= b['p']:
            return round(a['gh'] + (math.log(a['p'] / p) / math.log(a['p'] / b['p'])) * (b['gh'] - a['gh']))
    return None


def build(data, facing, label=None):
    models = {}
    for key, m in data['models'].items():
        zg = m.get('zsfc', {}).get('shahran')
        models[key] = dict(label=m['label'], licence=m['licence'], run=m['run'],
                           hours=[hour_view(key, r, zg, 'shahran', facing) for r in m['rows']
                                  if int(r['valid'][11:13]) in HOURS_UTC])
        zgs = [h['zg'] for h in models[key]['hours'] if h['zg'] is not None]
        models[key]['zg'] = zgs[0] if zgs else None
    ev = json.loads(EVAL.read_text(encoding='utf-8')) if EVAL.exists() else None
    case = json.loads(CASE.read_text(encoding='utf-8')) if CASE.exists() else None
    page = dict(made=label or data['made'], target=data.get('target_local_date'), site=wc.SITES['shahran'], facing=facing,
                airport=wc.SITES['oiii'], thresholds=wc.THRESHOLDS, models=models, metar=data.get('metar'), eval=ev, case=case)
    html = (HERE / 'wind_page.html').read_text(encoding='utf-8')
    PAGE.write_text(html.replace('__DATA__', json.dumps(page, ensure_ascii=False, separators=(',', ':'))), encoding='utf-8')
    print(f'wrote {PAGE.relative_to(HERE.parent)} · tomorrow (Tehran) = {page["target"]} · facing {facing}°')
    for key, m in models.items():
        labs = ' '.join(f"{(dt.datetime.strptime(h['valid'], '%Y-%m-%dT%H:%MZ') + TEHRAN):%H:%M}={h['indicator'][str(facing)]['label']}"
                        for h in m['hours'])
        print(f'  {key:5} run {m["run"]} · model ground {m["zg"]} m (real takeoff {wc.SITES["shahran"]["z"]} m) · {labs}')
    if ev:
        st = ev['stats']['all']
        print(f"  eval {ev['start']} +{ev['days']} d at OIII: wind MAE IFS {st['ifs']['wind']['mae']} / AIFS {st['aifs']['wind']['mae']} km/h,"
              f" bias {st['ifs']['wind']['bias']} / {st['aifs']['wind']['bias']}; IFS gust bias {st['ifs']['gust']['bias']}")
    return page


def serve(port=8767):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(HERE), **kw)  # noqa: E731
    with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as srv:
        print(f'open http://127.0.0.1:{port}/wind_live.html   (Ctrl-C to stop)')
        srv.serve_forever()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--offline', action='store_true', help='no network; use artifact/derived/latest.json')
    ap.add_argument('--replay', help='build from a saved run (path relative to artifact/)')
    ap.add_argument('--facing', type=int, default=wc.SITES['shahran']['facing'], choices=list(FACINGS), help='slope direction, degrees')
    ap.add_argument('--serve', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        import wind_selftest
        sys.exit(wind_selftest.run())
    if a.replay:
        d = json.loads((HERE / a.replay).read_text(encoding='utf-8'))
        build(d, a.facing, label='REPLAY of run fetched ' + d['made'])
    elif a.offline:
        if not LATEST.exists():
            sys.exit('no artifact/derived/latest.json yet: run once with network')
        build(json.loads(LATEST.read_text(encoding='utf-8')), a.facing)
    else:
        build(fetch(), a.facing)
    if a.serve:
        serve()
