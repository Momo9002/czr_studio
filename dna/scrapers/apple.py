"""
CZR DNA Scraper — Apple
Monitors apple.com for: product reveal copy, one-thing-per-beat structure,
CTA language, typography signals, neutral interface + vivid product patterns.
Output: dna/scrapers/reports/apple_YYYYMMDD.md
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
    "https://www.apple.com",
    "https://www.apple.com/iphone/",
    "https://www.apple.com/mac/",
    "https://www.apple.com/shop/buy-iphone",
]

CTA_PATTERNS = re.compile(
    r"\b(learn more|buy|get|shop|explore|discover|from|starting at|available|order)\b",
    re.IGNORECASE
)


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
    for tag in soup.find_all(["h1", "h2", "h3", "p"]):
        text = tag.get_text(strip=True)
        if 2 < len(text) < 200 and not text.startswith(("©", "Cookie", "Skip")):
            snippets.append(text)
    return list(dict.fromkeys(snippets))[:50]


def extract_ctas(soup: BeautifulSoup) -> list[str]:
    """Extract CTA button/link text to understand Apple's invitation language."""
    ctas = []
    for tag in soup.find_all(["a", "button"]):
        text = tag.get_text(strip=True)
        if CTA_PATTERNS.search(text) and 2 < len(text) < 40:
            ctas.append(text)
    return list(dict.fromkeys(ctas))[:15]


def analyse_copy(snippets: list[str]) -> dict:
    if not snippets:
        return {}
    lengths = [len(s.split()) for s in snippets]
    fragments = sum(1 for s in snippets if len(s.split()) <= 4)
    no_exclaim = sum(1 for s in snippets if "!" not in s)
    # Apple often uses period-free headlines
    no_period = sum(1 for s in snippets if not s.endswith(".") and len(s.split()) < 10)
    return {
        "avg_words": round(sum(lengths) / len(lengths), 1),
        "fragment_headlines_pct": round(fragments / len(snippets) * 100),
        "no_exclamation_pct": round(no_exclaim / len(snippets) * 100),
        "no_period_short_pct": round(no_period / len(snippets) * 100),
        "total_snippets": len(snippets),
    }


def scrape() -> dict:
    print("🔍 Scraping APPLE...")
    all_copy:  list[str] = []
    all_ctas:  list[str] = []

    for url in TARGETS:
        soup = fetch(url)
        if not soup:
            continue
        all_copy.extend(extract_copy(soup))
        all_ctas.extend(extract_ctas(soup))

    deduped_copy = list(dict.fromkeys(all_copy))[:35]
    deduped_ctas = list(dict.fromkeys(all_ctas))[:12]
    analysis = analyse_copy(deduped_copy)

    return {
        "model":      "Apple",
        "scraped_at": datetime.now().isoformat(),
        "copy_samples": deduped_copy[:20],
        "cta_samples": deduped_ctas,
        "analysis": analysis,
        "czr_signals": _derive_czr_signals(deduped_copy, deduped_ctas, analysis),
    }


def _derive_czr_signals(snippets: list[str], ctas: list[str], analysis: dict) -> list[str]:
    signals = []
    if analysis.get("fragment_headlines_pct", 0) > 30:
        signals.append("Apple uses fragment headlines heavily — CZR can use 1-3 word section headers")
    if analysis.get("no_exclamation_pct", 0) > 95:
        signals.append("Apple zero exclamation marks — CZR rule validated")
    # CTA analysis
    soft_ctas = [c for c in ctas if any(w in c.lower() for w in ["learn", "explore", "discover"])]
    if soft_ctas:
        signals.append(f"Apple soft CTAs: {soft_ctas[:3]} — CZR 'Start a Project' is correct register")
    # Price signal
    price_lines = [s for s in snippets if "from $" in s or "from €" in s or "starting" in s.lower()]
    if price_lines:
        signals.append(f"Apple states price simply: {price_lines[:2]} — validate CZR pricing copy")
    avg = analysis.get("avg_words", 10)
    if avg < 8:
        signals.append(f"Apple copy avg {avg} words — one-thing-per-beat validated")
    return signals


def write_report(data: dict, reports_dir: Path) -> Path:
    date = datetime.now().strftime("%Y%m%d_%H%M")
    path = reports_dir / f"apple_{date}.md"
    lines = [
        f"# Apple Scrape Report — {datetime.now().strftime('%B %d, %Y %H:%M')}",
        "",
        "## Copy Samples",
        *[f"- {s}" for s in data["copy_samples"]],
        "",
        "## CTA Samples",
    ]
    if data["cta_samples"]:
        lines += [f"- {c}" for c in data["cta_samples"]]
    else:
        lines += ["- (none extracted)"]
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
    print(f"  📊 {len(data['cta_samples'])} CTAs · {len(data['czr_signals'])} signals")
