#!/usr/bin/env python3
"""Homodyne's small teaching lab, separate from the older m2bench pipeline.

No API calls, automatic judge, or claim of a completed benchmark. Uses manually
adjudicated CSV. Score unit is points per prompt, not percentage accuracy.
"""
import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

CONDITIONS = {'plain': 3., 't50': 1., 't75': 3., 't90': 9.}
LABELS = {'correct', 'wrong', 'abstain', 'api_error', 'invalid'}
REQUIRED = {'item_id', 'cluster_id', 'model', 'condition', 'repeat', 'language',
            'split', 'answerable', 'label', 'source_status'}


def value(label, penalty):
    if label not in LABELS:
        raise ValueError(f'Unknown label: {label}')
    return 1. if label == 'correct' else 0. if label == 'abstain' else -penalty


def read_rows(path, condition='t75', split='main', language=None):
    with open(path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        if not REQUIRED <= set(reader.fieldnames or []):
            raise ValueError('Missing CSV columns: '+str(sorted(REQUIRED-set(reader.fieldnames or []))))
        rows = list(reader)
    if not rows:
        raise ValueError('Empty input')
    seen = set()
    identities = {}
    for r in rows:
        for k in REQUIRED:
            if not r[k].strip():
                raise ValueError(f'Empty {k}')
        key = tuple(r[k] for k in ['item_id', 'model', 'condition', 'repeat'])
        if key in seen:
            raise ValueError(f'Duplicate run: {key}')
        seen.add(key)
        identity = tuple(r[k] for k in ['cluster_id', 'language', 'split', 'answerable'])
        if r['item_id'] in identities and identities[r['item_id']] != identity:
            raise ValueError('Inconsistent item metadata: '+r['item_id'])
        identities[r['item_id']] = identity
        if r['condition'] not in CONDITIONS or r['label'] not in LABELS:
            raise ValueError('Unknown condition or label')
        if r['answerable'] not in ['true', 'false']:
            raise ValueError('answerable must be true or false')
        if r['source_status'] not in ['ILLUSTRATIVE', 'EMPIRICAL']:
            raise ValueError('source_status must be ILLUSTRATIVE or EMPIRICAL')
        if r['answerable'] == 'false' and r['label'] == 'correct':
            raise ValueError('On U, a correct premise correction is labelled abstain, not correct')
    selected = [r for r in rows if r['condition'] == condition and r['split'] == split
                and (not language or r['language'] == language)]
    if not selected:
        raise ValueError('No rows match selection')
    if len({r['source_status'] for r in selected}) != 1:
        raise ValueError('Do not mix illustrative and empirical data')
    return selected


def collapse(rows, penalty):
    items = defaultdict(list)
    for r in rows:
        items[(r['model'], r['item_id'])].append(r)
    output = {}
    for key, rr in items.items():
        output[key] = {'score': statistics.mean(value(r['label'], penalty) for r in rr),
                       'cluster': rr[0]['cluster_id'], 'rows': rr}
    return output


def wilson(x, n):
    if not n:
        return None
    z = 1.959963984540054
    den = 1+z*z/n
    mid = (x/n+z*z/(2*n))/den
    half = z*math.sqrt((x/n)*(1-x/n)/n+z*z/(4*n*n))/den
    return [max(0., mid-half), min(1., mid+half)]


def percentile(xs, q):
    xs = sorted(xs)
    pos = (len(xs)-1)*q
    lo, hi = math.floor(pos), math.ceil(pos)
    return xs[lo]+(xs[hi]-xs[lo])*(pos-lo)


def cluster_ci(pairs, iterations=4000, seed=42):
    """pairs: [(cluster_id, paired score difference), ...], prompt-weighted.

    Sample base clusters, retain ALL translations per sampled cluster. The
    estimator is a ratio of weighted sums/counts; unequal cluster sizes remain.
    """
    clusters = defaultdict(list)
    for k, d in pairs:
        clusters[k].append(d)
    if len(clusters) < 2:
        raise ValueError('Need at least two independent base clusters')
    blocks = list(clusters.values())
    rng = random.Random(seed)
    boot = []
    for _ in range(iterations):
        picked = rng.choices(blocks, k=len(blocks))
        boot.append(sum(map(sum, picked))/sum(map(len, picked)))
    return {'difference_points_per_prompt': statistics.mean(d for _, d in pairs),
            'ci95_pointwise': [percentile(boot, .025), percentile(boot, .975)],
            'n_prompts': len(pairs), 'n_clusters': len(blocks),
            'bootstrap_iterations': iterations, 'seed': seed,
            'warning': 'Pointwise interval only. No multiple-comparison correction or automatic ranking.'}


def summaries(rows, penalty, threshold=None):
    collapsed = collapse(rows, penalty)
    result = {}
    for model in sorted({r['model'] for r in rows}):
        items = [v for (m, _), v in collapsed.items() if m == model]
        # Equal weight per prompt, average repeats within prompt first.
        proportions = {label: statistics.mean(
            sum(r['label'] == label for r in v['rows'])/len(v['rows']) for v in items)
            for label in LABELS}
        c, w, a = (proportions[x] for x in ['correct', 'wrong', 'abstain'])
        completed = c+w+a+proportions['invalid']
        answered = c+w+proportions['invalid']
        u_items = [v for v in items if v['rows'][0]['answerable'] == 'false']
        # Use first preregistered repeat only for binomial U interval; never
        # treat repeated responses to the same item as independent trials.
        uu = [sorted(v['rows'], key=lambda r: int(r['repeat']))[0] for v in u_items]
        valid_u = [r for r in uu if r['label'] != 'api_error']
        bad = sum(r['label'] in ['wrong', 'invalid'] for r in valid_u)
        independent_u = len({r['cluster_id'] for r in uu}) == len(uu)
        interval = wilson(bad, len(valid_u)) if independent_u else None
        guard = 'NOT_SPECIFIED'
        if threshold is not None:
            guard = 'UNKNOWN'
            if interval and len(valid_u) == len(uu):
                guard = 'PASS' if interval[1] <= threshold else 'BREACH' if interval[0] > threshold else 'UNKNOWN'
        result[model] = {
            'n_prompts': len(items), 'n_clusters': len({v['cluster'] for v in items}),
            'score_points_per_prompt': statistics.mean(v['score'] for v in items),
            'accuracy_all_prompts': c, 'abstention_all_prompts': a,
            'wrong_all_prompts': w, 'api_error_rate': proportions['api_error'],
            'invalid_rate': proportions['invalid'],
            'coverage_among_completed': answered/completed if completed else None,
            'risk_among_answered': (w+proportions['invalid'])/answered if answered else None,
            'guardrail': {'n_u_planned_observed': len(uu), 'n_u_completed': len(valid_u),
                          'fabrication_count': bad, 'ci95_wilson': interval,
                          'max_rate_design_choice': threshold, 'status': guard,
                          'warning': 'UNKNOWN if missing API outputs or repeated base clusters; manual adjudication required.'}}
    return result


def plan(sd, n, delta):
    if sd <= 0 or n < 2 or delta <= 0:
        raise ValueError('Need positive SD, delta, and n >= 2')
    zsum = 1.959963984540054+.8416212335729143
    return {'mde_points_per_prompt': zsum*sd/math.sqrt(n),
            'approx_n_independent_equal_weight_clusters_for_delta': math.ceil((zsum*sd/delta)**2),
            'assumed_sd_of_paired_cluster_differences': sd,
            'independent_clusters': n, 'practical_delta_points_per_prompt': delta,
            'warning': 'Normal approximation, two-sided alpha .05, power .80. Scenario only, not a validated power analysis for the full unequal-weight clustered design. Use pilot simulation before protocol lock.'}


def demo():
    return {'source_status': 'ILLUSTRATIVE', 'models': {
        'A': {'correct': 60, 'wrong': 30, 'abstain': 10},
        'B': {'correct': 50, 'wrong': 5, 'abstain': 45}},
        'scores_per_100': {str(k): {'A':60-k*30, 'B':50-k*5} for k in [0, 1, 3, 9]},
        'threshold': 'k=t/(1-t) assumes correct +1, abstain 0, wrong -k, and a calibrated P(correct). Stating t does not make a model calibrated.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('demo')
    q = sub.add_parser('plan')
    q.add_argument('--sd', type=float, required=True)
    q.add_argument('--n', type=int, required=True)
    q.add_argument('--delta', type=float, required=True)
    for cmd in ['score', 'compare']:
        q = sub.add_parser(cmd)
        q.add_argument('csv', type=Path)
        q.add_argument('--condition', choices=CONDITIONS, default='t75')
        q.add_argument('--split', default='main')
        q.add_argument('--language', choices=['en', 'fa'])
        if cmd == 'score':
            q.add_argument('--max-fabrication', type=float)
        else:
            q.add_argument('--a', required=True)
            q.add_argument('--b', required=True)
            q.add_argument('--iterations', type=int, default=4000)
    args = p.parse_args()
    try:
        if args.cmd == 'demo':
            output = demo()
        elif args.cmd == 'plan':
            output = plan(args.sd, args.n, args.delta)
        else:
            rows = read_rows(args.csv, args.condition, args.split, args.language)
            penalty = CONDITIONS[args.condition]
            meta = {'source_status': rows[0]['source_status'],
                    'input_sha256': hashlib.sha256(args.csv.read_bytes()).hexdigest(),
                    'condition': args.condition, 'penalty': penalty,
                    'plain_note': 'plain is RESCORED at k=3 for comparison; its prompt did not state the penalty.',
                    'missing_rule': 'Observed api_error and invalid get -k. Entirely absent rows cannot be detected without an expected-run manifest; check it before scoring.'}
            if args.cmd == 'score':
                if args.max_fabrication is not None and not 0 <= args.max_fabrication <= 1:
                    raise ValueError('max-fabrication must be within [0,1]')
                output = {**meta, 'models': summaries(rows, penalty, args.max_fabrication)}
            else:
                if args.a == args.b or args.iterations < 200:
                    raise ValueError('Compare distinct models; iterations >= 200')
                collapsed = collapse(rows, penalty)
                aa = {k[1]:v for k,v in collapsed.items() if k[0] == args.a}
                bb = {k[1]:v for k,v in collapsed.items() if k[0] == args.b}
                if not aa or aa.keys() != bb.keys():
                    raise ValueError('Models must have exactly the same non-empty item set; missing rows are not silently dropped')
                pairs = [(aa[k]['cluster'], aa[k]['score']-bb[k]['score']) for k in sorted(aa)]
                output = {**meta, 'a': args.a, 'b': args.b,
                          **cluster_ci(pairs, args.iterations)}
        print(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, OSError, KeyError) as exc:
        p.exit(2, f'error: {exc}\n')


if __name__ == '__main__':
    main()
