"""
dna/swarm/tools.py — Website Builder Swarm Tools
Generic ADK tool functions: read DNA, write DNA patches, run builder.

These tools are brand-agnostic. They work with ANY identity.json
that follows the standard DNA schema.

ADK tool rules:
  - Plain Python functions only (no classes)
  - Return plain dicts or strings
  - Docstring = tool description visible to the LLM
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# ── Path resolution ───────────────────────────────────────────────────────────
# Tools are called from any working directory — resolve relative to this file.
_SWARM_DIR = Path(__file__).parent
_DNA_DIR   = _SWARM_DIR.parent
_ROOT_DIR  = _DNA_DIR.parent


def _identity_path() -> Path:
    return _DNA_DIR / "identity.json"


def _load_dna() -> dict:
    return json.loads(_identity_path().read_text())


def _save_dna(dna: dict) -> None:
    _identity_path().write_text(json.dumps(dna, indent=2, ensure_ascii=False))


# ── Read tools ────────────────────────────────────────────────────────────────

def read_dna_section(section: str) -> str:
    """Read a top-level section from identity.json and return it as JSON string.

    Args:
        section: Top-level key in identity.json (e.g. 'site', 'brand', 'voice',
                 'packages', 'colors', 'typography', 'faq', 'design', 'tokens').

    Returns:
        JSON string of the section value, or an error message if not found.
    """
    try:
        dna = _load_dna()
        if section not in dna:
            available = ", ".join(dna.keys())
            return f"Section '{section}' not found. Available: {available}"
        return json.dumps(dna[section], indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error reading DNA: {e}"


def read_full_dna() -> str:
    """Read the complete identity.json and return as JSON string.

    Use this to get a full picture of the brand DNA before making decisions.
    Returns the entire identity.json as a JSON string.
    """
    try:
        return _identity_path().read_text()
    except Exception as e:
        return f"Error reading DNA: {e}"


def read_dna_files() -> str:
    """Read the human-authored DNA source files: vision.md, models.md, visual.md.

    Returns a concatenated markdown string with all three files.
    Use this to understand the INTENT behind the DNA, not just the data.
    """
    result = []
    for fname in ("vision.md", "models.md", "visual.md", "voice.md"):
        path = _DNA_DIR / fname
        if path.exists():
            result.append(f"# {fname}\n\n{path.read_text()}")
    return "\n\n---\n\n".join(result) if result else "No DNA source files found."


# ── Write tools ───────────────────────────────────────────────────────────────

def patch_dna_site(patch_json: str) -> str:
    """Apply a partial update to the 'site' block in identity.json.

    Performs a deep merge — only the keys you provide are updated.
    Existing keys not in the patch are preserved.

    Args:
        patch_json: JSON string of fields to update in the site block.
            Example: '{"hero": {"headline": "New headline."}, "sections_order": [...]}'

    Returns:
        Summary of applied changes, or error message.
    """
    try:
        patch = json.loads(patch_json)
    except json.JSONDecodeError as e:
        return f"Invalid JSON patch: {e}"

    try:
        dna = _load_dna()
        site = dna.setdefault("site", {})
        applied = []

        # Deep merge for dict values, direct replace for lists/scalars
        for key, val in patch.items():
            if isinstance(val, dict) and isinstance(site.get(key), dict):
                for subkey, subval in val.items():
                    if site[key].get(subkey) != subval:
                        site[key][subkey] = subval
                        applied.append(f"site.{key}.{subkey}")
            else:
                if site.get(key) != val:
                    site[key] = val
                    applied.append(f"site.{key}")

        if not applied:
            return "No changes needed — DNA already matches patch."

        _save_dna(dna)
        return f"Applied {len(applied)} changes: {', '.join(applied)}"

    except Exception as e:
        return f"Error patching DNA: {e}"


def patch_dna_packages(patch_json: str) -> str:
    """Update the packages block in identity.json (sprint, flagship, retainer pricing/taglines).

    Args:
        patch_json: JSON string with package updates.
            Example: '{"flagship": {"tagline": "A complete digital flagship."}}'

    Returns:
        Summary of changes applied, or error message.
    """
    try:
        patch = json.loads(patch_json)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"

    try:
        dna = _load_dna()
        pkgs = dna.setdefault("packages", {})
        applied = []

        for pkg_name, fields in patch.items():
            if not isinstance(fields, dict):
                continue
            target = pkgs.setdefault(pkg_name, {})
            for k, v in fields.items():
                if target.get(k) != v:
                    target[k] = v
                    applied.append(f"packages.{pkg_name}.{k}")

        if applied:
            _save_dna(dna)
        return f"Applied {len(applied)} changes: {', '.join(applied)}" if applied else "No changes."

    except Exception as e:
        return f"Error: {e}"


def validate_dna_voice(text_to_check: str) -> str:
    """Check a block of text against the DNA voice rules (banned words, tone).

    Args:
        text_to_check: Any text content to validate (copy, headlines, CTAs).

    Returns:
        JSON string: {"approved": bool, "violations": [...], "suggestions": [...]}
    """
    try:
        dna = _load_dna()
        voice = dna.get("voice", {})
        banned = voice.get("never", [])
        violations = []
        text_lower = text_to_check.lower()

        for word in banned:
            if word.lower() in text_lower:
                violations.append(f"Banned word used: '{word}'")

        if "!" in text_to_check:
            violations.append("Exclamation mark used — never use exclamations")

        # Check for AI mentions
        ai_terms = ["ai", "artificial intelligence", "machine learning", "automation", "algorithm"]
        for term in ai_terms:
            if term in text_lower:
                violations.append(f"AI reference found: '{term}' — technology must be invisible")

        return json.dumps({
            "approved": len(violations) == 0,
            "violations": violations,
            "violation_count": len(violations),
        }, indent=2)

    except Exception as e:
        return json.dumps({"approved": False, "violations": [f"Error: {e}"]})


# ── Build tools ───────────────────────────────────────────────────────────────

def build_website(dry_run: bool = False) -> str:
    """Run the website builder to regenerate index.html from the current identity.json.

    Args:
        dry_run: If True, reports what would be built without writing files.

    Returns:
        Build output (success message with byte count, or error details).
    """
    try:
        cmd = [sys.executable, "-m", "dna.build"]
        if dry_run:
            cmd.append("--dry")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(_ROOT_DIR),
            timeout=30,
        )
        output = result.stdout.strip() + (f"\nSTDERR: {result.stderr.strip()}" if result.stderr else "")
        return output if output else "Build completed (no output)"

    except subprocess.TimeoutExpired:
        return "Error: Build timed out after 30s"
    except Exception as e:
        return f"Error running builder: {e}"


def build_case_studies(slug: str = "") -> str:
    """Run the case study builder to regenerate case HTML pages from identity.json.

    Args:
        slug: Optional — rebuild only this case study (e.g. 'restaurant').
              Leave empty to rebuild all case studies.

    Returns:
        Build output listing all rebuilt pages, or error details.
    """
    try:
        cmd = [sys.executable, "-m", "dna.cases_builder"]
        if slug:
            cmd += ["--slug", slug]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(_ROOT_DIR),
            timeout=60,
        )
        output = result.stdout.strip() + (f"\nSTDERR: {result.stderr.strip()}" if result.stderr else "")
        return output if output else "Case build completed (no output)"

    except Exception as e:
        return f"Error: {e}"


def run_dna_sync_audit(dry_run: bool = True) -> str:
    """Run the DNA sync audit pipeline to check for inconsistencies.

    Args:
        dry_run: If True (default), only reports without modifying files.

    Returns:
        Full audit output with pass/warning/fail counts.
    """
    try:
        cmd = [sys.executable, "-m", "dna.sync"]
        if dry_run:
            cmd.append("--dry")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(_ROOT_DIR),
            timeout=120,
        )
        return result.stdout.strip() or result.stderr.strip() or "Sync completed."

    except Exception as e:
        return f"Error: {e}"


# ── Design / file tools ───────────────────────────────────────────────────────

import re as _re

_ALLOWED_FILES = {
    "style.css": _ROOT_DIR / "style.css",
    "build.py":  _DNA_DIR  / "build.py",
}


def read_project_file(filename: str) -> str:
    """Read style.css or build.py and return its full contents.

    Use this before making design changes to understand the current state.

    Args:
        filename: 'style.css' or 'build.py'
    """
    path = _ALLOWED_FILES.get(filename)
    if path is None:
        return f"Not allowed. Use one of: {', '.join(_ALLOWED_FILES)}"
    try:
        return path.read_text()
    except Exception as e:
        return f"Error: {e}"


def write_css_rule(selector: str, properties: str) -> str:
    """Append a new CSS rule block to style.css.

    Use this to ADD new rules — appended rules naturally override earlier ones.
    For modifying existing rules, use replace_css_block().

    Args:
        selector: CSS selector, e.g. '.hero-inner' or '.about-stat-value'
        properties: CSS property declarations (no braces), e.g. 'font-size: clamp(4rem,8vw,7rem); font-weight:800;'

    Returns:
        Confirmation or error.
    """
    path = _ALLOWED_FILES["style.css"]
    try:
        rule = f"\n/* DesignAgent */\n{selector} {{\n  {properties}\n}}\n"
        with path.open("a") as f:
            f.write(rule)
        return f"Added CSS rule for '{selector}'"
    except Exception as e:
        return f"Error: {e}"


def replace_css_block(target_selector: str, new_properties: str) -> str:
    """Replace an existing CSS rule block in style.css.

    Finds the first matching selector and replaces its property block.

    Args:
        target_selector: Exact selector string, e.g. '.about-stat-value'
        new_properties: New declarations (no braces), e.g. 'font-size: clamp(3rem,6vw,5rem);'

    Returns:
        Confirmation or error.
    """
    path = _ALLOWED_FILES["style.css"]
    try:
        css = path.read_text()
        pattern = _re.compile(
            r'(' + _re.escape(target_selector) + r'\s*\{)[^}]*(\})',
            _re.DOTALL
        )
        if not pattern.search(css):
            return f"Selector '{target_selector}' not found. Use write_css_rule() to add it."
        new_css = pattern.sub(
            f"{target_selector} {{\n  {new_properties}\n}}",
            css, count=1
        )
        path.write_text(new_css)
        return f"Replaced CSS block for '{target_selector}'"
    except Exception as e:
        return f"Error: {e}"


def get_current_css_variables() -> str:
    """Read the CSS custom properties (design tokens) currently active in style.css.

    Returns the :root block so the DesignAgent knows what variables are available.
    """
    path = _ALLOWED_FILES["style.css"]
    try:
        css = path.read_text()
        match = _re.search(r':root\s*\{[^}]+\}', css, _re.DOTALL)
        return match.group(0) if match else "No :root block found."
    except Exception as e:
        return f"Error: {e}"
