# Flag or delete? A one-page card for any "this is fake" / "AI wrote this" detector

Homodyne HMD-013. Use it before a detector is allowed to act on people's text.

## Three questions before you trust the score

1. **How much text did it see?** In our run on the Ott corpus, the same model accused 39% of honest reviews when it saw one sentence, and 17% when it saw the whole review. OpenAI called its own AI-text classifier "very unreliable" below 1,000 characters. Turnitin raised its minimum from 150 to 300 words.
2. **What share of honest people does it accuse?** Ask for the false-accusation rate (false positive rate), not only accuracy. Ask it per group: Liang et al. (2023) found seven AI-text detectors labelled on average 61% of non-native writers' TOEFL essays as AI-written.
3. **How rare is the thing it looks for?** At 4.4% fakes (the share Tripadvisor reported for 2022, by its own detection), our 88%-accurate model would flag about 1,649 honest reviews to catch 409 fakes per 10,000. That is arithmetic, not a measurement.

## The decision (our default)

| Evidence | Allowed action |
|---|---|
| Text score alone | **Flag** for human review. The text stays visible until a person decides. Never auto-delete. |
| Text score + independent evidence (e.g. a confirmed paid-review network, no matching booking) | A person may remove it. The reason is recorded. |
| "AI wrote this" on student work | The score is never the only evidence. Talk to the student, look at drafts and history. No score below the tool's own minimum length. |

## Appeal design

- Tell the writer that the text was flagged or removed, and which rule fired, in plain words.
- One-step appeal. Accept simple proof: a booking receipt, a photo from the stay, a draft history.
- A person answers the appeal, not the same model. Set and publish a response time.
- If the appeal wins: restore the text, apologise, and log the case as a wrongful removal.

## Measure the cost of a wrongful removal

- Count wrongful removals every month from **two** sources: appeals that won, and a random audit of removals nobody appealed (most people never appeal).
- Report it per 10,000 decisions, next to how many fakes were caught.
- Write down the cost: an honest writer silenced, a real (often negative) review the next traveller never sees, and lost trust in the platform.

## What a text score can and cannot say

- It says how much a text **resembles** texts from one group in the training data.
- It cannot prove that a person lied or that a machine wrote the text. Research deception (paid crowd-workers) is not all real-world fraud.
