"""Loughran-McDonald semantic features."""
from __future__ import annotations
import re
import pandas as pd
import pysentiment2 as ps

# Load LM master dictionary once
_LM_DF = pd.read_csv(ps.LM().PATH)

POSITIVE = set(_LM_DF.loc[_LM_DF["Positive"] > 0, "Word"].str.upper())
NEGATIVE = set(_LM_DF.loc[_LM_DF["Negative"] > 0, "Word"].str.upper())
UNCERTAINTY = set(_LM_DF.loc[_LM_DF["Uncertainty"] > 0, "Word"].str.upper())
# LM Modal: 1=strong, 2=moderate, 3=weak. We treat weak (3) as hedging.
WEAK_MODAL = set(_LM_DF.loc[_LM_DF["Modal"] == 3, "Word"].str.upper())

_TOKEN_RE = re.compile(r"[A-Za-z]+")

# --- Guidance direction classifier ---
# Three layers (priority: raise > lower > neutral). Each layer = list of regex
# patterns. We count matches per layer and assign direction by max.

# "guidance noun" — the thing being raised/lowered/maintained.
_GUIDE_NOUN = (
    r"(?:full[- ]year\s+|fy\s+|fiscal[- ]year\s+|annual\s+|quarterly\s+|next[- ]quarter\s+|"
    r"forward\s+|prior\s+|previous\s+|fourth[- ]quarter\s+|third[- ]quarter\s+|second[- ]quarter\s+|first[- ]quarter\s+|q[1-4]\s+)?"
    r"(?:guidance|outlook|forecast|estimat\w+|projection\w*|target\w*|expectation\w*|earnings\s+(?:guidance|outlook))"
)
# Direct verbs near the guidance noun (within ~80 chars)
_RAISE_VERBS = r"(?:rais\w+|increas\w+|lift\w+|upward\w*|boost\w+|improv\w+|hik\w+|expand\w+|higher|above\s+prior)"
_LOWER_VERBS = r"(?:lower\w+|reduc\w+|cut\w*|cutting|trim\w+|moderat\w+|decreas\w+|downward\w*|below\s+prior|reduc\w+|weaken\w+|narrow\w+\s+(?:to|toward)\s+(?:lower|low\s+end))"
_NEUTRAL_VERBS = r"(?:maintain\w+|reiterat\w+|reaffirm\w+|confirm\w+|unchanged|in\s+line\s+with\s+(?:prior|previous))"

# Forward-projection forms ("we expect/anticipate/forecast/project ... above|below|in line")
_EXPECT_VERB = r"(?:we\s+(?:now\s+)?(?:expect|anticipate|forecast|project|see|estimate)|now\s+expects?|company\s+expects?|continues?\s+to\s+expect)"
_EXPECT_HIGHER = r"(?:greater\s+than|above|exceed\w*|in\s+excess\s+of|higher\s+than|stronger\s+than|better\s+than|to\s+grow|to\s+increase|to\s+rise)"
_EXPECT_LOWER = r"(?:less\s+than|below|short\s+of|lower\s+than|weaker\s+than|softer\s+than|to\s+decline|to\s+decrease|to\s+fall|to\s+contract)"

GUIDANCE_RAISE_PATTERNS = [
    re.compile(rf"\b{_RAISE_VERBS}\s+(?:our\s+|its\s+|the\s+)?{_GUIDE_NOUN}", re.IGNORECASE),
    re.compile(rf"\b{_GUIDE_NOUN}\s+(?:is\s+|was\s+|has\s+been\s+)?(?:rais\w+|increas\w+|lift\w+|revis\w+\s+upward)", re.IGNORECASE),
    re.compile(rf"\b{_EXPECT_VERB}\b[^.]{{0,120}}\b{_EXPECT_HIGHER}\b", re.IGNORECASE),
    re.compile(r"\bnow\s+expects?\b[^.]{0,80}\b(?:greater\s+than|above|exceed\w*)\b", re.IGNORECASE),
    re.compile(rf"\b(?:guidance|outlook|forecast)\s+(?:has\s+been\s+|was\s+|is\s+)?(?:rais\w+|increas\w+|revis\w+\s+upward)", re.IGNORECASE),
    re.compile(r"\b(?:above|at\s+the\s+(?:high|upper)\s+end\s+of|toward\s+the\s+(?:high|upper)\s+end\s+of)\b[^.]{0,40}\b(?:midpoint|guidance|range|outlook|expectation\w*|prior\s+(?:guidance|range))\b", re.IGNORECASE),
    re.compile(r"\b(?:better\s+than\s+expected|stronger\s+than\s+expected|ahead\s+of\s+(?:our\s+)?(?:plan|expectations|guidance))\b", re.IGNORECASE),
    re.compile(r"\b(?:exceed\w+|surpass\w+|beat|topped|outperform\w+)\b[^.]{0,40}\b(?:guidance|estimate\w*|expectation\w*|consensus|outlook)\b", re.IGNORECASE),
]

GUIDANCE_LOWER_PATTERNS = [
    re.compile(rf"\b{_LOWER_VERBS}\s+(?:our\s+|its\s+|the\s+)?{_GUIDE_NOUN}", re.IGNORECASE),
    re.compile(rf"\b{_GUIDE_NOUN}\s+(?:is\s+|was\s+|has\s+been\s+)?(?:lower\w+|reduc\w+|cut|revis\w+\s+downward)", re.IGNORECASE),
    re.compile(rf"\b{_EXPECT_VERB}\b[^.]{{0,120}}\b{_EXPECT_LOWER}\b", re.IGNORECASE),
    re.compile(r"\bnow\s+expects?\b[^.]{0,80}\b(?:less\s+than|below|short\s+of)\b", re.IGNORECASE),
    re.compile(rf"\b(?:guidance|outlook|forecast)\s+(?:has\s+been\s+|was\s+|is\s+)?(?:lower\w+|reduc\w+|cut|revis\w+\s+downward)", re.IGNORECASE),
    re.compile(r"\b(?:below|at\s+the\s+(?:low|lower)\s+end\s+of|toward\s+the\s+(?:low|lower)\s+end\s+of)\b[^.]{0,40}\b(?:midpoint|guidance|range|outlook|prior\s+(?:guidance|range))\b", re.IGNORECASE),
    re.compile(r"\b(?:missed|fell\s+short\s+of|underperform\w+|below\s+(?:our\s+)?prior)\b[^.]{0,40}\b(?:guidance|estimate\w*|expectation\w*|consensus)\b", re.IGNORECASE),
]

GUIDANCE_NEUTRAL_PATTERNS = [
    re.compile(rf"\b{_NEUTRAL_VERBS}\s+(?:our\s+|its\s+|the\s+)?{_GUIDE_NOUN}", re.IGNORECASE),
    re.compile(rf"\b{_GUIDE_NOUN}\s+(?:is\s+|was\s+|remains?\s+|stays?\s+)?(?:unchanged|reaffirm\w+|reiterat\w+|maintain\w+)", re.IGNORECASE),
    re.compile(rf"\b(?:reaffirm\w+|reiterat\w+|maintain\w+|confirm\w+|affirm\w+)\s+(?:our\s+|its\s+|the\s+|prior\s+|long[- ]term\s+)?{_GUIDE_NOUN}", re.IGNORECASE),
    re.compile(rf"\b(?:initiat\w+|narrow\w+|tighten\w+|provid\w+|introduc\w+)\s+(?:our\s+|its\s+|the\s+|a\s+|new\s+|updated\s+)?{_GUIDE_NOUN}", re.IGNORECASE),
    re.compile(rf"\b(?:expect\w+|forecast\w+|project\w+)\s+(?:our\s+|its\s+|the\s+|next[- ]quarter\s+|full[- ]year\s+|FY\s+|fiscal\s+|quarterly\s+)?(?:operating\s+earnings|EPS|revenue|earnings|sales|results)\s+(?:to\s+be\s+|of\s+|in\s+the\s+range\s+of|between)", re.IGNORECASE),
    re.compile(r"\b(?:revenue|earnings|EPS|sales|operating\s+earnings|results|net\s+income)\b[^.]{0,80}\b(?:is|are|will\s+be)\s+expected\s+to\s+be\s+(?:in\s+the\s+range\s+of|between|approximately|of)", re.IGNORECASE),
    re.compile(r"\bexpects?\b[^.]{0,40}\b(?:operating\s+earnings|EPS|revenue|earnings|sales|net\s+income|results)\b[^.]{0,40}\b(?:in\s+the\s+range\s+of|between|to\s+be\s+in)", re.IGNORECASE),
]


def tokens_upper(text: str) -> list[str]:
    return [m.group(0).upper() for m in _TOKEN_RE.finditer(text)]


def semantic_features_for(text: str) -> dict:
    toks = tokens_upper(text)
    n = max(1, len(toks))
    pos = sum(1 for t in toks if t in POSITIVE)
    neg = sum(1 for t in toks if t in NEGATIVE)
    unc = sum(1 for t in toks if t in UNCERTAINTY)
    hedge = sum(1 for t in toks if t in WEAK_MODAL)
    confidence = pos / (pos + neg) if (pos + neg) > 0 else 0.5
    raise_hits = sum(1 for p in GUIDANCE_RAISE_PATTERNS if p.search(text))
    lower_hits = sum(1 for p in GUIDANCE_LOWER_PATTERNS if p.search(text))
    neutral_hits = sum(1 for p in GUIDANCE_NEUTRAL_PATTERNS if p.search(text))
    if raise_hits > lower_hits and raise_hits > 0:
        gd = 1
    elif lower_hits > raise_hits and lower_hits > 0:
        gd = -1
    elif neutral_hits > 0:
        gd = 0
    else:
        gd = 0
    return {
        "confidence_score": float(confidence),
        "hedging_count": int(hedge),
        "guidance_direction": int(gd),
        "uncertainty_markers": int(unc),
    }
