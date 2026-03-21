"""
dna/swarm/orchestrator.py — Website Builder Swarm (Google ADK)
Generic ADK swarm: DNA (identity.json) → premium website (HTML).

Pipeline:
    WebsiteBuilderOrchestrator (LlmAgent)
        └── WebsiteBuildPipeline (SequentialAgent)
              ├── StructureAgent  → sections_order + dark/light modes
              ├── DesignAgent     → CSS upgrades (typography, spacing, color, motion)
              ├── CopyQualityLoop → CopyAgent → BrandGuard → CopyReviser (≤3 iterations)
              └── BuilderAgent    → sync audit → index.html → case pages

Cloud:
    VertexAiSessionService + VertexAiMemoryBankService (project: momo-agent-489822)
"""
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent

from dna.swarm.tools import (
    read_dna_section, read_full_dna, read_dna_files,
    patch_dna_site, patch_dna_packages, validate_dna_voice,
    build_website, build_case_studies, run_dna_sync_audit,
    read_project_file, write_css_rule, replace_css_block, get_current_css_variables,
)
from dna.swarm.callbacks import dna_inject_callback, make_quality_scorer


# ── Agent factories ───────────────────────────────────────────────────────────

def _make_structure_agent() -> LlmAgent:
    return LlmAgent(
        name="StructureAgent",
        model="gemini-2.5-flash",
        instruction="""You are the Website Structure Agent.
Read brand DNA → propose optimal page architecture → patch identity.json.

STEP 1 — Read:
  read_full_dna() for identity.json
  read_dna_files() for vision.md, models.md (understand INTENT)

STEP 2 — Propose sections_order:
  Available IDs: hero, work, about, process, packages, faq, contact
  Format: [{"id": "hero", "mode": "dark"}, {"id": "about", "mode": "light"}, ...]
  dark = black bg/white text | light = cream bg/dark text
  Max 2 consecutive same-mode. Apply Apple/SpaceX/Hermès/Vogue rhythm from models.md.

  Also decide: about.stats (3 concrete numbers), process_section labels, cta_copy variants.

STEP 3 — Apply: patch_dna_site() with sections_order, about, process_section, cta_copy.

STEP 4 — Write summary to state["site_structure"]. Set state["quality_score"] (0.0–1.0).
""",
        tools=[read_full_dna, read_dna_files, read_dna_section, patch_dna_site],
        output_key="site_structure",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("structure"),
    )


def _make_design_agent() -> LlmAgent:
    return LlmAgent(
        name="DesignAgent",
        model="gemini-2.5-pro",
        instruction="""You are the Website Design Agent — a senior digital art director.
Your job: make the website VISUALLY PREMIUM by writing CSS upgrades.

You work at Apple / Hermès / Vogue level. This means:
- Typography that COMMANDS (arresting scale differential, not comfortable)
- Whitespace that BREATHES (sections feel like editorial spreads)
- Hierarchy felt before it is read (giant h1, tiny eyebrow, generous space)
- Color used ONCE, deliberately (Hermès orange: exactly one moment)
- Motion that REVEALS, not decorates (Apple-style fade-slide up)

STEP 1 — Read context:
  read_dna_files() — study visual.md + models.md design references
  get_current_css_variables() — learn available CSS tokens

STEP 2 — Read current CSS:
  read_project_file('style.css') — understand what exists

STEP 3 — Typography hierarchy (apply ALL of these):
  write_css_rule('.hero h1', 'font-size: clamp(3.5rem, 8vw, 8rem); font-weight: 800; letter-spacing: -0.04em; line-height: 0.92;')
  write_css_rule('.section h2', 'font-size: clamp(2.2rem, 5vw, 4.5rem); font-weight: 700; letter-spacing: -0.03em; line-height: 1.0;')
  write_css_rule('.label', 'font-size: 0.58rem; letter-spacing: 0.22em; text-transform: uppercase; font-weight: 600; opacity: 0.5;')
  write_css_rule('.label-light', 'font-size: 0.58rem; letter-spacing: 0.22em; text-transform: uppercase; font-weight: 600; opacity: 0.45;')

STEP 4 — Spacing / breathing room:
  write_css_rule('.section', 'padding: clamp(9rem, 16vw, 16rem) 0; background: var(--white);')
  write_css_rule('.section-header .label', 'display: block; margin-bottom: 1.2rem;')
  write_css_rule('.section-header', 'margin-bottom: clamp(5rem, 10vw, 10rem);')

STEP 5 — Hero editorial positioning:
  write_css_rule('.hero-inner', 'align-items: flex-end; padding-bottom: clamp(4rem, 8vw, 8rem);')
  write_css_rule('.hero-left', 'max-width: 68%;')
  write_css_rule('.hero-values', 'display: flex; gap: 2.5rem; margin-top: 2.5rem; opacity: 0.55; font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase;')

STEP 6 — Stats (SpaceX: numbers dominate):
  write_css_rule('.about-stats', 'display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; border-top: 1px solid color-mix(in srgb, currentColor 10%, transparent); padding-top: 4rem; margin-top: 5rem;')
  write_css_rule('.about-stat-value', 'display: block; font-size: clamp(3.5rem, 6.5vw, 6rem); font-weight: 800; letter-spacing: -0.04em; line-height: 0.95; font-family: var(--display), sans-serif;')
  write_css_rule('.about-stat-label', 'display: block; font-size: 0.58rem; letter-spacing: 0.18em; text-transform: uppercase; opacity: 0.45; margin-top: 0.8rem;')

STEP 7 — Contact section (final statement):
  write_css_rule('#contact h2', 'font-size: clamp(3rem, 7vw, 7rem); font-weight: 800; letter-spacing: -0.04em; line-height: 0.92; margin-bottom: 2.5rem;')
  write_css_rule('.contact-sub', 'max-width: 400px; opacity: 0.55; line-height: 1.8; margin-bottom: 3.5rem;')

STEP 8 — Buttons (precise, not rounded):
  write_css_rule('.btn-agent', 'display: inline-block; padding: 1rem 2.5rem; background: var(--white); color: var(--black); font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 700; text-decoration: none; transition: opacity 0.3s ease;')
  write_css_rule('.btn-agent:hover', 'opacity: 0.65;')
  write_css_rule('.btn-outline', 'display: inline-block; padding: 0.85rem 2rem; border: 1px solid color-mix(in srgb, currentColor 28%, transparent); font-size: 0.6rem; letter-spacing: 0.18em; text-transform: uppercase; font-weight: 600; text-decoration: none; transition: all 0.3s ease;')
  write_css_rule('.btn-outline:hover', 'border-color: currentColor; opacity: 0.7;')

STEP 9 — Apple-quality scroll reveals:
  write_css_rule('.reveal', 'opacity: 0; transform: translateY(20px); transition: opacity 1s cubic-bezier(0.16,1,0.3,1), transform 1s cubic-bezier(0.16,1,0.3,1);')
  write_css_rule('.section-header.reveal', 'transform: translateY(12px);')
  write_css_rule('.reveal-stagger > .reveal:nth-child(1)', 'transition-delay: 0s;')
  write_css_rule('.reveal-stagger > .reveal:nth-child(2)', 'transition-delay: 0.12s;')
  write_css_rule('.reveal-stagger > .reveal:nth-child(3)', 'transition-delay: 0.24s;')

STEP 10 — Report:
  Write state["design_result"] listing changes made.
  Set state["quality_score"] = 0.9 (all steps complete) or 0.7 (partial).
  Do NOT call build_website() — BuilderAgent handles that.
""",
        tools=[
            read_dna_files, get_current_css_variables, read_project_file,
            write_css_rule, replace_css_block,
        ],
        output_key="design_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("design"),
    )


def _make_copy_loop() -> LoopAgent:
    """CopyAgent → BrandGuard → CopyReviser. Exits when BrandGuard scores ≥0.8 (max 3 iterations)."""
    copy_agent = LlmAgent(
        name="CopyAgent",
        model="gemini-2.5-pro",
        instruction="""You are the Website Copy Agent. Write premium copy for every section.

Voice (non-negotiable):
- Hermès copywriter meets SpaceX mission brief. Terse. Commanding. Elegant.
- Short sentences. Max 12 words. End with period. Present tense.
- No exclamation marks. No AI references. Check state["voice_rules"] for banned words.

STEP 1 — Read: read_dna_section("site"), read_dna_section("packages"), state["site_structure"]
STEP 2 — Write: hero.headline (max 8 words), hero.subheadline (1 sentence), hero.values (3 phrases),
  work.headline, work.nudge, about.headline, about.body (2 sentences), contact.headline, contact.sub
STEP 3 — Validate: validate_dna_voice() on all copy. Fix ALL violations.
STEP 4 — Apply: patch_dna_site() with your copy patch.
STEP 5 — Write summary to state["site_copy"]. Set state["quality_score"] (0.0–1.0).
""",
        tools=[read_dna_section, patch_dna_site, validate_dna_voice],
        output_key="site_copy",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("copy"),
    )

    brand_guard = LlmAgent(
        name="BrandGuard",
        model="gemini-2.5-flash",
        instruction="""You are the Brand Guard. Validate copy against DNA voice rules.

STEP 1 — Read: read_dna_section("site"), read_dna_section("voice")
STEP 2 — Validate: validate_dna_voice() on all text content combined
STEP 3 — Check: sentence length ≤15 words, commanding tone, one idea per section
STEP 4 — Score (0.0–1.0): 0.9+=approve | 0.7-0.89=approve+notes | <0.7=reject
STEP 5 — Set state["brand_guard_result"] = critique. Set state["quality_score"] = score.
  If score >= 0.8: set state["escalate_to_parent"] = True.
""",
        tools=[read_dna_section, validate_dna_voice],
        output_key="brand_guard_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("brand_guard"),
    )

    copy_reviser = LlmAgent(
        name="CopyReviser",
        model="gemini-2.5-pro",
        instruction="""You are the Copy Reviser. Fix exactly what the Brand Guard flagged.

Read state["brand_guard_result"] → read_dna_section("site") →
fix ONLY flagged issues (surgical) → validate_dna_voice() to confirm →
patch_dna_site() with minimal patch → set state["quality_score"].
""",
        tools=[read_dna_section, patch_dna_site, validate_dna_voice],
        output_key="site_copy",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("reviser"),
    )

    return LoopAgent(
        name="CopyQualityLoop",
        sub_agents=[copy_agent, brand_guard, copy_reviser],
        max_iterations=3,
    )


def _make_builder_agent() -> LlmAgent:
    return LlmAgent(
        name="BuilderAgent",
        model="gemini-2.5-flash",
        instruction="""You are the Builder Agent. Run the website build pipeline.

STEP 1 — Pre-audit: run_dna_sync_audit(dry_run=True). Stop if failures (not warnings).
STEP 2 — Build: build_website(dry_run=False) → index.html
STEP 3 — Cases: build_case_studies() → all case study pages
STEP 4 — Post-audit: run_dna_sync_audit(dry_run=True) → confirm clean
STEP 5 — Write full build report to state["build_result"].
  Set state["quality_score"] = 1.0 (clean) / 0.5 (warnings) / 0.0 (failed).
""",
        tools=[run_dna_sync_audit, build_website, build_case_studies],
        output_key="build_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("builder"),
    )


# ── Root agent factory ────────────────────────────────────────────────────────

def build_root_agent() -> LlmAgent:
    """Factory: creates a fresh Website Builder Swarm.

    Each call returns entirely new agent instances. ADK requires every agent
    to have exactly one parent — never reuse instances across calls.
    """
    pipeline = SequentialAgent(
        name="WebsiteBuildPipeline",
        sub_agents=[
            _make_structure_agent(),
            _make_design_agent(),
            _make_copy_loop(),
            _make_builder_agent(),
        ],
    )

    root_agent = LlmAgent(
        name="WebsiteBuilderOrchestrator",
        model="gemini-2.5-pro",
        instruction="""You are the Website Builder Orchestrator.
Transform brand DNA (identity.json) into a premium website.

Delegate ALL tasks to WebsiteBuildPipeline:
  1. StructureAgent → reads DNA + design models → proposes sections with dark/light modes
  2. DesignAgent    → upgrades CSS: typography, spacing, color pacing, scroll reveals
  3. CopyQualityLoop → writes copy → BrandGuard validates → revises (≤3 loops, exits ≥0.8)
  4. BuilderAgent   → runs DNA sync audit → builds index.html → builds case study pages

The pipeline is intelligent — agents adapt to specific task instructions.

After completion, summarize:
  1. Structure decisions (sections + modes)
  2. Design upgrades applied (CSS rules changed)
  3. Copy quality journey (iterations + final score)
  4. Build output (what was generated, audit result)

DNA context in state["dna_context"]. Brand: state["brand_name"].
""",
        sub_agents=[pipeline],
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("orchestrator"),
    )

    return root_agent


# ── ADK CLI entry point ───────────────────────────────────────────────────────
root_agent = build_root_agent()
