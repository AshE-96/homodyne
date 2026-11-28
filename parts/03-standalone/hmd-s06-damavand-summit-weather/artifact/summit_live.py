#!/usr/bin/env python3
"""summit_live.py · HMD-S06 · a summit forecast page for Damavand, standard library only.

    python3 -I artifact/summit_live.py                # fetch ECMWF IFS + AIFS + NOAA GFS (about 5 min), build the page
    python3 -I artifact/summit_live.py --openmeteo    # also Open-Meteo (ICON + three ensembles) — owner's licence decision
    python3 -I artifact/summit_live.py --offline      # no network: build from artifact/derived/latest.json (+ data/ cache)
    python3 -I artifact/summit_live.py --replay derived/replay-2026-11-28.json   # the rehearsal run, labelled as such
    python3 -I artifact/summit_live.py --serve        # build, then serve http://127.0.0.1:8766/summit_live.html
    python3 -I artifact/summit_live.py --selftest     # offline checks: wind chill, ISA, lapse rate, GRIB decoder, alerts

Views (keys 1–4 on the page): 1 side by side · 2 height correction · 3 go / no-go windows · 4 alert logic.
This is a teaching tool. It is not a warning service and it never says a climb is safe.
"""
import argparse
import datetime as dt
import http.server
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import summit_core as sc  # noqa: E402

DERIVED = HERE / 'derived' / 'latest.json'
CACHE = HERE / 'data'                        # git-ignored: Open-Meteo responses (licence: owner's decision)
PAGE = HERE / 'summit_live.html'
MODELS = {
    'ifs': dict(label='ECMWF IFS 0.25°', licence='CC BY 4.0 · ECMWF open data', clean=True),
    'aifs': dict(label='ECMWF AIFS 0.25° (AI model)', licence='CC BY 4.0 · ECMWF open data', clean=True),
    'gfs': dict(label='NOAA GFS 0.25°', licence='US public domain · NOAA/NCEP NOMADS', clean=True),
    'om-icon': dict(label='DWD ICON (via Open-Meteo)', licence='Open-Meteo free API: non-commercial only — REHEARSAL', clean=False),
}


def combine_all(models, ensemble=None):
    """Per valid time and site: the combined label across models (+ ensemble wind fractions)."""
    times = sorted({r['valid'] for m in models.values() for r in m['series']})
    ens_by_t = {}
    for e in (ensemble or {}).values():
        for s in e['steps']:
            ens_by_t.setdefault(s['valid'], []).extend(s['winds'])
    steps = []
    for t in times:
        row = dict(valid=t)
        for site in sc.SITES:
            per = [r[site] for m in models.values() for r in m['series'] if r['valid'] == t and site in r]
            row[site] = sc.combine(per, ens_by_t.get(t) if site == 'summit' else None) if len(per) >= 2 else dict(label='too few models', worst=None, n=len(per))
        steps.append(row)
    wins = {site: sc.windows([dict(valid=s['valid'], combined=s[site]) for s in steps]) for site in sc.SITES}
    return steps, wins


def headline(models, om):
    """The numbers the script quotes: spread of model-surface gusts vs spread of free-air summit wind."""
    h = {}
    fa = {k: max(r['summit']['fa']['wind'] for r in m['series'] if r['summit'].get('fa')) for k, m in models.items()}
    h['freeair_wind_max_72h'] = fa
    h['freeair_ratio'] = round(max(fa.values()) / max(1e-9, min(fa.values())), 2)
    h['wind10_max_72h'] = {k: max(r['summit']['wind10'] or 0 for r in m['series']) for k, m in models.items()}
    h['orography'] = {k: m['orography'] for k, m in models.items()}
    if om:
        g = {k: v['gust_max_72h'] for k, v in om.items()}
        h['om_surface_gust_max_72h'] = g
        vals = [v for v in g.values() if v]
        h['om_gust_ratio'] = round(max(vals) / min(vals), 1) if vals else None
    return h


def fetch(with_om, log=print):
    import summit_fetch as sf
    out = {}
    for key in ('ifs', 'aifs'):
        try:
            run = sf.ecmwf_run(key)
            out[key] = dict(MODELS[key], run=run.strftime('%Y-%m-%d %HZ'), **sf.ecmwf_series(key, run, sf.ecmwf_fetch(key, run, log=log)))
        except Exception as e:  # keep going: a page with two models is still useful, and says so
            log(f'  {key}: FAILED ({e})')
    try:
        run = sf.gfs_run()
        out['gfs'] = dict(MODELS['gfs'], run=run.strftime('%Y-%m-%d %HZ'), **sf.gfs_fetch(run, log=log))
    except Exception as e:
        log(f'  gfs: FAILED ({e})')
    data = dict(made=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ'), models=out)
    DERIVED.parent.mkdir(exist_ok=True)
    DERIVED.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    log(f'wrote {DERIVED.relative_to(HERE.parent)}')
    if with_om:
        om = sf.om_fetch(log=log)
        CACHE.mkdir(exist_ok=True)
        (CACHE / 'openmeteo-latest.json').write_text(json.dumps(om), encoding='utf-8')
        log(f'wrote {(CACHE / "openmeteo-latest.json").relative_to(HERE.parent)} (git-ignored; rehearsal only)')
    return data


def build(data, use_om=True):
    import summit_fetch as sf
    models = dict(data['models'])
    om_path = CACHE / 'openmeteo-latest.json'
    om, ens, om_meta = None, None, None
    if use_om and om_path.exists():
        raw = json.loads(om_path.read_text(encoding='utf-8'))
        om = sf.om_series(raw)
        ens = sf.ens_members(raw)
        models['om-icon'] = dict(MODELS['om-icon'], run='latest at ' + raw['fetched'],
                                 orography=dict(summit=raw['raw'].get('elevation'), camp3=None), series=om['om-icon']['series'])
        om_meta = dict(fetched=raw['fetched'], models={k: dict(gust_max_72h=v['gust_max_72h'], grid_height=v['grid_height'])
                                                       for k, v in om.items()})
    steps, wins = combine_all(models, ens)
    page = dict(made=data['made'], sites=sc.SITES, thresholds=sc.THRESHOLDS, spread_wind=sc.SPREAD_WIND,
                lapse=sc.LAPSE_STD, isa={p: round(sc.isa_height(p)) for p in (400, 500, 600, 700)},
                models=models, ensemble=ens, om=om_meta, steps=steps, windows=wins,
                headline=headline({k: v for k, v in models.items() if v.get('series')}, om))
    html = (HERE / 'summit_page.html').read_text(encoding='utf-8')
    PAGE.write_text(html.replace('__DATA__', json.dumps(page, ensure_ascii=False, separators=(',', ':'))), encoding='utf-8')
    hl = page['headline']
    print(f'wrote {PAGE.relative_to(HERE.parent)}  models: {", ".join(models)}'
          + (('  ensemble: ' + ', '.join(f"{k} ({v['n']})" for k, v in ens.items())) if ens else ''))
    print('  free-air summit wind, max over 72 h (km/h):', hl['freeair_wind_max_72h'], ' ratio', hl['freeair_ratio'])
    if 'om_surface_gust_max_72h' in hl:
        print('  Open-Meteo 10 m gust at 5,610 m, max over 72 h (km/h):', hl['om_surface_gust_max_72h'], ' ratio', hl['om_gust_ratio'])
    print('  quieter windows in the models (NOT safe windows):', {k: v for k, v in wins.items()})
    return page


def serve(port=8766):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(HERE), **kw)  # noqa: E731
    with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as srv:
        print(f'open http://127.0.0.1:{port}/summit_live.html   (Ctrl-C to stop)')
        srv.serve_forever()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--offline', action='store_true', help='no network; use cached derived data')
    ap.add_argument('--openmeteo', action='store_true', help='also fetch Open-Meteo (owner licence decision)')
    ap.add_argument('--no-openmeteo-cache', action='store_true', help='build without the Open-Meteo cache even if present')
    ap.add_argument('--serve', action='store_true')
    ap.add_argument('--replay', help='build from a saved run (path relative to artifact/)')
    a = ap.parse_args()
    if a.selftest:
        import summit_selftest
        sys.exit(summit_selftest.run())
    if a.replay:
        data = json.loads((HERE / a.replay).read_text(encoding='utf-8'))
        data['made'] = 'REPLAY of run built ' + data['made']
    elif a.offline:
        if not DERIVED.exists():
            sys.exit('no artifact/derived/latest.json yet: run once with network')
        data = json.loads(DERIVED.read_text(encoding='utf-8'))
    else:
        data = fetch(a.openmeteo)
    build(data, use_om=not a.no_openmeteo_cache)
    if a.serve:
        serve()
