#!/usr/bin/env python3
"""fold_live.py · HMD-S03 · AlphaFold vs experiment, live demo page for recording. Standard library only.

    python3 -I artifact/fold_live.py              # build artifact/fold_live.html from artifact/derived/fold-data.json
    python3 -I artifact/fold_live.py --fetch      # download from AlphaFold DB, RCSB PDB, UniProt (key-less), re-derive, build
    python3 -I artifact/fold_live.py --serve      # build, then serve http://127.0.0.1:8766/fold_live.html (+ live AFDB check)
    python3 -I artifact/fold_live.py --selftest   # offline checks on the cached derived data (numpy cross-check if present)

The page (keys): 1 / 2 protein (GP63 · CCHFV NP) · R next experimental structure · O overlay on/off
                 M fit on: all / pLDDT > 90 / head (NP) · C colour: pLDDT / distance to experiment · Space spin
                 L live check against the AlphaFold DB API (only with --serve) · H hide controls
URL parameters fix a state for a take: fold_live.html?p=np&ref=4AQG&overlay=1&fit=head&color=dist&rx=20&ry=-40
"""
import argparse
import http.server
import json
import math
import random
import sys
import time
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fold_core as fc  # noqa: E402
import fold_data as fd  # noqa: E402

PAGE = HERE / 'fold_live.html'
PORT = 8766


def load():
    return json.loads(fd.DERIVED.read_text(encoding='utf-8'))


def build():
    data = load()
    html = (HERE / 'fold_page.html').read_text(encoding='utf-8')
    PAGE.write_text(html.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':'))), encoding='utf-8')
    print(f'wrote {PAGE.relative_to(HERE.parent)}  (data derived {data["made"]}, fetched {data["fetched"]})')


def live(acc):
    """Ask the AlphaFold DB API now and compare with the cached record."""
    t0 = time.time()
    try:
        meta = json.loads(fd.get(f'https://alphafold.ebi.ac.uk/api/prediction/{acc}'))[0]
    except Exception as e:  # noqa: BLE001
        return dict(ok=False, error=str(e)[:200])
    cached = next(p for p in load()['proteins'] if p['acc'] == acc)['afdb']
    keys = ('entryId', 'toolUsed', 'modelCreatedDate', 'latestVersion', 'globalMetricValue')
    return dict(ok=True, ms=round(1000 * (time.time() - t0)), at=time.strftime('%Y-%m-%d %H:%M:%S'),
                now={k: meta.get(k) for k in keys}, same=all(meta.get(k) == cached.get(k) for k in keys))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(HERE), **kw)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == '/api/live':
            acc = urllib.parse.parse_qs(u.query).get('acc', [''])[0]
            if acc not in {p['acc'] for p in fd.PROTEINS}:
                self.send_error(400, 'unknown accession')
                return
            body = json.dumps(live(acc)).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, *a):
        pass


def serve():
    with http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler) as srv:
        print(f'open http://127.0.0.1:{PORT}/fold_live.html   (Ctrl-C to stop)')
        srv.serve_forever()


# ----------------------------------------------------------------------------- selftest
def selftest():
    ok = True

    def check(name, cond, detail=''):
        nonlocal ok
        ok &= bool(cond)
        print(('  ok    ' if cond else '  FAIL  ') + f'{name:52} {detail}')

    rnd = random.Random(7)
    P = [(rnd.uniform(-20, 20), rnd.uniform(-20, 20), rnd.uniform(-20, 20)) for _ in range(200)]
    a, b, c = 0.7, -1.3, 2.1                                      # a known rotation (ZYX Euler) and shift
    Rz = [[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]]
    Ry = [[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]]
    Rx = [[1, 0, 0], [0, math.cos(c), -math.sin(c)], [0, math.sin(c), math.cos(c)]]
    mm = lambda A, B: [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]  # noqa: E731
    Q = fc.apply(mm(Rz, mm(Ry, Rx)), (5, -3, 12), P)
    r, R, _ = fc.superpose_rmsd(P, Q)
    check('Kabsch recovers a known rotation + shift', r < 1e-9, f'RMSD {r:.1e} Å')
    check('rotation is proper (det = +1)', abs(fc.det3(R) - 1) < 1e-9, f'det {fc.det3(R):.12f}')
    Qn = [(x + rnd.gauss(0, 1), y + rnd.gauss(0, 1), z + rnd.gauss(0, 1)) for x, y, z in Q]
    rn, _, _ = fc.superpose_rmsd(P, Qn)
    check('noise of 1 Å per axis gives RMSD ≈ √3 Å', 1.55 < rn < 1.9, f'{rn:.3f} (√3 = 1.732)')
    mirror = [(-x, y, z) for x, y, z in P]
    check('a mirror image cannot be superposed', fc.superpose_rmsd(mirror, P)[0] > 5, f'{fc.superpose_rmsd(mirror, P)[0]:.2f} Å')
    tm, _, _ = fc.tm_score(P, Q)
    check('TM-score of identical shapes = 1', abs(tm - 1) < 1e-9, f'{tm:.6f}')
    check('d0(L) standard formula', abs(fc.d0(465) - (1.24 * 450 ** (1 / 3) - 1.8)) < 1e-12, f'd0(465) = {fc.d0(465):.3f} Å')
    pr = fc.align('MKVLAAGHE', 'VLAGHE')
    check('alignment: free end gaps, one internal gap', [(i, j) for i, j in pr][0] == (2, 0) and len(pr) == 6, str(pr))
    check('pLDDT bands follow the AFDB legend', [fc.band(x) for x in (95, 90, 80, 60, 30)] == ['very high', 'high', 'high', 'low', 'very low'])
    try:
        data = load()
    except FileNotFoundError:
        print('  FAIL  derived/fold-data.json missing: run --fetch once')
        return 1
    for p in data['proteins']:
        A = p['afdb']
        check(f'{p["acc"]}: mean pLDDT equals AFDB globalMetricValue', abs(p['mean_plddt'] - A['globalMetricValue']) < 0.06,
              f'{p["mean_plddt"]} vs {A["globalMetricValue"]}')
        for ours, theirs in (('very high', 'fractionPlddtVeryHigh'), ('very low', 'fractionPlddtVeryLow')):
            check(f'{p["acc"]}: fraction {ours} equals AFDB', abs(p['bands'][ours] - A[theirs]) < 0.006,
                  f'{p["bands"][ours]} vs {A[theirs]}')
        check(f'{p["acc"]}: {p["n"]} residues, coords and pLDDT agree', len(p['ca']) == 3 * p['n'] == 3 * len(p['plddt']))
        m = int(math.ceil(p['n'] / p['pae_step']))
        diag = sum(ord(p['pae'][i * m + i]) - 48 for i in range(m)) / m
        check(f'{p["acc"]}: PAE {m}x{m}, small on the diagonal', len(p['pae']) == m * m and diag < 3, f'mean diagonal {diag:.2f} Å')
        mxyz = [tuple(p['ca'][3 * i:3 * i + 3]) for i in range(p['n'])]
        for ref in p['refs']:
            Pm = [mxyz[i] for i in ref['idx']]
            Qr = [tuple(ref['ca'][3 * k:3 * k + 3]) for k in range(len(ref['idx']))]
            r, _, _ = fc.superpose_rmsd(Pm, Qr)
            check(f'{p["acc"]} vs {ref["pdb"]}: stored RMSD reproduced', abs(r - ref['result']['rmsd_all']) < 0.011,
                  f'{r:.2f} Å over {len(Pm)} Cα, TM {ref["result"]["tm"]}')
            try:
                import numpy as np
                X, Y = np.array(Pm), np.array(Qr)
                X, Y = X - X.mean(0), Y - Y.mean(0)
                U, S, Vt = np.linalg.svd(X.T @ Y)
                D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
                Rn = Vt.T @ D @ U.T
                rn = float(np.sqrt(((X @ Rn.T - Y) ** 2).sum(1).mean()))
                check(f'  numpy SVD Kabsch agrees ({np.__version__})', abs(rn - r) < 1e-6, f'{rn:.6f} vs {r:.6f}')
            except ImportError:
                pass
    gp, npr = data['proteins']
    check('GP63: very-low runs sit in signal/propeptides', all(e < 101 or s > 574 for s, e in gp['low_runs']), str(gp['low_runs']))
    check('NP: arm-to-head PAE > 10 Å and > 2x arm-to-arm', npr['pae_blocks']['arm_head'] > max(10, 2 * npr['pae_blocks']['arm_arm']),
          str(npr['pae_blocks']))
    check('NP: arm itself is confident (pLDDT > 70)', npr['arm_plddt'] > 70, f'{npr["arm_plddt"]}')
    heads = [r['result']['rmsd_head'] for r in npr['refs']]
    check('NP: head domain within 2.5 Å of every structure', max(heads) < 2.5, ' '.join(f'{h:.2f}' for h in heads))
    print('selftest ok' if ok else 'selftest FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--serve', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.fetch:
        fd.fetch()
        fd.derive()
    build()
    if a.serve:
        serve()
