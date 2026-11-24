"""charts.py — CSV tables and matplotlib PNG charts for HMD-023 (the deck redraws them as inline SVG).

Every chart of the fake service carries the label SIMULATED SERVICE (ILLUSTRATIVE) in its title.
If matplotlib is missing, the CSV files are still written and the charts are skipped with a note.
"""
import csv
from pathlib import Path

INF = float('inf')
AMBER, INK, MUTED, BG = '#E8A33D', '#1d1f22', '#8a8f98', '#F3F1EC'


def write_csv(path, rows, fields=None):
    rows = list(rows)
    if not rows:
        return
    fields = fields or list(rows[0].keys())
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: ('inf' if v == INF else (round(v, 4) if isinstance(v, float) else v)) for k, v in r.items()})


def _plt():
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False,
                             'figure.facecolor': 'white'})
        return plt
    except ImportError:
        return None


def _cap(v, cap):
    return cap if v is None or v == INF or v > cap else v


def charts(outdir, label, ramp=None, timeline=None, open_rows=None, policies=None, slo=3.0, timeout=30.0):
    plt = _plt()
    out = Path(outdir) / 'charts'
    if plt is None:
        return ['matplotlib not installed: charts skipped (CSV files are complete)']
    out.mkdir(parents=True, exist_ok=True)
    made = []
    if ramp:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        xs = [str(r['users']) for r in ramp]
        p95 = [_cap(r['ttft_p95'], timeout) for r in ramp]
        p50 = [_cap(r['ttft_p50'], timeout) for r in ramp]
        ax.bar(xs, p95, color=[AMBER if not r['slo_met'] else INK for r in ramp], label='first word, p95')
        ax.plot(xs, p50, 'o-', color=MUTED, label='first word, p50')
        ax.axhline(slo, color=AMBER, ls='--', lw=1.5)
        ax.text(-0.45, slo * 1.08, f'SLO {slo:g}s', color=AMBER, ha='left', va='bottom')
        for i, r in enumerate(ramp):
            ax.text(i, p95[i] * 1.08 + 0.05, f'n={r["sent"]}\nfail {r["fail_rate"]:.0%}', ha='center', fontsize=9)
        ax.set_yscale('symlog', linthresh=1)
        ax.set_ylim(0, timeout * 3)
        ax.set_xlabel('virtual users (closed loop)')
        ax.set_ylabel(f'seconds to first word (capped at timeout {timeout:g}s)')
        ax.set_title(f'Users vs time to first word · {label}', fontsize=11)
        ax.legend(frameon=False, loc='upper left')
        fig.tight_layout()
        fig.savefig(out / 'ramp.png', dpi=150)
        plt.close(fig)
        made.append('charts/ramp.png')
    if timeline:
        fig, ax = plt.subplots(figsize=(10, 3.8))
        t0, xs, ys, cuts = 0.0, [], [], []
        for stage, samples in timeline:
            for s in samples:
                xs.append(t0 + s['t'])
                ys.append(s['waiting'])
            if samples:
                cuts.append((t0, stage))
                t0 += samples[-1]['t'] + 5
        ax.fill_between(xs, ys, step='post', color=AMBER, alpha=0.8, lw=0)
        for x, stage in cuts:
            ax.axvline(x, color=MUTED, lw=0.8)
            ax.text(x + 2, max(ys + [1]) * 0.95, stage, fontsize=9, color=INK, va='top')
        ax.set_xlabel('seconds (stages back to back)')
        ax.set_ylabel('requests waiting for first word')
        ax.set_title(f'The queue over time · {label}', fontsize=11)
        fig.tight_layout()
        fig.savefig(out / 'queue.png', dpi=150)
        plt.close(fig)
        made.append('charts/queue.png')
    if open_rows:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        xs = [r['rate'] for r in open_rows]
        ax.plot(xs, [_cap(r['ttft_p95'], timeout) for r in open_rows], 'o-', color=AMBER, lw=2.5, label='first word, p95')
        ax.plot(xs, [_cap(r['ttft_p50'], timeout) for r in open_rows], 'o-', color=MUTED, label='first word, p50')
        ax.axhline(slo, color=INK, ls='--', lw=1)
        ax.text(xs[0], slo * 1.1, f'SLO {slo:g}s', color=INK)
        ax.set_xlabel('requests per second arriving (open loop)')
        ax.set_ylabel(f'seconds (capped at {timeout:g}s)')
        ax.set_title(f'Waiting does not climb gently · {label}', fontsize=11)
        ax.legend(frameon=False, loc='upper left')
        fig.tight_layout()
        fig.savefig(out / 'open-loop.png', dpi=150)
        plt.close(fig)
        made.append('charts/open-loop.png')
    if policies:
        fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
        names = [p['policy'] for p in policies]
        for ax, key, title in zip(axes, ('slo_good_share', 'fail_rate', 'mean_out_tokens'),
                                  ('within SLO (share of requests)', 'failed: timeout or busy (share)', 'mean answer length (tokens)')):
            vals = [p[key] or 0 for p in policies]
            ax.barh(names, vals, color=[AMBER if i else MUTED for i in range(len(names))])
            ax.set_title(title, fontsize=10)
            ax.set_xticks([])
            ax.spines['bottom'].set_visible(False)
            for i, v in enumerate(vals):
                ax.text(v, i, f' {v:.0%}' if key != 'mean_out_tokens' else f' {v:.0f}', va='center', fontsize=9)
        axes[0].invert_yaxis()
        fig.suptitle(f'100 users, four policies · {label}', fontsize=11)
        fig.tight_layout()
        fig.savefig(out / 'policies.png', dpi=150)
        plt.close(fig)
        made.append('charts/policies.png')
    return made
