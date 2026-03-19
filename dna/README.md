# CZR Studio DNA

> The single source of truth for everything CZR does.

Every process in CZR Studio links to this folder. Change the DNA here — all processes update.

---

## Files

| File | Format | Used by |
|---|---|---|
| `identity.json` | JSON | Agents, campaign scripts, any Python process |
| `visual.md` | Markdown | Website CSS, portfolio pages, image generation |
| `voice.md` | Markdown | Agents, Instagram captions, ad copy |
| `content.md` | Markdown | Instagram scheduling, Reels, campaign content |
| `contracts/campaign.md` | Markdown | Campaign scripts, ad creation |
| `contracts/portfolio.md` | Markdown | Case study pages, client delivery |
| `contracts/agents.md` | Markdown | Concierge, briefing, delivery agents |
| `contracts/production.md` | Markdown | Every client website delivered by CZR |

---

## How to Import in Python

```python
import json
from pathlib import Path

DNA = json.loads((Path(__file__).parent.parent / 'dna' / 'identity.json').read_text())

brand_name = DNA['brand']['name']           # "CZR Studio"
voice_cta  = DNA['voice']['cta']            # "→ czr.studio"
colors     = DNA['colors']                  # {"black": "#000000", ...}
hashtags   = ' '.join(DNA['hashtags'])      # "#CZRStudio #HauteCoutureDigital ..."
```

---

## DNA Update Protocol

1. Edit the relevant DNA file
2. Commit with: `git commit -m "dna: [what changed]"`
3. Any process that reads DNA will automatically use the new values
4. Test agents + campaign scripts to verify
