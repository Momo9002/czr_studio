# CZR Studio — Vision
# The Founder's Decisions. What I chose. Not derived from models.

> This file is Part 1 of the DNA vault.
> Equal weight to `models.md`. Neither overrides the other — they synthesise.
> Edit this when your vision for CZR shifts.
>
> **To change the website:** edit `## Tokens` at the bottom of this file.
> Then run: `python3 -m dna.sync` → commit → push. Done.

---

## Why CZR Exists

Premium brands are being failed by two extremes — agencies that take 6 weeks and still miss the point, or cheap freelancers that deliver templates. There is no one doing haute couture speed. I built CZR to be that third thing: irreproachable craft at an impossible pace. The brief gives us everything. We do the rest.

---

## The Knight ♞

The chess knight is the only piece that moves unconventionally — it jumps over obstacles, it does not move in straight lines, it cannot be blocked by what is in front of it. That is the avatar. Not because it is dramatic. Because it is accurate.

The Knight is matte black. It carries a single red accent line. It does not explain itself.

- The Knight is the brand representative — not a mascot, not a logo
- It appears alone, at scale, with negative space
- It never appears in groups or with text underneath it
- The red line is its only ornament. One line. That is all.

---

## The Offer Logic

**The Sprint — €999**
For brands that need to exist online. Three pages. 48 hours. No compromise on craft.
The price point removes doubt. The speed removes excuses. The guarantee removes risk.

**The Flagship — €2,499**
For brands that want a digital flagship. Not a website — a store you walk into.
Full architecture, CMS, e-commerce if needed, consultation on brand identity.

**The Retainer — €99/mo**
For brands that want the site to grow with them. Two updates a month. Priority. Cancel when you want.
This is the relationship, not the transaction.

The logic: low barrier entry (Sprint) → full commitment (Flagship) → ongoing relationship (Retainer).
No custom pricing. No negotiation. These are the prices. Take them or leave them.

---

## The 48h Guarantee

48 hours or you pay nothing. Unconditional. No questions. No conditions.

This is not a marketing claim. It is a constraint I chose to build the entire business around.
It forces ruthless clarity: brief fast, build fast, deliver. No approval chains because there are none.
The guarantee is the product as much as the website is.

If I ever remove the guarantee, CZR is a different company.

---

## The Duality — Dark / Cream

Dark mode is where we work. It is the studio.
Cream is what we deliver. It is the light the client steps into.

This is not aesthetic preference. It is architecture.
- Every dark section says: this is craft, precision, the black of a negative.
- Every cream section says: this is the delivered result, the print, the product.
- Maximum 2 consecutive sections of the same mode. The rhythm is the meaning.

---

## Markets — Dubai · NYC · Worldwide

Dubai: luxury brands, architecture studios, hospitality, high-growth founders. A market that is used to paying for quality and expects discretion.

NYC: creative directors, fashion labels, independent studios. Taste-driven. Reference-conscious. Speed is a flex here.

Worldwide: the brief is digital. The delivery is digital. Location is irrelevant.

These three are not random. Dubai is where luxury meets new money. NYC is where it meets culture. Worldwide is the principle.

---

## What We Never Do

- Mention AI. Technology is invisible. The result is what we sell.
- Use exclamation marks. Ever.
- Use: amazing, excited, leverage, synergy, innovative, cutting-edge, game-changing, bespoke, solution.
- Phone calls. The brief is structured. Concierge is chat only.
- Show our process until the client asks. We do, then we explain.
- Discount. The prices are the prices.
- Take on more than we can ship in 48 hours. The constraint is the craft.

---

## Voice — How CZR Speaks

Hermès copywriter. SpaceX mission brief.

Never sell — state. Never explain — imply.
Short sentences. One idea. Maximum 15 words.
Period endings. No exclamation marks.
"We do" not "we can."
"Delivered" not "provided."
"48 hours" not "fast" or "quickly."

The silence between sentences is as important as the sentences.

---

## Non-Negotiables

These do not change regardless of what models suggest:
1. The Knight is the only brand avatar
2. 48h delivery promise stays in every touchpoint
3. The guarantee language stays unconditional
4. No AI mention anywhere client-facing
5. Syne 800 for display type — no exceptions
6. Full IP transfer on every project — we keep nothing

---

## Tokens

> These are your visual decisions. Edit values here.
> Run `python3 -m dna.sync` after editing — synthesize.py will write these to identity.json → style.css → site.
> Keys map directly to CSS: type.display_weight → font-weight on all headings, etc.

```tokens
type.display_weight    = 700
type.display_tracking  = -0.03em
type.hero_size_max     = 9rem
type.hero_size_min     = 4rem
type.h2_size_max       = 5.5rem
type.h2_size_min       = 2.8rem
type.body_size         = 0.95rem
type.body_line_height  = 1.85
type.eyebrow_tracking  = 0.28em
type.eyebrow_size      = 0.6rem

space.section_v        = clamp(8rem, 16vw, 16rem)
space.section_h        = clamp(1.5rem, 4vw, 5rem)
space.component_v      = clamp(3rem, 6vw, 6rem)
space.gap              = 1px

surface.radius         = 0
surface.border_alpha   = 0.04

accent.line_width      = 1px
accent.red_alpha_bg    = 0
```
