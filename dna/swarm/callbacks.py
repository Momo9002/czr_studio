"""
dna/swarm/callbacks.py — ADK callbacks for the Website Builder Swarm.

Provides:
  - dna_inject_callback: before_agent_callback that injects DNA context into session
  - make_quality_scorer: after_agent_callback factory that logs quality scores

Compatible with ADK v1.27.x callback signature requirements.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.genai import types

_DNA_DIR = Path(__file__).parent.parent
_IDENTITY = _DNA_DIR / "identity.json"


def dna_inject_callback(
    callback_context: CallbackContext,
    **kwargs,
) -> Optional[types.Content]:
    """before_agent_callback: Inject DNA context + voice rules into session state.

    Called before each agent runs. Ensures every agent has fresh DNA context
    without needing to read the file itself. Brand-agnostic — reads from
    identity.json via the tool layer, but pre-populates state for convenience.
    """
    state = callback_context.state

    # Only load once per session (or if stale)
    if state.get("dna_loaded"):
        return None

    try:
        dna = json.loads(_IDENTITY.read_text())
        brand = dna.get("brand", {})
        voice = dna.get("voice", {})

        state["dna_loaded"] = True
        state["brand_name"] = brand.get("name", "Studio")
        state["brand_tagline"] = brand.get("tagline", "")
        state["brand_url"] = brand.get("site", "")
        state["voice_rules"] = json.dumps({
            "never_words": voice.get("never", []),
            "always_words": voice.get("always", []),
            "tone": voice.get("tone", ""),
            "register": voice.get("register", ""),
        }, ensure_ascii=False)
        state["dna_context"] = json.dumps({
            "brand": brand,
            "voice": voice,
            "colors": dna.get("colors", {}),
            "typography": dna.get("typography", {}),
            "packages": dna.get("packages", {}),
        }, ensure_ascii=False)

    except Exception as e:
        state["dna_load_error"] = str(e)

    return None


def make_quality_scorer(agent_role: str = "builder"):
    """Factory: returns an after_agent_callback that reads and persists quality scores.

    Args:
        agent_role: Role label for logging (e.g. 'copy', 'structure', 'brand_guard').

    Returns:
        A callable compatible with ADK's after_agent_callback signature.
    """
    def quality_scorer_callback(
        callback_context: CallbackContext,
        **kwargs,
    ) -> Optional[types.Content]:
        state = callback_context.state
        agent_name = callback_context.agent_name

        # Read quality score set by the agent (0.0–1.0)
        score = None
        for key in ("quality_score", f"{agent_role}_quality", "score"):
            val = state.get(key)
            if isinstance(val, (int, float)):
                score = float(val)
                break

        # Track run history in session state
        history = state.setdefault("quality_history", [])
        history.append({
            "agent": agent_name,
            "role": agent_role,
            "score": score,
        })

        # If below threshold, signal for revision
        if score is not None and score < 0.7:
            state["needs_revision"] = True
            state["revision_reason"] = f"{agent_name} scored {score:.2f} (below 0.7 threshold)"
        else:
            state["needs_revision"] = False

        return None

    quality_scorer_callback.__name__ = f"quality_scorer_{agent_role}"
    return quality_scorer_callback
