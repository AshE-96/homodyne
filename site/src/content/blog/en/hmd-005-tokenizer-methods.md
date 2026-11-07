---
title: "Counting Persian tokens: method and reproduction"
description: "50 self-written pairs, nine tokenizers pinned to exact commits, a per-pair ratio and five spelling controls. How to rerun count_tokens.py, and limits."
lang: en
translationKey: hmd-005-deep-dive
hmd: HMD-005
kind: deep-dive
date: 2026-12-18
tags: ["tokenizer", "tokens", "Persian", "reproducibility", "tiktoken", "Hugging Face"]
sources:
  - title: "Petrov, La Malfa, Torr, Bibi · Language Model Tokenizers Introduce Unfairness Between Languages (NeurIPS 2023)"
    url: "https://arxiv.org/abs/2305.15425"
  - title: "OpenAI · tiktoken (v0.9.0)"
    url: "https://github.com/openai/tiktoken"
datasets:
  - title: "HMD-005 · pairs.jsonl, 50 self-written Persian/English pairs in 7 domains, and count_tokens.py"
    url: "https://github.com/AshE-96/homodyne/tree/main/parts/03-standalone/hmd-005-persian-tokens/artifact"
    license: "Self-written; see the Homodyne LICENSE.md (code MIT)"
  - title: "tiktoken 0.9.0 · o200k_base, cl100k_base, gpt2"
    url: "https://github.com/openai/tiktoken"
    license: "MIT"
  - title: "NousResearch/Llama-2-7b-hf (mirror of the official Llama 2 tokenizer) @8efe6c9b9365"
    url: "https://huggingface.co/NousResearch/Llama-2-7b-hf"
    license: "Llama 2 Community License"
  - title: "unsloth/Llama-3.2-1B-Instruct (mirror of the official Llama 3.2 tokenizer) @5a8abab4a5d6"
    url: "https://huggingface.co/unsloth/Llama-3.2-1B-Instruct"
    license: "Llama 3.2 Community License"
  - title: "unsloth/gemma-3-1b-it (mirror of the official Gemma 3 tokenizer) @5b11413a10db"
    url: "https://huggingface.co/unsloth/gemma-3-1b-it"
    license: "Gemma Terms of Use"
  - title: "Qwen/Qwen3-8B @b968826d9c46"
    url: "https://huggingface.co/Qwen/Qwen3-8B"
    license: "Apache 2.0"
  - title: "deepseek-ai/DeepSeek-V3 @e815299b0bcb"
    url: "https://huggingface.co/deepseek-ai/DeepSeek-V3"
    license: "MIT (code) and DeepSeek Model License (model)"
  - title: "mistralai/Mistral-Nemo-Instruct-2407 @04d8a90549d2"
    url: "https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407"
    license: "Apache 2.0"
---

The measurement behind this episode is simple and fully reproducible: we gave 50 meaning-matched Persian/English sentence pairs to nine tokenizers pinned to exact versions, computed the Persian-to-English token ratio for every pair, and reported its median and spread. Medians ran from 1.21 to 4.61. Every number in this post comes from `results-2026-11-02.md` and `.json`, and one command rebuilds them.

> **Key Takeaways**
> - Corpus: 50 self-written pairs in 7 domains, with standard Persian spelling. Persian used a median 0.88 of the English character count and 1.00 of the word count.
> - Tokenizers: three tiktoken 0.9.0 encodings and six open Hugging Face tokenizers, each pinned to a specific commit.
> - Statistics: per-pair ratio, median, IQR, 10th and 90th percentiles, min and max, whole-corpus ratio, and the share of pairs where Persian needed more tokens.
> - Five spelling controls change only the Persian side: the half-space, Arabic ي/ك, and two other digit forms.
> - Main limitation: a small, self-written corpus. The result says nothing about quality, speed or price.

## What is in the corpus, and how was it written?

`artifact/corpus/pairs.jsonl` holds one pair per line with four fields: `id`, `domain`, `fa` and `en`. The 50 pairs span seven domains:

| domain | pairs |
|---|---:|
| chat messages (chat) | 10 |
| news (news) | 8 |
| how-to instructions (howto) | 6 |
| customer support (support) | 6 |
| code comments (code) | 6 |
| numbers and dates (numbers) | 8 |
| addresses (address) | 6 |

We wrote every sentence ourselves; addresses and numbers are fictional. The Persian side uses Persian ی/ک, correct half-spaces (the zero-width non-joiner, ZWNJ, that Persian places inside words such as می‌خواهم) and Persian digits. On load, the script also converts any Arabic ي/ك to the Persian forms so every run starts from the same spelling. The corpus is part of the Homodyne repository; to add your own text, append a line with the same four fields.

## Which tokenizers, from where, at which version?

Environment: Python 3.11.7, tiktoken 0.9.0, transformers 4.49.0 and tokenizers 0.21.0 on macOS, on 2 November 2026. Vocabulary size is the number each library reports.

| label | source | commit | vocabulary |
|---|---|---|---:|
| o200k_base | tiktoken | (version 0.9.0) | 200,019 |
| cl100k_base | tiktoken | (version 0.9.0) | 100,277 |
| gpt2 (r50k) | tiktoken | (version 0.9.0) | 50,257 |
| Llama-2 | `NousResearch/Llama-2-7b-hf` | `8efe6c9b9365` | 32,000 |
| Llama-3.2 | `unsloth/Llama-3.2-1B-Instruct` | `5a8abab4a5d6` | 128,256 |
| Gemma-3 | `unsloth/gemma-3-1b-it` | `5b11413a10db` | 262,145 |
| Qwen3 | `Qwen/Qwen3-8B` | `b968826d9c46` | 151,669 |
| DeepSeek-V3 | `deepseek-ai/DeepSeek-V3` | `e815299b0bcb` | 128,815 |
| Mistral-Nemo | `mistralai/Mistral-Nemo-Instruct-2407` | `04d8a90549d2` | 131,072 |

The official Llama and Gemma repositories on Hugging Face are gated, so we used public mirrors. On 7 November 2026 we checked through the Hugging Face file API (size and SHA) that the mirrors carry the official tokenizers:

- **Gemma-3:** `tokenizer.json` and `tokenizer.model` in the unsloth mirror are byte-identical to Google's official repository.
- **Llama-3.2:** the unsloth file stores merges in a newer format, but re-serializing it reproduces the official file exactly (SHA-1 starting `5cc5f00a5b20`), so it is functionally identical.
- **Llama-2:** `tokenizer.model` in NousResearch is identical to the official file.

The only tokenizer-to-model mapping we use is the one inside tiktoken 0.9.0: o200k_base for gpt-4o, o1 and o3; cl100k_base for gpt-4 and gpt-3.5-turbo. We make no claim about which tokenizer a product runs today.

## How were the ratio, statistics and controls computed?

**Counting.** For tiktoken we count the output of `encode`; for Hugging Face tokenizers, `encode(text, add_special_tokens=False)`. Special tokens such as BOS and EOS are not counted, and no chat template or system prompt is involved.

**Ratio.** For each pair, Persian tokens divided by English tokens. Above 1 means Persian needed more pieces.

**Statistics.** Per tokenizer: the median, first and third quartiles (the IQR, or middle half of pairs), 10th and 90th percentiles, min and max, the whole-corpus ratio (total Persian tokens over total English tokens), and the share of pairs with a ratio above 1. Quantiles use linear interpolation. The median is the headline number because a few unusual pairs cannot drag it around.

**Spelling controls.** The Persian side of each sentence was also counted in five altered forms:

| control | change | sentences changed |
|---|---|---:|
| `zwnj_space` | half-space (U+200C) to a normal space | 34 |
| `zwnj_none` | half-space deleted (letters joined) | 34 |
| `arabic_yk` | Persian ی/ک to Arabic ي/ك | 49 |
| `latin_digits` | Persian digits to Latin 0-9 | 11 |
| `arabic_digits` | Persian digits to Arabic-Indic digits | 11 |

For each control we report the median percentage change in Persian token count, only over the sentences that control actually changes.

## What are the detailed results?

<figure>
<svg viewBox="0 0 640 320" width="100%" role="img" aria-labelledby="hmd005-en-chart-title" direction="ltr" style="direction:ltr" font-size="13" fill="currentColor">
<title id="hmd005-en-chart-title">Median Persian-to-English token ratio for nine tokenizers on 50 sentence pairs, measured 2 November 2026</title>
<g stroke="currentColor" stroke-opacity="0.2"><line x1="290" y1="24" x2="290" y2="292"/><line x1="370" y1="24" x2="370" y2="292"/><line x1="450" y1="24" x2="450" y2="292"/><line x1="530" y1="24" x2="530" y2="292"/></g>
<line x1="210" y1="22" x2="210" y2="292" stroke="currentColor" stroke-opacity="0.6" stroke-dasharray="3 3"/>
<text x="210" y="15" font-size="11" text-anchor="middle">parity (1×)</text>
<g fill="#E8A33D"><rect x="130" y="30" width="96.8" height="18"/><rect x="130" y="60" width="103.2" height="18"/><rect x="130" y="90" width="111.2" height="18"/><rect x="130" y="120" width="111.2" height="18"/><rect x="130" y="150" width="130.4" height="18"/><rect x="130" y="180" width="184" height="18"/><rect x="130" y="210" width="233.6" height="18"/><rect x="130" y="240" width="273.6" height="18"/><rect x="130" y="270" width="368.8" height="18"/></g>
<g stroke="currentColor" stroke-width="2"><line x1="214" y1="39" x2="240.4" y2="39"/><line x1="222" y1="69" x2="246" y2="69"/><line x1="225.2" y1="99" x2="246.8" y2="99"/><line x1="228.4" y1="129" x2="250" y2="129"/><line x1="244.4" y1="159" x2="278" y2="159"/><line x1="282" y1="189" x2="337.2" y2="189"/><line x1="337.2" y1="219" x2="395.6" y2="219"/><line x1="362" y1="249" x2="439.6" y2="249"/><line x1="450" y1="279" x2="555.6" y2="279"/></g>
<g text-anchor="end"><text x="122" y="43">Gemma-3</text><text x="122" y="73">Mistral-Nemo</text><text x="122" y="103">Llama-3.2</text><text x="122" y="133">o200k_base</text><text x="122" y="163">DeepSeek-V3</text><text x="122" y="193">Qwen3</text><text x="122" y="223">cl100k_base</text><text x="122" y="253">Llama-2</text><text x="122" y="283">gpt2 (r50k)</text></g>
<g text-anchor="end" font-weight="bold"><text x="632" y="43">1.21</text><text x="632" y="73">1.29</text><text x="632" y="103">1.39</text><text x="632" y="133">1.39</text><text x="632" y="163">1.63</text><text x="632" y="193">2.30</text><text x="632" y="223">2.92</text><text x="632" y="253">3.42</text><text x="632" y="283">4.61</text></g>
<g font-size="11" text-anchor="middle" fill-opacity="0.7"><text x="130" y="310">0</text><text x="210" y="310">1×</text><text x="290" y="310">2×</text><text x="370" y="310">3×</text><text x="450" y="310">4×</text><text x="530" y="310">5×</text></g>
</svg>
<figcaption>Bar: median Persian/English token ratio over 50 pairs. Dark line: middle half of pairs (IQR). Data: <code>results-2026-11-02.json</code>, run on 2 November 2026.</figcaption>
</figure>

Alongside the median, the table shows the whole-corpus ratio, the share of pairs where Persian cost more, and characters per token on each side:

| tokenizer | median | corpus ratio | Persian more | chars/token (fa) | chars/token (en) |
|---|---:|---:|---:|---:|---:|
| Gemma-3 | 1.21 | 1.19 | 76% | 2.99 | 4.02 |
| Mistral-Nemo | 1.29 | 1.29 | 96% | 2.80 | 4.06 |
| Llama-3.2 | 1.39 | 1.35 | 98% | 2.82 | 4.30 |
| o200k_base | 1.39 | 1.38 | 100% | 2.82 | 4.40 |
| DeepSeek-V3 | 1.63 | 1.64 | 100% | 2.31 | 4.28 |
| Qwen3 | 2.30 | 2.19 | 100% | 1.66 | 4.09 |
| cl100k_base | 2.92 | 2.81 | 100% | 1.36 | 4.30 |
| Llama-2 | 3.42 | 3.28 | 100% | 1.01 | 3.74 |
| gpt2 (r50k) | 4.61 | 4.33 | 100% | 0.88 | 4.28 |

The last two columns carry the story. English sits between 3.74 and 4.40 characters per token on every tokenizer, while Persian ranges from 2.99 down to 0.88. Below 1, as on gpt2, means a Persian letter costs more than one token on average: letters are being split into bytes.

**Vocabulary size is a poor predictor.** Qwen3, with 151,669 entries, has a ratio of 2.30, while Llama-3.2, with 128,256, has 1.39. cl100k_base, with 100,277 entries, beats Llama-2 with 32,000 but does far worse than Mistral-Nemo with 131,072. A plausible explanation is that what matters is which languages the entries were spent on; but this measurement cannot see the Persian share of any tokenizer's training text, and does not prove it.

**One sentence, nine splits.** The demo sentence "I want to cancel my subscription and get a refund for the last month." in Persian became 21 tokens on Llama-3.2, 22 on o200k_base and Gemma-3, 23 on Mistral-Nemo, 27 on DeepSeek-V3, 36 on Qwen3, 46 on cl100k_base, 59 on Llama-2 and 69 on gpt2. The English version was 15 tokens everywhere except Llama-2, which gave 16 because it split "refund" in two. The shapes are telling: Llama-3.2 kept بگیر ("take back") as one piece, Gemma-3 put a letter, the half-space and the next letter into a single piece, Llama-2 split almost every letter apart, and gpt2 split letters into bytes.

**Domains.** How-to instructions had the highest median on all nine tokenizers (from 1.50 on Gemma-3 to 5.76 on gpt2). The lowest median belonged to code comments on six tokenizers, to addresses on Mistral-Nemo and Llama-3.2, and to numbers and dates on Gemma-3 (0.98). On Gemma-3, Persian needed fewer tokens in 7 pairs (code-01, num-01, num-02, num-03, num-06, addr-03 and addr-04) and tied in 5.

**Controls.** Median percentage change in Persian tokens:

| tokenizer | half-space→space | half-space removed | Arabic ي/ك | Latin digits | Arabic-Indic digits |
|---|---:|---:|---:|---:|---:|
| Gemma-3 | 0.0% | 0.0% | +11.5% | +14.3% | +6.7% |
| Mistral-Nemo | 0.0% | 0.0% | +10.5% | 0.0% | 0.0% |
| Llama-3.2 | 0.0% | 0.0% | +11.5% | 0.0% | +13.8% |
| o200k_base | 0.0% | 0.0% | +6.7% | −8.3% | +4.0% |
| DeepSeek-V3 | −13.5% | −11.4% | +6.2% | −7.1% | +11.8% |
| Qwen3 | −2.4% | −4.5% | −4.7% | −17.9% | 0.0% |
| cl100k_base | −2.2% | −3.1% | 0.0% | −21.2% | 0.0% |
| Llama-2 | 0.0% | −2.4% | 0.0% | −12.2% | 0.0% |
| gpt2 (r50k) | −2.5% | −4.4% | −6.2% | −16.7% | −3.2% |

DeepSeek-V3's half-space effect is visible in how it splits the character: in the demo sentence, the half-space became two byte tokens, `e280` and `8c`, because ZWNJ is three bytes in UTF-8. The headline result is not very sensitive to digits: with all digits typed as Latin, the o200k_base median moves from 1.39 to 1.36, and on rows without digits it is 1.40.

## How do you reproduce it?

All commands run from the repository root. The script needs Python 3.10 or later; tiktoken is required, and transformers is needed only for the six open tokenizers.

```bash
python3 -m pip install tiktoken==0.9.0 transformers==4.49.0 tokenizers==0.21.0
python3 parts/03-standalone/hmd-005-persian-tokens/artifact/count_tokens.py
```

The first run downloads the tokenizer files from Hugging Face. To re-run from the local cache only, or for a few tokenizers:

```bash
python3 parts/03-standalone/hmd-005-persian-tokens/artifact/count_tokens.py --offline
python3 parts/03-standalone/hmd-005-persian-tokens/artifact/count_tokens.py --only o200k_base cl100k_base
```

Output is written next to the script with the run date (`results-YYYY-MM-DD.md` and `.json`); `--out-dir` sends it elsewhere and `--corpus` points at another corpus. If a tokenizer fails to load, the script skips it and lists it under `skipped`; the run does not stop. Because the commits are pinned, the same library versions should give the same table. If you install other versions and a number changes, trust your new file, not this post.

To test your own text, append a line to `pairs.jsonl`:

```json
{"id": "my-01", "domain": "chat", "fa": "متن فارسی شما", "en": "Your English text"}
```

## What are the limitations?

- **Small, self-written corpus:** 50 pairs from one author. Translation choices move the ratio, and books, real conversations or legal text could give different numbers.
- **Digit controls on a small sample:** only 11 sentences contain digits, so read the digit percentages with care.
- **Tokenizer, not service:** special tokens, chat templates and system prompts are not counted, and a real service may add text of its own.
- **Model attribution:** only from tiktoken 0.9.0's map; products can change tokenizers.
- **Mirrors:** three tokenizers come from public mirrors. Their match with the official files was checked, but only for these commits.
- **No quality, speed or price:** none was measured. The cost formula is only: input cost equals input tokens times the per-token input price, with output priced separately.

## What this does not show

- That any model understands Persian worse. More tokens means a bigger share of budget and context.
- That the Persian ratio is the same for all text.
- Which tokenizer the service you use today runs, or what it costs.
- The word "unfairness" comes from the title of Petrov and colleagues' paper; it is not a verdict of this measurement.

## Further reading

- [Petrov et al., NeurIPS 2023](https://arxiv.org/abs/2305.15425), comparing token lengths across many languages.
- [The tiktoken repository](https://github.com/openai/tiktoken), for the encodings and the model-to-encoding map.
- The plain-language companion: [Why does Persian cost more tokens for AI models?](/en/blog/hmd-005-persian-token-tax/)
- The video and deck: [HMD-005 episode page](/en/episodes/hmd-005/); previous episode: [HMD-004](/en/episodes/hmd-004/)
- Persian original: [شمارش توکن فارسی: روش، نسخه‌ها و بازتولید](/fa/blog/hmd-005-tokenizer-methods/)
