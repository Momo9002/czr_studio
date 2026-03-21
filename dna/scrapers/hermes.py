"""
CZR DNA Scraper — Hermès
Monitors hermes.com for: restraint in copy, accent color usage,
product description patterns, silence philosophy, spacing signals.
Output: dna/scrapers/reports/hermes_YYYYMMDD.md
"""

import re
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

TARGETS = [
    "https://www.hermes.com/us/en/",
    "https://www.hermes.com/us/en/category/men/bags-and-small-leather-goods/bags-and-clutches/",
    "https://www.hermes.com/us/en/content/291399-story-of-a-craft/",
]


def fetch(url: str) -> BeautifulSoup | None:
    try:
        r = httpx.get(url, headers=HEADERS, timeout=14, follow_redirects=True)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ⚠️  Failed to fetch {url}: {e}")
        return None


def extract_copy(soup: BeautifulSoup) -> list[str]:
    """Get all text nodes — headlines, product names, descriptions."""
    snippets = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "figcaption", "span"]):
        text = tag.get_text(strip=True)
        if 2 < len(text) < 200 and not text.startswith(("©", "Cookie", "Accept")):
            snippets.append(text)
    return list(dict.fromkeys(snippets))[:40]


def analyse_copy(snippets: list[str]) -> dict:
    if not snippets:
        return {}
    words_per = [len(s.split()) for s in snippets]
    chars_per  = [len(s) for s in snippets]
    short_lines = sum(1 for s in snippets if len(s.split()) <= 5)
    no_exclaim  = sum(1 for s in snippets if "!" not in s)
    return {
        "avg_words_per_snippet": round(sum(words_per) / len(words_per), 1),
        "avg_chars_per_snippet": round(sum(chars_per) / len(chars_per)),
        "short_lines_pct":       round(short_lines / len(snippets) * 100),
        "no_exclamation_pct":    round(no_exclaim / len(snippets) * 100),
        "total_snippets":        len(snippets),
    }


def find_orange_usage(soup: BeautifulSoup) -> list[str]:
    """Look for Hermès orange (#E8601C, #e87722, adjacent) in inline styles and CSS."""
    orange_hits = []
    # Known Hermès orange variants
    orange_patterns = [
        r"e860[0-9a-fA-F]{2}",  # ~#E8601C family
        r"e877[0-9a-fA-F]{2}",  # #E87722 variant
        r"f36[0-9a-fA-F]{3}",   # orangey reds
    ]
    combined = re.compile("|".join(orange_patterns), re.IGNORECASE)
    for tag in soup.find_all(style=True):
        if combined.search(tag["style"]):
            orange_hits.append(tag.get_text(strip=True)[:60])
    for style in soup.find_all("style"):
        matches = combined.findall(style.get_text())
        if matches:
            orange_hits.append(f"CSS: found #{matches[0]}")
    return orange_hits[:5]


def scrape() -> dict:
    print("🔍 Scraping HERMÈS...")
    all_copy: list[str] = []
    all_orange: list[str] = []

    for url in TARGETS:
        soup = fetch(url)
        if not soup:
            continue
        all_copy.extend(extract_copy(soup))
        all_orange.extend(find_orange_usage(soup))

    deduped = list(dict.fromkeys(all_copy))[:35]
    analysis = analyse_copy(deduped)

    return {
        "model":      "Hermès",
        "scraped_at": datetime.now().isoformat(),
        "copy_samples": deduped[:20],
        "analysis": analysis,
        "orange_usage": list(dict.fromkeys(all_orange))[:5],
        "czr_signals": _derive_czr_signals(deduped, analysis),
    }


def _derive_czr_signals(snippets: list[str], analysis: dict) -> list[str]:
    signals = []
    avg = analysis.get("avg_words_per_snippet", 10)
    if avg < 8:
        signals.append(f"Hermès copy avg {avg} words/line — reinforce CZR short-sentence rule")
    if analysis.get("no_exclamation_pct", 0) > 95:
        signals.append("Hermès never uses exclamation marks — consistent with CZR non-negotiable")
    if analysis.get("short_lines_pct", 0) > 40:
        signals.append("Hermès prefers short, declarative lines — use in CZR guarantee + pricing copy")
    # Look for restraint vocabulary
    restraint_words = {"craft", "atelier", "since", "tradition", "hand", "object"}
    found = [s for s in snippets if any(w in s.lower() for w in restraint_words)]
    if found:
        signals.append(f"Craft vocabulary: {found[:2]}")
    return signals


def write_report(data: dict, reports_dir: Path) -> Path:
    date = datetime.now().strftime("%Y%m%d_%H%M")
    path = reports_dir / f"hermes_{date}.md"
    lines = [
        f"# Hermès Scrape Report — {datetime.now().strftime('%B %d, %Y %H:%M')}",
        "",
        "## Copy Samples",
        *[f"- {s}" for s in data["copy_samples"]],
        "",
        "## Analysis",
        *[f"- **{k}**: {v}" for k, v in data["analysis"].items()],
        "",
        "## Hermès Orange Usage Found",
    ]
    if data["orange_usage"]:
        lines += [f"- {o}" for o in data["orange_usage"]]
    else:
        lines += ["- (none detected in page source — likely JS-rendered)"]
    lines += [
        "## CZR Signals — What to Consider Updating",
        *[f"- {s}" for s in data["czr_signals"]],
        "",
        "---",
        f"_Scraped: {data['scraped_at']}_",
    ]
    path.write_text("\n".join(lines))
    return path


if __name__ == "__main__":
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    data = scrape()
    report = write_report(data, reports_dir)
    print(f"  ✅ Report written: {report.name}")
    print(f"  📊 {len(data['copy_samples'])} copy samples · {len(data['czr_signals'])} signals")
