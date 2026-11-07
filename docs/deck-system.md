# The deck system

Nine episodes, one visual system, nine standalone files.

## The constraint that shapes everything

On recording day a deck is opened straight from disk, dragged between machines, and thrown into
fullscreen. A broken relative path at that moment costs a shoot. So each episode deck is a
**single self-contained HTML file** — CSS and JS inlined, nothing fetched at runtime except web
fonts.

That conflicts with wanting one shared design language across nine episodes. The resolution is
a sync script rather than a build system:

```bash
vim parts/02-benchmarking/_archive/v1-m2lab/_shared/m2lab-deck.css     # edit the single source of truth
./scripts/sync-design-language.sh        # inline it into all nine decks
```

The script replaces everything between marker pairs and leaves everything outside them alone —
which is where each episode's own choreography and content live:

```
/* @shared:css:start */ … /* @shared:css:end */
/* @shared:js:start  */ … /* @shared:js:end  */
```

CI fails if the decks have drifted from the shared source. A deck that silently drifts is
discovered mid-take.

## The build system

Slides reveal in **beats**, driven by the presenter. Nothing is on a timer, because narration
never matches a timer twice. Three declarative attributes express the entire choreography:

```html
<tr  data-build="3">   <!-- hidden → revealed at 3 → amber at 3 → muted after 3 -->
<span data-track="3">  <!-- always visible; .is-now at 3, .is-done after -->
<div data-since="3">   <!-- always visible; .is-since from 3 onward -->
```

Elements arrive with the spoken line; the one being explained turns amber; everything already
said drops to muted. Each slide also carries `data-at="<step>"`, so bespoke per-slide
choreography can be written as plain CSS instead of more JavaScript.

Every slide gets one extra beat past its last build: all lit, none dimmed. That is the
summing-up moment, and it exists because presenters always want it.

## Fixed canvas

The deck is always 1920×1080 and is **scaled**, never reflowed:

```js
deck.style.setProperty('--k', Math.min(innerWidth / 1920, innerHeight / 1080));
```

What was designed and what the screen recorder captures are therefore the same pixels. A
reflowing deck looks different on every machine, which makes the design unverifiable.

## Content as data

Long tables and card grids are declared as data, not hand-written markup — so a row cannot
exist without a build step, and a build step cannot point at a row that is not there:

```js
M2Deck.init({
  episode : 'Ep.05',
  runtime : 1100,
  tables  : { 'tbl-metrics': { head: […], rows: [[…]], term: 0, strike: 3, chips: 'strip' } },
  entities: { 'grid-families': [ { name, tone, rows: [[k, v]], limit } ] },
  lists   : { 'ul-checks': { items: […], countId: 'badge' } },
});
```

## Record-day keys

| Key | Does |
|---|---|
| `→` / `Space` | Next beat, then next slide |
| `←` | Previous beat / slide — lands on the *finished* previous slide, never an empty one |
| `↑ ↓` | Jump a whole slide, skipping its build |
| `Home` / `End` | First / last slide |
| `R` | Reset this slide's build |
| `H` | Hide the reference bar — **do this before recording** |
| `F` | Fullscreen |
| `B` | Blank to graphite, for holding between takes |
| `S` | Source strip on/off |
| `T` | Start/reset the drift clock — turns amber when the take is 25s behind the script |
| `P` | Print the downloadable card as A4 |
| `?` | Key list |

The chrome is an overlay: hiding it with `H` must not move a single pixel of the frame.

The cursor auto-hides after two seconds of stillness, because a visible cursor ruins a clean
take.

## Why there are tests

A build hook pointing at an element that isn't there throws no error. It renders a slide that
never advances — discovered with the camera running. So the failures that would otherwise
surface mid-take are caught in CI.

### `scripts/check-decks.py` — structural, stdlib only

- The shared blocks are present and actually inlined (not empty markers).
- IDs are unique; the engine looks elements up by ID.
- Required elements `#deck` and `#viewport` exist.
- Every slide has a `data-comp` label; themes and focus values are known.
- **Interior gaps in build-step numbers** — a missing step 3 means pressing `→` consumes a beat
  and changes nothing on screen. A gap *at* step 1 is allowed and often deliberate: a slide
  that opens on a held composition and only then starts moving.
- Every ID the config points at exists in the markup.
- No slide starts after the declared runtime.
- The inlined JavaScript parses (`node --check`).

### `scripts/drive-decks.js` — runtime, needs jsdom

Loads each deck in a DOM and presses the keys, exactly as on the day:

- Chrome injects; dot count matches slide count.
- Every declared table, entity grid and list actually rendered rows.
- A right-arrow-only walk reaches the last slide rather than dead-ending halfway.
- Stepping back lands on a completed slide, not an empty one.
- The other record-day keys do not throw.

```
ok    parts/02-benchmarking/_archive/v1-m2lab/1/M2Lab_Episode_01_Design_Mockup.html   Ep.01  17 slides  87 presses
ok    parts/02-benchmarking/_archive/v1-m2lab/2/M2Lab_Episode_02_Design_Mockup.html   Ep.02  19 slides  93 presses
…
9 deck(s) driven, 0 failed
```

## Authoring a new deck

1. Copy an existing deck; keep the `@shared` marker pairs intact.
2. Write slides as `<section class="slide" data-comp="…" data-time="…" data-start="…">`.
3. Add build attributes in the order you will speak them.
4. Put per-slide choreography in the deck's own `<style>`, keyed off `[data-at]`.
5. Declare tables, entity grids and lists in `M2Deck.init()`.
6. `./scripts/sync-design-language.sh && make decks`

Component vocabulary and colour rules: [design-language.md](design-language.md).
