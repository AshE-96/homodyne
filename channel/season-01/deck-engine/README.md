# Recording decks v6: one source, a Persian deck and an English twin

Each episode has one source and two generated decks:

```
parts/<episode>/deck.src.html   ← edit this
parts/<episode>/deck-fa.html    ← generated: Persian, right to left (used for recording)
parts/<episode>/deck-en.html    ← generated: English, left to right, same frames in the same order
```

Build with `make decks`, or `python3 scripts/build-decks.py --only hmd-005` for one episode. `make episodes` runs `build-decks.py --check` first, and that fails if a generated deck is stale.

The engine is `deck.css` and `deck.js` in this folder. The builder inlines them, the Vazirmatn font (`brand/fonts/`, SIL OFL) and the Homodyne mark into each deck. That makes every deck one self-contained file you can open straight from disk.

The two pilots show every component:

- `parts/02-benchmarking/e01-is-a-higher-score-better/deck.src.html` (HMD-002)
- `parts/03-standalone/hmd-005-persian-tokens/deck.src.html` (HMD-005)

## Keys

| Key | Action |
|---|---|
| → / Space | Next frame |
| ← | Previous frame |
| Home / End | First / last frame |
| F | Fullscreen |
| H | Hide the bottom bar (do this while recording) |
| N | Presenter notes |

`#5` or `?frame=5` in the URL opens frame 5 (`#0` is the cover).

## Source format

```html
<section class="cover">
<h1><t-fa>…manifest title, one word may be <em>amber</em>…</t-fa><t-en>…episodes-meta title…</t-en></h1>
<p class="promise"><t-fa>…</t-fa><t-en>…</t-en></p>
</section>

<section class="frame paper" id="beat-2" data-start="44">     <!-- or "frame night" -->
<p class="kicker"><t-fa>…</t-fa><t-en>…</t-en></p>          <!-- short beat label, optional -->
<h1><t-fa>…</t-fa><t-en>…</t-en></h1>
…one component…
<p class="tag">…</p>                                          <!-- source / label line, optional -->
<footer><t-fa>…</t-fa><t-en>…</t-en></footer>                  <!-- primary source, short -->
<aside class="notes"><t-fa><b>…</b><p>…</p></t-fa><t-en><b>…</b><p>…</p></t-en></aside>
</section>
```

### What the builder handles

- **Text pairs.** Every visible string is a pair, `<t-fa>…</t-fa><t-en>…</t-en>`. The fa deck keeps the first half and the en deck the second. Text outside a pair appears unchanged in both decks. Use that for terminal output, model names, formulas and token chips.
- **Cover frame.** The cover is generated around your `h1` and `promise`, with the logo, the series, the HMD number, a noise-to-signal wave and the site link.
  - Its title must equal the manifest title in Persian (`channel/season-01/manifest.json` or `channel/global/manifest.json`).
  - In English it must equal `site/src/data/episodes-meta.json`.
  - Tags are ignored in that comparison, so `<em>` is fine.
- **Frame chrome.** The header (logo, series and beat counter), the `<main>` wrapper and the cover are added for you.
  - `id="beat-N"` must run 1, 2, 3 … with no gaps.
  - `data-start` (seconds) must ascend and match the script's beat times.
- **Persian text.** In the fa deck:
  - every Latin run inside Persian text is wrapped in `<bdi dir="ltr">`;
  - « · » separators become a thin vertical rule, because a dot next to Persian digits reads like «۰»;
  - letter-spacing is forced to zero.
- **Episode CSS.** A `<style>` block in the source is appended to that episode's CSS. Use it only for charts or diagrams, and size them in px on the 1920×1080 stage.

## Components (CSS classes)

| Class | Use |
|---|---|
| `h1`, `h1.xl`, `h1.formula` | Headline. `<em>` marks the one amber word. `formula` = monospace, always LTR |
| `.kicker` | Short amber beat label above the headline |
| `.caption` | One muted sentence under the component |
| `.sub` | A line with a rule above it |
| `.tag` | Small source/meta line. `<b>` inside makes a badge: `<b><t-fa>ساختگی</t-fa><t-en>ILLUSTRATIVE</t-en></b>` or `<b><t-fa>اجرا نشده</t-fa><t-en>NOT RUN YET</t-en></b>` |
| `.cols > div` (`.hi` on one) | Columns: `span` label, `b` big number (`b.word` for a short phrase), `small` unit, `p` note |
| `.stat` | One huge number: `b` plus `span` |
| `.bars` / `.bars.tight` | Rows of `<div><span>label</span><i style="--v:62"></i><span>value</span></div>`. `--v` is the % width. Use `.tight` for more than 5 rows |
| `.cards > div` (`.hi`, `.off`) | Boxes: `b` title, then text. The column count follows the number of cards |
| `.steps > div` (`.hi`, `.off`) | A sequence or timeline: `b` title, then text |
| `.tokens > i` (`.hi`, `.off`, `.mono`) | Chips. `.mono` = monospace, LTR |
| `.source` | `q` short quote (under 15 words) plus `cite` |
| `.boundary` | Claim boundary: `<div><b>This shows</b>…</div><div class="no"><b>This does not show</b>…</div>` |
| `.code`, `.code.sm` | Terminal output, always LTR, never translated. `.c` = comment grey, `.o` = amber highlight |
| `table.t` (`tr.hi`) | A small table |
| `svg.chart` | An inline chart with a viewBox; style it in the episode `<style>` block |

Keep a frame to **one component**, plus an optional caption and tag. If the content does not fit, the engine shrinks it and warns in the console. Treat that as a signal to cut words, not as a feature.

## Writing rules

**Persian (fa) is the canonical text.**

- Use written Persian, not the colloquial narration. Keep it consistent with what the script says in that beat.
- Use Persian digits in Persian text: `۲۴٪`, `۱٫۲۱`, `۶۰ درست`. The decimal separator is `٫` and the percent sign is `٪`, written at full size and not inside `<small>`.
- Keep ASCII digits only inside formulas, code, version numbers, model and file names (`gpt-5`, `tiktoken 0.9.0`, `arXiv 2509.04664`) and `<bdi dir="ltr">` math such as `<bdi dir="ltr">k = 0.4</bdi>`.
- Use Persian quotation marks «…» and the Persian comma «،».
- Write signs as words where a sign would flip in RTL: «۶٫۷٪ بیشتر», «منفی ۳۰».
- Model, benchmark, tool and file names stay in Latin script.
- Paper and report titles stay in their original language.
- Inside Persian text, an arrow pointing forward is «←».

**English (en) is a faithful translation of the Persian.**

- Translate frame by frame and item by item, in the same order, with the same numbers. Do not add, drop or merge content. Someone will dub the episode into English using this deck.
- Use sentence case. Do not write labels in ALL CAPS.
- Put Persian that is data rather than prose (example sentences, single letters, tokens) inside `lang="fa"` (`<bdi lang="fa">ی</bdi>`), so the builder knows it is meant to be there.

**Facts.**

- Every number, date, name and quote must match the episode's `script-fa.md` beat and `sources.md`.
- Keep ILLUSTRATIVE and NOT RUN YET labels wherever the script has them.
- Never state a `[RUN]` or `[VERIFY]` value as a result.

**Notes.**

- The Persian notes are the presenter's cues; keep them.
- The English notes are a translation of them.
- Notes are not shown on screen while recording.
