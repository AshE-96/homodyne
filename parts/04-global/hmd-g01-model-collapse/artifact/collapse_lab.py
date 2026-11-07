#!/usr/bin/env python3
"""Homodyne HMD-G01 - model collapse lab (ILLUSTRATIVE, synthetic data).

What it does
  Two toy "models" are trained, generation after generation, on data produced
  by the previous generation. Three data regimes are compared:
    replace     each generation trains ONLY on the previous generation's output
    keep10      each generation trains on 10% original real data + 90% synthetic
    accumulate  each generation trains on ALL data so far (real + every
                synthetic generation), as in Gerstgrasser et al. 2024

  Experiment 1 - Gaussian (the smallest possible "model")
    Real data: n draws from N(0, 1). A model = (mean, std) fitted by maximum
    likelihood. Reported: median fitted std across runs, and the probability
    mass the fitted model puts beyond |x| > 2 (true value: 4.55%).

  Experiment 2 - word frequencies (a unigram "language model")
    Real data: a corpus of N tokens drawn from a Zipf vocabulary of V word
    types (or your own text with --text). A model = word counts. Each
    generation samples a new corpus of N tokens from the counts. Reported:
    how many distinct word types survive, how many of the rarest half of the
    original vocabulary survive, and the effective vocabulary size
    exp(entropy). A word that hits zero never
    returns: the same arithmetic as genetic drift (Wright-Fisher model).

What it is NOT
  Not a large language model and not real web data. It shows the mechanism
  Shumailov et al. (Nature, 2024) describe, on toys small enough to read.

Standard library only. Python 3.9+.
  python3 collapse_lab.py                  # full report, writes results-<seed>.md/.json
  python3 collapse_lab.py --quick          # fewer runs, for a live demo
  python3 collapse_lab.py --seed 7         # robustness check
  python3 collapse_lab.py --text book.txt  # experiment 2 on your own text
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRUE_TAIL = 2 * (1 - 0.5 * (1 + math.erf(2 / math.sqrt(2))))  # P(|z| > 2) = 0.0455
GAUSS_REPORT = [0, 1, 10, 50, 100, 200, 500, 1000]
WORD_REPORT = [0, 1, 5, 10, 20, 50, 100]


def tail_mass(mu: float, sigma: float) -> float:
    """Mass a fitted N(mu, sigma) puts outside the ORIGINAL +-2 range."""
    if sigma <= 0:
        return 0.0
    cdf = lambda x: 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))
    return cdf(-2) + (1 - cdf(2))


def gaussian_run(rng: random.Random, regime: str, n: int, gens: int) -> list[tuple[float, float]]:
    """Return (mu, sigma) fitted at every generation 0..gens."""
    real = [rng.gauss(0, 1) for _ in range(n)]
    s, ss, count = sum(real), sum(x * x for x in real), n  # running sums for accumulate
    mu = s / n
    sigma = math.sqrt(max(ss / n - mu * mu, 0.0))
    fits = [(mu, sigma)]
    for _ in range(gens):
        if regime == 'replace':
            data = [rng.gauss(mu, sigma) for _ in range(n)]
        elif regime == 'keep10':
            k = n // 10
            data = rng.sample(real, k) + [rng.gauss(mu, sigma) for _ in range(n - k)]
        elif regime == 'accumulate':
            new = [rng.gauss(mu, sigma) for _ in range(n)]
            s += sum(new)
            ss += sum(x * x for x in new)
            count += n
            mu = s / count
            sigma = math.sqrt(max(ss / count - mu * mu, 0.0))
            fits.append((mu, sigma))
            continue
        else:
            raise ValueError(regime)
        mu = sum(data) / len(data)
        sigma = math.sqrt(max(sum((x - mu) ** 2 for x in data) / len(data), 0.0))
        fits.append((mu, sigma))
    return fits


def zipf_corpus(rng: random.Random, vocab: int, tokens: int, s: float = 1.0) -> list[str]:
    weights = [1 / (r ** s) for r in range(1, vocab + 1)]
    return rng.choices([f'w{r:05d}' for r in range(1, vocab + 1)], weights=weights, k=tokens)


def text_corpus(path: Path) -> list[str]:
    return re.findall(r'\w+', path.read_text(encoding='utf-8').lower())


def word_run(rng: random.Random, regime: str, real: list[str], gens: int, rare: set[str]) -> list[dict]:
    """Return per-generation stats for the unigram model."""
    n = len(real)
    counts = Counter(real)
    pool = Counter(real)  # for accumulate
    out = []
    for g in range(gens + 1):
        total = sum(counts.values())
        entropy = -sum(c / total * math.log(c / total) for c in counts.values())
        out.append({
            'types': len(counts),
            'rare_alive': sum(1 for w in counts if w in rare),
            'effective_vocab': math.exp(entropy),
        })
        if g == gens:
            break
        words, weights = zip(*counts.items())
        new = rng.choices(words, weights=weights, k=n)
        if regime == 'replace':
            counts = Counter(new)
        elif regime == 'keep10':
            counts = Counter(rng.sample(real, n // 10) + new[: n - n // 10])
        elif regime == 'accumulate':
            pool.update(new)
            counts = Counter(pool)
        else:
            raise ValueError(regime)
    return out


def median(xs):
    return statistics.median(xs)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--quick', action='store_true', help='fewer runs (live demo)')
    ap.add_argument('--n', type=int, default=100, help='samples per generation (Gaussian)')
    ap.add_argument('--vocab', type=int, default=5000)
    ap.add_argument('--tokens', type=int, default=20000)
    ap.add_argument('--text', type=Path, help='use your own text for experiment 2')
    ap.add_argument('--out-dir', type=Path, default=HERE)
    args = ap.parse_args()

    g_runs, w_runs = (20, 5) if args.quick else (200, 20)
    regimes = ['replace', 'keep10', 'accumulate']
    rng = random.Random(args.seed)

    # Experiment 1
    gauss = {}
    for regime in regimes:
        runs = [gaussian_run(rng, regime, args.n, GAUSS_REPORT[-1]) for _ in range(g_runs)]
        gauss[regime] = {
            g: {
                'median_sigma': round(median(r[g][1] for r in runs), 4),
                'median_tail_pct': round(100 * median(tail_mass(*r[g]) for r in runs), 3),
                'share_runs_sigma_below_0.5': round(sum(r[g][1] < 0.5 for r in runs) / g_runs, 3),
            }
            for g in GAUSS_REPORT
        }

    # Experiment 2
    if args.text:
        real = text_corpus(args.text)
        source = f'text file {args.text.name} ({len(real)} tokens)'
    else:
        real = zipf_corpus(rng, args.vocab, args.tokens)
        source = f'synthetic Zipf corpus (vocab {args.vocab}, {args.tokens} tokens, s=1.0)'
    ranked = [w for w, _ in Counter(real).most_common()]
    rare = set(ranked[len(ranked) // 2:])
    words = {}
    for regime in regimes:
        runs = [word_run(rng, regime, real, WORD_REPORT[-1], rare) for _ in range(w_runs)]
        words[regime] = {
            g: {
                'median_types': median(r[g]['types'] for r in runs),
                'median_rare_alive': median(r[g]['rare_alive'] for r in runs),
                'median_effective_vocab': round(median(r[g]['effective_vocab'] for r in runs), 1),
            }
            for g in WORD_REPORT
        }

    result = {
        'label': 'ILLUSTRATIVE - synthetic toy data, not web data, not an LLM',
        'seed': args.seed,
        'gaussian': {'n_per_generation': args.n, 'runs': g_runs,
                     'true_tail_pct': round(100 * TRUE_TAIL, 3), 'by_regime': gauss},
        'words': {'source': source, 'runs': w_runs, 'original_types': len(ranked),
                  'rare_half_types': len(rare), 'by_regime': words},
    }

    lines = [
        f'# HMD-G01 collapse lab - seed {args.seed}',
        '',
        '**ILLUSTRATIVE.** Synthetic toy data. Shows the mechanism, not the size of any real-world effect.',
        '',
        f'## Experiment 1 - Gaussian (n = {args.n} per generation, {g_runs} runs, medians)',
        '',
        f'True std = 1.000 · true mass beyond |x| > 2 = {100 * TRUE_TAIL:.2f}%',
        '',
        '| generation | ' + ' | '.join(f'{r} std' for r in regimes) + ' | ' + ' | '.join(f'{r} tail %' for r in regimes) + ' |',
        '|---:|' + '---:|' * (2 * len(regimes)),
    ]
    for g in GAUSS_REPORT:
        lines.append(f'| {g} | ' + ' | '.join(f"{gauss[r][g]['median_sigma']:.3f}" for r in regimes) + ' | '
                     + ' | '.join(f"{gauss[r][g]['median_tail_pct']:.2f}" for r in regimes) + ' |')
    lines += ['', 'Share of runs whose fitted std fell below 0.5: '
              + ', '.join(f"{r} {100 * gauss[r][1000]['share_runs_sigma_below_0.5']:.0f}%" for r in regimes)
              + ' (generation 1000).', '',
              f'## Experiment 2 - word frequencies ({source}, {w_runs} runs, medians)', '',
              f'Original distinct words: {len(ranked)} · rarest half = {len(rare)} words', '',
              '| generation | ' + ' | '.join(f'{r} words' for r in regimes) + ' | '
              + ' | '.join(f'{r} rare alive' for r in regimes) + ' | '
              + ' | '.join(f'{r} eff. vocab' for r in regimes) + ' |',
              '|---:|' + '---:|' * (3 * len(regimes))]
    for g in WORD_REPORT:
        lines.append(f'| {g} | ' + ' | '.join(f"{words[r][g]['median_types']:.0f}" for r in regimes) + ' | '
                     + ' | '.join(f"{words[r][g]['median_rare_alive']:.0f}" for r in regimes) + ' | '
                     + ' | '.join(f"{words[r][g]['median_effective_vocab']:.0f}" for r in regimes) + ' |')
    report = '\n'.join(lines) + '\n'
    print(report)

    if not args.quick:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        stem = f'results-seed{args.seed}' + ('-text' if args.text else '')
        (args.out_dir / f'{stem}.md').write_text(report, encoding='utf-8')
        (args.out_dir / f'{stem}.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(f'wrote {stem}.md and {stem}.json')


if __name__ == '__main__':
    main()
