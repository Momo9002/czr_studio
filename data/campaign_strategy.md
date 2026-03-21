# CZR Studio — Campaign Strategy & Playbook

> Living document. Updated after every campaign cycle.
> Last updated: 2026-03-19

---

## Current State

| Metric | Value |
|---|---|
| Ad Account | `act_1478847513654542` (CZR_AD) |
| Currency | USD |
| Timezone | Asia/Dubai |
| Billing | Mastercard *5710 |
| Meta Pixel | ❌ **NOT INSTALLED** — critical gap |
| Active Campaigns | 1 (PAUSED) |
| Total Spend | $0 |
| Clients from Ads | 0 |

---

## Critical Fixes (Before First $1 Spent)

### 1. Install Meta Pixel on czr.studio

**Why:** Without a Pixel, Meta cannot track who visits your site, who converts, or who to retarget. You're flying blind. No pixel = no conversion optimization = wasted budget.

```
Pixel events to track:
- PageView (every page)
- Lead (WhatsApp click / form submit)
- Contact (DM click)
- ViewContent (case study view)
```

### 2. Switch from TRAFFIC → LEAD GENERATION objective

**Why at $10/day:** Traffic campaigns optimize for clicks. But clicks don't pay. At $10/day you need every dollar aimed at people who will *message you*. Lead gen campaigns optimize for the action that matters.

Best setup for CZR: **Messages objective → WhatsApp destination** — your account has `WHATSAPP_DESTINATION_ADS` capability. This sends people directly to your WhatsApp (`+18107764057`) where you close deals.

### 3. Narrow the Audience

Current reach: **40-48M people** — way too broad for $10/day. Meta's algorithm can't learn with that much noise.

**Recommended audience (< 2M):**
- 🌍 AE only (start hyperlocal in Dubai, expand after proving ROI)
- 👤 Ages 28-45
- 💼 Interests: Brand management, Entrepreneurship, Small business owners, Luxury goods
- 📱 Instagram only (feed + explore + Reels)

---

## Campaign Structure (Optimal for < $20/day)

```
1 Campaign (Messages / Lead Gen)
└── 1 Ad Set ($10/day, AE, 28-45, entrepreneurs)
    ├── Ad 1: Static image — "Your Site. 48 Hours."
    ├── Ad 2: Carousel — 3 case study screenshots
    └── Ad 3: Video/Reel — 15s process walkthrough
```

**Rules:**
- **1 ad set only** — don't split budget, let Meta optimize across 2-3 creatives
- **Lowest cost bidding** — at $10/day, never use bid caps
- **No changes for 7 days** after launch — let the learning phase complete
- **Kill underperformers at Day 7** — turn off any ad with CTR < 0.5%
- **Refresh creatives every 30 days** — swap in new visuals before fatigue

---

## Creative Playbook

### What Works for Service Business Ads on Instagram

| Format | Performance | Notes |
|---|---|---|
| **Video / Reels** (15s) | 🟢 Best | First 3s = hook. Movement stops scroll. Add captions (80% watch muted) |
| **Carousel** | 🟢 Great | Show 3 case study screenshots. Each slide = different project |
| **Static image** | 🟡 OK | Works for retargeting. Weak for cold audiences |
| **Stories** | 🟡 OK | Good for urgency. "3 spots left" works well here |

### Creative Rotation Schedule

| Week | Creative | Focus |
|---|---|---|
| 1-2 | Launch set (current 3 images) | Test which resonates |
| 3-4 | Replace worst performer | Add video Reel |
| 5-6 | Refresh all visuals | New case studies, new hooks |
| 7+ | Scale winner | Expand geo, increase budget on best CTR ad |

### Caption Formulas That Convert (CZR voice)

```
Hook → Pain → Solution → CTA

"Three agencies. Six weeks each. We do it in 48 hours."
"Your website is losing you clients. Fix it this week."
"No meetings. No decks. Just a WhatsApp brief and a live site."
```

---

## Budget Control Rules

| Budget | Strategy |
|---|---|
| **$5/day** | 1 ad set, 1 creative, AE only. Test mode. |
| **$10/day** | 1 ad set, 2-3 creatives, AE only. Learning & optimizing. |
| **$20/day** | 1 ad set, 3 creatives, AE + US. Ready to scale what works. |
| **$50/day** | 2 ad sets (AE and US separate), 3 creatives each. Scale mode. |

**Golden rule:** Never increase budget by more than 20% at a time. Meta's algorithm resets learning if you jump too fast.

**Kill criteria:**
- CTR < 0.5% after 1,000 impressions → kill the ad
- CPC > $3.00 → kill the ad
- No leads after $30 spent → kill the ad set
- Frequency > 3.0 → creative is fatigued → swap it

---

## Measurement Framework

| KPI | Target | How to Track |
|---|---|---|
| **CTR** (click-through rate) | > 1.0% | Ads Manager |
| **CPC** (cost per click) | < $1.50 | Ads Manager |
| **CPL** (cost per lead) | < $20 | Ads Manager + Pixel |
| **ROAS** (return on ad spend) | > 5x | Manual (client revenue ÷ ad spend) |
| **Frequency** | < 3.0 | Ads Manager |
| **WhatsApp conversations** | 1+/day | WhatsApp + Ads Manager |

---

## Advanced Tactics (After First Client)

1. **Retargeting**: Create Custom Audience of website visitors (requires Pixel) → serve them a different ad ("Still thinking? 2 spots left.")
2. **Lookalike Audience**: Upload client list → Meta finds similar people → highest-quality cold audience
3. **Advantage+ Creative**: Let Meta auto-optimize headline/image combos — works well after 50+ conversions
4. **Instagram Shopping / Lead Forms**: Test native lead forms vs WhatsApp destination — track which has lower CPL
5. **A/B Test Landing Pages**: czr.studio vs dedicated landing page with single CTA
