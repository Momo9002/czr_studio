# Aura Web Studio — Agent Context

> Load this at the start of any Antigravity session on this workspace.

## What This Is

**CZR Studio** — AI-powered premium web agency. Websites delivered in 48h.
Business goal: €500/week → €2,000+/month. Currently at 0 clients.
Instagram: [@czr.studio](https://instagram.com/czr.studio)

## Site Stack

| Layer | Tech |
|---|---|
| Frontend | Vanilla HTML + CSS + JS (no build step) |
| Fonts | Syne (display) + Manrope (body) via Google Fonts |
| Hosting | TBD (Netlify or Cloudflare Pages recommended) |
| Leads | WhatsApp (`+971551343144`) via form → `wa.me` redirect |
| Portfolio | 6 fictional case studies in `/cases/` with real generated images |

## File Map

```
aura_web/
├── index.html          ← Main site (one-page)
├── style.css           ← Design system v4 — B&W + color rays, Syne+Manrope
├── script.js           ← Empty (all JS is inline in index.html)
├── cases/              ← 6 standalone case study pages
├── images/             ← 33 AI-generated portfolio images + OG image
└── .agent/             ← Agent context + knowledge
    ├── context.md      ← This file
    ├── knowledge/
    │   ├── adk_swarm_patterns.md     ← How ADK swarms work (primitives, patterns, costs)
    │   └── marketing_swarm_design.md ← Marketing Swarm: Instagram, LinkedIn, site QA
    └── workflows/
        ├── dev.md
        ├── deploy.md
        └── new-case.md
```

## Design System (v4 — B&W Edition)

- **BG**: `#000000` — pure black
- **Surface**: `#0A0A0A` / `#111` / `#1A1A1A`
- **Accent**: `#FFFFFF` — white for buttons/focus
- **Color rays**: `--m-red: #C8242A`, `--m-yellow: #F0C029`, `--m-blue: #1A4BA8` — used as hero rays and Mondrian portfolio tile colors
- **Hero**: animated canvas with color rays (red/yellow/blue) rotating slowly on pure black
- **Fonts**: Syne 800 (headlines) + Manrope 300–700 (body)
- **Splash**: CZR. logo with rotating conic-gradient color leak behind it

## WhatsApp Number

Currently: `+971551343144` (Amaury's personal number)
Location in code: `index.html` inline JS — `const WA = '971551343144';`

## Known Gaps

- [ ] No real hosting yet — needs Netlify/Cloudflare deploy
- [ ] 0 real clients — all testimonials and stats are fictional
- [ ] Case study pages (`/cases/*.html`) may need full visual rework beyond footer credit update
- [ ] `script.js` is empty — all JS is inline in `index.html`
- [ ] OG image (`images/og_image.png`) still shows Aura branding — needs regeneration for CZR

## Antigravity Conversations

| Topic | Conv ID |
|---|---|
| Aura Web Studio planning | `b0689e47-fa85-45a8-9419-612a83984620` |
| Marketing plan | `06a4fbc9-85b0-49f1-8fe0-dfe34f51df3b` |
| Cold outreach strategy + v2 redesign | `95a6d848-97f9-4729-87d6-cda8b2b05eeb` |
| CZR Studio rebrand (v4) | `7201cbe2-1e43-4dfa-bd27-c47e706747db` |
