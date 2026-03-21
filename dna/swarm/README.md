"""
dna/swarm/README.md — Website Builder Swarm

Generic Google ADK swarm that converts any brand DNA into a premium website.

## Architecture

    DNA (identity.json + vision.md + models.md)
           ↓
    WebsiteBuilderOrchestrator  (LlmAgent, gemini-2.5-pro)
           │
           ├── StructureAgent       → reads DNA + design models → proposes sections_order
           │                          with dark/light mode per section → patches identity.json
           │
           ├── CopyQualityLoop      (LoopAgent, max 3 iterations)
           │     ├── CopyAgent      → writes premium copy for all sections
           │     ├── BrandGuard     → validates against DNA voice rules
           │     └── CopyReviser    → surgical fixes based on BrandGuard critique
           │                          Loop exits when BrandGuard scores >= 0.8
           │
           └── BuilderAgent         → runs dna.sync audit → dna.build → dna.cases_builder
                                      Generates index.html + all case study pages
           ↓
    index.html + cases/*/index.html

## Cloud Sessions & Memory

- Sessions: VertexAiSessionService (project: momo-agent-489822, region: us-central1)
- Memory: VertexAiMemoryBankService (semantic memory across brand builds)
- Fallback: InMemorySessionService for local dev

## Running

### As ADK web UI (dev)
    cd czr_studio
    adk web --agent dna.swarm.orchestrator

### As FastAPI server (production)
    uvicorn dna.swarm.server:app --port 8902

### Trigger via HTTP
    POST http://localhost:8902/run
    {
      "task": "Full rebuild from DNA",
      "credentials": {"GOOGLE_API_KEY": "...", "GOOGLE_CLOUD_PROJECT": "momo-agent-489822"}
    }

### Via Momo
    Momo can trigger a full rebuild: POST http://localhost:8902/run

## Files

| File | Purpose |
|---|---|
| `orchestrator.py` | Root agent + all sub-agents + pipeline assembly |
| `tools.py` | DNA read/write/build tools (plain functions) |
| `callbacks.py` | DNA inject + quality scorer callbacks |
| `server.py` | FastAPI server with Vertex AI cloud sessions |
| `README.md` | This file |

## Brand-agnostic Design

This swarm works with ANY identity.json that follows the DNA schema:
- brand block: name, tagline, site URL
- voice block: never[], always[], tone, register
- site block: sections_order[], hero, work, about, process, packages, etc.
- packages block: sprint, flagship, retainer
- colors, typography, tokens

Change the DNA — the swarm adapts automatically.
"""
