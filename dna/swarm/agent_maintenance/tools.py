"""
dna/swarm/agent_maintenance/tools.py — Tools for the Agent Maintenance Swarm.

Reads real conversation logs from the DB, scores agent performance,
and provides tools to rewrite prompts when quality drops.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

_DNA_DIR = Path(__file__).parent.parent.parent
_PROMPTS_DIR = _DNA_DIR / "prompts"
_PROJECT_ROOT = _DNA_DIR.parent
_DB_PATH = _PROJECT_ROOT / "api" / "czr_studio.db"


# ── Conversation Log Readers ─────────────────────────────────────────────────

def get_recent_conversations(days: int = 7, limit: int = 50) -> list:
    """Get recent agent conversations from the DB. Returns list of {phone, phase, messages}."""
    if not _DB_PATH.exists():
        return [{"error": "DB not found"}]
    
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    # Get recent projects with their messages
    projects = conn.execute(
        "SELECT client_token, client_name, phone, phase FROM projects "
        "WHERE created_at > ? ORDER BY created_at DESC LIMIT ?",
        (cutoff, limit)
    ).fetchall()
    
    conversations = []
    for p in projects:
        msgs = conn.execute(
            "SELECT role, content, created_at FROM messages "
            "WHERE client_token = ? ORDER BY created_at ASC LIMIT 30",
            (p["client_token"],)
        ).fetchall()
        
        conversations.append({
            "client": p["client_name"] or p["phone"] or "unknown",
            "phase": p["phase"],
            "message_count": len(msgs),
            "messages": [{"role": m["role"], "text": m["content"][:200]} for m in msgs],
        })
    
    conn.close()
    return conversations


def get_conversion_stats() -> dict:
    """Get conversion stats: how many leads → briefing → production → delivery."""
    if not _DB_PATH.exists():
        return {"error": "DB not found"}
    
    conn = sqlite3.connect(str(_DB_PATH))
    
    phases = {}
    for row in conn.execute("SELECT phase, COUNT(*) as cnt FROM projects GROUP BY phase"):
        phases[row[0]] = row[1]
    
    total = sum(phases.values())
    paid = conn.execute("SELECT COUNT(*) FROM projects WHERE paid = 1").fetchone()[0]
    
    conn.close()
    return {
        "total_projects": total,
        "by_phase": phases,
        "paid": paid,
        "conversion_rate": f"{(paid / total * 100):.1f}%" if total > 0 else "0%",
    }


def get_phase_prompt(phase: str) -> str:
    """Read the current compiled prompt for a phase."""
    f = _PROMPTS_DIR / f"{phase}.md"
    return f.read_text() if f.exists() else f"No prompt for {phase}"


def get_voice_rules() -> str:
    """Read voice.md — the brand voice rules."""
    f = _DNA_DIR / "voice.md"
    return f.read_text() if f.exists() else "No voice.md"


def get_agents_contract() -> str:
    """Read the agents behavior contract."""
    f = _DNA_DIR / "contracts" / "agents.md"
    return f.read_text() if f.exists() else "No contract"


def write_phase_prompt(phase: str, prompt: str) -> dict:
    """Overwrite a phase prompt with an improved version."""
    valid = ["sales", "briefing", "production", "delivery"]
    if phase not in valid:
        return {"error": f"Invalid phase. Must be one of: {valid}"}
    _PROMPTS_DIR.mkdir(exist_ok=True)
    out = _PROMPTS_DIR / f"{phase}.md"
    
    # Backup the old version
    backup = _PROMPTS_DIR / f"{phase}.md.bak"
    if out.exists():
        backup.write_text(out.read_text())
    
    out.write_text(prompt)
    return {"written": phase, "chars": len(prompt), "backup": str(backup)}


def write_maintenance_report(report: str) -> dict:
    """Write maintenance audit report to dna/prompts/maintenance_report.md."""
    out = _PROMPTS_DIR / "maintenance_report.md"
    out.write_text(f"# Agent Maintenance Report\n\n_Generated: {datetime.now().isoformat()[:19]}_\n\n{report}")
    return {"written": str(out)}
