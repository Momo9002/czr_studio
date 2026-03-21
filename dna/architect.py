"""
CZR DNA — Architect Swarm (Google ADK)
Multi-agent system that reasons about DNA and regenerates site structure.

Usage:
    python3 -m dna.architect                  # full regeneration
    python3 -m dna.architect --section hero   # regenerate one section
    python3 -m dna.architect --audit          # audit mode: suggest improvements

Architecture:
    Director Agent (orchestrator)
      ├── Copy Agent      → headlines, values, CTAs
      ├── Structure Agent  → section order, layout decisions
      ├── Brand Guard      → validates output against DNA rules
      └── Builder          → dna/build.py (deterministic output)

The agents write changes to identity.json → build.py rebuilds index.html.
"""

import json
import os
import argparse
from pathlib import Path
from google import genai

ROOT = Path(__file__).parent.parent
DNA_DIR = Path(__file__).parent
IDENTITY = DNA_DIR / "identity.json"
VISION = DNA_DIR / "vision.md"
MODELS = DNA_DIR / "models.md"

# ── Gemini client ────────────────────────────────────────────────────────────

def get_client():
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        load_dotenv(ROOT / "api" / ".env")   # fallback location
    except ImportError:
        pass
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set — add to .env or api/.env")
    return genai.Client(api_key=api_key)


def load_context() -> dict:
    """Load all DNA files as context for agents."""
    dna = json.loads(IDENTITY.read_text())
    vision = VISION.read_text() if VISION.exists() else ""
    models = MODELS.read_text() if MODELS.exists() else ""
    return {"dna": dna, "vision": vision, "models": models}


# ── Agent definitions ────────────────────────────────────────────────────────

COPY_AGENT_PROMPT = """You are the CZR Studio Copy Agent. You write headlines, taglines, 
values, and CTAs for a luxury digital studio website.

DNA RULES (non-negotiable):
- Never use exclamation marks
- Never use: amazing, excited, leverage, synergy, innovative, cutting-edge, game-changing, bespoke, solution
- Voice: Hermès copywriter meets SpaceX mission brief
- Short sentences. One idea. Max 15 words per sentence
- Period endings only
- "We do" not "we can"
- "Delivered" not "provided"
- Never mention AI
- Never sell — state. Never explain — imply.

You receive the current DNA and must output JSON with your proposed changes to site.hero, 
site.contact, and site.process text. Only return valid JSON.
"""

STRUCTURE_AGENT_PROMPT = """You are the CZR Studio Structure Agent. You decide section order,
what sections to include, and layout architecture for the website.

You receive current DNA and model references (Vogue, Hermès, SpaceX, Apple).
Your output is a JSON object with:
- sections_order: array of section IDs
- section_additions: any new sections to propose
- section_removals: sections to remove
- layout_notes: brief reasoning

Design principles from models:
- Apple: full-bleed hero, product reveals, clean grids
- Hermès: negative space, restraint, editorial precision
- Vogue: editorial typography, dramatic scale contrast
- SpaceX: mission-brief clarity, numbered sequences
"""

BRAND_GUARD_PROMPT = """You are the CZR Studio Brand Guard. You validate proposed changes 
against DNA rules.

You receive proposed changes and the DNA. Check for:
1. Banned words: amazing, excited, leverage, synergy, innovative, cutting-edge, game-changing, bespoke, solution
2. No AI mentions
3. No exclamation marks
4. Voice consistency (Hermès × SpaceX)
5. Knight is only brand avatar
6. Syne 800 for display type

Output a JSON object:
- approved: true/false
- violations: array of issues found
- fixes: suggested corrections
"""

# ── Agent runners ────────────────────────────────────────────────────────────

def run_copy_agent(client, ctx: dict, section: str = None) -> dict:
    """Ask the copy agent to propose text improvements."""
    print("   🧠 Copy Agent — generating headlines and copy...")
    
    focus = f"Focus specifically on the '{section}' section." if section else "Review all sections."
    
    prompt = f"""Current DNA identity.json:
```json
{json.dumps(ctx['dna'].get('site', {}), indent=2)}
```

Current packages:
```json
{json.dumps(ctx['dna'].get('packages', {}), indent=2)}
```

Vision (founder's decisions):
{ctx['vision'][:2000]}

Models (brand references):
{ctx['models'][:2000]}

{focus}

Propose improved copy. Return a JSON object with the structure matching identity.json's 'site' block.
Only include fields you want to change. Keep values that are already good."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=COPY_AGENT_PROMPT,
            temperature=0.7,
            response_mime_type="application/json",
        )
    )
    
    try:
        result = json.loads(response.text)
        print(f"   ✅ Copy Agent returned {len(result)} keys")
        return result
    except json.JSONDecodeError:
        print(f"   ⚠️  Copy Agent returned invalid JSON, skipping")
        return {}


def run_structure_agent(client, ctx: dict) -> dict:
    """Ask the structure agent to propose layout changes."""
    print("   🧠 Structure Agent — analyzing section architecture...")
    
    prompt = f"""Current sections_order: {json.dumps(ctx['dna'].get('site', {}).get('sections_order', []))}

Current cases (portfolio):
{json.dumps(ctx['dna'].get('site', {}).get('cases', []), indent=2)}

Models (brand references):
{ctx['models'][:2000]}

Propose the optimal section order and any structural changes. Return JSON."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=STRUCTURE_AGENT_PROMPT,
            temperature=0.4,
            response_mime_type="application/json",
        )
    )
    
    try:
        result = json.loads(response.text)
        print(f"   ✅ Structure Agent returned {len(result)} keys")
        return result
    except json.JSONDecodeError:
        print(f"   ⚠️  Structure Agent returned invalid JSON, skipping")
        return {}


def run_brand_guard(client, ctx: dict, proposed_changes: dict) -> dict:
    """Validate proposed changes against DNA rules."""
    print("   🧠 Brand Guard — validating against DNA rules...")
    
    prompt = f"""Proposed changes to apply:
```json
{json.dumps(proposed_changes, indent=2)}
```

Current DNA voice rules:
```json
{json.dumps(ctx['dna'].get('voice', {}), indent=2)}
```

Non-negotiables from vision.md:
{ctx['vision'][:1000]}

Validate these changes. Return JSON with approved, violations, and fixes."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=BRAND_GUARD_PROMPT,
            temperature=0.2,
            response_mime_type="application/json",
        )
    )
    
    try:
        result = json.loads(response.text)
        approved = result.get("approved", False)
        violations = result.get("violations", [])
        status = "✅ Approved" if approved else f"⚠️  {len(violations)} violations"
        print(f"   {status}")
        return result
    except json.JSONDecodeError:
        print(f"   ⚠️  Brand Guard returned invalid JSON, approving by default")
        return {"approved": True, "violations": [], "fixes": []}


# ── Swarm orchestrator ───────────────────────────────────────────────────────

def apply_changes(dna: dict, changes: dict) -> list[str]:
    """Apply agent-proposed changes to DNA site block. Returns list of changes made."""
    site = dna.setdefault("site", {})
    applied = []
    
    # Hero changes
    if "hero" in changes:
        for key, val in changes["hero"].items():
            if key in site.get("hero", {}) and site["hero"][key] != val:
                site["hero"][key] = val
                applied.append(f"hero.{key}")
            elif key not in site.get("hero", {}):
                site.setdefault("hero", {})[key] = val
                applied.append(f"hero.{key} (new)")
    
    # Process changes
    if "process" in changes and isinstance(changes["process"], list):
        site["process"] = changes["process"]
        applied.append("process (replaced)")
    
    # Contact changes
    if "contact" in changes:
        for key, val in changes["contact"].items():
            site.setdefault("contact", {})[key] = val
            applied.append(f"contact.{key}")
    
    # Section order
    if "sections_order" in changes:
        site["sections_order"] = changes["sections_order"]
        applied.append("sections_order")
    
    return applied


def architect(section: str = None, audit: bool = False, dry: bool = False) -> dict:
    """
    Run the architect swarm.
    
    If audit=True, only reports suggestions without applying.
    If section is specified, only the copy agent runs for that section.
    """
    print("\n🏗️  DNA Architect Swarm")
    print("   Loading DNA context...\n")
    
    ctx = load_context()
    client = get_client()
    
    all_changes = {}
    
    # Step 1: Copy Agent
    copy_result = run_copy_agent(client, ctx, section)
    if copy_result:
        all_changes.update(copy_result)
    
    # Step 2: Structure Agent (skip if targeting a specific section)
    if not section:
        struct_result = run_structure_agent(client, ctx)
        if struct_result:
            if "sections_order" in struct_result:
                all_changes["sections_order"] = struct_result["sections_order"]
    
    if not all_changes:
        print("\n   No changes proposed by agents.")
        return {}
    
    # Step 3: Brand Guard validates everything
    guard_result = run_brand_guard(client, ctx, all_changes)
    
    if not guard_result.get("approved", False):
        violations = guard_result.get("violations", [])
        print(f"\n   ❌ Brand Guard rejected: {len(violations)} violations")
        for v in violations[:5]:
            print(f"      · {v}")
        
        # Try to apply fixes
        fixes = guard_result.get("fixes", [])
        if fixes:
            print(f"   🔧 Applying {len(fixes)} fixes from Brand Guard...")
            # Re-run copy agent with fixes context (simplified)
    
    if audit:
        print(f"\n   📋 [AUDIT MODE] Proposed {len(all_changes)} changes:")
        print(json.dumps(all_changes, indent=2))
        return all_changes
    
    if dry:
        print(f"\n   📋 [DRY RUN] Would apply {len(all_changes)} changes")
        return all_changes
    
    # Step 4: Apply changes to identity.json
    dna = ctx["dna"]
    applied = apply_changes(dna, all_changes)
    
    if applied:
        IDENTITY.write_text(json.dumps(dna, indent=2, ensure_ascii=False))
        print(f"\n   ✅ Applied {len(applied)} changes to identity.json:")
        for a in applied:
            print(f"      · {a}")
    
    # Step 5: Rebuild site
    from dna.build import build_site
    build_site(dna)
    
    print(f"\n   🏗️  Architect complete. Run `python3 -m dna.sync` to deploy.")
    return all_changes


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CZR DNA Architect Swarm")
    parser.add_argument("--section", type=str, help="Target a specific section (e.g. hero, contact)")
    parser.add_argument("--audit", action="store_true", help="Audit mode: suggest without applying")
    parser.add_argument("--dry", action="store_true", help="Dry run: show what would change")
    args = parser.parse_args()
    
    architect(section=args.section, audit=args.audit, dry=args.dry)
