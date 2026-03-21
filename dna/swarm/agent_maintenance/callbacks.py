"""
dna/swarm/agent_maintenance/callbacks.py — ADK callbacks for Agent Maintenance Swarm.
Reuses the same pattern as agent_builder/callbacks.py.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.genai import types

_DNA_DIR = Path(__file__).parent.parent.parent


def dna_inject_callback(
    callback_context: CallbackContext,
    **kwargs,
) -> Optional[types.Content]:
    """Inject DNA context before each maintenance agent runs."""
    state = callback_context.state
    if state.get("maint_dna_loaded"):
        return None

    try:
        dna = json.loads((_DNA_DIR / "identity.json").read_text())
        brand = dna.get("brand", {})
        voice = dna.get("voice", {})

        state["maint_dna_loaded"] = True
        state["brand_name"] = brand.get("name", "Studio")
        state["voice_tone"] = voice.get("tone", "")
        state["voice_never"] = json.dumps(voice.get("never", []))
    except Exception as e:
        print(f"[maint_dna_inject] Warning: {e}")
    return None


def make_quality_scorer(agent_name: str):
    """Log quality score to session state."""
    def _scorer(callback_context: CallbackContext, **kwargs) -> Optional[types.Content]:
        state = callback_context.state
        score = state.get("quality_score", None)
        log = state.get("quality_log", [])
        if not isinstance(log, list):
            log = []
        log.append({"agent": agent_name, "score": score})
        state["quality_log"] = log
        return None
    return _scorer
