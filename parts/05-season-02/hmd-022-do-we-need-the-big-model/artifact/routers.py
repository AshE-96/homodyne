"""HMD-022 · routers and the routing simulator.

Input: a per-item table, one row per request, with what each model did on it (correct or not, cost, latency, the
small model's self-reported confidence, and how many of three small-model samples agreed). Output: every router's
cost/quality points, the threshold each router picks on the dev set, and its result on the frozen test set.

No model is called here, so you can feed it any table with the same columns (see `COLUMNS`).

Routers
- always-small, always-big
- rule-category: a fixed rule written before any run: multistep and highrisk go to the big model
- rule-length: prompts longer than L characters go to the big model (L chosen on dev)
- confidence: the small model answers; if its own confidence is below t, ask the big model (t chosen on dev)
- cascade: three small-model samples; if fewer than m agree with the first, ask the big model (m chosen on dev)
- oracle: knows in advance which model is right; pays only for the cheapest one that is (the upper bound)

Selection rule (fixed in protocol.md before any run): on the dev set, non-risk categories only, keep thresholds whose
accuracy is at least always-big's accuracy minus QUALITY_BUDGET_PP, and pick the lowest cost per successful task.
The risk category is not routed: it always goes to the big model plus a human check.
"""
import csv
import math
import random

COLUMNS = ['id', 'split', 'category', 'lang', 'risk', 'chars',
           's1_correct', 's1_conf', 's1_cost', 's1_lat', 's1_in', 's1_out',
           's2_cost', 's2_lat', 's3_cost', 's3_lat', 'agree',
           'b_correct', 'b_cost', 'b_lat', 'b_in', 'b_out', 's1_refused', 'b_refused']
QUALITY_BUDGET_PP = 2.0
HARD_CATEGORIES = {'multistep', 'highrisk'}
FAMILIES = ['always-small', 'always-big', 'rule-category', 'rule-length', 'confidence', 'cascade', 'oracle']


def read_table(path):
    with open(path, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ('s1_correct', 'b_correct', 'risk', 's1_refused', 'b_refused'):
            r[k] = str(r.get(k, '')).lower() in ('1', 'true')
        for k in ('chars', 'agree', 's1_in', 's1_out', 'b_in', 'b_out'):
            r[k] = int(float(r[k] or 0))
        for k in ('s1_cost', 's1_lat', 's2_cost', 's2_lat', 's3_cost', 's3_lat', 'b_cost', 'b_lat'):
            r[k] = float(r[k] or 0)
        r['s1_conf'] = None if r['s1_conf'] in ('', 'None', None) else float(r['s1_conf'])
    return rows


def write_table(rows, path):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in COLUMNS})


# ── one router on one item ───────────────────────────────────────────────────────────────────────
def route(r, family, th=None):
    """Return (correct, cost, latency, escalated) for one item."""
    small = (r['s1_correct'], r['s1_cost'], r['s1_lat'], False)
    big = (r['b_correct'], r['b_cost'], r['b_lat'], True)
    if family == 'always-small':
        return small
    if family == 'always-big':
        return big
    if family == 'rule-category':
        return big if r['category'] in HARD_CATEGORIES else small
    if family == 'rule-length':
        return big if r['chars'] > th else small
    if family == 'confidence':
        conf = r['s1_conf'] if r['s1_conf'] is not None else -1
        if conf >= th:
            return small
        return r['b_correct'], r['s1_cost'] + r['b_cost'], r['s1_lat'] + r['b_lat'], True
    if family == 'cascade':
        cost = r['s1_cost'] + r['s2_cost'] + r['s3_cost']
        lat = max(r['s1_lat'], r['s2_lat'], r['s3_lat'])          # the three samples are sent together
        if r['agree'] >= th:
            return r['s1_correct'], cost, lat, False
        return r['b_correct'], cost + r['b_cost'], lat + r['b_lat'], True
    if family == 'oracle':
        if r['s1_correct'] or not r['b_correct']:
            return small                                           # cheapest model that is right (or nobody is)
        return big
    raise ValueError(family)


def thresholds(family, dev_rows):
    if family == 'rule-length':
        xs = sorted({r['chars'] for r in dev_rows})
        return [-1] + xs                                           # -1 = everything to the big model
    if family == 'confidence':
        return list(range(0, 101, 5)) + [101]                      # 101 = always escalate
    if family == 'cascade':
        return [1, 2, 3, 4]                                        # 1 = never escalate, 4 = always
    return [None]


def p95(values):
    """Nearest-rank 95th percentile: the slowest one in every twenty."""
    if not values:
        return 0.0
    v = sorted(values)
    return v[max(0, math.ceil(0.95 * len(v)) - 1)]


def evaluate(rows, family, th=None):
    out = [route(r, family, th) for r in rows]
    n = len(out)
    ok = sum(o[0] for o in out)
    cost = sum(o[1] for o in out)
    missed = sum((not o[3]) and (not r['s1_correct']) and r['b_correct'] for o, r in zip(out, rows))
    wasted = sum(o[3] and r['s1_correct'] for o, r in zip(out, rows))
    return {'family': family, 'threshold': th, 'n': n, 'correct': ok, 'accuracy': ok / n if n else 0.0,
            'cost': cost, 'cost_per_task': cost / n if n else 0.0, 'cost_per_success': cost / ok if ok else None,
            'escalation_rate': sum(o[3] for o in out) / n if n else 0.0,
            'p50_latency': sorted(o[2] for o in out)[n // 2] if n else 0.0, 'p95_latency': p95([o[2] for o in out]),
            'missed_escalations': missed, 'wasted_escalations': wasted}


def subset(rows, split=None, scope='nonrisk'):
    return [r for r in rows if (split is None or r['split'] == split)
            and (scope == 'all' or (scope == 'nonrisk' and not r['risk']) or (scope == 'risk' and r['risk']))]


def curves(rows, split, scope):
    """Every router at every threshold on one subset: the points of the cost/quality chart."""
    sub = subset(rows, split, scope)
    dev = subset(rows, 'dev', scope)
    return [evaluate(sub, f, th) for f in FAMILIES for th in thresholds(f, dev)]


def choose(rows, budget_pp=QUALITY_BUDGET_PP):
    """Pick each router's threshold on dev (non-risk), by the rule in protocol.md."""
    dev = subset(rows, 'dev', 'nonrisk')
    floor = evaluate(dev, 'always-big')['accuracy'] - budget_pp / 100
    picks = {}
    for f in FAMILIES:
        pts = [evaluate(dev, f, th) for th in thresholds(f, dev)]
        ok = [p for p in pts if p['accuracy'] >= floor - 1e-9 and p['cost_per_success'] is not None]
        best = min(ok, key=lambda p: (p['cost_per_success'], -p['accuracy'])) if ok else None
        picks[f] = {'threshold': best['threshold'] if best else None, 'feasible': bool(best), 'dev': best,
                    'floor': floor}
    return picks


def bootstrap(rows, family, th, reps=2000, seed=22):
    """Paired bootstrap over test items, router vs always-big, 95% intervals for:
    the accuracy difference (points) and the ratio of cost per successful task (router / always-big)."""
    rng = random.Random(seed)
    a = [route(r, family, th) for r in rows]
    b = [route(r, 'always-big') for r in rows]
    n = len(rows)

    def cps_ratio(idx):
        ca, cb = sum(a[i][1] for i in idx), sum(b[i][1] for i in idx)
        ka, kb = sum(a[i][0] for i in idx), sum(b[i][0] for i in idx)
        if not (ka and kb and cb):
            return float('nan')
        return (ca / ka) / (cb / kb)

    diffs, ratios = [], []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(100 * (sum(a[i][0] for i in idx) - sum(b[i][0] for i in idx)) / n)
        ratios.append(cps_ratio(idx))
    diffs.sort()
    ratios = sorted(x for x in ratios if x == x)
    lo, hi = int(0.025 * reps), int(0.975 * reps) - 1
    rlo, rhi = int(0.025 * len(ratios)), max(0, int(0.975 * len(ratios)) - 1)
    return {'acc_diff_pp': 100 * (sum(x[0] for x in a) - sum(x[0] for x in b)) / n, 'acc_diff_ci': (diffs[lo], diffs[hi]),
            'cps_ratio': cps_ratio(range(n)), 'cps_ratio_ci': (ratios[rlo], ratios[rhi]) if ratios else (float('nan'),) * 2}


def near(small, big, n, budget_pp=QUALITY_BUDGET_PP):
    """'Close to the big model' on one category = at most the quality budget behind it, in whole items.
    With 24 test items per category, 2 points is less than one item, so 'near' means not behind at all."""
    return small >= big - math.floor(budget_pp / 100 * n + 1e-9)


def by_category(rows, split='test'):
    cats = sorted({r['category'] for r in rows}, key=lambda c: ['lookup', 'convert', 'extract', 'multistep', 'highrisk'].index(c)
                  if c in ('lookup', 'convert', 'extract', 'multistep', 'highrisk') else 9)
    out = {}
    for c in cats:
        xs = [r for r in rows if r['category'] == c and r['split'] == split]
        out[c] = {'n': len(xs), 'small': sum(r['s1_correct'] for r in xs), 'big': sum(r['b_correct'] for r in xs),
                  'either': sum(r['s1_correct'] or r['b_correct'] for r in xs)}
        out[c]['near'] = near(out[c]['small'], out[c]['big'], out[c]['n'])
    return out


def simulate(rows, budget_pp=QUALITY_BUDGET_PP):
    """The full analysis from a per-item table: picks on dev, results on test, curves, risk view."""
    picks = choose(rows, budget_pp)
    test = subset(rows, 'test', 'nonrisk')
    risk = subset(rows, 'test', 'risk')
    result = {'budget_pp': budget_pp, 'picks': picks, 'test': {}, 'risk_test': {}, 'ci': {},
              'by_category': by_category(rows, 'test'), 'n_test_nonrisk': len(test), 'n_test_risk': len(risk)}
    for f, p in picks.items():
        fixed = thresholds(f, []) == [None]
        if not (p['feasible'] or fixed):
            continue                                   # a tuned router with no threshold inside the budget on dev
        th = p['threshold'] if p['feasible'] else None
        result['test'][f] = evaluate(test, f, th)
        result['risk_test'][f] = evaluate(risk, f, th)
        if f != 'always-big':
            result['ci'][f] = bootstrap(test, f, th)
    result['refusals'] = {'risk_big': sum(r.get('b_refused', False) for r in risk),
                          'nonrisk_big': sum(r.get('b_refused', False) for r in test),
                          'nonrisk_small': sum(r.get('s1_refused', False) for r in test)}
    result['curve_dev'] = curves(rows, 'dev', 'nonrisk')
    result['curve_test'] = curves(rows, 'test', 'nonrisk')
    return result
