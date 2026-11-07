---
title: "Prompt injection: can a document hijack your AI assistant?"
description: "Yes: to a language model, your request and a document arrive as one stream of words. Spotlighting helps; least privilege and approval limit the damage."
lang: en
translationKey: hmd-007-companion
hmd: HMD-007
kind: companion
date: 2027-01-01
tags: ["prompt injection", "indirect prompt injection", "AI assistant security", "spotlighting", "least privilege"]
sources:
  - title: "Anthropic: Mitigating the risk of prompt injections in browser use (24 Nov 2025)"
    url: "https://www.anthropic.com/research/prompt-injection-defenses"
  - title: "OWASP LLM01:2025 Prompt Injection"
    url: "https://genai.owasp.org/llmrisk/llm01-prompt-injection/"
  - title: "Hines et al. 2024, Defending Against Indirect Prompt Injection Attacks With Spotlighting (arXiv 2403.14720)"
    url: "https://arxiv.org/abs/2403.14720"
  - title: "Greshake et al. 2023, Not what you've signed up for (arXiv 2302.12173)"
    url: "https://arxiv.org/abs/2302.12173"
---

Yes. To a language model, your request and the text of the document it is reading arrive as a single stream of words, so a sentence planted in an invoice or an email can act like an instruction. Marking the document as "data" lowers the odds that the model is fooled, but the safer design is one where a fooled model still cannot reach anything dangerous.

This post accompanies [Homodyne episode HMD-007](/en/episodes/hmd-007/) and is written for readers who have not watched it. The offline lab, its metrics and how to plug in a real model are in the [deep dive for this episode](/en/blog/hmd-007-injection-lab/). The [Persian original](/fa/blog/hmd-007-prompt-injection/) is the canonical version.

> **Key takeaways**
> - Indirect prompt injection means instructions that reach the model through a document, email or web page rather than from the user. OWASP puts prompt injection first on its list of risks for LLM applications (LLM01:2025).
> - Spotlighting marks document text and asks the model to treat it as data only. It works only as well as the model honours that request.
> - Least privilege and human approval limit the damage even when the model is fooled, but they do not stop a misleading sentence in the answer.
> - In November 2025, Anthropic's chart showed a 1.4% attack success rate for Opus 4.5 with its improved safeguards against an adaptive attacker. Low, but not zero.
> - Our 20 test documents have not yet been run against a real model.

## What exactly is prompt injection?

Prompt injection is text that changes a model's behaviour or output in a way neither the app's builder nor the user wanted. OWASP's definition rests on that same idea: inputs that alter the model's behaviour or output "in unintended ways". OWASP, a well-known software security community, lists it as LLM01, the first entry in its risk list for LLM applications.

It comes in two forms. In direct injection, the user types the odd instruction. In indirect injection, the instruction sits inside content the assistant reads to do its job: an invoice, a quoted email, a web page. Greshake and colleagues introduced and studied this indirect form in LLM-integrated applications in 2023.

The episode opens with a scene. You ask your assistant to total this week's invoices. At the bottom of the third invoice, in white text on a white background, a line addressed to the assistant asks it to send a confidential file somewhere else. You cannot see that line. The model can.

This matters more now than a few years ago because assistants have tools. A chatbot that only talked could say something strange and you would read it and move on. An assistant that can send email or open files turns words into actions.

## Why can't the model separate instructions from data?

Because both arrive in one stream of words, and the model has to guess the boundary from the words themselves. A human secretary reading a letter aloud who reaches a line addressed to "dear secretary" knows it is part of the letter, because they know where the letter came from and who their boss is. A language model does not get that context separately from the text. On top of that, the model is trained precisely to follow instructions it sees in text. The problem comes from the same property that makes the model useful, not from a small bug.

A blunt rule such as "never take instructions from a document" is not enough either. Ordinary work email is full of instructions: "Please send the signed form by Friday." An assistant summarising that email should mention the request, but it should not go and send a form itself. Each time, the model has to get a fine distinction right: talk about instructions without carrying them out.

## What does spotlighting do, and what can't it do?

Spotlighting wraps the document in two markers, replaces the spaces in its text with a symbol, and tells the model that anything in this shape is data, whoever claims otherwise. Think of handing the secretary the letter in a red envelope and saying that whatever is inside the red envelope is for reading only.

Hines and colleagues, who introduced the method in 2024, reported that in their own experiments on GPT-family models the attack success rate fell from over 50% to under 2%. That result belongs to those models and that attack set. It does not transfer to other models automatically.

The main limitation is simple: spotlighting is a request to the model, not a lock. If a model ignores the red envelope, the label does nothing. Our lab showed exactly that.

## If the model is fooled, what can it still reach?

The second defence is about access, not the model. Least privilege means each task gets only the tools it needs. If the task is summarising an invoice, the assistant has no email tool at all. If the task is sending an email, it has only that tool and asks you before each send: to whom, with what content. OWASP's mitigation list also includes least privilege, human approval for high-risk actions, and separating and labelling untrusted content.

The strength of this defence is that security no longer depends on the model never being fooled. It still has two gaps. First, some attacks need no tool at all; they only want to change what the assistant says, for example by asking it to tell you that a fictional vendor was already approved by finance. No email is sent, so there is nothing for the gate to stop. Second, human approval only works when it is rare and specific. An assistant that keeps asking "are you sure?" trains you to approve without reading.

## What did our fake-office experiment show?

We built a fully fictional, offline office: an assistant with two mock tools, one to read files and one to send email, that never touch a real file or send a real message. We wrote 20 fictional documents. Twelve contain attacks: 7 need a tool and 5 only try to change the answer. Eight are clean, and some of those deliberately contain ordinary instructions meant for people. Every address uses the reserved `.invalid` domain.

For each setting we counted three things: whether the main task was done, whether the injected instruction actually took effect, and whether the defence broke a clean task (over-refusal). The third number matters because the safest possible assistant is one that does nothing, the same point [episode HMD-006](/en/episodes/hmd-006/) made about "fewer errors".

The two "models" we ran have no intelligence and are **ILLUSTRATIVE**: a few hand-written rules that only demonstrate the mechanism. `naive` obeys every instruction-like line. `boundary` ignores instructions inside the spotlighting markers, by construction.

| Setting | `naive`: injections executed | `boundary`: injections executed | Over-refusal (both) |
|---|---|---|---|
| No defence | 12 of 12 | 12 of 12 | 0 of 8 |
| Spotlighting | 12 of 12 | 0 of 12 | 0 of 8 |
| Least privilege + approval | 5 of 12 | 5 of 12 | 0 of 8 |
| Both combined | 5 of 12 | 0 of 12 | 0 of 8 |

*ILLUSTRATIVE: output of our own rules, not the behaviour of any real model. Source: `results-illustrative-2026-11-02.md` in the episode's artifact folder.*

Three things stand out. Spotlighting did nothing for `naive`, because that model does not understand the red envelope. Least privilege stopped all 7 tool-based attacks, even for a model that obeys everything; for the first document, the only trace of the attack was two BLOCKED lines in the log and an empty mock outbox. And the 5 attacks that got through are exactly the ones that need no tool.

The log for the first document shows one more thing. With no defence, the answer you see (the invoice total and due date) is entirely correct while the mock email has already gone to the attacker's address. A successful attack can hide behind a correct answer.

## What does a real model do?

We do not know yet. The 20 documents have not been run against a real model, and no rate has been written in advance. That run will be published separately, with the model's name and version.

The outside evidence we have is Anthropic's report "Mitigating the risk of prompt injections in browser use", published on 24 November 2025. In the company's own browser tests, against an adaptive Best-of-N attacker with 100 attempts per environment, its chart shows these attack success rates for Opus 4.5: 8.0% for the model alone, 7.6% with the earlier safeguards and 1.4% with the improved safeguards. The report's text speaks of "a 1% attack success rate"; we quote the chart value. The authors also describe prompt injection as "far from a solved problem".

Those numbers cannot be compared with our demo, because the environment, the attacker and the definition of success all differ. What they do show is that even the best reported defences have not brought the rate to zero.

## What this does not show

- It does not show that any real assistant is safe or unsafe. Twenty fictional documents with plain sentences are far simpler than a real attacker.
- It does not show that spotlighting gives Hines et al.'s result on every model. Each result belongs to one model, one date and one configuration.
- The numbers in the table above are not about AI. We wrote the two stand-ins' behaviour ourselves to make the mechanism visible.
- Anthropic's figure is not a security certificate for any product. It is limited to that company's browser tests at that date.

What it does show: a document can give orders, and a tool lock can stop the action even when the model has been fooled, but it cannot stop a misleading sentence.

## What should you ask before giving an assistant access?

One question is enough: "Without asking me, what can it do?" If the answer is "everything", shrink the access. Separate reading from sending, and put anything irreversible behind a short, clear confirmation. Spotlighting and model training lower the chance of being fooled; limiting access limits the size of the damage.

The next episode, [HMD-008](/en/episodes/hmd-008/), turns to an error that comes from neither the model nor an attacker: an answer key that is itself wrong.
