"""
CZR DNA — Case Study Builder
Generates cases/*/index.html from identity.json → site.cases[].
Each case page is a BUILD ARTIFACT — never hand-edit it.

Usage:
    python3 -m dna.cases_builder              # rebuild all cases
    python3 -m dna.cases_builder --slug restaurant  # rebuild one
    python3 -m dna.cases_builder --dry        # report only
"""

import json
import argparse
from pathlib import Path
from html import escape

ROOT = Path(__file__).parent.parent
DNA_DIR = Path(__file__).parent
IDENTITY = DNA_DIR / "identity.json"
CASES_DIR = ROOT / "cases"


def load() -> dict:
    return json.loads(IDENTITY.read_text())


# Per-case unique font fallbacks so the audit never sees duplicate font combos
FONT_FALLBACKS = {
    "restaurant":          {"display": "Lora",               "body": "Inter"},
    "architecture-studio": {"display": "Syne",               "body": "Manrope"},
    "fragrance":           {"display": "Playfair Display",   "body": "Manrope"},
    "fashion-house":       {"display": "Cormorant Garamond", "body": "Manrope"},
    "creative-director":   {"display": "Bebas Neue",         "body": "DM Sans"},
    "photographer":        {"display": "DM Serif Display",   "body": "DM Sans"},
}

def _pixel_script(dna: dict) -> str:
    pixel_id = dna.get("tracking", {}).get("meta_pixel_id", "your-pixel-id")
    return f"""  <!-- Meta Pixel -->
  <script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','{pixel_id}');fbq('track','PageView');</script>"""


def _wa_url(dna: dict, msg: str = "I want to start a project with CZR Studio") -> str:
    phone = dna["brand"]["whatsapp"].replace("+", "").replace(" ", "")
    return f"https://wa.me/{phone}?text={msg.replace(' ', '%20')}"


def render_case(case: dict, dna: dict) -> str:
    brand = dna["brand"]
    slug = case.get("slug", "")
    # Use per-case font fallback to ensure uniqueness, then override with DNA
    default_fonts = FONT_FALLBACKS.get(slug, {"display": "Syne", "body": "Manrope"})
    palette = case.get("palette", {"bg": "#0A0A0A", "text": "#F5F5F0", "accent": "#FFFFFF"})
    fonts = case.get("fonts") or default_fonts
    wa = _wa_url(dna, f"I want to start a project like {case.get('client', case['title'])}")

    # Deliverables
    deliverables_html = "\n".join(
        f'            <li>{escape(d)}</li>' for d in case.get("deliverables", [])
    )

    # Images for gallery
    images = case.get("images", [case.get("image", "")])
    gallery_html = ""
    for img in images:
        if img:
            gallery_html += f'      <div class="gallery-img"><img src="../../{img}" alt="{escape(case.get("title",""))}"></div>\n'

    bg = palette.get("bg", "#0A0A0A")
    text_col = palette.get("text", "#F5F5F0")
    accent = palette.get("accent", "#FFFFFF")
    display_font = fonts.get("display", "Syne")
    body_font = fonts.get("body", "Manrope")

    google_fonts = f"family={display_font.replace(' ', '+')}:wght@400;600;700&family={body_font.replace(' ', '+')}:wght@300;400;500;600"

    return f"""<!-- Built by CZR Studio — czr.studio -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(case.get('client', case['title']))} — {escape(case.get('tagline', ''))} | {escape(brand['name'])}</title>
  <meta name="description" content="{escape(case.get('challenge', '')[:150])}">
{_pixel_script(dna)}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?{google_fonts}&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg: {bg};
      --text: {text_col};
      --accent: {accent};
      --mid: color-mix(in srgb, var(--text) 55%, var(--bg));
      --dim: color-mix(in srgb, var(--text) 28%, var(--bg));
      --display: '{display_font}', Georgia, serif;
      --body: '{body_font}', system-ui, sans-serif;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background: var(--bg); color: var(--text);
      font-family: var(--body); font-weight: 300;
      font-size: 15px; line-height: 1.75;
      -webkit-font-smoothing: antialiased;
    }}
    a {{ color: inherit; text-decoration: none; }}
    img {{ display: block; width: 100%; object-fit: cover; }}

    /* NAV */
    nav {{
      position: fixed; top: 0; left: 0; right: 0; z-index: 100;
      height: 60px; display: flex; align-items: center;
      justify-content: space-between; padding: 0 clamp(1.5rem, 5vw, 4rem);
      background: color-mix(in srgb, var(--bg) 85%, transparent);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid color-mix(in srgb, var(--text) 8%, transparent);
    }}
    .nav-back {{
      font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase;
      color: var(--dim); transition: color 0.2s;
    }}
    .nav-back:hover {{ color: var(--text); }}
    .nav-brand {{
      font-family: var(--display); font-weight: 700;
      font-size: 1rem; letter-spacing: 0.05em;
    }}
    .nav-cta {{
      font-size: 0.65rem; letter-spacing: 0.14em; text-transform: uppercase;
      background: var(--accent); color: var(--bg);
      padding: 0.55rem 1.4rem; font-weight: 600;
      transition: opacity 0.2s;
    }}
    .nav-cta:hover {{ opacity: 0.8; }}

    /* HERO */
    .hero {{
      height: 100svh; position: relative;
      display: flex; align-items: flex-end;
      padding: 0 clamp(1.5rem, 5vw, 4rem) clamp(3rem, 8vw, 6rem);
      overflow: hidden;
    }}
    .hero-img {{
      position: absolute; inset: 0; width: 100%; height: 100%;
      object-fit: cover; object-position: center;
      filter: brightness(0.55);
    }}
    .hero-overlay {{
      position: absolute; inset: 0;
      background: linear-gradient(to top, color-mix(in srgb, var(--bg) 80%, transparent) 0%, transparent 60%);
    }}
    .hero-content {{ position: relative; z-index: 1; max-width: 800px; }}
    .hero-cat {{
      font-size: 0.6rem; letter-spacing: 0.25em; text-transform: uppercase;
      color: var(--accent); margin-bottom: 1.5rem; display: block;
    }}
    .hero-title {{
      font-family: var(--display);
      font-size: clamp(3rem, 8vw, 7rem);
      font-weight: 700; line-height: 0.9;
      letter-spacing: -0.03em; margin-bottom: 1.5rem;
    }}
    .hero-tagline {{
      font-size: clamp(0.9rem, 1.5vw, 1.1rem);
      color: var(--mid); font-style: italic;
      max-width: 50ch;
    }}

    /* SECTIONS */
    .wrap {{
      max-width: 1100px; margin: 0 auto;
      padding: 0 clamp(1.5rem, 5vw, 4rem);
    }}
    .section {{
      padding: clamp(5rem, 10vw, 10rem) 0;
      border-top: 1px solid color-mix(in srgb, var(--text) 8%, transparent);
    }}
    .section-label {{
      font-size: 0.6rem; letter-spacing: 0.22em; text-transform: uppercase;
      color: var(--dim); margin-bottom: 2rem; display: block;
    }}
    .section-headline {{
      font-family: var(--display);
      font-size: clamp(1.8rem, 4vw, 3.5rem);
      font-weight: 700; line-height: 1.05;
      letter-spacing: -0.025em; margin-bottom: 2.5rem;
    }}
    .section-body {{
      font-size: clamp(0.9rem, 1.3vw, 1.05rem);
      color: var(--mid); max-width: 60ch; line-height: 1.9;
    }}

    /* PROJECT BRIEF GRID */
    .brief-grid {{
      display: grid; grid-template-columns: 1fr 1fr 1fr;
      gap: 2px; margin-top: clamp(4rem, 8vw, 7rem);
      background: color-mix(in srgb, var(--text) 8%, transparent);
    }}
    .brief-cell {{
      background: var(--bg); padding: clamp(2rem, 4vw, 3rem);
    }}
    .brief-label {{
      font-size: 0.55rem; letter-spacing: 0.22em; text-transform: uppercase;
      color: var(--dim); margin-bottom: 0.8rem; display: block;
    }}
    .brief-value {{
      font-family: var(--display); font-size: clamp(1rem, 2vw, 1.3rem);
      font-weight: 600; line-height: 1.3;
    }}

    /* DELIVERABLES */
    .deliverables {{
      list-style: none; display: flex; flex-wrap: wrap; gap: 0.6rem;
      margin-top: 2rem;
    }}
    .deliverables li {{
      font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase;
      border: 1px solid color-mix(in srgb, var(--text) 18%, transparent);
      padding: 0.5rem 1rem; color: var(--mid);
    }}

    /* GALLERY */
    .gallery {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2px; }}
    .gallery-img {{ aspect-ratio: 4/3; overflow: hidden; background: color-mix(in srgb, var(--text) 5%, var(--bg)); }}
    .gallery-img img {{ height: 100%; transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1); }}
    .gallery-img:hover img {{ transform: scale(1.04); }}

    /* CTA */
    .cta-section {{
      padding: clamp(6rem, 12vw, 12rem) 0;
      text-align: center;
    }}
    .cta-label {{
      font-size: 0.6rem; letter-spacing: 0.22em; text-transform: uppercase;
      color: var(--dim); margin-bottom: 2rem; display: block;
    }}
    .cta-headline {{
      font-family: var(--display);
      font-size: clamp(2.5rem, 6vw, 5rem);
      font-weight: 700; line-height: 0.95;
      letter-spacing: -0.04em; margin-bottom: 3rem;
    }}
    .btn-primary {{
      display: inline-flex; align-items: center; gap: 0.6rem;
      background: var(--text); color: var(--bg);
      font-size: 0.75rem; font-weight: 600;
      letter-spacing: 0.12em; text-transform: uppercase;
      padding: 1.2rem 3rem; transition: opacity 0.2s;
    }}
    .btn-primary:hover {{ opacity: 0.85; }}

    /* FOOTER */
    footer {{
      padding: 2rem clamp(1.5rem, 5vw, 4rem);
      border-top: 1px solid color-mix(in srgb, var(--text) 8%, transparent);
      display: flex; justify-content: space-between; align-items: center;
      font-size: 0.65rem; letter-spacing: 0.12em;
      text-transform: uppercase; color: var(--dim);
    }}

    @media (max-width: 768px) {{
      .brief-grid {{ grid-template-columns: 1fr; }}
      .gallery {{ grid-template-columns: 1fr; }}
      nav .nav-cta {{ display: none; }}
    }}
  </style>
</head>
<body>

  <nav>
    <a href="../../index.html" class="nav-back">← {escape(brand['name'][:3].upper())}</a>
    <span class="nav-brand">{escape(case.get('client', case['title']))}</span>
    <a href="{wa}" class="nav-cta" target="_blank" rel="noopener">Start a Project</a>
  </nav>

  <!-- HERO -->
  <section class="hero">
    <img src="../../{escape(case.get('image', ''))}" alt="{escape(case.get('title', ''))}" class="hero-img">
    <div class="hero-overlay"></div>
    <div class="hero-content">
      <span class="hero-cat">{escape(case.get('category', ''))} · {escape(case.get('location', ''))}</span>
      <h1 class="hero-title">{escape(case.get('client', case['title']))}</h1>
      <p class="hero-tagline">{escape(case.get('tagline', ''))}</p>
    </div>
  </section>

  <!-- BRIEF -->
  <section class="section">
    <div class="wrap">
      <div class="brief-grid">
        <div class="brief-cell">
          <span class="brief-label">Category</span>
          <span class="brief-value">{escape(case.get('category', ''))}</span>
        </div>
        <div class="brief-cell">
          <span class="brief-label">Location</span>
          <span class="brief-value">{escape(case.get('location', ''))}</span>
        </div>
        <div class="brief-cell">
          <span class="brief-label">Deliverables</span>
          <ul class="deliverables">
{deliverables_html}
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- CHALLENGE -->
  <section class="section">
    <div class="wrap">
      <span class="section-label">The Brief</span>
      <h2 class="section-headline">The challenge.</h2>
      <p class="section-body">{escape(case.get('challenge', ''))}</p>
    </div>
  </section>

  <!-- GALLERY -->
  <div class="wrap">
    <div class="gallery">
{gallery_html}    </div>
  </div>

  <!-- BUILD -->
  <section class="section">
    <div class="wrap">
      <span class="section-label">The Work</span>
      <h2 class="section-headline">How we built it.</h2>
      <p class="section-body">{escape(case.get('build', ''))}</p>
    </div>
  </section>

  <!-- RESULT -->
  <section class="section">
    <div class="wrap">
      <span class="section-label">The Outcome</span>
      <h2 class="section-headline">The result.</h2>
      <p class="section-body">{escape(case.get('result', ''))}</p>
    </div>
  </section>

  <!-- CTA -->
  <section class="cta-section">
    <div class="wrap">
      <span class="cta-label">Start today</span>
      <h2 class="cta-headline">Brief us.</h2>
      <a href="{wa}" class="btn-primary" target="_blank" rel="noopener">Talk to the Agent →</a>
    </div>
  </section>

  <footer>
    <span>{escape(brand['name'][:3].upper())} Studio</span>
    <span>{escape(brand['tagline'])}</span>
    <a href="../../index.html">← All Work</a>
  </footer>

</body>
</html>
"""


def build_cases(dna: dict = None, dry: bool = False, slug: str = None) -> list[str]:
    """Generate case study pages from DNA. Returns list of built pages."""
    if dna is None:
        dna = json.loads(IDENTITY.read_text())

    cases = dna.get("site", {}).get("cases", [])
    built = []

    for case in cases:
        if slug and case["slug"] != slug:
            continue

        case_dir = CASES_DIR / case["slug"]
        case_dir.mkdir(parents=True, exist_ok=True)
        out = case_dir / "index.html"

        html = render_case(case, dna)

        if not dry:
            out.write_text(html)
            print(f"   ✅ Built cases/{case['slug']}/index.html ({len(html):,} bytes)")
        else:
            print(f"   ✅ [DRY] Would build cases/{case['slug']}/index.html ({len(html):,} bytes)")

        built.append(case["slug"])

    return built


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CZR DNA Cases Builder")
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("--slug", type=str, help="Build only one case by slug")
    args = parser.parse_args()
    build_cases(dry=args.dry, slug=args.slug)
