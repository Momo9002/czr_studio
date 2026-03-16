# Marketing Swarm — Design

> Third swarm for Aura Web Studio. Handles brand presence, content, and growth.
> Runs alongside the Worker Swarm (LeadGen/Build) and Meta Swarm (Auditor).

---

## Purpose

The Worker Swarm finds and serves clients.
The Marketing Swarm makes clients find Aura.

| Worker Swarm | Marketing Swarm |
|---|---|
| Outbound — Aura goes to clients | Inbound — clients come to Aura |
| DMs, proposals, site builds | Instagram, LinkedIn, blog, SEO |
| Triggered manually or daily | Triggered weekly (content calendar) |

---

## What It Does

### 1. Website Maintenance
- Monitors `index.html` + `style.css` for staleness (QA pass monthly)
- Updates case study count, testimonials, trust metrics
- Checks all links, images, and mobile breakpoints
- Proposes fixes → writes directly to repo (or opens PR)

### 2. Instagram Content
- Pulls from completed client work (`output/proposals/`, `output/builds/`)
- Generates 3 post types per week:
  - **Before/After** — client's old vs new site
  - **Process reel** — 48h build timeline
  - **Social proof** — result metric from delivered project
- Outputs: caption + hashtags + image brief (for generate_image or Canva prompt)
- Optional: schedules via Buffer/Later API

### 3. LinkedIn Content
- More professional angle — targets agency owners and founders
- 1 post per week: insight, case study, or "how we built X" story
- Uses `StrategistAgent` output as source material (strategy docs = content)

### 4. SEO Blog (future)
- 1 article/month on luxury web design
- Targets long-tail: "luxury restaurant website Dubai", "haute couture web design"
- Written by `BlogWriterAgent`, validated for SEO by `SeoValidatorAgent`

---

## Swarm Architecture

```
MarketingOrchestratorAgent  [BaseAgent]
  reads marketing_state.json (weekly schedule, last post date, content queue)
  │
  ├── WEBSITE_AUDIT  → SiteAuditSwarm
  │     SiteQAAgent       reads index.html → scores quality 0-10
  │     SiteFixAgent      applies approved fixes to index.html, style.css
  │
  ├── INSTAGRAM     → InstagramSwarm [SequentialAgent]
  │     ContentStrategyAgent   reads latest completed work → picks post angle
  │     CaptionWriterAgent     writes caption + hooks + hashtags
  │     ImageBriefAgent        writes Midjourney/generate_image prompt
  │     InstagramQualityLoop   [LoopAgent] validates tone/hook/length
  │     → output/social/instagram/{date}_post.json
  │
  ├── LINKEDIN      → LinkedInSwarm [SequentialAgent]
  │     InsightPickerAgent     picks most interesting recent project/learnings
  │     LinkedInWriterAgent    writes 150-word post, professional tone
  │     LinkedInQualityLoop    [LoopAgent] validates authority/value/CTA
  │     → output/social/linkedin/{date}_post.json
  │
  └── BLOG (future) → BlogSwarm [SequentialAgent]
        KeywordAgent   picks target keyword
        BlogWriterAgent  writes 800-word article
        SeoValidatorAgent  checks keyword density, meta, structure
        → output/blog/{date}_article.md
```

---

## State File: `marketing_state.json`

```json
{
  "last_site_audit": "2026-03-14",
  "last_instagram_post": "2026-03-13",
  "last_linkedin_post": "2026-03-10",
  "content_queue": [],
  "completed_builds": [],
  "weekly_schedule": {
    "monday": "INSTAGRAM",
    "wednesday": "LINKEDIN",
    "friday": "INSTAGRAM",
    "sunday": "WEBSITE_AUDIT"
  }
}
```

---

## ADK Patterns Used

| Pattern | Where |
|---|---|
| `BaseAgent` | `MarketingOrchestratorAgent` — reads schedule, routes to correct sub-swarm |
| `SequentialAgent` | All content pipelines |
| `LoopAgent` | Quality loops on every content type (same as Worker Swarm) |
| `LlmAgent` with `generate_image` tool | `ImageBriefAgent` — generates visual assets |

---

## What It Connects To

| Input | Source |
|---|---|
| Completed client work | `output/proposals/*.json`, `output/builds/` |
| Site to audit | `index.html`, `style.css` |
| Brand voice | `aura_config.json` (tone, style, target market) |

| Output | Destination |
|---|---|
| Instagram posts | `output/social/instagram/` → manual upload or Buffer API |
| LinkedIn posts | `output/social/linkedin/` → manual upload or LinkedIn API |
| Site fixes | Direct writes to `index.html` / `style.css` (or PR) |
| Blog articles | `output/blog/` → manual publish to Notion/Ghost |

---

## Cost Estimate (per week)

| Task | Runs | Cost |
|---|---|---|
| Site audit | 1/week | ~$0.003 |
| 2× Instagram posts | 2/week | ~$0.008 each |
| 1× LinkedIn post | 1/week | ~$0.005 |
| **Total** | | **~$0.024/week = $1/month** |

---

## Build Priority

| # | Task | When |
|---|---|---|
| 1 | `SiteAuditSwarm` — QA pass on index.html | Now (while at 0 clients, site is main asset) |
| 2 | `InstagramSwarm` — caption + image brief | After first client deliver (have real content) |
| 3 | `LinkedInSwarm` — thought leadership posts | After 2–3 clients (have credibility) |
| 4 | Blog + SEO | Month 2+ |
