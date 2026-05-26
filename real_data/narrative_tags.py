"""Definition of the 12 binary narrative tags used by concat_eq+.

Each tag is a boolean property of an earnings press release. Tags are
designed to be:
- mutually informative across categories (4 categories × 3 tags)
- mostly orthogonal within each category
- interpretable to a human analyst
- extractable from a 2-3 sentence narrative summary

The tags become an additional binary vector in concat_eq+'s composite
similarity score (weight 0.25 by default).
"""
from __future__ import annotations

NARRATIVE_TAGS = {
    # ── Category A: direction of the surprise ────────────────────────────
    "beat_and_raise":
        "Did the company beat earnings AND raise guidance?",
    "miss_or_cut":
        "Did the company miss earnings OR cut guidance?",
    "inline_results":
        "Were results approximately in line with expectations?",

    # ── Category B: fundamental drivers ──────────────────────────────────
    "demand_strength":
        "Is strong demand explicitly mentioned as a driver?",
    "demand_weakness":
        "Is weak/declining demand explicitly mentioned?",
    "margin_pressure":
        "Are margin headwinds (cost inflation, FX, mix) mentioned?",
    "margin_expansion":
        "Is margin improvement (pricing power, efficiency) mentioned?",

    # ── Category C: strategy & capital ──────────────────────────────────
    "capex_increase":
        "Is increased capex or investment announced?",
    "buyback_or_dividend":
        "Is a buyback or dividend increase announced?",
    "restructuring_or_layoffs":
        "Is restructuring, layoffs, or a cost-cutting program mentioned?",

    # ── Category D: thematic narrative ──────────────────────────────────
    "supply_chain_issue":
        "Are supply chain problems explicitly mentioned?",
    "AI_or_tech_narrative":
        "Are AI, GenAI, or digital transformation themes mentioned?",
}

# Preserve insertion order for prompt + parsing consistency
TAG_KEYS = list(NARRATIVE_TAGS.keys())
N_TAGS = len(TAG_KEYS)

CATEGORIES = {
    "A_direction": ["beat_and_raise", "miss_or_cut", "inline_results"],
    "B_drivers": ["demand_strength", "demand_weakness",
                  "margin_pressure", "margin_expansion"],
    "C_capital": ["capex_increase", "buyback_or_dividend",
                  "restructuring_or_layoffs"],
    "D_themes": ["supply_chain_issue", "AI_or_tech_narrative"],
}

# Pairs that should rarely both be 1 (used by validation as sanity)
MUTUALLY_EXCLUSIVE_PAIRS = [
    ("beat_and_raise", "miss_or_cut"),
    ("beat_and_raise", "inline_results"),
    ("miss_or_cut", "inline_results"),
    ("demand_strength", "demand_weakness"),
    ("margin_pressure", "margin_expansion"),
]
