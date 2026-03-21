# CZR Studio — Campaign Journal

> Log every campaign, result, and learning. This document gets smarter with every cycle.
> Format: one entry per campaign. Fill in after each 7-day cycle.

---

## Campaign #001 — WhatsApp Leads March 2026

| Field | Value |
|---|---|
| **Name** | CZR Studio — WhatsApp Leads — March 2026 |
| **Campaign ID** | `120241184370110193` |
| **Ad Set ID** | `120241184370250193` |
| **Ad 1 ID** | `120241184372530193` (48h WhatsApp CTA) |
| **Ad 2 ID** | `120241184372880193` (3 Spots → czr.studio) |
| **Objective** | TRAFFIC (link clicks → WhatsApp/czr.studio) |
| **Platform** | Instagram (feed + explore) |
| **Geo** | UAE only |
| **Age** | 28-45 |
| **Interests** | Web design, Entrepreneurship, Branding |
| **Daily Budget** | $10 |
| **Creative** | 2 static images — A/B test |
| **CTA** | WhatsApp direct + Learn More |
| **Start Date** | TBD (currently PAUSED) |
| **End Date** | — |

### Pre-Launch Checklist
- [x] Meta Pixel installed on czr.studio (ID: 2928293767375852)
- [x] Pixel on all case study pages
- [x] Lead event on WhatsApp clicks
- [ ] Deploy Pixel to production (Vercel)
- [x] Old campaigns paused
- [x] Audience narrowed to AE-only, 28-45
- [x] 2 creatives (A/B test)
- [ ] Campaign activated

### Results (fill after 7 days)

| Metric | Value | Notes |
|---|---|---|
| Impressions | — | |
| Reach | — | |
| Clicks | — | |
| CTR | — | Target: > 1.0% |
| CPC | — | Target: < $1.50 |
| Total Spend | — | |
| Leads (WhatsApp convos) | — | |
| CPL | — | Target: < $20 |
| Clients Closed | — | |
| Revenue from Clients | — | |
| ROAS | — | Target: > 5x |
| Frequency | — | Target: < 3.0 |

### Learnings & Actions
```
After 7 days, answer:
1. Which creative had the best CTR?
2. What time of day got the most clicks?
3. Was the CTA effective? Should we switch to WhatsApp direct?
4. Did the audience feel right or was it too broad?
5. What should we change for Campaign #002?
```

### Changes Made
- None yet

---

## Campaign #002 — (Template)

| Field | Value |
|---|---|
| **Name** | |
| **Campaign ID** | |
| **Objective** | |
| **Platform** | |
| **Geo** | |
| **Daily Budget** | |
| **Creative** | |
| **Start Date** | |

### Pre-Launch Checklist
- [ ] Previous campaign learnings reviewed
- [ ] Creative refreshed (no reuse from previous cycle)
- [ ] Budget adjusted based on previous ROAS
- [ ] Audience refined based on data

### Results (fill after 7 days)

| Metric | Value | Notes |
|---|---|---|
| Impressions | — | |
| CTR | — | vs Campaign #001: |
| CPC | — | vs Campaign #001: |
| Leads | — | vs Campaign #001: |
| CPL | — | vs Campaign #001: |
| ROAS | — | vs Campaign #001: |

### Learnings & Actions
```
1. What improved vs last campaign?
2. What got worse?
3. What's the one thing to change next?
```

---

## Running Learnings Bank

> Add observations here as they come. These compound over time.

| Date | Learning | Source |
|---|---|---|
| 2026-03-19 | Meta API requires `is_adset_budget_sharing_enabled` and `advantage_audience` fields in v22 | API testing |
| 2026-03-19 | System User must be explicitly assigned to ad account AND page | API testing |
| 2026-03-19 | No Pixel = no retargeting = blind spending | Strategy research |
| 2026-03-19 | For $10/day: 1 campaign, 1 ad set, 2-3 creatives. Don't split. | Best practice research |
| 2026-03-19 | 80% of Instagram Reels plays are with sound off → always use captions | Meta data |
| 2026-03-19 | First 3 seconds = everything. Movement/bold text stops the scroll. | Creative research |
| 2026-03-19 | WhatsApp destination ads available on this account — ideal for CZR | API capabilities check |
| 2026-03-19 | EU targeting requires DSA fields (dsa_beneficiary/dsa_payor) — skip EU until needed | API testing |
| 2026-03-19 | Never bump budget > 20% at once — resets Meta's learning phase | Industry best practice |
| 2026-03-19 | Kill ad if CTR < 0.5% after 1,000 impressions | Budget optimization |
