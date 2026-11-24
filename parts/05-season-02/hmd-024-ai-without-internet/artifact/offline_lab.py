#!/usr/bin/env python3
"""HMD-024 · Does AI really work without the internet? — Offline AI Capability Card.

30 fixed tasks (15 Persian, 15 English) on a laptop model through Ollama with the network really cut, then the
same tasks on an online model through tools/llm.py. Run from anywhere; paths are relative to this file.

    python3 offline_lab.py --selftest            # no Ollama, no key, no network use; < 60 s; output labelled DEMO
    python3 offline_lab.py plan                  # device, models, tasks, rules, what is filled in
    python3 offline_lab.py doctor                # is Ollama installed and running, which models are pulled
    python3 offline_lab.py check [--watch]       # the offline check alone (red → green on camera)
    python3 offline_lab.py run --local           # refuses unless the machine is offline; all models in models.json
    python3 offline_lab.py run --local --models qwen3.5:2b-q4_K_M --limit 3   # quick try
    python3 offline_lab.py run --online          # refuses unless online; estimate first, then asks y/N
    python3 offline_lab.py blind                 # blind sheet for the owner: translations and summaries
    python3 offline_lab.py report                # card (md + png), charts, Persian lines for the [RUN] beats

Results go to runs/<arm>-<model>/ (meta.json, results.jsonl) and results/ (card, charts, summary.json,
spoken-fa.txt). Nothing here installs anything or pulls a model.
"""
import argparse
import csv
import json
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(ROOT / 'tools'))

import graders  # noqa: E402
import offline_check  # noqa: E402
import locks  # noqa: E402
import ollama_client as oc  # noqa: E402
from task_bank import CATS, NOT_IN_TEXT, SYSTEM, TASKS, check_bank, prompt_hash  # noqa: E402

RUNS, RESULTS = HERE / 'runs', HERE / 'results'
OPTIONS = {'temperature': 0, 'seed': 42, 'num_ctx': 8192, 'num_predict': 1024}
ONLINE_MAX_TOKENS = 1024          # same cap as the local num_predict
MODELS = json.loads((HERE / 'models.json').read_text(encoding='utf-8'))


def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def slug(s):
    return re.sub(r'[^A-Za-z0-9._-]+', '-', s).strip('-')


def device():
    def sh(*cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout.strip()
        except Exception:
            return None
    mem = sh('sysctl', '-n', 'hw.memsize')
    return {'model': sh('sysctl', '-n', 'hw.model'), 'chip': sh('sysctl', '-n', 'machdep.cpu.brand_string'),
            'memory_gb': round(int(mem) / 2 ** 30) if mem and mem.isdigit() else None,
            'macos': sh('sw_vers', '-productVersion') or platform.platform(), 'python': platform.python_version()}


LOOPBACK = {'127.0.0.1', 'localhost', '::1'}


def loopback(url):
    from urllib.parse import urlsplit
    return (urlsplit(url).hostname or '') in LOOPBACK


class AttemptTimer:
    """Times each HTTP attempt tools/llm.py makes through urllib (Gemini, OpenAI-compatible), so the online
    latency can exclude retry back-off. The Anthropic SDK path does not use urllib: attempts stay unknown there."""

    def __enter__(self):
        import urllib.request as ur
        self._ur, self._orig, self.attempts = ur, ur.urlopen, []

        def timed(*a, **k):
            t = time.perf_counter()
            try:
                return self._orig(*a, **k)
            finally:
                self.attempts.append(time.perf_counter() - t)
        ur.urlopen = timed
        return self

    def __exit__(self, *exc):
        self._ur.urlopen = self._orig


def model_info(name):
    return next((m for m in MODELS['models'] if m['tag'] == name), {})


# ── run: local ─────────────────────────────────────────────────────────────────────────────────
def run_local(models, limit=None, base=None, checker=offline_check.check, runs_dir=RUNS, mem_match=None, demo=False,
              quiet=False):
    say = (lambda *a: None) if quiet else print
    target = base or oc.host()
    if not loopback(target):
        print(f'Refusing to run the local arm: Ollama host is {target}, not this machine. '
              'Unset OLLAMA_HOST (or set it to 127.0.0.1:11434). A model on another machine is not offline AI.')
        return 5
    offline, rows = checker()
    if not offline:
        offline_check.print_check(offline, rows)
        print('\nRefusing to run the local arm: this machine can still reach the internet.\n'
              'Turn off Wi-Fi first (and unplug any network cable), then run again.')
        return 3
    say(offline_check.banner(True, sys.stdout.isatty()))
    try:
        ver = oc.version(base)
        pulled = {m['name']: m for m in oc.tags(base)}
    except oc.OllamaError as e:
        print(f'{e}\nStart the Ollama app (or `ollama serve`), then run `python3 offline_lab.py doctor`.')
        return 4
    tasks = TASKS[:limit] if limit else TASKS
    for name in models:
        if name.endswith(':cloud') or name.endswith('-cloud'):
            print(f'{name}: a cloud model runs on Ollama\'s servers, not on this laptop. Skipped.')
            continue
        if name not in pulled:
            print(f'{name} is not pulled. While online: ollama pull {name}')
            continue
        info = oc.show(name, base)
        caps = info.get('capabilities') or []
        think = False if 'thinking' in caps else None
        out = Path(runs_dir) / f'local-{slug(name)}'
        out.mkdir(parents=True, exist_ok=True)
        from demo import SPOKEN
        meta = {'arm': 'local', 'model': name, 'spoken_fa': model_info(name).get('spoken_fa') or SPOKEN.get(name),
                'started': now(),
                'device': device(), 'ollama_version': ver, 'ollama_host': base or oc.host(),
                'digest': pulled[name].get('digest'), 'download_bytes': pulled[name].get('size'),
                'quantization': (info.get('details') or {}).get('quantization_level'),
                'parameter_size': (info.get('details') or {}).get('parameter_size'),
                'family': (info.get('details') or {}).get('family'), 'format': (info.get('details') or {}).get('format'),
                'capabilities': caps, 'think_sent': think, 'license_head': str(info.get('license', ''))[:120],
                'options': OPTIONS, 'system_prompt': SYSTEM, 'offline_before': True, 'offline_before_rows': rows,
                'offline_mid': [], 'demo': demo, 'tasks': len(tasks), 'locks': locks.record()}
        oc.unload(name, base)
        try:
            import psutil
            meta['swap_baseline_bytes'] = psutil.swap_memory().used
        except ImportError:
            meta['swap_baseline_bytes'] = None
        say(f'\n{name} · {meta["quantization"]} · {meta["parameter_size"]} · warm-up (cold load) …')
        warm = oc.chat_stream(name, SYSTEM, 'Reply with one word: ready', OPTIONS, think, base=base, mem_match=mem_match)
        meta['cold_load_s'] = warm['load_duration_s']
        meta['cold_first_token_s'] = warm['ttft_s']
        results = []
        with (out / 'results.jsonl').open('w', encoding='utf-8') as f:
            for i, t in enumerate(tasks, 1):
                row = {'task_id': t['id'], 'cat': t['cat'], 'lang': t['lang'], 'prompt_hash': prompt_hash(t)}
                try:
                    r = oc.chat_stream(name, SYSTEM, t['prompt'], OPTIONS, think, base=base, mem_match=mem_match)
                    row.update(r)
                    row['grade'] = graders.grade(t, r['text'])
                except oc.OllamaError as e:
                    row.update(error=str(e), grade={'pass': False, 'score': 0.0, 'why': 'error'})
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
                f.flush()
                results.append(row)
                mark = '✓' if row['grade']['pass'] else '✗'
                say(f'  {i:2}/{len(tasks)} {t["id"]:7} {mark} {row.get("total_s") or 0:6.1f}s  {row["grade"]["why"]}')
                if i % 10 == 0:
                    meta['offline_mid'].append(checker()[0])
        off_after, rows_after = checker()
        meta.update(offline_after=off_after, offline_after_rows=rows_after, finished=now())
        if not off_after or not all(meta['offline_mid']):
            print('WARNING: the network came back during this run; it is NOT verified offline. Re-run offline.')
        (out / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
        oc.unload(name, base)
        say(f'  → {out}')
    return 0


# ── run: online ────────────────────────────────────────────────────────────────────────────────
def estimate(tasks):
    fa = sum(len(SYSTEM + t['prompt']) / 2.5 for t in tasks if t['lang'] == 'fa')
    en = sum(len(SYSTEM + t['prompt']) / 4 for t in tasks if t['lang'] == 'en')
    return int(fa + en), len(tasks) * ONLINE_MAX_TOKENS


def run_online(limit=None, checker=offline_check.check, runs_dir=RUNS, ask=input, quiet=False):
    import llm
    from demo import mock_online
    say = (lambda *a: None) if quiet else print
    provider, name = llm.resolve('main')
    if provider != 'mock':
        offline, rows = checker()
        if offline:
            offline_check.print_check(offline, rows)
            print('\nThe online arm needs the internet. Turn Wi-Fi back on.')
            return 3
    tasks = TASKS[:limit] if limit else TASKS
    tin, tout_cap = estimate(tasks)
    model_id = f'{provider}:{name}'
    os.environ.setdefault('HOMODYNE_EFFORT', 'low')   # least hidden reasoning tools/llm.py offers (Claude only)
    prices = json.loads((HERE / 'prices.json').read_text(encoding='utf-8'))
    p = prices['models'].get(model_id) or {}
    say(f'{llm.describe()} · effort {os.environ["HOMODYNE_EFFORT"]}\n{len(tasks)} calls · rough input ≈ {tin:,} tokens '
        f'(Persian chars/2.5, English chars/4) + output up to {tout_cap:,} tokens (a cap, not expected)')
    if p.get('input_per_mtok') is not None and p.get('output_per_mtok') is not None:
        say(f'cost ceiling ≈ ${(tin * p["input_per_mtok"] + tout_cap * p["output_per_mtok"]) / 1e6:.2f} '
            f'(prices checked {prices.get("checked_on")})')
    else:
        fb = prices['fallback']
        say(f'no price for {model_id} in prices.json. UPPER BOUND with the deliberately high fallback '
            f'(${fb["input_per_mtok"]}/${fb["output_per_mtok"]} per M tokens, set {fb["set_on"]}, not a real price): '
            f'≈ ${(tin * fb["input_per_mtok"] + tout_cap * fb["output_per_mtok"]) / 1e6:.2f} at most')
    if provider != 'mock':
        if ask(f'Send {len(tasks)} requests to {model_id}? This may cost money. [y/N] ').strip().lower() != 'y':
            print('Cancelled. Nothing was sent.')
            return 1
    out = Path(runs_dir) / f'online-{slug(model_id)}'
    out.mkdir(parents=True, exist_ok=True)
    meta = {'arm': 'online', 'model': model_id, 'spoken_fa': 'سرویس آنلاین', 'started': now(), 'device': device(),
            'max_tokens': ONLINE_MAX_TOKENS, 'effort': os.environ.get('HOMODYNE_EFFORT'), 'system_prompt': SYSTEM,
            'demo': provider == 'mock', 'locks': locks.record(),
            'note': 'llm.py does not stream: total_s is request→full answer including the network; no time to first token. '
                    'Temperature is the provider default (llm.py does not set it); the local arm uses 0. '
                    'effort applies to Claude models only. last_attempt_s excludes retry back-off where attempts are known.'}
    with (out / 'results.jsonl').open('w', encoding='utf-8') as f:
        for i, t in enumerate(tasks, 1):
            row = {'task_id': t['id'], 'cat': t['cat'], 'lang': t['lang'], 'prompt_hash': prompt_hash(t)}
            try:
                with AttemptTimer() as at:
                    r = llm.call(t['prompt'], system=SYSTEM, max_tokens=ONLINE_MAX_TOKENS, cache_dir=out / 'cache',
                                 mock=mock_online)
                known = provider in ('gemini', 'openai', 'ollama') and not r.cached
                row.update(text=r.text, total_s=r.latency_s, input_tokens=r.input_tokens, output_tokens=r.output_tokens,
                           model_served=r.model_served, fell_back=r.fell_back, cached=r.cached, stop_reason=r.stop_reason,
                           attempts=len(at.attempts) if known else None,
                           last_attempt_s=at.attempts[-1] if known and at.attempts else None)
                row['grade'] = graders.grade(t, r.text)
            except llm.LLMError as e:
                row.update(error=str(e), grade={'pass': False, 'score': 0.0, 'why': 'error'})
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
            say(f'  {i:2}/{len(tasks)} {t["id"]:7} {"✓" if row["grade"]["pass"] else "✗"}  {row["grade"]["why"]}')
    meta['finished'] = now()
    (out / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    say(f'  → {out}')
    return 0


PREAMBLE = re.compile(r'^\s*(?:here(?:\'s| is)[^\n]{0,60}|sure[^\n]{0,40}|translation|summary|ترجمه|خلاصه)[^\n]{0,40}[:：]\s*\n?',
                      re.I)


def strip_preamble(text):
    """Remove code fences and a short leading 'Here is the translation:' style line, which can give a model away."""
    t = re.sub(r'^```[a-z]*\s*|\s*```$', '', str(text).strip())
    return PREAMBLE.sub('', t, count=1).strip()


# ── blind sheet ────────────────────────────────────────────────────────────────────────────────
def blind(runs_dir=RUNS, force=False, seed=24):
    from report import load_runs
    d = Path(runs_dir) / 'blind'
    keyd = Path(runs_dir) / '.key'          # kept out of the folder the owner opens while scoring
    if (d / 'sheet.csv').exists() and not force:
        print(f'{d / "sheet.csv"} exists (maybe already scored). Use --force to overwrite.')
        return 1
    items = []
    for run in load_runs(runs_dir):
        for tid, r in run['rows'].items():
            t = next(x for x in TASKS if x['id'] == tid)
            if t['cat'] in ('translate', 'summarise') and not r.get('error'):
                items.append((run['dir'].name, t, strip_preamble(r.get('text', ''))))
    random.Random(seed).shuffle(items)
    d.mkdir(parents=True, exist_ok=True)
    key = {}
    with (d / 'sheet.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['code', 'task', 'source', 'output', 'meaning_kept', 'numbers_names_kept', 'reads_naturally',
                    'adds_something_not_in_text'])
        for i, (run, t, text) in enumerate(items, 1):
            code = f'B{i:03d}'
            key[code] = [run, t['id']]
            src = t['prompt'].split('\n\n', 1)[-1]
            w.writerow([code, t['cat'], src, text, '', '', '', ''])
    keyd.mkdir(parents=True, exist_ok=True)
    (keyd / 'blind-key.json').write_text(json.dumps(key, indent=1), encoding='utf-8')
    print(f'{len(items)} items → {d / "sheet.csv"} (model names hidden; the key is in {keyd.name}/blind-key.json, '
          'outside the sheet folder: do not open it while scoring)\n'
          'Blind, but not perfectly: some models have a recognisable style.\n'
          'Translations: y/n in meaning_kept, numbers_names_kept, reads_naturally (all y = pass).\n'
          'Summaries: y/n in adds_something_not_in_text (y = fail). Leave a cell empty to keep the automatic grade.')
    return 0


# ── plan / doctor / report ─────────────────────────────────────────────────────────────────────
def plan():
    check_bank()
    dev = device()
    print(f'HMD-024 plan · {now()}\nDevice: {dev}\nOllama host: {oc.host()}\n')
    print('Local models (models.json, verified on ollama.com ' + MODELS['verified_on'] + '):')
    for m in MODELS['models']:
        print(f'  {m["tag"]:22} {m["download_gb"]:>4} GB  {m["quantization"]:7} {m["params"][:28]:28} {m["licence"][:40]}')
    print(f'  disk for all three ≈ {sum(m["download_gb"] for m in MODELS["models"]):.1f} GB (+ the Ollama app)\n')
    from collections import Counter
    c = Counter((t['cat'], t['lang']) for t in TASKS)
    print('Tasks: ' + ' · '.join(f'{k} fa {c[(k, "fa")]}/en {c[(k, "en")]}' for k in CATS))
    print(f'Local options: {OPTIONS} · think:false for models with the thinking capability')
    cost = json.loads((HERE / 'cost.json').read_text())
    prices = json.loads((HERE / 'prices.json').read_text())
    print(f'cost.json filled: laptop_price={cost["laptop_price"]} · watts={cost["power_watts_under_load"]} · '
          f'kWh price={cost["electricity_price_per_kwh"]}\nprices.json checked_on={prices["checked_on"]}')
    print('Rules locked: ' + json.loads((HERE / 'rules.json').read_text())['locked_on'])
    return 0


def doctor():
    ok = True
    exe = shutil.which('ollama') or ('/Applications/Ollama.app/Contents/Resources/ollama'
                                     if Path('/Applications/Ollama.app').exists() else None)
    print(f'ollama binary: {exe or "NOT FOUND"}')
    if not exe:
        ok = False
        print('  Install (while online), either:\n'
              '    1. download https://ollama.com/download/Ollama.dmg, open it, drag Ollama to Applications, open it once\n'
              '    2. or: curl -fsSL https://ollama.com/install.sh | sh\n'
              '  Needs macOS 14 Sonoma or newer (docs.ollama.com/macos).')
    try:
        print(f'server: {oc.host()} · version {oc.version()}')
        pulled = {m['name']: m for m in oc.tags()}
    except oc.OllamaError as e:
        ok = False
        pulled = {}
        print(f'server: not reachable ({e}). Open the Ollama app, or run `ollama serve` in another terminal.')
    for m in MODELS['models']:
        have = pulled.get(m['tag'])
        print(f'  {m["tag"]:22} ' + (f'pulled · {have["size"] / 1e9:.1f} GB · {have["details"].get("quantization_level")}'
                                     if have else f'MISSING → ollama pull {m["tag"]}   (~{m["download_gb"]} GB)'))
        ok &= bool(have)
    cloud = [n for n in pulled if n.endswith((':cloud', '-cloud'))]
    if cloud:
        print(f'  note: cloud models present ({", ".join(cloud)}); they run on Ollama\'s servers, not here.')
    print('  tip for recording: OLLAMA_NO_CLOUD=1 (or "disable_ollama_cloud": true in ~/.ollama/server.json) '
          'turns off Ollama\'s cloud features (docs.ollama.com/faq).')
    free = shutil.disk_usage(Path.home()).free / 1e9
    print(f'disk free in home: {free:.1f} GB (need ≈ {sum(m["download_gb"] for m in MODELS["models"]):.1f} GB for the models)')
    for mod in ('psutil', 'matplotlib'):
        try:
            __import__(mod)
            print(f'{mod}: ok')
        except ImportError:
            print(f'{mod}: missing (optional) → pip install {mod}')
    try:
        import llm
        print('online model: ' + llm.describe())
    except Exception as e:  # noqa: BLE001
        print(f'online model: {e}')
    print('\nREADY' if ok else '\nNOT READY: fix the lines above')
    return 0 if ok else 1


def cmd_report(runs_dir=RUNS, out_dir=RESULTS, demo=False, quiet=False, allow_changed=False):
    import lines_fa
    r = lines_fa.build(runs_dir, out_dir, demo=demo, allow_changed=allow_changed)
    if not quiet:
        print(('DEMO — NOT A RESULT\n' if demo else '') + ' | '.join(r['head']))
        for row in r['rows']:
            print(' | '.join(row))
        print(f'\nchosen local model: {r["chosen"] and r["chosen"]["model"]}')
        print(f'written: {r["out"]}/capability-card.md, summary.json, spoken-fa.txt, ' + ', '.join(r['pngs']))
        print('\n# Persian lines for the [RUN] beats (paste into script-fa.md; numbers are already words)\n')
        print('\n'.join(r['lines']))
    return r


def main():
    if '--selftest' in sys.argv:
        from selftest import selftest
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('plan')
    sub.add_parser('doctor')
    c = sub.add_parser('check')
    c.add_argument('--watch', action='store_true')
    r = sub.add_parser('run')
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument('--local', action='store_true')
    g.add_argument('--online', action='store_true')
    r.add_argument('--models', help='comma-separated Ollama tags (default: models.json)')
    r.add_argument('--limit', type=int)
    r.add_argument('--runs-dir', default=str(RUNS), help=argparse.SUPPRESS)
    b = sub.add_parser('blind')
    b.add_argument('--force', action='store_true')
    rp = sub.add_parser('report')
    rp.add_argument('--allow-changed-rules', action='store_true',
                    help='build the card even if rules/tasks/graders changed since the run (the card says so)')
    a = ap.parse_args()
    if a.cmd == 'plan':
        return plan()
    if a.cmd == 'doctor':
        return doctor()
    if a.cmd == 'check':
        if a.watch:
            return offline_check.watch()
        off, rows = offline_check.check()
        offline_check.print_check(off, rows)
        return 0 if off else 1
    if a.cmd == 'run' and a.local:
        models = a.models.split(',') if a.models else [m['tag'] for m in MODELS['models']]
        return run_local(models, a.limit, runs_dir=Path(a.runs_dir))
    if a.cmd == 'run':
        return run_online(a.limit, runs_dir=Path(a.runs_dir))
    if a.cmd == 'blind':
        return blind(force=a.force)
    if a.cmd == 'report':
        cmd_report(allow_changed=a.allow_changed_rules)
        return 0


if __name__ == '__main__':
    sys.exit(main())
