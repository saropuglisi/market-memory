"""Real-event schema. Isomorphic to mock: same field names + structures.

Order matters for downstream encoders (they read by key name only, so any field
order is fine, but exact key names are required).
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class RealEpisode:
    # identification
    id: str
    ticker: str
    date: str            # ISO YYYY-MM-DD (filing date)
    event_type: str = "earnings_8k"
    sector: str = "unknown"
    cik: str = ""

    # text
    text: str = ""        # primi 5000 char dell'Item 2.02 estratto
    text_full: str = ""   # versione completa (debug only)

    # macro / micro / semantic / reaction (same key names as mock)
    macro_features: dict = field(default_factory=dict)
    micro_features: dict = field(default_factory=dict)
    semantic_features: dict = field(default_factory=dict)
    reaction_30d: dict = field(default_factory=dict)

    # provenance / debug
    filing_url: str = ""
    accession: str = ""
    quarter: str = ""    # e.g. "2023Q3"
    market_cap_bn: Optional[float] = None

    def to_dict(self):
        return asdict(self)


MACRO_KEYS = ("vix", "yield_10y", "yield_curve_slope", "credit_spread", "dxy")
MICRO_KEYS = ("return_60d", "realized_vol_60d", "drawdown_from_high",
              "sector_return_60d", "relative_strength")
SEMANTIC_KEYS = ("confidence_score", "hedging_count", "guidance_direction",
                 "uncertainty_markers")
REACTION_KEYS = ("return", "realized_vol", "max_drawdown", "persistence")
