"""chalus_selftest.py · HMD-S07 · offline checks, no network, no keys. Run through: python3 -I artifact/chalus_live.py --selftest"""
import csv
import datetime as dt
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chalus_core as cc  # noqa: E402
import chalus_eval as ce  # noqa: E402
import chalus_fixture as fx  # noqa: E402
import chalus_prep as cp  # noqa: E402

OK = [True]


def check(name, cond, detail=''):
    OK[0] &= bool(cond)
    print(('  ok    ' if cond else '  FAIL  ') + f'{name:52} {detail}')


def fake_141_rows():
    """A 141-style export as we ASSUME it: Persian headers (Arabic ي/ك mixed in), Jalali times with Persian digits,
    15-minute rows, a 6-digit code per direction. Two hours × two directions."""
    fa = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    head = ['كد محور', 'نام محور', 'زمان شروع', 'زمان پايان', 'مدت زمان کارکرد (دقیقه)', 'تعداد کل وسیله نقلیه',
            'تعداد وسیله نقلیه کلاس ۱', 'تعداد وسیله نقلیه کلاس ۳', 'سرعت متوسط', 'تعداد برآورد شده']
    rows = []
    for code, base in (('111111', 100), ('222222', 40)):
        for hour in (13, 14):
            for q in range(4):
                c = base + 10 * q + (hour - 13)
                rows.append([code, 'کرج - چالوس', f'1405/01/13 {hour:02d}:{15 * q:02d}'.translate(fa),
                             f'1405/01/13 {hour:02d}:{15 * q + 14:02d}', '15', str(c), str(c - 5), '5',
                             str(60 - 10 * q), '0' if q else '2'])
    return head, rows


def write_xlsx(path, head, rows):
    def cell(ref, v):
        return f'<c r="{ref}" t="inlineStr"><is><t>{v}</t></is></c>'
    cols = 'ABCDEFGHIJKLMNOP'
    body = ''.join('<row r="%d">%s</row>' % (i + 1, ''.join(cell(f'{cols[j]}{i + 1}', v) for j, v in enumerate(r)))
                   for i, r in enumerate([head] + rows))
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('xl/worksheets/sheet1.xml', '<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/'
                   f'spreadsheetml/2006/main"><sheetData>{body}</sheetData></worksheet>')


def main():
    print('calendar')
    check('1 Farvardin 1404 = 21 Mar 2025', cc.farvardin1(1404) == dt.date(2025, 3, 21), str(cc.farvardin1(1404)))
    check('1 Farvardin 1405 = 21 Mar 2026', cc.farvardin1(1405) == dt.date(2026, 3, 21), str(cc.farvardin1(1405)))
    check('1 Farvardin 1406 = 21 Mar 2027', cc.farvardin1(1406) == dt.date(2027, 3, 21), str(cc.farvardin1(1406)))
    check('1403 is a leap year (30 Esfand = 20 Mar 2025)', cc.g2j(dt.date(2025, 3, 20)) == (1403, 12, 30))
    rt = all(cc.j2g(*cc.g2j(dt.date(2024, 1, 1) + dt.timedelta(days=k))) == dt.date(2024, 1, 1) + dt.timedelta(days=k)
             for k in range(1500))
    check('Jalali ↔ Gregorian round trip, 1500 days', rt)
    check('20 Shahrivar 1405 is a Friday (police notice)', cc.iran_weekday(cc.j2g(1405, 6, 20)) == 6, str(cc.j2g(1405, 6, 20)))
    check('the episode airs 21 Esfand 1405 = 12 Mar 2027', cc.j2g(1405, 12, 21) == dt.date(2027, 3, 12))
    hol = cc.load_holidays()
    f = cc.day_features(cc.j2g(1405, 1, 1), hol)
    check('Farvardin 1: off, Nowruz day 0', f['off'] == 1 and f['nz'] == 0, json.dumps(f))
    f13 = cc.day_features(cc.j2g(1405, 1, 13), hol)
    check('13 Farvardin is a holiday', f13['off'] == 1 and cc.day_key(f13) == 'nz+12', cc.day_key(f13))
    check('holidays.csv rows are not solar duplicates', all(n != 'Nowruz' for d, n in hol.items() if d.month in (5, 6, 7)))

    print('ingest (assumed 141 format)')
    head, rows = fake_141_rows()
    counters = {cp.norm('111111'): 'N', cp.norm('222222'): 'S'}
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / 'export.csv'
        buf = io.StringIO()
        csv.writer(buf).writerows([head] + rows)
        arabic = str.maketrans({'ی': 'ي', 'ک': 'ك', **{c: str(i) for i, c in enumerate('۰۱۲۳۴۵۶۷۸۹')}})
        p.write_bytes(buf.getvalue().translate(arabic).encode('cp1256'))      # how an old Windows export would store it
        out, rep = cp.convert([str(p)], counters=counters, closures=set())
        n13 = next(r for r in out if r['dir'] == 'N' and r['hour'] == 13)
        check('cp1256 CSV, Arabic ي/ك headers recognised', 'total' in rep[0] and 'speed' in rep[0], rep[0][:90])
        check('15-min rows summed to the hour', n13['count'] == 100 + 110 + 120 + 130, str(n13['count']))
        want = round(sum((100 + 10 * q) * (60 - 10 * q) for q in range(4)) / 460, 1)
        check('speed weighted by count', n13['speed'] == want, f'{n13["speed"]} vs {want}')
        check('Jalali date (1405/01/13) → 2 Apr 2026', n13['date'] == dt.date(2026, 4, 2), str(n13['date']))
        check('operating minutes and estimated vehicles kept', n13['minutes'] == 60 and n13['estimated'] == 2)
        check('heavy share from classes 3–5', abs(n13['heavy_share'] - 20 / 460) < 1e-3, str(n13['heavy_share']))
        x = Path(tmp) / 'export.xlsx'
        write_xlsx(x, head, rows)
        out2, _ = cp.convert([str(x)], counters=counters, closures=set())
        check('same table from .xlsx (UTF-8, Persian digits)', [(r['date'], r['hour'], r['dir'], r['count']) for r in out2] ==
              [(r['date'], r['hour'], r['dir'], r['count']) for r in out])
        g = Path(tmp) / 'generic.csv'
        g.write_text('Date,Hour,Vehicles,Avg Speed\n2026-04-02,13,500,41\n', encoding='utf-8')
        out3, _ = cp.convert([str(g) + '=S'], override={'total': 'Vehicles'}, counters={}, closures=set())
        check('date + hour columns, file=S, --map override', out3 and out3[0]['count'] == 500 and out3[0]['dir'] == 'S'
              and out3[0]['speed'] == 41.0)
        bad = [cp.parse_time(x) for x in ('1404/12/30 10:00', '1405/13/01', '2026-02-30 10:00', 'سه‌شنبه')]
        check('impossible dates are skipped, not wrapped or fatal', bad == [None] * 4 and cp.parse_time('1403/12/30') is not None)
        check('12-hour, day-first, hour-24 and Excel-serial+hour times', cp.parse_time('۱۴۰۵/۰۱/۱۳ ۰۱:۰۰ ب.ظ').hour == 13
              and cp.parse_time('21/03/2025 13:00').hour == 13 and cp.parse_time('1405/01/13', '24') == dt.datetime(2026, 4, 3)
              and cp.parse_time('45737', '14').hour == 14 and cp.num('NaN') is None)
        out4, rep4 = cp.convert([str(p), str(p)], counters=counters, closures=set())
        check('overlapping downloads are counted once', [r['count'] for r in out4] == [r['count'] for r in out]
              and any('duplicate' in x for x in rep4))
        try:
            cp.convert([str(p)], counters={cp.norm('111111'): 'N', cp.norm('222222'): 'N'}, closures=set())
            refused2 = False
        except SystemExit:
            refused2 = True
        out5, _ = cp.convert([str(p)], counters={cp.norm('111111'): 'N', cp.norm('222222'): 'N'}, closures=set(), only=['111111'])
        check('two counters in one direction: refused unless --only', refused2 and out5 and out5[0]['count'] == n13['count'])
        fxp = Path(tmp) / 'fix.csv'
        fx.write(fx.simulate(3, hol), fxp)
        try:
            cp.read_table(fxp)
            refused = False
        except SystemExit:
            refused = True
        check('prep refuses the SYNTHETIC fixture as 141 input', refused)
        shut = cp.load_closures(HERE / 'closures.csv')
        check('police closures.csv: 20 Shahrivar 1405, N closed 15–24', (dt.date(2026, 9, 11), 15, 'N') in shut
              and (dt.date(2026, 9, 11), 14, 'N') not in shut)

        print('fixture, closures, model')
        fxp = Path(tmp) / 'fix.csv'
        fx.write(fx.simulate(460, hol), fxp)
        rows, synthetic, _ = cc.read_hourly(fxp)
        check('fixture is marked SYNTHETIC', synthetic)
        truth = {(r['date'], r['hour'], r['dir']) for r in rows if r['closed']}
        for r in rows:
            r['closed'] = 0
        cc.detect_closures(rows)
        found = {(r['date'], r['hour'], r['dir']) for r in rows if r['closed']}
        hit = len(truth & found)
        check('closure heuristic: precision ≥ 0.8, recall ≥ 0.4', truth and found and hit / len(found) >= 0.8 and hit / len(truth) >= 0.4,
              f'{hit}/{len(found)} flagged are true, {hit}/{len(truth)} true found')
        rows, _, _ = cc.read_hourly(fxp)
        ce.annotate(rows, hol)
        sm = [r for r in rows if r['date'] < dt.date(2025, 9, 1)]
        if cc.np is not None:
            a = cc.Boosted(rounds=8).fit(sm, sm)
            npm, cc.np = cc.np, None
            b = cc.Boosted(rounds=8).fit(sm, sm)
            cc.np = npm
            d0 = dt.date(2025, 8, 1)
            pa = [a.predict(d0, h, 'N', cc.day_features(d0, hol))[0] for h in range(24)]
            pb = [b.predict(d0, h, 'N', cc.day_features(d0, hol))[0] for h in range(24)]
            check('boosted trees: numpy and pure Python agree', max(abs(u - v) for u, v in zip(pa, pb)) < 1e-6)
        else:
            print('  skip  numpy not installed: pure-Python trees only')
        rep = ce.evaluate(rows, hol, boosted_kw=dict(rounds=40))
        check('two folds: Nowruz 1405 and the last 182 days', [f['fold'] for f in rep] == ['nowruz_1405', 'last_6_months'],
              str([f['fold'] for f in rep]))
        nf = rep[0]
        check('no leakage: training ends before the test window', nf['n_train_days'] == (dt.date.fromisoformat(nf['start']) - rows[0]['date']).days)
        start = dt.date.fromisoformat(nf['start'])
        tr = [r for r in rows if r['date'] < start]
        lw, m4 = cc.LastWeek().fit(tr, rows, origin=start), cc.Median4().fit(tr, rows, origin=start)
        d14 = start + dt.timedelta(days=14)
        seen = {r['date'] for r in tr}
        check('baselines see only days before the test window', max(lw.by) < (start, 0, '') and max(m4.by) < (start, 0, '')
              and d14 - dt.timedelta(days=7 * cc._weeks_back(d14, start)) in seen
              and cc._weeks_back(d14, start) == 3 and cc._weeks_back(start, start) == 1)
        check('every model scored on the same hours', all(v['mae_count'] is not None for v in nf['models'].values()), str(nf['n_scored_hours']))
        check('closed hours are never scored', all(not any(c and a is not None for c, a in zip(s['closed'], s['actual']))
                                                   for s in nf['series']['N'].values()))
        prof = cc.Profile().fit(rows, rows)
        hrs = ce.day_forecast(cc.Boosted(rounds=40).fit(rows, rows), prof, cc.j2g(1405, 1, 13), 'S', hol)
        best = ce.best_windows(hrs)
        check('departure windows avoid likely closures', all(hrs[h]['p_closed'] <= 0.2 for h in best), str(best))

    print('page')
    out = HERE / 'chalus_live.html'
    if out.exists():
        html = out.read_text(encoding='utf-8')
        check('built page carries the MOCK watermark and synthetic flag', 'SYNTHETIC · MOCK DATA' in html and '"synthetic":true' in html)
    src = ''.join((HERE / f).read_text(encoding='utf-8') for f in ('chalus_core.py', 'chalus_prep.py', 'chalus_live.py', 'chalus_fixture.py'))
    check('no network or model API in the artifact code', 'urllib' not in src and 'http.client' not in src and 'import llm' not in src and 'from llm' not in src)
    print('selftest ok' if OK[0] else 'selftest FAILED')
    return 0 if OK[0] else 1


if __name__ == '__main__':
    sys.exit(main())
