#!/usr/bin/env python3
"""Ground truth for the nine replication questions (HMD-019).

This file is the answer key. It is NEVER copied into the agent's workspace, and on
macOS the sandbox denies the agent's code any read under the home folder, which
includes this repository.

Each function re-derives a number from the same data file the agent gets. The
self-test checks them against the numbers printed by the original episodes:
HMD-002 two_scores.py (crossover 0.0408, Konkur -1.0), HMD-006 bluff_lab.py
(A risk 28.6 %, B score +0.1) and HMD-010 penalty_threshold.py (0.130, 86 %, -0.385).

Standard library only.
"""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path

TASKS = Path(__file__).resolve().parent / 'tasks'


def _p1(folder):
    rows = {r['model']: r for r in csv.DictReader(open(folder / 'data/table.csv', encoding='utf-8'))}
    a, b = rows['OpenAI o4-mini'], rows['gpt-5-thinking-mini']
    acc = lambda r: float(r['accuracy_pct'])
    err = lambda r: float(r['error_pct'])
    score = lambda r, k: acc(r) - k * err(r)
    k_of = lambda t: t / (1 - t)
    return {
        'p1a': (acc(a) - acc(b)) / (err(a) - err(b)),
        'p1b': score(a, k_of(0.25)),
        'p1c': score(b, k_of(0.75)) - score(a, k_of(0.75)),
    }


def _p2(folder):
    rows = list(csv.DictReader(open(folder / 'data/labels.csv', encoding='utf-8')))

    def counts(model, lang=None):
        sel = [r for r in rows if r['model'] == model and (lang is None or r['language'] == lang)]
        c = sum(r['label'] == 'correct' for r in sel)
        w = sum(r['label'] == 'wrong' for r in sel)
        return len(sel), c, w

    n, c, w = counts('A')
    risk_a = 100 * w / (c + w)
    n, c, w = counts('B')
    score_b = (c - 3 * w) / n
    n, c, w = counts('A', 'fa')
    cover_a_fa = 100 * (c + w) / n
    return {'p2a': risk_a, 'p2b': score_b, 'p2c': cover_a_fa}


def _p3(folder):
    prm = json.loads((folder / 'data/params.json').read_text(encoding='utf-8'))
    rng = random.Random(prm['seed'])
    qs = []
    for _ in range(prm['n_questions']):
        p = min(prm['p_max'], max(prm['p_min'], rng.betavariate(prm['beta_a'], prm['beta_b'])))
        correct = rng.random() < p
        qs.append((p, min(prm['stated_max'], p + prm['overconfidence_shift']), correct))

    def policy(k, over):
        t = k / (k + 1)
        ans = right = wrong = 0
        for p, stated, ok in qs:
            if (stated if over else p) > t:
                ans += 1
                right += ok
                wrong += not ok
        n = len(qs)
        return (right - k * wrong) / n, 100 * ans / n

    return {'p3a': policy(3, False)[0], 'p3b': policy(1, True)[1], 'p3c': policy(9, True)[0]}


def truth() -> dict[str, float]:
    """All nine ground-truth values, keyed by question id."""
    out = {}
    out.update(_p1(TASKS / 'p1-rescoring'))
    out.update(_p2(TASKS / 'p2-four-numbers'))
    out.update(_p3(TASKS / 'p3-silence-line'))
    return out


if __name__ == '__main__':
    for qid, v in truth().items():
        print(f'{qid}  {v:.6f}')
