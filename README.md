# CZR Studio

Premium web studio — *Haute Couture Digital.*

**Site:** [czr.studio](https://czr.studio) · **WhatsApp:** +18107764057

---

## Project Structure

```
czr_studio/
├── index.html              # Main site
├── onboarding.html         # Client onboarding form
├── client.html             # Client portal (status, messages, revisions)
├── concierge.html          # AI concierge chat
├── dashboard.html          # Internal command center
├── api/                    # FastAPI server
│   ├── main.py             # Routes + startup
│   ├── projects.py         # Project DB layer
│   ├── leads.py            # Lead pipeline DB
│   ├── stripe_webhook.py   # Payment handling
│   ├── whatsapp.py         # Inbound WhatsApp
│   ├── whatsapp_send.py    # Outbound WhatsApp
│   ├── email_notify.py     # Email notifications
│   └── .env.example        # Environment variables template
├── agents/                 # AI agent system
│   ├── lifecycle.py        # CZR Concierge — core engine
│   ├── knowledge.py        # Brand knowledge base
│   ├── phases/             # Phase-specific agents
│   └── tools/              # Agent function tools
├── dna/                    # Brand DNA (identity, voice, visual)
├── cases/                  # Portfolio case studies
└── brand/                  # Brand assets + guidelines
```

## Quick Start

```bash
# 1. Copy and fill in your API keys
cp api/.env.example api/.env

# 2. Start everything (API + Cloudflare Tunnel)
./start_czr.sh
```

## Client Pipeline

1. **Lead arrives** (WhatsApp / onboarding form)
2. **Concierge qualifies** (AI sales agent, powered by DNA)
3. **Payment** (Stripe checkout → auto-advances phase)
4. **Briefing** (concierge confirms scope + collects assets)
5. **Production** (status updates, revision capture)
6. **Delivery** (site review, approval, testimonial)

## Key URLs

| URL | Purpose |
|---|---|
| `czr.studio` | Main website (Vercel) |
| `api.czr.studio` | API server (Cloudflare Tunnel) |
| `czr.studio/onboarding` | Client onboarding form |
| `czr.studio/client?token=xxx` | Client portal |
| `czr.studio/concierge?token=xxx` | AI concierge chat |
| `czr.studio/dashboard` | Internal command center |
