"""
CZR DNA — Synthesize
Reads the two DNA pillars (vision.md + models.md) and validates that
identity.json is consistent with both. Reports any gaps or drift.

This is Step 0 in the DNA propagation chain:
    vision.md + models.md → synthesize.py → identity.json → sync.py → everything

Usage:
    python3 -m dna.synthesize            # validate and report
    python3 -m dna.synthesize --fix      # attempt to auto-patch identity.json
    python3 -m dna.synthesize --report   # write a report to dna/scrapers/reports/
"""

import re
import json
import argparse
from pathlib import Path
from datetime import datetime

DNA_DIR      = Path(__file__).parent
VISION_FILE  = DNA_DIR / "vision.md"
MODELS_FILE  = DNA_DIR / "models.md"
IDENTITY     = DNA_DIR / "identity.json"
REPORTS_DIR  = DNA_DIR / "scrapers" / "reports"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ok(msg: str):  print(f"   ✅ {msg}")
def _warn(msg: str): print(f"   ⚠️  {msg}")
def _fail(msg: str): print(f"   ❌ {msg}")


def load_identity() -> dict:
    return json.loads(IDENTITY.read_text())


def load_md(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text()


# ── Extraction helpers — read vision.md / models.md as structured data
# ──────────────────────────────────────────────────────────────────────────────

def extract_banned_words_from_vision(vision: str) -> list[str]:
    """Parse the banned word list from vision.md."""
    m = re.search(r"Use:\s*([^\n]+)", vision)
    if not m:
        return []
    raw = m.group(1)
    return [w.strip().lower().rstrip(".") for w in raw.split(",") if w.strip()]


def extract_non_negotiables(vision: str) -> list[str]:
    """Return the non-negotiable items from vision.md."""
    section = re.search(r"## Non-Negotiables\n(.*?)(?=\n##|\Z)", vision, re.DOTALL)
    if not section:
        return []
    lines = section.group(1).strip().splitlines()
    return [re.sub(r'^\d+\.\s*', '', line).strip() for line in lines if line.strip()]


def extract_model_principles(models: str) -> dict[str, str]:
    """Extract the single principle per model from models.md."""
    out = {}
    # Format in models.md: ## VOGUE ... ### The single principle\n[text]
    for model_key, section_header in [
        ("Vogue", "## VOGUE"), ("Hermès", "## HERMÈS"),
        ("SpaceX", "## SPACEX"), ("Apple", "## APPLE")
    ]:
        # Find the model section, then the principle line that follows
        section_pat = rf"{re.escape(section_header)}(.*?)(?=\n## [A-Z]|\Z)"
        sec = re.search(section_pat, models, re.DOTALL | re.IGNORECASE)
        if not sec:
            continue
        section_text = sec.group(1)
        # Find ### The single principle header and grab the next non-empty line
        principle_pat = r"### The single principle\s*\n+(.+)"
        pm = re.search(principle_pat, section_text, re.IGNORECASE)
        if pm:
            out[model_key] = pm.group(1).strip().strip('*').strip('_')
    return out


def extract_accent_usage(models: str) -> dict:
    """Check Hermès orange usage rule from models.md."""
    hermes_section = re.search(r"## HERMÈS(.*?)## SPACEX", models, re.DOTALL)
    if not hermes_section:
        return {}
    text = hermes_section.group(1)
    once_rule = "once per page" in text.lower() or "once per" in text.lower()
    return {"hermes_orange_once_per_page": once_rule}


# ── Validation checks ─────────────────────────────────────────────────────────

def check_banned_words(dna: dict, vision: str, warnings: list, failures: list):
    """identity.json voice.never should contain words from vision.md banned list."""
    vision_banned = set(extract_banned_words_from_vision(vision))
    # identity.json stores banned words in voice.never
    voice = dna.get("voice", {})
    id_never = voice.get("never", voice.get("banned_words", []))
    id_banned = set(w.lower().strip("!") for w in id_never if isinstance(w, str) and len(w) > 1)

    if not vision_banned:
        warnings.append("vision.md: Could not parse banned word list")
        return
    if not id_banned:
        failures.append("identity.json: voice.never is empty — add banned words list")
        return

    missing_in_id = vision_banned - id_banned
    if missing_in_id:
        warnings.append(f"Words in vision.md but NOT in identity.json voice.never: {sorted(missing_in_id)}")
    else:
        _ok(f"Banned words aligned: vision.md ↔ identity.json voice.never ({len(id_banned)} words)")


def check_non_negotiables(dna: dict, vision: str, warnings: list, failures: list):
    """Spot-check key non-negotiables from vision.md against identity.json."""
    nn = extract_non_negotiables(vision)
    if not nn:
        warnings.append("vision.md: Could not parse non-negotiables section")
        return

    full_dna_str = json.dumps(dna).lower()
    checks = {
        "Knight (avatar)": "knight" in full_dna_str or "♞" in full_dna_str,
        "48h guarantee":   "48" in full_dna_str,
        "Syne font":       "syne" in full_dna_str,
        "IP/ownership":    "ip" in full_dna_str or "transfer" in full_dna_str or "ownership" in full_dna_str,
    }
    passed = sum(1 for v in checks.values() if v)
    for label, ok in checks.items():
        if not ok:
            warnings.append(f"Non-negotiable '{label}' not found in identity.json")
    if passed == len(checks):
        _ok(f"Non-negotiables: all {passed} spot-checks pass in identity.json")


def check_hermes_orange(dna: dict, models: str, warnings: list, failures: list):
    """identity.json should have hermes color token."""
    has_hermes_color = "hermes" in str(dna.get("colors", {})).lower()
    if has_hermes_color:
        _ok("Hermès orange token present in identity.json colors")
    else:
        failures.append("identity.json: Missing 'hermes' color token — add #E8601C")
    # Check models.md has a Hermès orange mention
    if "once per page" in models.lower() or "once per" in models.lower() or "single" in models.lower():
        _ok("models.md: Hermès accent restraint rule documented")
    else:
        warnings.append("models.md: Add explicit Hermès orange frequency rule")


def check_model_principles_referenced(dna: dict, models: str, warnings: list, failures: list):
    """Each model's principle should be reflected somewhere in the DNA docs."""
    principles = extract_model_principles(models)
    if not principles:
        warnings.append("models.md: Could not extract model principles")
        return
    _ok(f"Model principles extracted: {list(principles.keys())}")
    for model, principle in principles.items():
        _ok(f"  {model}: {principle[:60]}...")


def check_typography(dna: dict, vision: str, warnings: list, failures: list):
    """identity.json typography should include Syne as display (vision.md non-negotiable)."""
    typo = dna.get("typography", {})
    display = str(typo.get("display", "")).lower()
    if "syne" in display:
        _ok("Typography: Syne 800 confirmed as display font")
    else:
        failures.append(f"identity.json: display font is '{display}', should be 'Syne' (vision.md non-negotiable)")


def check_guarantee(dna: dict, vision: str, warnings: list, failures: list):
    """48h guarantee must be in identity.json."""
    guarantee = dna.get("guarantee", "")
    if "48" in str(guarantee) and ("nothing" in str(guarantee).lower() or "free" in str(guarantee).lower()):
        _ok("Guarantee: 48h + unconditional language present")
    else:
        failures.append("identity.json: guarantee field missing or weak — should say '48h or free, no questions'")


def check_voice_pillar(dna: dict, vision: str, warnings: list, failures: list):
    """vision.md voice rules should align with identity.json voice section."""
    voice = dna.get("voice", {})
    # Check for period ending rule
    tone = json.dumps(voice).lower()
    if "period" in tone or "exclamation" in tone or "!" in tone:
        _ok("Voice: period/exclamation rule captured in identity.json")
    else:
        warnings.append("identity.json voice: no reference to period endings or exclamation ban — add to voice rules")


# ── Generative synthesis — vision.md → identity.json ─────────────────────────

def parse_vision_tokens(vision: str) -> dict:
    """
    Parse the ```tokens block from vision.md.
    Format:
        type.display_weight = 700
        space.section_v     = clamp(8rem, 16vw, 16rem)
    Returns nested dict: {"type": {"display_weight": "700"}, "space": {...}}
    """
    token_block = re.search(r"```tokens\n(.*?)```", vision, re.DOTALL)
    if not token_block:
        return {}

    result: dict[str, dict] = {}
    for line in token_block.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key_part, _, val_part = line.partition("=")
        key = key_part.strip()
        val = val_part.strip()
        if "." in key:
            group, _, subkey = key.partition(".")
            result.setdefault(group, {})[subkey] = val
        else:
            result[key] = val
    return result


def apply_vision_tokens(tokens: dict) -> tuple[int, list[str]]:
    """
    Write parsed vision tokens to identity.json → tokens block.
    Returns (n_changes, changed_keys).
    """
    if not tokens:
        return 0, []

    dna = load_identity()
    existing = dna.get("tokens", {})
    changes = []

    for group_key, group_val in tokens.items():
        if isinstance(group_val, dict):
            for subkey, val in group_val.items():
                old = existing.get(group_key, {}).get(subkey)
                if old != val:
                    existing.setdefault(group_key, {})[subkey] = val
                    changes.append(f"{group_key}.{subkey}: {old!r} → {val!r}")
        else:
            old = existing.get(group_key)
            if old != group_val:
                existing[group_key] = group_val
                changes.append(f"{group_key}: {old!r} → {group_val!r}")

    if changes:
        dna["tokens"] = existing
        IDENTITY.write_text(json.dumps(dna, indent=2, ensure_ascii=False))

    return len(changes), changes


# ── Main synthesize ───────────────────────────────────────────────────────────

def synthesize(fix: bool = False) -> tuple[int, int, int]:
    """
    Returns (passed, warnings, failures).
    If fix=True, attempts auto-patching of safe discrepancies.
    """
    print("\n0️⃣  Synthesize — visión.md + models.md → identity.json")
    print("   Checking DNA pillar consistency...\n")

    dna    = load_identity()
    vision = load_md(VISION_FILE)
    models = load_md(MODELS_FILE)

    if not vision:
        print("   ❌ dna/vision.md not found. Run /dna-update workflow.")
        return 0, 0, 1
    if not models:
        print("   ❌ dna/models.md not found.")
        return 0, 0, 1

    warnings: list[str] = []
    failures: list[str] = []

    # ── Generative step: read vision.md Tokens block → write to identity.json ──
    vision_tokens = parse_vision_tokens(vision)
    if vision_tokens:
        n_changes, changed = apply_vision_tokens(vision_tokens)
        if n_changes:
            _ok(f"Tokens: wrote {n_changes} changes from vision.md → identity.json")
            for c in changed[:5]:
                print(f"     · {c}")
            # Reload identity after writing
            dna = load_identity()
        else:
            _ok(f"Tokens: vision.md → identity.json already in sync ({len(vision_tokens)} keys)")
    else:
        _warn("vision.md: No ```tokens block found — add one to drive visual changes from vision")

    checks = [
        check_banned_words,
        check_non_negotiables,
        check_hermes_orange,
        check_model_principles_referenced,
        check_typography,
        check_guarantee,
        check_voice_pillar,
    ]

    passed = 0
    # Each tuple: (fn, second_arg) — vision or models, depending on what the check needs
    dispatch = [
        (check_banned_words,                vision),
        (check_non_negotiables,             vision),
        (check_hermes_orange,               models),
        (check_model_principles_referenced, models),
        (check_typography,                  vision),
        (check_guarantee,                   vision),
        (check_voice_pillar,                vision),
    ]
    for check, arg in dispatch:
        before_w = len(warnings)
        before_f = len(failures)
        check(dna, arg, warnings, failures)
        if len(failures) == before_f and len(warnings) == before_w:
            passed += 1

    # Print warnings and failures
    for w in warnings:  _warn(w)
    for f in failures:  _fail(f)

    print(f"\n   Synthesize: {passed} passed · {len(warnings)} warnings · {len(failures)} failures")
    return passed, len(warnings), len(failures)


def write_report(passed: int, n_warnings: int, n_failures: int) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    date = datetime.now().strftime("%Y%m%d_%H%M")
    path = REPORTS_DIR / f"synthesize_{date}.md"
    status = "🟢 Clean" if n_failures == 0 else "🔴 Issues found"
    lines = [
        f"# DNA Synthesize Report — {datetime.now().strftime('%B %d, %Y %H:%M')}",
        "",
        f"**Status:** {status}",
        f"- ✅ {passed} checks passed",
        f"- ⚠️  {n_warnings} warnings",
        f"- ❌ {n_failures} failures",
        "",
        "Run `python3 -m dna.synthesize` for details.",
        "",
        "---",
        f"_Generated: {datetime.now().isoformat()}_",
    ]
    path.write_text("\n".join(lines))
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CZR DNA Synthesize")
    parser.add_argument("--fix",    action="store_true", help="Auto-patch safe discrepancies")
    parser.add_argument("--report", action="store_true", help="Write report to scrapers/reports/")
    args = parser.parse_args()

    passed, n_warn, n_fail = synthesize(fix=args.fix)

    if args.report:
        path = write_report(passed, n_warn, n_fail)
        print(f"   📋 Report: {path.name}")

    exit(0 if n_fail == 0 else 1)
