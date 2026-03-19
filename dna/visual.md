# CZR Studio — Visual DNA

> Read by: website, campaign, portfolio, production

---

## The Duality Principle

Inspired by **Apple, Hermès, SpaceX** — three brands that master contrast.

| Mode | When | Background | Text |
|---|---|---|---|
| **Dark** | Craft, studio, the Knight | `#000000` | `#FFFFFF` |
| **Light** | Delivered work, results, joy | `#F7F4EF` | `#0a0a0a` |

**Rule:** Maximum 2 consecutive sections of the same mode. Contrast creates rhythm.

---

## Color Tokens

| Token | Hex | Role |
|---|---|---|
| `--czr-black` | `#000000` | Primary background (dark mode) |
| `--czr-cream` | `#F7F4EF` | Primary background (light mode) |
| `--czr-white` | `#FFFFFF` | Text on dark |
| `--czr-dark-text` | `#0a0a0a` | Text on cream |
| `--czr-red` | `#C8242A` | Accent only — never fill — Knight mane, thin lines |
| `--czr-surface` | `#080808` | Dark cards, elevated surfaces |
| `--czr-muted` | `#999999` | Secondary text on dark |
| `--czr-muted-light` | `#666666` | Secondary text on cream |
| `--czr-gold` | `#C9A84C` | Reserve — once per 10 posts/pages max |

**Forbidden:** Mondrian primaries (blue `#1A4BA8`, yellow `#F0C029`) in main content. Tiny accent tiles only.

---

## Typography

| Role | Font | Weight | Notes |
|---|---|---|---|
| Headlines | Syne | 800 | Letter-spacing: -0.04em |
| Body | Manrope | 400 | Line-height: 1.65 |
| Eyebrow labels | Manrope | 700 | ALL CAPS, letter-spacing: 0.20em |
| Captions | Manrope | 300–400 | Sentence case, period endings |

**Google Fonts import:**
```html
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Manrope:wght@300;400;600;700&display=swap" rel="stylesheet">
```

---

## Photography Rules

### Dark Mode Photos
- Black backgrounds, nero marquina marble, matte surfaces
- Single cinematic light source from side-left
- Knight visible as recurring element
- Max 3 objects in frame
- Shallow depth of field

### Light Mode Photos
- Warm cream (`#F7F4EF`) backgrounds, linen, light oak
- Soft natural daylight from window
- MacBook / iPad / iPhone showing real CZR client work
- Props: ceramic espresso cup, dried pampas grass, architecture books, thin pen
- Feels like: Hermès store window, Kinfolk editorial, Apple launch

### Always Forbidden
- ❌ Flat-lay on white backgrounds
- ❌ Stock photography of any kind
- ❌ Text-on-black graphics as posts
- ❌ Neon, heavy gradients, multicolor fills
- ❌ Text overlays on photos (captions handle words)
- ❌ More than 3 objects in frame
- ❌ Humans (Knight is the avatar)

---

## Website Section Map

| Section | Mode | Rationale |
|---|---|---|
| Hero | Dark | Dramatic opening, Knight presence |
| Marquee | Dark | Continuation |
| Portfolio Grid | Dark | The work is serious craft |
| Process | **Cream** | Four moves — educational, approachable |
| Results | Dark | Metrics hit harder on black |
| Guarantee | **Cream** | Calm, trustworthy, reassuring |
| Pricing | Dark | Professional authority |
| FAQ | Dark | Continuation |
| CTA / Contact | **Cream** | Warm, inviting close |

---

## The Knight — Usage Rules

The Knight (`♞`) is CZR's avatar. It appears:
- As the favicon and profile picture
- In the hero section of the website (SVG or image, subtle)
- On every portfolio page watermark (bottom-right, 32px, 30% opacity)
- In Instagram posts as a recurring editorial element
- Never colored — always matte black with red accent line

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
