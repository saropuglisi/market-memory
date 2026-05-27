"""Narrative tags v2 — data-driven redesign.

Designed after analyzing the full-text n-gram statistics of all 500 8-K
events (see real_data/processed/text_concepts_analysis.md and
real_data/processed/tags_redesign_rationale.md).

Selection rule for each tag in this set:
  estimated frequency on the 500-event corpus is in [5%, 45%] when matched
  via a domain-specific regex seed. Tags below 5% (demand_weakness,
  capex_increase, AI_narrative, beat_and_raise from v1) were dropped or
  redefined. Tags above 45% under loose definitions (e.g. naive guidance
  match at 55%) were tightened so that they discriminate.

14 tags across 4 categories.
"""
from __future__ import annotations

NARRATIVE_TAGS_V2 = {
    # ── Category A — direction of the surprise / outcome framing ─────────
    "guidance_raise":
        "Did the company raise, increase, or update its forward guidance "
        "or outlook upward this period? Examples that qualify: 'raised "
        "full-year revenue guidance', 'narrowed guidance to the upper end', "
        "'increased outlook'.",
    "guidance_cut":
        "Did the company lower, reduce, withdraw, or suspend its forward "
        "guidance? Examples: 'lowered FY guidance', 'withdrew prior outlook', "
        "'reduced earnings forecast'.",
    "record_results":
        "Does management explicitly frame a metric as a record? Examples: "
        "'record revenue', 'all-time high backlog', 'best ever quarterly "
        "earnings'. Excludes routine year-over-year growth language.",

    # ── Category B — fundamental drivers ────────────────────────────────
    "demand_strength":
        "Is strong, robust, broad-based, or accelerating demand explicitly "
        "cited as the driver of results? Examples: 'strong demand across "
        "all segments', 'robust order intake', 'accelerating bookings'.",
    "margin_expansion":
        "Are gross, operating, or EBITDA margins explicitly described as "
        "expanding, improving, or widening this period?",
    "margin_pressure":
        "Are margins explicitly described as under pressure, compressed, "
        "contracting, or facing headwinds this period?",
    "cost_inflation":
        "Are inflationary cost pressures explicitly cited — e.g. raw "
        "material inflation, wage/labor inflation, freight, fuel, energy, "
        "commodity cost increases?",
    "pricing_action":
        "Are price increases, pricing actions, pricing power, or favorable "
        "price realization explicitly mentioned as a benefit this period?",

    # ── Category C — capital strategy & corporate action ───────────────
    "capital_return":
        "Did the company announce or execute share repurchases, a buyback "
        "authorization, a dividend increase, a special dividend, or "
        "explicitly emphasize 'returning capital to shareholders'?",
    "MA_activity":
        "Did the company announce or close an acquisition, merger, "
        "divestiture, spin-off, or sale of a business segment this period? "
        "Generic 'combined entity' language without a specific event does "
        "NOT qualify.",
    "restructuring":
        "Did the company announce restructuring, reorganization, layoffs, "
        "workforce/headcount reduction, or a cost-savings/simplification "
        "program?",

    # ── Category D — thematic narratives / external factors ─────────────
    "supply_constraint":
        "Are supply chain issues, component/chip shortages, capacity "
        "constraints, or inventory/logistics tightness explicitly mentioned "
        "as factors affecting the business?",
    "FX_headwind":
        "Are currency/FX/foreign-exchange impacts explicitly cited as a "
        "headwind, pressure, or unfavorable factor on results?",
    "ESG_sustainability":
        "Are ESG, sustainability initiatives, carbon-neutral / net-zero "
        "commitments, renewable energy, or decarbonization themes "
        "explicitly mentioned as part of the strategic narrative?",
}

TAG_KEYS_V2 = list(NARRATIVE_TAGS_V2.keys())
N_TAGS_V2 = len(TAG_KEYS_V2)

CATEGORIES_V2 = {
    "A_outcome":  ["guidance_raise", "guidance_cut", "record_results"],
    "B_drivers":  ["demand_strength", "margin_expansion", "margin_pressure",
                   "cost_inflation", "pricing_action"],
    "C_capital":  ["capital_return", "MA_activity", "restructuring"],
    "D_thematic": ["supply_constraint", "FX_headwind", "ESG_sustainability"],
}

# Mutually-exclusive pairs (validation should report contradictions but
# Qwen may occasionally produce 1+1 on these — small contradiction rate
# is acceptable since the press release CAN contain both signals).
MUTUALLY_EXCLUSIVE_PAIRS_V2 = [
    ("guidance_raise", "guidance_cut"),
    ("margin_expansion", "margin_pressure"),
    # demand_strength + demand_weakness was paired in v1; v2 dropped
    # demand_weakness (freq <2%) so no pair here.
]

# Estimated frequencies on the 500-event corpus (from regex seed analysis).
# These are upper-bound estimates — Qwen extraction with strict YES/NO is
# typically more conservative, so realized Qwen frequencies will likely
# be 50-80% of these values.
ESTIMATED_FREQUENCIES = {
    "guidance_raise":     0.376,
    "capital_return":     0.306,
    "MA_activity":        0.176,
    "restructuring":      0.166,
    "record_results":     0.154,
    "margin_pressure":    0.132,
    "guidance_cut":       0.124,
    "supply_constraint":  0.122,
    "margin_expansion":   0.110,
    "demand_strength":    0.106,
    "pricing_action":     0.084,
    "ESG_sustainability": 0.074,
    "cost_inflation":     0.070,
    "FX_headwind":        0.068,
}
