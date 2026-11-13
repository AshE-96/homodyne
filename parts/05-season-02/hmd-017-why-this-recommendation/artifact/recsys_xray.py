#!/usr/bin/env python3
"""HMD-017 · A small recommender, X-rayed.

An item-item recommender on MovieLens ml-latest-small, with two ranking policies:

  similarity  rank candidates by how close they are to what you already watched
  mmr         Maximal Marginal Relevance (Carbonell & Goldstein 1998):
              pick greedily by  lam * relevance - (1 - lam) * max genre-overlap
              with the films already on the list. lam = 1 is pure similarity.

Two experiments, kept apart on purpose:

  OFFLINE (real ratings): per-user time split, last 20% of each user's ratings
      held out. NDCG@10 (held-out films rated >= 4 count as relevant),
      intra-list genre diversity, distinct genres per list, catalogue coverage.
      Paired bootstrap over users for the NDCG change.

  SIMULATION (ILLUSTRATIVE): two simulated users with the same five starting
      films and the same click rule; they differ by ONE click. Each round the
      system shows ten films and each user clicks one (position bias: slot k
      is chosen with probability proportional to 1/k; both users share the
      same random numbers). We track how far their feeds drift apart.
      Simulated users have no taste of their own. This says nothing about
      real people, real taste or YouTube's real system.

Usage:
    python3 fetch_movielens.py           # once; downloads and verifies the data
    python3 recsys_xray.py               # run everything, write results/
    python3 recsys_xray.py --selftest    # offline, no data needed, < 2 s
    python3 recsys_xray.py --report      # print frame-ready numbers from results/

Needs Python 3.9+ and numpy.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "ml-latest-small"
OUT = HERE / "results"

# Decided before the first run and not tuned afterwards.
CONFIG = {
    "test_fraction": 0.2,          # last 20% of each user's ratings (by time) held out
    "relevant_rating": 4.0,        # a held-out film rated >= 4 is "relevant" for NDCG
    "min_train_ratings": 5,        # catalogue = films with >= 5 training ratings and >= 1 genre
    "shrink": 10.0,                # cosine shrinkage for item-item similarity
    "k": 10,                       # list length
    "pool": 100,                   # MMR re-ranks the top 100 candidates
    "lambdas": [1.0, 0.9, 0.8, 0.7, 0.6, 0.5],
    "product_lambda": 0.7,         # the option the product decision is about
    "bootstrap": 2000,
    "seed": 0,
    "sim_rounds": 20,
    "sim_runs": 200,
    "sim_start": ["Toy Story (1995)", "Forrest Gump (1994)", "Jurassic Park (1993)",
                  "Matrix, The (1999)", "Shawshank Redemption, The (1994)"],
    # First run used "Silence of the Lambs, The (1991)" as click A. It was already in the
    # starting list, so one of its "changes" was only the film itself leaving the list.
    # Replaced (before any write-up) by a film of similar popularity that was not in it.
    "sim_click_a": "Shining, The (1980)",
    "sim_click_b": "Sleepless in Seattle (1993)",
}
DROP_GENRES = {"(no genres listed)", "IMAX"}  # IMAX is a screen format, not a genre


# ---------------------------------------------------------------- core maths

def item_similarity(X: np.ndarray, shrink: float) -> np.ndarray:
    """Cosine similarity between item columns of a binary user x item matrix, with shrinkage."""
    co = X.T @ X
    n = np.diag(co).astype(float)
    S = co / (np.sqrt(np.outer(n, n)) + shrink)
    np.fill_diagonal(S, 0.0)
    return S


def genre_jaccard(G: np.ndarray) -> np.ndarray:
    """Jaccard overlap of genre sets, item x item."""
    inter = G @ G.T
    size = G.sum(1)
    union = size[:, None] + size[None, :] - inter
    return np.where(union > 0, inter / np.maximum(union, 1), 0.0)


def scores_for(S: np.ndarray, history: list[int]) -> np.ndarray:
    s = S[history].sum(0) if history else np.zeros(S.shape[0])
    s = s.astype(float).copy()
    s[history] = -np.inf
    return s


def recommend(S: np.ndarray, GJ: np.ndarray, history: list[int], k: int, lam: float, pool: int) -> list[int]:
    """lam = 1: pure similarity. lam < 1: MMR with genre overlap as redundancy."""
    s = scores_for(S, history)
    order = np.argsort(-s, kind="stable")
    if lam >= 1.0:
        return [int(i) for i in order[:k]]
    cand = [int(i) for i in order[:pool] if np.isfinite(s[i])]
    top = max(s[cand[0]], 1e-12)
    rel = {i: s[i] / top for i in cand}
    chosen: list[int] = []
    while cand and len(chosen) < k:
        best, best_v = None, -np.inf
        for i in cand:
            red = max((GJ[i, j] for j in chosen), default=0.0)
            v = lam * rel[i] - (1 - lam) * red
            if v > best_v:
                best, best_v = i, v
        chosen.append(best)
        cand.remove(best)
    return chosen


def ndcg_at_k(ranked: list[int], relevant: set[int], k: int) -> float:
    dcg = sum(1.0 / math.log2(r + 2) for r, i in enumerate(ranked[:k]) if i in relevant)
    ideal = sum(1.0 / math.log2(r + 2) for r in range(min(len(relevant), k)))
    return dcg / ideal if ideal else 0.0


def intra_list_diversity(items: list[int], GJ: np.ndarray) -> float:
    """Mean genre distance (1 - Jaccard) over all pairs in the list."""
    pairs = [(a, b) for x, a in enumerate(items) for b in items[x + 1:]]
    return float(np.mean([1 - GJ[a, b] for a, b in pairs])) if pairs else 0.0


def genre_entropy(items: list[int], G: np.ndarray) -> float:
    """Shannon entropy (bits) of the genre mix; a film with n genres adds 1/n to each."""
    w = (G[items] / np.maximum(G[items].sum(1, keepdims=True), 1)).sum(0)
    p = w[w > 0] / w.sum()
    return float(-(p * np.log2(p)).sum())


def distinct_genres(items: list[int], G: np.ndarray) -> int:
    return int((G[items].sum(0) > 0).sum())


def jaccard(a: list[int], b: list[int]) -> float:
    A, B = set(a), set(b)
    return len(A & B) / len(A | B) if A | B else 1.0


# ---------------------------------------------------------------- data

def load():
    if not (DATA / "ratings.csv").exists():
        sys.exit("data missing: run  python3 fetch_movielens.py  first")
    movies = {}
    with open(DATA / "movies.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            movies[int(r["movieId"])] = (r["title"], [g for g in r["genres"].split("|") if g not in DROP_GENRES])
    rows = []
    with open(DATA / "ratings.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((int(r["userId"]), int(r["movieId"]), float(r["rating"]), int(r["timestamp"])))
    return movies, rows


def split(rows, frac):
    by_user: dict[int, list] = {}
    for u, m, r, t in rows:
        by_user.setdefault(u, []).append((t, m, r))
    train, test = {}, {}
    for u, lst in by_user.items():
        lst.sort()
        n_test = max(1, round(len(lst) * frac))
        train[u] = [(m, r) for _, m, r in lst[:-n_test]]
        test[u] = [(m, r) for _, m, r in lst[-n_test:]]
    return train, test


def build(movies, train, cfg):
    counts: dict[int, int] = {}
    for lst in train.values():
        for m, _ in lst:
            counts[m] = counts.get(m, 0) + 1
    cat = sorted(m for m, c in counts.items() if c >= cfg["min_train_ratings"] and movies[m][1])
    idx = {m: i for i, m in enumerate(cat)}
    users = sorted(train)
    X = np.zeros((len(users), len(cat)), dtype=np.float32)
    for ui, u in enumerate(users):
        for m, _ in train[u]:
            if m in idx:
                X[ui, idx[m]] = 1.0
    genres = sorted({g for m in cat for g in movies[m][1]})
    G = np.zeros((len(cat), len(genres)), dtype=np.float32)
    for m in cat:
        for g in movies[m][1]:
            G[idx[m], genres.index(g)] = 1.0
    return cat, idx, users, X, G, genres


# ---------------------------------------------------------------- experiments

def paired_ci(diff, base, rng, n):
    """Paired bootstrap over users: absolute and relative change of the mean, 95%."""
    absd, rel = [], []
    for _ in range(n):
        s = rng.integers(0, len(diff), len(diff))
        absd.append(diff[s].mean())
        rel.append(diff[s].mean() / base[s].mean())
    return ([float(np.percentile(absd, 2.5)), float(np.percentile(absd, 97.5))],
            [float(np.percentile(rel, 2.5)), float(np.percentile(rel, 97.5))])


def offline(cfg, train, test, idx, users, S, G, GJ, pop):
    rng = np.random.default_rng(cfg["seed"])
    k, rows, per_user = cfg["k"], [], {}
    eval_users = []
    for u in users:
        hist = [idx[m] for m, _ in train[u] if m in idx]
        rel = {idx[m] for m, r in test[u] if m in idx and r >= cfg["relevant_rating"]}
        if hist and rel:
            eval_users.append((hist, rel))
    pop_order = [int(i) for i in np.argsort(-pop, kind="stable")]
    policies = [("popular", None)] + [(f"lambda={lam}", lam) for lam in cfg["lambdas"]]
    for name, lam in policies:
        nd, ild, dg, pp, seen = [], [], [], [], set()
        for hist, rel in eval_users:
            if lam is None:   # reference: the most-rated films the user has not rated yet
                h = set(hist)
                rec = [i for i in pop_order if i not in h][:k]
            else:
                rec = recommend(S, GJ, hist, k, lam, cfg["pool"])
            nd.append(ndcg_at_k(rec, rel, k))
            ild.append(intra_list_diversity(rec, GJ))
            dg.append(distinct_genres(rec, G))
            pp.append(float(pop[rec].mean()))
            seen.update(rec)
        per_user[name] = np.array(nd)
        rows.append({"policy": name, "lambda": lam, "ndcg10": float(np.mean(nd)), "ild": float(np.mean(ild)),
                     "distinct_genres": float(np.mean(dg)), "coverage": len(seen) / S.shape[0],
                     "items_recommended": len(seen), "mean_popularity": float(np.mean(pp))})
    base = per_user["lambda=1.0"]
    for r in rows:
        if r["lambda"] is not None and r["lambda"] < 1.0:
            diff = per_user[r["policy"]] - base
            r["ndcg_diff_vs_similarity"] = float(diff.mean())
            r["ndcg_rel_change"] = float(diff.mean() / base.mean())
            r["ndcg_diff_ci95"], r["ndcg_rel_change_ci95"] = paired_ci(diff, base, rng, cfg["bootstrap"])
    # Is similarity really better than the popular reference? Same paired bootstrap (drawn after the
    # lambda comparisons, so their intervals are unchanged).
    pop_base = per_user["popular"]
    diff = base - pop_base
    abs_ci, rel_ci = paired_ci(diff, pop_base, rng, cfg["bootstrap"])
    sim_vs_pop = {"ndcg_diff": float(diff.mean()), "ndcg_rel_change": float(diff.mean() / pop_base.mean()),
                  "ndcg_diff_ci95": abs_ci, "ndcg_rel_change_ci95": rel_ci}
    return {"users_evaluated": len(eval_users), "catalogue_items": int(S.shape[0]), "policies": rows,
            "similarity_vs_popular": sim_vs_pop}


def one_click_demo(cfg, movies, cat, idx, S, GJ, G, pop):
    t2i = {movies[m][0]: idx[m] for m in cat}
    start = [t2i[t] for t in cfg["sim_start"]]
    a, b = t2i[cfg["sim_click_a"]], t2i[cfg["sim_click_b"]]
    out = {}
    for name, lam in (("similarity", 1.0), ("mmr", cfg["product_lambda"])):
        base = recommend(S, GJ, start, cfg["k"], lam, cfg["pool"])
        ra = recommend(S, GJ, start + [a], cfg["k"], lam, cfg["pool"])
        rb = recommend(S, GJ, start + [b], cfg["k"], lam, cfg["pool"])
        out[name] = {
            "start_list": [movies[cat[i]][0] for i in base],
            "after_click_a": [movies[cat[i]][0] for i in ra],
            "after_click_b": [movies[cat[i]][0] for i in rb],
            "changed_by_click_a": len(set(ra) - set(base)),
            "changed_by_click_b": len(set(rb) - set(base)),
            "shared_a_b": len(set(ra) & set(rb)),
        }
        out[name]["_ids"] = base
    # Why one click moves the list and the other does not (similarity policy):
    order = [int(i) for i in np.argsort(-scores_for(S, start), kind="stable")]
    rank = {i: r + 1 for r, i in enumerate(order)}
    base = recommend(S, GJ, start, cfg["k"], 1.0, cfg["pool"])
    explain = {}
    for label, c in (("click_a", a), ("click_b", b)):
        after = recommend(S, GJ, start + [c], cfg["k"], 1.0, cfg["pool"])
        neighbours = [int(i) for i in np.argsort(-S[c], kind="stable")[:3]]
        explain[label] = {
            "entered_list_rank_before": {movies[cat[i]][0]: rank[i] for i in after if i not in base},
            "nearest_films_rank_before": {movies[cat[i]][0]: rank.get(i) for i in neighbours},
        }
    out["why"] = explain
    # How typical are the two clicks? Every catalogue film with a similar number of training ratings
    # (0.8 x the smaller to 1.2 x the larger of the two clicks), not already in the starting list.
    lo, hi = 0.8 * min(pop[a], pop[b]), 1.2 * max(pop[a], pop[b])
    counts: dict[int, int] = {}
    for c in range(S.shape[0]):
        if c in start or not lo <= pop[c] <= hi:
            continue
        n = len(set(recommend(S, GJ, start + [c], cfg["k"], 1.0, cfg["pool"])) - set(base))
        counts[n] = counts.get(n, 0) + 1
    out["click_spread"] = {"rule": "films with lo..hi training ratings, not in the start list; similarity policy",
                           "lo": float(lo), "hi": float(hi), "candidates": sum(counts.values()),
                           "changed_of_10_distribution": {str(k): counts[k] for k in sorted(counts)},
                           "click_a_ratings": float(pop[a]), "click_b_ratings": float(pop[b])}
    sim_start, mmr_start = out["similarity"].pop("_ids"), out["mmr"].pop("_ids")
    out["knob"] = {"from_lambda": 1.0, "to_lambda": cfg["product_lambda"],
                   "changed": len(set(mmr_start) - set(sim_start))}
    return out


def simulate(cfg, movies, cat, idx, S, GJ, G, pop):
    """ILLUSTRATIVE feedback loop: two identical simulated users, one different click."""
    t2i = {movies[m][0]: idx[m] for m in cat}
    start = [t2i[t] for t in cfg["sim_start"]]
    a, b = t2i[cfg["sim_click_a"]], t2i[cfg["sim_click_b"]]
    k, R = cfg["k"], cfg["sim_rounds"]
    p = np.array([1 / (r + 1) for r in range(k)])
    cdf = np.cumsum(p / p.sum())
    res = {}
    for name, lam in (("similarity", 1.0), ("mmr", cfg["product_lambda"])):
        overlap = np.zeros((cfg["sim_runs"], R + 1))
        ent = np.zeros((cfg["sim_runs"], R + 1))
        dg = np.zeros((cfg["sim_runs"], R + 1))
        hist_genres = np.zeros((cfg["sim_runs"], R + 1))
        popm = np.zeros((cfg["sim_runs"], R + 1))
        shared = np.zeros((cfg["sim_runs"], R + 1))
        for run in range(cfg["sim_runs"]):
            rng = np.random.default_rng(cfg["seed"] + run)
            ha, hb = start + [a], start + [b]
            for t in range(R + 1):
                la = recommend(S, GJ, ha, k, lam, cfg["pool"])
                lb = recommend(S, GJ, hb, k, lam, cfg["pool"])
                overlap[run, t] = jaccard(la, lb)
                shared[run, t] = len(set(la) & set(lb))
                ent[run, t] = (genre_entropy(la, G) + genre_entropy(lb, G)) / 2
                dg[run, t] = (distinct_genres(la, G) + distinct_genres(lb, G)) / 2
                hist_genres[run, t] = (distinct_genres(ha, G) + distinct_genres(hb, G)) / 2
                popm[run, t] = (pop[la].mean() + pop[lb].mean()) / 2
                u = rng.random()                       # same random number for both users
                slot = int(np.searchsorted(cdf, u))
                ha.append(la[slot])
                hb.append(lb[slot])
        res[name] = {
            "overlap_mean": overlap.mean(0).round(4).tolist(),
            "shared_of_10_mean": shared.mean(0).round(2).tolist(),
            "entropy_mean": ent.mean(0).round(4).tolist(),
            "distinct_genres_mean": dg.mean(0).round(3).tolist(),
            "history_genres_mean": hist_genres.mean(0).round(3).tolist(),
            "list_popularity_mean": popm.mean(0).round(1).tolist(),
            "overlap_round0_p10_p90": [float(np.percentile(overlap[:, 0], 10)), float(np.percentile(overlap[:, 0], 90))],
            "overlap_last_p10_p90": [float(np.percentile(overlap[:, -1], 10)), float(np.percentile(overlap[:, -1], 90))],
        }
    # Control: with no different click and the same random numbers, the two feeds stay identical by construction.
    return {"label": "ILLUSTRATIVE", "rounds": R, "runs": cfg["sim_runs"],
            "click_rule": "slot k chosen with probability proportional to 1/k; same random numbers for both users",
            "start": cfg["sim_start"], "click_a": cfg["sim_click_a"], "click_b": cfg["sim_click_b"], **res}


def run() -> None:
    movies, rows = load()
    train, test = split(rows, CONFIG["test_fraction"])
    cat, idx, users, X, G, genres = build(movies, train, CONFIG)
    S = item_similarity(X, CONFIG["shrink"])
    pop = X.sum(0)  # training ratings per film
    GJ = genre_jaccard(G)
    print(f"ratings {len(rows)} · users {len(users)} · catalogue {len(cat)} films · {len(genres)} genres")
    off = offline(CONFIG, train, test, idx, users, S, G, GJ, pop)
    demo = one_click_demo(CONFIG, movies, cat, idx, S, GJ, G, pop)
    sim = simulate(CONFIG, movies, cat, idx, S, GJ, G, pop)
    OUT.mkdir(exist_ok=True)
    meta = {"dataset": "MovieLens ml-latest-small (GroupLens, generated 26 Sep 2018)",
            "dataset_sha256": "696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436",
            "model": "item-item cosine on binary 'rated' signal, numpy", "config": CONFIG,
            "ratings": len(rows), "users": len(users), "genres": genres}
    (OUT / "offline.json").write_text(json.dumps({**meta, **off}, indent=1, ensure_ascii=False))
    (OUT / "one_click.json").write_text(json.dumps(demo, indent=1, ensure_ascii=False))
    (OUT / "simulation.json").write_text(json.dumps(sim, indent=1, ensure_ascii=False))
    with open(OUT / "chart-data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["round", "shared_of_10_similarity", "shared_of_10_mmr", "overlap_similarity", "overlap_mmr", "entropy_similarity", "entropy_mmr",
                    "genres_in_list_similarity", "genres_in_list_mmr"])
        for t in range(sim["rounds"] + 1):
            w.writerow([t, sim["similarity"]["shared_of_10_mean"][t], sim["mmr"]["shared_of_10_mean"][t],
                        sim["similarity"]["overlap_mean"][t], sim["mmr"]["overlap_mean"][t],
                        sim["similarity"]["entropy_mean"][t], sim["mmr"]["entropy_mean"][t],
                        sim["similarity"]["distinct_genres_mean"][t], sim["mmr"]["distinct_genres_mean"][t]])
    report()


def report() -> None:
    off = json.loads((OUT / "offline.json").read_text())
    demo = json.loads((OUT / "one_click.json").read_text())
    sim = json.loads((OUT / "simulation.json").read_text())
    print(f"\nOFFLINE · real ratings · {off['users_evaluated']} users · catalogue {off['catalogue_items']} films")
    print(f"{'policy':>11} {'NDCG@10':>8} {'vs lambda=1 (95% CI)':>27} {'diversity':>9} {'genres':>6} {'coverage':>8} {'popularity':>10}")
    for r in off["policies"]:
        ci = ""
        if "ndcg_rel_change" in r:
            lo, hi = r["ndcg_rel_change_ci95"]
            ci = f"{r['ndcg_rel_change']:+.1%} [{lo:+.1%}, {hi:+.1%}]"
        print(f"{r['policy']:>11} {r['ndcg10']:>8.4f} {ci:>27} {r['ild']:>9.3f} {r['distinct_genres']:>6.2f} "
              f"{r['coverage']:>7.1%} {r['mean_popularity']:>10.1f}")
    sp = off["similarity_vs_popular"]
    print(f"similarity vs popular: NDCG {sp['ndcg_rel_change']:+.1%} "
          f"[{sp['ndcg_rel_change_ci95'][0]:+.1%}, {sp['ndcg_rel_change_ci95'][1]:+.1%}] (paired bootstrap, 95%)")
    print("\nONE CLICK · same five starting films")
    print(f"  knob lambda {demo['knob']['from_lambda']} -> {demo['knob']['to_lambda']}: {demo['knob']['changed']}/10 films change")
    for label, e in demo["why"].items():
        print(f"  {label}: entered (rank before) {e['entered_list_rank_before']} · nearest films (rank before) {e['nearest_films_rank_before']}")
    cs = demo["click_spread"]
    print(f"  spread: {cs['candidates']} films with {cs['lo']:.0f}-{cs['hi']:.0f} ratings, films changed by one click -> "
          + ", ".join(f"{k}: {v}" for k, v in cs["changed_of_10_distribution"].items()))
    for name in ("similarity", "mmr"):
        d = demo[name]
        print(f"  {name:>10}: click A changes {d['changed_by_click_a']}/10 · click B changes {d['changed_by_click_b']}/10 · "
              f"A and B share {d['shared_a_b']}/10")
    print(f"\nSIMULATION · ILLUSTRATIVE · {sim['runs']} paired runs · {sim['rounds']} rounds")
    for name in ("similarity", "mmr"):
        s = sim[name]
        print(f"  {name:>10}: shared films (of 10) round 0 {s['shared_of_10_mean'][0]:.1f} -> round 5 {s['shared_of_10_mean'][5]:.1f}"
              f" -> round 10 {s['shared_of_10_mean'][10]:.1f} -> round {sim['rounds']} {s['shared_of_10_mean'][-1]:.1f}")
        print(f"  {'':>10}  overlap (Jaccard) {s['overlap_mean'][0]:.2f} -> {s['overlap_mean'][-1]:.2f} · "
              f"genres in list {s['distinct_genres_mean'][0]:.1f} -> {s['distinct_genres_mean'][-1]:.1f} · "
              f"entropy {s['entropy_mean'][0]:.2f} -> {s['entropy_mean'][-1]:.2f} bits · "
              f"popularity {s['list_popularity_mean'][0]:.0f} -> {s['list_popularity_mean'][-1]:.0f}")


# ---------------------------------------------------------------- self-test

def selftest() -> int:
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("ok   " if cond else "FAIL ") + name)
        ok &= bool(cond)

    check("ndcg perfect list = 1", abs(ndcg_at_k([1, 2, 3], {1, 2, 3}, 10) - 1) < 1e-12)
    check("ndcg hit at rank 2 = 1/log2(3)", abs(ndcg_at_k([9, 1], {1}, 10) - 1 / math.log2(3)) < 1e-12)
    check("ndcg no hit = 0", ndcg_at_k([7, 8], {1}, 10) == 0)
    # 6 users x 6 items: items 0-2 "comedy" cluster, 3-5 "thriller" cluster
    X = np.array([[1, 1, 1, 0, 0, 0], [1, 1, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0],
                  [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 0], [0, 0, 1, 0, 1, 1]], dtype=np.float32)
    G = np.array([[1, 0], [1, 0], [1, 0], [0, 1], [0, 1], [0, 1]], dtype=np.float32)
    S, GJ = item_similarity(X, 0.0), genre_jaccard(G)
    check("similarity is symmetric with zero diagonal", np.allclose(S, S.T) and np.all(np.diag(S) == 0))
    pure = recommend(S, GJ, [0], 2, 1.0, 6)
    check("pure similarity keeps the cluster", set(pure) == {1, 2})
    mixed = recommend(S, GJ, [0], 2, 0.3, 6)
    check("MMR with low lambda mixes genres", distinct_genres(mixed, G) == 2)
    check("lambda = 1 returns the top of the similarity ranking", recommend(S, GJ, [0], 3, 1.0, 6)[:2] == pure)
    check("history is never recommended", 0 not in recommend(S, GJ, [0], 5, 0.5, 6))
    check("ILD of one genre = 0", intra_list_diversity([0, 1, 2], GJ) == 0)
    check("entropy of two balanced genres = 1 bit", abs(genre_entropy([0, 3], G) - 1) < 1e-12)
    check("jaccard", jaccard([1, 2], [2, 3]) == 1 / 3)
    check("same input, same output", recommend(S, GJ, [3], 3, 0.6, 6) == recommend(S, GJ, [3], 3, 0.6, 6))
    print("selftest " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="HMD-017 recommender X-ray")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.report:
        report()
    else:
        run()
