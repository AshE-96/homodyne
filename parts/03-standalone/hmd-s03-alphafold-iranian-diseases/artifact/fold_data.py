"""fold_data.py · HMD-S03 · download (key-less) and derive the compact data the demo page needs. Standard library only.

Raw files go to artifact/data/ (git-ignored). The derived file artifact/derived/fold-data.json is small and may be
redistributed: AlphaFold DB / Viro3D models are CC BY 4.0 (attribution in SOURCE.txt and on the page); PDB entries are
CC0 1.0; UniProt is CC BY 4.0.

Sources: AlphaFold DB API  https://alphafold.ebi.ac.uk/api/prediction/<UniProt>  (+ model, confidence and PAE files)
         RCSB PDB          https://files.rcsb.org/download/<id>.cif  and  https://data.rcsb.org/rest/v1/core/entry/<id>
         UniProt           https://rest.uniprot.org/uniprotkb/<acc>.json
Note: the AFDB file host answers 403 to curl's default User-Agent; urllib with a plain descriptive one is served normally.
"""
import datetime as dt
import hashlib
import json
import math
import urllib.request
from pathlib import Path

import fold_core as fc

HERE = Path(__file__).resolve().parent
RAW = HERE / 'data'
DERIVED = HERE / 'derived' / 'fold-data.json'
UA = {'User-Agent': 'homodyne-fold-demo/1.0 (python-urllib; educational video demo)'}

PROTEINS = [
    dict(key='gp63', acc='P08148', disease='cutaneous leishmaniasis', disease_fa='سالک (لیشمانیوز جلدی)',
         name='GP63 · leishmanolysin', name_fa='GP63 لیشمانیا ماژور', organism='Leishmania major',
         refs=[('1LML', 'A')]),
    dict(key='np', acc='P89522', disease='Crimean–Congo haemorrhagic fever', disease_fa='تب کریمه‌کنگو',
         name='CCHFV nucleoprotein (N)', name_fa='نوکلئوپروتئین ویروس کریمه‌کنگو', organism='CCHF virus, strain IbAr10200',
         refs=[('4AQG', 'A'), ('4AQF', 'B'), ('9WA4', 'A')]),
]
PAE_STEP = 2          # PAE heatmap is stored as 2x2 block means
HEAD_CORE = (list(range(0, 150)) + list(range(330, 482)))   # NP residues used to find the arm from PAE (0-based)


def get(url, binary=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        b = r.read()
    return b if binary else b.decode('utf-8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fetch(log=print):
    """Download everything into artifact/data/. Returns a list of (file, url, sha256)."""
    RAW.mkdir(exist_ok=True)
    got = []

    def save(name, url, binary=False):
        body = get(url, binary)
        p = RAW / name
        p.write_bytes(body) if binary else p.write_text(body, encoding='utf-8')
        got.append((name, url, sha(p)))
        log(f'  got {name:48} {p.stat().st_size:>9,} B')

    for P in PROTEINS:
        acc = P['acc']
        save(f'afdb-{acc}.json', f'https://alphafold.ebi.ac.uk/api/prediction/{acc}')
        meta = json.loads((RAW / f'afdb-{acc}.json').read_text())[0]
        save(f'model-{acc}.pdb', meta['pdbUrl'])
        save(f'pae-{acc}.json', meta['paeDocUrl'])
        save(f'plddt-{acc}.json', meta['plddtDocUrl'])
        save(f'uniprot-{acc}.json', f'https://rest.uniprot.org/uniprotkb/{acc}.json')
        for pdb, _ in P['refs']:
            save(f'{pdb}.cif', f'https://files.rcsb.org/download/{pdb}.cif')
            save(f'{pdb}-entry.json', f'https://data.rcsb.org/rest/v1/core/entry/{pdb}')
    (RAW / 'FETCHED.json').write_text(json.dumps(dict(at=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
                                                      files=got), indent=1), encoding='utf-8')
    return got


def _r(x, k=2):
    return round(x, k)


def arm_from_pae(pae, n):
    """Residues whose mean PAE to the NP head core exceeds 10 Å: the largest such run is the arm (stalk) domain."""
    m = [sum(pae[i][j] for j in HEAD_CORE) / len(HEAD_CORE) for i in range(n)]
    runs = fc.runs([v > 10 for v in m])
    a, b = max(runs, key=lambda r: r[1] - r[0])
    return a, b, [_r(v, 1) for v in m]


def compare(model, ref, groups):
    """Align by sequence, superpose with our Kabsch, report RMSD/TM for several residue subsets."""
    ms = ''.join(r['aa'] for r in model)
    rs = ''.join(r['aa'] for r in ref)
    pairs = fc.align(ms, rs)
    ident = sum(ms[i] == rs[j] for i, j in pairs) / len(pairs)
    P = [model[i]['xyz'] for i, _ in pairs]
    Q = [ref[j]['xyz'] for _, j in pairs]
    out = dict(n_ref=len(ref), n_pairs=len(pairs), identity=_r(ident, 3),
               model_range=[pairs[0][0] + 1, pairs[-1][0] + 1])
    rm, R, t = fc.superpose_rmsd(P, Q)
    tm, R2, t2 = fc.tm_score(P, Q, L=len(ref))
    d = fc.dists(fc.apply(R2, t2, P), Q)
    out.update(rmsd_all=_r(rm), tm=_r(tm, 3), within2=sum(x < 2 for x in d), d0=_r(fc.d0(len(ref))))
    for name, keep in groups.items():
        sel = [k for k, (i, _) in enumerate(pairs) if keep(i)]
        if len(sel) >= 3:
            r, R3, t3 = fc.superpose_rmsd([P[k] for k in sel], [Q[k] for k in sel])
            out[f'rmsd_{name}'] = _r(r)
            out[f'n_{name}'] = len(sel)
            if name == 'head':                       # where does the arm land once the heads are aligned?
                arm = [k for k in range(len(pairs)) if k not in set(sel)]
                Pa = fc.apply(R3, t3, [P[k] for k in arm])
                Qa = [Q[k] for k in arm]
                Ra, _ = fc.kabsch(Pa, Qa)
                tr = (Ra[0][0] + Ra[1][1] + Ra[2][2] - 1) / 2
                out['arm_after_head_fit'] = _r(fc.rmsd(Pa, Qa), 1)
                out['arm_rotation_deg'] = round(math.degrees(math.acos(max(-1, min(1, tr)))))
    coords = [_r(c) for _, j in pairs for c in ref[j]['xyz']]
    return out, [i for i, _ in pairs], [ref[j]['n'] for _, j in pairs], coords


def features(up):
    keep = {'Signal', 'Propeptide', 'Chain', 'Motif', 'Active site', 'Binding site', 'Lipidation', 'Site'}
    out = []
    for f in up.get('features', []):
        if f['type'] in keep:
            out.append(dict(type=f['type'], start=f['location']['start']['value'], end=f['location']['end']['value'],
                            note=f.get('description') or (f.get('ligand') or {}).get('name', '')))
    return out


def entry_meta(e):
    c = e.get('rcsb_primary_citation', {})
    return dict(title=e['struct']['title'], method=e['exptl'][0]['method'],
                resolution=(e.get('rcsb_entry_info', {}).get('resolution_combined') or [None])[0],
                released=e['rcsb_accession_info']['initial_release_date'][:10],
                citation=f"{(c.get('rcsb_authors') or ['?'])[0]} et al., {c.get('journal_abbrev', '?')} {c.get('year', '')}".strip())


def derive(log=print):
    fetched = json.loads((RAW / 'FETCHED.json').read_text())
    out = dict(made=dt.date.today().isoformat(), fetched=fetched['at'], made_by='artifact/fold_live.py (fold_core.py, stdlib)',
               licence='AlphaFold DB and Viro3D models: CC BY 4.0. PDB: CC0 1.0. UniProt: CC BY 4.0.', proteins=[])
    for P in PROTEINS:
        acc = P['acc']
        meta = json.loads((RAW / f'afdb-{acc}.json').read_text())[0]
        model = fc.parse_pdb((RAW / f'model-{acc}.pdb').read_text())
        pl = json.loads((RAW / f'plddt-{acc}.json').read_text())['confidenceScore']
        pae_doc = json.loads((RAW / f'pae-{acc}.json').read_text())
        pae = (pae_doc[0] if isinstance(pae_doc, list) else pae_doc)['predicted_aligned_error']
        n = len(model)
        assert len(pl) == n == len(pae), (acc, n, len(pl), len(pae))
        rec = dict(key=P['key'], acc=acc, name=P['name'], name_fa=P['name_fa'], disease=P['disease'],
                   disease_fa=P['disease_fa'], organism=P['organism'], n=n,
                   seq=''.join(r['aa'] for r in model),
                   afdb={k: meta.get(k) for k in ('entryId', 'toolUsed', 'providerId', 'modelCreatedDate', 'latestVersion',
                                                  'globalMetricValue', 'fractionPlddtVeryHigh', 'fractionPlddtConfident',
                                                  'fractionPlddtLow', 'fractionPlddtVeryLow')},
                   plddt=[_r(p, 1) for p in pl], ca=[_r(c) for r in model for c in r['xyz']],
                   pae_step=PAE_STEP, pae_max=max(max(r) for r in pae),
                   pae=''.join(chr(48 + min(40, round(v))) for row in fc.downsample(pae, PAE_STEP) for v in row),
                   features=features(json.loads((RAW / f'uniprot-{acc}.json').read_text())))
        rec['mean_plddt'] = _r(sum(pl) / n)
        rec['bands'] = {k: _r(v, 3) for k, v in fc.band_fractions(pl).items()}
        rec['low_runs'] = [[a + 1, b + 1] for a, b in fc.runs([p < 50 for p in pl]) if b - a >= 2]
        groups = {'confident': (lambda i, pl=pl: pl[i] > 90)}
        if P['key'] == 'np':
            a, b, prof = arm_from_pae(pae, n)
            rec['arm'] = [a + 1, b + 1]
            rec['arm_plddt'] = _r(sum(pl[a:b + 1]) / (b - a + 1), 1)
            rec['pae_to_head'] = prof
            rec['pae_blocks'] = dict(
                head_head=_r(sum(pae[i][j] for i in HEAD_CORE for j in HEAD_CORE) / len(HEAD_CORE) ** 2, 1),
                arm_arm=_r(sum(pae[i][j] for i in range(a, b + 1) for j in range(a, b + 1)) / (b - a + 1) ** 2, 1),
                arm_head=_r(sum(pae[i][j] for i in range(a, b + 1) for j in HEAD_CORE) / ((b - a + 1) * len(HEAD_CORE)), 1))
            groups['head'] = (lambda i, a=a, b=b: not a <= i <= b)
            groups['arm'] = (lambda i, a=a, b=b: a <= i <= b)
        else:
            mature = next(f for f in rec['features'] if f['type'] == 'Chain')
            groups['mature'] = (lambda i, m=mature: m['start'] - 1 <= i <= m['end'] - 1)
            rec['mature_plddt'] = _r(sum(pl[mature['start'] - 1:mature['end']]) / (mature['end'] - mature['start'] + 1))
        rec['refs'] = []
        for pdb, chain in P['refs']:
            ref = fc.parse_cif((RAW / f'{pdb}.cif').read_text(), chain)
            res, idx, auth, coords = compare(model, ref, groups)
            rec['refs'].append(dict(pdb=pdb, chain=chain, **entry_meta(json.loads((RAW / f'{pdb}-entry.json').read_text())),
                                    result=res, idx=idx, auth=auth, ca=coords))
            log(f'  {acc} vs {pdb}:{chain}  pairs {res["n_pairs"]}  RMSD {res["rmsd_all"]} Å  TM {res["tm"]}'
                + (f'  head {res["rmsd_head"]} Å  arm {res["arm_rotation_deg"]}°' if 'rmsd_head' in res else ''))
        if P['key'] == 'np':                        # experiment vs experiment: do the crystals agree on the arm?
            rec['exp_vs_exp'] = exp_vs_exp(rec)
        out['proteins'].append(rec)
    DERIVED.parent.mkdir(exist_ok=True)
    DERIVED.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    log(f'wrote {DERIVED.relative_to(HERE.parent)}  ({DERIVED.stat().st_size:,} B)')
    return out


def exp_vs_exp(rec):
    a, b = rec['arm'][0] - 1, rec['arm'][1] - 1
    xyz = {r['pdb']: {i: tuple(r['ca'][3 * k:3 * k + 3]) for k, i in enumerate(r['idx'])} for r in rec['refs']}
    out = []
    ids = list(xyz)
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            A, B = xyz[ids[x]], xyz[ids[y]]
            com = sorted(set(A) & set(B))
            H = [i for i in com if not a <= i <= b]
            Ar = [i for i in com if a <= i <= b]
            rh, R, t = fc.superpose_rmsd([A[i] for i in H], [B[i] for i in H])
            Pa = fc.apply(R, t, [A[i] for i in Ar])
            Ra, _ = fc.kabsch(Pa, [B[i] for i in Ar])
            tr = (Ra[0][0] + Ra[1][1] + Ra[2][2] - 1) / 2
            out.append(dict(a=ids[x], b=ids[y], rmsd_head=_r(rh), rmsd_all=_r(fc.superpose_rmsd([A[i] for i in com], [B[i] for i in com])[0]),
                            arm_rotation_deg=round(math.degrees(math.acos(max(-1, min(1, tr)))))))
    return out
