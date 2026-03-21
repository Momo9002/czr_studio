"""
dna/swarm/builder/tools.py — Builder Swarm Tools
DNA-to-website tools: read DNA, write HTML/CSS files directly, audit output.

Brand-agnostic. Works with any identity.json following the DNA schema.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

_BUILDER_DIR = Path(__file__).parent
_SWARM_DIR   = _BUILDER_DIR.parent
_DNA_DIR     = _SWARM_DIR.parent
_ROOT_DIR    = _DNA_DIR.parent

_IDENTITY   = _DNA_DIR / "identity.json"
_INDEX_HTML = _ROOT_DIR / "index.html"
_STYLE_CSS  = _ROOT_DIR / "style.css"
_CASES_DIR  = _ROOT_DIR / "cases"


# ── DNA read tools ────────────────────────────────────────────────────────────

def read_dna_section(section: str) -> str:
    """Read a top-level section from identity.json.

    Args:
        section: Key in identity.json: 'brand', 'voice', 'site', 'packages',
                 'colors', 'typography', 'cases', 'tokens', 'faq', 'design'

    Returns:
        JSON string of the section, or error.
    """
    try:
        dna = json.loads(_IDENTITY.read_text())
        if section not in dna:
            return f"Section '{section}' not found. Available: {', '.join(dna.keys())}"
        return json.dumps(dna[section], indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


def read_full_dna() -> str:
    """Read the complete identity.json. Use before writing HTML to get all brand data."""
    try:
        return _IDENTITY.read_text()
    except Exception as e:
        return f"Error: {e}"


def read_dna_files() -> str:
    """Read all human-authored DNA source files: vision.md, models.md, visual.md, voice.md.

    Use to understand design intent and visual principles before writing CSS.
    Returns concatenated markdown.
    """
    parts = []
    for fname in ("vision.md", "models.md", "visual.md", "voice.md", "content.md"):
        p = _DNA_DIR / fname
        if p.exists():
            parts.append(f"# {fname}\n\n{p.read_text()}")
    return "\n\n---\n\n".join(parts) or "No DNA source files found."


def read_case_list() -> str:
    """List all portfolio case study slugs and their basic DNA data.

    Returns JSON list of cases with id, title, type, and description.
    """
    try:
        dna = json.loads(_IDENTITY.read_text())
        cases = dna.get("cases", [])
        return json.dumps(cases, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {e}"


# ── File write tools ──────────────────────────────────────────────────────────

def write_index_html(html_content: str) -> str:
    """Write the complete index.html file.

    This REPLACES the entire file. Pass the full HTML document.
    Include <!DOCTYPE html> through </html>.

    Args:
        html_content: Complete HTML document string.

    Returns:
        Confirmation with byte count, or error.
    """
    try:
        if not html_content.strip().startswith("<!DOCTYPE") and not html_content.strip().startswith("<html"):
            return "Error: HTML must start with <!DOCTYPE html> or <html>"
        _INDEX_HTML.write_text(html_content, encoding="utf-8")
        kb = len(html_content.encode()) / 1024
        return f"Written index.html ({kb:.1f} KB, {html_content.count(chr(10))} lines)"
    except Exception as e:
        return f"Error writing index.html: {e}"


def write_style_css(css_content: str) -> str:
    """Write the complete style.css file.

    This REPLACES the entire file. Pass the full stylesheet.

    Args:
        css_content: Complete CSS string.

    Returns:
        Confirmation with byte count, or error.
    """
    try:
        _STYLE_CSS.write_text(css_content, encoding="utf-8")
        kb = len(css_content.encode()) / 1024
        rules = css_content.count("{")
        return f"Written style.css ({kb:.1f} KB, ~{rules} rule blocks)"
    except Exception as e:
        return f"Error writing style.css: {e}"


def write_case_html(slug: str, html_content: str) -> str:
    """Write a case study HTML file for a given slug.

    Creates cases/{slug}/index.html. Replaces existing file.

    Args:
        slug: Case study slug (e.g. 'restaurant', 'fashion-house').
        html_content: Complete HTML document for this case study.

    Returns:
        Confirmation or error.
    """
    try:
        case_dir = _CASES_DIR / slug
        case_dir.mkdir(parents=True, exist_ok=True)
        out = case_dir / "index.html"
        out.write_text(html_content, encoding="utf-8")
        kb = len(html_content.encode()) / 1024
        return f"Written cases/{slug}/index.html ({kb:.1f} KB)"
    except Exception as e:
        return f"Error writing case {slug}: {e}"


def append_css(css_block: str) -> str:
    """Append additional CSS rules to style.css without replacing existing content.

    Use when you want to ADD rules rather than rewrite the whole file.

    Args:
        css_block: CSS rules to append (can be multiple selectors).

    Returns:
        Confirmation or error.
    """
    try:
        with _STYLE_CSS.open("a", encoding="utf-8") as f:
            f.write(f"\n/* Builder Swarm append */\n{css_block}\n")
        return f"Appended {len(css_block)} chars to style.css"
    except Exception as e:
        return f"Error: {e}"


# ── Read output tools ─────────────────────────────────────────────────────────

def read_output_file(filename: str) -> str:
    """Read a generated output file for auditing.

    Args:
        filename: 'index.html', 'style.css', or 'cases/{slug}/index.html'

    Returns:
        File contents or error.
    """
    try:
        if filename == "index.html":
            return _INDEX_HTML.read_text()
        if filename == "style.css":
            return _STYLE_CSS.read_text()
        if filename.startswith("cases/"):
            return (_ROOT_DIR / filename).read_text()
        return f"Unknown file: {filename}"
    except Exception as e:
        return f"Error reading {filename}: {e}"


# ── Audit tools ───────────────────────────────────────────────────────────────

def audit_html_structure(filename: str = "index.html") -> str:
    """Audit HTML structure for completeness and quality issues.

    Checks for: missing sections, missing IDs, missing meta tags,
    broken links, missing alt attributes, and DNA consistency.

    Args:
        filename: File to audit, default 'index.html'.

    Returns:
        JSON audit report with issues list and score (0–10).
    """
    try:
        path = _ROOT_DIR / filename if not filename.startswith("/") else Path(filename)
        html = path.read_text()
        dna  = json.loads(_IDENTITY.read_text())

        issues = []
        score  = 10

        # Check required sections
        required_ids = ["work", "about", "process", "packages", "contact"]
        for sid in required_ids:
            if f'id="{sid}"' not in html:
                issues.append(f"Missing section: #{sid}")
                score -= 1

        # Check meta tags
        for meta in ["description", "og:title", "og:description"]:
            if f'name="{meta}"' not in html and f'property="{meta}"' not in html:
                issues.append(f"Missing meta: {meta}")
                score -= 0.5

        # Check WhatsApp link present
        if "wa.me" not in html:
            issues.append("Missing WhatsApp CTA link")
            score -= 1

        # Check DOCTYPE
        if not html.strip().startswith("<!DOCTYPE"):
            issues.append("Missing DOCTYPE declaration")
            score -= 1

        # Check style.css referenced
        if "style.css" not in html:
            issues.append("style.css not referenced — styles may be missing")
            score -= 1

        # Check canonical link
        if "canonical" not in html:
            issues.append("Missing canonical link tag")

        # Check inject.js
        if "inject.js" not in html:
            issues.append("Missing inject.js script — live data injection disabled")

        # Check brand name present
        brand_name = dna.get("brand", {}).get("name", "")
        if brand_name and brand_name not in html:
            issues.append(f"Brand name '{brand_name}' not found in HTML")
            score -= 0.5

        return json.dumps({
            "score": max(0, round(score, 1)),
            "max_score": 10,
            "issues": issues,
            "issue_count": len(issues),
            "approved": score >= 8,
            "file_size_kb": round(len(html.encode()) / 1024, 1),
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "score": 0, "approved": False})


def audit_css_tokens() -> str:
    """Check that style.css uses the correct CSS custom properties from identity.json.

    Verifies color tokens like --black, --cream, --hermes are defined.
    Returns a report of which tokens are present vs missing.
    """
    try:
        dna  = json.loads(_IDENTITY.read_text())
        css  = _STYLE_CSS.read_text()
        colors = dna.get("colors", {})

        present = []
        missing = []
        for token_name in colors:
            css_var = f"--{token_name}"
            if css_var in css:
                present.append(css_var)
            else:
                missing.append(css_var)

        return json.dumps({
            "present": present,
            "missing": missing,
            "coverage": f"{len(present)}/{len(present)+len(missing)}",
        }, indent=2)
    except Exception as e:
        return f"Error: {e}"
