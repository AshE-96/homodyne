#!/usr/bin/env python3
"""HMD-K01 · konkur_run.py — five models sit Konkur at the same moment, one question per call.

    python3 konkur_run.py plan                         # calls, tokens, $ UPPER BOUND per model; no network
    python3 konkur_run.py run --limit 10               # paid pilot: plan, then [y/N]; 10 questions per model
    python3 konkur_run.py run                          # full run (resumable: run it again after a crash)
    python3 konkur_run.py run --mock --synthetic       # no key, no network: mock models on synthetic questions
    python3 konkur_run.py report [--run NAME]          # tables, contamination check, rank ESTIMATE, spoken lines
    python3 konkur_run.py --selftest                   # keys unset, temp folder, < 30 s

Models: slots in models.json (gemini, claude, gpt, open1, open2); fill the exact IDs at run time, or pass
--model claude=anthropic:claude-opus-5-5 (repeatable). The IDs actually used and the model each provider says it served
are recorded per call. Questions: private/konkur/questions/*.json (konkur_prep.py validate must pass).
Raw replies, events and the answer cache go to private/konkur/runs/<run>/ (git-ignored); report writes only
aggregates without question text to artifact/results/<run>/.

Protocol (protocol.md): same Persian system prompt, JSON schema {choice: 1-4 | null}, figures as images, provider
default sampling, Claude effort medium, every model starts at the same instant (a barrier), each model answers its
questions in booklet order, one at a time.
"""
import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
import threading
import time
from pathlib import Path

import kcore
import llm
import rank_estimate
import runmeta

MODELS_FILE = kcore.HERE / 'models.json'
PRICES_FILE = kcore.HERE / 'prices.json'
RESULTS = kcore.HERE / 'results'
REGISTERED = ('kcore.py', 'konkur_run.py', 'protocol.md', 'models.json')
os.environ.setdefault('HOMODYNE_HTTP_TIMEOUT', '900')   # long reasoning replies; llm.py's default is 180 s
MOCK_STYLE = {'gemini': (0.80, 0.04, 9, 3.1), 'claude': (0.78, 0.08, 11, 2.6), 'gpt': (0.82, 0.03, 14, 2.9),
              'open1': (0.55, 0.02, 6, 1.9), 'open2': (0.62, 0.10, 7, 2.2)}   # p_right, p_blank, sec, chars/token


# ── setup ────────────────────────────────────────────────────────────────────────────────────────
def slots(args):
    cfg = json.loads(MODELS_FILE.read_text(encoding='utf-8'))['slots']
    over = dict(m.split('=', 1) for m in (args.model or []))
    out = []
    for s in cfg:
        spec = 'mock:' + s['slot'] if args.mock else over.get(s['slot'], s.get('model'))
        out.append({'slot': s['slot'], 'label': s['label'], 'model': spec,
                    'no_schema': bool(s.get('no_schema'))})   # per slot, only if the pilot showed it rejects the schema
    missing = [s['slot'] for s in out if not s['model']]
    if missing:
        sys.exit(f'no model ID for slot(s) {missing}: fill models.json or pass --model SLOT=provider:model '
                 f'(protocol.md §1: choose the current flagship on run day and write it down)')
    return out


def questions(args):
    if args.synthetic:
        import konkur_prep
        qs = [q for d in konkur_prep.synthetic(per_subject=args.per_subject) for q in d['questions']]
    else:
        files = kcore.question_files(args.exam)
        if not files:
            sys.exit(f'no question files in {kcore.private_dir() / "questions"} (prep-fa.md §2, konkur_prep.py)')
        for f in files:
            errs = kcore.validate_exam(json.loads(f.read_text(encoding='utf-8')))
            if errs:
                sys.exit(f'{f.name} does not validate ({len(errs)} problems): python3 konkur_prep.py validate')
        qs = kcore.load_exams(files)
    if args.limit:                     # pilot: spread over exams and subjects, booklet order kept
        by = {}
        for q in qs:
            by.setdefault((q['year'], q['group'], q['subject']), []).append(q)
        pick, i = [], 0
        while len(pick) < min(args.limit, len(qs)):
            for k in sorted(by):
                if i < len(by[k]) and len(pick) < args.limit:
                    pick.append(by[k][i])
            i += 1
        qs = sorted(pick, key=lambda q: (q['year'], q['group'], q['number']))
    return qs


def run_dir(args, sl):
    name = args.run or ('mock' if args.mock else hashlib.sha256('|'.join(
        s['model'] + ('#no-schema' if s.get('no_schema') else '') for s in sl).encode()).hexdigest()[:8])
    if args.synthetic and not name.startswith('synthetic'):
        name = 'synthetic-' + name
    return kcore.private_dir() / 'runs' / name


def fingerprints():
    out = {n: hashlib.sha256((kcore.HERE / n).read_bytes()).hexdigest() for n in REGISTERED}
    try:
        r = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=kcore.HERE, capture_output=True, text=True, timeout=10)
        d = subprocess.run(['git', 'status', '--porcelain', '--', '.'], cwd=kcore.HERE, capture_output=True, text=True,
                           timeout=10)
        out['commit'] = r.stdout.strip() + (' + uncommitted changes in artifact/' if d.stdout.strip() else '')
    except (OSError, subprocess.SubprocessError):
        out['commit'] = 'unknown'
    return out


def plan_lines(sl, qs):
    sys_chars = len(kcore.SYSTEM)
    chars = sum(len(kcore.prompt_for(q)) + sys_chars for q in qs)
    images = sum(len(q.get('figures', [])) for q in qs)
    tok_in = int(chars / 1.5 + images * 1600)          # deliberately high: Persian ~1.5 chars/token, 1600 per image
    prices = json.loads(PRICES_FILE.read_text(encoding='utf-8'))
    lines = [f'{len(qs)} questions × {len(sl)} models = {len(qs) * len(sl)} calls · {chars:,} input characters per model '
             f'· {images} figure images · ≤ ~{tok_in:,} input tokens per model (rough, deliberately high)']
    for s in sl:
        lines += runmeta.dollar_lines({'main': tok_in}, {'main': len(qs)}, {'main': s['model']}, prices,
                                      kcore.MAX_TOKENS, out_typical=3000)
    return lines


# ── the exam engine (also used by konkur_live.py) ────────────────────────────────────────────────
def mock_reply(slot, q):
    p_right, p_blank, _, _ = MOCK_STYLE.get(slot, (0.6, 0.05, 8, 2.5))
    r = random.Random(f'{slot}|{q["id"]}').random()
    key = q.get('key') or [1]
    if r < p_blank:
        return {'choice': None}
    if r < p_blank + p_right:
        return {'choice': key[0]}
    return {'choice': [c for c in (1, 2, 3, 4) if c not in key][int(r * 1000) % (4 - len(key))]}


def mock_measure(slot, q, prompt):
    _, _, sec, cpt = MOCK_STYLE.get(slot, (0.6, 0.05, 8, 2.5))
    r = random.Random(f'm|{slot}|{q["id"]}')
    lat = sec * r.lognormvariate(0, 0.45)
    return {'latency_s': round(lat, 2), 'input_tokens': int((len(prompt) + len(kcore.SYSTEM)) / cpt),
            'output_tokens': int(lat * 90), 'reasoning_tokens': int(lat * 80)}


def answer_one(s, q, out, use_schema=True, delay=0.0):
    prompt = kcore.prompt_for(q)
    mock = s['model'].startswith('mock:')
    t0 = time.monotonic()
    res = llm.call(prompt, system=kcore.SYSTEM, images=kcore.figure_paths(q), model=s['model'],
                   max_tokens=kcore.MAX_TOKENS, cache_dir=out / 'cache' / s['slot'],
                   schema=kcore.SCHEMA if use_schema and not s.get('no_schema') else None,
                   mock=lambda p, schema=None: json.dumps(mock_reply(s['slot'], q)))
    choice, flag = kcore.parse_choice(res.text)
    label = kcore.label_for(q, choice)
    ex = res.extra or {}
    row = {'qid': q['id'], 'year': q['year'], 'group': q['group'], 'subject': q['subject'], 'number': q['number'],
           'slot': s['slot'], 'model': s['model'], 'model_served': res.model_served, 'choice': choice, 'flag': flag,
           'label': label, 'latency_s': round(res.latency_s, 3), 'attempts': ex.get('attempts', 1),
           'last_attempt_s': ex.get('last_attempt_s', round(res.latency_s, 3)), 'input_tokens': res.input_tokens,
           'output_tokens': res.output_tokens,
           'reasoning_tokens': ex.get('reasoning_tokens', ex.get('thoughts_tokens')),
           'input_chars': len(prompt) + len(kcore.SYSTEM), 'output_chars': len(res.text or ''),
           'usd_reported': ex.get('cost_usd'), 'stop_reason': res.stop_reason, 'refusal': ex.get('refusal_category'),
           'fell_back': res.fell_back, 'upstream': ex.get('upstream_provider'), 'cached': res.cached, 'n_images': len(q.get('figures', [])), 'mock': mock,
           'reply': (res.text or '')[:400]}
    if mock:
        row.update(mock_measure(s['slot'], q, prompt))
        if delay:
            time.sleep(max(0.0, row['latency_s'] * delay - (time.monotonic() - t0)))
    return row


def load_done(path):
    done = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.strip():
                r = json.loads(line)
                done[r['qid']] = r
    return done


def run_exam(sl, qs, out, on_event=None, use_schema=True, delay=0.0):
    """One thread per model, all released together; each answers in booklet order. Appends rows to <slot>.jsonl
    (resume = skip questions already there) and events to events-<n>.jsonl (for konkur_live.py --replay)."""
    out.mkdir(parents=True, exist_ok=True)
    n = len(list(out.glob('events-*.jsonl'))) + 1
    ev_path, lock, barrier = out / f'events-{n}.jsonl', threading.Lock(), threading.Barrier(len(sl))
    t_start = [None]

    def emit(ev):
        with lock:
            ev['t'] = round(time.monotonic() - (t_start[0] or time.monotonic()), 3)
            with ev_path.open('a', encoding='utf-8') as f:
                f.write(json.dumps(ev, ensure_ascii=False) + '\n')
        if on_event:
            on_event(ev)

    meta = {'slots': sl, 'questions': [{'qid': q['id'], 'year': q['year'], 'group': q['group'],
                                        'subject': q['subject'], 'number': q['number']} for q in qs]}
    t_start[0] = time.monotonic()
    emit({'type': 'start', 'session': n, 'wall': time.strftime('%Y-%m-%d %H:%M:%S'), **meta})
    errors = {}

    def worker(s):
        path = out / f'{s["slot"]}.jsonl'
        done = load_done(path)
        barrier.wait()
        for i, q in enumerate(qs):
            if q['id'] in done:
                r = done[q['id']]
                emit({'type': 'answer', 'resumed': True, **{k: v for k, v in r.items() if k != 'reply'}, 'i': i})
                continue
            emit({'type': 'ask', 'slot': s['slot'], 'qid': q['id'], 'subject': q['subject'], 'year': q['year'],
                  'group': q['group'], 'number': q['number'], 'i': i})
            try:
                r = answer_one(s, q, out, use_schema, delay)
            except Exception as e:            # LLMError, or anything else: never let one slot's thread die silently
                errors[s['slot']] = errors.get(s['slot'], 0) + 1
                emit({'type': 'error', 'slot': s['slot'], 'qid': q['id'], 'error': str(e)[:300], 'i': i})
                continue
            with lock:
                with path.open('a', encoding='utf-8') as f:
                    f.write(json.dumps(r, ensure_ascii=False) + '\n')
            emit({'type': 'answer', **{k: v for k, v in r.items() if k != 'reply'}, 'i': i})
        emit({'type': 'done', 'slot': s['slot']})

    threads = [threading.Thread(target=worker, args=(s,), daemon=True) for s in sl]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    emit({'type': 'end'})
    return errors


def cmd_plan(args):
    sl, qs = slots(args), questions(args)
    print('\n'.join(plan_lines(sl, qs)))
    return 0


def cmd_run(args):
    sl, qs = slots(args), questions(args)
    out = run_dir(args, sl)
    print('\n'.join(plan_lines(sl, qs)) + f'\n→ {out}')
    if not args.mock and not args.yes and input('This spends API money. Continue? [y/N] ').strip().lower() != 'y':
        print('stopped')
        return 1
    out.mkdir(parents=True, exist_ok=True)
    prev = json.loads((out / 'meta.json').read_text()) if (out / 'meta.json').exists() else {}
    fp = prev.get('fingerprints') or fingerprints()
    changed = [k for k in REGISTERED if fp.get(k) != fingerprints().get(k)]
    if changed:
        print('WARNING: registered files changed since this run started: ' + ', '.join(changed))
    meta = {**prev, 'slots': sl, 'first_started': prev.get('first_started', time.strftime('%Y-%m-%d %H:%M')),
            'last_started': time.strftime('%Y-%m-%d %H:%M'), 'fingerprints': fp, 'changed_at_resume': changed,
            'system': kcore.SYSTEM, 'schema': kcore.SCHEMA if not args.no_schema else None,
            'max_tokens': kcore.MAX_TOKENS, 'http_timeout_s': os.environ.get('HOMODYNE_HTTP_TIMEOUT'), 'effort': os.environ.get('HOMODYNE_EFFORT', 'medium'),
            'temperature': os.environ.get('HOMODYNE_TEMPERATURE'), 'no_fallback': bool(os.environ.get('HOMODYNE_NO_FALLBACK')),
            'mock': args.mock, 'synthetic': args.synthetic, 'limit_pilot': args.limit, 'n_questions': len(qs)}
    (out / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    errors = run_exam(sl, qs, out, use_schema=not args.no_schema,
                      on_event=lambda e: e['type'] == 'done' and print(f'  {e["slot"]} finished at {e["t"]:.0f} s'))
    print(f'errors (not answered; run again to retry): {errors}' if errors else 'all questions answered')
    print(f'next: python3 {Path(__file__).name} report --run {out.name}')
    return 0


# ── report ───────────────────────────────────────────────────────────────────────────────────────
def load_rows(out):
    return [r for p in sorted(out.glob('*.jsonl')) if not p.name.startswith('events') for r in load_done(p).values()]


def usd(r, prices):
    if r.get('usd_reported') is not None:
        return r['usd_reported']
    p = prices.get('models', {}).get(r['model'], {})
    if p.get('input_per_mtok') is None or p.get('output_per_mtok') is None:
        return None
    return (r['input_tokens'] * p['input_per_mtok'] + r['output_tokens'] * p['output_per_mtok']) / 1e6


def summarize(rows, prices):
    labels = [r['label'] for r in rows]
    scored = [x for x in labels if x is not None]
    ci = kcore.mean_ci([kcore.item_value(x) for x in scored])
    dollars = [usd(r, prices) for r in rows]
    lat_ok = [r['latency_s'] for r in rows if (r.get('attempts') or 1) == 1 and not r.get('cached')] or \
             [r['latency_s'] for r in rows]
    return {'n': len(scored), 'right': scored.count('correct'), 'wrong': scored.count('wrong'),
            'blank': scored.count('abstain'), 'unparsed': sum(r['flag'] == 'unparsed' for r in rows),
            'accuracy': 100 * scored.count('correct') / len(scored) if scored else None,
            'percent': kcore.konkur_percent(labels),
            'ci95': None if not ci else [round(100 * ci[1], 1), round(100 * ci[2], 1)], 'latency_total_s': round(sum(r['latency_s'] for r in rows), 1),
            'latency_median_s': kcore.median(lat_ok), 'retried': sum((r.get('attempts') or 1) > 1 for r in rows),
            'in_tok': sum(r['input_tokens'] for r in rows), 'out_tok': sum(r['output_tokens'] for r in rows),
            'reasoning_tok': sum(r.get('reasoning_tokens') or 0 for r in rows),
            'reasoning_reported': sum(r.get('reasoning_tokens') is not None for r in rows),
            'in_chars': sum(r['input_chars'] for r in rows), 'out_chars': sum(r['output_chars'] for r in rows),
            'usd': None if any(d is None for d in dollars) else round(sum(dollars), 4),
            'refused': sum(bool(r.get('refusal')) for r in rows), 'fell_back': sum(bool(r.get('fell_back')) for r in rows),
            'truncated': sum(str(r.get('stop_reason')).lower() in ('max_tokens', 'length') for r in rows),
            'served': sorted({r['model_served'] for r in rows}),
            'upstream': sorted({r['upstream'] for r in rows if r.get('upstream')})}


def build_report(out, prices):
    rows, meta = load_rows(out), json.loads((out / 'meta.json').read_text(encoding='utf-8'))
    rep = {'run': out.name, 'meta': {k: meta.get(k) for k in ('slots', 'first_started', 'mock', 'synthetic',
                                                               'limit_pilot', 'n_questions', 'effort', 'fingerprints')},
           'prices_checked_on': prices.get('checked_on'), 'by_subject': [], 'by_exam': [], 'contamination': [],
           'tokens_per_kchar': {}, 'karnameh': []}
    for s in meta['slots']:
        mine = [r for r in rows if r['slot'] == s['slot']]
        rep['overall_' + s['slot']] = summarize(mine, prices)
        for (y, g) in sorted({(r['year'], r['group']) for r in mine}):
            ex = [r for r in mine if (r['year'], r['group']) == (y, g)]
            rep['by_exam'].append({'slot': s['slot'], 'year': y, 'group': g, **summarize(ex, prices)})
            pcts = {}
            for subj in sorted({r['subject'] for r in ex}):
                sub = summarize([r for r in ex if r['subject'] == subj], prices)
                rep['by_subject'].append({'slot': s['slot'], 'year': y, 'group': g, 'subject': subj, **sub})
                pcts[subj] = sub['percent']
            rep['karnameh'].append({'slot': s['slot'], 'year': y, 'group': g, 'percents': pcts,
                                    'estimate': rank_estimate.estimate(g, y, pcts)})
        for g in sorted({r['group'] for r in mine}):
            new = [kcore.item_value(r['label']) for r in mine if r['group'] == g and r['year'] == 1405 and r['label']]
            old = [kcore.item_value(r['label']) for r in mine if r['group'] == g and r['year'] < 1405 and r['label']]
            d = kcore.bootstrap_diff(new, old)
            if d:
                rep['contamination'].append({'slot': s['slot'], 'group': g, 'n_1405': len(new), 'n_before': len(old),
                                             'diff_pp': round(100 * d[0], 1), 'ci95_pp': [round(100 * d[1], 1),
                                                                                         round(100 * d[2], 1)]})
        text_only = [r for r in mine if not r['n_images']]
        if text_only:
            rep['tokens_per_kchar'][s['slot']] = round(1000 * sum(r['input_tokens'] for r in text_only)
                                                       / sum(r['input_chars'] for r in text_only), 1)
    tot = sorted(meta['slots'], key=lambda s: -(rep['overall_' + s['slot']]['percent'] or -999))
    if len(tot) > 1:                       # paired: the same questions, leader minus runner-up
        a, b = ({r['qid']: kcore.item_value(r['label']) for r in rows if r['slot'] == s['slot'] and r['label']}
                for s in tot[:2])
        d = kcore.mean_ci([a[q] - b[q] for q in sorted(set(a) & set(b))])
        if d:
            rep['leader_vs_second'] = {'leader': tot[0]['slot'], 'second': tot[1]['slot'], 'diff_pp': round(100 * d[0], 1),
                                       'ci95_pp': [round(100 * d[1], 1), round(100 * d[2], 1)],
                                       'separated': d[1] > 0 or d[2] < 0}
    return rep


def pp(x, nd=1):
    return '—' if x is None else f'{x:.{nd}f}'


def render(rep):
    m = rep['meta']
    head = '**MOCK / SYNTHETIC — NOT A RESULT**\n\n' if m['mock'] or m['synthetic'] else ''
    lines = [f'# HMD-K01 · run {rep["run"]}', '', head + f'started {m["first_started"]} · questions {m["n_questions"]}'
             + (f' · PILOT --limit {m["limit_pilot"]}' if m['limit_pilot'] else '') + f' · effort {m["effort"]} · '
             f'prices {rep["prices_checked_on"] or "not filled (no $)"}', '',
             '| model | served | درصد (−1/3) [95% CI] | accuracy | right/wrong/blank | unparsed | total s | median s | in tok | '
             'out tok | reasoning | in chars | $ | refused/fallback/truncated |', '|' + '---|' * 14]
    for s in m['slots']:
        o = rep['overall_' + s['slot']]
        lines.append(f'| {s["label"]} `{s["model"]}`' + (' (no schema)' if s.get('no_schema') else '')
                     + f' | {", ".join(o["served"])}' + (f' via {", ".join(o["upstream"])}' if o.get('upstream') else '') + f' | {pp(o["percent"])} {o["ci95"]} | {pp(o["accuracy"])} '
                     f'| {o["right"]}/{o["wrong"]}/{o["blank"]} | {o["unparsed"]} | {o["latency_total_s"]} | '
                     f'{pp(o["latency_median_s"])} | {o["in_tok"]:,} | {o["out_tok"]:,} | {o["reasoning_tok"]:,} '
                     f'({o["reasoning_reported"]} calls reported) | {o["in_chars"]:,} | {pp(o["usd"], 2)} | '
                     f'{o["refused"]}/{o["fell_back"]}/{o["truncated"]} |')
    lv = rep.get('leader_vs_second')
    if lv:
        lines += ['', f'Leader vs runner-up on the same questions (paired): {lv["leader"]} − {lv["second"]} = '
                  f'{lv["diff_pp"]:+} points [{lv["ci95_pp"][0]:+}, {lv["ci95_pp"][1]:+}] → '
                  + ('separated' if lv['separated'] else 'TOO CLOSE TO CALL')]
    lines += ['', '## Per exam and subject (درصد with −1/3)', '', '| model | year | group | subject | n | درصد | accuracy '
              '| blank | median s | out tok | $ |', '|' + '---|' * 11]
    for r in rep['by_subject']:
        lines.append(f'| {r["slot"]} | {r["year"]} | {r["group"]} | {r["subject"]} | {r["n"]} | {pp(r["percent"])} | '
                     f'{pp(r["accuracy"])} | {r["blank"]} | {pp(r["latency_median_s"])} | {r["out_tok"]:,} | {pp(r["usd"], 3)} |')
    lines += ['', '## Contamination check: 1405 (after most cutoffs) minus 1403+1404, same group', '',
              'Per-question points (1 / 0 / −1/3), 95% bootstrap interval over questions. A drop can also mean 1405 '
              'was simply harder: this check cannot separate the two (protocol.md §6).', '']
    lines += [f'- {c["slot"]} · {c["group"]}: {c["diff_pp"]:+} points of درصد [{c["ci95_pp"][0]:+}, {c["ci95_pp"][1]:+}] '
              f'(n = {c["n_1405"]} vs {c["n_before"]})' for c in rep['contamination']]
    lines += ['', '## Input tokens per 1000 characters (text-only questions; identical prompts)', '']
    lines += [f'- {k}: {v}' for k, v in rep['tokens_per_kchar'].items()]
    lines += ['', '## کارنامه (ESTIMATE, see rank_estimate.py)', '']
    for k in rep['karnameh']:
        lines.append(f'- {k["slot"]} · {k["year"]} {k["group"]}: ' + ', '.join(f'{s} {pp(v)}' for s, v in k['percents'].items())
                     + f' → {k["estimate"]["summary_en"]}')
    return '\n'.join(lines) + '\n'


def fa_num(x, nd=1):
    """Spoken-style Persian number: Persian digits, «٫» decimal, «منفی» instead of a minus sign."""
    v = round(x, nd)
    t = kcore.fa(f'{abs(v):.{nd}f}'.rstrip('0').rstrip('.') if nd else str(abs(round(v)))).replace('.', '٫')
    return ('منفی ' + t) if v < 0 else t


def spoken(rep):
    """Persian lines for the [RUN] beats, filled with this run's numbers."""
    m, out = rep['meta'], []
    if m['mock'] or m['synthetic']:
        out.append('هشدار: این اجرا ساختگی (MOCK) است؛ این جمله‌ها را ضبط نکن.')
    best = sorted(m['slots'], key=lambda s: -(rep['overall_' + s['slot']]['percent'] or -999))
    fast = sorted(m['slots'], key=lambda s: rep['overall_' + s['slot']]['latency_total_s'])
    o = lambda s: rep['overall_' + s['slot']]
    out.append(f'[قاب ۸] بیشترین درصد کل: {best[0]["label"]} با حدود {fa_num(o(best[0])["percent"] or 0, 0)} درصد؛ '
               f'کمترین: {best[-1]["label"]} با حدود {fa_num(o(best[-1])["percent"] or 0, 0)} درصد.')
    lv = rep.get('leader_vs_second')
    if lv:
        out.append('[قاب ۸] ' + ('فاصلهٔ اول و دوم از بازهٔ اطمینان بیشتر است.' if lv['separated'] else
                                 'فاصلهٔ اول و دوم از بازهٔ اطمینان کمتر است: نزدیک‌تر از آنکه بشود برنده گفت.'))
    out.append(f'[قاب ۹] زودتر از همه {fast[0]["label"]} تمام کرد؛ دیرتر از همه {fast[-1]["label"]}.')
    for c in rep['contamination']:
        out.append(f'[قاب ۱۰] {c["slot"]} · {kcore.GROUPS[c["group"]]}: ۱۴۰۵ منهای ۱۴۰۳ و ۱۴۰۴ = '
                   f'{fa_num(c["diff_pp"])} درصد (بازهٔ ۹۵٪: {fa_num(c["ci95_pp"][0])} تا {fa_num(c["ci95_pp"][1])}).')
    return '\n'.join(out) + '\n'


def cmd_report(args):
    root = kcore.private_dir() / 'runs'
    runs = sorted(root.glob('*/meta.json'), key=lambda p: p.stat().st_mtime) if root.exists() else []
    if args.run:
        runs = [root / args.run / 'meta.json']
    if not runs or not runs[-1].exists():
        sys.exit('no run found; run first')
    out = runs[-1].parent
    rep = build_report(out, json.loads(PRICES_FILE.read_text(encoding='utf-8')))
    dest = Path(args.results or RESULTS) / out.name
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'report.md').write_text(render(rep), encoding='utf-8')
    (dest / 'summary.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    (dest / 'spoken-fa.txt').write_text(spoken(rep), encoding='utf-8')
    print(render(rep) if not args.quiet else '', f'→ {dest}', sep='\n')
    return 0


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        os.environ['KONKUR_PRIVATE'] = tmp
        try:
            base = ['--mock', '--synthetic', '--per-subject', '3', '--yes', '--run', 'synthetic-t']
            assert main(['run', *base, '--limit', '12']) == 0
            out = Path(tmp) / 'runs' / 'synthetic-t'
            assert all(len(load_done(out / f'{s}.jsonl')) == 12 for s in MOCK_STYLE), 'pilot: 12 per model'
            assert main(['run', *base]) == 0                                  # resume: only the rest is asked
            rows = load_rows(out)
            nq = sum(len(d['questions']) for d in __import__('konkur_prep').synthetic(per_subject=3))
            assert len(rows) == 5 * nq and len({(r['slot'], r['qid']) for r in rows}) == 5 * nq, 'resume duplicated rows'
            ev = [json.loads(x) for x in (out / 'events-2.jsonl').read_text().splitlines()]
            assert sum(bool(e['type'] == 'answer' and e.get('resumed')) for e in ev) == 60       # 12 per model, 5 models
            assert ev[0]['type'] == 'start' and ev[-1]['type'] == 'end'
            assert main(['report', '--run', 'synthetic-t', '--results', str(Path(tmp) / 'res'), '--quiet']) == 0
            rep = json.loads((Path(tmp) / 'res/synthetic-t/summary.json').read_text())
            assert rep['contamination'] and rep['karnameh'] and 'ESTIMATE' in rep['karnameh'][0]['estimate']['summary_en']
            assert 'MOCK' in (Path(tmp) / 'res/synthetic-t/report.md').read_text()
            g = rep['overall_gpt']
            assert g['n'] == nq and g['right'] + g['wrong'] + g['blank'] == nq and g['usd'] is None
            assert all(r['latency_s'] > 0 and r['input_tokens'] > 0 for r in rows)
            assert g['ci95'][0] < g['percent'] < g['ci95'][1] and 'separated' in rep['leader_vs_second']
            assert '[SYNTHETIC]' not in json.dumps(rep, ensure_ascii=False), 'results must not contain question text'
        finally:
            os.environ.pop('KONKUR_PRIVATE', None)
    lines = plan_lines([{'slot': 'x', 'label': 'X', 'model': 'openrouter:a/b'}],
                       [q for d in __import__('konkur_prep').synthetic(per_subject=1) for q in d['questions']])
    assert any('UPPER BOUND' in x for x in lines), lines
    print('konkur_run selftest passed (mock pilot, resume, events, report, no question text in results, $ bound)')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--selftest', action='store_true')
    sub = ap.add_subparsers(dest='cmd')
    for name in ('plan', 'run'):
        s = sub.add_parser(name)
        s.add_argument('--model', action='append', help='SLOT=provider:model (repeatable)')
        s.add_argument('--exam', action='append', help='only these question files, e.g. 1405-tajrobi')
        s.add_argument('--limit', type=int, help='pilot: this many questions per model, spread over subjects')
        s.add_argument('--mock', action='store_true', help='mock:<slot> models; no key, no network')
        s.add_argument('--synthetic', action='store_true', help='synthetic questions instead of private/konkur')
        s.add_argument('--per-subject', type=int, default=5)
        s.add_argument('--run', help='run folder name under private/konkur/runs/')
        s.add_argument('--yes', action='store_true', help='skip the [y/N] money prompt')
        s.add_argument('--no-schema', action='store_true', help='plain-text JSON instead of native schema decoding')
    s = sub.add_parser('report')
    s.add_argument('--run')
    s.add_argument('--results')
    s.add_argument('--quiet', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    return {'plan': cmd_plan, 'run': cmd_run, 'report': cmd_report}.get(args.cmd, lambda a: ap.print_help() or 0)(args)


if __name__ == '__main__':
    sys.exit(main())
