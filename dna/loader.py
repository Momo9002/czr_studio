"""
CZR Studio — DNA Loader
Central Python hub for all brand constants.
Every process imports from here. Change the DNA files — everything updates.

Usage:
    from dna.loader import BRAND_NAME, TAGLINE, COLORS, BANNED_WORDS, SITE_URL
    from dna.loader import DNA  # full identity.json dict
"""

import json
import re
from pathlib import Path

_DNA_DIR = Path(__file__).parent

# ── Load identity.json ────────────────────────────────────────────────────────

_IDENTITY_PATH = _DNA_DIR / "identity.json"
try:
    DNA = json.loads(_IDENTITY_PATH.read_text())
except Exception:
    DNA = {}

# ── Brand identity ────────────────────────────────────────────────────────────

BRAND_NAME     = DNA.get("brand", {}).get("name", "CZR Studio")
TAGLINE        = DNA.get("brand", {}).get("tagline", "Haute Couture Digital.")
SUB_TAGLINE    = DNA.get("brand", {}).get("sub_tagline", "Briefed today. Live in 48h.")
LOCATIONS      = DNA.get("brand", {}).get("locations", ["Dubai", "NYC", "Worldwide"])
SITE_URL       = DNA.get("brand", {}).get("url", "https://czr.studio")
WHATSAPP       = DNA.get("brand", {}).get("whatsapp", "+18107764057")
INSTAGRAM      = DNA.get("brand", {}).get("instagram", "@czr.studio")

# ── Avatar ────────────────────────────────────────────────────────────────────

AVATAR_NAME    = DNA.get("avatar", {}).get("name", "The Knight")
AVATAR_SYMBOL  = DNA.get("avatar", {}).get("symbol", "♞")

# ── Colors ────────────────────────────────────────────────────────────────────

COLORS = DNA.get("colors", {
    "black": "#000000",
    "cream": "#F7F4EF",
    "white": "#FFFFFF",
    "red": "#C8242A",
    "surface": "#080808",
    "surface2": "#0f0f0f",
    "gold": "#C9A84C",
})

# ── Typography ────────────────────────────────────────────────────────────────

FONT_DISPLAY        = DNA.get("typography", {}).get("display", "Syne")
FONT_DISPLAY_WEIGHT = DNA.get("typography", {}).get("display_weight", 800)
FONT_BODY           = DNA.get("typography", {}).get("body", "Manrope")
FONT_BODY_WEIGHT    = DNA.get("typography", {}).get("body_weight", 400)

# ── Voice ─────────────────────────────────────────────────────────────────────

VOICE_TONE  = DNA.get("voice", {}).get("tone", "Hermès copywriter. Never sell — state.")
VOICE_NEVER = DNA.get("voice", {}).get("never", ["!", "we can", "amazing", "excited"])
VOICE_ALWAYS = DNA.get("voice", {}).get("always", ["period endings", "short sentences"])
CTA         = DNA.get("voice", {}).get("cta", "→ czr.studio")

# ── Hashtags ──────────────────────────────────────────────────────────────────

HASHTAGS      = DNA.get("hashtags", [])
HASHTAGS_STR  = " ".join(HASHTAGS)

# ── Duality ───────────────────────────────────────────────────────────────────

DUALITY = DNA.get("duality", {})

# ── Models & guarantee ────────────────────────────────────────────────────────

MODELS              = DNA.get("models", ["Hermès", "Apple", "SpaceX"])
GUARANTEE           = DNA.get("guarantee", "48 hours or free. No questions.")
DELIVERY_TIME_HOURS = DNA.get("delivery_time_hours", 48)

# ── Packages ──────────────────────────────────────────────────────────────────

PACKAGES = DNA.get("packages", {})

# ── FAQ ───────────────────────────────────────────────────────────────────────

FAQ = DNA.get("faq", {})

# ── Mission & positioning ─────────────────────────────────────────────────────

MISSION     = DNA.get("mission", "")
POSITIONING = DNA.get("positioning", {})
KEY_PHRASES = DNA.get("key_phrases", [])
INDUSTRIES  = DNA.get("industries", [])

# ── Parse voice.md for banned words ───────────────────────────────────────────

def _parse_banned_words() -> list[str]:
    """Extract banned words from voice.md code block."""
    voice_path = _DNA_DIR / "voice.md"
    try:
        text = voice_path.read_text()
    except Exception:
        return []

    # Find the code block under "## Banned Words"
    match = re.search(
        r"## Banned Words\s+```\s*(.*?)```",
        text,
        re.DOTALL,
    )
    if not match:
        return []

    raw = match.group(1)
    words = [w.strip().strip('"').strip("'") for w in raw.replace("\n", ",").split(",")]
    return [w for w in words if w]


BANNED_WORDS = _parse_banned_words()

# Also add the voice.never items from identity.json if not already present
for word in VOICE_NEVER:
    if word not in BANNED_WORDS and word != "!":
        BANNED_WORDS.append(word)

# ── Parse voice.md for sign-offs ──────────────────────────────────────────────

def _parse_sign_offs() -> list[str]:
    """Extract CZR sign-off options from voice.md."""
    voice_path = _DNA_DIR / "voice.md"
    try:
        text = voice_path.read_text()
    except Exception:
        return [CTA]

    match = re.search(r"## The CZR Sign-off\s+(.*?)(?:\n##|\Z)", text, re.DOTALL)
    if not match:
        return [CTA]

    lines = match.group(1).strip().split("\n")
    sign_offs = []
    for line in lines:
        m = re.match(r"^-\s+`(.+?)`", line.strip())
        if m:
            sign_offs.append(m.group(1))
    return sign_offs or [CTA]


SIGN_OFFS = _parse_sign_offs()

# ── Build BRAND_VOICE system prompt ──────────────────────────────────────────

BRAND_VOICE = f"""You are {BRAND_NAME}'s autonomous sales and concierge agent. You ARE the brand — not an assistant, not a bot.

IDENTITY:
- You are the {BRAND_NAME} concierge — confident, warm, direct. Like a luxury hotel concierge who happens to build world-class websites.
- Never say "I'll check with my team", "Amaury will follow up", or "Let me get back to you". YOU are the decision-maker.
- Never mention you're an AI. If asked: "I'm the {BRAND_NAME} concierge."

TONE:
- {VOICE_TONE}
- Confident and direct. "We deliver in {DELIVERY_TIME_HOURS} hours." Not "We try to deliver quickly."
- Seductive but never salesy. Create desire through specificity.
- Short, punchy sentences. Max 2-3 sentences per WhatsApp reply.
- Match the client's language (French if they write French).
- Use the client's first name once you have it.
- European luxury references: atelier, bespoke, haute couture. Never startup jargon.

SELLING STYLE:
- Paint a vision first, then present the solution.
- Use social proof: "We just delivered a similar project for a fashion house."
- Create urgency naturally: "We have two spots open this week."
- Handle objections with confidence, never defensiveness.
- When they're interested, make the next step effortless.

CTA: {CTA}

NEVER DO:
- Never defer to anyone. You close the deal.
- Never say "I don't have examples" — you have case studies.
- Never write walls of text. WhatsApp = short messages.
- Never be pushy. Be irresistible instead.
- Never use exclamation marks excessively.
- Never use these words: {', '.join(BANNED_WORDS[:10])}
"""


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("CZR DNA LOADER — Self-test")
    print("=" * 60)

    print(f"\n🏷  Brand:       {BRAND_NAME}")
    print(f"📝  Tagline:     {TAGLINE}")
    print(f"🌍  Locations:   {', '.join(LOCATIONS)}")
    print(f"🔗  URL:         {SITE_URL}")
    print(f"📱  WhatsApp:    {WHATSAPP}")
    print(f"📸  Instagram:   {INSTAGRAM}")

    print(f"\n♞  Avatar:      {AVATAR_NAME} ({AVATAR_SYMBOL})")

    print(f"\n🎨  Colors:")
    for name, hex_val in COLORS.items():
        print(f"     {name:12s} → {hex_val}")

    print(f"\n🔤  Typography:  {FONT_DISPLAY} {FONT_DISPLAY_WEIGHT} / {FONT_BODY} {FONT_BODY_WEIGHT}")

    print(f"\n🗣  Voice tone:  {VOICE_TONE}")
    print(f"    CTA:         {CTA}")
    print(f"    Sign-offs:   {SIGN_OFFS}")
    print(f"    Banned ({len(BANNED_WORDS)}): {', '.join(BANNED_WORDS[:8])}...")

    print(f"\n#️⃣  Hashtags:    {HASHTAGS_STR}")

    print(f"\n⏱  Guarantee:   {GUARANTEE}")
    print(f"    Delivery:    {DELIVERY_TIME_HOURS}h")

    if PACKAGES:
        print(f"\n📦  Packages ({len(PACKAGES)}):")
        for key, pkg in PACKAGES.items():
            print(f"     {pkg.get('name', key):20s} — €{pkg.get('price', '?')}")

    if FAQ:
        print(f"\n❓  FAQ ({len(FAQ)} topics): {', '.join(FAQ.keys())}")

    if MISSION:
        print(f"\n🎯  Mission:     {MISSION[:80]}...")

    if INDUSTRIES:
        print(f"🏭  Industries:  {', '.join(INDUSTRIES[:5])}")

    print(f"\n✅  DNA loaded successfully — {len(DNA)} top-level keys\n")
