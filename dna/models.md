# CZR Studio — Models
# What CZR extracts from each reference. Specific. Bounded. Not worship — extraction.

> This file is Part 2 of the DNA vault.
> Equal weight to `vision.md`. Models inform; your vision decides.
> This file is live — scraped and updated as models evolve (see `dna/scrapers/`).

---

## How To Read This File

Each model has three sections:
- **What we take** — specific rules CZR applies, derived from studying the model
- **What we don't take** — explicit exclusions. Models inspire; they don't define.
- **The single principle** — one sentence that distills what CZR extracts

Models are equal to vision in weight. When they conflict, identify which aspect of each is in conflict and resolve deliberately — do not default to either.

---

## VOGUE

> *"The page is white. The image is everything."*

### What we take
- **Editorial hierarchy**: One image dominates. Typography is secondary to the image. Text is at scale — headline first, reader earns the body copy.
- **Color authority in photography**: Images are full color, full saturation. Never muted. Never filtered. The photograph is the editorial statement.
- **Issue rhythm**: Each section is a spread. You move through the site like you turn a page. Nothing is skimmed — it is read or it is not.
- **Title case in labels**: Category labels are proper nouns — "The Sprint", "The Knight", "The Guarantee". Never lowercase.
- **White space as editorial pace**: Empty space is not missing content. It is the pause between sentences.
- **The masthead**: The logo/wordmark is the authority signature. It does not animate. It does not compete.

### What we don't take
- The pink, the lifestyle photography, the celebrity adjacency
- The volume — Vogue publishes constantly. CZR releases deliberately.
- The multi-column layout — that is print. This is web.

### The single principle
**The image earns its size. The text earns its position.**

---

## HERMÈS

> *"A single orange box in a grey room."*

### What we take
- **Restraint as luxury**: The fewer elements, the more each one matters. Every element present must justify its existence.
- **The single accent**: Hermès orange (#E8601C) is rare — it appears once per page, maximum. If it appears twice, it loses its power.
- **Craft over speed (paradox)**: Hermès takes two years to make a bag. CZR takes 48 hours to deliver. The paradox is deliberate — the speed is the craft.
- **No explanation needed**: Hermès does not explain why the bag costs €10,000. CZR does not explain why it takes 48 hours. The work is self-evident.
- **The unboxing as reveal**: The first time the client sees the delivered site is a reveal moment. Everything before it is preparation. The reveal is not rushed.
- **Neutrality as canvas**: The background (black/cream) is the neutral store interior. Color only enters with the work — the photography, the accent, the client's brand.
- **Materials language**: We use leather/craft language where appropriate — "structured", "crafted", "built", not "created" or "made".

### What we don't take
- The equestrian iconography (the Knight is our own iconography)
- The silence on price — CZR is transparent on price. Hermès is not. We take the restraint, not the opacity.
- The exclusivity-as-rejection model — we say "get started", not "apply for access"

### The single principle
**Restraint is the work. Each element earns its place or it leaves.**

---

## SPACEX

> *"The mission is the message."*

### What we take
- **Data is raw**: Numbers are stated without decoration. "48 hours." "100%." "€999." Not "in just 48 hours!" or "a remarkable 100%." The number is the argument.
- **Mission-critical language**: Every word is load-bearing. Nothing is filler. The copy works like a technical brief — precise, no synonyms for precision.
- **Dark + depth**: Deep blacks, surfaces that suggest depth, not flatness. The dark sections have weight because of layered surfaces (`--surface`, `--surface-2`, `--surface-3`).
- **Progress is visible**: Status indicators, delivery timelines, step numbers — progress is always surfaced. The client always knows where they are.
- **The system is the product**: SpaceX sells systems — reusability, the whole pipeline. CZR sells the system: brief → build → ship. The process is as much the value as the result.
- **No unnecessary motion**: Animation communicates state change or progress. It does not decorate. The hero does not have orbiting particles. The process steps do not float.

### What we don't take
- The NASA-adjacent blue (#0d47a1 type) — navy (#0B1A2E) only, and only as alternate dark
- The rocket/aerospace metaphor — we are building websites, not launching rockets. The SpaceX discipline applies; the imagery does not.
- The constant live-feed energy — SpaceX is always launching. CZR is quiet between deliveries.

### The single principle
**State the mission. State the number. The work does not need embellishment.**

---

## APPLE

> *"The product is the hero. Everything else is the stage."*

### What we take
- **The reveal**: Each section reveals one thing. One product. One idea. One number. The viewer's attention is a resource — use it on one thing per beat.
- **Neutral interface, vivid product**: The UI is always neutral (black or cream). The client's work — the portfolio cases — is vivid, full color, filling the frame.
- **Product capture**: Case study images fill the panel. No thumbnails. No grids of 6 equals. When we show work, we show it at scale.
- **Typography as product**: Apple uses their own type as a design decision. CZR uses Syne 800 as a design decision — it is not a neutral choice, it is the voice of the wordmark.
- **The CTA as invitation, not demand**: "Get Started" not "Buy Now." "View Work" not "See Portfolio." Apple says "Learn more" — CZR says "Start a Project."
- **Feature density per section = one**: One message per section. One stat per card. One CTA per screen. Not because of minimalism aesthetics, but because it works.

### What we don't take
- The consumer-product photography (iPhone on white background) — we shoot editorial, not product catalog
- The rainbow color moments — Apple uses color for product differentiation. CZR uses color for accent only.
- The "one more thing" reveal structure — that is keynote. This is a service website.

### The single principle
**One thing per beat. The stage disappears so the work can breathe.**

---

## Synthesis Rules

When models conflict, apply these:

| Conflict | Resolution |
|---|---|
| Vogue says color, SpaceX says monochrome | Color lives in photography only. UI stays black/cream. |
| Hermès says slow, Apple says reveal fast | The pace of the reveal is slow. The product appears fully-formed. |
| Apple says explain the product, SpaceX says state the number | State the number. The product speaks. |
| Hermès says expensive silence, Vogue says editorial volume | Fewer sections — but each designed like a spread. |
| Any model vs. vision.md | Identify which specific rule conflicts. Choose deliberately. Document the choice here. |

---

## Scrapers — Continuous Model Research

> `dna/scrapers/` — automated research that keeps this file current.
> Each scraper monitors a model's public-facing outputs and extracts visual/copy patterns.

| Scraper | What it monitors | Update frequency |
|---|---|---|
| `scrapers/vogue.py` | vogue.com editorials, covers, headlines | Weekly |
| `scrapers/hermes.py` | hermes.com campaigns, product pages, copy | Weekly |
| `scrapers/spacex.py` | spacex.com launches, mission copy, UI patterns | On launch |
| `scrapers/apple.py` | apple.com product pages, event copy, keynote language | On event |

Scrapers extract: headline patterns, color usage, spacing decisions, animation choices, copy structure.
Output goes to `dna/scrapers/reports/` as timestamped markdown reports.
The synthesis — what changes in `models.md` — is a human decision. Scrapers inform; you decide.
