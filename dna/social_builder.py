"""
CZR DNA — Social Content Builder
Generates brand-compliant captions for Instagram and LinkedIn from DNA.

Usage:
    python3 -m dna.social_builder --intent portfolio --case restaurant
    python3 -m dna.social_builder --intent launch
    python3 -m dna.social_builder --intent value

Intents: launch, portfolio, value, process, offer
"""

import json
import argparse
import random
from pathlib import Path

ROOT = Path(__file__).parent.parent
DNA_DIR = Path(__file__).parent
IDENTITY = DNA_DIR / "identity.json"
VOICE = DNA_DIR / "voice.md"


def load() -> dict:
    return json.loads(IDENTITY.read_text())


def _hashtags(dna: dict, n: int = 5) -> str:
    tags = dna.get("hashtags", [])
    return " ".join(tags[:n])


def _wa_url(dna: dict) -> str:
    phone = dna["brand"]["whatsapp"].replace("+", "").replace(" ", "")
    return f"https://wa.me/{phone}"


TEMPLATES = {
    "launch": [
        """{client} is live.

{tagline}

Built in a focused sprint. No revisions. No delays.
Brief today — live at lightning speed.

{url}
{tags}""",
        """New work.

{client}. {category}. {location}.

"{tagline}"

{url}
{tags}""",
    ],
    "portfolio": [
        """{client}. {category}.

{challenge_short}

The brief was clear. The build was focused. The result speaks.

{url}
{tags}""",
        """The portfolio grows.

{client} — {tagline}

{result_short}

See the full case at {url}
{tags}""",
    ],
    "value": [
        """Three things we do not do.

No discovery calls.
No mood boards.
No approval loops.

You brief once. We build. You receive.

{url}
{tags}""",
        """The brief takes ten minutes.

Three questions. Vision, audience, references.
We begin the same day.

{name}. {tagline}

{url}
{tags}""",
        """What we transfer on delivery.

Source files. Full IP. Hosting instructions.
No dependencies. No subscriptions. No ongoing fees unless you choose them.

The Sprint starts at €{sprint_price}.

{url}
{tags}""",
    ],
    "process": [
        """How a sprint works.

01. Brief — ten minutes.
02. Build — focused, no interruptions.
03. Ship — delivered at lightning speed.

{name}. {tagline}

{url}
{tags}""",
    ],
    "offer": [
        """The Sprint. €{sprint_price}.

3-page website. Mobile-first. Lightning fast delivery.
Full IP transfer.

{name}.

{url}
{tags}""",
        """The Flagship. €{flagship_price}.

Up to 8 pages. Brand consultation. CMS ready. 2 revisions.
Everything transferred.

Inquire via {wa_url}
{tags}""",
    ],
}


def generate_post(
    intent: str,
    case_slug: str = None,
    platform: str = "instagram",
    dna: dict = None,
) -> str:
    """
    Generate a brand-compliant caption from DNA.

    Args:
        intent: one of launch, portfolio, value, process, offer
        case_slug: slug of a case study (for portfolio/launch intents)
        platform: instagram or linkedin
        dna: pre-loaded DNA dict (optional)

    Returns:
        Validated caption string
    """
    if dna is None:
        dna = load()

    brand = dna["brand"]
    packages = dna["packages"]
    cases = dna.get("site", {}).get("cases", [])

    # Find case if given
    case = next((c for c in cases if c["slug"] == case_slug), None)

    # Build template context
    ctx = {
        "name": brand["name"],
        "tagline": brand["tagline"],
        "url": brand["site"],
        "wa_url": _wa_url(dna),
        "sprint_price": packages["sprint"]["price"],
        "flagship_price": packages["flagship"]["price"],
        "tags": _hashtags(dna, 6 if platform == "instagram" else 4),
        "client": case.get("client", "") if case else "",
        "category": case.get("category", "") if case else "",
        "location": case.get("location", "") if case else "",
        "tagline_case": case.get("tagline", "") if case else "",
        "challenge_short": (case.get("challenge", "")[:100] + "...") if case else "",
        "result_short": (case.get("result", "")[:100] + "...") if case else "",
    }
    # Use case tagline for launch/portfolio
    if case and intent in ("launch", "portfolio"):
        ctx["tagline"] = case.get("tagline", brand["tagline"])

    templates = TEMPLATES.get(intent, TEMPLATES["value"])
    template = random.choice(templates)
    caption = template.format(**ctx).strip()

    # Brand guard check
    try:
        from api.content_templates import brand_guard
        passes, reason = brand_guard(caption, platform)
        if not passes:
            print(f"   ⚠️  Brand Guard: {reason}")
    except ImportError:
        pass

    return caption


def build_social(dna: dict = None, dry: bool = False) -> dict[str, str]:
    """
    Generate one caption per intent and write to dna/social_drafts.json.
    Returns dict of intent → caption.
    """
    if dna is None:
        dna = load()

    intents = ["value", "process", "offer", "portfolio"]
    cases = dna.get("site", {}).get("cases", [])
    drafts = {}

    for intent in intents:
        case_slug = cases[0]["slug"] if cases and intent in ("portfolio", "launch") else None
        caption = generate_post(intent, case_slug=case_slug, dna=dna)
        drafts[intent] = caption
        if not dry:
            print(f"   ✅ {intent}: {len(caption)} chars")
        else:
            print(f"   ✅ [DRY] {intent}: {len(caption)} chars")

    if not dry:
        out = DNA_DIR / "social_drafts.json"
        out.write_text(json.dumps(drafts, indent=2, ensure_ascii=False))
        print(f"   ✅ Written dna/social_drafts.json ({len(drafts)} drafts)")

    return drafts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CZR DNA Social Builder")
    parser.add_argument("--intent", type=str, default="value",
                        choices=["launch", "portfolio", "value", "process", "offer"])
    parser.add_argument("--case", type=str, help="Case slug for portfolio/launch")
    parser.add_argument("--platform", type=str, default="instagram",
                        choices=["instagram", "linkedin"])
    parser.add_argument("--dry", action="store_true")
    args = parser.parse_args()

    caption = generate_post(args.intent, case_slug=args.case, platform=args.platform)
    print("\n" + "─" * 50)
    print(caption)
    print("─" * 50)
