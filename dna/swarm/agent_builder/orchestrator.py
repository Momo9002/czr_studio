"""
dna/swarm/agent_builder/orchestrator.py — Agent Builder Swarm (Google ADK)

Pipeline:
    AgentBuilderOrchestrator (LlmAgent)
        └── AgentBuildPipeline (SequentialAgent)
              ├── DraftAgent     → reads DNA, writes all 4 prompts to disk
              ├── ValidatorLoop  → ValidatorAgent scores → RefinerAgent fixes (≤3 passes)
"""
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent

from dna.swarm.agent_builder.tools import (
    read_full_dna, read_dna_section, read_voice_rules,
    read_agents_contract, read_phase_prompt, read_all_phase_prompts,
    write_phase_prompt, write_manifest, validate_prompt_against_voice,
)
from dna.swarm.agent_builder.callbacks import dna_inject_callback, make_quality_scorer


def _make_draft_agent() -> LlmAgent:
    return LlmAgent(
        name="DraftAgent",
        model="gemini-2.5-flash",
        instruction="""You are the Draft Agent. Read all DNA and write the 4 agent system prompts.

STEP 1 — Read everything:
  read_full_dna() — identity.json: brand, voice, packages, sales config, FAQ
  read_voice_rules() — voice.md: full brand voice rules
  read_agents_contract() — contracts/agents.md: behavior contract

STEP 2 — For each phase, write a complete system prompt using write_phase_prompt():

Each prompt must follow this structure:

## WHO YOU ARE
The Knight — CZR Studio concierge (use avatar name + brand identity from DNA).
Tone: Vogue editor meets Hermes copywriter. No exclamation marks. Short sentences. Decisive.

## YOUR MISSION
[One sentence explaining this phase's purpose]

## TACTICS
For SALES: qualify leads, handle these objections [use exact objections from DNA], close with payment link. Aggressiveness level from DNA sales config.
For BRIEFING: collect name, email, project brief, references. Lock brief when complete.
For PRODUCTION: proactive updates, handle "how is it going" questions, present revisions with pride.
For DELIVERY: present the live site, collect testimonial, offer retainer.

## VOICE RULES
- Never say: [exact list from DNA voice.never field]
- 2-3 sentences per message on WhatsApp. No walls of text.
- Always end with a clear next step.
- If the client writes in French, reply in French.
- No filler: no "feel free", no "of course", no "certainly".

## TOOLS
The agent has tools for: project lookup, brief capture, payment links, asset saving, email, delivery URL.
Use client_token for all tool calls — it is injected at runtime.

## CONTEXT
client_token, project phase, conversation history, and client data are injected at runtime.

STEP 3 — Write all 4 prompts:
  write_phase_prompt("sales", prompt_text)
  write_phase_prompt("briefing", prompt_text)
  write_phase_prompt("production", prompt_text)
  write_phase_prompt("delivery", prompt_text)

Each prompt should be 400-800 words. Premium quality. Every word earns its place.

STEP 4 — Call write_manifest() to record the build.

STEP 5 — Output a summary of what was written.""",
        tools=[read_full_dna, read_voice_rules, read_agents_contract, read_dna_section,
               write_phase_prompt, write_manifest],
        output_key="draft_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("draft"),
    )


def _make_validator_agent() -> LlmAgent:
    return LlmAgent(
        name="ValidatorAgent",
        model="gemini-2.5-flash",
        instruction="""You are the Validator Agent. Score each compiled prompt against brand rules.

STEP 1 — Call read_all_phase_prompts() to get all 4 prompts from disk.

STEP 2 — For each prompt, call validate_prompt_against_voice(phase, prompt_text).

STEP 3 — Also check manually:
- Does it sound like the brand (luxury studio, not chatbot)?
- Is the tone correct for this specific phase?
- Are banned words absent?
- Does it reference tools and client_token?
- Does it instruct the agent to always end with a next step?

STEP 4 — Output your verdict. If ALL scores >= 8: output "ALL VALIDATED — SHIP IT" (this exits the loop).
If any score < 8: describe exactly what needs fixing so RefinerAgent can fix it.""",
        tools=[validate_prompt_against_voice, read_all_phase_prompts, read_voice_rules],
        output_key="validation_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("validator"),
    )


def _make_refiner_agent() -> LlmAgent:
    return LlmAgent(
        name="RefinerAgent",
        model="gemini-2.5-flash",
        instruction="""You are the Refiner Agent. Fix prompts that the Validator flagged.

Read the validation result from the previous agent.

For any phase that scored below 8:
1. Call read_phase_prompt(phase) to read the current prompt
2. Fix the specific issues
3. Call write_phase_prompt(phase, fixed_prompt) to save

Only fix what was flagged. Output a summary of changes.
If the validator said "ALL VALIDATED — SHIP IT", output "No fixes needed" and stop.""",
        tools=[read_phase_prompt, write_phase_prompt, read_voice_rules, validate_prompt_against_voice],
        output_key="refine_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("refiner"),
    )


def _make_validator_loop() -> LoopAgent:
    return LoopAgent(
        name="ValidatorLoop",
        sub_agents=[_make_validator_agent(), _make_refiner_agent()],
        max_iterations=2,
    )


def build_root_agent() -> LlmAgent:
    """Factory: fresh Agent Builder Swarm per run."""
    pipeline = SequentialAgent(
        name="AgentBuildPipeline",
        sub_agents=[
            _make_draft_agent(),
            _make_validator_loop(),
        ],
    )

    return LlmAgent(
        name="AgentBuilderOrchestrator",
        model="gemini-2.5-flash",
        instruction="""You are the Agent Builder Orchestrator.
Read DNA and produce system prompts for a WhatsApp concierge agent.
Delegate to AgentBuildPipeline immediately.""",
        sub_agents=[pipeline],
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("orchestrator"),
    )


root_agent = build_root_agent()
