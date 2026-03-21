"""
dna/swarm/agent_maintenance/orchestrator.py — Agent Maintenance Swarm (Google ADK)

Reads real conversation logs from the DB → scores agent tone and performance →
identifies weak phases → rewrites prompts. Runs weekly or on quality drop.

Pipeline:
    AgentMaintenanceOrchestrator (LlmAgent, gemini-2.5-pro)
        └── MaintenancePipeline (SequentialAgent)
              ├── AuditAgent     → reads conversations, scores tone/brand/conversion
              ├── DiagnosisAgent → identifies which phase is underperforming
              └── RepairLoop     → RefinerAgent rewrites weak prompts → ValidatorAgent scores (≤3 passes)
              └── ReporterAgent  → writes maintenance_report.md

Triggered by: weekly cron, manual trigger, or when conversion drops
"""
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent

from dna.swarm.agent_maintenance.tools import (
    get_recent_conversations, get_conversion_stats,
    get_phase_prompt, get_voice_rules, get_agents_contract,
    write_phase_prompt, write_maintenance_report,
)
from dna.swarm.agent_maintenance.callbacks import dna_inject_callback, make_quality_scorer


def _make_audit_agent() -> LlmAgent:
    return LlmAgent(
        name="AuditAgent",
        model="gemini-2.5-flash",
        instruction="""You are the Audit Agent. Score the live agent's real conversations.

STEP 1 — Read data:
  get_recent_conversations(days=7) → actual WhatsApp messages between agent and clients
  get_conversion_stats() → how many leads converted to paid
  get_voice_rules() → what the brand tone should be

STEP 2 — Score each conversation (0-10) on:
  TONE: Does the agent sound like the brand? Luxury concierge vs generic chatbot?
  FLOW: Does it move the client forward? Or does it stall with questions?
  COMPLIANCE: Does it follow the contract? (no "AI", no "our team", always a next step)
  CLOSING: In sales convos — did it offer the payment link? Too early? Too late?
  LENGTH: Are messages the right length for WhatsApp? (2-3 sentences, not walls of text)

STEP 3 — Write to state:
  state["audit_scores"] = {
    "overall": 7.5,
    "tone": 8,
    "flow": 7,
    "compliance": 9,
    "closing": 6,
    "length": 8,
    "conversations_reviewed": 12,
    "worst_phase": "sales",  ← which phase had the lowest scores
    "issues": ["Sales agent doesn't push for payment link early enough", ...]
  }
  state["quality_score"] = overall / 10

The issues list is the most important output — be SPECIFIC about what's wrong.""",
        tools=[get_recent_conversations, get_conversion_stats, get_voice_rules],
        output_key="audit_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("audit"),
    )


def _make_diagnosis_agent() -> LlmAgent:
    return LlmAgent(
        name="DiagnosisAgent",
        model="gemini-2.5-flash",
        instruction="""You are the Diagnosis Agent. Based on the audit, decide what to fix.

STEP 1 — Read:
  state["audit_scores"] — scores, worst_phase, issues list
  get_phase_prompt(worst_phase) — the current prompt for the weakest phase

STEP 2 — Decide action:

  If overall score ≥ 8: Agent is healthy. No rewrite needed.
    → state["action"] = "none"
    → state["escalate_to_parent"] = True (skip repair loop)

  If overall score 6-7: Targeted fix. Only rewrite the worst phase.
    → state["action"] = "fix"
    → state["fix_phases"] = ["sales"]  (or whichever is weakest)
    → Read the current prompt, identify which SPECIFIC lines need to change

  If overall score < 6: Major rewrite. Rewrite all phases.
    → state["action"] = "full_rebuild"
    → state["fix_phases"] = ["sales", "briefing", "production", "delivery"]

STEP 3 — For each phase to fix, write concrete instructions:
  state["fix_instructions_PHASE"] = "The sales prompt needs to push for payment link after the 3rd message instead of waiting for the client to ask..."

Be surgical. Don't say "improve tone" — say exactly WHAT to change and HOW.
Set state["quality_score"] = 1.0 (diagnosis always completes).""",
        tools=[get_phase_prompt, get_voice_rules, get_agents_contract],
        output_key="diagnosis_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("diagnosis"),
    )


def _make_refiner_agent() -> LlmAgent:
    return LlmAgent(
        name="RefinerAgent",
        model="gemini-2.5-flash",
        instruction="""You are the Refiner Agent. Rewrite agent prompts based on diagnosis.

STEP 1 — Read:
  state["action"] — "fix" or "full_rebuild"
  state["fix_phases"] — which phases to rewrite
  state["fix_instructions_PHASE"] — exact instructions from DiagnosisAgent

STEP 2 — For each phase in fix_phases:
  - get_phase_prompt(phase) → read the current prompt
  - Apply the fix instructions SURGICALLY — change what's broken, keep what works
  - write_phase_prompt(phase, improved_prompt) → save it

STEP 3 — Write to state:
  state["rewrite_summary"] = what was changed and why
  Set state["quality_score"] = 0.9 if all rewrites applied.""",
        tools=[get_phase_prompt, write_phase_prompt, get_voice_rules],
        output_key="refine_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("refiner"),
    )


def _make_repair_validator() -> LlmAgent:
    return LlmAgent(
        name="RepairValidator",
        model="gemini-2.5-flash",
        instruction="""You are the Repair Validator. Check if the rewritten prompts are better.

STEP 1 — For each phase that was rewritten (state["fix_phases"]):
  get_phase_prompt(phase) → read the new prompt
  get_voice_rules() → check against brand voice

STEP 2 — Score each rewritten prompt (0-10):
  - Does it fix the specific issues from state["audit_scores"]["issues"]?
  - Does it still follow the brand voice?
  - Is it the right length (400-800 words)?

STEP 3 — If ALL rewrites score ≥ 8:
  state["escalate_to_parent"] = True (exits RepairLoop — we're done)
  
If any score < 8:
  state["validation_issues"] = specific remaining problems for RefinerAgent""",
        tools=[get_phase_prompt, get_voice_rules],
        output_key="repair_validation",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("repair_validator"),
    )


def _make_reporter_agent() -> LlmAgent:
    return LlmAgent(
        name="ReporterAgent",
        model="gemini-2.5-flash",
        instruction="""You are the Reporter Agent. Write the maintenance report.

STEP 1 — Read everything from state:
  state["audit_scores"] — original scores
  state["action"] — what was decided
  state["fix_phases"] — what was fixed
  state["rewrite_summary"] — what changed

STEP 2 — Write a clear maintenance report using write_maintenance_report():
  Format:
  ## Audit Results
  - Overall score: X/10
  - Conversations reviewed: N
  - Worst phase: (the weakest phase)
  
  ## Issues Found
  - Issue 1
  - Issue 2
  
  ## Action Taken
  - {action}: rewrote {phases}
  - Changes: {summary}
  
  ## Recommendation
  - Next audit in: 7 days
  - Watch: (the weakest phase) closely

Set state["quality_score"] = 1.0.""",
        tools=[write_maintenance_report],
        output_key="report_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("reporter"),
    )


def _make_repair_loop() -> LoopAgent:
    return LoopAgent(
        name="RepairLoop",
        sub_agents=[_make_refiner_agent(), _make_repair_validator()],
        max_iterations=3,
    )


# ── Root Agent ────────────────────────────────────────────────────────────────

def build_root_agent() -> LlmAgent:
    """Factory: fresh Agent Maintenance Swarm per run."""
    pipeline = SequentialAgent(
        name="MaintenancePipeline",
        sub_agents=[
            _make_audit_agent(),
            _make_diagnosis_agent(),
            _make_repair_loop(),
            _make_reporter_agent(),
        ],
    )

    return LlmAgent(
        name="AgentMaintenanceOrchestrator",
        model="gemini-2.5-pro",
        instruction="""You are the Agent Maintenance Orchestrator.
Your mission: keep the WhatsApp concierge agent performing at peak quality.

You read real conversation logs, score the agent's performance, and fix what's broken.

Delegate to MaintenancePipeline:
  1. AuditAgent     → reads real WhatsApp conversations, scores tone/flow/closing
  2. DiagnosisAgent → identifies which phase is weak, decides fix vs full rebuild
  3. RepairLoop     → RefinerAgent rewrites prompts → RepairValidator scores (≤3 passes)
  4. ReporterAgent  → writes maintenance_report.md with findings + actions

After completion, report:
  - Overall agent health score
  - Which phases were audited and their scores
  - What action was taken (none / fix / full_rebuild)
  - Were rewrites validated successfully?""",
        sub_agents=[pipeline],
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("orchestrator"),
    )


root_agent = build_root_agent()
