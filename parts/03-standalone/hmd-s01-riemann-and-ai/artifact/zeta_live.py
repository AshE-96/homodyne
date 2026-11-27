#!/usr/bin/env python3
"""zeta_live.py · HMD-S01 · live demo page for recording, standard library only (mpmath only cross-checks).

    python3 -I artifact/zeta_live.py              # build artifact/zeta_live.html (+ artifact/derived/zeta-data.json)
    python3 -I artifact/zeta_live.py --serve      # build, then serve on http://127.0.0.1:8765/zeta_live.html
    python3 -I artifact/zeta_live.py --selftest   # offline numerical checks against published values
    python3 -I artifact/zeta_live.py --rebuild    # recompute the zeros even if derived/zeta-data.json exists

The page has three views (keys 1 2 3):
  1 · staircase  Chebyshev psi(x) rebuilt from the first k zeros by the explicit formula; → adds a zero, space plays
  2 · Hardy Z    Z(t) on the critical line; each sign change is a zero; the count against Riemann–von Mangoldt
  3 · 67%        what "a proportion of zeros on the line" means, and the timeline of proven proportions
URL parameters fix a state for a take: zeta_live.html?view=a&k=10&x=100 · ?view=b&T=50 · ?view=c&year=8
"""
import argparse
import http.server
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import zeta_core as zc  # noqa: E402

DATA = HERE / 'derived' / 'zeta-data.json'
PAGE = HERE / 'zeta_live.html'
N_ZEROS, T_GRID, DT = 500, 300.0, 0.025

# Proven lower bounds for the share of nontrivial zeros on the critical line. Every number is from the
# paper itself (title, abstract or theorem); see ../sources.md for links and the exact wording.
TIMELINE = [
    dict(when='1914', pct=0.0, label='∞ many', who='G. H. Hardy: infinitely many zeros on the line, but a 0% share',
         src='Hardy, C. R. Acad. Sci. Paris 158 (1914) 1012–1014'),
    dict(when='1942', pct=0.5, label='> 0%', who='A. Selberg: a positive proportion (the constant was tiny and not optimised)',
         src='Selberg, Skr. Norske Vid.-Akad. Oslo I 1942, no. 10'),
    dict(when='1974', pct=100 / 3, label='> 33.3%', who='N. Levinson: more than one third (mollifier method)',
         src='Levinson, Adv. Math. 13 (1974) 383–436 · title: "More than one third…"'),
    dict(when='1989', pct=40.88, label='> 40.88%', who='J. B. Conrey: more than two fifths',
         src='Conrey, J. reine angew. Math. 399 (1989) 1–26 · κ > 0.4088'),
    dict(when='2011', pct=41.05, label='> 41.05%', who='Bui, Conrey, Young: more than 41%',
         src='Acta Arith. 150 (2011) 35–64 · κ > 0.4105'),
    dict(when='2020', pct=41.73, label='> 41.7%', who='Pratt, Robles, Zaharescu, Zeindler: more than five twelfths',
         src='Res. Math. Sci. 7 (2020) · κ ≥ 0.417293 (Anthropic\'s post rounds the old record as 41.6%)'),
    dict(when='1973*', pct=200 / 3, label='66.7%*', conditional=True,
         who='H. Montgomery: two thirds are simple and on the line, IF the Riemann hypothesis is true',
         src='Montgomery, Proc. Sympos. Pure Math. 24 (1973) · conditional, hatched'),
    dict(when='Aug 2026', pct=67.25, label='> 67.2%', who='Claude (Anthropic, unreleased model): Montgomery\'s 2/3 made unconditional; 67.25% with a better window',
         src='Alpöge, Furman, arXiv 2608.13637 · proof found by Claude · Lean 4 (anthropics/zeta-23-lean)'),
    dict(when='Sep 2026', pct=67.25, label='> 67.25%', who='Y. Lamzouri: a new, simpler human proof of the same bound',
         src='Lamzouri, arXiv 2609.02882 (preprint)'),
    dict(when='Oct 2026', pct=67.35, label='> 67.35%', who='K. M. Knausgård: a small improvement (preprint, not yet refereed)',
         src='arXiv 2610.08965 · Lean 4 with three computational axioms'),
]
KNOWN_ZEROS = [14.134725141734693790, 21.022039638771554993, 25.010857580145688763,
               30.424876125859513210, 32.935061587739189691]          # Odlyzko's tables; LMFDB
KNOWN_PI = {100: 25, 1000: 168, 10_000: 1229, 1_000_000: 78498}        # OEIS A006880


def compute():
    t0 = time.time()
    zeros = zc.zeros(N_ZEROS)
    n = int(T_GRID / DT)
    z = [round(zc.hardy_z(i * DT), 4) for i in range(n + 1)]
    th = [round(zc.theta(i * DT), 4) for i in range(n + 1)]
    data = dict(meta=dict(made_by='artifact/zeta_live.py (zeta_core.py, standard library)', n_zeros=N_ZEROS,
                          grid=f'0..{T_GRID} step {DT}', seconds=round(time.time() - t0, 1)),
                zeros=[round(g, 9) for g in zeros], dt=DT, z=z, theta=th)
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps(data, separators=(',', ':')), encoding='utf-8')
    return data


def build(rebuild=False):
    data = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() and not rebuild else compute()
    data['timeline'] = TIMELINE
    html = (HERE / 'zeta_page.html').read_text(encoding='utf-8')
    PAGE.write_text(html.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':'))), encoding='utf-8')
    print(f'wrote {PAGE.relative_to(HERE.parent)}  ({len(data["zeros"])} zeros, Z(t) on 0..{T_GRID})')


def selftest():
    ok = True

    def check(name, cond, detail):
        nonlocal ok
        ok &= bool(cond)
        print(('  ok    ' if cond else '  FAIL  ') + f'{name:44} {detail}')

    check('zeta(2) = pi^2/6', abs(zc.zeta(2) - math.pi ** 2 / 6) < 1e-12, f'{zc.zeta(2).real:.15f}')
    check('zeta(-1) = -1/12 (analytic continuation)', abs(zc.zeta(-1) + 1 / 12) < 1e-10, f'{zc.zeta(-1).real:.12f}')
    check('zeta(-2) = 0 (trivial zero)', abs(zc.zeta(-2)) < 1e-10, f'{abs(zc.zeta(-2)):.1e}')
    check('Z(t) is real: |Im| tiny at t = 50', abs((zc.cmath.exp(1j * zc.theta(50)) * zc.zeta(0.5 + 50j)).imag) < 1e-9, '')
    zs = zc.zeros(t_max=101)
    for i, g in enumerate(KNOWN_ZEROS):
        check(f'zero #{i + 1} vs published value', abs(zs[i] - g) < 1e-9, f'{zs[i]:.9f} vs {g:.9f}')
    check('N(100) = 29 zeros on the line', len(zs) == 29, f'found {len(zs)}; formula theta/pi+1 = {zc.n_smooth(100):.3f}')
    for T in (50, 100):
        found = sum(1 for g in zs if g <= T)
        check(f'Riemann–von Mangoldt at T = {T}', abs(found - zc.n_smooth(T)) < 1.5,
              f'found {found}, smooth {zc.n_smooth(T):.2f}, asymptotic {zc.n_asymptotic(T):.2f}')
    for x, want in KNOWN_PI.items():
        got = zc.prime_pi(x)
        check(f'pi({x:,})', got == want, f'{got}')
    true = zc.psi(100.5)
    check('psi(100.5) = log lcm(1..100)', abs(true - math.log(math.lcm(*range(1, 101)))) < 1e-9, f'{true:.6f}')
    g500 = json.loads(DATA.read_text(encoding='utf-8'))['zeros'] if DATA.exists() else zc.zeros(200)
    for k in (0, 10, 100, len(g500)):
        approx = zc.psi_explicit(100.5, g500[:k])
        check(f'explicit formula, first {k} zeros, x = 100.5', k < 100 or abs(approx - true) < 1.0,
              f'{approx:8.3f} vs true {true:.3f} (gap {abs(approx - true):.3f})')
    try:
        import mpmath
        worst = max(abs(zc.zeta(s) - complex(mpmath.zeta(s))) / abs(complex(mpmath.zeta(s)))
                    for s in (0.5 + 14j, 0.3 + 300j, 0.5 + 811j, 2 + 3j, -0.5 + 40j))
        check('zeta vs mpmath (relative)', worst < 1e-9, f'worst {worst:.1e}  (mpmath {mpmath.__version__})')
        if DATA.exists():
            gap = max(abs(g500[k - 1] - float(mpmath.zetazero(k).imag)) for k in (1, 2, 50, 100, 250, 400, 500))
            check('stored zeros vs mpmath.zetazero', gap < 1e-8, f'max gap {gap:.1e} over 7 zeros up to #500')
            check('500 zeros, none missed (mpmath.nzeros)', mpmath.nzeros(g500[-1] + 1e-6) == len(g500), f'#500 at t = {g500[-1]:.6f}')
    except ImportError:
        print('  skip  mpmath not installed: cross-checks skipped (the checks above are enough)')
    pcts = [e['pct'] for e in TIMELINE if not e.get('conditional')]
    check('timeline is non-decreasing', pcts == sorted(pcts), ' '.join(f'{p:.2f}' for p in pcts))
    print('selftest ok' if ok else 'selftest FAILED')
    return 0 if ok else 1


def serve(port=8765):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(HERE), **kw)  # noqa: E731
    with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as srv:
        print(f'open http://127.0.0.1:{port}/zeta_live.html   (Ctrl-C to stop)')
        srv.serve_forever()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--serve', action='store_true')
    ap.add_argument('--rebuild', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    build(a.rebuild)
    if a.serve:
        serve()
