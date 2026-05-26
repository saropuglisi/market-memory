"""Boilerplate removal for SEC 8-K Item 2.02 press release texts.

Removes systematic noise observed in sample_50:
- EX-99 SGML header garbage at top
- Item 2.02 announcement boilerplate (when full PR is below)
- Conference call / webcast logistics (phone numbers, access codes)
- Investor relations / media contact blocks
- Forward-looking statements + safe harbor disclaimers
- Exhibit listings
- Trailing page numbers / pagination artifacts

API:
    cleaned, stats = clean_text(raw)
    stats = {"removed_chars": int, "removed_pct": float, "patterns_hit": [str]}
"""
from __future__ import annotations
import re
from typing import Tuple


# Header noise: "EX-99.1 2 d528939dex991.htm EX-99.1 EX-99.1 Exhibit 99.1 P R E S S R E L E A S E"
HEADER_EX99 = re.compile(
    r"^\s*EX[-_]?99[\.\-_]?\d*\s+\d*\s*[a-z0-9_\-\.]+\.(?:htm|html|txt)\s*"
    r"(?:EX[-_]?99[\.\-_]?\d*\s*)*"
    r"(?:Exhibit\s*99[\.\-_]?\d*\s*)?"
    r"(?:P\s*R\s*E\s*S\s*S\s+R\s*E\s*L\s*E\s*A\s*S\s*E\s*)?",
    re.IGNORECASE,
)

# Generic exhibit prefix that may appear without filename
HEADER_EXHIBIT_ONLY = re.compile(
    r"^\s*Exhibit\s*99[\.\-_]?\d*\s*(?:P\s*R\s*E\s*S\s*S\s+R\s*E\s*L\s*E\s*A\s*S\s*E\s*)?",
    re.IGNORECASE,
)

# Item 2.02 announcement boilerplate — appears when only the 8-K cover is in text.
# Pattern: "Item 2.02 Results of Operations... press release ... furnished as Exhibit 99.1..."
ITEM_202_BOILERPLATE = re.compile(
    r"Item\s*2\.02\s*Results?\s*of\s*Operations[^.]*\.\s*"
    r"On\s+[A-Z][a-z]+\s+\d+,\s*\d{4},\s*[^.]+(?:issued|announced|reported)[^.]+\.\s*"
    r"(?:The\s+full\s+text\s+of\s+the\s+press\s+release\s+is\s+furnished[^.]+\.\s*)?"
    r"(?:The\s+information\s+in\s+this\s+Current\s+Report[^.]+\.\s*)?"
    r"(?:This\s+information\s+shall\s+not\s+be\s+deemed[^.]+\.\s*)?",
    re.IGNORECASE,
)

# Conference call / webcast trailer (often final ~500-1500 chars)
CONF_CALL_TRAILER = re.compile(
    r"(?:Conference\s+Call\s+(?:and|&)\s+Webcast|Webcast\s+(?:and|&)\s+Conference\s+Call|"
    r"Earnings\s+Conference\s+Call)\b.*",
    re.IGNORECASE | re.DOTALL,
)

# Investor/Media contacts trailer
CONTACTS_TRAILER = re.compile(
    r"(?:Investor\s+Relations\s+Contacts?|Media\s+Contacts?|"
    r"[A-Z][A-Za-z\s]{2,40}\s+Contacts?:|Contact:|For\s+(?:more\s+)?information,?\s+(?:please\s+)?contact)\b.*",
    re.IGNORECASE | re.DOTALL,
)

# Forward-looking statements disclaimer (multi-sentence chunk)
FLS_DISCLAIMER = re.compile(
    r"(?:Forward[-\s]Looking\s+Statements?|Cautionary\s+(?:Note|Statement)\s+(?:Regarding|on)\s+Forward[-\s]Looking|"
    r"Safe\s+Harbor(?:\s+Statement)?)\b.*",
    re.IGNORECASE | re.DOTALL,
)

# Phone/dial-in lines (defensive — if conf-call removal misses)
PHONE_LINE = re.compile(
    r"(?:Dial[- ]in|Toll[- ]free|Domestic(?:\s+Replay)?|International(?:\s+Replay)?|Access\s+Code|Passcode)[^\n.]*"
    r"(?:\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\d{4,})",
    re.IGNORECASE,
)

# Trailing page numbers like " 5" " 14 " repeated
PAGE_NUM_TAIL = re.compile(r"\s+\d{1,3}\s*$")

# Multiple spaces collapse
WHITESPACE = re.compile(r"\s+")


_PATTERNS = [
    ("header_ex99", HEADER_EX99),
    ("header_exhibit_only", HEADER_EXHIBIT_ONLY),
    ("item_202_boilerplate", ITEM_202_BOILERPLATE),
    ("fls_disclaimer", FLS_DISCLAIMER),
    ("conf_call_trailer", CONF_CALL_TRAILER),
    ("contacts_trailer", CONTACTS_TRAILER),
    ("phone_line", PHONE_LINE),
]


def clean_text(raw: str) -> Tuple[str, dict]:
    """Apply boilerplate removal. Returns (cleaned_text, stats_dict)."""
    if not raw:
        return "", {"removed_chars": 0, "removed_pct": 0.0, "patterns_hit": [],
                    "orig_len": 0, "clean_len": 0}
    orig_len = len(raw)
    text = raw
    hit = []
    for name, pat in _PATTERNS:
        new = pat.sub(" ", text)
        if len(new) != len(text):
            hit.append(name)
        text = new
    # Collapse whitespace, strip page-tail
    text = WHITESPACE.sub(" ", text).strip()
    text = PAGE_NUM_TAIL.sub("", text).strip()
    clean_len = len(text)
    removed = orig_len - clean_len
    return text, {
        "orig_len": orig_len,
        "clean_len": clean_len,
        "removed_chars": removed,
        "removed_pct": round(100.0 * removed / orig_len, 2) if orig_len else 0.0,
        "patterns_hit": hit,
    }
