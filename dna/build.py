"""
CZR DNA — Site Builder
Reads identity.json and generates index.html.
index.html is a BUILD ARTIFACT — never hand-edit it.

Usage:
    python3 -m dna.build              # generates index.html
    python3 -m dna.build --stdout     # print to stdout instead of writing
    python3 -m dna.build --dry        # show what would change

Pipeline:
    vision.md + models.md → synthesize → identity.json → build.py → index.html
                                                       → sync.py  → style.css
"""

import json
import argparse
from pathlib import Path
from html import escape

ROOT = Path(__file__).parent.parent
DNA_DIR = Path(__file__).parent
IDENTITY = DNA_DIR / "identity.json"
OUTPUT = ROOT / "index.html"


def load() -> dict:
    return json.loads(IDENTITY.read_text())


# ── Section renderers ────────────────────────────────────────────────────────

def render_head(dna: dict) -> str:
    brand = dna["brand"]
    typo = dna["typography"]
    hero = dna.get("site", {}).get("hero", {})
    headline_text = hero.get("headline", "").replace("<br>", " ")
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(brand["name"])} — {escape(brand["tagline"])} {escape(headline_text)}</title>
  <meta name="description" content="Concierge-focused digital studio. Sprint from €{dna['packages']['sprint']['price']}. Flagship from €{dna['packages']['flagship']['price']}.">
  <meta property="og:title" content="{escape(brand["name"])} — {escape(brand["tagline"])}">
  <meta property="og:description" content="{escape(headline_text)}">
  <meta property="og:url" content="{brand["site"]}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{typo["google_fonts"]}" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
  <script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','your-pixel-id');fbq('track','PageView');</script>
</head>
<body>
"""


def _wa_url(dna: dict, msg: str = "I want to start a project with CZR Studio") -> str:
    phone = dna["brand"]["whatsapp"].replace("+", "").replace(" ", "")
    return f"https://wa.me/{phone}?text={msg.replace(' ', '%20')}"


def render_nav(dna: dict) -> str:
    site = dna.get("site", {})
    nav_items = site.get("nav", [])
    
    links = ""
    for item in nav_items:
        cls = ' class="nav-customer"' if item.get("style") == "underline" else ""
        links += f'        <a href="{item["href"]}"{cls}>{escape(item["label"])}</a>\n'
    
    return f"""  <nav class="nav nav-transparent" id="nav">
    <div class="nav-inner">
      <a href="/" class="nav-logo">{escape(dna["brand"]["name"][:3].upper())}</a>
      <div class="nav-links">
{links}      </div>
      <a id="wa-link" href="{_wa_url(dna)}" class="nav-agent-btn" target="_blank" rel="noopener">Talk to the Agent</a>
    </div>
  </nav>
"""


def render_hero(dna: dict) -> str:
    hero = dna.get("site", {}).get("hero", {})
    cta_copy = dna.get("site", {}).get("cta_copy", {})
    
    values_html = "\n".join(
        f'          <span>{escape(v)}</span>' for v in hero.get("values", [])
    )
    
    cta_text = cta_copy.get("primary", hero.get("cta", {}).get("text", "Talk to the Agent →"))
    btn_class = "btn-agent btn-orange" if hero.get("cta", {}).get("style") == "black" else "btn-agent"
    subheadline = hero.get("subheadline", "")
    
    return f"""  <section class="hero">
    <div class="hero-image-wrap">
      <img src="{hero.get('image', 'images/hero-bg.jpg')}" alt="" class="hero-img" aria-hidden="true">
      <div class="hero-overlay"></div>
    </div>
    <div class="hero-inner wrap hero-center">
      <div class="hero-left">
        <p class="hero-label">{hero.get("label", "")}</p>
        <h1>{hero.get("headline", "")}</h1>
        {f'<p class="hero-sub">{escape(subheadline)}</p>' if subheadline else ''}
        <div class="hero-values">
{values_html}
        </div>
        <a id="hero-cta" href="{_wa_url(dna)}" class="{btn_class}" target="_blank" rel="noopener">{cta_text}</a>
      </div>
    </div>
  </section>

  <div class="full-rule"></div>
"""


def render_work(dna: dict) -> str:
    cases = dna.get("site", {}).get("cases", [])
    work = dna.get("site", {}).get("work", {})
    cta_copy = dna.get("site", {}).get("cta_copy", {})
    
    label = work.get("label", "Selected Work")
    headline = work.get("headline", "The portfolio.")
    nudge = work.get("nudge", "Want work like this for your brand?")
    cta_text = cta_copy.get("nudge", "Talk to the Agent →")
    
    panels = ""
    for c in cases:
        panels += f"""      <a href="cases/{c['slug']}/index.html" class="case-panel">
        <div class="case-image" style="background-image:url('{c.get('image', '')}')"></div>
        <div class="case-info">
          <span class="case-cat">{escape(c.get('category', ''))}</span>
          <span class="case-title">{escape(c.get('title', ''))}</span>
        </div>
      </a>
"""
    
    return f"""  <section class="section" id="work">
    <div class="wrap">
      <header class="section-header">
        <span class="label">{escape(label)}</span>
        <h2>{escape(headline)}</h2>
      </header>
    </div>
    <div class="cases-grid">
{panels}    </div>
    <div class="wrap">
      <div class="section-cta-nudge">
        <p>{escape(nudge)}</p>
        <a href="{_wa_url(dna)}" class="btn-agent" target="_blank" rel="noopener">{cta_text}</a>
      </div>
    </div>
  </section>
"""


def render_process(dna: dict) -> str:
    steps = dna.get("site", {}).get("process", [])
    ps = dna.get("site", {}).get("process_section", {})
    
    label = ps.get("label", "How it works")
    headline = ps.get("headline", "Three steps.")
    
    steps_html = ""
    for s in steps:
        steps_html += f"""        <div class="process-step">
          <span class="step-n">{s['num']}</span>
          <h3 class="light">{escape(s['title'])}</h3>
          <p class="light-muted">{escape(s['text'])}</p>
        </div>
"""
    
    return f"""  <section class="section section-dark" id="process">
    <div class="wrap">
      <header class="section-header">
        <span class="label label-light">{escape(label)}</span>
        <h2 class="light">{escape(headline)}</h2>
      </header>
      <div class="process-grid">
{steps_html}      </div>
    </div>
  </section>
"""


def render_about(dna: dict) -> str:
    about = dna.get("site", {}).get("about", {})
    if not about:
        return ""
    
    stats_html = ""
    for stat in about.get("stats", []):
        stats_html += f"""        <div class="about-stat">
          <span class="about-stat-value">{escape(stat['value'])}</span>
          <span class="about-stat-label">{escape(stat['label'])}</span>
        </div>
"""
    
    return f"""  <section class="section section-grey" id="about">
    <div class="wrap about-wrap">
      <header class="section-header">
        <span class="label">{escape(about.get('label', 'The studio'))}</span>
        <h2>{escape(about.get('headline', ''))}</h2>
      </header>
      <p class="about-body">{escape(about.get('body', ''))}</p>
      <div class="about-stats">
{stats_html}      </div>
    </div>
  </section>
"""


def render_packages(dna: dict) -> str:
    pkgs = dna["packages"]
    ps = dna.get("site", {}).get("packages_section", {})
    feats = ps.get("features", {})
    cta_copy = dna.get("site", {}).get("cta_copy", {})
    
    label = ps.get("label", "The offer")
    headline = ps.get("headline", "One price.")
    subheadline = ps.get("subheadline", "No negotiation.")
    
    def feat_list(key, defaults):
        items = feats.get(key, defaults)
        return "\n".join(f'            <li>{escape(i)}</li>' for i in items)
    
    sprint_feats   = feat_list('sprint',   ['3-page website', 'Mobile-first', 'Lightning fast delivery', 'Full IP transfer'])
    flagship_feats = feat_list('flagship', ['Up to 8 pages', 'Brand consultation', 'CMS or e-commerce ready', '2 revision rounds', 'Full IP transfer'])
    retainer_feats = feat_list('retainer', ['2 updates per month', 'Priority response', 'Cancel anytime'])
    
    return f"""  <section class="section" id="packages">
    <div class="wrap">
      <header class="section-header">
        <span class="label">{escape(label)}</span>
        <h2>{escape(headline)}<br>{escape(subheadline)}</h2>
      </header>
      <div class="packages-grid">
        <div class="pkg">
          <span class="pkg-name">{escape(pkgs['sprint']['name'])}</span>
          <div class="pkg-price"><span class="pkg-cur">€</span>{pkgs['sprint']['price']}</div>
          <p class="pkg-line">{escape(pkgs['sprint']['tagline'])}</p>
          <ul>
{sprint_feats}
          </ul>
          <a href="{_wa_url(dna, 'I want to start The Sprint')}" class="btn-outline" target="_blank" rel="noopener">{escape(cta_copy.get('sprint', 'Start the Sprint →'))}</a>
        </div>
        <div class="pkg pkg-featured">
          <span class="pkg-badge">Complete</span>
          <span class="pkg-name">{escape(pkgs['flagship']['name'])}</span>
          <div class="pkg-price"><span class="pkg-cur">€</span>{pkgs['flagship']['price']}</div>
          <p class="pkg-line">{escape(pkgs['flagship']['tagline'])}</p>
          <ul>
{flagship_feats}
          </ul>
          <a href="{_wa_url(dna, 'I want to build The Flagship')}" class="btn-agent-sm" target="_blank" rel="noopener">{escape(cta_copy.get('flagship', 'Build the Flagship →'))}</a>
        </div>
        <div class="pkg">
          <span class="pkg-name">{escape(pkgs['retainer']['name'])}</span>
          <div class="pkg-price"><span class="pkg-cur">€</span>{pkgs['retainer']['price']}<span class="pkg-mo">/mo</span></div>
          <p class="pkg-line">{escape(pkgs['retainer']['tagline'])}</p>
          <ul>
{retainer_feats}
          </ul>
          <a href="{_wa_url(dna, 'I want The Retainer')}" class="btn-outline" target="_blank" rel="noopener">{escape(cta_copy.get('retainer', 'Start the Retainer →'))}</a>
        </div>
      </div>
    </div>
  </section>
"""


def render_faq(dna: dict) -> str:
    faqs = dna.get("faq", [])
    fs = dna.get("site", {}).get("faq_section", {})
    
    label = fs.get("label", "Questions")
    headline = fs.get("headline", "Answered.")
    
    items = ""
    for f in faqs:
        items += f"""        <details class="faq-item">
          <summary>{escape(f['q'])}</summary>
          <p>{escape(f['a'])}</p>
        </details>
"""
    items += """        <details class="faq-item">
          <summary>I am already a client — where do I access my project?</summary>
          <p>Log into your <a href="/dashboard.html" class="inline-link">Customer Area</a> to track your project, download assets, and communicate with the team.</p>
        </details>
"""
    
    return f"""  <section class="section section-grey" id="faq">
    <div class="wrap">
      <header class="section-header">
        <span class="label">{escape(label)}</span>
        <h2>{escape(headline)}</h2>
      </header>
      <div class="faq-list">
{items}      </div>
    </div>
  </section>
"""


def render_contact(dna: dict) -> str:
    contact = dna.get("site", {}).get("contact", {})
    
    return f"""  <section class="section" id="contact">
    <div class="wrap contact-wrap">
      <span class="label">{escape(contact.get('label', 'Start today'))}</span>
      <h2>{escape(contact.get('headline', 'Brief us.'))}</h2>
      <p class="contact-sub">{escape(contact.get('sub', ''))}</p>
      <a id="contact-cta" href="{_wa_url(dna)}" class="btn-agent btn-agent-lg" target="_blank" rel="noopener">{escape(contact.get('cta', 'Talk to the Agent →'))}</a>
    </div>
  </section>
"""


def render_footer(dna: dict) -> str:
    footer_links = dna.get("site", {}).get("footer", [])
    
    links = ""
    for link in footer_links:
        ext = ' target="_blank" rel="noopener"' if link.get("external") else ""
        links += f'        <a href="{link["href"]}"{ext}>{escape(link["label"])}</a>\n'
    
    return f"""  <footer class="footer">
    <div class="wrap footer-inner">
      <span class="footer-logo">{escape(dna["brand"]["name"][:3].upper())}</span>
      <span class="footer-tag">{escape(dna["brand"]["tagline"])}</span>
      <nav class="footer-nav">
{links}      </nav>
    </div>
  </footer>
"""


def render_scripts() -> str:
    return """  <script src="dna/inject.js" type="module"></script>
  <script>
    const nav = document.getElementById('nav');
    window.addEventListener('scroll', () => {
      nav.classList.toggle('nav-solid', window.scrollY > 60);
    }, { passive: true });
  </script>
</body>
</html>
"""


# ── Section registry ─────────────────────────────────────────────────────────

SECTION_RENDERERS = {
    "hero":     render_hero,
    "work":     render_work,
    "about":    render_about,
    "process":  render_process,
    "packages": render_packages,
    "faq":      render_faq,
    "contact":  render_contact,
}


# ── Main build ───────────────────────────────────────────────────────────────

def build_site(dna: dict = None, dry: bool = False) -> str:
    """Generate index.html from DNA. Returns the HTML string."""
    if dna is None:
        dna = load()
    
    sections_order = dna.get("site", {}).get("sections_order", 
        ["hero", "work", "process", "packages", "faq", "contact"])
    
    parts = [render_head(dna), render_nav(dna)]
    
    for section_id in sections_order:
        renderer = SECTION_RENDERERS.get(section_id)
        if renderer:
            parts.append(renderer(dna))
    
    parts.append(render_footer(dna))
    parts.append(render_scripts())
    
    html = "\n".join(parts)
    
    if not dry:
        OUTPUT.write_text(html)
        print(f"   ✅ Built index.html ({len(html):,} bytes, {len(sections_order)} sections)")
    else:
        print(f"   ✅ [DRY] Would build index.html ({len(html):,} bytes)")
    
    return html


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CZR DNA Site Builder")
    parser.add_argument("--dry", action="store_true", help="Don't write, just report")
    parser.add_argument("--stdout", action="store_true", help="Print HTML to stdout")
    args = parser.parse_args()
    
    html = build_site(dry=args.dry)
    if args.stdout:
        print(html)
