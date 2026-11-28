"""wind_eval.py · HMD-S11 · "tomorrow's forecast" against what the airport measured, for a past month.

    python3 -I artifact/wind_eval.py --start 2025-04-01 --days 30      # about 10–20 min, writes derived/eval-<start>.json

For each day D: the 00Z run of day D-1 (ECMWF IFS and AIFS Single, 0.25°, open data from the Google Cloud mirror),
steps 30 and 36 h -> valid 06Z and 12Z of day D (09:30 and 15:30 Tehran). Compared with METAR at Tehran
Mehrabad (OIII) from the Iowa Environmental Mesonet archive:
  wind   model 10 m wind (from u, v)          vs the METAR mean wind at the valid time
  gust   IFS 10fg (max gust in the last 1 h at steps 30/36: GRIB2 template 4.8, checked 28 Nov 2026)
                                              vs the highest METAR gust in the 3 h before (mean wind when no gust group)
The airport is not the takeoff: this measures how well the model does at a flat, open, instrumented place.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wind_core as wc  # noqa: E402

STEPS = (30, 36)
SITE_KEYS = ['oiii', 'shahran']
PTS = [(wc.SITES[s]['lat'], wc.SITES[s]['lon']) for s in SITE_KEYS]


def parse(s):
    return dt.datetime.strptime(s, '%Y-%m-%dT%H:%MZ').replace(tzinfo=dt.timezone.utc)


def obs_at(obs, valid, window_h=3):
    """METAR mean wind at the valid time (within 20 min) and the peak gust/wind in the window before it."""
    v = parse(valid)
    near = [o for o in obs if abs((parse(o['valid']) - v).total_seconds()) <= 1200 and o['wind'] is not None]
    win = [o for o in obs if dt.timedelta(0) <= v - parse(o['valid']) < dt.timedelta(hours=window_h)]
    peaks = [o['gust'] if o['gust'] is not None else o['wind'] for o in win if (o['gust'] or o['wind']) is not None]
    best = min(near, key=lambda o: abs((parse(o['valid']) - v).total_seconds())) if near else None
    return dict(wind=None if best is None else round(best['wind'], 1), dir=None if best is None else best['dir'],
                peak=round(max(peaks), 1) if peaks else None, n_window=len(win),
                gust_groups=sum(1 for o in win if o['gust'] is not None))


def evaluate(start, days, log=print):
    import wind_fetch as wf
    t0 = dt.datetime.combine(start, dt.time(0), dt.timezone.utc)
    obs = wf.iem_metar('OIII', t0 - dt.timedelta(days=1), t0 + dt.timedelta(days=days + 1))
    log(f'  METAR OIII: {len(obs)} reports')
    rows = []
    for k in range(days):
        run = t0 + dt.timedelta(days=k - 1)
        day = dict(run=run.strftime('%Y-%m-%d %HZ'))
        for model, sfc in (('ifs', ('10u', '10v', '10fg', '2t', '2d')), ('aifs', ('10u', '10v', '2t', '2d'))):
            try:
                vals = wf.ecmwf_points(model, run, STEPS, PTS, sfc=sfc, levels=(), archive=True)
                day[model], _ = wf.ecmwf_rows(vals, run, SITE_KEYS)
            except Exception as e:                       # a missing run is recorded, not hidden
                day[model] = None
                log(f'  {run:%Y-%m-%d} {model}: FAILED {e}')
        rows.append(day)
        log(f'  {run:%Y-%m-%d} 00Z done')
    return summarise(rows, obs, start, days)


def summarise(rows, obs, start, days):
    pairs = []
    for day in rows:
        for i, step in enumerate(STEPS):
            ref = day.get('ifs') or day.get('aifs')
            if not ref:
                continue
            valid = ref[i]['valid']
            o = obs_at(obs, valid)
            rec = dict(valid=valid, obs=o)
            for model in ('ifs', 'aifs'):
                r = day.get(model)
                if not r:
                    continue
                a = r[i]['oiii']
                w = None if a['u10'] is None else round(wc.speed_kmh(a['u10'], a['v10']), 1)
                d = None if a['u10'] is None else round(wc.direction_from(a['u10'], a['v10']))
                rec[model] = dict(wind=w, dir=d, gust=None if a['gust'] is None else round(a['gust'], 1),
                                  shahran_wind=None if r[i]['shahran']['u10'] is None else
                                  round(wc.speed_kmh(r[i]['shahran']['u10'], r[i]['shahran']['v10']), 1))
            pairs.append(rec)
    out = dict(made=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ'), start=str(start), days=days,
               station='OIII', steps=STEPS, pairs=pairs)
    out['stats'] = stats(pairs)
    return out


def stats(pairs):
    res = {}
    for hour in ('06', '12', 'all'):
        sel = [p for p in pairs if hour == 'all' or p['valid'][11:13] == hour]
        st = {}
        for model in ('ifs', 'aifs'):
            wpairs = [(p[model]['wind'], p['obs']['wind']) for p in sel if model in p]
            st[model] = dict(wind=wc.errors(wpairs))
            daily = [None if f is None or o is None else f - o for f, o in wpairs]
            r1 = wc.lag1_autocorr(daily)
            st[model]['wind']['lag1'] = r1
            st[model]['wind']['n_eff'] = wc.effective_n(st[model]['wind']['n'], r1)
            dirs = [wc.angle_diff(p[model]['dir'], p['obs']['dir']) for p in sel if model in p
                    and p['obs']['wind'] and p['obs']['wind'] >= 9.3 and p['obs']['dir'] is not None and p[model]['dir'] is not None]
            st[model]['dir'] = dict(n=len(dirs), median=sorted(dirs)[len(dirs) // 2] if dirs else None,
                                    over_45=sum(1 for x in dirs if x > 45))
            if model == 'ifs':
                st[model]['gust'] = wc.errors([(p[model]['gust'], p['obs']['peak']) for p in sel if model in p])
        obs_w = [p['obs']['wind'] for p in sel if p['obs']['wind'] is not None]
        obs_p = [p['obs']['peak'] for p in sel if p['obs']['peak'] is not None]
        line = wc.THRESHOLDS['wind']['amber']
        st['over_novice_line'] = dict(line=line, obs=sum(1 for p in sel if (p['obs']['wind'] or 0) >= line),
                                      **{m: sum(1 for p in sel if m in p and (p[m]['wind'] or 0) >= line) for m in ('ifs', 'aifs')})
        st['ifs_gust_above_obs_peak'] = sum(1 for p in sel if 'ifs' in p and p['ifs']['gust'] is not None
                                            and p['obs']['peak'] is not None and p['ifs']['gust'] > p['obs']['peak'])
        st['obs'] = dict(n=len(obs_w), mean_wind=round(sum(obs_w) / len(obs_w), 1) if obs_w else None,
                         max_peak=max(obs_p) if obs_p else None,
                         gust_reports=sum(p['obs']['gust_groups'] for p in sel))
        wi = [(p['ifs']['wind'], p['obs']['wind']) for p in sel if 'ifs' in p and 'aifs' in p]
        wa = [(p['aifs']['wind'], p['obs']['wind']) for p in sel if 'ifs' in p and 'aifs' in p]
        # the effective n of the paired difference comes from the difference series itself
        dd = [abs(fa - o) - abs(fb - o2) for (fa, o), (fb, o2) in zip(wi, wa) if None not in (fa, o, fb, o2)]
        r_d = wc.lag1_autocorr(dd)
        st['ifs_minus_aifs_abs_error'] = wc.paired_abs_diff(wi, wa, wc.effective_n(len(dd), r_d))
        if st['ifs_minus_aifs_abs_error']:
            st['ifs_minus_aifs_abs_error'].update(lag1=r_d, n_eff=wc.effective_n(len(dd), r_d))
        res[hour] = st
    return res


def case(day, log=print):
    """One afternoon in detail: the run of the day before and the run of the same morning, against METAR."""
    import wind_fetch as wf
    t = dt.datetime.combine(day, dt.time(0), dt.timezone.utc)
    obs = wf.iem_metar('OIII', t, t + dt.timedelta(days=1))
    out = dict(day=str(day), station='OIII', metar=[o for o in obs if '06:00' <= o['valid'][11:16] <= '15:00'], runs={})
    for label, run, steps in (('day_before', t - dt.timedelta(days=1), (30, 33, 36, 39)), ('same_morning', t, (6, 9, 12, 15))):
        r = {}
        v = wf.ecmwf_points('ifs', run, steps, PTS[:1], sfc=('10u', '10v', '10fg', 'mucape'), levels=(), archive=True)
        for s in steps:
            g = lambda k: v[(s, k, None)][0]  # noqa: E731
            r[(run + dt.timedelta(hours=s)).strftime('%H:%MZ')] = dict(
                ifs_wind=round(wc.speed_kmh(g('u10'), g('v10')), 1), ifs_gust=round(wc.ms_to_kmh(g('gust')), 1),
                ifs_cape=round(g('cape')))
        a = wf.ecmwf_points('aifs', run, [s for s in steps if s % 6 == 0], PTS[:1], sfc=('10u', '10v'), levels=(), archive=True)
        for (s, k, _), val in a.items():
            if k == 'u10':
                r[(run + dt.timedelta(hours=s)).strftime('%H:%MZ')]['aifs_wind'] = round(
                    wc.speed_kmh(val[0], a[(s, 'v10', None)][0]), 1)
        out['runs'][label] = dict(run=run.strftime('%Y-%m-%d %HZ'), steps=r)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--start', default='2025-04-01')
    ap.add_argument('--days', type=int, default=30)
    ap.add_argument('--restat', action='store_true', help='recompute the statistics of an existing file, no network')
    ap.add_argument('--case', help='one day in detail, e.g. 2025-04-17 -> derived/case-<day>.json')
    a = ap.parse_args()
    start = dt.date.fromisoformat(a.start)
    path = HERE / 'derived' / f'eval-{start:%Y-%m}.json'
    if a.case:
        c = case(dt.date.fromisoformat(a.case))
        cp = HERE / 'derived' / f'case-{a.case}.json'
        cp.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding='utf-8')
        print('wrote', cp.relative_to(HERE.parent), json.dumps(c['runs'], ensure_ascii=False))
        sys.exit(0)
    if a.restat:
        res = json.loads(path.read_text(encoding='utf-8'))
        res['stats'] = stats(res['pairs'])
    else:
        res = evaluate(start, a.days)
    path.write_text(json.dumps(res, ensure_ascii=False, indent=0), encoding='utf-8')
    print('wrote', path.relative_to(HERE.parent))
    for h, st in res['stats'].items():
        print(h, json.dumps(st, ensure_ascii=False))
