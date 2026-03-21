"""
dna/swarm/server.py — Website Builder Swarm FastAPI Server
Runs the ADK swarm with Google Cloud sessions and semantic memory.

Usage:
    uvicorn dna.swarm.server:app --port 8902 --reload

Trigger via Momo or any HTTP client:
    POST http://localhost:8902/run
    {
      "task": "Full rebuild from DNA",
      "user_id": "amaury",
      "session_id": "czr-2026-03-21",   // optional — creates new if omitted
      "credentials": {
        "GOOGLE_API_KEY": "...",         // required
        "GOOGLE_CLOUD_PROJECT": "...",   // required for Vertex sessions
        "GOOGLE_CLOUD_LOCATION": "us-central1"  // optional
      }
    }
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.genai.types import Content, Part

# ── ADK imports ───────────────────────────────────────────────────────────────
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# ── Local imports ─────────────────────────────────────────────────────────────
from dna.swarm.orchestrator import build_root_agent

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Website Builder Swarm",
    description="Google ADK swarm: DNA (identity.json) → premium website (HTML)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response schemas ──────────────────────────────────────────────────

class BuildRequest(BaseModel):
    task: str = "Full rebuild from DNA"
    user_id: str = "default"
    session_id: Optional[str] = None
    credentials: Optional[dict] = None


class BuildResponse(BaseModel):
    session_id: str
    result: str
    quality_history: list
    build_result: Optional[str] = None
    brand_guard_result: Optional[str] = None
    site_structure: Optional[str] = None


# ── Runner factory ────────────────────────────────────────────────────────────

def _make_runner(credentials: dict | None = None) -> tuple[Runner, object]:
    """Create an ADK Runner with the best available session service.

    Priority:
    1. VertexAiSessionService if GOOGLE_CLOUD_PROJECT is available (cloud sessions)
    2. InMemorySessionService as fallback (dev mode, no persistence)

    Returns:
        (runner, session_service) tuple
    """
    # Inject credentials into environment if provided
    if credentials:
        for key, val in credentials.items():
            if val:
                os.environ[key] = val

    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "momo-agent-489822")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    # Try Vertex AI session service first (persistent cloud sessions)
    session_service = None
    memory_service = None

    try:
        from google.adk.sessions import VertexAiSessionService
        from google.adk.memory import VertexAiMemoryBankService

        session_service = VertexAiSessionService(
            project=project,
            location=location,
        )
        memory_service = VertexAiMemoryBankService(
            project=project,
            location=location,
        )
        print(f"   ✅ Using Vertex AI session service (project: {project})")

    except Exception as e:
        print(f"   ⚠️  Vertex AI session service unavailable ({e}), using InMemory")
        session_service = InMemorySessionService()

    agent = build_root_agent()

    runner_kwargs = dict(
        agent=agent,
        app_name="website_builder_swarm",
        session_service=session_service,
    )
    if memory_service:
        runner_kwargs["memory_service"] = memory_service

    runner = Runner(**runner_kwargs)
    return runner, session_service


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "swarm": "website_builder", "version": "1.0.0"}


# ── Main run endpoint ─────────────────────────────────────────────────────────

@app.post("/run", response_model=BuildResponse)
async def run_swarm(req: BuildRequest):
    """Run the website builder swarm.

    Accepts a task description and triggers the full DNA → website pipeline.
    Returns the build result, quality history, and agent outputs.
    """
    session_id = req.session_id or str(uuid.uuid4())

    try:
        runner, session_service = _make_runner(req.credentials)

        # Create or retrieve session
        try:
            session = await session_service.create_session(
                app_name="website_builder_swarm",
                user_id=req.user_id,
                session_id=session_id,
                state={"input": req.task},
            )
        except Exception:
            # Session may already exist — fetch it
            session = await session_service.get_session(
                app_name="website_builder_swarm",
                user_id=req.user_id,
                session_id=session_id,
            )
            if session:
                session.state["input"] = req.task

        # Run the swarm
        final_response = ""
        message = Content(role="user", parts=[Part(text=req.task)])

        async for event in runner.run_async(
            user_id=req.user_id,
            session_id=session_id,
            new_message=message,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text or ""

        # Read session state for outputs
        final_session = await session_service.get_session(
            app_name="website_builder_swarm",
            user_id=req.user_id,
            session_id=session_id,
        )
        state = final_session.state if final_session else {}

        return BuildResponse(
            session_id=session_id,
            result=final_response or "Swarm completed.",
            quality_history=state.get("quality_history", []),
            build_result=state.get("build_result"),
            brand_guard_result=state.get("brand_guard_result"),
            site_structure=state.get("site_structure"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Status endpoint ───────────────────────────────────────────────────────────

@app.get("/session/{session_id}")
async def get_session_status(session_id: str, user_id: str = "default"):
    """Get the current state of a build session."""
    try:
        _, session_service = _make_runner()
        session = await session_service.get_session(
            app_name="website_builder_swarm",
            user_id=user_id,
            session_id=session_id,
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return {
            "session_id": session_id,
            "state": {k: v for k, v in session.state.items() if k != "dna_context"},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8902, reload=False)
