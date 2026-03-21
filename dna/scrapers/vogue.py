"""
CZR DNA Scraper — Vogue
Monitors vogue.com for editorial patterns: headline style, copy structure,
color signals, image treatment, white space philosophy.
Output: dna/scrapers/reports/vogue_YYYYMMDD.md
"""

import re
import json
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

TARGETS = [
    "https://www.vogue.com",
    "https://www.vogue.com/fashion",
    "https://www.vogue.com/beauty",
]


def fetch(url: str) -> BeautifulSoup | None:
    try:
        r = httpx.get(url, headers=HEADERS, timeout=12, follow_redirects=True)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ⚠️  Failed to fetch {url}: {e}")
        return None


def extract_headlines(soup: BeautifulSoup) -> list[str]:
    headlines = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(strip=True)
        if 4 < len(text) < 120:
            headlines.append(text)
    return list(dict.fromkeys(headlines))[:20]  # dedupe, cap at 20


def extract_copy_patterns(headlines: list[str]) -> dict:
    """Analyse headline patterns: length, capitalisation, punctuation."""
    if not headlines:
        return {}
    lengths = [len(h.split()) for h in headlines]
    has_period    = sum(1 for h in headlines if h.endswith("."))
    has_question  = sum(1 for h in headlines if "?" in h)
    title_case    = sum(1 for h in headlines if h.istitle() or h[0].isupper())
    return {
        "avg_headline_words": round(sum(lengths) / len(lengths), 1),
        "max_headline_words": max(lengths),
        "period_endings_pct": round(has_period / len(headlines) * 100),
        "question_pct":       round(has_question / len(headlines) * 100),
        "title_case_pct":     round(title_case / len(headlines) * 100),
    }


def extract_color_palette(soup: BeautifulSoup) -> list[str]:
    """Extract prominent CSS color values from inline styles."""
    colors = set()
    hex_pattern = re.compile(r"#([0-9a-fA-F]{3,6})")
    for tag in soup.find_all(style=True):
        colors.update(f"#{m}" for m in hex_pattern.findall(tag["style"]))
    # From <style> blocks
    for style in soup.find_all("style"):
        colors.update(f"#{m}" for m in hex_pattern.findall(style.get_text()))
    # Filter noise (white, black, very light greys)
    filtered = [c for c in colors if c.lower() not in ("#fff", "#ffffff", "#000", "#000000")]
    return sorted(filtered)[:12]


def scrape() -> dict:
    print("🔍 Scraping VOGUE...")
    all_headlines: list[str] = []
    all_colors: list[str] = []

    for url in TARGETS:
        soup = fetch(url)
        if not soup:
            continue
        all_headlines.extend(extract_headlines(soup))
        all_colors.extend(extract_color_palette(soup))

    deduped_headlines = list(dict.fromkeys(all_headlines))[:25]
    patterns = extract_copy_patterns(deduped_headlines)

    return {
        "model":     "Vogue",
        "scraped_at": datetime.now().isoformat(),
        "headlines": deduped_headlines,
        "copy_patterns": patterns,
        "colors_found": sorted(set(all_colors))[:10],
        "czr_signals": _derive_czr_signals(deduped_headlines, patterns),
    }


def _derive_czr_signals(headlines: list[str], patterns: dict) -> list[str]:
    """What should CZR take from what we observed today."""
    signals = []
    avg = patterns.get("avg_headline_words", 0)
    if avg < 7:
        signals.append(f"Vogue headlines avg {avg} words — reinforce CZR's max-15-word rule")
    if patterns.get("period_endings_pct", 0) > 20:
        signals.append("Vogue uses period endings — consistent with CZR voice rule")
    if patterns.get("title_case_pct", 0) > 70:
        signals.append("Vogue uses title case — reinforce label casing in CZR UI")
    # Look for power words
    power_words = {"exclusive", "inside", "the", "only", "now", "first"}
    found = [h for h in headlines if any(w in h.lower() for w in power_words)]
    if found:
        signals.append(f"Editorial authority words observed: {found[:3]}")
    return signals


def write_report(data: dict, reports_dir: Path) -> Path:
    date = datetime.now().strftime("%Y%m%d_%H%M")
    path = reports_dir / f"vogue_{date}.md"
    lines = [
        f"# Vogue Scrape Report — {datetime.now().strftime('%B %d, %Y %H:%M')}",
        "",
        "## Headlines Observed",
        *[f"- {h}" for h in data["headlines"]],
        "",
        "## Copy Pattern Analysis",
        *[f"- **{k}**: {v}" for k, v in data["copy_patterns"].items()],
        "",
        "## Colors Found",
        *[f"- `{c}`" for c in data["colors_found"]],
        "",
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
    print(f"  📊 {len(data['headlines'])} headlines · {len(data['czr_signals'])} signals")
