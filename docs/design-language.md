# Homodyne Benchmark Design Language

**v1.1** — implemented by [`parts/02-benchmarking/_archive/v1-m2lab/_shared/m2lab-deck.css`](../parts/02-benchmarking/_archive/v1-m2lab/_shared/m2lab-deck.css)
and [`m2lab-deck.js`](../parts/02-benchmarking/_archive/v1-m2lab/_shared/m2lab-deck.js). Section numbers here are the ones
the CSS cites in its comments.

---

## The mother rule

> **Nothing exists to be pretty.** Every moving part earns its place by making one argument
> visible that words alone would leave abstract.

A slide is not a summary of what is being said. It is the piece of the argument that only works
if you can see it — a rank that flips, an interval that overlaps, a score that stays the same
while the weights move. If a slide would be equally convincing as a sentence, it should be a
sentence.

Where a slide has a bespoke device, the CSS comment says **which claim it carries**. A device
with no claim gets deleted.

---

## §1 Foundations

### §1.1 Colour — definitive

| Role | Value | Use |
|---|---|---|
| Primary ink | `#14171A` | Text, rules, the graphite background |
| Base background | `#F5F3EE` | Every standard slide |
| Signal accent | `#E8A33D` | **The thing being explained right now.** Nothing else. |
| Amber as text | `#8F6410` | Amber legible on off-white; labels and eyebrows |
| Surface | `#EAE6DC` | Table headers, inline code, quiet panels |
| Muted | `ink @ 60%` | Everything already said |
| Faint | `ink @ 32%` | Not yet reached |
| Line | `ink @ 16%` | Rules and borders |

**Amber is a pointer, not decoration.** At any moment at most one element on screen is amber.
The instant two things are amber, the viewer has to decide which one you mean, and the device
has stopped working.

**No red, ever** — including for warnings and failures. Warning cards use amber attention
(§2.6). Red reads as *error* rather than *caution*, and much of this material is about results
that are wrong without anything having failed.

**Graphite mode** (`data-theme="graphite"`) inverts to ink-on-background and is reserved for
three moments: the Hook, a Core-idea statement, and the End Card. It is a punctuation mark. Used
on a fourth slide it stops being one.

### §1.2 Type

| Role | Family | Size |
|---|---|---|
| Display | Inter Tight 600–800 | 108px |
| Figure | Inter Tight 800 | 132px |
| Body | Inter 400–600 | 28px |
| Table header | Inter 600 | 20px, tracking `.08em`, uppercase |
| Table cell | Inter 400–500 | 24px |
| Caption | Inter 400 | 18px |
| Label / eyebrow | JetBrains Mono 500 | 15px, tracking `.14em`, uppercase |

Display tracking is `-0.024em`. Numerals are **tabular everywhere** — a column of figures that
shifts as it builds is unreadable, and this deck is mostly columns of figures.

Monospace marks machine things: metric ids, field names, statuses, code. If a viewer could type
it into a file, it is monospace.

### §1.3 Grid

1920×1080 fixed canvas, scaled not reflowed. Safe area 80px; top padding 138px; bottom 124px;
gutter 24px; measure 1180px.

The generous top padding is deliberate: it leaves room for the presenter's head in a
picture-in-picture corner without covering content.

### §1.4 Motion

Fade plus a short rise. `cubic-bezier(.22,.61,.36,1)`, 260ms.

**Never bounce, never spin, never slide across the frame.** A longer 520ms move is permitted
only for devices that carry an argument — a bar reordering to show a rank flip, a point moving
across a scatter. Motion that decorates competes with the narration for attention and always
wins, which is the wrong outcome.

---

## §2 Components

Each component exists for one job. The list is closed on purpose: a new component needs a new
argument, not a new look.

### §2.1 Statement Card

One sentence, held. The claim the episode turns on.

**Never shrink the type to fit a long sentence.** If it does not fit at display size, it is two
statements, and it gets split into a lead line and a follow line. A statement card that has been
shrunk to fit reads as a paragraph and stops landing.

### §2.2 Formula Card

A structural claim rendered as an equation:

```
BEST = USER + TASK + CONSTRAINTS + FAILURE COST + EVIDENCE
```

Terms arrive one per spoken beat. The term being explained is amber; the rest go muted. This is
the workhorse device of the whole chapter — it turns "it depends on several things" into
something with parts you can point at.

### §2.3 Tables

One row per spoken beat, never all at once. `term` marks the entity column; `strike` marks a
column that reads as crossed out.

Tables longer than about eight rows carry a **chip strip** overview above them, so the audience
can see where they are in a long list rather than losing the thread at row six.

### §2.4 Entity Cards

For comparing three to five things along the same dimensions.

The entity's tone dot is **never amber** — it is a neutral identifier, and letting it be amber
would put it in competition with the signal colour.

Every entity card ends with a **"Doesn't prove"** band, and it is the loudest row on the card.
That placement is the argument: for each benchmark family, what it cannot tell you is at least
as important as what it can, and putting it last means it is the last thing read.

### §2.5 Build focus

The three-state rule that governs every component:

| State | Appearance | Meaning |
|---|---|---|
| Not reached | Hidden, or faint | Not said yet |
| Now | Amber | Being explained |
| Said | Muted | Context, not focus |

### §2.6 Warning Card

Amber attention, never red. Used in pairs where the episode has two cautions — a single warning
card reads as an aside; two read as a section.

### §2.7 Proof / Source Strip

A slide making an empirical claim carries its source on the slide, in the frame, at caption
size. Toggleable with `S` for a cleaner cut, but present by default.

A chapter about evidence that shows uncited numbers is arguing against itself.

### §2.8 Question / Build Card

The live-construction device: a vague question at the top, and the specification being built
underneath it beat by beat. Used in Episodes 3–6, where the point is watching a transformation
happen rather than seeing its result.

### §2.9 End Card

Graphite. The episode's takeaway, the artifact, and the bridge to the next episode. Never a
subscribe animation.

### §2.10 Downloadable Artifact

Portrait, print-ready, A4 via `P`. Every episode ships one thing a viewer can keep — a card, a
checklist, a template. The artifact is designed as a real document, not a screenshot of a slide,
because it has to survive outside the video.

### §2.11 Thumbnail

16:9, one flat amber block, one promise, and text that is readable at 168px wide.

**Never a collage of tool logos.** The thumbnail states what the episode will settle, not which
products appear in it.

### §2.12 Data Plot

Bars, points and intervals. Axes are drawn before the data, and they hold while the data
changes — because the argument is usually *"same axes, different result"*, and redrawing the
axes destroys it.

Confidence intervals are drawn whenever they exist. A bare bar chart of point estimates in a
chapter about uncertainty would be a lie told in the visual layer.

### §2.13 Scale Comparison

For quantities that differ by orders of magnitude, where a bar chart would render the smaller
value as a pixel.

### §2.14 Completeness Meter

For "how much of the methodology can you actually find?" — a filled fraction, not a score.
Deliberately not a percentage: the point is that some of it is missing, not that it earned 60%.

### §2.15 Chrome — record day only

Slide number, component label, scripted time, beat counter, drift clock, progress scrubber.

**It is an overlay.** Hiding it with `H` must not move a single pixel of the frame. If hiding
the chrome reflows the slide, the presenter checks framing against a layout that is not the one
being recorded.

The drift clock turns amber when the take is more than 25 seconds behind the scripted timing —
a signal to keep going and fix it in the edit, not to stop.

---

## §3 Rules that apply everywhere

1. **One idea per slide.** If a slide has two arguments, it is two slides.
2. **Elements arrive with the spoken line.** Never before, never in a batch.
3. **Nothing is on a timer.** The presenter drives every beat.
4. **Numbers are tabular.** Always.
5. **Illustrative data is labelled `ILLUSTRATIVE`.** Any figure not from a completed run says so
   on the slide. This is the visual counterpart of the data-lock rule in Episode 08.
6. **Every empirical claim carries a source strip.**
7. **The last frame of a build shows everything lit, nothing dimmed** — the summing-up beat.
8. **Flat.** No gradients, no shadows, no 3D, no bevel, no glow.

---

## Adding a component

Answer three questions first:

1. **What claim does it carry** that words alone leave abstract?
2. **Why does no existing component carry it?**
3. **What does it look like when the claim is false** — does the device still work, or does it
   only ever show the flattering case?

The third question is the one that matters. A device that can only render a clean result is a
device that will misrepresent a messy one, and most real benchmark results are messy.

Then add it to `parts/02-benchmarking/_archive/v1-m2lab/_shared/m2lab-deck.css` under §5 with a comment naming its claim, run
`./scripts/sync-design-language.sh`, and document it here.
