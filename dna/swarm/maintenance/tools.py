"""
dna/swarm/maintenance/tools.py — Maintenance Swarm Tools
Tools for auditing, updating, and deploying the live website.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_MAINT_DIR = Path(__file__).parent
_SWARM_DIR = _MAINT_DIR.parent
_DNA_DIR   = _SWARM_DIR.parent
_ROOT_DIR  = _DNA_DIR.parent
_IDENTITY  = _DNA_DIR / "identity.json"


def read_live_html() -> str:
    """Read the current live index.html for auditing against DNA."""
    try:
        return (_ROOT_DIR / "index.html").read_text()
    except Exception as e:
        return f"Error: {e}"


def read_dna_section(section: str) -> str:
    """Read a section from identity.json.

    Args:
        section: 'brand', 'voice', 'site', 'packages', 'cases', etc.
    """
    try:
        dna = json.loads(_IDENTITY.read_text())
        return json.dumps(dna.get(section, {}), indent=2)
    except Exception as e:
        return f"Error: {e}"


def read_dna_files() -> str:
    """Read vision.md, models.md, visual.md, voice.md."""
    parts = []
    for fname in ("vision.md", "models.md", "visual.md", "voice.md"):
        p = _DNA_DIR / fname
        if p.exists():
            parts.append(f"# {fname}\n\n{p.read_text()}")
    return "\n\n---\n\n".join(parts) or "No files."


def diff_dna_vs_html() -> str:
    """Compare DNA content (site copy) against what's actually in index.html.

    Returns a list of mismatches: copy in DNA that doesn't appear in the HTML.
    Use this to detect stale content that needs updating.
    """
    try:
        dna  = json.loads(_IDENTITY.read_text())
        html = (_ROOT_DIR / "index.html").read_text()
        site = dna.get("site", {})
        mismatches = []

        # Check headline
        hero = site.get("hero", {})
        headline = hero.get("headline", "")
        if headline and headline not in html:
            mismatches.append(f"Hero headline stale: DNA='{headline[:50]}' not in HTML")

        # Check brand tagline
        brand_tagline = dna.get("brand", {}).get("tagline", "")
        if brand_tagline and brand_tagline not in html:
            mismatches.append(f"Brand tagline stale: '{brand_tagline[:50]}'")

        # Check packages
        pkgs = dna.get("packages", {})
        for pkg_id, pkg in pkgs.items():
            price = str(pkg.get("price", ""))
            if price and price not in html:
                mismatches.append(f"Package '{pkg_id}' price {price} not in HTML")

        return json.dumps({
            "stale_count": len(mismatches),
            "mismatches": mismatches,
            "needs_rebuild": len(mismatches) > 0,
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


def audit_seo(filename: str = "index.html") -> str:
    """Audit SEO quality of index.html.

    Checks: title length, meta description, OG tags, canonical, schema,
    heading hierarchy, image alt attributes.

    Returns a scored SEO report.
    """
    try:
        html  = (_ROOT_DIR / filename).read_text()
        dna   = json.loads(_IDENTITY.read_text())
        issues = []
        score  = 10

        brand = dna.get("brand", {})

        # Title check
        import re
        title_match = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        if not title:
            issues.append("Missing <title> tag"); score -= 2
        elif len(title) < 30:
            issues.append(f"Title too short: '{title}' ({len(title)} chars, min 30)"); score -= 0.5
        elif len(title) > 65:
            issues.append(f"Title too long: {len(title)} chars, max 65"); score -= 0.5

        # Meta description
        desc_match = re.search(r'name="description"[^>]*content="([^"]+)"', html)
        if not desc_match:
            issues.append("Missing meta description"); score -= 1.5
        else:
            desc = desc_match.group(1)
            if len(desc) < 100:
                issues.append(f"Meta description too short: {len(desc)} chars"); score -= 0.5
            if len(desc) > 160:
                issues.append(f"Meta description too long: {len(desc)} chars"); score -= 0.5

        # OG tags
        for og in ["og:title", "og:description", "og:image"]:
            if f'property="{og}"' not in html:
                issues.append(f"Missing {og}"); score -= 0.5

        # Canonical
        if "canonical" not in html:
            issues.append("Missing canonical link"); score -= 0.5

        # H1 check
        h1s = re.findall(r"<h1[^>]*>", html)
        if len(h1s) == 0:
            issues.append("No h1 found"); score -= 1
        elif len(h1s) > 1:
            issues.append(f"Multiple h1 tags ({len(h1s)}) — should be exactly 1"); score -= 0.5

        # Image alt attributes
        imgs = re.findall(r"<img[^>]+>", html)
        missing_alt = [i for i in imgs if "alt=" not in i]
        if missing_alt:
            issues.append(f"{len(missing_alt)} image(s) missing alt attribute"); score -= 0.5

        return json.dumps({
            "seo_score": max(0, round(score, 1)),
            "max_score": 10,
            "issues": issues,
            "approved": score >= 8,
            "title": title,
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "seo_score": 0})


def trigger_builder_swarm(task: str = "Full rebuild") -> str:
    """Trigger the Builder Swarm to regenerate the website.

    Use this when diff_dna_vs_html() shows the site is stale,
    or when the SEO audit reveals structural issues that require a rebuild.

    Args:
        task: Task description for the Builder Swarm.

    Returns:
        Response from the Builder Swarm API, or error.
    """
    try:
        import httpx
        resp = httpx.post(
            "http://localhost:8902/run",
            json={"task": task, "user_id": "maintenance_swarm"},
            timeout=300,
        )
        return resp.json().get("result", resp.text)
    except Exception as e:
        return f"Builder Swarm unavailable: {e}. Rebuild must be triggered manually."


def run_deploy() -> str:
    """Run the production deploy script to push changes to production.

    Only call this after a successful build and quality audit.
    Returns deploy output (rsync + cache purge result).
    """
    deploy_script = _ROOT_DIR / "deploy.sh"
    if not deploy_script.exists():
        return "deploy.sh not found — deploy manually or check /deploy workflow"
    try:
        result = subprocess.run(
            ["bash", str(deploy_script)],
            capture_output=True, text=True,
            cwd=str(_ROOT_DIR), timeout=120,
        )
        return result.stdout.strip() or result.stderr.strip() or "Deploy completed"
    except Exception as e:
        return f"Deploy error: {e}"
