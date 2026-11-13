#!/usr/bin/env python3
"""HMD-011 · storm_replay.py · replay real space-weather forecasts against what happened.

Question: can the next geomagnetic storm be forecast, and is an earlier warning or a surer one worth more?

Event      A UT day whose largest 3-hour planetary Kp is >= 5- (4.667), i.e. NOAA scale G1 or stronger.
Truth      GFZ Potsdam definitive Kp (CC BY 4.0).
Forecasts  For each target day D, using only what existed when the forecast was issued:
             noaa_d1/d2/d3  NOAA SWPC daily report (RSGA, issued ~22:00 UT), middle-latitude probability of
                            "minor storm" + "major-severe storm", issued 1, 2 or 3 days ahead.
             climatology    one constant: the storm-day rate in the training years.
             persistence    "tomorrow looks like today": storm-day rate in training years, conditioned on whether
                            the day of issue (up to 21:00 UT, the same cutoff as the RSGA) already had Kp >= 5-.
             recurrence     "the Sun turns every ~27 days": conditioned on day D-27. Known 27 days ahead.
             always_warn    probability 1 every day (the warning that is never missed).
Split      Fit (base rates only): 1996-01-01 .. 2017-12-31.  Test: 2018-01-01 .. 2025-12-31. Nothing from the test
           years is used to build a forecast.
Scores     Brier score and skill vs climatology; reliability table; hits / misses / false alarms at a warning
           threshold; warning lead time per storm episode; cost-loss value for three ILLUSTRATIVE users;
           a block bootstrap of the Brier skill (the uncertainty question of the next episode).

Standard library only. Python 3.9+.

  python3 storm_replay.py              run the experiment from derived/ and write results/
  python3 storm_replay.py --fetch      download raw files into data/ (git-ignored) and rebuild derived/
  python3 storm_replay.py --selftest   fast offline checks (used by `make selftest`)
"""
import argparse
import csv
import datetime as dt
import io
import json
import random
import re
import sys
import tarfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / 'data'          # raw downloads; parts/*/*/artifact/data/ is git-ignored
DERIVED = HERE / 'derived'   # small committed CSVs built from the raw files
RESULTS = HERE / 'results'

KP_URL = 'https://kp.gfz.de/app/files/Kp_ap_Ap_SN_F107_since_1932.txt'
SWPC_WAREHOUSE = 'ftp://ftp.swpc.noaa.gov/pub/warehouse/{y}/{y}_{kind}'
TEST_YEARS = range(2018, 2026)
FIT_START, FIT_END = dt.date(1996, 1, 1), dt.date(2017, 12, 31)
TEST_START, TEST_END = dt.date(2018, 1, 1), dt.date(2025, 12, 31)
G1 = 4.667          # Kp 5-: NOAA counts it as G1 ("4.67 (G1 Minor)" in SWPC 3-day forecasts)
G4 = 7.667          # Kp 8-: NOAA G4 starts at Kp 8, "including a 9-"; 8- rounds to 8
THRESHOLD = 0.30    # default warning threshold for the counts table
SEED = 11
BOOT = 2000
BLOCK = 27          # days; one solar rotation, keeps storm clusters together in the bootstrap

# ILLUSTRATIVE cost-loss ratios. C = cost of acting on a warning, L = loss if a storm comes unwarned.
# They are teaching assumptions, not measured costs. needs_lead = days ahead the user must decide.
USERS = [
    {'id': 'photographer', 'name': 'aurora photographer', 'C_over_L': 0.25, 'needs_lead': 1,
     'why': 'a wasted night and fuel vs missing a rare sky; decides the evening before'},
    {'id': 'satellite', 'name': 'satellite operator', 'C_over_L': 0.10, 'needs_lead': 3,
     'why': 'postponing a manoeuvre or upload vs an anomaly; plans two to three days ahead'},
    {'id': 'grid', 'name': 'power-grid operator', 'C_over_L': 0.05, 'needs_lead': 2,
     'why': 'extra reserves and deferred maintenance vs equipment stress; plans a day or two ahead'},
]


# ---------------------------------------------------------------- parsing

def parse_kp_file(text):
    """GFZ Kp file -> {date: (kp_max_full_day, kp_max_until_21UT, definitive_flag)}."""
    out = {}
    for line in text.splitlines():
        if not line or line.startswith('#'):
            continue
        f = line.split()
        d = dt.date(int(f[0]), int(f[1]), int(f[2]))
        kp = [float(x) for x in f[7:15]]
        if min(kp) < 0:
            continue
        out[d] = (max(kp), max(kp[:7]), int(f[-1]))
    return out


MONTHS = {m: i for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
                                      'Nov', 'Dec'], 1)}


def parse_rsga(text):
    """One RSGA report -> dict with issue time, day-1 date and middle/high latitude probabilities (percent)."""
    m = re.search(r':Issued:\s+(\d{4}) (\w{3}) (\d{2}) (\d{2})(\d{2}) UTC', text)
    if not m:
        return None
    issued = dt.datetime(int(m[1]), MONTHS[m[2]], int(m[3]), int(m[4]), int(m[5]))
    v = re.search(r'VI\.\s+Geomagnetic Activity Probabilities\s+(\d{2}) (\w{3})-(\d{2}) (\w{3})(.*?)(?:\n\s*\n|\Z)',
                  text, re.S)
    if not v:
        return None
    day1 = dt.date(issued.year, MONTHS[v[2]], int(v[1]))
    if day1 < issued.date() - dt.timedelta(days=200):      # 31 Dec report for 01 Jan
        day1 = day1.replace(year=issued.year + 1)
    body = v[5]
    mid = body.split('B.')[0]
    high = body.split('B.')[1] if 'B.' in body else ''

    def three(block, label):
        r = re.search(label + r'\s+(\d+)/(\d+)/(\d+)', block)
        return [int(x) for x in r.groups()] if r else None

    rec = {'issued': issued, 'day1': day1}
    for zone, block in (('mid', mid), ('high', high)):
        for key, label in (('active', 'Active'), ('minor', 'Minor Storm'), ('major', 'Major-severe storm')):
            rec[f'{zone}_{key}'] = three(block, label)
    if not rec['mid_minor'] or not rec['mid_major']:
        return None
    return rec


def parse_dgd(text):
    """SWPC Daily Geomagnetic Data -> {date: Fredericksburg daily max K} (days with a missing K are skipped)."""
    out = {}
    for line in text.splitlines():
        if not re.match(r'\d{4} \d{2} \d{2}', line):
            continue
        d = dt.date(int(line[0:4]), int(line[5:7]), int(line[8:10]))
        ks = [int(line[17 + 2 * i:19 + 2 * i]) for i in range(8)]
        if min(ks) < 0:
            continue
        out[d] = max(ks)
    return out


# ---------------------------------------------------------------- fetch + derive

def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f'  get {url}')
    with urllib.request.urlopen(url, timeout=180) as r:
        dest.write_bytes(r.read())


def fetch():
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    kp_path = RAW / 'Kp_ap_Ap_SN_F107_since_1932.txt'
    download(KP_URL, kp_path)
    for y in TEST_YEARS:
        download(SWPC_WAREHOUSE.format(y=y, kind='RSGA.tar.gz'), RAW / f'{y}_RSGA.tar.gz')
        download(SWPC_WAREHOUSE.format(y=y, kind='DGD.txt'), RAW / f'{y}_DGD.txt')
    build_derived(stamp)


def build_derived(stamp):
    DERIVED.mkdir(exist_ok=True)
    kp = parse_kp_file((RAW / 'Kp_ap_Ap_SN_F107_since_1932.txt').read_text())
    with open(DERIVED / 'kp_daily_1996_2025.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['date', 'kp_max', 'kp_max_until_21ut', 'gfz_definitive_flag'])
        for d in sorted(kp):
            if FIT_START <= d <= TEST_END:
                w.writerow([d.isoformat(), f'{kp[d][0]:.3f}', f'{kp[d][1]:.3f}', kp[d][2]])

    reports, skipped = [], 0
    for y in TEST_YEARS:
        with tarfile.open(RAW / f'{y}_RSGA.tar.gz') as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                rec = parse_rsga(tar.extractfile(member).read().decode('latin-1'))
                if rec is None:
                    skipped += 1
                    continue
                reports.append(rec)
    with open(DERIVED / 'noaa_rsga_probabilities_2018_2025.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['issued_utc', 'day1', 'lead_days', 'target_day', 'mid_active', 'mid_minor', 'mid_major_severe',
                    'high_active', 'high_minor', 'high_major_severe'])
        for rec in sorted(reports, key=lambda r: r['issued']):
            for k in range(3):
                row = [rec['issued'].strftime('%Y-%m-%d %H:%M'), rec['day1'].isoformat(), k + 1,
                       (rec['day1'] + dt.timedelta(days=k)).isoformat()]
                for zone in ('mid', 'high'):
                    for key in ('active', 'minor', 'major'):
                        vals = rec[f'{zone}_{key}']
                        row.append(vals[k] if vals else '')
                w.writerow(row)

    fred = {}
    for y in TEST_YEARS:
        fred.update(parse_dgd((RAW / f'{y}_DGD.txt').read_text()))
    with open(DERIVED / 'fredericksburg_kmax_2018_2025.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['date', 'fredericksburg_k_max'])
        for d in sorted(fred):
            w.writerow([d.isoformat(), fred[d]])

    (DERIVED / 'FETCHED.txt').write_text(
        f'Downloaded {stamp} by storm_replay.py --fetch\n'
        f'{KP_URL}\n'
        + ''.join(f'{SWPC_WAREHOUSE.format(y=y, kind="RSGA.tar.gz")}\n{SWPC_WAREHOUSE.format(y=y, kind="DGD.txt")}\n'
                  for y in TEST_YEARS)
        + f'RSGA reports parsed: {len(reports)}; unparsed files skipped: {skipped}\n')
    print(f'  derived/ rebuilt: {len(reports)} RSGA reports ({skipped} skipped), {len(fred)} Fredericksburg days')


def load_derived():
    kp = {}
    with open(DERIVED / 'kp_daily_1996_2025.csv') as f:
        for r in csv.DictReader(f):
            kp[dt.date.fromisoformat(r['date'])] = (float(r['kp_max']), float(r['kp_max_until_21ut']))
    noaa = {}   # (target, lead) -> (issued, p_mid_storm)
    with open(DERIVED / 'noaa_rsga_probabilities_2018_2025.csv') as f:
        for r in csv.DictReader(f):
            issued = dt.datetime.fromisoformat(r['issued_utc'])
            target = dt.date.fromisoformat(r['target_day'])
            lead = int(r['lead_days'])
            # Only a report issued before the target day starts counts, and it must be the lead it claims:
            # day 1 = the next UT day after issue (a late report issued after 00 UT is dropped for that lead).
            if issued >= dt.datetime.combine(target, dt.time(0, 0)) - dt.timedelta(days=lead - 1):
                continue
            p = (int(r['mid_minor']) + int(r['mid_major_severe'])) / 100
            key = (target, lead)
            if key not in noaa or issued > noaa[key][0]:     # an amended report replaces the earlier one
                noaa[key] = (issued, min(p, 1.0))
    fred = {}
    with open(DERIVED / 'fredericksburg_kmax_2018_2025.csv') as f:
        for r in csv.DictReader(f):
            fred[dt.date.fromisoformat(r['date'])] = int(r['fredericksburg_k_max'])
    return kp, noaa, fred


# ---------------------------------------------------------------- scoring

def brier(pairs):
    return sum((p - o) ** 2 for p, o in pairs) / len(pairs)


def reliability(pairs, edges=(0, 0.10, 0.20, 0.30, 0.40, 0.60, 1.01)):
    rows = []
    for lo, hi in zip(edges, edges[1:]):
        sel = [(p, o) for p, o in pairs if lo <= p < hi]
        if sel:
            rows.append({'bin': f'{round(lo * 100)}-{min(100, round(hi * 100) - 1)}%', 'n': len(sel),
                         'mean_forecast': round(sum(p for p, _ in sel) / len(sel), 3),
                         'observed_rate': round(sum(o for _, o in sel) / len(sel), 3)})
    return rows


def counts(pairs, thr):
    hit = sum(1 for p, o in pairs if p >= thr and o)
    miss = sum(1 for p, o in pairs if p < thr and o)
    fa = sum(1 for p, o in pairs if p >= thr and not o)
    cn = len(pairs) - hit - miss - fa
    events = hit + miss
    return {'threshold': thr, 'days': len(pairs), 'storm_days': events, 'hits': hit, 'misses': miss,
            'false_alarms': fa, 'correct_quiet': cn,
            'hit_rate': round(hit / events, 3) if events else None,
            'false_alarm_ratio': round(fa / (hit + fa), 3) if hit + fa else None,
            'warning_days_per_year': round((hit + fa) / len(pairs) * 365.25, 1),
            'false_alarms_per_year': round(fa / len(pairs) * 365.25, 1),
            'missed_storm_days_per_year': round(miss / len(pairs) * 365.25, 1)}


def value(pairs, c_over_l):
    """Relative economic value in the static cost-loss model (L = 1). 1 = perfect, 0 = no better than the
    best fixed policy (always or never act), negative = worse than that."""
    n = len(pairs)
    s = sum(o for _, o in pairs) / n
    e_clim = min(c_over_l, s)
    e_perf = s * c_over_l
    e_fc = sum(c_over_l if p >= c_over_l else (1.0 if o else 0.0) for p, o in pairs) / n
    return round((e_clim - e_fc) / (e_clim - e_perf), 3) if e_clim > e_perf else None


def block_bootstrap_bss(days, f_pairs, ref_pairs, rng, n_boot=BOOT, block=BLOCK):
    """Moving-block bootstrap of the Brier skill score of f against ref over the same days."""
    n = len(days)
    stats = []
    for _ in range(n_boot):
        idx = []
        while len(idx) < n:
            start = rng.randrange(0, n - block + 1)
            idx.extend(range(start, start + block))
        idx = idx[:n]
        bf = sum((f_pairs[i][0] - f_pairs[i][1]) ** 2 for i in idx)
        br = sum((ref_pairs[i][0] - ref_pairs[i][1]) ** 2 for i in idx)
        stats.append(1 - bf / br if br else 0.0)
    stats.sort()
    return round(stats[int(0.025 * n_boot)], 3), round(stats[int(0.975 * n_boot) - 1], 3)


def episodes(days, obs):
    """Runs of consecutive storm days -> list of (first_day, last_day, max_kp_index_in_run)."""
    out, run = [], []
    for d in days:
        if obs[d]:
            run.append(d)
        elif run:
            out.append(run)
            run = []
    if run:
        out.append(run)
    return out


# ---------------------------------------------------------------- experiment

def fit_baselines(kp):
    fit_days = [d for d in sorted(kp) if FIT_START <= d <= FIT_END]
    storm = {d: kp[d][0] >= G1 for d in fit_days}
    base = sum(storm.values()) / len(storm)
    pers = {}
    for lead in (1, 2, 3):
        yes = [0, 0]
        no = [0, 0]
        for d in fit_days:
            issue_day = d - dt.timedelta(days=lead)
            if issue_day not in kp or issue_day < FIT_START:
                continue
            bucket = yes if kp[issue_day][1] >= G1 else no
            bucket[0] += storm[d]
            bucket[1] += 1
        pers[lead] = {'if_storm_today': yes[0] / yes[1], 'if_quiet_today': no[0] / no[1]}
    yes = [0, 0]
    no = [0, 0]
    for d in fit_days:
        back = d - dt.timedelta(days=27)
        if back < FIT_START:
            continue
        bucket = yes if storm[back] else no
        bucket[0] += storm[d]
        bucket[1] += 1
    rec = {'if_storm_27_days_ago': yes[0] / yes[1], 'if_quiet_27_days_ago': no[0] / no[1]}
    return {'fit_days': len(fit_days), 'base_rate': base, 'persistence': pers, 'recurrence': rec}


LAST_PAIRS = {}


def your_user(c_over_l, lead):
    """Value and warning counts for your own cost ratio and decision lead (uses the last run's forecasts)."""
    run(write=False, n_boot=0)
    out = [f'Your user: C/L = {c_over_l} (warn when p >= {c_over_l}), must decide {lead} day(s) ahead. '
           'Value: 1 = perfect, 0 = no better than always/never acting.', '',
           '| forecaster | value | hits | misses | false alarms | false alarms/yr |', '|---|---:|---:|---:|---:|---:|']
    for n in (f'noaa_d{lead}', f'persistence_d{lead}', 'recurrence_27d', 'climatology', 'always_warn'):
        c = counts(LAST_PAIRS[n], c_over_l)
        out.append(f"| {n} | {value(LAST_PAIRS[n], c_over_l)} | {c['hits']} | {c['misses']} | {c['false_alarms']} | "
                   f"{c['false_alarms_per_year']} |")
    return '\n'.join(out)


def run(write=True, n_boot=BOOT):
    kp, noaa, fred = load_derived()
    fit = fit_baselines(kp)
    days = [d for d in sorted(kp) if TEST_START <= d <= TEST_END
            and all((d, k) in noaa for k in (1, 2, 3))]
    obs = {d: kp[d][0] >= G1 for d in days}
    all_test = [d for d in sorted(kp) if TEST_START <= d <= TEST_END]

    def forecast(name, d):
        if name.startswith('noaa_d'):
            return noaa[(d, int(name[-1]))][1]
        if name == 'climatology':
            return fit['base_rate']
        if name.startswith('persistence_d'):
            lead = int(name[-1])
            today = d - dt.timedelta(days=lead)
            p = fit['persistence'][lead]
            return p['if_storm_today'] if kp[today][1] >= G1 else p['if_quiet_today']
        if name == 'recurrence_27d':
            back = d - dt.timedelta(days=27)
            r = fit['recurrence']
            return r['if_storm_27_days_ago'] if kp[back][0] >= G1 else r['if_quiet_27_days_ago']
        if name == 'always_warn':
            return 1.0
        raise KeyError(name)

    names = ['climatology', 'always_warn', 'recurrence_27d', 'persistence_d1', 'persistence_d2', 'persistence_d3',
             'noaa_d3', 'noaa_d2', 'noaa_d1']
    pairs = {n: [(forecast(n, d), int(obs[d])) for d in days] for n in names}
    LAST_PAIRS.clear()
    LAST_PAIRS.update(pairs)
    b_clim = brier(pairs['climatology'])
    table = []
    for n in names:
        b = brier(pairs[n])
        table.append({'forecaster': n, 'brier': round(b, 4), 'skill_vs_climatology': round(1 - b / b_clim, 3),
                      'mean_forecast': round(sum(p for p, _ in pairs[n]) / len(days), 3)})

    rng = random.Random(SEED)
    boot = {}
    for a, ref in (() if not n_boot else (('noaa_d1', 'climatology'), ('noaa_d1', 'persistence_d1'), ('noaa_d3', 'persistence_d3'),
                   ('noaa_d3', 'climatology'))):
        boot[f'{a}_vs_{ref}'] = {
            'skill': round(1 - brier(pairs[a]) / brier(pairs[ref]), 3),
            'ci95': block_bootstrap_bss(days, pairs[a], pairs[ref], rng, n_boot=n_boot)}

    eps = episodes(days, obs)
    ep_rows = []
    for run_days in eps:
        first = run_days[0]
        peak = max(kp[d][0] for d in run_days)
        ep_rows.append({'first_day': first.isoformat(), 'days': len(run_days), 'peak_kp': round(peak, 3),
                        'noaa_p_first_day': {f'd{k}': noaa[(first, k)][1] for k in (3, 2, 1)}})

    def lead_summary(thr):
        warned = {k: sum(1 for e in ep_rows if e['noaa_p_first_day'][f'd{k}'] >= thr) for k in (1, 2, 3)}
        return {'threshold': thr, 'episodes': len(ep_rows),
                'first_day_warned_at_lead': warned,
                'share': {k: round(v / len(ep_rows), 3) for k, v in warned.items()}}

    big = [e for e in ep_rows if e['peak_kp'] >= G4]

    users = []
    for u in USERS:
        lead = u['needs_lead']
        row = {**u, 'threshold': u['C_over_L'],
               'value_noaa_by_lead': {f'd{k}': value(pairs[f'noaa_d{k}'], u['C_over_L']) for k in (1, 2, 3)},
               'value': {n: value(pairs[n], u['C_over_L'])
                         for n in ('climatology', 'recurrence_27d', f'persistence_d{lead}', f'noaa_d{lead}',
                                   'noaa_d1', 'always_warn')},
               'counts_noaa_at_needed_lead': counts(pairs[f'noaa_d{lead}'], u['C_over_L']),
               'counts_noaa_d1': counts(pairs['noaa_d1'], u['C_over_L'])}
        users.append(row)

    # NOAA scored against its own target (Fredericksburg K >= 5), same days where that station has data
    own = [d for d in days if d in fred]
    own_pairs = {k: [(noaa[(d, k)][1], int(fred[d] >= 5)) for d in own] for k in (1, 2, 3)}
    own_base = sum(o for _, o in own_pairs[1]) / len(own)
    own_clim = brier([(own_base, o) for _, o in own_pairs[1]])
    own_check = {'days': len(own), 'event_rate': round(own_base, 3),
                 'note': 'climatology here = the test-period rate itself (an optimistic reference)',
                 'skill_vs_inperiod_climatology': {f'd{k}': round(1 - brier(own_pairs[k]) / own_clim, 3)
                                                   for k in (1, 2, 3)},
                 'reliability_d1': reliability(own_pairs[1])}

    may = {}
    for day in ('2024-05-10', '2024-05-11', '2024-05-12'):
        d = dt.date.fromisoformat(day)
        may[day] = {'kp_max_gfz': kp[d][0], 'noaa_p': {f'd{k}': noaa[(d, k)][1] for k in (3, 2, 1) if (d, k) in noaa}}

    res = {
        'experiment': 'HMD-011 storm_replay',
        'event': 'UT day with max planetary Kp >= 5- (4.667), NOAA G1 or stronger; truth = GFZ definitive Kp',
        'fit_period': f'{FIT_START} .. {FIT_END}', 'test_period': f'{TEST_START} .. {TEST_END}',
        'test_days_scored': len(days), 'test_days_total': len(all_test),
        'test_days_dropped_missing_noaa': len(all_test) - len(days),
        'storm_days': sum(obs.values()), 'storm_rate': round(sum(obs.values()) / len(days), 3),
        'fit': {'base_rate': round(fit['base_rate'], 3),
                'persistence': {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in fit['persistence'].items()},
                'recurrence': {k: round(v, 3) for k, v in fit['recurrence'].items()}},
        'scores': table,
        'reliability': {n: reliability(pairs[n]) for n in ('noaa_d1', 'noaa_d2', 'noaa_d3', 'persistence_d1')},
        'counts_at_threshold': {n: counts(pairs[n], THRESHOLD) for n in
                                ('noaa_d1', 'noaa_d2', 'noaa_d3', 'persistence_d1', 'recurrence_27d', 'always_warn')},
        'counts_noaa_d1_by_threshold': [counts(pairs['noaa_d1'], t) for t in (0.05, 0.10, 0.20, 0.30, 0.50)],
        'counts_noaa_d3_by_threshold': [counts(pairs['noaa_d3'], t) for t in (0.05, 0.10, 0.20, 0.30, 0.50)],
        'episodes': {'n': len(eps), 'lead_at_30pct': lead_summary(0.30), 'lead_at_10pct': lead_summary(0.10),
                     'big_storms_kp_ge_8minus': big},
        'bootstrap_brier_skill': {'block_days': BLOCK, 'resamples': n_boot, 'seed': SEED, **boot},
        'users_ILLUSTRATIVE_costs': users,
        'noaa_vs_own_target_fredericksburg_k5': own_check,
        'may_2024': may,
    }
    if write:
        RESULTS.mkdir(exist_ok=True)
        (RESULTS / 'results.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
        (RESULTS / 'results.md').write_text(report(res))
    return res


def pct(x):
    return f'{100 * x:.1f}%' if x is not None else '—'


def report(r):
    L = [f"# HMD-011 · storm_replay results\n",
         f"Event: {r['event']}.  ",
         f"Fit: {r['fit_period']} (base rates only).  Test: {r['test_period']}.\n",
         f"Scored test days: {r['test_days_scored']} of {r['test_days_total']} "
         f"(dropped {r['test_days_dropped_missing_noaa']} without all three NOAA leads). "
         f"Storm days: {r['storm_days']} ({pct(r['storm_rate'])}). Fit-period storm rate: {pct(r['fit']['base_rate'])}. "
         f"Storm episodes (runs of storm days): {r['episodes']['n']}.\n",
         '## Brier score (lower is better) and skill vs climatology\n',
         '| forecaster | Brier | skill | mean forecast |', '|---|---:|---:|---:|']
    for s in r['scores']:
        L.append(f"| {s['forecaster']} | {s['brier']:.4f} | {s['skill_vs_climatology']:+.3f} | {s['mean_forecast']:.3f} |")
    L += ['', '## Block bootstrap of Brier skill (95% interval)\n', '| comparison | skill | 95% interval |', '|---|---:|---|']
    for k, v in r['bootstrap_brier_skill'].items():
        if isinstance(v, dict):
            L.append(f"| {k} | {v['skill']:+.3f} | {v['ci95'][0]:+.3f} .. {v['ci95'][1]:+.3f} |")
    L += ['', '## Reliability: when the forecast said p, how often did it happen?\n']
    for n, rows in r['reliability'].items():
        L += [f'**{n}**\n', '| forecast bin | days | mean forecast | observed |', '|---|---:|---:|---:|']
        for x in rows:
            L.append(f"| {x['bin']} | {x['n']} | {pct(x['mean_forecast'])} | {pct(x['observed_rate'])} |")
        L.append('')
    L += [f"## Warnings at threshold {pct(THRESHOLD)}\n",
          '| forecaster | hits | misses | false alarms | hit rate | false-alarm ratio | warning days/yr | false alarms/yr |',
          '|---|---:|---:|---:|---:|---:|---:|---:|']
    for n, c in r['counts_at_threshold'].items():
        L.append(f"| {n} | {c['hits']} | {c['misses']} | {c['false_alarms']} | {pct(c['hit_rate'])} | "
                 f"{pct(c['false_alarm_ratio'])} | {c['warning_days_per_year']} | {c['false_alarms_per_year']} |")
    for key in ('counts_noaa_d1_by_threshold', 'counts_noaa_d3_by_threshold'):
        L += ['', f"### {key.replace('counts_', '').replace('_', ' ')}\n",
              '| threshold | hits | misses | false alarms | hit rate | false alarms/yr | missed storm days/yr |',
              '|---:|---:|---:|---:|---:|---:|---:|']
        for c in r[key]:
            L.append(f"| {pct(c['threshold'])} | {c['hits']} | {c['misses']} | {c['false_alarms']} | {pct(c['hit_rate'])} | "
                     f"{c['false_alarms_per_year']} | {c['missed_storm_days_per_year']} |")
    e = r['episodes']
    L += ['', '## Lead time: was the first day of each storm episode warned 1, 2, 3 days ahead?\n',
          '| NOAA threshold | episodes | warned 3 days ahead | 2 days ahead | 1 day ahead |', '|---:|---:|---:|---:|---:|']
    for k in ('lead_at_10pct', 'lead_at_30pct'):
        s = e[k]
        L.append(f"| {pct(s['threshold'])} | {s['episodes']} | {pct(s['share'][3])} | {pct(s['share'][2])} | {pct(s['share'][1])} |")
    L += ['', '### Episodes that reached Kp >= 8- (G4 or stronger)\n',
          '| first storm day | days | peak Kp | NOAA p, 3 days ahead | 2 days | 1 day |', '|---|---:|---:|---:|---:|---:|']
    for b in e['big_storms_kp_ge_8minus']:
        p = b['noaa_p_first_day']
        L.append(f"| {b['first_day']} | {b['days']} | {b['peak_kp']} | {pct(p['d3'])} | {pct(p['d2'])} | {pct(p['d1'])} |")
    L += ['', '## Three users (ILLUSTRATIVE cost-loss ratios)\n',
          'Relative economic value: 1 = perfect forecast, 0 = no better than the best fixed policy, below 0 = worse.\n',
          '| user | C/L = threshold | needs lead | value: NOAA at that lead | NOAA day 1 | persistence | recurrence | climatology | always warn |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for u in r['users_ILLUSTRATIVE_costs']:
        v = u['value']
        lead = u['needs_lead']
        L.append(f"| {u['name']} | {u['C_over_L']} | {lead} d | {v[f'noaa_d{lead}']} | {v['noaa_d1']} | "
                 f"{v[f'persistence_d{lead}']} | {v['recurrence_27d']} | {v['climatology']} | {v['always_warn']} |")
    L += ['', 'Value of the NOAA forecast if the same user could decide 1, 2 or 3 days ahead '
          '(a forecast issued later than the user can act on is worth nothing to that user):\n',
          '| user | C/L | NOAA 1 day ahead | 2 days | 3 days |', '|---|---:|---:|---:|---:|']
    for u in r['users_ILLUSTRATIVE_costs']:
        v = u['value_noaa_by_lead']
        L.append(f"| {u['name']} | {u['C_over_L']} | {v['d1']} | {v['d2']} | {v['d3']} |")
    L += ['', '| user | NOAA lead used | hits | misses | false alarms | warning days/yr | false alarms/yr |',
          '|---|---:|---:|---:|---:|---:|---:|']
    for u in r['users_ILLUSTRATIVE_costs']:
        c = u['counts_noaa_at_needed_lead']
        L.append(f"| {u['name']} | {u['needs_lead']} d | {c['hits']} | {c['misses']} | {c['false_alarms']} | "
                 f"{c['warning_days_per_year']} | {c['false_alarms_per_year']} |")
    o = r['noaa_vs_own_target_fredericksburg_k5']
    L += ['', '## Fairness check: NOAA against its own target (Fredericksburg K >= 5)\n',
          f"Days: {o['days']}; event rate {pct(o['event_rate'])}; skill vs in-period climatology: "
          + ', '.join(f"{k} {v:+.3f}" for k, v in o['skill_vs_inperiod_climatology'].items()) + '.\n',
          '| forecast bin | days | mean forecast | observed |', '|---|---:|---:|---:|']
    for x in o['reliability_d1']:
        L.append(f"| {x['bin']} | {x['n']} | {pct(x['mean_forecast'])} | {pct(x['observed_rate'])} |")
    L += ['', '## May 2024\n', '| day | GFZ max Kp | NOAA p 3 days ahead | 2 days | 1 day |', '|---|---:|---:|---:|---:|']
    for day, v in r['may_2024'].items():
        p = v['noaa_p']
        L.append(f"| {day} | {v['kp_max_gfz']} | {pct(p.get('d3'))} | {pct(p.get('d2'))} | {pct(p.get('d1'))} |")
    L.append('\nNOAA probability here = middle-latitude "minor storm" + "major-severe storm" from the RSGA report. '
             'This is an educational replay, not an official verification and not a warning service.\n')
    return '\n'.join(L)


# ---------------------------------------------------------------- selftest

SAMPLE_RSGA = """:Product: 0509RSGA.txt
:Issued: 2024 May 09 2200 UTC
VI.  Geomagnetic Activity Probabilities 10 May-12 May
A.  Middle Latitudes
Active                35/15/25
Minor Storm           30/35/40
Major-severe storm    10/50/25
B.  High Latitudes
Active                10/01/05
Minor Storm           25/10/15
Major-severe storm    65/90/79
"""
SAMPLE_DGD = "2024 05 10    80  3 3 2 1 3 5 7 9   146  2 3 5 4 4 8 9 9   118   3.00  3.00  2.67  2.33\n" \
             "2019 10 29     8  3 3 1 1 2 2-1 1    -1  2-1-1-1 0-1-1-1     8  3 3 1 1 1 2 2 1\n"
SAMPLE_KP = "2024 05 10 33733 33733.5 2601 20  2.667  2.667  2.333  2.000  3.667  7.667  8.667  8.667   12   12    9    " \
            "7   22  179  300  300   105 172    223.4    227.9 2\n"


def selftest():
    r = parse_rsga(SAMPLE_RSGA)
    assert r['day1'] == dt.date(2024, 5, 10) and r['mid_minor'] == [30, 35, 40] and r['mid_major'] == [10, 50, 25]
    assert r['high_major'] == [65, 90, 79]
    yearend = parse_rsga(SAMPLE_RSGA.replace('2024 May 09', '2024 Dec 31').replace('10 May-12 May', '01 Jan-03 Jan'))
    assert yearend['day1'] == dt.date(2025, 1, 1)
    g = parse_dgd(SAMPLE_DGD)
    assert g == {dt.date(2024, 5, 10): 9}, g          # the day with a missing K is skipped
    k = parse_kp_file(SAMPLE_KP)
    assert k[dt.date(2024, 5, 10)] == (8.667, 8.667, 2)
    assert abs(brier([(0.7, 1), (0.7, 0)]) - 0.29) < 1e-12
    assert brier([(1, 1), (0, 0)]) == 0
    rel = reliability([(0.7, 1)] * 7 + [(0.7, 0)] * 3)
    assert rel == [{'bin': '60-100%', 'n': 10, 'mean_forecast': 0.7, 'observed_rate': 0.7}]
    c = counts([(0.9, 1), (0.9, 0), (0.1, 1), (0.1, 0)], 0.5)
    assert (c['hits'], c['false_alarms'], c['misses'], c['correct_quiet']) == (1, 1, 1, 1)
    assert value([(1, 1), (0, 0), (0, 0), (0, 0)], 0.1) == 1.0          # perfect forecast
    assert value([(0.25, 1), (0.25, 0), (0.25, 0), (0.25, 0)], 0.1) == 0.0  # constant = best fixed policy
    eps = episodes([1, 2, 3, 4, 5], {1: 1, 2: 1, 3: 0, 4: 1, 5: 0})
    assert eps == [[1, 2], [4]]
    rng = random.Random(1)
    lo, hi = block_bootstrap_bss(list(range(60)), [(0.2, 0)] * 60, [(0.4, 0)] * 60, rng, n_boot=50, block=10)
    assert lo == hi == 0.75
    if (DERIVED / 'kp_daily_1996_2025.csv').exists() and (RESULTS / 'results.json').exists():
        fresh = run(write=False, n_boot=0)
        saved = json.loads((RESULTS / 'results.json').read_text())
        assert fresh['scores'] == saved['scores'], 'results/results.json is stale: run storm_replay.py again'
        assert fresh['storm_days'] == saved['storm_days']
    print('selftest ok')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--fetch', action='store_true', help='download raw data into data/ and rebuild derived/')
    ap.add_argument('--selftest', action='store_true', help='fast offline checks')
    ap.add_argument('--quiet', action='store_true', help='write results/ without printing the report')
    ap.add_argument('--cost', type=float, help='your cost-loss ratio C/L (0..1): price of a false alarm / loss from a miss')
    ap.add_argument('--lead', type=int, default=1, choices=(1, 2, 3), help='days ahead you must decide (with --cost)')
    a = ap.parse_args()
    if a.cost is not None:
        print(your_user(a.cost, a.lead))
        return
    if a.selftest:
        selftest()
        return
    if a.fetch:
        fetch()
    res = run()
    if not a.quiet:
        print(report(res))


if __name__ == '__main__':
    sys.exit(main())
