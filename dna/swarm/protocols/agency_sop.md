# Elite Digital Agency: Standard Operating Procedure (SOP)

This document outlines the professional methodology used by world-class digital agencies to produce premium websites. All swarm agents must adhere to this framework when generating output.

## Phase 1: Strategy & Architecture (StructureAgent)
- **Objective:** Define the blueprint. A website is a digital product, not a brochure.
- **Rule 1: Content-First Design.** Never design a layout without knowing the content it must hold. Read the DNA thoroughly.
- **Rule 2: The Narrative Arc.** A homepage must tell a story. 
  - *Top:* The Hook (Hero) - What is it?
  - *Middle:* The Proof (Cases/Products) - Why trust us?
  - *Bottom:* The Action (CTA) - What next?
- **Rule 3: Modularity.** Design sections as reusable components (dark/light alternations, grids, stacks).

## Phase 2: Design System & UI (DesignAgent)
- **Objective:** Create the visual language before writing structural HTML.
- **Rule 1: Tokens First.** Define all colors, typography, and spacing as CSS Custom Properties (`:root`).
- **Rule 2: The 8pt Grid.** All spacing (margins, padding) MUST be multiples of 8px (0.5rem) or use fluid `clamp()` functions for responsiveness.
- **Rule 3: Micro-interactions.** Premium sites feel "alive." Implement subtle hover states, smooth transitions, and focus styling.
- **Rule 4: Semantic CSS.** Avoid utility classes (`.mt-4`, `.text-red`). Write semantic component classes (`.hero`, `.nav`, `.card`).

## Phase 3: Development & Code (HTMLAgent / PagesAgent)
- **Objective:** Translate the architecture and design system into flawless markup.
- **Rule 1: Semantic HTML5.** Use `<header>`, `<main>`, `<section>`, `<article>`, `<nav>`, and `<footer>` appropriately. Never use a `<div>` when a semantic tag exists.
- **Rule 2: Accessibility (a11y).** 
  - All images MUST have descriptive `alt` attributes.
  - Buttons and links MUST have recognizable focus states.
  - Color contrast must meet WCAG AA standards.
- **Rule 3: SEO Foundation.** 
  - Every page must have exactly ONE `<h1>`.
  - Proper heading hierarchy (`<h1>` down to `<h2>`, `<h3>`).
  - Meta description and Open Graph tags required.

## Phase 4: Quality Assurance (QualityLoop)
- **Objective:** Rigorous internal audit before deployment.
- **Rule 1: Zero Tolerance.** If a CSS token is missing, or an HTML tag is unclosed, the build fails.
- **Rule 2: DNA Compliance Check.** The output must perfectly reflect the client's provided DNA.

By following this SOP, you elevate your output from standard generation to professional agency implementation.
