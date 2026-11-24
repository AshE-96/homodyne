"""HMD-024 · report: Offline AI Capability Card (markdown + PNG), charts, summary.json and the Persian spoken
lines for the [RUN] beats (numbers written as words)."""
import csv
import json
import statistics
from pathlib import Path

from spoken import dec_fa, fa_num, smart_fa, words_fa
from task_bank import CAT_EN, CAT_FA, CATS, TASKS

HERE = Path(__file__).resolve().parent
TASK = {t['id']: t for t in TASKS}
GB = 1e9


def load_runs(runs_dir):
    runs = []
    for meta_path in sorted(Path(runs_dir).glob('*/meta.json')):
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        res = meta_path.parent / 'results.jsonl'
        rows = [json.loads(l) for l in res.read_text(encoding='utf-8').splitlines() if l.strip()] if res.exists() else []
        if rows:
            runs.append({'meta': meta, 'rows': {r['task_id']: r for r in rows}, 'dir': meta_path.parent})
    runs.sort(key=lambda r: (r['meta']['arm'] != 'local', r['meta'].get('download_bytes') or 0, r['meta']['model']))
    return runs


def load_blind(runs_dir):
    """Owner's blind sheet → {(run_dir_name, task_id): {'pass': bool|None, 'adds': bool|None}}."""
    sheet, key = Path(runs_dir) / 'blind' / 'sheet.csv', Path(runs_dir) / '.key' / 'blind-key.json'
    if not sheet.exists() or not key.exists():
        return {}
    k = json.loads(key.read_text(encoding='utf-8'))
    yes = lambda v: {'y': True, 'yes': True, 'n': False, 'no': False}.get(str(v).strip().lower())
    out = {}
    with sheet.open(encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['code'] not in k:
                continue
            run, tid = k[row['code']]
            if TASK[tid]['cat'] == 'translate':
                marks = [yes(row.get(c)) for c in ('meaning_kept', 'numbers_names_kept', 'reads_naturally')]
                out[(run, tid)] = {'pass': all(marks) if None not in marks else None}
            else:
                out[(run, tid)] = {'adds': yes(row.get('adds_something_not_in_text'))}
    return out


def final_pass(run, tid, blind):
    r = run['rows'].get(tid)
    if not r or r.get('error'):
        return False, 'error'
    b = blind.get((run['dir'].name, tid), {})
    if TASK[tid]['cat'] == 'translate':
        return (b['pass'], 'owner') if b.get('pass') is not None else (r['grade']['pass'], 'auto')
    if TASK[tid]['cat'] == 'summarise' and b.get('adds') is not None:
        return r['grade']['pass'] and not b['adds'], 'auto+owner'
    return r['grade']['pass'], 'auto'


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def summarise(runs, rules, blind):
    out = []
    for run in runs:
        m, rows = run['meta'], run['rows']
        cats = {}
        for c in CATS:
            ids = [t['id'] for t in TASKS if t['cat'] == c]
            res = {tid: final_pass(run, tid, blind) for tid in ids}
            n = sum(p for p, _ in res.values())
            lang = {lg: (sum(res[t][0] for t in ids if TASK[t]['lang'] == lg), sum(TASK[t]['lang'] == lg for t in ids))
                    for lg in ('fa', 'en')}
            pc = rules['per_category']
            sym = '✓' if n >= pc['offline_ok_min'] else ('~' if n >= pc['offline_with_check_min'] else '✗')
            tot = med(rows[t].get('total_s') for t in ids if t in rows)
            slow = m['arm'] == 'local' and sym == '✓' and tot is not None and tot > rules['speed']['max_median_total_s']
            cats[c] = {'n': n, 'of': len(ids), 'sym': '~' if slow else sym, 'slow': slow, 'fa': lang['fa'],
                       'en': lang['en'], 'source': sorted({s for _, s in res.values()}), 'median_total_s': tot}
        rr = list(rows.values())
        lat = online_latency(rr) if m['arm'] == 'online' else None
        absent = [r for r in rr if TASK[r['task_id']]['grader'] == 'absent']
        swap0 = m.get('swap_baseline_bytes')
        swap_growth = max(0, max((r.get('max_swap_used_bytes') or 0) for r in rr) - swap0) if swap0 is not None and rr else None
        ps_size = max((r.get('ps_size_bytes') or 0) for r in rr) or None
        ps_vram = max((r.get('ps_size_vram_bytes') or 0) for r in rr) or None
        fits = m['arm'] != 'local' or ((swap_growth is None or swap_growth <= rules['fit']['max_swap_growth_gb'] * GB)
                                        and (ps_size is None or ps_vram is None or ps_vram >= ps_size))
        s = {
            'model': m['model'], 'arm': m['arm'], 'spoken_fa': m.get('spoken_fa') or m['model'], 'dir': run['dir'].name,
            'passed': sum(final_pass(run, t['id'], blind)[0] for t in TASKS), 'of': len(TASKS),
            'fa': sum(final_pass(run, t['id'], blind)[0] for t in TASKS if t['lang'] == 'fa'),
            'en': sum(final_pass(run, t['id'], blind)[0] for t in TASKS if t['lang'] == 'en'),
            'cats': cats, 'invented': sum(bool(r['grade'].get('invented')) for r in absent), 'absent_n': len(absent),
            'errors': sum(bool(r.get('error')) for r in rr), 'truncated': sum(bool(r.get('possibly_truncated')) for r in rr),
            'ttft_med': med(r.get('ttft_s') for r in rr),
            'total_med': lat['median'] if lat else med(r.get('total_s') for r in rr),
            'retry_rows': lat['dropped'] if lat else 0,
            'tps_med': med(r.get('tokens_per_s') for r in rr), 'busy_s': sum(r.get('total_s') or 0 for r in rr),
            'peak_rss': max((r.get('peak_runner_rss_bytes') or 0) for r in rr) or None, 'ps_size': ps_size,
            'ps_vram': ps_vram, 'min_avail': min((r['min_available_bytes'] for r in rr if r.get('min_available_bytes')), default=None),
            'swap_growth': swap_growth, 'fits': fits, 'cold_load_s': m.get('cold_load_s'),
            'download_bytes': m.get('download_bytes'), 'quant': m.get('quantization'), 'params': m.get('parameter_size'),
            'tokens_in': sum(r.get('input_tokens') or 0 for r in rr), 'tokens_out': sum(r.get('output_tokens') or 0 for r in rr),
            'offline_verified': bool(m.get('offline_before') and m.get('offline_after') and all(m.get('offline_mid') or [True])),
            'fell_back': sum(bool(r.get('fell_back')) for r in rr), 'demo': bool(m.get('demo')),
            'locks': m.get('locks') or {}, 'effort': m.get('effort'), 'max_tokens': m.get('max_tokens'),
        }
        out.append(s)
    return out


def online_latency(rows):
    """Median online time without retry back-off: rows with a known retry (attempts > 1) use their last attempt;
    where attempts are unknown (Anthropic SDK path), rows slower than 3× the median are dropped as probable retries."""
    vals, dropped = [], 0
    plain = [r.get('total_s') for r in rows if r.get('total_s') is not None and not r.get('cached')]
    m0 = med(plain)
    for r in rows:
        if r.get('total_s') is None or r.get('cached'):
            continue
        if r.get('attempts'):
            vals.append(r['last_attempt_s'] if r.get('last_attempt_s') is not None else r['total_s'])
            dropped += r['attempts'] > 1
        elif m0 and r['total_s'] > 3 * m0:
            dropped += 1
        else:
            vals.append(r['total_s'])
    return {'median': med(vals), 'dropped': dropped}


def choose(summ, rules):
    local = [s for s in summ if s['arm'] == 'local' and s['fits'] and s['offline_verified']]
    if not local:
        return None
    return sorted(local, key=lambda s: (-sum(c['sym'] == '✓' for c in s['cats'].values()), s['download_bytes'] or 0))[0]


def route(chosen, online, cat, rules):
    if not chosen:
        return '—'
    sym = chosen['cats'][cat]['sym']
    if sym == '✗' and online and online['cats'][cat]['n'] <= 2:
        return 'hard for both: a person does it'
    return {'✓': 'offline', '~': 'offline + human check', '✗': 'stronger model (confidential: redact or by hand)'}[sym]


def costs(s, cost, prices, meta_prices):
    out = {}
    if s['arm'] == 'local':
        w, e, lp = cost.get('power_watts_under_load'), cost.get('electricity_price_per_kwh'), cost.get('laptop_price')
        if w is not None:
            out['energy_kwh'] = w * s['busy_s'] / 3.6e6
            if e is not None:
                out['energy_cost'] = out['energy_kwh'] * e
        if lp is not None:
            out['depreciation_cost'] = lp / (cost['lifetime_years'] * cost['use_hours_per_year']) * s['busy_s'] / 3600
    else:
        p = (prices or {}).get(s['model']) or {}
        if p.get('input_per_mtok') is not None and p.get('output_per_mtok') is not None:
            out['usd'] = (s['tokens_in'] * p['input_per_mtok'] + s['tokens_out'] * p['output_per_mtok']) / 1e6
            out['checked_on'] = meta_prices.get('checked_on')
    return out


def gbs(b):
    return 'n/a' if b is None else f'{max(0, b) / GB:.1f} GB'


def secs(x):
    return f'{x:.1f} s' if x is not None else 'n/a'


def card_rows(summ, chosen, online, rules):
    head = ['Task category'] + [s['model'] + ('' if s['arm'] != 'local' or s['offline_verified'] else ' (NOT VERIFIED OFFLINE)')
                                for s in summ] + ['Decision (chosen local model)']
    rows = []
    for c in CATS:
        cells = []
        for s in summ:
            x = s['cats'][c]
            tag = ''
            if c == 'translate' and 'auto' in x['source']:
                tag = ' owner+auto' if 'owner' in x['source'] else ' auto'
            cells.append(f"{x['sym']} {x['n']}/{x['of']} (fa {x['fa'][0]}/{x['fa'][1]} · en {x['en'][0]}/{x['en'][1]}){tag}")
        rows.append([CAT_EN[c]] + cells + [route(chosen, online, c, rules)])
    rows.append(['All 30 tasks'] + [f"{s['passed']}/{s['of']} (fa {s['fa']}/15 · en {s['en']}/15)" for s in summ] + [''])
    rows.append(['Median time to first token'] + [secs(s['ttft_med']) if s['arm'] == 'local' else 'not streamed' for s in summ] + [''])
    rows.append(['Median total time per task'] + [secs(s['total_med']) for s in summ] + [''])
    rows.append(['Tokens per second (median)'] + [f"{s['tps_med']:.0f}" if s['tps_med'] else 'n/a' for s in summ] + [''])
    rows.append(['Peak memory (RSS / Ollama)'] + [f"{gbs(s['peak_rss'])} / {gbs(s['ps_size'])}" if s['arm'] == 'local' else '—' for s in summ] + [''])
    rows.append(['Swap growth during run'] + [gbs(s['swap_growth']) if s['arm'] == 'local' and s['swap_growth'] is not None else '—' for s in summ] + [''])
    rows.append(['On disk · quantization'] + [f"{gbs(s['download_bytes'])} · {s['quant']}" if s['arm'] == 'local' else 'cloud' for s in summ] + [''])
    rows.append(['Cold load (first request)'] + [secs(s['cold_load_s']) if s['arm'] == 'local' else '—' for s in summ] + [''])
    return head, rows


def lock_lines(summ, rules, lock_issues):
    s0 = next((s for s in summ if s['locks'].get('sha256')), None)
    if not s0:
        return ['Rule lock: no hashes recorded.']
    h = s0['locks']['sha256']
    commit = (s0['locks'].get('git') or {}).get('commit')
    out = [f"Rules written {rules.get('locked_on')} · sha256 at run: " + ' · '.join(f'{f} {v[:12]}' for f, v in h.items())
           + (f' · commit {commit}' if commit else ' · not committed when run')]
    if lock_issues:
        out.append('WARNING: built with --allow-changed-rules; these files changed since a run: ' + '; '.join(lock_issues))
    return out


def write_md(path, head, rows, meta, summ, demo, rules=None, lock_issues=()):
    title = ('DEMO — fake server and mock model, NOT a result · ' if demo else '') + 'Offline AI Capability Card · HMD-024'
    dev = meta.get('device', {})
    lines = [f'# {title}', '',
             f"Device: {dev.get('model', '?')} · {dev.get('chip', '?')} · {dev.get('memory_gb', '?')} GB · macOS {dev.get('macos', '?')} · "
             f"Ollama {meta.get('ollama_version', '?')} · run {meta.get('started', '?')[:10]}",
             'Offline verified before and after every local run: ' + ', '.join(f"{s['model']} {'yes' if s['offline_verified'] else 'NO'}" for s in summ if s['arm'] == 'local'),
             '', '| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    lines += ['| ' + ' | '.join(r) + ' |' for r in rows]
    lines += ['', '✓ 4–5 of 5 pass → keep offline · ~ 3 of 5 (or ✓ but median over 30 s) → offline + a person checks · ✗ 0–2 of 5 → stronger model.',
              '"auto" on translation = required-terms check only; the owner\'s blind sheet replaces it.',
              *lock_lines(summ, rules or {}, lock_issues),
              *(f"Online: {s['model']}, max_tokens {s['max_tokens']}, effort {s['effort']}, provider-default temperature; "
                f"{s['retry_rows']} row(s) with a retry left out of the median time." for s in summ if s['arm'] == 'online'),
              'Boundary: one laptop, 30 synthetic tasks, these models, this date. Offline is not the same as secure. Online timing includes the network.']
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


# ── PNGs (matplotlib optional) ─────────────────────────────────────────────────────────────────
SERIES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']   # dataviz reference palette, slots 1–4 (light surface)
SURFACE, INK, MUTED, AMBER = '#fcfcfb', '#0b0b0b', '#52514e', '#E8A33D'


def write_pngs(out, head, rows, summ, demo):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return ['matplotlib not installed: PNGs skipped (pip install matplotlib)']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.edgecolor': MUTED,
                         'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED})
    stamp = 'DEMO — not a result' if demo else 'HMD-024 · one laptop · 30 tasks'
    written = []
    # card
    fig, ax = plt.subplots(figsize=(4.2 + 3.1 * (len(head) - 1), 0.34 * (len(rows) + 2)), facecolor=SURFACE)
    ax.axis('off')
    tb = ax.table(cellText=rows, colLabels=head, loc='upper left', cellLoc='left', colLoc='left')
    tb.auto_set_font_size(False)
    tb.set_fontsize(10)
    tb.auto_set_column_width(list(range(len(head))))
    tb.scale(1, 1.45)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor('#d9d8d4')
        cell.set_facecolor(SURFACE if r else '#ecebe6')
        txt = cell.get_text().get_text()
        if r and txt.startswith('✓'):
            cell.set_facecolor('#fff3dc')
        if r == 0:
            cell.get_text().set_weight('bold')
    ax.set_title(('DEMO · ' if demo else '') + 'Offline AI Capability Card', loc='left', color=INK, fontsize=15, weight='bold')
    fig.text(0.01, 0.01, stamp + ' · ✓ keep offline  ~ offline + human check  ✗ stronger model', color=MUTED, fontsize=9)
    fig.savefig(out / 'capability-card.png', dpi=160, bbox_inches='tight', facecolor=SURFACE)
    plt.close(fig)
    written.append('capability-card.png')
    # quality: tasks passed per category, one bar per model (≤ 4 series)
    show = summ[:4]
    fig, ax = plt.subplots(figsize=(10, 5.2), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    h = 0.8 / len(show)
    for i, s in enumerate(show):
        ys = [k + i * h for k in range(len(CATS))]
        vals = [s['cats'][c]['n'] for c in CATS]
        ax.barh(ys, vals, height=h - 0.03, color=SERIES[i], label=s['model'])
        for y, v in zip(ys, vals):
            ax.text(v + 0.06, y, f'{v}/5', va='center', fontsize=9, color=INK)
    ax.set_yticks([k + 0.4 - h / 2 for k in range(len(CATS))], [CAT_EN[c] for c in CATS])
    ax.invert_yaxis()
    ax.set_xlim(0, 5.6)
    ax.set_xlabel('tasks passed (of 5 per category)')
    ax.axvline(4, color=AMBER, lw=1.5, ls='--')
    ax.text(4.03, -0.45, 'offline line (4/5)', color=MUTED, fontsize=9)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='x', color='#ecebe6')
    ax.set_axisbelow(True)
    ax.legend(loc='lower right', frameon=False, fontsize=9)
    ax.set_title(('DEMO · ' if demo else '') + 'Which tasks pass, by category', loc='left', color=INK, weight='bold')
    fig.savefig(out / 'quality.png', dpi=160, bbox_inches='tight', facecolor=SURFACE)
    plt.close(fig)
    written.append('quality.png')
    # speed + memory: three small multiples, one axis each
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), facecolor=SURFACE)
    panels = [('Median time to first token (s)', [s['ttft_med'] if s['arm'] == 'local' else None for s in show]),
              ('Median total time per task (s)', [s['total_med'] for s in show]),
              ('Peak memory, Ollama-reported (GB)', [(s['ps_size'] or 0) / GB if s['arm'] == 'local' else None for s in show])]
    for ax, (title, vals) in zip(axes, panels):
        ax.set_facecolor(SURFACE)
        for i, (s, v) in enumerate(zip(show, vals)):
            if v is None:
                ax.text(i, 0, 'n/a', ha='center', va='bottom', color=MUTED, fontsize=9)
                continue
            ax.bar(i, v, width=0.62, color=SERIES[i])
            ax.text(i, v, f'{v:.2f}' if v < 1 else f'{v:.1f}', ha='center', va='bottom', fontsize=9, color=INK)
        ax.set_xticks(range(len(show)), [s['model'].replace(':', ':\n', 1) for s in show], fontsize=8)
        ax.set_title(title, loc='left', fontsize=11, color=INK)
        ax.set_axisbelow(True)
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', color='#ecebe6')
        if 'memory' in title:
            ax.axhline(8, color=AMBER, lw=1.5, ls='--')
            ax.text(-0.4, 8.1, 'all of the laptop\'s RAM: 8 GB', color=MUTED, fontsize=8)
            ax.set_ylim(0, 9)
    fig.suptitle(('DEMO · ' if demo else '') + 'Speed and memory · online time includes the network; online is not streamed',
                 x=0.01, ha='left', color=INK, weight='bold')
    fig.savefig(out / 'speed-memory.png', dpi=160, bbox_inches='tight', facecolor=SURFACE)
    plt.close(fig)
    written.append('speed-memory.png')
    return written
