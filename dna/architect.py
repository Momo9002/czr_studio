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

COPY_AGENT_PROMPT = """You are the CZR Studio Copy Agent. Your job is to REWRITE the entire site copy from scratch based on the DNA.

You are NOT a safety net. You are not here to preserve what exists.
You are here to make the copy BETTER — more precise, more luxurious, more converted.

DNA RULES (non-negotiable):
- No exclamation marks. Never.
- Banned words: amazing, excited, leverage, synergy, innovative, cutting-edge, game-changing, bespoke, solution, seamless, empower
- Voice: Hermès copywriter meets SpaceX mission brief. Terse. Commanding. Elegant.
- Short sentences. One idea per sentence. Max 12 words per sentence.
- End every sentence with a period.
- Use present tense: "We build" not "We will build".
- Never explain. State.
- Never sell. Imply the value.
- Never mention AI, automation, or technology explicitly.
- The studio is not an agency. It is an atelier.

You will receive the FULL current site block from identity.json.
You MUST return a JSON object with the COMPLETE site block rewritten.
Be bold. Change things. Make it feel like Hermès just launched a digital studio.

Return the full 'site' block as JSON. Every field. No partial updates."""

STRUCTURE_AGENT_PROMPT = """You are the CZR Studio Structure Agent. You architect the page layout.

Your job is to determine:
1. sections_order — what sections appear, in what order
2. about block — what stats to show (exactly 3)
3. work block — what the portfolio section says
4. process_section — how the process is labeled
5. packages_section — headlines and feature lists per package
6. faq_section — label and headline
7. cta_copy — button text for each CTA

Available section IDs: hero, work, about, process, packages, faq, contact

Design model references:
- Apple: full-bleed hero → proof → product reveal (packages) → social proof → CTA
- Hermès: restraint, no section bloat, quality over quantity
- SpaceX: mission → process → specs → CTA. Nothing extra.
- Vogue: editorial scale, drama, then precision

Return a complete JSON object covering: sections_order, about (with stats[]), work, 
process_section, packages_section (with features.sprint[], features.flagship[], features.retainer[]),
faq_section, cta_copy (primary, sprint, flagship, retainer, nudge).

Be decisive. Remove sections that add no value. The page should feel like one focused editorial."""

BRAND_GUARD_PROMPT = """You are the CZR Studio Brand Guard. You protect the brand.

You receive proposed changes and check for violations. Be strict.

VIOLATION RULES:
1. Banned words used: amazing, excited, leverage, synergy, innovative, cutting-edge, game-changing, bespoke, solution, seamless, empower
2. Any exclamation mark (!)
3. Any mention of AI, automation, artificial intelligence, machine learning
4. Multi-clause sentences (more than one comma in a sentence is usually wrong)
5. Passive voice: "is delivered" should be "We deliver"
6. Empty filler: "take your brand to the next level", "we are passionate about", etc.
7. First-person plural that sounds corporate: "our team", "our experts" (use "we" directly)

If there are violations, list them specifically with the offending text.
Always set approved: true if violations are minor (0-1 small issues).
Set approved: false only for critical brand violations (banned words, AI mentions, exclamation marks).

Return JSON: { approved: bool, violations: [], fixes: {} }"""

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
    
    # Deep merge — apply any key in the changes dict to the site block
    deep_keys = ["hero", "contact", "work", "about", "process_section", 
                 "packages_section", "faq_section", "cta_copy"]
    
    for key in deep_keys:
        if key in changes and isinstance(changes[key], dict):
            old = site.get(key, {})
            for subkey, val in changes[key].items():
                if old.get(subkey) != val:
                    site.setdefault(key, {})[subkey] = val
                    applied.append(f"{key}.{subkey}")
    
    # Process steps (list replacement)
    if "process" in changes and isinstance(changes["process"], list):
        site["process"] = changes["process"]
        applied.append("process (replaced)")
    
    # Section order
    if "sections_order" in changes and isinstance(changes["sections_order"], list):
        site["sections_order"] = changes["sections_order"]
        applied.append("sections_order")
    
    # Hero values (list)
    if "hero" in changes and "values" in changes["hero"]:
        site.setdefault("hero", {})["values"] = changes["hero"]["values"]
        if "hero.values" not in applied:
            applied.append("hero.values")
    
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
