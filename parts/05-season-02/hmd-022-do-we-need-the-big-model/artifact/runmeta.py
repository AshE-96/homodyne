"""HMD-022 · run bookkeeping: the dollar bound before [y/N], the design fingerprints, and per-model call health.

- Dollars before a run: real prices from prices.json when filled; otherwise a CONSERVATIVE UPPER BOUND from the
  `fallback` block (deliberately high prices, NOT an official price), with every call assumed to use its full output
  cap. Same convention as HMD-021.
- Fingerprints: sha256 of the files that define the experiment (graders, routers, task set, protocol) plus the git
  commit. `run` stores them in meta.json; `report` flags any file that changed after the run started.
- Call health: refused, fallback, truncated and unparsed replies per model, and how the small model's confidence was
  written (0-100, "85%", 0.85, missing), so a confidence router built on messy numbers is visible.
"""
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTERED = ('grade.py', 'routers.py', 'tasks/tasks.json', 'protocol.md')
REFUSAL_STOPS = {'refusal', 'safety', 'prohibited_content', 'blocklist', 'spii', 'content_filter'}
TRUNCATED_STOPS = {'max_tokens', 'length'}


# ── dollars before the run ────────────────────────────────────────────────────────────────────
def dollar_lines(tokens_in, calls, models, prices, max_tokens, out_typical=150):
    """tokens_in / calls: {'main': n, 'small': n}; models: {'main': 'provider:model', 'small': ...}."""
    lines = []
    known = prices.get('models', {})
    fb = prices.get('fallback', {})
    total_real, total_upper, all_real = 0.0, 0.0, True
    for role in ('small', 'main'):
        mid = models.get(role)
        if not mid:
            continue
        provider = mid.split(':', 1)[0]
        if provider in ('mock', 'ollama'):
            lines.append(f'{role:5} {mid}: no API cost')
            continue
        p = known.get(mid, {})
        if p.get('input_per_mtok') is not None and p.get('output_per_mtok') is not None:
            usd = (tokens_in[role] * p['input_per_mtok'] + calls[role] * out_typical * p['output_per_mtok']) / 1e6
            total_real += usd
            lines.append(f'{role:5} {mid}: ~${usd:,.2f} at prices checked {prices.get("checked_on")} '
                         f'(~{out_typical} output tokens per reply; no caching or batch discount)')
        else:
            all_real = False
        fp = fb.get(provider) or fb.get('default') or {}
        if fp.get('input_per_mtok') is not None:
            up = (tokens_in[role] * fp['input_per_mtok'] + calls[role] * max_tokens * fp['output_per_mtok']) / 1e6
            total_upper += up
            lines.append(f'{role:5} {mid}: UPPER BOUND ≤ ${up:,.2f} (CONSERVATIVE UPPER BOUND, NOT AN OFFICIAL PRICE: '
                         f'${fp["input_per_mtok"]}/${fp["output_per_mtok"]} per M tokens from prices.json fallback, set '
                         f'{fb.get("set_on")}; every call at its {max_tokens}-token output cap)')
    if total_upper:
        lines.append(f'TOTAL UPPER BOUND ≤ ${total_upper:,.2f} (CONSERVATIVE UPPER BOUND, NOT AN OFFICIAL PRICE)'
                     + (f' · estimate at real prices ~${total_real:,.2f}' if all_real and total_real else
                        ' · fill prices.json for a real estimate'))
    return lines


# ── fingerprints ─────────────────────────────────────────────────────────────────────────────
def fingerprints():
    out = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in REGISTERED}
    try:
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=HERE, capture_output=True, text=True, timeout=10)
        dirty = subprocess.run(['git', 'status', '--porcelain', '--', '.'], cwd=HERE, capture_output=True, text=True,
                               timeout=10)
        if head.returncode:
            out['commit'] = 'uncommitted (not a git checkout)'
        else:
            changed = [ln for ln in dirty.stdout.splitlines() if not re.search(r'(^|/)(runs|results)/', ln)]
            out['commit'] = head.stdout.strip() + (' + uncommitted changes in artifact/' if changed else '')
    except (OSError, subprocess.SubprocessError):
        out['commit'] = 'unknown (git unavailable)'
    return out


def fingerprint_lines(fp):
    return [f'commit {fp.get("commit")}'] + [f'  sha256 {k:18} {fp[k]}' for k in REGISTERED if k in fp]


def mismatches(fp_run, fp_now):
    """Registered files whose hash differs between the run and now (the commit line is informational)."""
    return [k for k in REGISTERED if fp_run.get(k) and fp_run.get(k) != fp_now.get(k)]


# ── call health ──────────────────────────────────────────────────────────────────────────────
def classify(call):
    stop = str(call.get('stop_reason') or '').lower()
    return {'refused': stop in REFUSAL_STOPS or bool(call.get('refusal_category')),
            'truncated': stop in TRUNCATED_STOPS,
            'fallback': bool(call.get('fell_back')),
            'no_json': not call.get('json_ok', True)}


def call_health(records):
    """records: the rows of items.jsonl. Returns per-role counts and the small model's confidence formats."""
    out = {}
    for role in ('small', 'main'):
        calls = [c for r in records for c in r['calls'].values() if c['role'] == role]
        k = Counter()
        for c in calls:
            for name, v in classify(c).items():
                k[name] += v
        served = Counter(c.get('model_served') for c in calls)
        out[role] = {'calls': len(calls), **{n: k[n] for n in ('refused', 'fallback', 'truncated', 'no_json')},
                     'served': dict(served)}
    firsts = [r['calls'].get('small1', {}) for r in records if 'small1' in r['calls']]
    flags = Counter(c.get('conf_flag', 'ok' if c.get('confidence') is not None else 'missing') for c in firsts)
    bins = Counter()
    for c in firsts:
        v = c.get('confidence')
        if v is not None:
            bins['<50' if v < 50 else '50-79' if v < 80 else '80-89' if v < 90 else '90-99' if v < 100 else '100'] += 1
    usable = sum(v for f, v in flags.items() if f in ('ok', 'percent_string', 'unit_scale'))
    out['confidence'] = {'n': len(firsts), 'flags': dict(flags), 'bins': dict(bins),
                         'unparsed_share': 1 - usable / len(firsts) if firsts else 0.0}
    return out


def health_lines(h):
    lines = ['call health (refused = the model declined; fallback = another model answered; truncated = hit the cap):']
    for role in ('small', 'main'):
        x = h[role]
        lines.append(f'  {role:5} calls {x["calls"]:4} · refused {x["refused"]} · fallback {x["fallback"]} · '
                     f'truncated {x["truncated"]} · no JSON {x["no_json"]} · served {json.dumps(x["served"])}')
    c = h['confidence']
    lines.append(f'  small confidence (first sample, n = {c["n"]}): formats {json.dumps(c["flags"])} · '
                 f'unparsed share {c["unparsed_share"]:.1%} · distribution {json.dumps(c["bins"])}')
    return lines
