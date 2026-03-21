# CZR Studio — Visual DNA

> Read by: website, campaign, portfolio, production

---

## Brand Models — Visual Influence

| Model | What CZR takes |
|---|---|
| **Vogue** | Editorial color authority. Full-color photography, jewel tones, bold type on white. The color in photography is the statement — not shy, not muted. Black masthead, full-color world beneath. |
| **Hermès** | Signature orange (#E8601C). Rich leather and amber tones. Color is rare but unmistakable — like a single orange box in a grey room. Restraint makes each color moment powerful. |
| **SpaceX** | Deep space navy + electric blue. Dark, precise, mission-critical. Color only to convey data or progress. Everything else is black and metallic. |
| **Apple** | Products burst with color against clean white/black backgrounds. The interface is neutral — the product is the color. Saturated, confident, never fussy. |

---

## Color Philosophy — The CZR Principle

> **The canvas is black. The world inside is in full color.**

Black and cream are the structure. Color is what lives inside.
- Photography is **full color, unrestricted** — it is the editorial statement.
- The brand frame (typography, UI, backgrounds) stays black/cream.
- Accent colors appear strategically — like a single orange Hermès box.

This is how Vogue works: white page, full-color spread inside.
This is how Apple works: matte black device, vibrant screen inside.
This is how Hermès works: grey concrete store, one orange element.

---

## Color Tokens

### Foundation (Structure — never change)
| Token | Hex | Role |
|---|---|---|
| `--black` | `#000000` | Primary background (dark mode) |
| `--cream` | `#F7F4EF` | Primary background (light mode) |
| `--white` | `#FFFFFF` | Text on dark |
| `--dark-text` | `#0a0a0a` | Text on cream |

### Accent Palette (Use with intention)
| Token | Hex | Model | Frequency |
|---|---|---|---|
| `--red` | `#C8242A` | CZR primary — Knight mane, lines, progress | Always available |
| `--hermes` | `#E8601C` | Hermès — warm tension, urgent CTAs, featured badges | Max 1 use per page |
| `--navy` | `#0B1A2E` | SpaceX — deep dark sections, data overlays | Alternate dark mode only |
| `--electric` | `#1B6CA8` | SpaceX — live status, active states, links in dark | Functional only |
| `--gold` | `#C9A84C` | Hermès hardware — achievement, premium moments | Reserve — once per page max |

### Surface System (Dark)
| Token | Hex | Role |
|---|---|---|
| `--surface` | `#080808` | Cards, elevated dark |
| `--surface-2` | `#111111` | Hover states, featured cards |
| `--surface-3` | `#1a1a1a` | Borders, subtle dividers |

### Portrait Colors (Photography — no restriction)
Photography is **always full color**. No desaturation. No grayscale filters.
The editorial color IS the content. Each industry has a defined palette:

| Industry | Primary | Secondary | Accent |
|---|---|---|---|
| Fashion | Black + cream + one client brand color | Fabric texture tones | Metallic if present |
| Architecture | Concrete grey + warm timber | Shadow blacks | Sky blue or raw steel |
| Fine Dining | Warm amber + cream + oak | Deep shadow | Garnish green or wine red |
| Fragrance | Black + amber glass + marble veining | Soft skin tone | Dry petal rose/ivory |
| Photography | High contrast B&W + one strong saturated color | Paper white + shadow | Film orange or deep teal |
| Creative Direction | Concrete + warm lamp + white paper | Black equipment | One bold artwork color |

---

## The Duality System

| Mode | When | Background | Text | Photography |
|---|---|---|---|---|
| **Dark** | Craft, studio, the Knight, tension | `#000000` | `#FFFFFF` | Full color — pops against black |
| **Cream** | Delivered work, results, warmth | `#F7F4EF` | `#0a0a0a` | Full color — editorial spreads |

**Rule:** Maximum 2 consecutive sections of the same mode.
**Principle:** Dark is the *question*. Cream is the *answer*. Photography is what makes both feel alive.

---

## Typography

| Role | Font | Weight | Notes |
|---|---|---|---|
| Headlines | Syne | 800 | Letter-spacing: -0.04em. Like a Vogue cover line — heavy, inevitable. |
| Body | Manrope | 400 | Line-height: 1.65. Apple copy register — room around every sentence. |
| Eyebrow labels | Manrope | 700 | ALL CAPS, letter-spacing: 0.22em. Hermès category labels. |
| Captions | Manrope | 300–400 | Sentence case, period endings. SpaceX mission log register. |

---

## Layout Principles

### From Vogue — Editorial Authority
- Every section is a **spread**. One idea per section, told completely.
- Full-bleed photography. Images are never thumbnails — they are environments.
- Typography commands. Images support. Never the other way.
- Asymmetry creates tension. The grid breaks are intentional.

### From Apple — Product Reveal
- **The work is always the hero.** Let the website case study fill the frame.
- Generous breathing room around every element.
- Smooth reveal animations — Apple Keynote pacing, never abrupt.
- One focal point per section. No visual competition.

### From Hermès — Restraint as Luxury
- What you remove defines you more than what you include.
- Maximum 3 elements in any composition.
- Color is rare — when it appears, it is unmissable.
- The empty space is as intentional as the content.

### From SpaceX — Data as Design
- Numbers are larger than the words around them.
- Metrics are displayed raw, on black, with zero decoration.
- Timelines and phases are always visible to the client.
- The deadline is never hidden.

---

## Photography Rules

### Always
- ✅ Full color — never desaturated, never grayscale unless deliberately B&W for purpose
- ✅ Single dominant light source
- ✅ Max 3 objects in frame
- ✅ Subject has negative space to breathe
- ✅ Industry mood matches client's world

### Never
- ❌ Flat-lay on white backgrounds
- ❌ Stock photography
- ❌ Text overlays on photos (captions handle words)
- ❌ More than 3 objects in frame
- ❌ Humans — the Knight is the avatar
- ❌ Neon or multicolor gradient fills in UI
- ❌ Heavy vignetting as a design crutch

---

## Website Section Map

| Section | Mode | Color Moment | Feel |
|---|---|---|---|
| Hero | Dark | Red accent line + Knight on black marble | SpaceX launch |
| Portfolio Grid | Dark | Full-color editorial photography pops against black | Vogue spread |
| Process | Cream | Red progress lines on cream — Hermès touch | Apple keynote |
| Results | Dark | White metrics on black — SpaceX data | Mission confirmed |
| Guarantee | Cream | Subtle warm amber/Hermès note in tone | Hermès box opening |
| Pricing | Dark | Hermès orange on featured card badge | Apple pricing table |
| Contact | Dark | Red submit accent — no color noise | Clean close |

---

## The Knight — Usage Rules

The Knight (`♞`) is CZR's avatar. It appears:
- As the favicon and profile picture (matte black)
- In the hero section (backlit with red rim)
- On portfolio page watermarks (bottom-right, 30% opacity)
- In Instagram posts as a recurring editorial element
- Never coloured — always matte black with red accent
- Always placed with intent — never floating

---

## Spacing System

```css
Section padding: clamp(6rem, 12vw, 12rem) 0
Container max-width: 1440px
Container padding: clamp(1.5rem, 4vw, 4rem)
```

---

## CSS Layout Rules — Required (DesignAgent must implement these exactly)

These prevent horizontal overflow and ensure correct layout on all screen sizes.

```css
/* Global overflow prevention — REQUIRED */
html, body {
  overflow-x: hidden;
  max-width: 100%;
}

/* All elements must respect container width */
* { box-sizing: border-box; }

/* Nav must not exceed viewport */
nav, .nav {
  width: 100%;
  max-width: 100vw;
}

/* Sections must never create horizontal scroll */
section {
  width: 100%;
  overflow: hidden;
}

/* Container must have explicit padding, not cause bleed */
.container {
  width: 100%;
  max-width: var(--container-max-width);
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--container-padding);
  padding-right: var(--container-padding);
  box-sizing: border-box;
}
```

These rules are non-negotiable. Any element wider than the viewport breaks the design.
