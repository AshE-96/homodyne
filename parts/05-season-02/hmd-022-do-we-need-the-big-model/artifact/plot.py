"""HMD-022 · the cost/quality chart (PNG) and its data (CSV), for the deck and the description.

Left: every router on the frozen test set, non-risk categories. Horizontal = cost per 1,000 tasks, vertical = share
correct. Lines join one router's thresholds; the ring marks the threshold picked on dev. Right: the risk category,
which is not routed (always the big model plus a human check); it shows what each router would have let through.
"""
import csv

AMBER, INK, MUTED, GRID = '#E8A33D', '#1d1f23', '#8a8f98', '#d9d6cf'
STYLE = {'always-small': ('s', MUTED), 'always-big': ('D', INK), 'rule-category': ('^', '#5b6b7f'),
         'rule-length': ('v', '#7d8ea3'), 'confidence': ('o', '#3f6f8f'), 'cascade': ('P', '#6b5b8f'), 'oracle': ('*', AMBER)}


def write_csv(result, path):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['set', 'router', 'threshold', 'n', 'correct', 'accuracy', 'cost_per_1000_tasks', 'cost_per_1000_successes',
                    'escalation_rate', 'p95_latency_s', 'missed_escalations', 'wasted_escalations', 'picked_on_dev'])
        for name, pts in (('dev', result['curve_dev']), ('test', result['curve_test'])):
            for p in pts:
                picked = result['picks'][p['family']]['threshold'] == p['threshold'] and result['picks'][p['family']]['feasible']
                w.writerow([name, p['family'], p['threshold'], p['n'], p['correct'], f'{p["accuracy"]:.4f}',
                            f'{1000 * p["cost_per_task"]:.4f}',
                            '' if p['cost_per_success'] is None else f'{1000 * p["cost_per_success"]:.4f}',
                            f'{p["escalation_rate"]:.4f}', f'{p["p95_latency"]:.3f}', p['missed_escalations'],
                            p['wasted_escalations'], int(picked)])


def plot(result, path, title, label):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={'width_ratios': [2.1, 1]})
    for a in (ax, bx):
        a.spines[['top', 'right']].set_visible(False)
        a.grid(True, color=GRID, linewidth=0.7)
        a.set_axisbelow(True)
    pts = result['curve_test']
    for fam, (marker, color) in STYLE.items():
        xs = sorted(((1000 * p['cost_per_task'], 100 * p['accuracy']) for p in pts if p['family'] == fam))
        if not xs:
            continue
        if len(xs) > 1:
            ax.plot([x for x, _ in xs], [y for _, y in xs], '-', color=color, linewidth=1.4, alpha=0.8)
        ax.plot([x for x, _ in xs], [y for _, y in xs], marker, color=color, markersize=7 if fam != 'oracle' else 15,
                linestyle='none', label='oracle (upper bound)' if fam == 'oracle' else fam)
        pick = result['picks'][fam]
        if pick['feasible'] and fam in result['test'] and pick['threshold'] is not None or fam == 'rule-category' and pick['feasible']:
            t = result['test'][fam]
            ax.plot(1000 * t['cost_per_task'], 100 * t['accuracy'], 'o', markersize=17, markerfacecolor='none',
                    markeredgecolor=AMBER, markeredgewidth=2.2)
    ax.set_xlabel('cost per 1,000 tasks (USD, prices.json)')
    ax.set_ylabel('correct (%) · test set, non-risk categories')
    ax.set_title(f'{title}\nring = threshold picked on dev (quality budget {result["budget_pp"]:g} points)', fontsize=10.5)
    ax.legend(frameon=False, fontsize=9, loc='lower right')

    fams = [f for f in ('always-small', 'confidence', 'cascade', 'rule-category', 'always-big') if f in result['risk_test']]
    vals = [100 * result['risk_test'][f]['accuracy'] for f in fams]
    bx.barh(fams, vals, color=[AMBER if f == 'always-big' else MUTED for f in fams])
    for i, (f, v) in enumerate(zip(fams, vals)):
        r = result['risk_test'][f]
        bx.text(v + 1, i, f'{r["correct"]}/{r["n"]}', va='center', fontsize=9)
    bx.set_xlim(0, 112)
    bx.set_xlabel('correct (%) · risk category, test')
    bx.set_title('risk category: not routed\n(policy: big model + human check)', fontsize=10.5)
    if 'MOCK' in label:
        fig.text(0.5, 0.5, 'MOCK · NOT A RESULT', fontsize=54, color='#b5452f', alpha=0.13, ha='center', va='center',
                 rotation=18, weight='bold')
    fig.text(0.01, 0.01, label, fontsize=9, color='#b5452f' if 'MOCK' in label else MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(path, dpi=150)
    plt.close(fig)
