"""chalus_eval.py · HMD-S07 · honest folds, scores and the departure-window forecast (split from chalus_core.py)."""
import datetime as dt
from collections import defaultdict

from chalus_core import DIRS, MODELS, Boosted, day_features, day_key, g2j, j2g, jstr, state, usable


# ── evaluation ────────────────────────────────────────────────────────────────────────────────────────────────
def annotate(rows, holidays):
    cache = {}
    for r in rows:
        if r['date'] not in cache:
            cal = day_features(r['date'], holidays)
            cache[r['date']] = (cal, day_key(cal))
        r['_cal'], r['_key'] = cache[r['date']]
    return rows


def folds(rows, holidays):
    """Two honest folds; every model, the two naive baselines included, sees only data BEFORE its test window.
    F1 · Nowruz: 25 Esfand – 15 Farvardin of the last Nowruz inside the data.  F2 · the last 182 days."""
    days = sorted({r['date'] for r in rows})
    first, last = days[0], days[-1]
    out = []
    for jy in range(g2j(last)[0], g2j(first)[0], -1):
        a, b = j2g(jy - 1, 12, 25), j2g(jy, 1, 15)
        if a > first + dt.timedelta(days=200) and b <= last:
            out.append(dict(name='nowruz_%d' % jy, label='Nowruz %d (held out)' % jy, start=a, end=b))
            break
    cut = last - dt.timedelta(days=181)
    if cut > first + dt.timedelta(days=200):
        out.append(dict(name='last_6_months', label='last 182 days (held out)', start=cut, end=last))
    return out


def evaluate(rows, holidays, models=MODELS, boosted_kw=None):
    """Per fold and model: MAE of count and speed, skill vs last-week, heavy-hour (state C) recall, balanced accuracy
    over states A/B/C, and for the Nowruz fold the error in the hour of each day's peak. Closed hours are excluded."""
    annotate(rows, holidays)
    report = []
    for fold in folds(rows, holidays):
        train = [r for r in rows if r['date'] < fold['start']]
        test = [r for r in rows if fold['start'] <= r['date'] <= fold['end'] and usable(r)]
        res = dict(fold=fold['name'], label=fold['label'], start=str(fold['start']), end=str(fold['end']),
                   n_train_days=len({r['date'] for r in train}), n_test_hours=len(test), models={})
        preds = {}
        for M in models:
            m = (M(**(boosted_kw or {})) if M is Boosted else M()).fit(train, rows, origin=fold['start'])
            preds[m.name] = {(r['date'], r['hour'], r['dir']): m.predict(r['date'], r['hour'], r['dir'], r['_cal'])
                             for r in test}
        common = [r for r in test if all(preds[n][r['date'], r['hour'], r['dir']][0] is not None for n in preds)]
        res['n_scored_hours'] = len(common)
        for name, p in preds.items():
            ec = [abs(p[r['date'], r['hour'], r['dir']][0] - r['count']) for r in common]
            es = [abs(p[r['date'], r['hour'], r['dir']][1] - r['speed']) for r in common
                  if r['speed'] is not None and p[r['date'], r['hour'], r['dir']][1] is not None]
            conf = defaultdict(int)
            for r in common:
                ps = p[r['date'], r['hour'], r['dir']][1]
                if r['speed'] is not None and ps is not None:
                    conf[state(r['speed']), state(ps)] += 1
            recall = {s: (conf[s, s] / sum(conf[s, t] for t in 'ABC')) if sum(conf[s, t] for t in 'ABC') else None
                      for s in 'ABC'}
            got = [v for v in recall.values() if v is not None]
            res['models'][name] = dict(mae_count=round(sum(ec) / len(ec), 1) if ec else None,
                                       mae_speed=round(sum(es) / len(es), 1) if es else None,
                                       recall_C=round(recall['C'], 3) if recall['C'] is not None else None,
                                       n_C=sum(conf['C', t] for t in 'ABC'),
                                       balanced_acc=round(sum(got) / len(got), 3) if got else None)
        ref = res['models']['last_week']['mae_count']
        for v in res['models'].values():
            v['skill_vs_last_week'] = round(1 - v['mae_count'] / ref, 3) if ref and v['mae_count'] is not None else None
        if fold['name'].startswith('nowruz'):
            res['peak_hour_error'] = peak_errors(common, preds)
            res['series'] = series(rows, fold, preds)
        report.append(res)
    return report


def series(rows, fold, preds):
    """Hour-by-hour actual vs each model in a fold, for the page: {dir: {date: {actual, closed, <model>: [24]}}}."""
    out = {x: {} for x in DIRS}
    for r in rows:
        if fold['start'] <= r['date'] <= fold['end']:
            day = out[r['dir']].setdefault(str(r['date']), dict(jalali=jstr(r['date']), actual=[None] * 24, closed=[0] * 24,
                                                                    **{n: [None] * 24 for n in preds}))
            day['actual'][r['hour']] = r['count'] if usable(r) else None
            day['closed'][r['hour']] = 1 if r['closed'] else 0
            for n, p in preds.items():
                v = p.get((r['date'], r['hour'], r['dir']))
                day[n][r['hour']] = None if v is None or v[0] is None else round(v[0])
    return out


def peak_errors(test, preds, top=4):
    """For the `top` busiest test days per direction: |predicted peak hour − actual peak hour|, per model."""
    out = {}
    for dirn in DIRS:
        by_day = defaultdict(dict)
        for r in test:
            if r['dir'] == dirn:
                by_day[r['date']][r['hour']] = r
        busiest = sorted(by_day, key=lambda d: -sum(x['count'] for x in by_day[d].values()))[:top]
        for name, p in preds.items():
            errs = []
            for d in busiest:
                hrs = by_day[d]
                act = max(hrs, key=lambda h: hrs[h]['count'])
                prd = max(hrs, key=lambda h: p[d, h, dirn][0])
                errs.append(abs(act - prd))
            out.setdefault(name, {})[dirn] = dict(days=[str(d) for d in busiest], errors=errs,
                                                 within_2h=sum(e <= 2 for e in errs))
    return out


# ── departure window ──────────────────────────────────────────────────────────────────────────────────────────
def day_forecast(model, profile, d, dirn, holidays):
    """24 hourly forecasts for one future date and direction: count, speed, state, P(closed)."""
    cal = day_features(d, holidays)
    out = []
    for h in range(24):
        c, s = model.predict(d, h, dirn, cal)
        out.append(dict(hour=h, count=None if c is None else round(c), speed=None if s is None else round(s, 1),
                        state=state(s), p_closed=round(profile.p_closed(d, h, dirn, cal), 2)))
    return out


def best_windows(hours, n=3, max_p_closed=0.2):
    """Rank departure hours (the hour you pass the counter): open, then fastest predicted speed, then fewest cars."""
    ok = [x for x in hours if x['speed'] is not None and x['p_closed'] <= max_p_closed and 5 <= x['hour'] <= 22]
    return [x['hour'] for x in sorted(ok, key=lambda x: (-x['speed'], x['count'] or 0))[:n]]


