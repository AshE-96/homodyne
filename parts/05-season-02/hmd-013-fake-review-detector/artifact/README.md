# HMD-013 artifact · Review Trust Lab

Can you spot a fake review? Can AI? And how much text does an "AI wrote this" call need?

Run everything from the repository root. Python 3.9+; the local experiment uses the standard library only.

## 1. Get the data (once)

```bash
python3 parts/05-season-02/hmd-013-fake-review-detector/artifact/fetch_data.py
```

Downloads the **Deceptive Opinion Spam Corpus v1.4** (Ott, Choi, Cardie & Hancock 2011; Ott, Cardie & Hancock 2013) into `artifact/data/` and checks its SHA-256. 1,600 reviews of 20 Chicago hotels: 800 deceptive (written on Mechanical Turk by people who had not stayed there), 800 truthful (mined from review sites; presumed, not verified, truthful). The corpus's five folds are split by hotel.

**Licence:** CC BY-NC-SA 3.0 (non-commercial, attribution, share-alike). The data is **not** committed (`.gitignore`), and neither are model rewrites of it (`runs/`). Cite the two papers if you use it.

## 2. Local experiment (no API, about 2 minutes)

```bash
python3 parts/05-season-02/hmd-013-fake-review-detector/artifact/review_lab.py
python3 parts/05-season-02/hmd-013-fake-review-detector/artifact/review_lab.py --quiz       # the 10-review viewer quiz
python3 parts/05-season-02/hmd-013-fake-review-detector/artifact/review_lab.py --selftest   # 10 checks, no data needed
```

Simple rules vs a Naive Bayes model (words + word pairs), always tested on hotels the detector never saw, next to the human judges published by Ott et al. 2011. "Fake" is the accusation. Reported with 95% Wilson intervals: precision of the accusation, recall, false-accusation rate (honest reviews called fake); then the same as the detector sees 1, 3, 5 sentences or the whole review; a strict "auto-delete" threshold (≤ 1% honest reviews flagged on the training hotels); transfer to the other sentiment (unseen domain); and an arithmetic projection to a site with 4.4% fakes.

Committed outputs (13 Nov 2026, Python 3.11.7, seed 13; sklearn 1.7.2 only for the robustness line):

- [`results/local-output.txt`](results/local-output.txt) · [`results/local-results.json`](results/local-results.json) · [`results/local-selftest.txt`](results/local-selftest.txt)

Headline (whole reviews, unseen hotels): rules 69.4% accuracy (71.2% on the judges' 160 reviews), 32.0% of honest reviews accused · model 87.8% accuracy, precision 84.3%, recall 92.9%, 17.2% honest reviews accused · with one sentence the model accuses 38.6% · auto-delete threshold: 0.9% accused but only 35.4% of fakes caught · trained on positive, tested on negative: recall 94.5% → 65.5%.

## 3. AI-written text (needs a model key; NOT RUN YET)

```bash
export ANTHROPIC_API_KEY=...            # or GEMINI_API_KEY / OPENAI_API_KEY, see tools/llm.py
python3 parts/05-season-02/hmd-013-fake-review-detector/artifact/ai_text_lab.py plan      # what will be asked; no network
python3 parts/05-season-02/hmd-013-fake-review-detector/artifact/ai_text_lab.py run       # about 380 calls, cached in runs/cache/
python3 parts/05-season-02/hmd-013-fake-review-detector/artifact/ai_text_lab.py report    # Persian spoken lines for beats 9 and 10
HOMODYNE_MODEL=mock:echo python3 parts/05-season-02/hmd-013-fake-review-detector/artifact/ai_text_lab.py --selftest
```

`run` asks the model to write 80 hotel reviews as a guest who never stayed (20 hotels × 2 sentiments × 2), and to polish 30 truthful reviews ("keep every fact"). Then three detectors see the first 1, 3 or 10 sentences: the fake-review model from step 2 (does it call AI reviews fake?), a Naive Bayes "AI text" detector trained on human vs AI reviews from other hotels, and the model itself as judge ("probability this was written by AI", flag at ≥ 50). Results go to `results/api-results.json`; `report` prints the exact Persian sentences for the [RUN] beats. Self-test output: [`results/api-selftest.txt`](results/api-selftest.txt) (16/16, mock model, synthetic data).

Boundary: one generator model, one prompt style, English hotel reviews, and an "AI text" detector trained on that same generator. It says nothing about commercial detectors or about Persian text.

## 4. The decision card

[`flag-or-delete-card.md`](flag-or-delete-card.md): three questions before trusting a detector score, when a detector may flag vs delete, appeal design, and how to count wrongful removals.

## Sources

Ott et al. 2011 (ACL, arXiv 1107.4557) · Ott, Cardie & Hancock 2013 (NAACL, pp. 497–501) · Liang et al. 2023 (Patterns 4(7), 100779) · OpenAI AI classifier post (31 Jan 2023, withdrawn 20 Jul 2023) · Turnitin (23 May and 14 Jun 2023) · Tripadvisor Review Transparency Report (11 Apr 2023). Details: [`../sources.md`](../sources.md).
