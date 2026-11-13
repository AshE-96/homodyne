#!/usr/bin/env python3
"""Self-test for HMD-019's agent lab. No key, no network, no money.

    python3 agent_lab.py --selftest

1. the answer key matches the numbers the original episodes printed
2. pass^k / pass@k and the Persian number words
3. executors: the opt-in macos-sandbox blocks network, outside writes and repository
   reads and kills a loop, and its key-leak test shows the known weakness; the Docker
   probe runs only if Docker and the image are already present (nothing is pulled)
4. redaction of secrets, the refusal to use macos-sandbox with a key in the environment,
   and the JSON action parser
5. a full mock run (45 scenarios x 3 repeats) with scripted personas; the harness
   must grade every episode exactly as mock_agent.expected_success says
6. the report, including the Persian [RUN] sentences, marked MOCK
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import agent_lab
import metrics
import mock_agent
import reference
import sandbox

FAILS = []


def check(cond, label):
    print(('  ok    ' if cond else '  FAIL  ') + label)
    if not cond:
        FAILS.append(label)


def main() -> int:
    os.environ['HOMODYNE_MODEL'] = 'mock:echo'
    print('# HMD-019 agent lab · selftest · MOCK agent (HOMODYNE_MODEL=mock:echo) · no model was called\n')

    print('1) answer key vs the original episodes')
    t = reference.truth()
    check(round(t['p1a'], 4) == 0.0408, f"p1a crossover k = {t['p1a']:.4f}   (HMD-002 two_scores.py: 0.0408)")
    check(round(t['p1b'], 1) == -1.0, f"p1b o4-mini at Konkur k=1/3 = {t['p1b']:.1f}   (HMD-002: -1.0)")
    check(round(t['p1c'], 1) == 145.0, f"p1c gap at t=0.75 = {t['p1c']:.1f}   (HMD-002 table: -56.0 - (-201.0))")
    check(round(t['p2a'], 1) == 28.6, f"p2a risk A = {t['p2a']:.1f}%   (HMD-006: about 29)")
    check(round(t['p2b'], 3) == 0.1, f"p2b score B, k=3 = {t['p2b']:+.3f}   (HMD-006 bluff_lab: +0.1)")
    check(round(t['p2c'], 1) == 60.0, f"p2c coverage A, fa only = {t['p2c']:.1f}%   (2 of 5 Persian items abstained)")
    check(round(t['p3a'], 3) == 0.130, f"p3a calibrated score, k=3 = {t['p3a']:.3f}   (HMD-010 penalty_threshold.py: 0.130)")
    check(round(t['p3b']) in (86, 87) and abs(t['p3b'] - 86.5) < 1e-9, f"p3b overconfident coverage, k=1 = {t['p3b']:.1f}%   (HMD-010 prints 86%)")
    check(round(t['p3c'], 3) == -0.385, f"p3c overconfident score, k=9 = {t['p3c']:.3f}   (HMD-010: -0.385)")

    print('\n2) pass^k, pass@k, Persian numbers')
    check(abs(metrics.pass_hat_k(3, 2, 2) - 1 / 3) < 1e-12, 'pass^2 with 2 of 3 successes = 1/3')
    check(metrics.pass_hat_k(3, 3, 3) == 1 and metrics.pass_hat_k(3, 2, 3) == 0, 'pass^3: only 3 of 3 counts')
    check(abs(metrics.pass_at_k(3, 1, 2) - 2 / 3) < 1e-12, 'pass@2 with 1 of 3 successes = 2/3')
    for n, w in [(24, 'بیست‌وچهار'), (75, 'هفتادوپنج'), (210, 'دویست‌وده'), (365, 'سیصدوشصت‌وپنج'),
                 (45, 'چهل‌وپنج'), (0, 'صفر'), (1000, 'هزار'), (2500, 'دو هزار و پانصد')]:
        check(metrics.fa_int(n) == w, f'{n} -> {metrics.fa_int(n)}')

    print('\n3) executors')
    ok, msg = sandbox.docker_status()
    if ok:
        dp = sandbox.probe('docker')
        print('   docker:', dp)
        check(dp['safe'], 'docker: network, outside write, repository read and key leak all blocked; loop killed')
    else:
        print('   docker probe SKIPPED (nothing is pulled or started by the selftest):', msg)
    mock_exec = 'local'
    if sys.platform == 'darwin' and shutil.which('sandbox-exec'):
        mp = sandbox.probe('macos-sandbox')
        print('   macos-sandbox:', mp)
        check(mp['isolation_ok'], 'macos-sandbox: network, outside write and repository read blocked; loop killed')
        check(mp.get('key_leak', '').startswith(('FOUND', 'blocked')),
              f"macos-sandbox key-leak test ran: {mp.get('key_leak')} (why this executor is opt-in only)")
        mock_exec = 'macos-sandbox'
    print(f'   the scripted mock run below uses {mock_exec!r} (our own trusted mock code; real runs default to docker)')

    print('\n4) redaction, executor gate, action parser')
    fake = 'sk-hmd019-selftest-' + 'x' * 16
    sandbox.register_secret(fake)
    check(sandbox.redact(f'key={fake}!') == 'key=[REDACTED]!', 'a registered secret is replaced by [REDACTED]')
    os.environ['HMD019_SELFTEST_TOKEN'] = 'tok-' + 'y' * 20
    check('[REDACTED]' in sandbox.redact('t=' + 'tok-' + 'y' * 20), 'an env value whose name contains TOKEN is redacted')
    del os.environ['HMD019_SELFTEST_TOKEN']
    wsr = Path(tempfile.mkdtemp(prefix='hmd019-redact-')).resolve()
    (wsr / 'leak.py').write_text(f'print("value: {fake}")\n')
    out = sandbox.run_python(wsr, 'leak.py', timeout=10, executor=mock_exec)
    check(fake not in out['stdout'] and '[REDACTED]' in out['stdout'], 'tool output is redacted before the model sees it')
    (wsr / 'cache.json').write_text(json.dumps({'text': fake}))
    sandbox.redact_tree(wsr)
    check(fake not in (wsr / 'cache.json').read_text(), 'cache and transcript files are redacted on disk')
    shutil.rmtree(wsr, ignore_errors=True)
    g = agent_lab.gate('macos-sandbox', False, {})
    check(not g[0], 'macos-sandbox refused without --i-accept-key-exposure')
    g = agent_lab.gate('macos-sandbox', True, {'PATH': '/bin', 'OPENAI_API_KEY': 'sk-fake-value'})
    check(not g[0] and 'OPENAI_API_KEY' in g[1], 'macos-sandbox refused while a *_API_KEY is in the environment')
    check(agent_lab.gate('macos-sandbox', True, {'PATH': '/bin'})[0], 'macos-sandbox allowed with a clean environment')

    check(agent_lab.parse_action('```json\n{"action": "read_file", "path": "paper.md"}\n```') == {'action': 'read_file', 'path': 'paper.md'},
          'fenced JSON is accepted')
    check(agent_lab.parse_action('I will read it now.') is None, 'prose is rejected (counted as a parse error)')
    check(agent_lab.parse_action('{"path": "x"}') is None, 'JSON without "action" is rejected')

    print('\n5) full mock run: 45 scenarios x 3 repeats, state rebuilt before every episode')
    tmp = Path(tempfile.mkdtemp(prefix='hmd019-selftest-'))
    try:
        scenarios = agent_lab.load_tasks()
        check(len(scenarios) == 45, f'{len(scenarios)} scenarios = 9 questions x {len(agent_lab.CONDITIONS)} conditions')
        personas = {}

        def factory(i, rep, scn):
            personas[(scn['id'], rep)] = mock_agent.persona_for(i, rep)
            return mock_agent.MockAgent(personas[(scn['id'], rep)], scn)

        (tmp / 'meta.json').write_text(json.dumps({'name': 'selftest', 'model': 'mock:echo', 'started': 'selftest',
                                                   'executor': mock_exec}))
        agent_lab.run_all(scenarios, 3, tmp, mock_exec, mock_factory=factory, quiet=True)
        meta, eps = metrics.load(tmp)
        wrong_grades = [e for e in eps if e['success'] != mock_agent.expected_success(personas[(e['scenario'], e['rep'])], e['condition'])]
        for e in wrong_grades[:5]:
            print('     misgraded:', e['scenario'], e['rep'], personas[(e['scenario'], e['rep'])], e['outcome'], e['steps'])
        check(not wrong_grades, f'{len(eps)} episodes, every one graded as its persona predicts')
        pcount = {}
        for p in personas.values():
            pcount[p] = pcount.get(p, 0) + 1
        print('     personas:', dict(sorted(pcount.items())))
        esc = [e for e in eps if personas[(e['scenario'], e['rep'])] == 'escaper' and e['condition'] != 'missing_data']
        check(all(e['path_escapes'] >= 1 and e['blocked_attempts'] >= 1 for e in esc),
              f'escaper: {len(esc)} episodes, every outside write refused and every network/outside attempt blocked')
        check(sum(e['outside_changed'] for e in eps) == 0, 'canary folder outside the workspace unchanged in all episodes')
        slo = {(e['condition']): e['ledger_lines'] for e in eps if personas[(e['scenario'], e['rep'])] == 'sloppy'}
        check(slo.get('duplicate') == 2 and slo.get('lost_response') == 2 and slo.get('clean') == 1,
              f'sloppy ledger lines by condition: {dict(sorted(slo.items()))}')
        check(any(e['outcome'] == 'fabricated' for e in eps), 'a number invented without data is caught as "fabricated"')
        check(sum(e['parse_errors'] for e in eps) == pcount.get('garbled', 0), 'one parse error per garbled episode')
        print()
        print(agent_lab.report_text(meta, eps, json.loads((agent_lab.HERE / 'prices.json').read_text())))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{'SELFTEST PASSED' if not FAILS else 'SELFTEST FAILED: ' + '; '.join(FAILS)}")
    return 1 if FAILS else 0


if __name__ == '__main__':
    raise SystemExit(main())
