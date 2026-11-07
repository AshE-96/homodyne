# Homodyne · هومودین

**One familiar question about AI and science, answered with an experiment you can see.**
A Persian-language YouTube channel with English subtitles, a bilingual blog at **[homodyne.m2gh.ir](https://homodyne.m2gh.ir)**, and every episode's script, sources and runnable artifact in this repository.

[فارسی](README.fa.md)

## Four promises in every episode

1. **A question in the title** and a plain answer at the end.
2. **A primary source** on screen, with name and date.
3. **An artifact** you can run or read yourself (`artifact/`).
4. **A claim boundary**: what the result does *not* show.

Numbers come from a named source or from a run in this repo. Simulated data is labelled ILLUSTRATIVE. An experiment that has not run yet is called exactly that.

## Season 01

| HMD | Question | Folder |
|---|---|---|
| 002 | How can the same answers crown a different AI winner? | [`parts/02-benchmarking/e01-…`](parts/02-benchmarking/e01-is-a-higher-score-better/) |
| 003 | Can satellites spot a forest fire while it is still small? | [`parts/03-standalone/hmd-003-…`](parts/03-standalone/hmd-003-wildfire-from-space/) |
| 004 | Is the top model on the leaderboard the best one for you? | [`parts/02-benchmarking/e02-…`](parts/02-benchmarking/e02-which-benchmark-answers-your-question/) |
| 005 | Why does Persian cost more tokens for some AI models? | [`parts/03-standalone/hmd-005-…`](parts/03-standalone/hmd-005-persian-tokens/) |
| 006 | When they say an AI makes fewer mistakes, what are they not telling you? | [`parts/02-benchmarking/e03-…`](parts/02-benchmarking/e03-what-exactly-are-we-measuring/) |
| 007 | Can a single document hijack your AI assistant? | [`parts/03-standalone/hmd-007-…`](parts/03-standalone/hmd-007-prompt-injection/) |
| 008 | If the answer key is wrong, which AI loses? | [`parts/02-benchmarking/e04-…`](parts/02-benchmarking/e04-who-decides-the-right-answer/) |
| 009 | How does Google Maps know when you will arrive? | [`parts/03-standalone/hmd-009-…`](parts/03-standalone/hmd-009-maps-eta/) |
| 010 | Can negative marking make an AI more careful? | [`parts/02-benchmarking/e05-…`](parts/02-benchmarking/e05-how-do-you-penalise-a-bluff/) |
| G01 | What happens when AI learns from AI-written text? | [`parts/04-global/hmd-g01-…`](parts/04-global/hmd-g01-model-collapse/) |
| 012 | We tested it a thousand times. Can we trust it now? (course E06) | [`parts/02-benchmarking/e06-…`](parts/02-benchmarking/e06-how-many-questions-and-a-fair-run/) |
| 014 | Every number in this table is right. Why does it mislead? (E07) | [`parts/02-benchmarking/e07-…`](parts/02-benchmarking/e07-where-does-this-benchmark-mislead-you/) |
| 016 | Which AI says "I don't know" at the right time? (E08, results after data lock) | [`parts/02-benchmarking/e08-…`](parts/02-benchmarking/e08-which-model-knows-when-to-abstain/) |
| 018 | Where did this AI score come from? Check it yourself (E09) | [`parts/02-benchmarking/e09-…`](parts/02-benchmarking/e09-how-do-you-publish-a-refutable-result/) |
| B07 | Can AI find where you are from one photo? | [`parts/04-global/hmd-b07-…`](parts/04-global/hmd-b07-photo-geolocation/) |

Full map with status: [`channel/README.md`](channel/README.md). HMD-001 (what an AI PM does) lives in [`parts/01-ai-pm/`](parts/01-ai-pm/).

## Layout

```
parts/        one folder per episode: README, script-fa.md, hooks-fa.md, package-fa.md,
              deck.src.html → deck-fa.html + deck-en.html (recording decks), sources.md,
              artifact/ (runnable code and results)
channel/      season map, episode bible, hook bank, calendar, idea banks, manifests
site/         homodyne.m2gh.ir: Astro, Persian (RTL) + English, blog in site/src/content/blog/
tools/        bluff_lab.py: scoring tool shared by the benchmark-course episodes
scripts/      checkers and the teleprompter export
brand/        logo, mark, favicon
```

## Run it

```bash
make decks         # build deck-fa.html + deck-en.html from each deck.src.html
make episodes      # check every package: beats, word counts, decks, links
make teleprompter  # write parts/…/recording/ (teleprompter HTML/TXT + recording sheet)
make selftest      # artifact self-tests
make site          # build the website into site/dist
make preview       # serve it locally as it will go live
make deploy        # check, build and upload to Cloudflare (run on each release day)
```

Every artifact uses the Python standard library unless its README says otherwise. The benchmark-course episodes refer to the M2Lab benchmarking framework (`framework/`, `examples/bluff-v1`, `m2bench`), which lives in its own repository.

## Corrections

Found a wrong number or a broken claim? Open a [correction issue](../../issues/new?template=correction.yml) with the source. Corrections are made in the open and noted in the episode's `sources.md`.

## License

Content (scripts, decks, posts, brand) is CC BY-NC-SA 4.0; code is MIT. See [`LICENSE.md`](LICENSE.md).
