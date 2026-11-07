---
title: "Why does Persian cost more tokens for AI models?"
description: "On 50 matched sentence pairs, Persian took 1.21 to 4.61 times as many tokens as English, depending on the tokenizer, despite using fewer letters."
lang: en
translationKey: hmd-005-companion
hmd: HMD-005
kind: companion
date: 2026-12-18
tags: ["tokens", "tokenizer", "Persian", "language models", "ZWNJ", "BPE"]
sources:
  - title: "Petrov, La Malfa, Torr, Bibi · Language Model Tokenizers Introduce Unfairness Between Languages (NeurIPS 2023)"
    url: "https://arxiv.org/abs/2305.15425"
  - title: "OpenAI · tiktoken (v0.9.0)"
    url: "https://github.com/openai/tiktoken"
---

Most tokenizers have fewer Persian pieces in their vocabulary, so they cut Persian text into smaller, more numerous chunks. On 50 matched sentence pairs we wrote ourselves, Persian used a median 0.88 of the English character count, yet took between 1.21 and 4.61 times as many tokens, depending on the tokenizer. That means a larger share of the budget and the context window, not necessarily worse understanding.

> **Key Takeaways**
> - A token is the chunk of text a model works with. Context limits and most usage billing are counted in tokens, not letters.
> - Across nine tokenizers, the median Persian-to-English token ratio ran from 1.21 (Gemma-3) to 4.61 (gpt2). Measured on 2 November 2026.
> - Two tokenizers from the same library differed sharply: cl100k_base at 2.92 and o200k_base at 1.39.
> - Typing Arabic ي/ك instead of Persian ی/ک added a median 6.7% to 11.5% more tokens on o200k_base, Mistral-Nemo, Llama-3.2 and Gemma-3. The effect of the half-space and of digits depended on the tokenizer.
> - The experiment says nothing about how well models understand Persian, about response speed, or about any service's prices.

## What is a token, and why count it?

A language model does not read text letter by letter. First a program called a tokenizer cuts the text into pieces, and each piece is a token. Every model family has its own tokenizer, and both the context window (how much text a model reads in one go) and most usage billing are counted in these tokens.

Take one sentence: "I want to cancel my subscription and get a refund for the last month." With the o200k_base tokenizer that is 15 tokens, roughly one per word. The same sentence in Persian:

| tokenizer | Persian tokens | English tokens |
|---|---:|---:|
| o200k_base | 22 | 15 |
| cl100k_base | 46 | 15 |
| gpt2 (r50k) | 69 | 15 |

The tiktoken library, version 0.9.0, maps o200k_base to GPT-4o and cl100k_base to GPT-4. That is only the library's own mapping, not a claim about the product you use today.

In cl100k_base, the Persian word for "last" (آخر) did not even get one piece: the preceding space plus the first byte of its first letter became one token, and the second byte became another. This tokenizer simply had no whole piece for some Persian letters.

## Why does a tokenizer cut Persian finer?

A tokenizer's vocabulary is learned from text. In common methods such as byte-pair encoding (BPE), it starts from very small units (characters or bytes) and repeatedly merges the pairs that appear together most often in its training text, until the vocabulary reaches a fixed size. A language with a smaller share of that text gets fewer merges, so its pieces stay small.

Three more things work against Persian:

- **Bytes:** in UTF-8, each Persian letter takes two bytes and the zero-width non-joiner (ZWNJ, the "half-space" Persian uses inside words) takes three. A tokenizer with no merges for those bytes can split one letter into two tokens, which is what happens in gpt2's 69 pieces.
- **Look-alike letters:** Persian ی and ک look almost identical to Arabic ي and ك, but to a computer they are different characters and can get different pieces. Text from Arabic keyboards or older systems often contains the Arabic forms.
- **Vocabulary size is not everything:** Qwen3, with 151,669 entries, had a ratio of 2.30; Llama-3.2, with 128,256, had 1.39. What matters is which languages the vocabulary was spent on.

The idea is not new. [Petrov and colleagues (NeurIPS 2023)](https://arxiv.org/abs/2305.15425) showed that the token length of the same translated text can differ by up to 15 times across languages, and their title speaks of "unfairness between languages". But that paper does not give today's Persian ratio on today's tokenizers. That we had to count.

## What did we measure on nine tokenizers?

We wrote 50 meaning-matched pairs across seven domains: chat messages, news, how-to instructions, customer support, code comments, numbers and dates, and addresses. The Persian side uses Persian ی/ک, correct half-spaces and Persian digits. For each pair we divided Persian tokens by English tokens and report the median ratio per tokenizer. The run was on 2 November 2026 with tiktoken 0.9.0 and transformers 4.49.0.

| tokenizer | median Persian/English ratio | middle half of pairs (IQR) |
|---|---:|---|
| Gemma-3 | 1.21 | 1.05 to 1.38 |
| Mistral-Nemo | 1.29 | 1.15 to 1.45 |
| Llama-3.2 | 1.39 | 1.19 to 1.46 |
| o200k_base | 1.39 | 1.23 to 1.50 |
| DeepSeek-V3 | 1.63 | 1.43 to 1.85 |
| Qwen3 | 2.30 | 1.90 to 2.59 |
| cl100k_base | 2.92 | 2.59 to 3.32 |
| Llama-2 | 3.42 | 2.90 to 3.87 |
| gpt2 (r50k) | 4.61 | 4.00 to 5.32 |

Three things stand out:

- **One library, two generations:** cl100k_base and o200k_base both ship in tiktoken. The Persian ratio fell from 2.92 to 1.39, less than half.
- **One number is not enough:** on o200k_base the cheapest pair was 1.05 and the most expensive 2.10, and Persian needed more tokens in all 50 pairs. Code comments had the lowest domain median (1.20), since part of the text is the code itself; how-to instructions had the highest (1.72).
- **There are exceptions:** on Gemma-3, Persian needed fewer tokens in 7 pairs and tied in 5, mostly number and address sentences. Persian was more expensive in only 76% of pairs.

More detail, a chart and the reproduction commands are in the [technical deep dive](/en/blog/hmd-005-tokenizer-methods/).

## How much do typing habits matter?

Part of the count is down to the keyboard. We re-counted the same 50 Persian sentences with three changes, and took the median change in token count only over the sentences each change actually touched.

**Arabic ي/ك instead of Persian ی/ک (49 sentences):** the median rose 6.7% on o200k_base, 11.5% on Llama-3.2 and Gemma-3, and 10.5% on Mistral-Nemo. On cl100k_base and Llama-2 the median change was zero, and on gpt2 and Qwen3 it went the other way. So on the four lowest-ratio tokenizers in the table, correct Persian letters are also cheaper.

**A normal space instead of the half-space (34 sentences):** on most tokenizers the median change was about zero. The exception was DeepSeek-V3, which splits the half-space itself into two byte tokens; there, replacing it with a normal space cut tokens by about 13.5%.

**Latin digits instead of Persian digits (11 sentences):** on o200k_base Latin digits were 8.3% cheaper, and on cl100k_base 21.2% cheaper. On Gemma-3 it was the reverse: 14.3% more expensive.

So there is no universal "write it this way to save tokens" rule. We are not suggesting anyone write incorrect Persian either: correct half-spaces matter for readability and search.

## What does this mean for cost and context?

Most services charge for input and output tokens separately. The formula is simple: cost equals tokens times the price per token. Send the same content in Persian under the same price list and the input cost scales by roughly the same ratio: at 1.39, about 39% more. We quote no prices here; they change, and should be read on each provider's official page on the day.

The second effect is the context window. At a ratio of 1.39, the same window holds about 72% as much content as in English (1 divided by 1.39). A long Persian contract hits the limit sooner. We did not measure response speed and make no claim about it.

## What this does not show

- **Quality:** more tokens means a bigger share of budget and context, not that a model understands Persian worse. Answer quality needs its own test.
- **All Persian text:** 50 self-written sentences are not a representative sample of Persian, and our own translations affect the ratios.
- **Today's products:** we do not claim which tokenizer the service you use runs today.
- **Price and speed:** no price or speed was measured or claimed.

## Where to go next

- The video and deck: [HMD-005 episode page](/en/episodes/hmd-005/)
- Corpus, exact versions, a chart and reproduction steps: [HMD-005 deep dive](/en/blog/hmd-005-tokenizer-methods/)
- Next episode, on the number behind "fewer errors": [HMD-006](/en/episodes/hmd-006/)
- Persian original: [چرا فارسی برای AI توکن بیشتری می‌برد؟](/fa/blog/hmd-005-persian-token-tax/)
