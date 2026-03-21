# CZR Portfolio Contract

> Source: `dna/identity.json`, `dna/visual.md`, `dna/voice.md`
> Apply this to every case study page and every Instagram portfolio post.

---

## The Soul Requirement

Every portfolio piece must have a **soul sentence** — the one thing that makes this project irreplaceable. This sentence appears in the case study page, the Instagram caption, and the LinkedIn post.

**How to find the soul:**
1. What does this client refuse to do?
2. What constraint made the design inevitable?
3. What number, fact, or detail would surprise someone?
4. If you removed the client name, could you tell which project this is?

**Examples:**
| Client | Soul Sentence |
|---|---|
| Fashion house | "Fourteen silhouettes. Appointment-only. No cart." |
| Architecture | "Twelve commissions per year. If it can't be justified structurally, it's removed." |
| Restaurant | "One table. Twelve guests. One chef. By request only." |
| Fragrance | "72 bottles per edition. Each one numbered." |
| Photographer | "No cropping. No retouching. The frame is the decision." |
| Creative director | "No agency name. No logo. The work IS the brand." |

---

## Case Study Page Requirements

### Each site must feel like its own world

**Do not copy-paste the CZR studio aesthetic onto client sites.** Each case study is a demonstration that we can enter someone else's world and build something that feels native to them.

| Element | Rule |
|---|---|
| **Typography** | Must match the client's industry mood — never default to Syne/Manrope for client sites |
| **Color palette** | Derived from the client's brand or industry — never CZR's palette |
| **Layout** | Unique grid per site — never the same template twice |
| **Photography** | Follow the industry mood from `visual.md` — each industry has its own light, texture, props |
| **Copy** | Written in the client's voice, not CZR's |

### Structure
1. **Hero** — Full-bleed. Client name. One line that captures the soul.
2. **Work showcase** — Minimum 3 screenshots: desktop hero, mobile, key inner page.
3. **The detail** — One zoomed-in moment that shows craft (a hover state, a transition, a type pairing).
4. **Context** — 2-3 sentences. What the client does, what they needed, what we delivered.
5. **Footer** — `Built by CZR Studio ↗` linking back to czr.studio.

### URL Pattern
`czr.studio/cases/[client-slug]/`

### Meta
```html
<title>[Client Name] — Built by CZR Studio</title>
<meta name="description" content="[Soul sentence]. Built by CZR Studio.">
```

### Technical Requirements
- `♞ CZR` watermark — bottom-right, 30% opacity
- Meta Pixel installed
- Responsive: 375px → 1440px
- Lighthouse ≥ 90

---

## Instagram Portfolio Post

Image: Device mockup in the client's industry mood (see `visual.md` per-industry rules).

**Caption:** Follow the soul-finding process from `voice.md`. Never the same structure twice.

---

## Quality Gate

A portfolio piece (page or post) only goes live if:

1. [ ] **Soul test** — It has a soul sentence that could only describe THIS project
2. [ ] **Immersion test** — Could another studio have made this? If yes → redo the design
3. [ ] **Differentiation test** — Does it look and feel different from every other CZR case study?
4. [ ] **Voice test** — Caption follows voice.md rules, passes brand guard
5. [ ] **Visual test** — Image looks like it belongs in AD Architectural Digest or Kinfolk
6. [ ] **Technical test** — Meta pixel, watermark, responsive, Lighthouse ≥ 90
