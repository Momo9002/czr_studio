---
description: Deploy CZR Studio to production (czr.studio)
---

# CZR Studio — Deploy to Production

## Machine Info

| Key | Value |
|---|---|
| WSL hostname | `BaronHorse` |
| WSL user | `amaur` |
| WSL IP (internal) | `172.22.172.175` (changes on restart) |
| Workspace path | `/home/amaur/.workspaces/aura_web` |

---

## 1. SSH into the WSL Machine from Mac

WSL doesn't expose SSH by default. Two options:

### Option A — Install & start sshd in WSL (one-time setup)

Run this **once** in WSL:

```bash
sudo apt update && sudo apt install -y openssh-server
# Allow your user without password prompt (optional)
echo "PasswordAuthentication yes" | sudo tee -a /etc/ssh/sshd_config
sudo service ssh start
```

Then from your **Mac terminal**:

```bash
# Check WSL IP first (run in WSL):
# ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1

ssh amaur@172.22.172.175
# or if you've set up Windows port-forwarding (see below):
ssh amaur@<windows-machine-ip>
```

### Option B — Windows port-forward (SSH through Windows IP)

Run this in **Windows PowerShell as Administrator** on BaronHorse:

```powershell
# Forward port 2222 on Windows → port 22 in WSL
netsh interface portproxy add v4tov4 listenport=2222 listenaddress=0.0.0.0 connectport=22 connectaddress=172.22.172.175

# Allow firewall
New-NetFirewallRule -DisplayName "WSL SSH" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 2222
```

Then from **Mac**:

```bash
ssh -p 2222 amaur@<windows-machine-public-ip>
```

---

## 2. Deploy Frontend — Cloudflare Pages (Direct Upload)

The site is pure static HTML — no build step.

### Files to upload

From `/home/amaur/.workspaces/aura_web/`, upload **only**:

```
index.html
style.css
script.js
cases/
images/
```

### What to exclude

```
.agent/       ← private AI config
api/          ← backend, runs separately
.env          ← secrets, never upload
cloudflared.exe
aura_api.log
leads.db
start_aura.*
requirements.txt
```

### Upload steps

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages** → **Create** → **Pages** → **Direct Upload**
2. Name the project `czr-studio`
3. Drag the files/folders listed above into the upload zone
4. Click **Deploy site**
5. Go to **Custom domains** → Add `czr.studio`

> If `czr.studio` is already on Cloudflare DNS, the domain connection is instant.

---

## 3. Deploy Backend API (Optional — for future lead capture)

The `api/` folder is a FastAPI app. For now, the lead form goes direct to WhatsApp (no API needed at launch).

When ready, deploy the API to **Railway**:

```bash
# From Mac, after SSH into WSL:
cd /home/amaur/.workspaces/aura_web/api
# Push to GitHub, then connect repo to railway.app
```

Or keep using the **Cloudflare tunnel** for local dev:

```bash
./cloudflared.exe tunnel --url http://localhost:8000
```

---

## 4. Pre-Deploy Checklist

- [ ] `style.css?v=4` — version already bumped ✓
- [ ] WhatsApp number: `+971551343144` (personal, switch to Telnyx `+18107764057` when ready)
- [ ] OG image `images/og_image.png` — still shows old Aura branding, regenerate for CZR
- [ ] All 6 case study pages (`/cases/*/`) load correctly
- [ ] Lead form → WhatsApp redirect works end-to-end
- [ ] Check site on mobile (hero canvas, marquee, form)

---

## 5. Post-Deploy

```bash
# Purge Cloudflare cache after updates:
# dash.cloudflare.com → czr.studio → Caching → Purge Everything
```

Update DNS CNAME if needed:
```
CNAME  czr.studio  →  czr-studio.pages.dev
```
