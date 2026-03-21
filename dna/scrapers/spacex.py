"""
CZR DNA Scraper — SpaceX
Monitors spacex.com for: mission copy patterns, data-first language,
number usage, precision vocabulary, dark UI decisions.
Output: dna/scrapers/reports/spacex_YYYYMMDD.md
"""

import re
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

TARGETS = [
    "https://www.spacex.com",
    "https://www.spacex.com/vehicles/starship/",
    "https://www.spacex.com/vehicles/falcon-9/",
    "https://www.spacex.com/human-spaceflight/",
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
    snippets = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "span"]):
        text = tag.get_text(strip=True)
        if 2 < len(text) < 300 and not text.startswith(("©", "Cookie")):
            snippets.append(text)
    return list(dict.fromkeys(snippets))[:50]


def extract_numbers(snippets: list[str]) -> list[str]:
    """Find all data/stat statements — SpaceX is number-forward."""
    number_re = re.compile(r"\b\d[\d,.]*\s*(?:kg|km|mph|kph|lbs|tons?|meters?|ft|s|%|seconds?|hours?|times?|flights?|missions?|satellites?)?\b", re.IGNORECASE)
    hits = []
    for s in snippets:
        if number_re.search(s):
            hits.append(s)
    return hits[:15]


def analyse_copy(snippets: list[str]) -> dict:
    if not snippets:
        return {}
    lengths = [len(s.split()) for s in snippets]
    imperative = sum(1 for s in snippets if s.split()[0] if s and s.split()[0][0].isupper() and len(s.split()) < 6)
    no_exclaim  = sum(1 for s in snippets if "!" not in s)
    return {
        "avg_words": round(sum(lengths) / len(lengths), 1),
        "imperative_short_pct": round(imperative / len(snippets) * 100),
        "no_exclamation_pct": round(no_exclaim / len(snippets) * 100),
        "total_snippets": len(snippets),
    }


def scrape() -> dict:
    print("🔍 Scraping SPACEX...")
    all_copy: list[str] = []

    for url in TARGETS:
        soup = fetch(url)
        if not soup:
            continue
        all_copy.extend(extract_copy(soup))

    deduped = list(dict.fromkeys(all_copy))[:40]
    numbers = extract_numbers(deduped)
    analysis = analyse_copy(deduped)

    return {
        "model":      "SpaceX",
        "scraped_at": datetime.now().isoformat(),
        "copy_samples": deduped[:20],
        "data_statements": numbers,
        "analysis": analysis,
        "czr_signals": _derive_czr_signals(deduped, numbers, analysis),
    }


def _derive_czr_signals(snippets: list[str], numbers: list[str], analysis: dict) -> list[str]:
    signals = []
    if numbers:
        signals.append(f"SpaceX leads {len(numbers)} lines with raw numbers — reinforce CZR stat blocks (48h, 100%, €999)")
    avg = analysis.get("avg_words", 10)
    if avg < 10:
        signals.append(f"SpaceX copy avg {avg} words — mission-brief density, consistent with CZR")
    if analysis.get("no_exclamation_pct", 0) > 90:
        signals.append("SpaceX zero exclamation marks — CZR rule validated")
    # Look for mission-critical vocab
    mission_words = {"mission", "launch", "orbit", "payload", "reusable", "deploy"}
    found = [s for s in snippets if any(w in s.lower() for w in mission_words)]
    if found:
        signals.append(f"Mission vocabulary (map to CZR delivery language): {found[:2]}")
    return signals


def write_report(data: dict, reports_dir: Path) -> Path:
    date = datetime.now().strftime("%Y%m%d_%H%M")
    path = reports_dir / f"spacex_{date}.md"
    lines = [
        f"# SpaceX Scrape Report — {datetime.now().strftime('%B %d, %Y %H:%M')}",
        "",
        "## Copy Samples",
        *[f"- {s}" for s in data["copy_samples"]],
        "",
        "## Data Statements (number-forward lines)",
    ]
    if data["data_statements"]:
        lines += [f"- {s}" for s in data["data_statements"]]
    else:
        lines += ["- (none found — may be JS-rendered)"]
    lines += [
        "## Analysis",
        *[f"- **{k}**: {v}" for k, v in data["analysis"].items()],
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
    print(f"  📊 {len(data['data_statements'])} data statements · {len(data['czr_signals'])} signals")
