#!/usr/bin/env python3
"""Homodyne HMD-013 - "Can you spot a fake review? Can AI?"  (local experiment, no API)

Data: Deceptive Opinion Spam Corpus v1.4 (Ott et al. 2011, 2013), 1,600 hotel reviews of
20 Chicago hotels. Deceptive = written on Mechanical Turk by people who never stayed there,
asked to sound real. Truthful = mined from review sites (TripAdvisor etc.); the authors
filtered them but could not verify each stay, so "truthful" means "presumed truthful".
Run fetch_data.py first; the corpus is CC BY-NC-SA 3.0 and is not committed here.

Contestants, all tested on hotels they never saw (the corpus's own 5 folds are by hotel):
  rules   two transparent cues from the paper's findings - more "I/me/my", fewer
          concrete spatial words - with thresholds tuned on the training hotels
  model   multinomial Naive Bayes on words and word pairs (standard library)
  humans  NOT re-run here: the three student judges reported by Ott et al. 2011, Table 2
          (fold 1, positive reviews, 160 texts). We score our model on those same 160 texts.

"fake" is the positive class (the accusation). For each detector we report
  precision  of all reviews it calls fake, how many really are
  recall     of all fake reviews, how many it catches
  FPR        false-accusation rate: of all real reviews, how many it calls fake
with 95% Wilson intervals. Then: how these change with the amount of text the detector
sees (first 1, 3, 5 sentences, whole review; and 1, 3, 10 on reviews with >= 10 sentences),
a strict "auto-delete" threshold, transfer to the other sentiment (unseen domain),
and an arithmetic projection to a site where 4.4% of reviews are fake.

    python3 review_lab.py              # full run (about 1-2 minutes), writes results/local-results.json
    python3 review_lab.py --quiz       # print the 10-review viewer quiz (texts stay local)
    python3 review_lab.py --selftest   # checks on toy data; no corpus needed

Standard library only (sklearn, if installed, adds one robustness line).
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import random
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data' / 'op_spam_v1.4'
RESULTS = HERE / 'results'
SEED = 13
STRICT_FPR = 0.01          # auto-delete mode: at most 1% of real reviews flagged on training hotels
PREVALENCE = 0.044         # Tripadvisor 2022: 4.4% of 30.2M submissions judged fake (its own detection)
STATUS = 'MEASURED on the Ott corpus (research-written deception); projections are ARITHMETIC, not measured'

# Published human baseline, Ott et al. 2011 (ACL), Table 2: fold 1, positive reviews, n = 160
# (80 deceptive, 80 truthful). Deceptive columns give precision/recall of the "fake" call.
HUMANS_OTT2011 = {
    'JUDGE 1': {'accuracy': 0.619, 'precision': 0.744, 'recall': 0.363},
    'JUDGE 2': {'accuracy': 0.569, 'precision': 0.789, 'recall': 0.188},
    'JUDGE 3': {'accuracy': 0.531, 'precision': 0.547, 'recall': 0.363},
}

FIRST_PERSON = {'i', 'me', 'my', 'mine', 'myself'}
CONCRETE = {  # spatial / sensory detail, after Ott et al. 2011 sec. 5 ("small, bathroom, on, location")
    'bathroom', 'floor', 'floors', 'location', 'located', 'small', 'tiny', 'block', 'blocks', 'street',
    'walk', 'walking', 'elevator', 'elevators', 'lobby', 'view', 'shower', 'door', 'window', 'minutes',
    'corner', 'size', 'square', 'mile', 'miles', 'train', 'station', 'parking', 'downstairs', 'upstairs',
    'avenue', 'bed', 'beds', 'tub', 'sink', 'carpet', 'noise', 'loud', 'checkin', 'desk',
}
SENT = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'(])')
TOKEN = re.compile(r"[a-z]+(?:'[a-z]+)?|[0-9]+|[!?$]")


# ---------------------------------------------------------------- data

def load(data_dir: Path = DATA) -> list[dict]:
    if not data_dir.exists():
        raise SystemExit(f'No corpus at {data_dir}. Run: python3 {HERE.name}/fetch_data.py')
    rows = []
    for f in sorted(data_dir.glob('*/*/fold*/*.txt')):
        polarity, _source, fold, name = f.relative_to(data_dir).parts
        cls, hotel, idx = f.stem.split('_')
        text = f.read_text(encoding='utf-8', errors='replace').strip()
        rows.append({'id': f'{polarity[:3]}/{f.stem}', 'text': text, 'fake': int(cls == 'd'),
                     'hotel': hotel, 'fold': int(fold[-1]), 'polarity': polarity.split('_')[0]})
    return rows


def sentences(text: str) -> list[str]:
    return [s.strip() for s in SENT.split(text.strip()) if s.strip()]


def first_k(text: str, k: int | None) -> str:
    return text if k is None else ' '.join(sentences(text)[:k])


def words(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def features(text: str) -> list[str]:
    w = words(text)
    return w + [a + ' ' + b for a, b in zip(w, w[1:])]


# ---------------------------------------------------------------- detectors

class NaiveBayes:
    """Multinomial NB, Laplace smoothing. score() = log-odds of 'fake' (prior 50/50)."""

    def fit(self, texts: list[str], labels: list[int]) -> 'NaiveBayes':
        self.counts = [Counter(), Counter()]
        for t, y in zip(texts, labels):
            self.counts[y].update(features(t))
        vocab = set(self.counts[0]) | set(self.counts[1])
        totals = [sum(c.values()) + len(vocab) for c in self.counts]
        self.logp = {w: math.log((self.counts[1][w] + 1) / totals[1]) - math.log((self.counts[0][w] + 1) / totals[0])
                     for w in vocab}
        self.unseen = math.log(1 / totals[1]) - math.log(1 / totals[0])
        return self

    def score(self, text: str) -> float:
        return sum(self.logp.get(f, self.unseen) for f in features(text))


def rule_features(text: str) -> tuple[float, float]:
    w = words(text)
    n = max(len(w), 1)
    return sum(x in FIRST_PERSON for x in w) / n, 100 * sum(x in CONCRETE for x in w) / n


class Rules:
    """Flag as fake when (I/me/my rate > a) and/or (concrete words per 100 < b); tuned for accuracy on train."""

    def fit(self, texts, labels):
        feats = [rule_features(t) for t in texts]
        ia = sorted({round(f[0], 3) for f in feats})
        cb = sorted({round(f[1], 1) for f in feats})
        grid_a = [ia[int(q * (len(ia) - 1))] for q in [i / 40 for i in range(41)]]
        grid_b = [cb[int(q * (len(cb) - 1))] for q in [i / 40 for i in range(41)]]
        best = (-1, None)
        for mode in ('I', 'concrete', 'I and concrete', 'I or concrete'):
            for a in (grid_a if mode != 'concrete' else [None]):
                for b in (grid_b if mode != 'I' else [None]):
                    self.mode, self.a, self.b = mode, a, b
                    acc = sum(self._flag(f) == y for f, y in zip(feats, labels))
                    if acc > best[0]:
                        best = (acc, (mode, a, b))
        self.mode, self.a, self.b = best[1]
        return self

    def _flag(self, f):
        hi_i = self.a is not None and f[0] > self.a
        lo_c = self.b is not None and f[1] < self.b
        return int({'I': hi_i, 'concrete': lo_c, 'I and concrete': hi_i and lo_c, 'I or concrete': hi_i or lo_c}[self.mode])

    def predict(self, text):
        return self._flag(rule_features(text))

    def describe(self):
        parts = []
        if self.a is not None:
            parts.append(f'I/me/my share > {self.a:.3f}')
        if self.b is not None:
            parts.append(f'concrete words per 100 < {self.b:.1f}')
        joiner = ' OR ' if self.mode == 'I or concrete' else ' AND '
        return joiner.join(parts)


# ---------------------------------------------------------------- metrics

def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def metrics(y: list[int], pred: list[int]) -> dict:
    tp = sum(a == 1 and b == 1 for a, b in zip(y, pred))
    fp = sum(a == 0 and b == 1 for a, b in zip(y, pred))
    fn = sum(a == 1 and b == 0 for a, b in zip(y, pred))
    tn = sum(a == 0 and b == 0 for a, b in zip(y, pred))
    def ratio(k, n):
        return {'value': k / n if n else None, 'ci95': wilson(k, n), 'k': k, 'n': n}
    return {'n': len(y), 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'accuracy': ratio(tp + tn, len(y)), 'precision': ratio(tp, tp + fp),
            'recall': ratio(tp, tp + fn), 'fpr': ratio(fp, fp + tn)}


def project(recall: float, fpr: float, prevalence: float = PREVALENCE, n: int = 10_000) -> dict:
    """Arithmetic only: what the same recall/FPR would mean on a site with this share of fakes."""
    fakes = n * prevalence
    caught, wrong = recall * fakes, fpr * (n - fakes)
    return {'reviews': n, 'prevalence': prevalence, 'fake_reviews': round(fakes), 'fakes_flagged': round(caught),
            'real_flagged': round(wrong), 'precision': caught / (caught + wrong) if caught + wrong else None}


def pct(m: dict, key: str) -> str:
    r = m[key]
    if r['value'] is None:
        return '   n/a          '
    lo, hi = r['ci95']
    return f"{100 * r['value']:5.1f}% [{100 * lo:4.1f}-{100 * hi:4.1f}]"


# ---------------------------------------------------------------- experiments

def folds_of(rows):
    return sorted({r['fold'] for r in rows})


def strict_threshold(train: list[dict], k: int | None, max_fpr: float = STRICT_FPR) -> float:
    """Out-of-fold NB scores on the training hotels (inner CV by fold), cut so <= max_fpr of real reviews are flagged."""
    real_scores = []
    for g in folds_of(train):
        nb = NaiveBayes().fit([r['text'] for r in train if r['fold'] != g], [r['fake'] for r in train if r['fold'] != g])
        real_scores += [nb.score(first_k(r['text'], k)) for r in train if r['fold'] == g and not r['fake']]
    real_scores.sort()
    cut = int(math.ceil((1 - max_fpr) * len(real_scores))) - 1
    return real_scores[min(max(cut, 0), len(real_scores) - 1)]


def run_cv(rows: list[dict], lengths: list[int | None], strict: bool = True, rules: bool = True) -> dict:
    """5-fold cross-validation by hotel. Returns per-length predictions for NB (default + strict) and rules (full)."""
    out = {'nb': {str(k): {'y': [], 'pred': [], 'score': [], 'id': []} for k in lengths},
           'nb_strict': {str(k): {'y': [], 'pred': []} for k in lengths},
           'rules': {'y': [], 'pred': [], 'id': [], 'describe': []}}
    for f in folds_of(rows):
        train = [r for r in rows if r['fold'] != f]
        test = [r for r in rows if r['fold'] == f]
        nb = NaiveBayes().fit([r['text'] for r in train], [r['fake'] for r in train])
        for k in lengths:
            o = out['nb'][str(k)]
            for r in test:
                s = nb.score(first_k(r['text'], k))
                o['y'].append(r['fake']); o['score'].append(s); o['pred'].append(int(s > 0)); o['id'].append(r['id'])
            if strict:
                t = strict_threshold(train, k)
                o2 = out['nb_strict'][str(k)]
                for r, s in zip(test, o['score'][-len(test):]):
                    o2['y'].append(r['fake']); o2['pred'].append(int(s > t))
        if rules:
            ru = Rules().fit([r['text'] for r in train], [r['fake'] for r in train])
            out['rules']['describe'].append(f'fold {f}: {ru.describe()}')
            for r in test:
                out['rules']['y'].append(r['fake']); out['rules']['pred'].append(ru.predict(r['text'])); out['rules']['id'].append(r['id'])
    return out


def transfer(rows: list[dict]) -> dict:
    """Train on one sentiment, test on the other, always on held-out hotels: an unseen domain."""
    res = {}
    for src, dst in (('positive', 'negative'), ('negative', 'positive')):
        y, pred, y_in, pred_in = [], [], [], []
        for f in folds_of(rows):
            train = [r for r in rows if r['fold'] != f and r['polarity'] == src]
            nb = NaiveBayes().fit([r['text'] for r in train], [r['fake'] for r in train])
            for r in rows:
                if r['fold'] == f and r['polarity'] == dst:
                    y.append(r['fake']); pred.append(int(nb.score(r['text']) > 0))
                if r['fold'] == f and r['polarity'] == src:
                    y_in.append(r['fake']); pred_in.append(int(nb.score(r['text']) > 0))
        res[f'{src}->{dst}'] = metrics(y, pred)
        res[f'{src}->{src}'] = metrics(y_in, pred_in)
    return res


def sklearn_check(rows: list[dict]) -> dict | None:
    try:
        import sklearn
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.linear_model import LogisticRegression
    except ImportError:
        return None
    y, pred = [], []
    for f in folds_of(rows):
        train = [r for r in rows if r['fold'] != f]
        test = [r for r in rows if r['fold'] == f]
        vec = CountVectorizer(ngram_range=(1, 2), lowercase=True, binary=True)
        X = vec.fit_transform([r['text'] for r in train])
        clf = LogisticRegression(max_iter=2000, C=1.0).fit(X, [r['fake'] for r in train])
        pred += list(clf.predict(vec.transform([r['text'] for r in test])))
        y += [r['fake'] for r in test]
    return {'sklearn': sklearn.__version__, 'model': 'LogisticRegression(C=1) on binary 1-2 grams',
            **metrics(y, [int(p) for p in pred])}


def quiz(rows: list[dict], cv: dict, n: int = 10) -> list[dict]:
    """10 short positive reviews from fold 1 (the hotels Ott's student judges saw), 5 fake + 5 real, seeded."""
    rng = random.Random(SEED)
    scores = dict(zip(cv['nb']['None']['id'], cv['nb']['None']['score']))
    pool = [r for r in rows if r['fold'] == 1 and r['polarity'] == 'positive' and 60 <= len(r['text'].split()) <= 110]
    pick = rng.sample([r for r in pool if r['fake']], n // 2) + rng.sample([r for r in pool if not r['fake']], n // 2)
    rng.shuffle(pick)
    return [{'q': i + 1, 'id': r['id'], 'truth': 'fake' if r['fake'] else 'real', 'words': len(r['text'].split()),
             'model_says': 'fake' if scores[r['id']] > 0 else 'real'} for i, r in enumerate(pick)]


def main_run(args) -> int:
    rows = load()
    rng_note = f'seed {SEED}'
    lengths = [1, 3, 5, None]
    nsent = [len(sentences(r['text'])) for r in rows]
    print('HMD-013 review_lab.py ·', STATUS)
    print(f'python {platform.python_version()} · standard library · {rng_note}')
    print(f'\n1. DATA  {len(rows)} reviews · {sum(r["fake"] for r in rows)} deceptive · 20 hotels in 5 folds of 4 · '
          f'median {sorted(nsent)[len(nsent) // 2]} sentences, {sorted(len(r["text"].split()) for r in rows)[len(rows) // 2]} words')

    cv = run_cv(rows, lengths)
    res = {'status': STATUS, 'python': platform.python_version(), 'seed': SEED, 'n_reviews': len(rows),
           'corpus': 'Deceptive Opinion Spam Corpus v1.4 (Ott et al. 2011, 2013), CC BY-NC-SA 3.0'}

    full = metrics(cv['nb']['None']['y'], cv['nb']['None']['pred'])
    rul = metrics(cv['rules']['y'], cv['rules']['pred'])
    f1 = [i for i, rid in enumerate(cv['nb']['None']['id']) if rid.startswith('pos/') and
          any(h in rid for h in ('_hilton_', '_james_', '_monaco_', '_sofitel_'))]
    same160 = metrics([cv['nb']['None']['y'][i] for i in f1], [cv['nb']['None']['pred'][i] for i in f1])
    f1r = [i for i, rid in enumerate(cv['rules']['id']) if rid.startswith('pos/') and
           any(h in rid for h in ('_hilton_', '_james_', '_monaco_', '_sofitel_'))]
    rules160 = metrics([cv['rules']['y'][i] for i in f1r], [cv['rules']['pred'][i] for i in f1r])
    print('\n2. CONTEST  whole reviews, hotels never seen in training   (fake = positive class; 95% Wilson CI)')
    print(f'   {"detector":34} {"accuracy":20} {"precision":20} {"recall":20} {"false accusation":20}')
    print(f'   {"simple rules":34} {pct(rul, "accuracy")} {pct(rul, "precision")} {pct(rul, "recall")} {pct(rul, "fpr")}')
    print(f'   {"Naive Bayes, words + pairs":34} {pct(full, "accuracy")} {pct(full, "precision")} {pct(full, "recall")} {pct(full, "fpr")}')
    print(f'   {"  same rules, Ott fold-1 positive":34} {pct(rules160, "accuracy")} {pct(rules160, "precision")} {pct(rules160, "recall")} {pct(rules160, "fpr")}   n={rules160["n"]}')
    print(f'   {"  same model, Ott fold-1 positive":34} {pct(same160, "accuracy")} {pct(same160, "precision")} {pct(same160, "recall")} {pct(same160, "fpr")}   n={same160["n"]}')
    for name, h in HUMANS_OTT2011.items():
        print(f'   {"human " + name + " (Ott 2011, published)":34} {100 * h["accuracy"]:5.1f}%                {100 * h["precision"]:5.1f}%                {100 * h["recall"]:5.1f}%')
    print('   rules learned per fold:', '; '.join(cv['rules']['describe']))
    res['contest'] = {'rules': rul, 'naive_bayes': full, 'naive_bayes_ott_fold1_positive': same160, 'rules_ott_fold1_positive': rules160,
                      'humans_ott2011_table2': HUMANS_OTT2011, 'rules_learned': cv['rules']['describe']}
    sk = sklearn_check(rows) if not args.no_sklearn else None
    if sk:
        print(f'   robustness: sklearn {sk["sklearn"]} {sk["model"]}: accuracy {pct(sk, "accuracy")}, false accusation {pct(sk, "fpr")}')
    res['sklearn_check'] = sk

    print('\n3. HOW MUCH TEXT  detector trained on whole reviews, shown only the first k sentences of each test review')
    print(f'   {"text seen":18} {"accuracy":20} {"precision":20} {"recall":20} {"false accusation":20}')
    res['length'] = {}
    for k in lengths:
        m = metrics(cv['nb'][str(k)]['y'], cv['nb'][str(k)]['pred'])
        res['length'][str(k)] = m
        label = 'whole review' if k is None else f'{k} sentence' + ('s' if k > 1 else '')
        print(f'   {label:18} {pct(m, "accuracy")} {pct(m, "precision")} {pct(m, "recall")} {pct(m, "fpr")}')

    long_rows = [r for r in rows if len(sentences(r['text'])) >= 10]
    print(f'\n   same idea, one population: the {len(long_rows)} reviews with at least 10 sentences '
          f'({sum(r["fake"] for r in long_rows)} deceptive), shown 1, 3 or 10 sentences')
    cv_long_scores = {}
    for k in (1, 3, 10):
        y, pred = [], []
        for f in folds_of(rows):
            train = [r for r in rows if r['fold'] != f]
            nb = NaiveBayes().fit([r['text'] for r in train], [r['fake'] for r in train])
            for r in long_rows:
                if r['fold'] == f:
                    y.append(r['fake']); pred.append(int(nb.score(first_k(r['text'], k)) > 0))
        m = metrics(y, pred)
        cv_long_scores[str(k)] = m
        print(f'   {str(k) + (" sentences" if k > 1 else " sentence"):18} {pct(m, "accuracy")} {pct(m, "precision")} {pct(m, "recall")} {pct(m, "fpr")}')
    res['length_long_subset'] = {'n': len(long_rows), **cv_long_scores}

    print(f'\n4. AUTO-DELETE MODE  threshold set on training hotels so at most {100 * STRICT_FPR:.0f}% of real reviews are flagged')
    print(f'   {"text seen":18} {"precision":20} {"recall":20} {"false accusation":20}')
    res['strict'] = {}
    for k in lengths:
        m = metrics(cv['nb_strict'][str(k)]['y'], cv['nb_strict'][str(k)]['pred'])
        res['strict'][str(k)] = m
        label = 'whole review' if k is None else f'{k} sentence' + ('s' if k > 1 else '')
        print(f'   {label:18} {pct(m, "precision")} {pct(m, "recall")} {pct(m, "fpr")}')

    print('\n5. UNSEEN DOMAIN  train on one sentiment, test on the other (and on unseen hotels)')
    tr = transfer(rows)
    res['transfer'] = tr
    for key in ('positive->positive', 'positive->negative', 'negative->negative', 'negative->positive'):
        m = tr[key]
        print(f'   {key:20} accuracy {pct(m, "accuracy")}  precision {pct(m, "precision")}  recall {pct(m, "recall")}  false accusation {pct(m, "fpr")}')

    print(f'\n6. PROJECTION (arithmetic, not measured)  10,000 reviews, {100 * PREVALENCE:.1f}% fake as Tripadvisor reported for 2022')
    res['projection'] = {}
    for label, m in (('flag mode, whole review', full), ('flag mode, 1 sentence', res['length']['1']),
                     ('auto-delete mode, whole review', res['strict']['None']),
                     ('auto-delete mode, 3 sentences', res['strict']['3'])):
        p = project(m['recall']['value'], m['fpr']['value'])
        res['projection'][label] = p
        print(f'   {label:32} catches {p["fakes_flagged"]:4} of {p["fake_reviews"]} fakes · wrongly flags {p["real_flagged"]:4} real · '
              f'precision {100 * p["precision"]:4.1f}%')

    qz = quiz(rows, cv)
    res['quiz'] = qz
    right = sum(q['truth'] == q['model_says'] for q in qz)
    print(f'\n7. VIEWER QUIZ  10 positive reviews from fold 1, 60-110 words; the model (never trained on these hotels) gets {right}/10')
    print('   ' + ' '.join(f'{q["q"]}:{q["truth"][0]}' for q in qz) + '   (texts: python3 review_lab.py --quiz)')

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / 'local-results.json').write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(f'\nwrote {(RESULTS / "local-results.json").relative_to(HERE)}')
    return 0


def show_quiz() -> int:
    rows = {r['id']: r for r in load()}
    path = RESULTS / 'local-results.json'
    if not path.exists():
        raise SystemExit('run python3 review_lab.py first')
    qz = json.loads(path.read_text())['quiz']
    for q in qz:
        print(f'--- {q["q"]} ---\n{rows[q["id"]]["text"]}\n')
    print('answers: ' + ' '.join(f'{q["q"]}={q["truth"]}' for q in qz))
    print('Corpus CC BY-NC-SA 3.0 (Ott et al.). Credit the authors wherever these texts are shown.')
    return 0


# ---------------------------------------------------------------- self-test

def selftest() -> int:
    checks = []

    def ok(name, cond):
        checks.append(bool(cond))
        print(('ok  ' if cond else 'FAIL') + ' ' + name)

    ok('sentences split on . ! ?', len(sentences('We loved it. The bed was small! Would we return? Yes.')) == 4)
    ok('first_k keeps k sentences', first_k('A b. C d. E f.', 2) == 'A b. C d.')
    ok('first_k None keeps all', first_k('A b. C d.', None) == 'A b. C d.')
    ok('features add word pairs', 'the bed' in features('The bed'))
    lo, hi = wilson(8, 10)
    ok('Wilson 8/10 ~ [0.49, 0.94]', abs(lo - 0.490) < 0.01 and abs(hi - 0.943) < 0.01)
    m = metrics([1, 1, 0, 0, 0], [1, 0, 1, 0, 0])
    ok('metrics: precision 1/2, recall 1/2, FPR 1/3',
       m['precision']['value'] == 0.5 and m['recall']['value'] == 0.5 and abs(m['fpr']['value'] - 1 / 3) < 1e-9)
    p = project(0.9, 0.1, 0.044, 10_000)
    ok('projection: 0.9 recall, 10% FPR at 4.4% -> precision ~ 29%', abs(p['precision'] - 0.2929) < 0.001)
    fake = ['My husband and I loved my stay, I would return, my favourite!'] * 20
    real = ['The bathroom was small and the elevator two blocks from the station was slow.'] * 20
    nb = NaiveBayes().fit(fake + real, [1] * 20 + [0] * 20)
    ok('NB separates toy fake/real', nb.score(fake[0]) > 0 > nb.score(real[0]))
    ok('NB is neutral on unseen text', abs(nb.score('')) < 1e-9)
    ru = Rules().fit(fake + real, [1] * 20 + [0] * 20)
    ok('rules flag the I-heavy toy review', ru.predict(fake[0]) == 1 and ru.predict(real[0]) == 0)
    print(f'{sum(checks)}/{len(checks)} checks passed')
    return 0 if all(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--quiz', action='store_true', help='print the viewer quiz texts (needs a previous run)')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--no-sklearn', action='store_true', help='skip the optional sklearn robustness line')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.quiz:
        return show_quiz()
    return main_run(args)


if __name__ == '__main__':
    sys.exit(main())
