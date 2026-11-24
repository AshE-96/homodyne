"""HMD-024 · self-test: the whole pipeline with no Ollama, no key and no paid call, in under 60 seconds.

- graders, number words, the task bank
- the offline check with fake probes (offline / online) and the refusals of `run --local` (network reachable,
  Ollama host not on this machine). No real network use by default. With `--selftest --net` it also runs the real
  probes and a real `run --local` subprocess pointed at OLLAMA_HOST=127.0.0.1:1 and a temporary runs folder, so
  it can never touch a real Ollama or real results
- a fake Ollama server on 127.0.0.1 (demo.py) streaming two fake models, with real memory sampling
- the online arm through tools/llm.py with HOMODYNE_MODEL=mock:echo
- blind sheet export and scoring, report, card (md + png), charts, Persian lines
Everything it writes goes to demo/ and is labelled DEMO. None of it is a result.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMO = HERE / 'demo'


def selftest():
    t0 = time.time()
    os.environ['HOMODYNE_MODEL'] = 'mock:echo'   # tools/llm.py: no key, no network, deterministic
    import graders as G
    import offline_lab as L
    from spoken import dec_fa, words_fa
    from task_bank import TASKS, check_bank
    ok = True
    log = []

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        line = ('  ok    ' if cond else '  FAIL  ') + name
        log.append(line)
        print(line, flush=True)

    T = {t['id']: t for t in TASKS}
    print('HMD-024 selftest · DEMO (fake server + mock model; not a result)')
    check('task bank: 30 tasks, 5 per category, 15 Persian, needles unique', check_bank())
    check('norm: Persian digits, separators, decimal', G.norm('۱٬۲۸۵٬۰۰۰ و ۴٫۶') == '1285000 و 4.6')
    check('whole-token match: 3 is not inside 30', not G.has('30 روز', '3') and G.has('3 روز', '3'))
    check('summary: right bullets + key points pass', G.grade(T['sum-4'], '- battery lasts longer\n- still $49\n- ships June 3')['pass'])
    check('summary: 2 bullets when 3 asked fails', not G.grade(T['sum-4'], '- battery\n- $49 June 3')['pass'])
    check('extract: Persian digits and separators in JSON',
          G.grade(T['ext-1'], '```json\n{"seller":"لوازم‌التحریر نیلوفر","date":"۱۴۰۶/۰۲/۱۲","total_toman":"۱٬۲۸۵٬۰۰۰","buyer":"آقای کامران صدری"}\n```')['pass'])
    check('extract: "300 میلیون" is not 300000000', not G.grade(T['ext-2'], '{"landlord":"مهتاب رحیمی","start_date":"1406/03/01","deposit_toman":"300 میلیون","rent_toman":12000000}')['pass'])
    check('extract: date written differently, same day', G.field_ok('date', '2027-03-09', '2027/3/9'))
    check('qa: NOT_IN_TEXT on an unanswerable question passes', G.grade(T['qa-5'], 'NOT_IN_TEXT')['pass'])
    check('qa: NOT_IN_TEXT on an answerable question fails', not G.grade(T['qa-1'], 'NOT_IN_TEXT')['pass'])
    check('qa: invented answer to an unanswerable question is flagged',
          G.grade(T['qa-3'], 'ورودی ۵۰ هزار تومان است')['invented'])
    check('label: two labels at once fails', not G.grade(T['cls-4'], 'positive or neutral')['pass'])
    check('final: ANSWER line read, Persian digits', G.grade(T['nogo-1'], '۴۸ − ۸ = ۴۰ …\nANSWER: ۲۵')['pass'])
    check('terms: wrong language fails', not G.grade(T['tr-3'], 'The server restarts at 23:00, 15 minutes')['pass'])
    check('words_fa / dec_fa', words_fa(24) == 'بیست‌وچهار' and words_fa(1500) == 'هزار و پونصد'
          and dec_fa(1.2) == 'یک و دو دهم' and dec_fa(0.8) == 'هشت دهم' and dec_fa(12.5) == 'دوازده و نیم')

    import offline_check as OC
    off, _ = OC.check({'dns': lambda: (False, 'gaierror'), 'tcp': lambda: (False, 'timeout')})
    check('offline check: every probe fails → offline', off)
    off, _ = OC.check({'dns': lambda: (False, 'gaierror'), 'tcp': lambda: (True, 'connected')})
    check('offline check: one TCP probe reaches → online', not off)
    online_fake = lambda: (False, [{'probe': 'fake', 'reached_internet': True, 'detail': 'selftest'}])
    import contextlib
    import io
    import tempfile
    with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()) as buf:
        rc = L.run_local(['demo-small:q4'], base='http://127.0.0.1:1', checker=online_fake, runs_dir=Path(tmp))
        check('`run --local` refuses while the network is reachable ("Turn off Wi-Fi first")',
              rc == 3 and 'Turn off Wi-Fi first' in buf.getvalue() and not any(Path(tmp).iterdir()))
        rc = L.run_local(['demo-small:q4'], base='http://10.0.0.5:11434', checker=lambda: (True, []), runs_dir=Path(tmp))
        check('`run --local` refuses an Ollama host that is not this machine', rc == 5 and not any(Path(tmp).iterdir()))
    if '--net' in sys.argv:
        real_off, _ = OC.check()
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, 'OLLAMA_HOST': '127.0.0.1:1'}
            r = subprocess.run([sys.executable, str(HERE / 'offline_lab.py'), 'run', '--local', '--limit', '1',
                                '--runs-dir', tmp], capture_output=True, text=True, timeout=60, env=env)
            wrote = any(Path(tmp).rglob('results.jsonl'))
        if real_off:
            check('--net: offline right now → refuses for lack of Ollama at 127.0.0.1:1, writes nothing',
                  r.returncode == 4 and not wrote)
        else:
            check('--net: real probes see the internet → `run --local` refuses, writes nothing',
                  r.returncode == 3 and 'Turn off Wi-Fi first' in r.stdout and not wrote)
    else:
        log.append('  note  real network probes skipped (add --net to run them)')
        print(log[-1])
    check('hedged answer «۷٫۹ یا ۸٫۲» fails; a single answer passes',
          not G.grade(T['nogo-5'], 'ANSWER: ۷٫۹ یا ۸٫۲')['pass'] and G.grade(T['nogo-5'], 'ANSWER: ۷٫۹')['pass'])
    check('blind sheet hides boilerplate', L.strip_preamble('Here is the translation:\nThe server…') == 'The server…')

    if DEMO.exists():
        shutil.rmtree(DEMO)
    runs = DEMO / 'runs'
    srv = subprocess.Popen([sys.executable, str(HERE / 'demo.py'), 'serve', '--port', '0', 'ollama-fake', 'runner'],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(HERE))
    try:
        line = srv.stdout.readline()
        port = int(line.rsplit(':', 1)[1])
        base = f'http://127.0.0.1:{port}'
        check('fake Ollama server bound to 127.0.0.1 only', '127.0.0.1' in line)
        fake_offline = lambda: (True, [{'probe': 'fake', 'reached_internet': False, 'detail': 'selftest'}])
        rc = L.run_local(['demo-small:q4', 'demo-big:q4', 'qwen3.5:4b:cloud'], base=base, checker=fake_offline,
                         runs_dir=runs, mem_match='ollama-fake', demo=True, quiet=True)
        check('local arm ran on the fake server', rc == 0)
        rows = [json.loads(l) for l in (runs / 'local-demo-small-q4' / 'results.jsonl').read_text().splitlines()]
        meta = json.loads((runs / 'local-demo-small-q4' / 'meta.json').read_text())
        check('30 rows with streamed timings (ttft < total)', len(rows) == 30 and all(0 < r['ttft_s'] <= r['total_s'] for r in rows))
        check('tokens per second from Ollama counters', all(r['tokens_per_s'] and r['tokens_per_s'] > 0 for r in rows))
        check('memory sampled from the runner process (RSS > 0)', all(r['peak_runner_rss_bytes'] > 0 for r in rows)
              and rows[0]['mem_source'] == 'psutil:runner')
        check('think:false sent only to a model with the thinking capability', meta['think_sent'] is False and
              json.loads((runs / 'local-demo-big-q4' / 'meta.json').read_text())['think_sent'] is None)
        check('cloud model refused for the local arm', not (runs / 'local-qwen3.5-4b-cloud').exists())
        check('offline recorded before, during and after', meta['offline_before'] and meta['offline_after'] and all(meta['offline_mid']))
        check('rule-lock hashes recorded at run', set(meta['locks']['sha256']) == {'rules.json', 'task_bank.py', 'graders.py'})
        rc = L.run_online(runs_dir=runs, ask=lambda q: 'n', quiet=True)
        om = json.loads((runs / 'online-mock-echo' / 'meta.json').read_text())
        check('online arm via tools/llm.py (mock:echo, no prompt, no cost); same 1024 cap; effort low',
              rc == 0 and om['max_tokens'] == L.OPTIONS['num_predict'] == 1024 and om['effort'] == 'low')
        check('blind sheet exported with model names hidden; key kept outside the sheet folder',
              L.blind(runs_dir=runs) == 0 and 'demo-' not in (runs / 'blind' / 'sheet.csv').read_text()
              and (runs / '.key' / 'blind-key.json').exists() and not (runs / 'blind' / 'key.json').exists())
        import csv
        p = runs / 'blind' / 'sheet.csv'
        with p.open(encoding='utf-8', newline='') as f:
            sheet = list(csv.DictReader(f))
        next(r_ for r_ in sheet if r_['task'] == 'translate').update(meaning_kept='y', numbers_names_kept='y', reads_naturally='y')
        next(r_ for r_ in sheet if r_['task'] == 'summarise').update(adds_something_not_in_text='n')
        with p.open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(sheet[0]))
            w.writeheader()
            w.writerows(sheet)
        rep = L.cmd_report(runs_dir=runs, out_dir=DEMO / 'out', demo=True, quiet=True)
        check('owner blind marks override the automatic translation grade',
              any('owner' in x['cats']['translate']['source'] for x in rep['summ']))
        out = DEMO / 'out'
        card = (out / 'capability-card.md').read_text(encoding='utf-8')
        check('card markdown written and labelled DEMO', card.startswith('# DEMO') and '✓' in card)
        check('PNGs written (card, quality, speed-memory)', all((out / p).exists() for p in ('capability-card.png', 'quality.png', 'speed-memory.png'))
              or rep['pngs'][0].startswith('matplotlib not installed'))
        s = {x['model']: x for x in rep['summ']}
        check('small demo model scores below the big one', s['demo-small:q4']['passed'] < s['demo-big:q4']['passed'])
        check('invented answers counted', s['demo-small:q4']['invented'] == 2 and s['demo-big:q4']['invented'] == 1)
        check('a model is chosen by the locked rule', rep['chosen'] is not None)
        lines = '\n'.join(rep['lines'])
        check('Persian lines: numbers as words, no Latin digits', 'از سی کار' in lines and
              not any(ch.isdigit() and ch.isascii() for ln in rep['lines'] if not ln.startswith(('[', '!!!')) for ch in ln))
        check('card prints the lock hashes', 'sha256 at run: rules.json' in card)
        print('\n'.join('    ' + l for l in rep['lines'][:6]))
        # a run whose locked files changed: report refuses
        mp = runs / 'local-demo-big-q4' / 'meta.json'
        saved = mp.read_text()
        m_ = json.loads(saved)
        m_['locks']['sha256']['rules.json'] = '0' * 64
        mp.write_text(json.dumps(m_))
        try:
            L.cmd_report(runs_dir=runs, out_dir=DEMO / 'tmp-out', demo=True, quiet=True)
            refused = False
        except SystemExit as e:
            refused = 'Refusing to build the card' in str(e)
        check('report refuses when rules/tasks/graders changed since a run', refused)
        # a run that was not verified offline: left out of the choice and the spoken lines
        m_ = json.loads(saved)
        m_['offline_after'] = False
        mp.write_text(json.dumps(m_))
        rep2 = L.cmd_report(runs_dir=runs, out_dir=DEMO / 'tmp-out', demo=True, quiet=True)
        check('a run not verified offline is excluded and flagged as blocking',
              rep2['chosen']['model'] != 'demo-big:q4' and rep2['lines'][0].startswith('!!! BLOCKING')
              and not any('مدل نمایشی بزرگ' in ln for ln in rep2['lines'][1:]))
        mp.write_text(saved)
        shutil.rmtree(DEMO / 'tmp-out', ignore_errors=True)
        rep = L.cmd_report(runs_dir=runs, out_dir=DEMO / 'out', demo=True, quiet=True)
    finally:
        srv.terminate()
        srv.wait(timeout=5)
    with socket.socket() as s_:
        s_.settimeout(0.5)
        check('fake server shut down (port closed)', s_.connect_ex(('127.0.0.1', port)) != 0)
    took = time.time() - t0
    check(f'under 60 seconds ({took:.1f} s)', took < 60)
    verdict = 'SELFTEST PASSED' if ok else 'SELFTEST FAILED'
    print(verdict + ' · DEMO only: fake server + mock model, not a result')
    (HERE / 'selftest-output.txt').write_text(
        f'HMD-024 selftest · {time.strftime("%Y-%m-%d %H:%M")} · DEMO (fake server + mock model; not a result)\n'
        + '\n'.join(log) + '\n\nDEMO spoken lines (format check only):\n' + '\n'.join(rep['lines']) + '\n\n'
        + 'DEMO card:\n' + card + '\n' + verdict + '\n', encoding='utf-8')
    return 0 if ok else 1
