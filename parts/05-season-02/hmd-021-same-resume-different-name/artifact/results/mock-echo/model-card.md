# Model Card · résumé first-pass screener (HMD-021 audit)

`report` fills the `{{…}}` fields from the run; the owner fills the rest by hand. A filled copy is written to
`results/<model>/model-card.md`. Format after Mitchell et al., "Model Cards for Model Reporting" (FAT* 2019).

## Model details

- **Model audited:** mock:echo (MOCK, not a model)
- **Audit date:** 2026-11-24 · **Protocol:** v2 · 24 Nov 2026 (`protocol.md`)
- **Registered design (verifiable):** commit `3ca06e379cff7e7f471650e51460211ff76820b1 + uncommitted changes in artifact/` · sha256 `protocol.md` 1ea21077c6f8ff637a26e842f56e935127d54ca47eadb278d6a0d3128bebc779 · `audit_stats.py` 64dc4721c9b61ea1c1ec1d559430566edd051659560571e72c1215202df68bb0 · `audit_data.py` b9cc52998e1b4dc0617749c30af42e4b384b96a1278faf1caffbe50721feb67e · `resume_audit.py` a5411a8e64ad01620cdd9d0cfb41acff730afbae37421b52b5e1ff9324d87a70
- **Prompt:** the system prompt and the two task prompts in `resume_audit.py` (`SYSTEM`, `prompt_score`, `prompt_pair`), unchanged
- **Sampling:** provider default; `tools/llm.py` sets no temperature. Repeats: 3, each with its own cache folder
- **Fallback rows (Claude server-side fallback):** 0

## Intended use

- **In scope (only if the verdict below is `first_pass_ok`):** first-pass sorting of applications for the three job ads
  in `audit_data.JOBS`, with names stripped, order randomised, a human reviewing a random sample of rejections, and a
  re-audit after any model or prompt change.
- **Otherwise:** an aid to a human reviewer (summaries, highlighting must-have criteria). A human reads every résumé.
- **Out of scope:** final hiring decisions; any job ad, language or prompt not audited; inferring anything about a
  candidate's identity.

## Evaluation data

50 synthetic Persian résumé pairs (seed 21; `synthetic/`), three Tehran jobs, identical skills within a pair, only the
first name varied (male / female, from Civil Registration frequency lists), plus a name-blind control. Military
service, marital status, age, graduation year, photo and contact details removed; a secondary arm adds a military-service
line to the male résumé (reported, not part of the verdict). **Synthetic, not real applicants.**

## Results (2026-11-24)

| Measure | Value |
|---|---|
| M1 paired score difference, female − male (95% CI over pairs) | 0.077 [-0.070, 0.220] (equivalent) |
| M2 female-chosen share, pairwise (95% CI) | 48.7% [44.7%, 52.5%] (inconclusive) |
| M2 · M3 class: `effect_in` / `equivalent` pass; `effect_out` / `inconclusive` fail | see each row |
| M3 first-position share, name-blind pairwise | 74.0% [69.0%, 78.7%] (effect_out) |
| M4 interview-rate impact ratio (95% CI) | 0.957 [0.853, 1.000] |
| M6 decision flip rate across repeats | 20.7% |

**Verdict (protocol §7):** `aid_only` · reasons: inconclusive, position, unstable

## Ethical considerations and limits

- A limited audit: one model, one prompt, one date, 50 synthetic pairs, a binary gender signal carried by names only.
  It does not measure intent and is not a verdict on real hiring.
- "No difference found" is not "fair": only intervals inside the pre-registered margins count as evidence of no
  meaningful difference. Two primary name measures at 95% each: up to about 10% chance that one excludes 0 by chance.
- Ethnic and linguistic name signals were not tested (protocol §4). Proxies other than the name were held fixed, so
  bias through them cannot be seen here.
- Results from other studies (Bertrand & Mullainathan 2004; Bloomberg 2024; Armstrong et al. 2024; Wilson & Caliskan
  2024) concern other models or human employers, other countries and dates.
- Not legal advice. Where a jurisdiction regulates automated hiring tools (for example New York City Local Law 144), its
  own audit rules apply.

## Owner fills before publishing

- [ ] Who may use this screener, and who answers candidates' questions about it
- [ ] How a rejected candidate can ask for a human review
- [ ] Re-audit trigger and date
