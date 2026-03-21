"""
CZR DNA — Agent Prompt Builder
Compiles a system prompt for the CZR concierge agent from DNA.

Every time DNA changes (new package price, new tagline, new voice rule),
run sync → agent_prompt.txt updates → agent uses current DNA.

Outputs:
  dna/agent_prompt.txt  — system prompt for the CZR concierge agent
  dna/agent_prompt.json — structured version for API integrations

Usage:
    python3 -m dna.agent_builder
    python3 -m dna.agent_builder --dry
    python3 -m dna.agent_builder --stdout
"""

import json
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent
DNA_DIR = Path(__file__).parent
IDENTITY = DNA_DIR / "identity.json"
VOICE = DNA_DIR / "voice.md"
AGENTS_CONTRACT = DNA_DIR / "contracts" / "agents.md"


def load() -> dict:
    return json.loads(IDENTITY.read_text())


def _wa_url(dna: dict) -> str:
    phone = dna["brand"]["whatsapp"].replace("+", "").replace(" ", "")
    return f"https://wa.me/{phone}"


def build_agent_prompt(dna: dict = None, dry: bool = False) -> str:
    """
    Compile the CZR concierge agent system prompt from DNA.
    Returns the prompt string.
    """
    if dna is None:
        dna = load()

    brand = dna["brand"]
    packages = dna["packages"]
    voice = dna.get("voice", {})
    site = dna.get("site", {})
    hero = site.get("hero", {})
    values = hero.get("values", [])
    process = site.get("process", [])
    faqs = dna.get("faq", [])

    # Build FAQ block
    faq_block = "\n".join(
        f"Q: {f['q']}\nA: {f['a']}" for f in faqs[:8]
    )

    # Build process block
    process_block = "\n".join(
        f"{s['num']}. {s['title']} — {s['text']}" for s in process
    )

    # Build package block
    pkg_lines = []
    for key in ["sprint", "flagship", "retainer"]:
        pkg = packages.get(key, {})
        pkg_lines.append(
            f"  - {pkg.get('name','')}: €{pkg.get('price','')} — {pkg.get('tagline','')}"
        )
    packages_block = "\n".join(pkg_lines)

    # Voice rules from DNA
    banned = ", ".join(voice.get("banned_words", [])[:12])
    tone_rules = "\n".join(f"- {r}" for r in voice.get("rules", [
        "Never use exclamation marks",
        "Never apologize for the process",
        "Answer what was asked — nothing more",
        "Short sentences. One idea per sentence.",
        "Never sell — state. Never explain — imply.",
    ]))

    prompt = f"""You are the CZR Studio concierge agent.

# Identity
Name: {brand['name']}
Tagline: {brand['tagline']}
Site: {brand['site']}
WhatsApp: {brand['whatsapp']}
Type: Digital atelier. Not an agency. Not a freelancer.

# Brand values
{chr(10).join(f'- {v}' for v in values)}

# Your role
You handle the initial client brief. You ask three questions:
1. What is the project? (website, landing page, portfolio, e-commerce)
2. Who is it for? (brand, audience, market)
3. What are three visual references? (sites, brands, aesthetics they admire)

After the brief, you confirm the package and next steps.

# Process
{process_block}

# Packages
{packages_block}

# Tone rules (non-negotiable)
{tone_rules}

# Banned words
{banned}

# Never do
- Never use exclamation marks
- Never say "no problem", "of course", "absolutely", "sure", "with pleasure"
- Never apologize for timelines — the speed is a feature, not a risk
- Never use AI, automation, or technology as selling points
- Never ask more than two questions at once

# Always do
- Respond within one hour (during business hours)
- Confirm the package clearly before any payment
- State the price once, clearly, without hedging
- Refer to the studio as "we" — never "I" or "the team"

# Frequently asked questions
{faq_block}

# Contact fallback
If a question is beyond your brief scope, direct the client to: {brand['site']}
"""

    # Structured JSON version for API use
    agent_data = {
        "system_prompt": prompt,
        "brand": {
            "name": brand["name"],
            "tagline": brand["tagline"],
            "whatsapp": brand["whatsapp"],
            "site": brand["site"],
        },
        "packages": {
            k: {"name": v.get("name"), "price": v.get("price"), "tagline": v.get("tagline")}
            for k, v in packages.items()
        },
        "voice_rules": voice.get("rules", []),
        "banned_words": voice.get("banned_words", []),
    }

    if not dry:
        (DNA_DIR / "agent_prompt.txt").write_text(prompt)
        (DNA_DIR / "agent_prompt.json").write_text(json.dumps(agent_data, indent=2, ensure_ascii=False))
        print(f"   ✅ Built dna/agent_prompt.txt ({len(prompt):,} chars)")
        print(f"   ✅ Built dna/agent_prompt.json")
    else:
        print(f"   ✅ [DRY] Would build agent_prompt.txt ({len(prompt):,} chars)")

    return prompt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CZR DNA Agent Builder")
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("--stdout", action="store_true", help="Print prompt to stdout")
    args = parser.parse_args()

    prompt = build_agent_prompt(dry=args.dry)
    if args.stdout:
        print(prompt)
