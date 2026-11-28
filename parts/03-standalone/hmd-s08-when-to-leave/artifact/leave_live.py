#!/usr/bin/env python3
"""leave_live.py · HMD-S08 · "when should I leave to arrive on time?" on real NYC taxi trips. Standard library only.

    python3 -I artifact/leave_live.py                  # build artifact/leave_live.html from derived/weekday_trips.csv
    python3 -I artifact/leave_live.py --serve          # build, then serve http://127.0.0.1:8768/leave_live.html
    python3 -I artifact/leave_live.py --report         # every number the episode uses (also derived/episode_numbers.json)
    python3 -I artifact/leave_live.py --ask jfk 18:00 95   # one terminal answer: route, deadline, confidence %
    python3 -I artifact/leave_live.py --selftest       # offline checks: quantile maths, newsvendor, backtest, data, page

The page (one screen, 1600x900): pick a route and a deadline, set the confidence (or the late:early cost ratio);
it draws the travel-time band for every departure time, marks the latest safe departure, shows the trip-time
histogram for that departure, and backtests the advice on held-out April weekdays.
URL parameters fix a state for a take: leave_live.html?route=jfk&deadline=18:00&conf=95 (&ratio=19 &clean=1)
No network, no keys. Model: "your trip = the trips that really left within 15 minutes of you on past weekdays".
"""
import argparse
import hashlib
import http.server
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import leave_core as L  # noqa: E402

PAGE_TMPL, PAGE, JS = HERE / 'leave_page.html', HERE / 'leave_live.html', HERE / 'leave_core.js'
NUMBERS = HERE / 'derived' / 'episode_numbers.json'
HMD009 = HERE.parent.parent / 'hmd-009-maps-eta' / 'artifact' / 'derived' / 'midtown_jfk_trips.csv'
DATA_SHA = 'ad11a755f177f30fd90ec02d07bffae3b2d2ba3e64eb821e4e211fdda9b96550'
DEADLINES = range(7 * 60, 22 * 60 + 1, 30)          # the 31 deadlines of the calibration table
HERO = dict(route='jfk', deadline=18 * 60)

# Numbers spoken in script-fa.md / shown in the deck. --selftest fails if the data or code stops producing them.
EPISODE = {
    'rows': 30750, 'jfk_rows': 8509, 'train_days': 30, 'test_days': 14,
    'hero_n_1645': 234, 'hero_mean_1645': 74.8, 'hero_p50_1645': 74.2, 'hero_p95_1645': 99.7, 'hero_p05_1645': 52.1,
    'on_time_1600': 100.0, 'on_time_1615': 99.3, 'on_time_1620': 96.8, 'on_time_1630': 86.9, 'on_time_1645': 52.1,
    'leave_mean': '16:45', 'leave_50': '16:45', 'leave_90': '16:25', 'leave_95': '16:20',
    'bt_late_mean': 72.7, 'bt_late_95': 8.3, 'bt_days_late_mean': 14, 'bt_days_late_95': 5,
    'p50_1300': 59.6, 'p95_1600': 92.8, 'p95_1630': 99.4, 'arr95_1600': '17:33', 'arr95_1630': '18:09',
    'arr95_1730': '19:03', 'arr95_1830': '19:40', 'bi_1645': 0.33, 'pti_1645': 2.91, 'free_flow': 34.3,
    'cal_late_95': {'jfk': 11.0, 'lga': 3.7, 'ewr': 5.1, 'fidi': 6.1},
    'cal_late_mean': {'jfk': 64.9, 'lga': 32.8, 'ewr': 33.1, 'fidi': 35.9},
    'jfk_med_1518_train': 71.2, 'jfk_med_1518_test': 83.2, 'cal_late_95_jfk_without_recess': 10.3,
    'bt_trips_mean': 77, 'bt_trips_95': 108,
}


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def numbers(data=None):
    data = data or L.load()
    out = {'rows': sum(len(v) for v in data.values()), 'jfk_rows': len(data['jfk'])}
    tr, te = L.split(data['jfk'])
    out['train_days'], out['test_days'] = len({d for d, _, _ in tr}), len({d for d, _, _ in te})
    idx, D = L.Index(tr), HERO['deadline']
    s = L.stats(idx.sample(16 * 60 + 45))
    out.update(hero_n_1645=s['n'], hero_mean_1645=round(s['mean'], 1), hero_p50_1645=round(s['p50'], 1),
               hero_p95_1645=round(s['p95'], 1), hero_p05_1645=round(s['p05'], 1))
    for t in (960, 975, 980, 990, 1005):
        out[f'on_time_{L.hhmm(t).replace(":", "")}'] = round(100 * L.on_time_share(idx.sample(t), D - t), 1)
    t_mean, picks = L.leave_by_mean(idx, D), {c: L.leave_by(idx, D, c / 100) for c in (50, 90, 95)}
    out['leave_mean'] = L.hhmm(t_mean)
    out.update({f'leave_{c}': L.hhmm(t) for c, t in picks.items()})
    bm, b95 = L.backtest(te, t_mean, D), L.backtest(te, picks[95], D)
    out.update(bt_late_mean=round(100 * bm['late_share'], 1), bt_late_95=round(100 * b95['late_share'], 1),
               bt_days_late_mean=bm['days_with_late'], bt_days_late_95=b95['days_with_late'],
               bt_trips_mean=bm['trips'], bt_trips_95=b95['trips'])
    out['p50_1300'] = round(L.stats(idx.sample(13 * 60))['p50'], 1)
    for t in (960, 990):
        out[f'p95_{L.hhmm(t).replace(":", "")}'] = round(L.stats(idx.sample(t))['p95'], 1)
    for t in (960, 990, 1050, 1110):
        out[f'arr95_{L.hhmm(t).replace(":", "")}'] = L.hhmm(round(t + L.stats(idx.sample(t))['p95']))
    r = L.reliability(idx, 16 * 60 + 45)
    out.update(bi_1645=round(r['buffer_index'], 2), pti_1645=round(r['planning_time_index'], 2),
               free_flow=round(r['free_flow'], 1))
    cal95, calm = {}, {}
    for route, trips in data.items():
        a, b = L.split(trips)
        ix = L.Index(a)
        for rule, store in (('95', cal95), ('mean', calm)):
            n = late = 0
            for dl in DEADLINES:
                t = L.leave_by(ix, dl, .95) if rule == '95' else L.leave_by_mean(ix, dl)
                if t is not None:
                    bt = L.backtest(b, t, dl)
                    n, late = n + bt['trips'], late + bt['late']
            store[route] = round(100 * late / n, 1)
    out['cal_late_95'], out['cal_late_mean'] = cal95, calm
    a, b = L.split(data['jfk'])
    ix = L.Index([x for x in a if not ('2026-04-02' <= x[0] <= '2026-04-10')])   # NYC school spring recess (sources.md)
    n = late = 0
    for dl in DEADLINES:
        t = L.leave_by(ix, dl, .95)
        if t is not None:
            bt = L.backtest(b, t, dl)
            n, late = n + bt['trips'], late + bt['late']
    out['cal_late_95_jfk_without_recess'] = round(100 * late / n, 1)
    win = lambda S: sorted(m for _, d, m in S if 900 <= d < 1080)  # noqa: E731
    out['jfk_med_1518_train'] = round(L.quantile(win(tr), .5), 1)
    out['jfk_med_1518_test'] = round(L.quantile(win(te), .5), 1)
    from datetime import date, timedelta
    weeks = {}
    for d, dep, m in data['jfk']:
        if 900 <= dep < 1080:
            day = date.fromisoformat(d)
            weeks.setdefault(str(day - timedelta(days=day.weekday())), []).append(m)
    out['jfk_week_median_1518'] = {k: round(L.quantile(sorted(v), .5), 1) for k, v in sorted(weeks.items())}
    return out


def report():
    n = numbers()
    NUMBERS.write_text(json.dumps(n, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    w = 34
    print('HMD-S08 · numbers for the episode (NYC TLC yellow taxi, weekdays Mar-Apr 2026; our computation)')
    for k, v in n.items():
        print(f'  {k:{w}} {v}')
    print(f'wrote {NUMBERS.relative_to(HERE.parent)}')


def ask(route, deadline, conf):
    data = L.load()
    tr, te = L.split(data[route])
    idx = L.Index(tr)
    h, m = map(int, deadline.split(':'))
    D, c = h * 60 + m, conf / 100
    t, tm = L.leave_by(idx, D, c), L.leave_by_mean(idx, D)
    print(f'{L.ROUTES[route][0]} · arrive by {deadline} · weekdays · trained on {len({x[0] for x in tr})} days before {L.SPLIT}')
    for name, tt in ((f'{conf:g}% confidence', t), ('trust the average', tm)):
        if tt is None:
            print(f'  {name:20} no estimate (too few trips)')
            continue
        s, bt = L.stats(idx.sample(tt)), L.backtest(te, tt, D)
        late = f'{100 * bt["late_share"]:.0f}% of {bt["trips"]} trips late, {bt["days_with_late"]}/{bt["days"]} days' if bt['trips'] else 'no test trips'
        print(f'  {name:20} leave {L.hhmm(tt)}  (median {s["p50"]:.0f}, P95 {s["p95"]:.0f} min, n={s["n"]})  · April backtest: {late}')


def page_data():
    data = L.load()
    days = sorted({d for v in data.values() for d, _, _ in v})
    routes = {}
    for code, trips in data.items():
        routes[code] = dict(label=L.ROUTES[code][0], fa=L.ROUTES[code][1],
                            trips=[[days.index(d), dep, m] for d, dep, m in trips])
    tr, te = L.split(data['jfk'])
    idx = L.Index(tr)
    check = dict(route='jfk', deadline=HERO['deadline'], leave95=L.leave_by(idx, HERO['deadline'], .95),
                 leave_mean=L.leave_by_mean(idx, HERO['deadline']),
                 late95=L.backtest(te, L.leave_by(idx, HERO['deadline'], .95), HERO['deadline'])['late'])
    return dict(days=days, split=L.SPLIT, half=L.HALF, bt_half=L.BT_HALF, step=L.STEP, horizon=L.HORIZON,
                min_n=L.MIN_N, routes=routes, check=check)


def build():
    blob = json.dumps(page_data(), ensure_ascii=False, separators=(',', ':'))
    html = PAGE_TMPL.read_text(encoding='utf-8').replace('/*__CORE__*/', JS.read_text(encoding='utf-8'))
    PAGE.write_text(html.replace('__DATA__', blob), encoding='utf-8')
    print(f'wrote {PAGE.relative_to(HERE.parent)}  ({PAGE.stat().st_size // 1024} KB)')


def selftest():
    ok = True

    def check(name, cond, detail=''):
        nonlocal ok
        ok &= bool(cond)
        print(('  ok    ' if cond else '  FAIL  ') + f'{name:46} {detail}')

    import random
    import statistics
    q = L.quantile
    check('quantile [1,2,3,4] at 0.5 = 2.5', q([1, 2, 3, 4], .5) == 2.5)
    check('quantile 1..20 at 0.95 = 19.05', abs(q(list(range(1, 21)), .95) - 19.05) < 1e-12)
    rng = random.Random(8)
    xs = sorted(rng.lognormvariate(4, .25) for _ in range(997))
    ref = statistics.quantiles(xs, n=100, method='inclusive')
    check('quantile = statistics.quantiles(inclusive)', all(abs(q(xs, k / 100) - ref[k - 1]) < 1e-9 for k in range(1, 100)))
    check('critical q: late 19x early -> 0.95', abs(L.critical_q(19, 1) - .95) < 1e-12)
    check('critical q: equal costs -> 0.5 (median)', L.critical_q(1, 1) == .5)
    real = sorted(m for _, d, m in L.load()['jfk'] if abs(d - 1005) <= 15 and d >= 0)
    for sample, nm in ((xs, 'lognormal'), (real, 'JFK 16:45 trips')):
        for cl, ce in ((1, 1), (9, 1), (19, 1), (3, 2)):
            qq = L.critical_q(cl, ce)
            b = L.best_budget(sample, cl, ce)
            rank = sample.index(b) + 1
            fine = L.expected_cost(sample, b, cl, ce) <= L.expected_cost(sample, q(sample, qq), cl, ce) + 1e-9
            check(f'newsvendor argmin = q-quantile ({nm}, {cl}:{ce})', fine and abs(rank - qq * len(sample)) <= 1,
                  f'rank {rank} of {len(sample)}, q*n = {qq * len(sample):.1f}')
    # synthetic backtest with a known answer: 8 of 10 trips take 60 min, 2 take 90
    syn = [(f'2026-04-{13 + i:02d}', 600, 60.0 if i < 8 else 90.0) for i in range(10)]
    bt = L.backtest(syn, 600, 600 + 70)
    check('backtest on synthetic trips: 2 of 10 late', bt['late'] == 2 and bt['trips'] == 10 and bt['days_with_late'] == 2)
    check('backtest window excludes trips 11 min away', L.backtest([('2026-04-13', 611, 99.0)], 600, 610)['trips'] == 0)
    syn_tr = [('2026-03-02', d, 30.0 + (d % 10)) for d in range(400, 800) for _ in range(3)]
    ix = L.Index(syn_tr)
    t = L.leave_by(ix, 700, .95)
    check('leave_by obeys t + Q(t) <= D, t+5 does not', t + q(ix.sample(t), .95) <= 700 < t + 5 + q(ix.sample(t + 5), .95), L.hhmm(t))
    # the real data
    check('weekday_trips.csv sha256 = SOURCE.txt', sha256(L.DATA) == DATA_SHA)
    data = L.load()
    from datetime import date
    check('all rows are weekdays, Mar 2 .. Apr 30', all(date.fromisoformat(d).weekday() < 5 and '2026-03-02' <= d <= '2026-04-30'
                                                       for v in data.values() for d, _, _ in v))
    if HMD009.exists():
        import csv
        with open(HMD009, newline='') as f:
            ref = [(r['pickup'][:10], round(float(r['minutes']), 1)) for r in csv.DictReader(f)
                   if date.fromisoformat(r['pickup'][:10]).weekday() < 5]
        mine = [(d, m) for d, _, m in data['jfk']]
        check('JFK rows = HMD-009 weekday rows', len(ref) == len(mine) and sorted(ref) == sorted(mine), f'{len(mine)} vs {len(ref)}')
    else:
        print('  skip  HMD-009 derived CSV not found (cross-check skipped)')
    idx = L.Index(L.split(data['jfk'])[0])
    groups = [[L.leave_by(idx, d, c) for c in (.5, .8, .9, .95)] for d in DEADLINES]
    check('higher confidence never means leaving later', all(None not in g and g == sorted(g, reverse=True) for g in groups),
          f'{len(groups)} deadlines x 4 levels')
    got = numbers(data)
    bad = {k: (v, got.get(k)) for k, v in EPISODE.items() if got.get(k) != v}
    check('episode numbers reproduce (script, deck)', not bad, '; '.join(f'{k}: want {a} got {b}' for k, (a, b) in bad.items())[:300])
    build()
    html = PAGE.read_text(encoding='utf-8')
    check('page built with data and core', '__DATA__' not in html and 'function leaveBy' in html)
    node = shutil.which('node')
    if node:
        js = JS.read_text(encoding='utf-8') + '\nconst D=' + json.dumps(page_data()) + ';\nconsole.log(JSON.stringify(selfCheck(D)));'
        r = subprocess.run([node, '-e', js], capture_output=True, text=True, timeout=60)
        res = json.loads(r.stdout or '{}') if r.returncode == 0 else {}
        check('page JS = Python (leave95, mean rule, backtest)', res.get('ok') is True, r.stdout.strip()[:160] or r.stderr[:160])
    else:
        print('  skip  node not installed: JS parity check skipped')
    print('selftest ok' if ok else 'selftest FAILED')
    return 0 if ok else 1


def serve(port=8768):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(HERE), **kw)  # noqa: E731
    with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as srv:
        print(f'open http://127.0.0.1:{port}/leave_live.html?route=jfk&deadline=18:00&conf=95   (Ctrl-C to stop)')
        srv.serve_forever()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--serve', action='store_true')
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--ask', nargs=3, metavar=('ROUTE', 'HH:MM', 'CONF'))
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.report:
        sys.exit(report())
    if a.ask:
        sys.exit(ask(a.ask[0], a.ask[1], float(a.ask[2])))
    build()
    if a.serve:
        serve()
