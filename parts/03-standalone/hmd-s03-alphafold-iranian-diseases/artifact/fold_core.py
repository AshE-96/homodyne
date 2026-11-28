"""fold_core.py · HMD-S03 · structure maths for the AlphaFold demo, standard library only.

  parse_pdb / parse_cif   C-alpha trace (one chain) from a PDB or mmCIF file, with B-factor (= pLDDT in AF models)
  align                   global sequence alignment (Needleman–Wunsch, free end gaps, BLOSUM-free identity scoring)
  kabsch                  optimal rigid superposition (Horn's quaternion method; a 4x4 Jacobi eigen-solve, no SVD)
  rmsd / tm_score         after superposition; TM-score with the standard d0(L) and a TM-score-program-style search
  bands                   pLDDT bands as the AlphaFold DB defines them (>90, 70–90, 50–70, <50)
"""
import math
import re

AA3 = dict(ALA='A', ARG='R', ASN='N', ASP='D', CYS='C', GLN='Q', GLU='E', GLY='G', HIS='H', ILE='I', LEU='L',
           LYS='K', MET='M', PHE='F', PRO='P', SER='S', THR='T', TRP='W', TYR='Y', VAL='V', MSE='M', SEC='U')
TOKEN = re.compile(r"'[^']*'|\"[^\"]*\"|\S+")


# ----------------------------------------------------------------------------- parsing
def parse_pdb(text, chain=None):
    """C-alpha atoms of the first model: list of dict(n=resnum, aa, xyz, b). First altloc only."""
    out, seen = [], set()
    for ln in text.splitlines():
        if ln.startswith('ENDMDL'):
            break
        if not ln.startswith('ATOM') or ln[12:16].strip() != 'CA':
            continue
        ch, n, alt = ln[21], int(ln[22:26]), ln[16]
        if (chain and ch != chain) or (n, ch) in seen or alt not in ' A':
            continue
        seen.add((n, ch))
        out.append(dict(n=n, aa=AA3.get(ln[17:20], 'X'), xyz=(float(ln[30:38]), float(ln[38:46]), float(ln[46:54])),
                        b=float(ln[60:66])))
    return out


def parse_cif(text, chain=None):
    """C-alpha atoms from the atom_site loop of an mmCIF file (first model; auth chain id; first altloc)."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith('_atom_site.'):
            break
        i += 1
    cols = []
    while i < len(lines) and lines[i].startswith('_atom_site.'):
        cols.append(lines[i].split('.', 1)[1].strip())
        i += 1
    c = {k: j for j, k in enumerate(cols)}
    out, seen, model = [], set(), None
    for ln in lines[i:]:
        if ln.startswith('#') or ln.startswith('loop_') or ln.startswith('_'):
            break
        t = TOKEN.findall(ln)
        if len(t) < len(cols) or t[c['group_PDB']] != 'ATOM' or t[c['label_atom_id']] != 'CA':
            continue
        m = t[c.get('pdbx_PDB_model_num', 0)] if 'pdbx_PDB_model_num' in c else '1'
        model = model or m
        if m != model:
            break
        ch = t[c['auth_asym_id']]
        if chain is None:
            chain = ch
        alt = t[c['label_alt_id']] if 'label_alt_id' in c else '.'
        n = int(t[c['auth_seq_id']])
        if ch != chain or (n, ch) in seen or alt not in '.A?':
            continue
        seen.add((n, ch))
        out.append(dict(n=n, aa=AA3.get(t[c['label_comp_id']], 'X'),
                        xyz=tuple(float(t[c['Cartn_' + a]]) for a in 'xyz'), b=float(t[c['B_iso_or_equiv']])))
    return out


def cif_chains(text):
    """Protein chains (auth ids) of the first model with their C-alpha counts, in file order."""
    counts, first = {}, None
    for ln in text.splitlines():
        if not ln.startswith('ATOM'):
            continue
        t = TOKEN.findall(ln)
        if first is None:
            first = _cols(text)
        c = first
        if t[c['label_atom_id']] != 'CA' or t[c['pdbx_PDB_model_num']] != '1':
            continue
        counts[t[c['auth_asym_id']]] = counts.get(t[c['auth_asym_id']], 0) + 1
    return counts


def _cols(text):
    cols = [ln.split('.', 1)[1].strip() for ln in text.splitlines() if ln.startswith('_atom_site.')]
    return {k: j for j, k in enumerate(cols)}


# ----------------------------------------------------------------------------- sequence alignment
def align(a, b, match=2, mismatch=-1, gap=-2):
    """Global alignment with free end gaps. Returns list of (i, j) index pairs of aligned (non-gap) positions."""
    n, m = len(a), len(b)
    S = [[0] * (m + 1) for _ in range(n + 1)]
    T = [[0] * (m + 1) for _ in range(n + 1)]          # 0 diag, 1 up (gap in b), 2 left (gap in a)
    for i in range(1, n + 1):
        T[i][0] = 1
    for j in range(1, m + 1):
        T[0][j] = 2
    for i in range(1, n + 1):
        ai, Si, Sp, Ti = a[i - 1], S[i], S[i - 1], T[i]
        last = i == n
        for j in range(1, m + 1):
            d = Sp[j - 1] + (match if ai == b[j - 1] else mismatch)
            u = Sp[j] + (0 if j == m else gap)
            l = Si[j - 1] + (0 if last else gap)
            if d >= u and d >= l:
                Si[j], Ti[j] = d, 0
            elif u >= l:
                Si[j], Ti[j] = u, 1
            else:
                Si[j], Ti[j] = l, 2
    i, j, pairs = n, m, []
    while i > 0 and j > 0:
        t = T[i][j]
        if t == 0:
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif t == 1:
            i -= 1
        else:
            j -= 1
    return pairs[::-1]


# ----------------------------------------------------------------------------- superposition
def _centroid(P):
    k = len(P)
    return tuple(sum(p[a] for p in P) / k for a in range(3))


def _jacobi4(A):
    """Eigen-decomposition of a symmetric 4x4 matrix. Returns (values, vectors as columns)."""
    A = [row[:] for row in A]
    V = [[float(i == j) for j in range(4)] for i in range(4)]
    for _ in range(60):
        off = sum(A[i][j] ** 2 for i in range(4) for j in range(4) if i != j)
        if off < 1e-22:
            break
        for p in range(3):
            for q in range(p + 1, 4):
                if abs(A[p][q]) < 1e-30:
                    continue
                th = (A[q][q] - A[p][p]) / (2 * A[p][q])
                t = (1 if th >= 0 else -1) / (abs(th) + math.sqrt(th * th + 1))
                c = 1 / math.sqrt(t * t + 1)
                s = t * c
                for k in range(4):
                    akp, akq = A[k][p], A[k][q]
                    A[k][p], A[k][q] = c * akp - s * akq, s * akp + c * akq
                for k in range(4):
                    apk, aqk = A[p][k], A[q][k]
                    A[p][k], A[q][k] = c * apk - s * aqk, s * apk + c * aqk
                for k in range(4):
                    vkp, vkq = V[k][p], V[k][q]
                    V[k][p], V[k][q] = c * vkp - s * vkq, s * vkp + c * vkq
    return [A[i][i] for i in range(4)], V


def kabsch(P, Q):
    """Rotation R and translation t minimising sum |R p + t - q|^2 (proper rotation, det = +1).
    Horn (1987): the optimal quaternion is the top eigenvector of a 4x4 matrix built from the cross-covariance."""
    cp, cq = _centroid(P), _centroid(Q)
    S = [[0.0] * 3 for _ in range(3)]
    for p, q in zip(P, Q):
        x = (p[0] - cp[0], p[1] - cp[1], p[2] - cp[2])
        y = (q[0] - cq[0], q[1] - cq[1], q[2] - cq[2])
        for a in range(3):
            for b in range(3):
                S[a][b] += x[a] * y[b]
    (xx, xy, xz), (yx, yy, yz), (zx, zy, zz) = S
    N = [[xx + yy + zz, yz - zy, zx - xz, xy - yx],
         [yz - zy, xx - yy - zz, xy + yx, zx + xz],
         [zx - xz, xy + yx, -xx + yy - zz, yz + zy],
         [xy - yx, zx + xz, yz + zy, -xx - yy + zz]]
    vals, V = _jacobi4(N)
    k = max(range(4), key=lambda i: vals[i])
    w, x, y, z = (V[r][k] for r in range(4))
    R = [[w * w + x * x - y * y - z * z, 2 * (x * y - w * z), 2 * (x * z + w * y)],
         [2 * (x * y + w * z), w * w - x * x + y * y - z * z, 2 * (y * z - w * x)],
         [2 * (x * z - w * y), 2 * (y * z + w * x), w * w - x * x - y * y + z * z]]
    Rcp = apply(R, (0, 0, 0), [cp])[0]
    t = (cq[0] - Rcp[0], cq[1] - Rcp[1], cq[2] - Rcp[2])
    return R, t


def apply(R, t, P):
    return [(R[0][0] * p[0] + R[0][1] * p[1] + R[0][2] * p[2] + t[0],
             R[1][0] * p[0] + R[1][1] * p[1] + R[1][2] * p[2] + t[1],
             R[2][0] * p[0] + R[2][1] * p[1] + R[2][2] * p[2] + t[2]) for p in P]


def det3(R):
    return (R[0][0] * (R[1][1] * R[2][2] - R[1][2] * R[2][1]) - R[0][1] * (R[1][0] * R[2][2] - R[1][2] * R[2][0])
            + R[0][2] * (R[1][0] * R[2][1] - R[1][1] * R[2][0]))


def dists(P, Q):
    return [math.dist(p, q) for p, q in zip(P, Q)]


def rmsd(P, Q):
    d = dists(P, Q)
    return math.sqrt(sum(x * x for x in d) / len(d))


def superpose_rmsd(P, Q):
    R, t = kabsch(P, Q)
    return rmsd(apply(R, t, P), Q), R, t


# ----------------------------------------------------------------------------- TM-score
def d0(L):
    return max(0.5, 1.24 * (L - 15) ** (1 / 3) - 1.8) if L > 21 else 0.5


def tm_score(P, Q, L=None):
    """TM-score of model P against reference Q for a FIXED residue correspondence (P[i] <-> Q[i]).
    L = normalisation length (default: number of pairs). Search as in the TM-score program: seed superpositions
    on fragments of length L, L/2, L/4 … then iterate on the residues closer than a cutoff. Returns (tm, R, t)."""
    n = len(P)
    L = L or n
    D0 = d0(L)
    best = (-1.0, None, None)
    frag = n
    while frag >= 4:
        step = max(1, frag // 2) if frag < n else n
        for s in range(0, n - frag + 1, step):
            idx = list(range(s, s + frag))
            for _ in range(20):
                R, t = kabsch([P[i] for i in idx], [Q[i] for i in idx])
                d = dists(apply(R, t, P), Q)
                tm = sum(1 / (1 + (x / D0) ** 2) for x in d) / L
                if tm > best[0]:
                    best = (tm, R, t)
                cut = D0 + 1.0
                new = [i for i, x in enumerate(d) if x < cut]
                while len(new) < 3 and cut < 50:
                    cut += 0.5
                    new = [i for i, x in enumerate(d) if x < cut]
                if new == idx:
                    break
                idx = new
        frag //= 2
    return best


# ----------------------------------------------------------------------------- confidence
BANDS = [(90, 'very high'), (70, 'high'), (50, 'low'), (-1, 'very low')]   # AFDB legend, faq-12


def band(p):
    for lo, name in BANDS:
        if p > lo:
            return name
    return 'very low'


def band_fractions(pl):
    out = {name: 0 for _, name in BANDS}
    for p in pl:
        out[band(p)] += 1
    return {k: v / len(pl) for k, v in out.items()}


def runs(flags):
    """Contiguous runs of True as (start, end) inclusive index pairs."""
    out, s = [], None
    for i, f in enumerate(list(flags) + [False]):
        if f and s is None:
            s = i
        elif not f and s is not None:
            out.append((s, i - 1))
            s = None
    return out


def downsample(M, k):
    """Block-mean of a square matrix by factor k (for a compact PAE heatmap)."""
    n = len(M)
    m = (n + k - 1) // k
    out = []
    for I in range(m):
        row = []
        for J in range(m):
            vals = [M[i][j] for i in range(I * k, min(n, I * k + k)) for j in range(J * k, min(n, J * k + k))]
            row.append(sum(vals) / len(vals))
        out.append(row)
    return out
