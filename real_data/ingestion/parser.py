"""Parse 8-K filings to extract Item 2.02 'Results of Operations' text."""
from __future__ import annotations
import re
import unicodedata
from bs4 import BeautifulSoup


def _clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "head"]):
        tag.decompose()
    return _clean(soup.get_text(separator=" "))


def extract_item_202(text: str) -> str | None:
    """Find the Item 2.02 section. Heuristic: look for header, take until next
    Item X.XX or end of document. Returns None if not present."""
    pattern = re.compile(r"item\s*2\.02[\s\.\-\:]*results?\s*of\s*operations", re.IGNORECASE)
    m = pattern.search(text)
    if not m:
        # weaker fallback: "Item 2.02" anywhere
        m = re.search(r"item\s*2\.02", text, re.IGNORECASE)
        if not m:
            return None
    start = m.start()
    # find next "Item X.XX" after this one
    next_item = re.search(r"item\s*\d\.\d{2}", text[m.end():], re.IGNORECASE)
    end = m.end() + next_item.start() if next_item else len(text)
    section = text[start:end]
    return _clean(section)


def parse_filing(html: str) -> dict:
    """Return {raw_text, item_202_text, has_item_202}."""
    raw = html_to_text(html)
    section = extract_item_202(raw)
    return {
        "raw_text": raw,
        "item_202_text": section or "",
        "has_item_202": section is not None,
    }


def parse_press_release(html_or_text: str) -> str:
    """Extract press-release body. Often includes 'forward-looking statements'
    boilerplate at end — keep but down-weight downstream via length cap."""
    if "<" in html_or_text[:500]:
        text = html_to_text(html_or_text)
    else:
        text = _clean(html_or_text)
    # Drop common boilerplate trailers
    text = re.split(r"(?:about [A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+){0,3}|forward[- ]looking statements|safe harbor|investor relations contacts|contact:)",
                    text, flags=re.IGNORECASE, maxsplit=1)[0]
    return _clean(text)


def select_press_release_exhibits(exhibits: list[dict]) -> list[str]:
    """Pick exhibit filenames likely to be the earnings press release.
    Convention: ex-99.1 / ex99-1 / ex991 etc."""
    candidates = []
    for ex in exhibits:
        name = ex.get("name", "").lower()
        if not name.endswith((".htm", ".html", ".txt")):
            continue
        if any(token in name for token in ("ex-99", "ex99", "exhibit99", "exhibit-99",
                                            "ex_99", "991", "ex-991")):
            candidates.append(ex["name"])
    return candidates
