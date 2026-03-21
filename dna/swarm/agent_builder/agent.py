"""agent.py — ADK entry point for the Agent Builder Swarm."""
import sys, os
_this_dir = os.path.dirname(os.path.abspath(__file__))
_swarm_dir = os.path.dirname(_this_dir)
_dna_dir = os.path.dirname(_swarm_dir)
_root = os.path.dirname(_dna_dir)
for p in [_root, _dna_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from dna.swarm.agent_builder.orchestrator import root_agent
print(f"[agent_builder] root_agent loaded: {root_agent.name}")
