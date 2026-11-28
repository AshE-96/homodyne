#!/usr/bin/env python3
"""chalus_live.py · HMD-S07 · "when is the Chalus road quiet?" — the recording page. Standard library (numpy optional, faster).

    python3 -I artifact/chalus_live.py                       # SYNTHETIC fixture → artifact/chalus_live.html (MOCK watermark)
    python3 -I artifact/chalus_live.py --data artifact/data/chalus_hourly.csv
                                                             # the owner's real 141 data → artifact/data/chalus_live_real.html
    python3 -I artifact/chalus_live.py --serve               # build, then http://127.0.0.1:8767/chalus_live.html
    python3 -I artifact/chalus_live.py --selftest            # offline checks (calendar, ingest, model, folds, page)

Views (keys 1–4): 1 heatmap hour × weekday per direction · 2 holidays overlaid on the ordinary week ·
3 the race on held-out days (baselines vs boosted trees) · 4 departure-window picker for Nowruz 1406.
The counter sees one point of the road: this page never gives a door-to-door travel time, and a closed road is
never "quiet". It is a teaching tool, not a traffic service; the police decide closures on the day.
"""
import argparse
import datetime as dt
import http.server
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chalus_core as cc  # noqa: E402
import chalus_eval as ce  # noqa: E402

FIXTURE = HERE / 'fixture' / 'SYNTHETIC_chalus_hourly.csv'
PICK_FROM, PICK_TO = cc.j2g(1405, 12, 20), cc.j2g(1406, 1, 15)         # 11 Mar – 4 Apr 2027: the Nowruz 1406 trip window


def heat(rows, keyf):
    """{key: {dir: {'speed': [24], 'count': [24], 'closed': [24]}}} medians by key and hour."""
    acc = defaultdict(lambda: defaultdict(lambda: dict(speed=[], count=[], closed=[])))
    for r in rows:
        k = keyf(r)
        if k is None:
            continue
        a = acc[k][r['dir'], r['hour']]
        a['closed'].append(1 if r['closed'] else 0)
        if cc.usable(r):
            a['count'].append(r['count'])
            if r['speed'] is not None:
                a['speed'].append(r['speed'])
    out = {}
    for k, cells in acc.items():
        out[k] = {}
        for x in cc.DIRS:
            row = [cells.get((x, h), dict(speed=[], count=[], closed=[])) for h in range(24)]
            out[k][x] = dict(speed=[cc.median(c['speed']) for c in row], count=[cc.median(c['count']) for c in row],
                             closed=[round(sum(c['closed']) / len(c['closed']), 2) if c['closed'] else 0 for c in row],
                             n=max(len(c['closed']) for c in row))
    return out


def build_data(path, synthetic_expected=None):
    t0 = time.time()
    rows, synthetic, comments = cc.read_hourly(path)
    if synthetic_expected is False and synthetic:
        raise SystemExit('this file says SYNTHETIC: it cannot be used as real data')
    holidays, anomalies = cc.load_holidays(), cc.load_anomalies()
    rows = [r for r in rows if r['date'] not in anomalies]
    ce.annotate(rows, holidays)
    ordinary = heat(rows, lambda r: None if (r['_cal']['off'] and r['_cal']['dow'] != 6) or r['_cal']['nz'] != 99
                    else 'dow%d' % r['_cal']['dow'])
    special_keys = ['eve', 'blk-first', 'blk-mid', 'blk-last', 'after'] + ['nz%+d' % k for k in range(-3, 14)]
    special = heat(rows, lambda r: r['_key'] if r['_key'] in special_keys else None)
    report = ce.evaluate(rows, holidays)
    # the picker: every model trained on all the data, forecasting Nowruz 1406
    boosted = cc.Boosted().fit(rows, rows)
    profile = cc.Profile().fit(rows, rows)
    pick = []
    d = PICK_FROM
    while d <= PICK_TO:
        cal = cc.day_features(d, holidays)
        day = dict(date=str(d), jalali=cc.jstr(d), dow=cal['dow'], off=cal['off'], key=cc.day_key(cal),
                   holiday=holidays.get(d, ''), dirs={})
        for x in cc.DIRS:
            hrs = ce.day_forecast(boosted, profile, d, x, holidays)
            day['dirs'][x] = dict(hours=hrs, best=ce.best_windows(hrs))
        pick.append(day)
        d += dt.timedelta(days=1)
    days = sorted({r['date'] for r in rows})
    return dict(meta=dict(synthetic=synthetic, source=str(Path(path).name), comments=comments,
                          first=str(days[0]), last=str(days[-1]), first_j=cc.jstr(days[0]), last_j=cc.jstr(days[-1]),
                          n_hours=len(rows), n_closed=sum(1 for r in rows if r['closed']), anomalies=len(anomalies),
                          thresholds=dict(A=cc.SPEED_A, C=cc.SPEED_C), seconds=round(time.time() - t0, 1),
                          built=dt.datetime.now().strftime('%Y-%m-%d %H:%M'), dir_label=cc.DIR_LABEL,
                          model_label=cc.MODEL_LABEL, weekdays_fa=cc.WEEKDAY_FA, weekdays_en=cc.WEEKDAY_EN),
                ordinary=ordinary, special=special, special_keys=special_keys, report=report, pick=pick)


def build(path=FIXTURE, out=None):
    data = build_data(path)
    real = not data['meta']['synthetic']
    out = out or ((HERE / 'data' / 'chalus_live_real.html') if real else (HERE / 'chalus_live.html'))
    out.parent.mkdir(parents=True, exist_ok=True)
    html = (HERE / 'chalus_page.html').read_text(encoding='utf-8')
    rel = '../' if out.parent != HERE else ''
    html = html.replace('__FONTS__', rel + '../../../../brand/fonts/')
    out.write_text(html.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':'))), encoding='utf-8')
    summ = (HERE / 'derived' / ('results-real.json' if real else 'results-SYNTHETIC.json'))
    if real:
        summ = HERE / 'data' / 'results-real.json'     # stays git-ignored until the owner has read the 141 terms
    summ.write_text(json.dumps(dict(meta={k: v for k, v in data['meta'].items() if k != 'comments'},
                                    report=[{k: v for k, v in f.items() if k != 'series'} for f in data['report']]),
                               ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'wrote {out.relative_to(HERE.parent)} · {"REAL data" if real else "SYNTHETIC fixture (MOCK watermark)"} · '
          f'{data["meta"]["first_j"]} … {data["meta"]["last_j"]} · {data["meta"]["seconds"]} s · summary {summ.relative_to(HERE.parent)}')
    for f in data['report']:
        print(f'  {f["label"]}: ' + ' · '.join(f'{k} {v["mae_count"]} veh/h (skill {v["skill_vs_last_week"]:+.2f}, C-recall {v["recall_C"]})'
                                               for k, v in f['models'].items()))
    return out


def serve(port=8767):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(HERE.parents[3]), **kw)  # noqa: E731
    rel = HERE.relative_to(HERE.parents[3]).as_posix()
    with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as srv:
        print(f'open http://127.0.0.1:{port}/{rel}/chalus_live.html   (Ctrl-C to stop)')
        srv.serve_forever()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--data', type=Path, help='hourly CSV from chalus_prep.py (default: the SYNTHETIC fixture)')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--serve', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        import chalus_selftest
        sys.exit(chalus_selftest.main())
    if a.data is None and not FIXTURE.exists():
        import chalus_fixture
        chalus_fixture.write(chalus_fixture.simulate((chalus_fixture.END - chalus_fixture.START).days + 1, cc.load_holidays()), FIXTURE)
    build(a.data or FIXTURE)
    if a.serve:
        serve()
