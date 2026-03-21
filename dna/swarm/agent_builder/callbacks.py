"""
dna/swarm/agent_builder/callbacks.py — ADK callbacks for the Agent Builder Swarm.

Same pattern as dna/swarm/builder/callbacks.py but injects agent-specific DNA context
(voice rules, sales config, contracts) rather than visual/design context.
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
    """before_agent_callback: Inject DNA context into session state before each agent runs."""
    state = callback_context.state

    if state.get("agent_dna_loaded"):
        return None

    try:
        dna = json.loads((_DNA_DIR / "identity.json").read_text())
        brand = dna.get("brand", {})
        voice = dna.get("voice", {})
        sales = dna.get("sales", {})

        state["agent_dna_loaded"] = True
        state["brand_name"] = brand.get("name", "Studio")
        state["brand_tagline"] = brand.get("tagline", "")
        state["avatar_name"] = brand.get("avatar_name", "")
        state["delivery_hours"] = brand.get("delivery_hours", 48)
        state["voice_tone"] = voice.get("tone", "")
        state["voice_never"] = json.dumps(voice.get("never", []))
        state["sales_approach"] = sales.get("approach", "consultative")
        state["sales_aggressiveness"] = sales.get("aggressiveness", 3)

        # Load voice.md if exists
        voice_file = _DNA_DIR / "voice.md"
        if voice_file.exists():
            state["voice_md"] = voice_file.read_text()[:2000]  # first 2k chars

        # Load agents contract if exists
        contract_file = _DNA_DIR / "contracts" / "agents.md"
        if contract_file.exists():
            state["agents_contract"] = contract_file.read_text()[:2000]

    except Exception as e:
        print(f"[dna_inject_callback] Warning: {e}")

    return None


def make_quality_scorer(agent_name: str):
    """after_agent_callback factory: logs quality score to session state."""
    def _scorer(callback_context: CallbackContext, **kwargs) -> Optional[types.Content]:
        state = callback_context.state
        score = state.get("quality_score", None)
        log = state.get("quality_log", [])
        if not isinstance(log, list):
            log = []
        log.append({
            "agent": agent_name,
            "score": score,
        })
        state["quality_log"] = log
        return None
    return _scorer
