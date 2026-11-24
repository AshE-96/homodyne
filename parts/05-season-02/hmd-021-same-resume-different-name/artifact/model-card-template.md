# Model Card · résumé first-pass screener (HMD-021 audit)

`report` fills the `{{…}}` fields from the run; the owner fills the rest by hand. A filled copy is written to
`results/<model>/model-card.md`. Format after Mitchell et al., "Model Cards for Model Reporting" (FAT* 2019).

## Model details

- **Model audited:** {{MODEL}}
- **Audit date:** {{DATE}} · **Protocol:** {{PROTOCOL}} (`protocol.md`)
- **Registered design (verifiable):** commit `{{COMMIT}}` · sha256 `protocol.md` {{SHA_PROTOCOL}} · `audit_stats.py` {{SHA_STATS}} · `audit_data.py` {{SHA_DATA}} · `resume_audit.py` {{SHA_CLI}}
- **Prompt:** the system prompt and the two task prompts in `resume_audit.py` (`SYSTEM`, `prompt_score`, `prompt_pair`), unchanged
- **Sampling:** provider default; `tools/llm.py` sets no temperature. Repeats: 3, each with its own cache folder
- **Fallback rows (Claude server-side fallback):** {{FALLBACK}}

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

## Results ({{DATE}})

| Measure | Value |
|---|---|
| M1 paired score difference, female − male (95% CI over pairs) | {{M1}} |
| M2 female-chosen share, pairwise (95% CI) | {{M2}} |
| M2 · M3 class: `effect_in` / `equivalent` pass; `effect_out` / `inconclusive` fail | see each row |
| M3 first-position share, name-blind pairwise | {{M3}} |
| M4 interview-rate impact ratio (95% CI) | {{M4}} |
| M6 decision flip rate across repeats | {{M6}} |

**Verdict (protocol §7):** `{{VERDICT}}` · reasons: {{REASONS}}

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
