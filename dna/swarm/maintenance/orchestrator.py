"""
dna/swarm/maintenance/orchestrator.py — Maintenance Swarm (Google ADK)

DNA-blind website maintenance system.
Keeps any website in sync with its DNA. Audits, patches, deploys.
Runs scheduled or triggered on DNA change.

Pipeline:
    MaintenanceOrchestrator (LlmAgent)
        └── MaintenancePipeline (SequentialAgent)
              ├── DriftAgent  → diffs DNA vs live HTML
              ├── SEOAgent    → audits SEO quality
              └── ActionLoop  → triggers Builder Swarm or deploys
"""
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent

from dna.swarm.maintenance.tools import (
    read_live_html, read_dna_section, read_dna_files, read_agency_protocols,
    diff_dna_vs_html, audit_seo,
    trigger_builder_swarm, run_deploy,
)
from dna.swarm.maintenance.callbacks import dna_inject_callback, make_quality_scorer


def _make_drift_agent() -> LlmAgent:
    return LlmAgent(
        name="DriftAgent",
        model="gemini-2.5-flash",
        instruction="""You are a content drift detector.
Compare the live website against the DNA. Find anything stale or mismatched.

STEP 1 — diff_dna_vs_html() → automated mismatch detection
STEP 2 — read_dna_section("site") → what the DNA says content should be
STEP 3 — Decide:
  0 mismatches → site is fresh → action: "none"
  1–3 mismatches → minor drift → action: "patch"
  4+ mismatches → major drift → action: "full_rebuild"

Write state["drift_result"] = {"stale_count": N, "action": "...", "mismatches": [...]}
Set state["quality_score"] = 1.0.
""",
        tools=[diff_dna_vs_html, read_dna_section],
        output_key="drift_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("drift"),
    )


def _make_seo_agent() -> LlmAgent:
    return LlmAgent(
        name="SEOAgent",
        model="gemini-2.5-flash",
        instruction="""You are the Lead SEO Strategist of a top-tier digital agency.
Audit the live website for SEO quality. All evaluation is based on the DNA.

STEP 1 — Learn the Agency SOPs:
  read_agency_protocols() → learn the technical SEO and development standards
STEP 2 — audit_seo("index.html") → full SEO report
STEP 3 — read_dna_section("brand") → verify brand info consistency
STEP 4 — Evaluate:
  Score >= 8: pass
  Score 6–7: minor issues, flag for patch
  Score < 6: major issues, trigger rebuild

Write state["seo_result"]. Set state["quality_score"] = seo_score / 10.
""",
        tools=[read_agency_protocols, audit_seo, read_dna_section],
        output_key="seo_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("seo"),
    )


def _make_action_agent() -> LlmAgent:
    return LlmAgent(
        name="ActionAgent",
        model="gemini-2.5-flash",
        instruction="""You are the maintenance action executor.
Act on what DriftAgent and SEOAgent found.

Read state["drift_result"] and state["seo_result"].

If drift == "full_rebuild" OR seo_score < 7:
  → trigger_builder_swarm("Full rebuild — drift or SEO issues detected")
  → After builder, run_deploy()

If drift == "patch" AND seo_score >= 7:
  → trigger_builder_swarm("Patch — minor content drift")
  → run_deploy()

If drift == "none" AND seo_score >= 8:
  → No action. Site is healthy.
  → Set state["escalate_to_parent"] = True immediately.

Write state["action_result"]. Set state["quality_score"].
Set state["escalate_to_parent"] = True when done.
""",
        tools=[trigger_builder_swarm, run_deploy],
        output_key="action_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("action"),
    )


def _make_action_loop() -> LoopAgent:
    return LoopAgent(
        name="ActionLoop",
        sub_agents=[_make_action_agent()],
        max_iterations=2,
    )


def build_root_agent() -> LlmAgent:
    """Factory: fresh Maintenance Swarm. DNA-blind."""
    pipeline = SequentialAgent(
        name="MaintenancePipeline",
        sub_agents=[
            _make_drift_agent(),
            _make_seo_agent(),
            _make_action_loop(),
        ],
    )

    return LlmAgent(
        name="MaintenanceOrchestrator",
        model="gemini-2.5-pro",
        instruction="""You are the Maintenance Orchestrator.
Keep any website in sync with its DNA. You know nothing about the brand.

Delegate to MaintenancePipeline:
  1. DriftAgent → compares DNA to live HTML
  2. SEOAgent → audits SEO quality
  3. ActionLoop → rebuilds or deploys based on findings

After completion, report: drift status, SEO score, actions taken.
""",
        sub_agents=[pipeline],
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("orchestrator"),
    )


root_agent = build_root_agent()
