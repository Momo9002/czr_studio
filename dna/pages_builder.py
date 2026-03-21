"""
CZR DNA — Utility Pages Builder
Generates concierge.html and other utility pages from identity.json.
These pages are BUILD ARTIFACTS — never hand-edit them.

Pages built:
  - concierge.html   (private client concierge interface)
  - privacy.html     (injects brand name, contact)

Usage:
    python3 -m dna.pages_builder
    python3 -m dna.pages_builder --page concierge
    python3 -m dna.pages_builder --dry
"""

import json
import argparse
from pathlib import Path
from html import escape

ROOT = Path(__file__).parent.parent
DNA_DIR = Path(__file__).parent
IDENTITY = DNA_DIR / "identity.json"


def load() -> dict:
    return json.loads(IDENTITY.read_text())


def _wa_url(dna: dict, msg: str = "Hello, I need help with my project.") -> str:
    phone = dna["brand"]["whatsapp"].replace("+", "").replace(" ", "")
    return f"https://wa.me/{phone}?text={msg.replace(' ', '%20')}"


def build_concierge(dna: dict) -> str:
    """Inject DNA values into concierge.html — brand name, WhatsApp, tagline, packages."""
    brand = dna["brand"]
    packages = dna["packages"]
    site = dna.get("site", {})
    values = site.get("hero", {}).get("values", [])

    wa = _wa_url(dna, "I am a client and need assistance.")
    wa_new = _wa_url(dna, "I want to start a project with CZR Studio")

    template_path = ROOT / "concierge.html"
    if not template_path.exists():
        print("   ⚠️  concierge.html not found, skipping")
        return ""

    html = template_path.read_text()

    # Inject brand values
    replacements = {
        "CZR Studio": escape(brand["name"]),
        "Haute Couture Digital.": escape(brand["tagline"]),
        # WhatsApp links
        "https://wa.me/18107764057": f"https://wa.me/{brand['whatsapp'].replace('+','').replace(' ','')}",
        # Package prices (sprint)
        "€999": f"€{packages['sprint']['price']}",
        # Package prices (flagship)
        "€2,499": f"€{packages['flagship']['price']}",
        "€2499": f"€{packages['flagship']['price']}",
    }

    for old, new in replacements.items():
        html = html.replace(old, new)

    return html


def build_privacy(dna: dict) -> str:
    """Inject DNA brand values into privacy.html."""
    brand = dna["brand"]
    template_path = ROOT / "privacy.html"
    if not template_path.exists():
        return ""

    html = template_path.read_text()
    replacements = {
        "CZR Studio": escape(brand["name"]),
        "Haute Couture Digital.": escape(brand["tagline"]),
        "czr.studio": brand["site"].replace("https://", ""),
        "https://wa.me/18107764057": f"https://wa.me/{brand['whatsapp'].replace('+','').replace(' ','')}",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)

    return html


PAGE_BUILDERS = {
    "concierge": (build_concierge, "concierge.html"),
    "privacy": (build_privacy, "privacy.html"),
}


def build_pages(dna: dict = None, dry: bool = False, page: str = None) -> list[str]:
    """Build all utility pages from DNA. Returns list of built page names."""
    if dna is None:
        dna = load()

    built = []
    pages = {page: PAGE_BUILDERS[page]} if page and page in PAGE_BUILDERS else PAGE_BUILDERS

    for name, (builder_fn, filename) in pages.items():
        html = builder_fn(dna)
        if not html:
            continue

        out_path = ROOT / filename
        if not dry:
            out_path.write_text(html)
            print(f"   ✅ Injected DNA into {filename} ({len(html):,} bytes)")
        else:
            print(f"   ✅ [DRY] Would inject DNA into {filename} ({len(html):,} bytes)")

        built.append(name)

    return built


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CZR DNA Pages Builder")
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("--page", type=str, help="Build only one page", choices=list(PAGE_BUILDERS))
    args = parser.parse_args()
    build_pages(dry=args.dry, page=args.page)
