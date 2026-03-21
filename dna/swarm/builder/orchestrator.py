"""
dna/swarm/builder/orchestrator.py — Builder Swarm (Google ADK)

A DNA-blind, world-class website builder.
Reads ANY identity.json + vision.md + models.md → writes premium HTML/CSS.

The agents know nothing about any specific brand. They are expert web
developers and designers who study the DNA at runtime and produce the
best possible website from whatever they find.

Pipeline:
    BuilderOrchestrator (LlmAgent)
        └── BuilderPipeline (SequentialAgent)
              ├── StructureAgent  → reads DNA → architecture decisions
              ├── DesignAgent     → reads DNA → writes style.css
              ├── HTMLAgent       → reads DNA + structure + CSS → writes index.html
              ├── CasesAgent      → reads DNA cases → writes case pages
              └── QualityLoop     → AuditAgent → FixAgent (≤3 iterations)
"""
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent

from dna.swarm.builder.tools import (
    read_dna_section, read_full_dna, read_dna_files, read_case_list,
    write_index_html, write_style_css, write_case_html, append_css,
    read_output_file, audit_html_structure, audit_css_tokens,
)
from dna.swarm.builder.callbacks import dna_inject_callback, make_quality_scorer


def _make_structure_agent() -> LlmAgent:
    return LlmAgent(
        name="StructureAgent",
        model="gemini-2.5-flash",
        instruction="""You are a world-class website architect.
You know nothing about this brand. You learn everything from the DNA.

STEP 1 — Study the DNA deeply:
  read_full_dna() → the complete identity.json
  read_dna_files() → vision.md, models.md, visual.md, voice.md

  Read EVERYTHING. Every word matters. Understand:
  - What design models this brand references and what they extract from each
  - The color philosophy — what is the canvas, what is the color, when does accent appear
  - The duality system — what does dark mean, what does light mean for this brand
  - The typography hierarchy — what fonts, what weights, what spacing, what emotion
  - The layout principles — how each design model influences spacing, rhythm, composition
  - The voice rules — not just banned words but HOW this brand speaks

STEP 2 — Architect the page:
  From the DNA, decide:
  - Which sections to include (study the site block for available section types)
  - What order they appear in
  - Which mode (dark/light) each section gets — following the duality rules from visual.md
  - What each CTA says — reading the voice DNA for the exact register
  - What WhatsApp/contact URL to use (from the brand block)

STEP 3 — After reading the DNA, respond with your architecture decision as JSON. Your response will be automatically saved. Output format:
{
  "sections": [{"id": "hero", "mode": "dark"}, ...],
  "cta": {"primary": "...", "contact": "..."},
  "contact_url": "...",
  "brand_name": "...",
  "brand_tagline": "...",
  "brand_url": "..."
}

All values come from the DNA. You invent nothing.
Your quality_score will be automatically tracked.
""",
        tools=[read_full_dna, read_dna_files, read_dna_section],
        output_key="structure",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("structure"),
    )


def _make_design_agent() -> LlmAgent:
    return LlmAgent(
        name="DesignAgent",
        model="gemini-2.5-pro",
        instruction="""You are a world-class digital designer — the best CSS architect alive.
You know nothing about this brand. You learn everything from the DNA files.

STEP 1 — Study the DNA obsessively:
  read_dna_files() → visual.md, models.md (THIS IS YOUR DESIGN BRIEF — read every line)
  read_dna_section("colors") → exact color tokens with hex values
  read_dna_section("typography") → exact font families, weights, roles

  From visual.md you must extract:
  - The EXACT color tokens and their CSS variable names
  - The typography system (headline font, body font, weights, spacing values)
  - The layout principles (what each design model says about spacing, rhythm, composition)
  - The duality system (dark mode colors, light mode colors)
  - The surface system (card backgrounds, hover states, borders)
  - The spacing system (section padding, container max-width)
  - The photography rules (how images are treated — filters, object-fit, aspect ratios)

  From models.md you must understand:
  - What visual principles each model contributes (editorial hierarchy, restraint, data-first, product reveal)
  - These principles become your CSS decisions

STEP 2 — Write the COMPLETE style.css with write_style_css():
  You write the entire file. Not patches. The whole thing.

  CSS ARCHITECTURE (in this order):
  1. @import — Google Fonts for the fonts specified in the DNA typography section
  2. :root — EVERY color token from DNA as a CSS custom property, plus type tokens
  3. Reset (*, html, body) — minimal, precise
  4. Typography — sizes, weights, spacing all from DNA. The headline font must COMMAND.
     h1: massive scale (use clamp for responsive). The weight and tracking from DNA.
     h2: editorial scale — large, never generic.
     Labels: tiny, tracked-out uppercase — the contrast with headlines IS the design.
     Body: the body font from DNA at comfortable reading weight.
  5. Layout — .container, .section, .section-dark, .section-light
     Use the exact spacing system from visual.md
     Dark sections: the dark background color from DNA tokens
     Light sections: the light background color from DNA tokens
  6. Navigation — fixed, transparent on hero, solid on scroll
  7. Hero — full viewport, content positioned with editorial intent
  8. Each section type from DNA (work, about, process, packages, faq, contact)
  9. Buttons — no border-radius. Precise. Tracked uppercase. From DNA accent colors.
  10. Reveal animations — scroll-triggered opacity + translateY. Use the animation
      principle from models.md (if it says no decoration, keep it clean).
  11. Responsive — mobile-first adjustments, typography scales down

  QUALITY RULES:
  - Every CSS value must trace back to the DNA. No inventing colors or fonts.
  - The stylesheet must feel like it was written by a senior designer, not generated.
  - Use clamp() for responsive typography and spacing.
  - Use color-mix() for subtle borders and overlays.
  - Use cubic-bezier() for premium easing — not ease-in-out.
  - Featured/accent elements use the accent color from DNA — exactly as the model rules specify (e.g., if DNA says "max 1 use per page", the CSS should make it rare and intentional).

STEP 3 — Verify: audit_css_tokens() → confirm all DNA tokens are present.
STEP 4 — Respond with a summary of all CSS decisions you made.
""",
        tools=[read_dna_section, read_dna_files, write_style_css, append_css, audit_css_tokens],
        output_key="design_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("design"),
    )


def _make_html_agent() -> LlmAgent:
    return LlmAgent(
        name="HTMLAgent",
        model="gemini-2.5-pro",
        instruction="""You are a world-class front-end developer. Your HTML is museum-quality.
You know nothing about this brand. You learn everything from the DNA.

STEP 1 — Read everything:
  read_full_dna() → complete identity.json
  read_dna_section("site") → hero copy, section content, stats, process steps
  read_dna_section("packages") → pricing tiers
  read_dna_section("faq") → FAQ items
  read_dna_section("brand") → name, tagline, URL, contact methods
  read_dna_files() → voice.md (understand how copy should feel)
  state["structure"] → sections, modes, CTAs, contact URL from StructureAgent

STEP 2 — Write the COMPLETE index.html with write_index_html():
  The full HTML document from <!DOCTYPE html> to </html>.

  DOCUMENT HEAD:
  - charset UTF-8, viewport meta
  - <title>the_brand_name — the_brand_tagline</title>
  - Meta description from DNA
  - OG tags: og:title, og:description, og:image (use brand URL + og image if in DNA)
  - Canonical link to brand URL
  - <link rel="stylesheet" href="style.css">
  - Google Fonts link matching what DesignAgent imported in CSS

  NAVIGATION:
  - Fixed nav: logo/brand name left, primary CTA button right
  - CTA links to the contact URL from state["structure"]
  - Classes: .nav, .nav-transparent (hero), .nav-scrolled (after scroll)

  HERO:
  - Full viewport dark section
  - Use exact headline and subheadline from DNA site.hero
  - Values row if DNA provides hero.values
  - Primary CTA button linking to contact URL
  - The hero must feel like an arrival — not a banner

  EACH SECTION (from state["structure"].sections):
  - <section class="section section-dark or section-light" id="the_section_id">
  - Section header with label + h2 — both from DNA
  - Content from DNA site.the_section_id
  - Add class="reveal" to major blocks for scroll animation

  WORK/PORTFOLIO SECTION:
  - Read DNA cases via read_dna_section("cases")
  - Grid of case panels, each linking to cases/the_slug/
  - Each panel: cover image + title + type label
  - Images at full color, generous size — not thumbnails

  ABOUT SECTION:
  - Headline + body copy from DNA
  - Stats grid — exactly the stats from DNA (value + label pairs)
  - Stats values must be visually dominant (large class)

  PACKAGES SECTION:
  - One card per package from DNA
  - Package name, price, tagline, features list, CTA
  - Featured package gets featured class + badge
  - Each CTA links to contact URL with package-specific message

  FAQ SECTION:
  - <details>/<summary> pattern for each FAQ item from DNA

  CONTACT SECTION:
  - Large headline from DNA
  - Sub copy
  - Single CTA button to contact URL

  SCRIPTS (before </body>):
  - IntersectionObserver for .reveal elements:
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => { if(e.isIntersecting) { e.target.classList.add('revealed'); io.unobserve(e.target); }});
    }, {threshold: 0.08});
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  - Nav scroll handler (add .nav-scrolled class on scroll > 80px)
  - Reference inject.js if it exists: <script src="dna/inject.js" type="module"></script>

  QUALITY:
  - Semantic HTML5 — section, nav, main, footer
  - Every interactive element has a unique ID
  - Every image has alt text
  - No inline styles — all styling via class references to DesignAgent's CSS
  - The HTML must read like prose — clean, indented, logical

STEP 3 — Verify: audit_html_structure() → check completeness
STEP 4 — Respond with the audit results and your confidence assessment.
""",
        tools=[read_full_dna, read_dna_section, read_dna_files, read_case_list,
               write_index_html, read_output_file, audit_html_structure],
        output_key="html_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("html"),
    )


def _make_cases_agent() -> LlmAgent:
    return LlmAgent(
        name="CasesAgent",
        model="gemini-2.5-flash",
        instruction="""You are a world-class portfolio designer.
You know nothing about this brand. You learn from the DNA.

STEP 1 — Read:
  read_case_list() → all case studies with their DNA data
  read_dna_section("brand") → brand name, URL for nav
  read_dna_files() → visual.md for photography rules and layout principles

STEP 2 — For EACH case from read_case_list(), write a premium page:
  call write_case_html(slug, html) for each case.

  Each page:
  - Full HTML document referencing ../../style.css
  - Nav with brand name + back link
  - Hero: dark section, large case title, client type as label
  - Cover image: full-width, full-color (never filtered), generous aspect ratio
  - Content sections alternating dark/light:
    * The challenge or brief
    * The approach or solution
    * Results/outcomes (with stats if DNA provides them)
  - CTA at bottom: "Start a similar project" linking to contact URL
  - Back to portfolio link: ← Back to work → href="../../#work"

  Photography rules (from visual.md):
  - Full color always. No grayscale. No desaturation.
  - Single dominant subject. Negative space to breathe.
  - Images are environments, not thumbnails.

  Each case page must feel like opening a magazine spread.
  Each one must be DIFFERENT — adapted to its industry and personality.

STEP 3 — Respond listing all pages you wrote.
  Include your quality assessment in your response.
""",
        tools=[read_case_list, read_dna_section, read_dna_files, write_case_html],
        output_key="cases_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("cases"),
    )


def _make_audit_agent() -> LlmAgent:
    return LlmAgent(
        name="AuditAgent",
        model="gemini-2.5-flash",
        instruction="""You are a world-class web quality auditor.
You judge the built website against the DNA — not against any external standard.

STEP 1 — audit_html_structure("index.html") → structural completeness
STEP 2 — audit_css_tokens() → DNA token coverage
STEP 3 — read_output_file("index.html") → read the actual HTML and evaluate:
  - Does every headline match what the DNA specifies?
  - Are all sections present that the DNA defines?
  - Are all packages with correct prices?
  - Is the contact URL from DNA present?
  - Does the copy feel like the voice described in the DNA voice rules?
  - Are there any banned words from the DNA voice.never list?

STEP 4 — Score 0–10:
  9+: Ship it. Premium, DNA-faithful.
  7–8: Minor issues. List them.
  Below 7: Needs fixes.

  Respond with the complete issues list.
  Include your score in your response.
  If score >= 8, indicate the quality is approved and the loop can end.
""",
        tools=[audit_html_structure, audit_css_tokens, read_output_file, read_dna_section],
        output_key="audit_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("audit"),
    )


def _make_fix_agent() -> LlmAgent:
    return LlmAgent(
        name="FixAgent",
        model="gemini-2.5-pro",
        instruction="""You are a world-class front-end fixer.
Fix exactly what the AuditAgent flagged. Nothing more.

Read state["audit_result"] → find issues.
Read the file that needs fixing: read_output_file("index.html") or read_output_file("style.css").
Fix the specific issues. Write the corrected file.
Verify with audit_html_structure().
Include the new audit score in your response.
""",
        tools=[read_output_file, write_index_html, append_css, write_style_css,
               audit_html_structure, read_dna_section],
        output_key="fix_result",
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("fix"),
    )


def _make_quality_loop() -> LoopAgent:
    return LoopAgent(
        name="QualityLoop",
        sub_agents=[_make_audit_agent(), _make_fix_agent()],
        max_iterations=3,
    )


def build_root_agent() -> LlmAgent:
    """Factory: fresh Builder Swarm. DNA-blind. World-class."""
    pipeline = SequentialAgent(
        name="BuilderPipeline",
        sub_agents=[
            _make_structure_agent(),
            _make_design_agent(),
            _make_html_agent(),
            _make_cases_agent(),
            _make_quality_loop(),
        ],
    )

    return LlmAgent(
        name="BuilderOrchestrator",
        model="gemini-2.5-pro",
        instruction="""You are the Builder Orchestrator.
You build premium websites from brand DNA. You know nothing about any specific brand.
You delegate to a pipeline of world-class specialist agents.

Delegate ALL tasks to BuilderPipeline:
  1. StructureAgent → studies DNA → decides page architecture
  2. DesignAgent → studies DNA visual principles → writes complete style.css
  3. HTMLAgent → reads DNA content + structure + CSS classes → writes complete index.html
  4. CasesAgent → reads DNA case studies → writes each portfolio case page
  5. QualityLoop → audits against DNA → fixes issues → repeats until score ≥ 8/10

After completion, report what was built and the final quality score.
""",
        sub_agents=[pipeline],
        before_agent_callback=dna_inject_callback,
        after_agent_callback=make_quality_scorer("orchestrator"),
    )


root_agent = build_root_agent()
