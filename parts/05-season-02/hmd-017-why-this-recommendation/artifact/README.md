# HMD-017 artifact · a small recommender, X-rayed

An item-item recommender on MovieLens `ml-latest-small`, two ranking policies, an offline test on real ratings and an ILLUSTRATIVE feedback-loop simulation. Python 3.9+ and numpy.

```bash
python3 recsys_xray.py --selftest     # offline, no data, under 2 s
python3 fetch_movielens.py            # downloads from GroupLens, checks SHA-256, unpacks to data/
python3 recsys_xray.py                # about 90 s on a laptop; writes results/
python3 recsys_xray.py --report       # prints the frame-ready numbers from results/
```

## What is here

| File | What it is |
|---|---|
| `recsys_xray.py` | Model, both policies, metrics, offline test, one-click demo, simulation, self-test |
| `fetch_movielens.py` | Downloads `ml-latest-small.zip` from GroupLens and verifies it (SHA-256 `696d65a3…`, MD5 matches GroupLens's `.md5`) |
| `results/offline.json` | Offline test per policy: NDCG@10, intra-list diversity, distinct genres, coverage, mean popularity, paired-bootstrap CIs, and similarity vs the most-rated reference |
| `results/one_click.json` | The five starting films, the list after each extra click, why (rank of the films that entered), and `click_spread` over 123 similar-popularity films |
| `results/simulation.json` | ILLUSTRATIVE feedback loop: shared films, Jaccard overlap, genre entropy, genres per list, popularity, per round |
| `results/chart-data.csv` | 21 rows (round 0–20) for the deck chart |
| `results/report.txt` | The printed report from the run of 13 Nov 2026 |
| `data/` | Downloaded data. Not committed (see `.gitignore` and the licence below) |

## Design, fixed before the first run

- **Signal:** binary "this person rated this film". Star values are ignored by the model and used only to define relevance in the test.
- **Model:** item-item cosine similarity with shrinkage 10. A user's score for a film is the sum of its similarity to the films in their history.
- **Policies:** `similarity` (λ = 1) ranks by that score. `mmr` re-ranks the top 100 greedily by `λ · relevance − (1 − λ) · max genre-Jaccard with the films already chosen` (Carbonell & Goldstein 1998). Relevance is the score divided by the top score. The product option is λ = 0.7.
- **Offline split:** per user, the last 20% of ratings by timestamp are held out. A held-out film rated ≥ 4 is relevant. Catalogue: films with ≥ 5 training ratings and at least one genre (3,037 films). IMAX and "(no genres listed)" are not genres here.
- **Metrics:** NDCG@10 with binary gain (Järvelin & Kekäläinen 2002); intra-list diversity = mean genre distance (1 − Jaccard) over pairs; distinct genres in the list; catalogue coverage = share of the catalogue recommended to at least one user; mean popularity = mean training ratings per listed film. Paired bootstrap over users (2,000 resamples, seed 0) for the change against λ = 1.
- **Simulation (ILLUSTRATIVE):** two simulated users start with the same five films and differ by one extra film. Each round both see ten films and click one: slot k with probability ∝ 1/k, using the same random number for both. 20 rounds, 200 paired runs. The users have no taste of their own, so with the same extra film they would stay identical for ever. All divergence comes from one click plus the loop.

One change after the first run, logged in `CONFIG`: click A was "Silence of the Lambs", which was already in the starting list, so one of its "changes" was only the film itself leaving. It was replaced by "The Shining" (88 training ratings, close to "Sleepless in Seattle" at 97) before anything was written up.

## Headline results (13 Nov 2026)

- λ = 0.7 against pure similarity: genres per list 10.9 → 13.4, coverage 294 → 328 films, NDCG@10 −3.2% [−9.9%, +3.6%]. The interval includes zero.
- λ = 0.5: NDCG@10 −12.6% [−20.2%, −4.7%], the same NDCG as showing each user the most-rated films they have not yet seen.
- Pure similarity against that most-rated reference: +14.5% [−1.2%, +33.3%]. The interval includes zero, so with 587 users this gap cannot be told from zero either.
- One click: The Shining changes 0 of 10; Sleepless in Seattle changes 4 of 10. Turning λ from 1 to 0.7 changes 5 of 10. These two clicks are the two ends of the spread: across 123 films with 70–116 training ratings, one click changed 0 films 13 times, 1 film 67 times, 2 films 25 times, 3 three, 4 nine, 5 six (`click_spread` in `results/one_click.json`). Sleepless in Seattle's own nearest films (ranks 69 and 80) did not enter; the four that did were already at ranks 11–25.
- Simulation (ILLUSTRATIVE): shared films fall from 6 of 10 to 0.9 (similarity) or 1.8 (λ = 0.7) after 20 rounds. Genres per list do not shrink under similarity (12.0 → 12.2). The listed films get less popular (204 → 134 ratings on average), partly by design: watched films are never suggested again, so the popular ones run out.

## What this does not show

- Anything about YouTube's real system. YouTube's published signals and its 2016 paper are context, not a description of today's code.
- Any change in a real person's taste. Simulated users have no taste. Measuring that needs a randomised study with real volunteers (for example Liu et al., PNAS 2025, on political opinions, not film taste).
- That offline NDCG predicts what happens live. The 2016 YouTube paper says live A/B results do not always match offline tests.
- That the simulation's "drift apart, not narrower" result is general. It depends on this model, this click rule and this starting profile. Chaney, Stewart & Engelhardt (RecSys 2018) report homogenisation in a different simulation design.

## Data licence

MovieLens is © GroupLens Research, University of Minnesota. The licence allows research use with acknowledgement, no implied endorsement, redistribution only under the same terms, and **no commercial or revenue-bearing use without permission**. This folder holds only small derived numbers; the data is fetched from GroupLens by each user.

Cite: F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets: History and Context. ACM TiiS 5(4): 19:1–19:19. doi:10.1145/2827872
