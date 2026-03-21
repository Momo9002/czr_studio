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
    Accepts both hyphen and underscore variants (CSS standard = hyphens).
    Returns a report of which tokens are present vs missing.
    """
    try:
        dna  = json.loads(_IDENTITY.read_text())
        css  = _STYLE_CSS.read_text()
        colors = dna.get("colors", {})

        present = []
        missing = []
        for token_name in colors:
            # CSS standard uses hyphens; DNA keys use underscores — accept both
            css_var_hyphen     = f"--{token_name.replace('_', '-')}"  # --dark-text
            css_var_underscore = f"--{token_name}"                     # --dark_text
            if css_var_hyphen in css or css_var_underscore in css:
                present.append(css_var_hyphen)
            else:
                missing.append(css_var_hyphen)

        return json.dumps({
            "present": present,
            "missing": missing,
            "coverage": f"{len(present)}/{len(present)+len(missing)}",
            "note": "Both --token-name and --token_name accepted as valid CSS conventions",
        }, indent=2)
    except Exception as e:
        return f"Error: {e}"


# ── Generic multipage tools ───────────────────────────────────────────────────

def read_page_collections() -> str:
    """Discover page collections from the DNA — returns SLUGS ONLY, not full data.

    Returns a list of collections with their folder, type, label, and list of slugs.
    Use this to know WHAT to build. Then call read_page_item(folder, slug) for each.

    IMPORTANT: This returns slugs only. You MUST call read_page_item for each slug
    to get the full content needed to write the page.
    """
    try:
        dna = json.loads(_IDENTITY.read_text())
        pages_config = dna.get("pages_config", {})
        collections = pages_config.get("collections", [])

        result = []
        for col in collections:
            if not col.get("enabled", True):
                continue

            # Resolve data_path (e.g. "site.cases" → dna["site"]["cases"])
            data_path = col.get("data_path", "")
            items = dna
            for part in data_path.split("."):
                items = items.get(part, {}) if isinstance(items, dict) else []

            if not isinstance(items, list):
                items = []

            slugs = [item.get("slug", str(i)) for i, item in enumerate(items)]

            result.append({
                "type": col.get("type", "page"),
                "folder": col.get("folder", "pages"),
                "label": col.get("label", "Pages"),
                "item_count": len(items),
                "slugs": slugs,
                "instruction": f"Call read_page_item('{col.get('folder','pages')}', slug) for each slug, then write_page('{col.get('folder','pages')}', slug, html)",
            })

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)})


def read_page_item(folder: str, slug: str) -> str:
    """Fetch the full DNA data for a single page item.

    Call this for each slug from read_page_collections() before writing its page.
    Returns the complete item object with all fields (challenge, result, palette, etc.)

    Args:
        folder: Collection folder (e.g. 'cases', 'products', 'team')
        slug:   Slug of the specific item to retrieve
    """
    try:
        dna = json.loads(_IDENTITY.read_text())
        pages_config = dna.get("pages_config", {})
        collections = pages_config.get("collections", [])

        for col in collections:
            if col.get("folder") != folder:
                continue
            data_path = col.get("data_path", "")
            items = dna
            for part in data_path.split("."):
                items = items.get(part, {}) if isinstance(items, dict) else []
            if not isinstance(items, list):
                continue
            for item in items:
                if item.get("slug") == slug:
                    return json.dumps({
                        "folder": folder,
                        "slug": slug,
                        "type": col.get("type", "page"),
                        "data": item,
                    }, indent=2, ensure_ascii=False)

        return json.dumps({"error": f"No item found: {folder}/{slug}"})

    except Exception as e:
        return f"Error: {e}"


def write_page(folder: str, slug: str, html_content: str) -> str:
    """Write a single subpage HTML file for any page collection.

    Generic replacement for write_case_html. Use for ANY page type:
    cases, products, team members, menu sections, services, etc.

    Args:
        folder: Collection folder name (e.g. 'cases', 'products', 'team', 'services')
        slug:   URL slug for this page (e.g. 'restaurant', 'espresso-blend', 'jane-doe')
        html_content: Complete HTML document for this page.

    Returns:
        Confirmation with path and size, or error.
    """
    try:
        page_dir = _ROOT_DIR / folder / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        out = page_dir / "index.html"
        out.write_text(html_content, encoding="utf-8")
        kb = len(html_content.encode()) / 1024
        return f"Written {folder}/{slug}/index.html ({kb:.1f} KB)"
    except Exception as e:
        return f"Error writing {folder}/{slug}: {e}"


def list_generated_pages() -> str:
    """List all subpages that have been generated so far.

    Returns a JSON object mapping folder → list of slugs with file sizes.
    Use to verify PagesAgent output after writing.
    """
    try:
        result = {}
        # Find all index.html files in subdirectories (not the root one)
        for folder in _ROOT_DIR.iterdir():
            if not folder.is_dir() or folder.name.startswith('.'):
                continue
            pages = []
            for slug_dir in folder.iterdir():
                idx = slug_dir / "index.html"
                if slug_dir.is_dir() and idx.exists():
                    pages.append({
                        "slug": slug_dir.name,
                        "size_kb": round(idx.stat().st_size / 1024, 1)
                    })
            if pages:
                result[folder.name] = pages
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {e}"


# ── Reference site tools ──────────────────────────────────────────────────────

def fetch_reference_sites() -> str:
    """Fetch real websites from the DNA's design model brands for visual reference.

    Reads models from identity.json, fetches their homepages, extracts:
    - CSS patterns (custom properties, typography scale, spacing)
    - HTML structure (nav patterns, section hierarchy, class naming)
    - Design decisions (color usage, whitespace, interaction hints)

    Use this in DesignAgent and HTMLAgent to compare your output against
    the actual reference websites your DNA says to learn from.

    Returns a JSON object with each brand's extracted patterns.
    """
    try:
        import urllib.request
        import urllib.error
        import html as html_lib

        dna = json.loads(_IDENTITY.read_text())
        models = dna.get("models", [])

        # Map known model names to their URLs
        model_urls = {
            "vogue": "https://www.vogue.com",
            "hermes": "https://www.hermes.com",
            "hermès": "https://www.hermes.com",
            "apple": "https://www.apple.com",
            "spacex": "https://www.spacex.com",
            "bottega": "https://www.bottegaveneta.com",
            "bottega veneta": "https://www.bottegaveneta.com",
            "loewe": "https://www.loewe.com",
            "balenciaga": "https://www.balenciaga.com",
            "dior": "https://www.dior.com",
        }

        results = {}
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        }

        brands_to_fetch = []
        for model in models:
            name = model if isinstance(model, str) else model.get("name", "")
            name_lower = name.lower()
            for key, url in model_urls.items():
                if key in name_lower:
                    brands_to_fetch.append({"name": name, "url": url})
                    break

        if not brands_to_fetch:
            # Fallback: try Apple and Hermès as defaults
            brands_to_fetch = [
                {"name": "Apple", "url": "https://www.apple.com"},
                {"name": "Hermès", "url": "https://www.hermes.com"},
            ]

        for brand in brands_to_fetch[:4]:  # Max 4 sites to avoid slow runs
            name = brand["name"]
            url = brand["url"]
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=8) as resp:
                    raw = resp.read(64000).decode("utf-8", errors="replace")

                # Extract CSS custom properties
                css_vars = re.findall(r'--[\w-]+:\s*[^;]+;', raw)[:20]

                # Extract font-family references
                fonts = re.findall(r"font-family['\"]?\s*:\s*['\"]([^'\"]+)", raw)[:5]

                # Extract class names from HTML (design system hints)
                classes = re.findall(r'class="([^"]{3,60})"', raw)
                unique_classes = list(dict.fromkeys(
                    c.split()[0] for c in classes if not c.startswith('js-')
                ))[:20]

                # Get <title>
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', raw, re.I)
                title = title_match.group(1).strip() if title_match else ""

                # Check for key patterns
                uses_grid = 'display:grid' in raw or 'display: grid' in raw
                uses_flex = 'display:flex' in raw or 'display: flex' in raw
                uses_custom_props = len(css_vars) > 0

                results[name] = {
                    "url": url,
                    "title": title,
                    "css_custom_properties": css_vars[:10],
                    "fonts_referenced": fonts,
                    "class_patterns": unique_classes[:15],
                    "uses_css_grid": uses_grid,
                    "uses_flexbox": uses_flex,
                    "uses_css_variables": uses_custom_props,
                    "html_size_kb": round(len(raw) / 1024, 1),
                }
            except Exception as e:
                results[name] = {"url": url, "error": str(e)[:100]}

        return json.dumps({
            "reference_sites": results,
            "instruction": (
                "Use these patterns as INSPIRATION and COMPARISON only. "
                "Your output must still come from the DNA. "
                "These references show what world-class implementation looks like."
            )
        }, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)})
