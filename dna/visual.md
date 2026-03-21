# CZR Studio — Visual DNA

> Read by: website, campaign, portfolio, production

---

## Brand Models — Visual Influence

| Model | What CZR takes |
|---|---|
| **Vogue** | Editorial page layout. Typography as art. Generous white space. Every spread tells one story. |
| **Hermès** | One object. One moment. Nothing else in frame. The craft speaks without captions. |
| **SpaceX** | Technical precision. Data-forward. Dark interfaces. Countdown energy. |
| **Apple** | Product reveals. Let the work breathe. Obsessive pixel polish. The interface disappears. |

---

## The Duality Principle

| Mode | When | Background | Text |
|---|---|---|---|
| **Dark** | Craft, studio, the Knight, tension | `#000000` | `#FFFFFF` |
| **Light** | Delivered work, results, warmth, resolution | `#F7F4EF` | `#0a0a0a` |

**Rule:** Maximum 2 consecutive sections of the same mode. Contrast creates rhythm.

**Principle:** Dark mode is the *question*. Light mode is the *answer*. Every transition is a reveal — like turning a Vogue page.

---

## Color Tokens

| Token | Hex | Role |
|---|---|---|
| `--czr-black` | `#000000` | Primary background (dark mode) |
| `--czr-cream` | `#F7F4EF` | Primary background (light mode) |
| `--czr-white` | `#FFFFFF` | Text on dark |
| `--czr-dark-text` | `#0a0a0a` | Text on cream |
| `--czr-red` | `#C8242A` | Accent only — never fill — Knight mane, thin lines, progress bars |
| `--czr-surface` | `#080808` | Dark cards, elevated surfaces |
| `--czr-muted` | `#999999` | Secondary text on dark |
| `--czr-muted-light` | `#666666` | Secondary text on cream |
| `--czr-gold` | `#C9A84C` | Reserve — once per 10 posts/pages max |

**Forbidden:** Mondrian primaries (blue, yellow) in main content. Tiny accent tiles only.

---

## Typography

| Role | Font | Weight | Notes |
|---|---|---|---|
| Headlines | Syne | 800 | Letter-spacing: -0.04em. Headlines should feel heavy. Like a Vogue cover line. |
| Body | Manrope | 400 | Line-height: 1.65. Clean, breathing. Like Apple copy — room around every sentence. |
| Eyebrow labels | Manrope | 700 | ALL CAPS, letter-spacing: 0.20em. Like Hermès category labels. |
| Captions | Manrope | 300–400 | Sentence case, period endings. SpaceX mission log register. |

---

## Layout Principles

### From Vogue
- Every section is a **spread**. One idea per section.
- White space is a design decision, not empty space.
- Typography is the art — images support it, not the other way around.
- Asymmetry is intentional. Grid breaks create editorial tension.

### From Apple
- **One hero per section.** No visual competition.
- Generous padding. Things breathe. Nothing is crowded.
- The product (the website we built) is always the centrepiece.
- Transitions are smooth, never abrupt. Apple Keynote pacing.

### From Hermès
- **Maximum 3 elements per composition.** Restraint is luxury.
- The single object in empty space communicates more than a grid of thumbnails.
- Storytelling through absence — what you leave out defines the message.

### From SpaceX
- **Data is visual.** Numbers are larger than surrounding text.
- Metrics stand alone in dark mode. No decoration around them.
- Countdown energy — timelines, phases, and deadlines are prominent.

---

## Photography — Mood by Industry

Each portfolio shoot must match the **client's world**, not CZR's default.

### Fashion / Luxury
- Fabric textures (silk, cashmere, raw linen)
- Runway lighting: single sharp sidelight
- Props: needle, thimble, measuring tape
- Palette: black + cream + one warm accent from the client's brand

### Architecture / Interiors
- Raw material textures (concrete, marble, timber grain)
- Architectural lighting: one beam, hard shadows
- Props: scale model, drafting pencil, trace paper
- Palette: concrete grey + black + warm wood tone

### Fine Dining / Hospitality
- Table setting textures (linen, ceramic, raw oak)
- Golden hour or candle-warm light
- Props: single dish, wine glass, herb sprig
- Palette: cream + warm neutrals + one deep accent

### Fragrance / Beauty
- Skin and glass textures (frosted bottle, marble slab)
- Soft diffused light with one specular highlight
- Props: single bottle, dried flower, stone
- Palette: black + matte rose or amber

### Photography / Creative Direction
- Paper and process textures (contact sheets, film strips)
- Mixed light: warm practicals + cool daylight
- Props: prints, loupe, light table
- Palette: high contrast B&W + one bold colour

### Default
- Nero marquina marble, matte surfaces
- Single cinematic light from side-left
- Knight as recurring element
- Max 3 objects in frame, shallow DOF

### Always Forbidden
- ❌ Flat-lay on white backgrounds
- ❌ Stock photography
- ❌ Text-on-black graphics as posts
- ❌ Neon, heavy gradients, multicolor fills
- ❌ Text overlays on photos
- ❌ More than 3 objects in frame
- ❌ Humans (Knight is the avatar)
- ❌ Cluttered compositions — Hermès restraint applies everywhere

---

## Website Section Map

| Section | Mode | Feel | Model Influence |
|---|---|---|---|
| Hero | Dark | Arrival. "You've entered something different." | SpaceX launch countdown |
| Marquee | Dark | Movement. Urgency without pressure. | Apple keynote ticker |
| Portfolio Grid | Dark | The work. Each card hints at a world. | Vogue editorial grid |
| Process | **Cream** | Relief. "Four steps — that's it." | Apple product page flow |
| Results | Dark | Impact. Numbers on black. | SpaceX mission metrics |
| Guarantee | **Cream** | Trust. "We believe in this enough to guarantee it." | Hermès packaging confidence |
| Pricing | Dark | Decision. Clear, no tricks. | Apple pricing table |
| FAQ | Dark | Transparency. | Hermès Q&A simplicity |
| CTA / Contact | **Cream** | Invitation. "We're ready when you are." | Hermès warm close |

---

## The Knight — Usage Rules

The Knight (`♞`) is CZR's avatar. It appears:
- As the favicon and profile picture
- In the hero section of the website
- On every portfolio page watermark (bottom-right, 32px, 30% opacity)
- In Instagram posts as a recurring editorial element
- Never coloured — always matte black with red accent line
- Never floating randomly — always placed with intent

---

## Spacing System

```css
--sp-1: 0.25rem;   --sp-2: 0.5rem;    --sp-3: 0.75rem;
--sp-4: 1rem;      --sp-6: 1.5rem;    --sp-8: 2rem;
--sp-10: 2.5rem;   --sp-12: 3rem;     --sp-16: 4rem;
--sp-24: 6rem;     --sp-32: 8rem;
```

Section padding: `clamp(5rem, 10vw, 10rem) 0`
Container max-width: `1360px`
