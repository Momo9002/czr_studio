"""
dna/swarm/agent_builder/tools.py — Tools for the Agent Builder Swarm.

Reads DNA files and writes compiled agent phase prompts to dna/prompts/.
Mirrors the pattern of dna/swarm/builder/tools.py (website builder).
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from datetime import datetime

_DNA_DIR = Path(__file__).parent.parent.parent        # dna/
_PROMPTS_DIR = _DNA_DIR / "prompts"
_CONTRACTS_DIR = _DNA_DIR / "contracts"
_PROJECT_ROOT = _DNA_DIR.parent


# ── DNA Readers ──────────────────────────────────────────────────────────────

def read_full_dna() -> dict:
    """Read the full identity.json — brand, voice, packages, sales, FAQ, cases."""
    return json.loads((_DNA_DIR / "identity.json").read_text())


def read_dna_section(section: str) -> dict | str:
    """Read a specific section from identity.json (brand, voice, packages, sales, site, faq)."""
    dna = json.loads((_DNA_DIR / "identity.json").read_text())
    return dna.get(section, {})


def read_voice_rules() -> str:
    """Read voice.md — full brand voice rules, banned words, tone guidelines."""
    f = _DNA_DIR / "voice.md"
    return f.read_text() if f.exists() else "No voice.md found."


def read_agents_contract() -> str:
    """Read contracts/agents.md — the agent behavior contract (what it must/must never do)."""
    f = _CONTRACTS_DIR / "agents.md"
    return f.read_text() if f.exists() else "No agents contract found."


def read_phase_prompt(phase: str) -> str:
    """Read the current compiled prompt for a phase (sales, briefing, production, delivery)."""
    f = _PROMPTS_DIR / f"{phase}.md"
    if not f.exists():
        return f"No prompt found for phase: {phase}"
    return f.read_text()


def read_all_phase_prompts() -> dict:
    """Read all 4 currently compiled phase prompts. Returns dict of phase → prompt text."""
    result = {}
    for phase in ["sales", "briefing", "production", "delivery"]:
        f = _PROMPTS_DIR / f"{phase}.md"
        result[phase] = f.read_text() if f.exists() else ""
    return result


# ── Prompt Writers ───────────────────────────────────────────────────────────

def write_phase_prompt(phase: str, prompt: str) -> dict:
    """Write a compiled agent system prompt for a phase to dna/prompts/{phase}.md.
    
    phase: one of sales, briefing, production, delivery
    prompt: the full system prompt text
    """
    valid = ["sales", "briefing", "production", "delivery"]
    if phase not in valid:
        return {"error": f"Invalid phase '{phase}'. Must be one of: {valid}"}
    
    _PROMPTS_DIR.mkdir(exist_ok=True)
    out = _PROMPTS_DIR / f"{phase}.md"
    out.write_text(prompt)
    return {
        "written": str(out),
        "phase": phase,
        "chars": len(prompt),
        "tokens_est": len(prompt) // 4,
    }


def write_manifest(phases_built: str = "sales,briefing,production,delivery", compiled_by: str = "agent_builder_swarm") -> dict:
    """Write manifest.json. phases_built is a comma-separated list of phase names."""
    _PROMPTS_DIR.mkdir(exist_ok=True)
    phases_list = [p.strip() for p in phases_built.split(",")]
    manifest = {
        "compiled_at": datetime.now().isoformat()[:19],
        "compiled_by": compiled_by,
        "model": "gemini-2.5-flash",
        "phases": {
            "sales":      {"tools": 10, "phase": "onboarding"},
            "briefing":   {"tools": 12, "phase": "briefing"},
            "production": {"tools": 12, "phase": "in_progress/revision"},
            "delivery":   {"tools": 12, "phase": "review/delivered"},
        },
        "built": phases_list,
    }
    (_PROMPTS_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return {"manifest_written": True, "phases": phases_list}


# ── Validation ───────────────────────────────────────────────────────────────

def validate_prompt_against_voice(phase: str, prompt: str) -> dict:
    """Check a prompt against voice.md rules. Returns score 0-10 and violations list."""
    dna = json.loads((_DNA_DIR / "identity.json").read_text())
    voice = dna.get("voice", {})
    never_words = voice.get("never", [])
    
    violations = []
    score = 10
    
    # Check banned words
    prompt_lower = prompt.lower()
    for word in never_words:
        if word.lower() in prompt_lower:
            violations.append(f"Banned word in prompt: '{word}'")
            score -= 1
    
    # Check prompt length (too short = not enough guidance)
    if len(prompt) < 500:
        violations.append(f"Prompt too short ({len(prompt)} chars) — agents need detailed instructions")
        score -= 2
    
    # Check for required elements
    required = ["client_token", "phase", "tool"]
    for req in required:
        if req not in prompt_lower:
            violations.append(f"Missing reference to '{req}' — agents need this context")
            score -= 1
    
    return {
        "phase": phase,
        "score": max(0, score),
        "violations": violations,
        "pass": score >= 7,
        "chars": len(prompt),
    }
