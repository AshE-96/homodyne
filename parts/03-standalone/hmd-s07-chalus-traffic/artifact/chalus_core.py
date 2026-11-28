"""chalus_core.py · HMD-S07 · calendar, baselines, a small boosted-tree model and honest evaluation. Standard library only.

Everything works on one hourly table (see chalus_prep.py for how the owner's 141 export becomes it):
    date (YYYY-MM-DD, Gregorian) · hour (0–23) · dir ('N' = Karaj→Chalus, south to north; 'S' = Chalus→Karaj)
    count (vehicles in that hour, or None) · speed (mean km/h, or None) · closed (1 if that direction was shut by police)

Forecast question: "at hour h on date d, in direction x, how many cars pass the counter and how fast?" — asked days or
weeks ahead, so no model here uses the last hours of traffic; only the calendar (and, for the naive baselines, the
same hour in the latest weeks before the forecast origin).
"""
import csv
import datetime as dt
import math
import random
from collections import defaultdict

try:
    import numpy as np                     # optional: the same trees, about 30x faster
except ImportError:                        # pragma: no cover
    np = None
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIRS = ('N', 'S')
DIR_LABEL = {'N': 'Karaj → Chalus (south to north)', 'S': 'Chalus → Karaj (north to south)'}
# Our own state thresholds on the counter's mean speed (km/h). NOT the thresholds of Rasaizadi et al. 2021,
# whose A–C states are defined in the paper itself ([VERIFY] there). Change them here; everything else follows.
SPEED_A, SPEED_C = 60.0, 30.0          # A (free) ≥ 60 · B (slow) 30–60 · C (heavy) < 30
WEEKDAY_FA = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
WEEKDAY_EN = ['Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri']


# ── Jalali calendar (arithmetic of the jalaali-js algorithm, Borkowski breaks) ─────────────────────────────────
_BREAKS = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178]


def _div(a, b):
    return int(a / b)


def _jal_cal(jy):
    """(leap, gregorian year, March day of 1 Farvardin) for Jalali year jy."""
    gy, leap_j, jp, jump = jy + 621, -14, _BREAKS[0], 0
    for jm in _BREAKS[1:]:
        jump = jm - jp
        if jy < jm:
            break
        leap_j += _div(jump, 33) * 8 + _div(jump % 33, 4)
        jp = jm
    n = jy - jp
    leap_j += _div(n, 33) * 8 + _div(n % 33 + 3, 4)
    if jump % 33 == 4 and jump - n == 4:
        leap_j += 1
    leap_g = _div(gy, 4) - _div((_div(gy, 100) + 1) * 3, 4) - 150
    march = 20 + leap_j - leap_g
    if jump - n < 6:
        n = n - jump + _div(jump + 4, 33) * 33
    leap = ((n + 1) % 33 - 1) % 4
    return (4 if leap == -1 else leap), gy, march


def farvardin1(jy):
    _, gy, march = _jal_cal(jy)
    return dt.date(gy, 3, march)


def is_leap(jy):
    """True if Esfand of Jalali year jy has 30 days."""
    return (farvardin1(jy + 1) - farvardin1(jy)).days == 366


def j2g(jy, jm, jd):
    off = (jm - 1) * 31 if jm <= 7 else 186 + (jm - 7) * 30
    return farvardin1(jy) + dt.timedelta(days=off + jd - 1)


def g2j(d):
    jy = d.year - 621
    f1 = farvardin1(jy)
    if d < f1:
        jy -= 1
        f1 = farvardin1(jy)
    k = (d - f1).days
    if k < 186:
        return jy, k // 31 + 1, k % 31 + 1
    k -= 186
    return jy, 7 + k // 30, k % 30 + 1


def jstr(d):
    return '%d/%02d/%02d' % g2j(d)


def iran_weekday(d):
    """0 = Saturday … 6 = Friday."""
    return (d.weekday() + 2) % 7


# ── holidays and day types ─────────────────────────────────────────────────────────────────────────────────────
SOLAR_HOLIDAYS = [((1, 1), 'Nowruz'), ((1, 2), 'Nowruz'), ((1, 3), 'Nowruz'), ((1, 4), 'Nowruz'),
                  ((1, 12), 'Islamic Republic Day'), ((1, 13), 'Nature Day (Sizdah-be-dar)'),
                  ((3, 14), 'Death of Khomeini'), ((3, 15), '15 Khordad uprising'),
                  ((11, 22), 'Revolution Day'), ((12, 29), 'Oil Nationalisation Day')]


def load_holidays(path=HERE / 'holidays.csv', years=(1403, 1404, 1405, 1406)):
    """{date: name}. Solar holidays are computed; lunar and one-off days come from holidays.csv (owner verifies)."""
    out = {}
    for jy in years:
        for (jm, jd), name in SOLAR_HOLIDAYS:
            out[j2g(jy, jm, jd)] = name
    for row in _special_rows(path):
        if row.get('type', '').strip() != 'anomaly':
            out[dt.date.fromisoformat(row['date'].strip())] = row.get('name', 'holiday').strip()
    return out


def _special_rows(path):
    if not Path(path).exists():
        return []
    return [r for r in csv.DictReader(line for line in open(path, encoding='utf-8') if not line.startswith('#'))
            if r.get('date', '').strip()]


def load_anomalies(path=HERE / 'holidays.csv'):
    """Dates of type 'anomaly' (emergencies, a road shut for days): excluded from training and from scoring."""
    return {dt.date.fromisoformat(r['date'].strip()) for r in _special_rows(path) if r.get('type', '').strip() == 'anomaly'}


def day_features(d, holidays):
    """Calendar description of one date. Off = Friday or official holiday. A 'block' is a run of off days."""
    def off(x):
        return iran_weekday(x) == 6 or x in holidays
    f = dict(dow=iran_weekday(d), off=int(off(d)))
    if f['off']:
        a = b = d
        while off(a - dt.timedelta(days=1)):
            a -= dt.timedelta(days=1)
        while off(b + dt.timedelta(days=1)):
            b += dt.timedelta(days=1)
        n = (b - a).days + 1
        f['blk'] = min(n, 5)
        f['pos'] = 1 if n == 1 else 2 if d == a else 4 if d == b else 3        # single · first · last · middle
        f['eve'], f['after'] = 0, 0
    else:
        f['blk'], f['pos'] = 0, 0
        k = 1
        while k <= 3 and not off(d + dt.timedelta(days=k)):
            k += 1
        nxt = d + dt.timedelta(days=k)
        n = 0
        while k <= 3 and off(nxt + dt.timedelta(days=n)):
            n += 1
        f['eve'] = k if k <= 3 and n >= 2 else 0                                # days before a block of ≥ 2 off days
        f['after'] = int(off(d - dt.timedelta(days=1)))
    jy, jm, jd = g2j(d)
    nz = (d - farvardin1(jy if jm < 7 else jy + 1)).days                     # days from the nearest Farvardin 1
    f['nz'] = nz if -7 <= nz <= 15 else 99
    f['season'] = (jm - 1) // 3
    return f


FEATURES = ['hour', 'dirn', 'dow', 'off', 'blk', 'pos', 'eve', 'after', 'nz', 'season']


def state(speed):
    if speed is None:
        return None
    return 'A' if speed >= SPEED_A else 'C' if speed < SPEED_C else 'B'


# ── the hourly table ──────────────────────────────────────────────────────────────────────────────────────────
def read_hourly(path):
    """Read the common hourly CSV. Lines starting with '#' are comments (the synthetic fixture says so there)."""
    lines = open(path, encoding='utf-8').read().splitlines()
    comments = [x for x in lines if x.startswith('#')]
    rows = []
    for r in csv.DictReader(x for x in lines if not x.startswith('#')):
        rows.append(dict(date=dt.date.fromisoformat(r['date']), hour=int(r['hour']), dir=r['dir'],
                         count=int(float(r['count'])) if r.get('count', '') not in ('', None) else None,
                         speed=float(r['speed']) if r.get('speed', '') not in ('', None) else None,
                         closed=int(r.get('closed') or 0)))
    synthetic = any('SYNTHETIC' in c for c in comments) or any(k == 'synthetic' for k in (lines[len(comments)].split(',')))
    return rows, synthetic, comments


def detect_closures(rows):
    """Mark hours where one direction is (almost) empty while the other is busy: a police one-way, not a quiet road.
    Heuristic: count ≤ 3% of that direction's median at that hour, and the other direction above its own median.
    Rows already marked closed (from the police table) stay closed. Returns the number of hours newly marked."""
    by = {(r['date'], r['hour'], r['dir']): r for r in rows}
    med = {}
    for dirn in DIRS:
        for h in range(24):
            v = sorted(r['count'] for r in rows if r['dir'] == dirn and r['hour'] == h and r['count'] is not None)
            med[dirn, h] = v[len(v) // 2] if v else 0
    n = 0
    for r in rows:
        other = by.get((r['date'], r['hour'], 'S' if r['dir'] == 'N' else 'N'))
        if r['closed'] or r['count'] is None or other is None or other['count'] is None:
            continue
        if r['count'] <= 0.03 * med[r['dir'], r['hour']] and other['count'] > med[other['dir'], r['hour']]:
            r['closed'] = 2                      # 2 = detected by heuristic (1 = police table / fixture truth)
            n += 1
    return n


def usable(r):
    """Rows a model may learn from or be scored on: the direction was open and the counter reported."""
    return not r['closed'] and r['count'] is not None


# ── predictors ────────────────────────────────────────────────────────────────────────────────────────────────
def median(v):
    v = sorted(v)
    return None if not v else v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2


def _weeks_back(d, origin):
    """Smallest k >= 1 with d - 7k before the forecast origin: the latest same weekday the forecaster has seen."""
    k = 1
    if origin is not None and d >= origin:
        k = (d - origin).days // 7 + 1
    return k


class LastWeek:
    """B0 · the same hour, same direction and weekday, in the last week before the forecast origin (whatever that day was).
    Inside a held-out window the origin is the window's first day, so day 8 of Nowruz does NOT see day 1: like the
    other models, the baseline knows only data before the test days. Outside a fold (origin None) it is plain d − 7."""
    name = 'last_week'

    def fit(self, train, all_rows, origin=None):
        self.origin = origin
        self.by = {(r['date'], r['hour'], r['dir']): r for r in (train if origin is not None else all_rows)}
        return self

    def predict(self, d, h, dirn, cal):
        r = self.by.get((d - dt.timedelta(days=7 * _weeks_back(d, self.origin)), h, dirn))
        if r is None or not usable(r):
            return None, None
        return r['count'], r['speed']


class Median4:
    """B1 · median of the same hour on the same weekday over the 4 latest weeks before the forecast origin."""
    name = 'median_4wk'

    def fit(self, train, all_rows, origin=None):
        self.origin = origin
        self.by = {(r['date'], r['hour'], r['dir']): r for r in (train if origin is not None else all_rows)}
        return self

    def predict(self, d, h, dirn, cal):
        k0 = _weeks_back(d, self.origin)
        past = [self.by.get((d - dt.timedelta(days=7 * k), h, dirn)) for k in range(k0, k0 + 4)]
        past = [r for r in past if r is not None and usable(r)]
        return (median([r['count'] for r in past]),
                median([r['speed'] for r in past if r['speed'] is not None])) if past else (None, None)


def day_key(f):
    """The seasonal profile's day type: Nowruz day, holiday-block position, eve of a block, or plain weekday."""
    if f['nz'] != 99 and -3 <= f['nz'] <= 13:
        return 'nz%+d' % f['nz']
    if f['off'] and f['blk'] >= 2:
        return 'blk-' + {2: 'first', 3: 'mid', 4: 'last'}[f['pos']]
    if f['eve'] == 1:
        return 'eve'
    if f['after']:
        return 'after'
    return 'dow%d|s%d' % (f['dow'], f['season'])


class Profile:
    """B2 · seasonal profile with a holiday flag: median of training rows with the same day type, hour and direction
    (falls back to the plain weekday). Also gives P(closed): how often the police shut that direction at that slot."""
    name = 'profile'

    def fit(self, train, all_rows, origin=None):
        cnt, spd, clo = defaultdict(list), defaultdict(list), defaultdict(list)
        for r in train:
            k = (r['_key'], r['hour'], r['dir'])
            clo[k].append(1 if r['closed'] else 0)
            if usable(r):
                cnt[k].append(r['count'])
                if r['speed'] is not None:
                    spd[k].append(r['speed'])
        self.cnt = {k: median(v) for k, v in cnt.items()}
        self.spd = {k: median(v) for k, v in spd.items()}
        self.clo = {k: sum(v) / len(v) for k, v in clo.items()}
        return self

    def predict(self, d, h, dirn, cal):
        for key in (day_key(cal), 'dow%d|s%d' % (cal['dow'], cal['season'])):
            if (key, h, dirn) in self.cnt:
                return self.cnt[key, h, dirn], self.spd.get((key, h, dirn))
        return None, None

    def p_closed(self, d, h, dirn, cal):
        return self.clo.get((day_key(cal), h, dirn), self.clo.get(('dow%d|s%d' % (cal['dow'], cal['season']), h, dirn), 0.0))


class Boosted:
    """M · gradient-boosted regression trees on calendar features only (squared loss, depth 5, 150 trees, shrinkage 0.1).
    Rows with identical features are grouped first, which is exact for squared loss and makes pure Python fast."""
    name = 'boosted'

    def __init__(self, rounds=150, depth=5, lr=0.1, min_n=20, seed=7):
        self.rounds, self.depth, self.lr, self.min_n, self.seed = rounds, depth, lr, min_n, seed

    @staticmethod
    def vec(h, dirn, cal):
        return (h, DIRS.index(dirn), cal['dow'], cal['off'], cal['blk'], cal['pos'], cal['eve'], cal['after'],
                cal['nz'] + 7 if cal['nz'] != 99 else 30, cal['season'])

    def _fit_one(self, groups):
        # groups: list of [vec, n, sum_y]; returns (base, trees). numpy, if installed, only makes it faster.
        if np is not None:
            return self._fit_np(groups)
        tot_n = sum(g[1] for g in groups)
        base = sum(g[2] for g in groups) / tot_n
        pred = [base] * len(groups)
        trees = []
        for _ in range(self.rounds):
            res = [(g[2] - g[1] * p) for g, p in zip(groups, pred)]        # residual sums
            tree = self._grow(groups, res, list(range(len(groups))), 0)
            trees.append(tree)
            for i, g in enumerate(groups):
                pred[i] += self.lr * self._eval(tree, g[0])
        return base, trees

    def _fit_np(self, groups):
        X = np.array([g[0] for g in groups], dtype=np.int64)
        n = np.array([g[1] for g in groups], dtype=float)
        sy = np.array([g[2] for g in groups], dtype=float)
        base = sy.sum() / n.sum()
        pred = np.full(len(groups), base)
        width = X.max(axis=0) + 1
        trees = []

        def grow(idx, res, depth):
            nn, ss = n[idx].sum(), res[idx].sum()
            if depth == self.depth or nn < 2 * self.min_n:
                return float(ss / nn) if nn else 0.0
            best = None
            for f in range(X.shape[1]):
                cn = np.cumsum(np.bincount(X[idx, f], weights=n[idx], minlength=width[f]))[:-1]
                cs = np.cumsum(np.bincount(X[idx, f], weights=res[idx], minlength=width[f]))[:-1]
                rn = nn - cn
                ok = (cn >= self.min_n) & (rn >= self.min_n)
                if not ok.any():
                    continue
                gain = np.where(ok, cs * cs / np.maximum(cn, 1) + (ss - cs) ** 2 / np.maximum(rn, 1), -np.inf)
                v = int(gain.argmax())
                if best is None or gain[v] > best[0]:
                    best = (gain[v], f, v)
            if best is None:
                return float(ss / nn)
            _, f, v = best
            m = X[idx, f] <= v
            return (f, v, grow(idx[m], res, depth + 1), grow(idx[~m], res, depth + 1))

        def leaf_values(tree, idx, out):
            if not isinstance(tree, tuple):
                out[idx] = tree
                return
            m = X[idx, tree[0]] <= tree[1]
            leaf_values(tree[2], idx[m], out)
            leaf_values(tree[3], idx[~m], out)

        all_idx = np.arange(len(groups))
        step = np.zeros(len(groups))
        for _ in range(self.rounds):
            tree = grow(all_idx, sy - n * pred, 0)
            trees.append(tree)
            leaf_values(tree, all_idx, step)
            pred += self.lr * step
        return float(base), trees

    def _grow(self, groups, res, idx, depth):
        n = sum(groups[i][1] for i in idx)
        s = sum(res[i] for i in idx)
        if depth == self.depth or n < 2 * self.min_n:
            return s / n if n else 0.0
        best = None
        for f in range(len(FEATURES)):
            acc = defaultdict(lambda: [0, 0.0])
            for i in idx:
                a = acc[groups[i][0][f]]
                a[0] += groups[i][1]
                a[1] += res[i]
            vals = sorted(acc)
            ln, ls = 0, 0.0
            for v in vals[:-1]:                                              # split: feature ≤ v goes left
                ln += acc[v][0]
                ls += acc[v][1]
                rn, rs = n - ln, s - ls
                if ln < self.min_n or rn < self.min_n:
                    continue
                gain = ls * ls / ln + rs * rs / rn
                if best is None or gain > best[0]:
                    best = (gain, f, v)
        if best is None:
            return s / n
        _, f, v = best
        left = [i for i in idx if groups[i][0][f] <= v]
        right = [i for i in idx if groups[i][0][f] > v]
        return (f, v, self._grow(groups, res, left, depth + 1), self._grow(groups, res, right, depth + 1))

    @staticmethod
    def _eval(tree, x):
        while isinstance(tree, tuple):
            tree = tree[2] if x[tree[0]] <= tree[1] else tree[3]
        return tree

    def fit(self, train, all_rows, origin=None):
        self.models = {}
        for target in ('count', 'speed'):
            g = {}
            for r in train:
                if not usable(r) or r[target] is None:
                    continue
                v = self.vec(r['hour'], r['dir'], r['_cal'])
                a = g.setdefault(v, [v, 0, 0.0])
                a[1] += 1
                a[2] += r[target]
            self.models[target] = self._fit_one(list(g.values())) if g else None
        return self

    def predict(self, d, h, dirn, cal):
        x = self.vec(h, dirn, cal)
        out = []
        for target in ('count', 'speed'):
            m = self.models.get(target)
            out.append(None if m is None else max(0.0, m[0] + self.lr * sum(self._eval(t, x) for t in m[1])))
        return tuple(out)


MODELS = [LastWeek, Median4, Profile, Boosted]
MODEL_LABEL = {'last_week': 'same hour last week', 'median_4wk': 'median of last 4 weeks',
               'profile': 'calendar profile + holiday flag', 'boosted': 'boosted trees (calendar ML)'}


def seeded(seed):
    return random.Random(seed)


def lognormal(rng, sd):
    return math.exp(rng.gauss(0, sd) - sd * sd / 2)
