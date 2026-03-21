"""
CZR Studio — DNA Sync
One command to propagate DNA changes across the full pipeline.

Checks:
  1. Validate identity.json
  2. Load dna.loader constants
  3. Sync CSS variables in style.css
  4. Check Google Fonts in index.html
  5. Run brand guard tests
  6. Verify Python import chain
  7. Audit campaign content (captions pass brand guard, hashtags match DNA)
  8. Audit agent tone (banned words, voice rules)
  9. Audit production sites (Knight watermark, fonts, Meta pixel)

Usage:
    python3 -m dna.sync          # full sync + audit
    python3 -m dna.sync --dry    # show what would change without writing
    python3 -m dna.sync --audit  # only run audits, skip CSS sync
"""

import json
import re
import sys
import glob
from pathlib import Path

_ROOT = Path(__file__).parent.parent
_DNA_DIR = _ROOT / "dna"
_STYLE_CSS = _ROOT / "style.css"

_PASS = 0
_WARN = 0
_FAIL = 0


def _ok(msg: str):
    global _PASS; _PASS += 1; print(f"   ✅ {msg}")

def _warn(msg: str):
    global _WARN; _WARN += 1; print(f"   ⚠️  {msg}")

def _fail(msg: str):
    global _FAIL; _FAIL += 1; print(f"   ❌ {msg}")


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1: Validate identity.json
# ══════════════════════════════════════════════════════════════════════════════

def validate_identity() -> dict:
    print("1️⃣  Validating dna/identity.json...")
    path = _DNA_DIR / "identity.json"
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        _fail(f"Invalid JSON: {e}")
        sys.exit(1)

    required = ["brand", "colors", "typography", "voice", "hashtags"]
    missing = [k for k in required if k not in data]
    if missing:
        _fail(f"Missing required keys: {missing}")
        sys.exit(1)

    _ok(f"Valid — {len(data)} top-level keys")
    return data


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 2: Load and verify the loader
# ══════════════════════════════════════════════════════════════════════════════

def verify_loader():
    print("\n2️⃣  Loading dna.loader...")
    try:
        from dna.loader import (
            BRAND_NAME, TAGLINE, COLORS, BANNED_WORDS, SITE_URL,
            PACKAGES, FAQ, HASHTAGS,
        )
        checks = {
            "BRAND_NAME": bool(BRAND_NAME),
            "COLORS": len(COLORS) >= 4,
            "BANNED_WORDS": len(BANNED_WORDS) >= 5,
            "SITE_URL": SITE_URL.startswith("http"),
            "HASHTAGS": len(HASHTAGS) >= 5,
        }
        for name, ok in checks.items():
            (_ok if ok else _warn)(name)
    except Exception as e:
        _fail(f"Loader import failed: {e}")
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3: Sync CSS variables
# ══════════════════════════════════════════════════════════════════════════════

def sync_css(dna: dict, dry: bool = False) -> int:
    print(f"\n3️⃣  {'[DRY RUN] ' if dry else ''}Syncing style.css...")
    css = _STYLE_CSS.read_text()
    changes = 0

    color_map = {
        "--czr-black":     dna["colors"].get("black", "#000000"),
        "--czr-cream":     dna["colors"].get("cream", "#F7F4EF"),
        "--czr-white":     dna["colors"].get("white", "#FFFFFF"),
        "--czr-red":       dna["colors"].get("red", "#C8242A"),
        "--czr-surface":   dna["colors"].get("surface", "#080808"),
        "--czr-surface-2": dna["colors"].get("surface2", "#0f0f0f"),
        "--czr-gold":      dna["colors"].get("gold", "#C9A84C"),
    }

    for var_name, dna_value in color_map.items():
        pattern = rf"({re.escape(var_name)}:\s*)#[0-9a-fA-F]{{3,8}}"
        match = re.search(pattern, css)
        if match:
            current = re.search(r"#[0-9a-fA-F]{3,8}", match.group(0)).group(0)
            if current.lower() != dna_value.lower():
                print(f"   🔄 {var_name}: {current} → {dna_value}")
                css = re.sub(pattern, rf"\g<1>{dna_value}", css, count=1)
                changes += 1
            else:
                _ok(f"{var_name}: {current}")
        else:
            _warn(f"{var_name} not found in CSS")

    typo = dna.get("typography", {})
    for var_name, font in [("--font-display", typo.get("display", "Syne")),
                           ("--font-body", typo.get("body", "Manrope"))]:
        pattern = rf"({re.escape(var_name)}:\s*')([^']+?)'"
        match = re.search(pattern, css)
        if match:
            current = match.group(2)
            if current != font:
                print(f"   🔄 {var_name}: '{current}' → '{font}'")
                css = re.sub(pattern, rf"\g<1>{font}'", css, count=1)
                changes += 1
            else:
                _ok(f"{var_name}: '{current}'")

    if changes and not dry:
        _STYLE_CSS.write_text(css)
        print(f"\n   📝 Wrote {changes} change(s) to style.css")
    elif changes:
        print(f"\n   📝 {changes} change(s) would be written (dry run)")
    else:
        _ok("CSS already in sync")

    return changes


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 4: Check Google Fonts link
# ══════════════════════════════════════════════════════════════════════════════

def sync_fonts_link(dna: dict):
    print(f"\n4️⃣  Checking index.html fonts link...")
    html_path = _ROOT / "index.html"
    if not html_path.exists():
        _warn("index.html not found")
        return
    html = html_path.read_text()
    display = dna.get("typography", {}).get("display", "Syne")
    body = dna.get("typography", {}).get("body", "Manrope")
    if display in html and body in html:
        _ok(f"Fonts present: {display}, {body}")
    else:
        _warn(f"Font mismatch — DNA says {display} + {body}")


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 5: Brand guard tests
# ══════════════════════════════════════════════════════════════════════════════

def run_brand_guard():
    print("\n5️⃣  Running brand guard tests...")
    from api.content_templates import brand_guard
    tests = [
        ("One table. Twelve guests. Monaco.", "instagram", True),
        ("We leverage AI to disrupt web design", "instagram", False),
        ("Amazing 🚀🔥💯🎯✨ launch!", "instagram", False),
        ("Visit czrstudio.com", "linkedin", False),
        ("Three agencies. Six weeks each.\n\n→ czr.studio", "linkedin", True),
    ]
    for caption, platform, expected in tests:
        result, reason = brand_guard(caption, platform)
        if result == expected:
            _ok(f"{platform}: {caption[:40]}...")
        else:
            _fail(f"{platform}: expected {expected}, got {result} — {reason}")


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 6: Import chain check
# ══════════════════════════════════════════════════════════════════════════════

def check_imports():
    print("\n6️⃣  Checking import chain...")
    for name in ["dna.loader", "agents.knowledge", "api.content_templates"]:
        try:
            __import__(name)
            _ok(name)
        except Exception as e:
            _fail(f"{name}: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 7: Audit marketing content
# ══════════════════════════════════════════════════════════════════════════════

# Industry hashtags allowed (from content.md)
_INDUSTRY_HASHTAGS = {
    "#FashionWebDesign", "#LuxuryFashion", "#EditorialDesign",
    "#ArchitectureWebDesign", "#MinimalDesign", "#BrutalArchitecture",
    "#RestaurantWebDesign", "#HospitalityDesign", "#FineDining",
    "#EcommerceDesign", "#BeautyBranding", "#ProductDesign",
    "#PhotographerWebsite", "#PortfolioDesign", "#VisualArts",
    "#CreativeDirection", "#PersonalBrand", "#DesignPortfolio",
}


def audit_marketing():
    print("\n7️⃣  Auditing marketing content (STRICT)...")
    from api.content_templates import brand_guard
    from dna.loader import HASHTAGS

    campaign_files = list(_ROOT.glob("*.json")) + list(_ROOT.glob("data/*.json"))
    campaign_files = [f for f in campaign_files if "campaign" in f.name.lower()]

    if not campaign_files:
        _warn("No campaign JSON files found")
        return

    dna_hashtags = set(HASHTAGS)
    all_hashtags = dna_hashtags | _INDUSTRY_HASHTAGS
    seen_openers = []  # track first lines for uniqueness

    for cf in campaign_files:
        try:
            data = json.loads(cf.read_text())
        except Exception:
            _fail(f"Can't parse {cf.name}")
            continue

        posts = data.get("posts", [])
        if not posts:
            continue

        print(f"   📄 {cf.name} — {len(posts)} posts")
        for post in posts:
            pid = post.get("id", "?")
            caption = post.get("caption", "")
            platform = post.get("platform", "instagram")

            # Brand guard (STRICT — fail, not warn)
            passes, reason = brand_guard(caption, platform)
            if not passes:
                _fail(f"  {pid}: {reason}")
            else:
                _ok(f"  {pid}: brand guard")

            # Hashtag check (Instagram only) — allow DNA + industry hashtags
            if platform == "instagram":
                caption_tags = set(re.findall(r"#\w+", caption))
                unknown = caption_tags - all_hashtags
                if unknown:
                    _fail(f"  {pid}: unknown hashtags (not in DNA or industry list): {unknown}")

            # CTA check (STRICT)
            if "czr.studio" not in caption and "Link in bio" not in caption:
                _fail(f"  {pid}: missing CTA (→ czr.studio or Link in bio)")

            # Uniqueness check — first line should be unique across all posts
            first_line = caption.strip().split("\n")[0].strip()
            if first_line in seen_openers:
                _warn(f"  {pid}: duplicate opening line: '{first_line[:40]}'")
            seen_openers.append(first_line)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 8: Audit agent tone
# ══════════════════════════════════════════════════════════════════════════════

def audit_agent_tone():
    print("\n8️⃣  Auditing agent tone...")
    from dna.loader import BANNED_WORDS, BRAND_NAME, VOICE_NEVER

    agent_files = list((_ROOT / "agents" / "phases").glob("*.py"))
    agent_files.append(_ROOT / "agents" / "knowledge.py")
    agent_files.append(_ROOT / "api" / "concierge.py")

    for af in agent_files:
        if af.name.startswith("__"):
            continue
        try:
            content = af.read_text().lower()
        except Exception:
            continue

        issues = []

        # Check for banned words in hardcoded strings (not in variable names)
        for word in BANNED_WORDS:
            if word.lower() in ("!", "we can"):
                continue  # These are too common in code
            # Only flag if it appears in a string literal
            if f'"{word.lower()}"' in content or f"'{word.lower()}'" in content:
                issues.append(f"contains banned word: '{word}'")

        # Check brand name is correct (not hardcoded wrong)
        for wrong in ["czrstudio", "czr-studio", "czrstudio.com"]:
            if wrong in content:
                issues.append(f"wrong brand reference: '{wrong}'")

        if issues:
            for issue in issues:
                _fail(f"  {af.name}: {issue}")
        else:
            _ok(f"  {af.name}: tone OK")


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 9: Audit production sites (cases/)
# ══════════════════════════════════════════════════════════════════════════════

def audit_production():
    print("\n9️⃣  Auditing production sites (STRICT)...")
    from dna.loader import FONT_DISPLAY, FONT_BODY, AVATAR_SYMBOL

    cases_dir = _ROOT / "cases"
    if not cases_dir.exists():
        _warn("cases/ directory not found")
        return

    case_pages = list(cases_dir.glob("*/index.html"))
    if not case_pages:
        _warn("No case study pages found")
        return

    seen_fonts = set()  # track fonts across sites for differentiation
    seen_palettes = []  # track color use for differentiation

    for page in case_pages:
        slug = page.parent.name
        html = page.read_text()
        ok_items = []

        # ── HARD REQUIREMENTS (fail) ──

        # CZR credit (HARD FAIL)
        has_credit = ("CZR" in html or "czr.studio" in html or "Built by CZR" in html)
        if has_credit:
            ok_items.append("CZR credit")
        else:
            _fail(f"  {slug}: MISSING CZR credit / watermark")

        # Meta Pixel (HARD FAIL)
        if "fbq(" in html or "facebook.net" in html or "Meta Pixel" in html:
            ok_items.append("Meta Pixel")
        else:
            _fail(f"  {slug}: MISSING Meta Pixel")

        # Responsive viewport (HARD FAIL)
        if "viewport" in html:
            ok_items.append("viewport")
        else:
            _fail(f"  {slug}: MISSING viewport meta tag")

        # Has some font loaded (HARD FAIL)
        has_fonts = "fonts.googleapis.com" in html or "font-family" in html
        if has_fonts:
            ok_items.append("fonts")
        else:
            _fail(f"  {slug}: NO font definitions found")

        # ── DIFFERENTIATION CHECKS (warn) ──

        # Extract font families used
        font_matches = re.findall(r"family=([^&'\"]+)", html)
        site_fonts = frozenset(f.replace("+", " ") for f in font_matches)
        if site_fonts and site_fonts in seen_fonts:
            _warn(f"  {slug}: same font combo as another case study — needs its own typography")
        if site_fonts:
            seen_fonts.add(site_fonts)

        # Check that it links back to CZR
        if "czr.studio" in html or "index.html" in html:
            ok_items.append("CZR link")

        if ok_items:
            _ok(f"  {slug}: {', '.join(ok_items)}")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    global _PASS, _WARN, _FAIL
    dry = "--dry" in sys.argv
    audit_only = "--audit" in sys.argv

    print("=" * 60)
    title = "CZR DNA SYNC"
    if dry:
        title += " — DRY RUN"
    if audit_only:
        title += " — AUDIT ONLY"
    print(title)
    print("=" * 60)

    dna = validate_identity()
    verify_loader()

    if not audit_only:
        sync_css(dna, dry=dry)

    sync_fonts_link(dna)
    run_brand_guard()
    check_imports()

    # Extended pipeline audits
    audit_marketing()
    audit_agent_tone()
    audit_production()

    # Summary
    print("\n" + "=" * 60)
    print(f"  ✅ {_PASS} passed   ⚠️ {_WARN} warnings   ❌ {_FAIL} failed")
    print("=" * 60)

    if _FAIL == 0 and _WARN == 0:
        print("🟢 DNA is fully synced. Pipeline is clean.")
    elif _FAIL == 0:
        print("🟡 DNA synced with warnings. Review items above.")
    else:
        print("🔴 Failures found. Fix the items above and re-run.")
    print()


if __name__ == "__main__":
    main()
