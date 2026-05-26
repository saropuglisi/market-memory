"""
Genera mock_events_L<n>.json — dataset sintetico con ground truth nota.

Difficulty levels:
  L1: parametri base, ~9% noise (default originale).
  L2: stds × 1.5 + means shrink 35% verso grand mean + sector cross-pollination
      + 25 template per cluster (richer texts). Noise ~20%.
  L3: stds × 2.0, +15% eventi HYBRID, noise ~25%.
  L4: cluster differenziati SOLO su semantic_features.
  L5: cluster definiti dalla reaction_30d, features overlap (×1.8).

Uso:
  python generate_mock_dataset.py --difficulty 2 --out data/mock_events_L2.json
  python generate_mock_dataset.py --difficulty 1   # default out: data/mock_events_L1.json
"""
from __future__ import annotations
import argparse
import copy
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

SEED = 42


# ============================================================
# SECTOR / TICKER POOL (used for cross-pollination)
# ============================================================

SECTOR_TICKERS = {
    "tech":          ["NVDA", "AVGO", "AMD", "ANET", "VRT", "SMCI",
                      "MU", "WDC", "STX", "INTC", "QCOM", "MRVL"],
    "financial":     ["BAC", "WFC", "C", "KEY", "ZION", "RF", "JPM", "GS", "MS"],
    "consumer":      ["F", "GM", "WHR", "HBI", "VFC", "KMB", "RH", "TGT", "M"],
    "industrial":    ["CAT", "GE", "MMM", "ETN", "HON", "EMR", "DE"],
    "transport":     ["FDX", "UPS", "DAL", "LUV", "CSX", "NSC"],
    "healthcare":    ["JNJ", "PFE", "MRK", "ABBV", "BMY"],
}

# Per-cluster sector mix (sums to 1.0). Cross-pollination ~25-30%.
CLUSTER_SECTOR_MIX = {
    "A": {"tech": 0.70, "financial": 0.15, "consumer": 0.10, "industrial": 0.05},
    "B": {"consumer": 0.55, "industrial": 0.20, "financial": 0.15, "tech": 0.10},
    "C": {"tech": 0.45, "transport": 0.25, "consumer": 0.20, "industrial": 0.10},
    "D": {"financial": 0.65, "consumer": 0.10, "industrial": 0.15, "tech": 0.10},
}


def pick_sector(cluster_id: str) -> str:
    mix = CLUSTER_SECTOR_MIX[cluster_id]
    sectors = list(mix.keys())
    probs = list(mix.values())
    return str(np.random.choice(sectors, p=probs))


def pick_ticker(cluster_id: str) -> tuple[str, str]:
    sector = pick_sector(cluster_id)
    ticker = random.choice(SECTOR_TICKERS[sector])
    return ticker, sector


# ============================================================
# TEXT POOLS (~25 templates per cluster, richer + vocabulary-trigger sets)
# ============================================================

TEXTS = {
"A": [  # AI/growth euphoria
    "We're seeing accelerating demand across our AI infrastructure portfolio. Customer commitments reached record levels this quarter. Our guidance for next quarter reflects continued strength.",
    "Record demand for our datacenter solutions drove exceptional results. We are raising full-year guidance based on strong order backlog. Capacity expansion is on track.",
    "Demand environment remains exceptionally strong, particularly in AI accelerators. Customer pipeline visibility extends multiple quarters forward.",
    "Outstanding execution across all business lines this quarter, led by AI infrastructure. We're meaningfully raising guidance. The structural demand picture has never been stronger.",
    "Generative AI workloads are inflecting faster than we anticipated three months ago. Our hyperscaler customers continue to materially expand commitments. We are leaning into capacity.",
    "This was our strongest bookings quarter ever, with multi-year contracts representing the bulk of the upside. We see compounding momentum into next year.",
    "Order linearity through the quarter was exceptional. Customers are pulling forward orders to secure capacity. Revenue mix is shifting toward higher-margin AI products.",
    "Our AI roadmap is hitting milestones ahead of plan. Customer engagement has expanded from pilots to full deployments. Pricing power is firmly in our favor.",
    "We delivered another beat-and-raise quarter on the back of broad-based demand strength. Datacenter, networking, and high-performance silicon all contributed.",
    "End-customer demand signals remain explosive. We are sold out through next year and are working with suppliers to expand wafers. Visibility is the best in our company history.",
    "Hyperscalers, sovereigns, and enterprise are all bidding for capacity simultaneously. We have never seen this confluence of demand. Guidance reflects only conservative assumptions.",
    "Generative AI adoption inside our enterprise customers is moving from experiment to production at unprecedented speed. Our software-attach is compounding.",
    "We are seeing accelerating demand cohorts month over month. New customers added this quarter represent the largest single-quarter expansion we have logged.",
    "Pipeline conversion rates are at all-time highs. Enterprise CIO surveys we have run confirm AI infrastructure is the #1 budget priority. Booking trajectory remains exceptional.",
    "Backlog grew sequentially despite record shipments, indicating demand continues to outrun supply. Our manufacturing partners are adding shifts.",
    "Our product cycle is benefitting from a true platform shift. Customer total cost of ownership advantages are widening, not narrowing. Demand pull remains intense.",
    "Average selling prices expanded again this quarter on richer mix. We are not seeing any pricing pressure across the AI portfolio. Demand-supply imbalance persists.",
    "Software attach rates on our accelerated computing platforms doubled year over year. This is becoming a meaningful margin and stickiness driver.",
    # competitive / operational secondary
    "Demand for our AI silicon is accelerating, and our operational scale advantages continue to widen versus competitors. Yield improvements added another point to gross margin.",
    "Our competitive moat in accelerated networking strengthened materially this quarter. Operational throughput in our build-to-order facilities reached record levels.",
    "Beyond record demand, we are seeing operational excellence translate to faster fulfillment cycles. Competitive positioning in inference workloads continues to consolidate in our favor.",
    "Customer demand is strong, but the underlying competitive separation is what compounds. Our supply chain operational reliability is now a primary win-reason cited by customers.",
    "Operational execution this quarter was outstanding: lead times compressed, defect rates fell, and competitive win rates ticked up further. AI demand is the macro tailwind on top.",
    "We continue to extend our competitive lead through superior operational scale and engineering velocity. Demand momentum is the icing — the structural moat is the cake.",
    "Capacity expansion is tracking ahead of schedule operationally. Our competitive position in advanced packaging is a key differentiator we expect to monetize for multiple cycles.",
],
"B": [  # Margin compression / defensive late-cycle
    "The operating environment remains challenging. We are taking a more cautious view on the second half. Margin discipline and cost optimization remain our primary focus.",
    "Demand patterns have weakened meaningfully since our last call. We are implementing rigorous cost actions to protect profitability. Guidance reflects a more conservative outlook.",
    "While we delivered against expectations this quarter, forward visibility has deteriorated. We are emphasizing efficiency and capital discipline. Customer decision-making has elongated.",
    "Margin pressure intensified through the quarter as pricing dynamics shifted. We are focused on optimization and disciplined execution. The competitive environment requires patience.",
    "Volume softness was broad-based across categories. We are leaning into productivity programs to defend margin. Promotional intensity from competitors has stepped up.",
    "Consumer trade-down behavior accelerated in our middle-market segments. We are tightening SG&A and prioritizing cash generation. Guidance is revised lower for the year.",
    "Channel inventory remained elevated through the quarter. Our partners are pushing back on price. We are taking a measured approach to production.",
    "Input cost relief has slowed, and pricing pass-through has reached its limit. Margin recovery is now a multi-quarter project. We are cutting discretionary spend.",
    "We see continued moderation in core volumes. Cost productivity is offsetting only a portion of the gross margin headwind. We expect a softer second half.",
    "The promotional environment is irrational in several segments. We are choosing to protect margin over share in those categories. Volumes will reflect that discipline.",
    "Customer order books have shortened meaningfully. We are managing the business for cash conversion. Operating expense reductions are now company-wide.",
    "Working capital came in heavy this quarter as inventory accumulated. We are cutting forward production schedules. Margin guide-down primarily reflects de-leverage.",
    "Channel destocking continued to weigh on volumes. We expect another two quarters before normalization. We are emphasizing capital allocation discipline.",
    "Demand softness persisted across most categories. We are focused on operational efficiency and tight inventory control. Forward outlook remains conservative.",
    "Cost actions taken last quarter are tracking, but the demand backdrop is offsetting the benefit. We are prepared to take further measures if conditions deteriorate further.",
    "Our pricing posture has shifted defensive in three of four product lines. We are prioritizing customer retention over near-term margin expansion.",
    "Industrial customers in particular are deferring orders. We are right-sizing our cost base accordingly. Guidance reflects a multi-quarter trough scenario.",
    "Volume deleverage drove most of the gross margin compression this quarter. Cost takeout will be a primary 2026 priority.",
    # late-cycle explicit
    "This feels increasingly like a late-cycle dynamic. We are positioning the balance sheet defensively and pulling back on discretionary capex. Margin discipline is our late-cycle playbook.",
    "Indicators we monitor — credit conditions, customer payment behavior, hiring intentions — all point to a late-stage business cycle. Our actions assume cycle maturity.",
    "We are operating under the assumption that we are in the late innings of the current cycle. Defensive posture and balance sheet preservation are our priorities.",
    "Multiple late-cycle markers are now flashing: tightening credit, inventory overhangs in adjacent industries, consumer fatigue. We are managing accordingly.",
    "Our planning scenarios now lead with a late-cycle base case. We are pulling forward cost actions rather than waiting. Capital allocation skews toward buybacks over capacity.",
    "Late-cycle behavior is evident in our customer base — order deferrals, payment-term renegotiations, inventory caution. We are leaning into operating discipline.",
    "Cycle maturity is increasingly visible across our end markets. We are managing the business for through-cycle returns rather than near-term volume. Guide reflects this stance.",
],
"C": [  # Recovery surprise
    "We're seeing early signs of demand stabilization across key end markets. Inventory positions have normalized at most major customers. Leading indicators are improving.",
    "Trends improved through the quarter, particularly in our core segments. Customer engagement levels have increased materially. Our guidance reflects this gradual improvement.",
    "After several quarters of headwinds, we're observing stabilization. Channel inventory has worked through. New product cycles are gaining traction.",
    "Demand patterns showed sequential improvement across the quarter. Customer sentiment has shifted notably. Forward indicators are encouraging.",
    "End-market visibility is the best it has been in six quarters. We are seeing order rate improvement across most product families. Cautious optimism is warranted.",
    "Channel partners are starting to rebuild inventory after a long destock. Order rates are recovering off the bottom. We expect this to compound over coming quarters.",
    "Sequential growth returned across all geographies for the first time since the downturn started. We are increasing production rates modestly.",
    "Our backlog grew for the first time in five quarters. The composition is improving as well, with higher-margin product mix returning. We are guiding modestly higher.",
    "We are observing positive inflection signals across multiple leading indicators. Bookings, customer engagement, and pipeline conversion are all firming.",
    "After a difficult eighteen months, the order environment has clearly turned. New product wins are accelerating. Visibility is improving.",
    "Distributor sell-through has firmed materially. We see normalizing customer order patterns and the first signs of price discipline returning to the channel.",
    "Macro headwinds are easing in our key end markets. Cyclical bottoming signals are now broad-based. We are positioning for the upcycle.",
    "Customer feedback at recent industry events was uniformly more constructive. Pipeline activity is materially stronger than two quarters ago.",
    "We exited the quarter with the highest book-to-bill in seven quarters. Channel checks confirm the recovery is real and broadening.",
    "Memory pricing is firming and inventory levels in the channel have normalized. We are seeing the first early stages of cyclical recovery.",
    "Order pickup was broad across customer segments. Pricing is starting to firm after extended weakness. We see scope for sequential margin recovery.",
    "Customer order patterns suggest the demand trough is behind us. We are calibrating production to the firming demand signals.",
    "Sequential improvement across geographies and product lines suggests a durable trough. We are cautiously optimistic about second-half acceleration.",
    # competitive / operational secondary
    "Recovery is broad-based and our competitive position has strengthened during the downturn. Operational restructuring during the trough left us better-positioned than competitors.",
    "Improving demand is meeting an operationally leaner organization. Competitive share gains during the downturn are now amplifying the topline recovery.",
    "Recovery in end-market demand is being compounded by operational gains from the productivity work done over the past 18 months. Competitive positioning is the best in years.",
    "We are seeing demand recover and competitive intensity ease simultaneously. Operational discipline maintained through the trough is now translating to margin acceleration.",
    "End-market normalization is favorable, but the real story is our operational improvements and competitive share wins during the downcycle.",
    "Recovery is here, and we enter it with a stronger competitive moat and a leaner operational base. Both contribute to the guidance raise.",
    "Operational efficiency gains accumulated during the downturn are now translating to outsized margin leverage on the recovering volumes. Competitive dynamics are also improving.",
],
"D": [  # Liquidity stress / macro
    "The macroeconomic backdrop has become significantly more uncertain. We are monitoring developments closely and maintaining flexibility. We are not providing specific guidance at this time.",
    "Recent market developments create significant uncertainty for our outlook. We are taking a defensive posture given the macro headwinds. Liquidity management and balance sheet strength remain priorities.",
    "Given the rapidly evolving macro environment, we are adopting a more cautious stance. Multiple headwinds are converging across our business.",
    "The current market environment presents significant challenges across our portfolio. We are emphasizing capital preservation and operational flexibility. Visibility has diminished.",
    "Cross-asset volatility has spilled into our credit portfolio. Spreads have widened materially. We are tightening underwriting standards across all desks.",
    "Funding markets remain dislocated. We are maintaining excess liquidity and limiting balance sheet expansion. Deposit cost pressures persist.",
    "Reserve build was meaningfully elevated this quarter. We are adopting a defensive credit stance across consumer and commercial books.",
    "Capital markets activity has slowed sharply. Investment banking pipelines have softened. We are managing expenses tightly.",
    "Counterparty risk pricing has moved materially. We are reducing exposures in cyclically sensitive sectors. Provisioning has been pulled forward.",
    "Net interest margin compression has accelerated as deposit costs continue to reprice. We are managing balance sheet duration defensively.",
    "Loan growth has decelerated as we tighten standards. Trading desks are de-risking. Our priority is capital ratio defense.",
    "Wholesale funding spreads remain elevated. We have repositioned our investment portfolio defensively. We are not currently providing forward guidance.",
    "Credit conditions are tightening across our footprint. Charge-offs ticked up modestly. We are increasing reserve coverage proactively.",
    "Treasury yields and credit spreads suggest persistent macro stress. We are managing through this with a strong capital position and selective lending.",
    "Volatility-driven trading desks performed well, but the overall macro environment is constraining our core lending and capital markets businesses.",
    "We are running with elevated liquidity buffers given the macro stress signals. Credit selection has tightened across all consumer and commercial books.",
    "Deposit beta acceleration combined with curve inversion is compressing core margins. We are managing expenses and capital actions defensively.",
    "Multiple macro stress indicators — credit spreads, funding markets, asset price volatility — are flashing. We are positioned defensively across the franchise.",
    # late-cycle explicit
    "All the classic late-cycle credit signals are now present: rising charge-offs, spread widening, tighter origination. We are managing this as a late-cycle credit reset.",
    "Cycle maturity is evident in our consumer credit book. Delinquencies are normalizing toward late-cycle peaks. We are reserving accordingly.",
    "We are in the late stages of this credit cycle. Reserve build, balance sheet conservatism, and capital preservation are our priorities.",
    "Late-cycle deterioration is visible across commercial and consumer portfolios. We expect another two to four quarters of normalization before a constructive setup emerges.",
    "Macro stress is compounding late-cycle credit dynamics. We are running the bank defensively until cycle conditions improve.",
    "Late-cycle credit cost normalization is now the dominant earnings headwind. We are absorbing this with disciplined capital actions.",
    "We are operating under a late-cycle framework. Spreads, delinquencies, and capital markets activity all point to cycle maturity. Our posture is defensive accordingly.",
],
}


# ============================================================
# DEFINIZIONI DEI CLUSTER (Level 1 base)
# ============================================================

CLUSTERS_BASE = {
    "A": {
        "name": "ai_infra_euphoria",
        "macro_means": {"vix": 13.5, "yield_10y": 4.2, "yield_curve_slope": 0.3,
                        "credit_spread": 3.0, "dxy": 103.0},
        "macro_stds":  {"vix": 1.5,  "yield_10y": 0.2, "yield_curve_slope": 0.15,
                        "credit_spread": 0.2, "dxy": 1.0},
        "micro_means": {"return_60d": 0.22, "realized_vol_60d": 0.45,
                        "drawdown_from_high": -0.04, "sector_return_60d": 0.18,
                        "relative_strength": 0.85},
        "micro_stds":  {"return_60d": 0.08, "realized_vol_60d": 0.08,
                        "drawdown_from_high": 0.03, "sector_return_60d": 0.06,
                        "relative_strength": 0.10},
        "semantic_means": {"confidence_score": 0.82, "hedging_count": 2,
                           "guidance_direction": 1, "uncertainty_markers": 3},
        "semantic_stds":  {"confidence_score": 0.08, "hedging_count": 1.5,
                           "guidance_direction": 0.3, "uncertainty_markers": 2},
        "reaction_means": {"return": 0.10, "realized_vol": 0.40,
                           "max_drawdown": -0.06, "persistence": 0.55},
        "reaction_stds":  {"return": 0.05, "realized_vol": 0.08,
                           "max_drawdown": 0.04, "persistence": 0.15},
    },
    "B": {
        "name": "late_cycle_compression",
        "macro_means": {"vix": 22.0, "yield_10y": 4.8, "yield_curve_slope": -0.4,
                        "credit_spread": 4.5, "dxy": 106.5},
        "macro_stds":  {"vix": 2.5, "yield_10y": 0.25, "yield_curve_slope": 0.2,
                        "credit_spread": 0.4, "dxy": 1.2},
        "micro_means": {"return_60d": -0.12, "realized_vol_60d": 0.38,
                        "drawdown_from_high": -0.18, "sector_return_60d": -0.08,
                        "relative_strength": 0.30},
        "micro_stds":  {"return_60d": 0.06, "realized_vol_60d": 0.07,
                        "drawdown_from_high": 0.06, "sector_return_60d": 0.05,
                        "relative_strength": 0.12},
        "semantic_means": {"confidence_score": 0.40, "hedging_count": 8,
                           "guidance_direction": -1, "uncertainty_markers": 9},
        "semantic_stds":  {"confidence_score": 0.10, "hedging_count": 2,
                           "guidance_direction": 0.3, "uncertainty_markers": 2.5},
        "reaction_means": {"return": -0.14, "realized_vol": 0.48,
                           "max_drawdown": -0.20, "persistence": 0.65},
        "reaction_stds":  {"return": 0.06, "realized_vol": 0.10,
                           "max_drawdown": 0.06, "persistence": 0.15},
    },
    "C": {
        "name": "recovery_surprise",
        "macro_means": {"vix": 17.0, "yield_10y": 3.9, "yield_curve_slope": 0.15,
                        "credit_spread": 3.8, "dxy": 104.5},
        "macro_stds":  {"vix": 2.0, "yield_10y": 0.2, "yield_curve_slope": 0.15,
                        "credit_spread": 0.3, "dxy": 1.0},
        "micro_means": {"return_60d": 0.05, "realized_vol_60d": 0.35,
                        "drawdown_from_high": -0.22, "sector_return_60d": 0.02,
                        "relative_strength": 0.45},
        "micro_stds":  {"return_60d": 0.06, "realized_vol_60d": 0.06,
                        "drawdown_from_high": 0.05, "sector_return_60d": 0.05,
                        "relative_strength": 0.12},
        "semantic_means": {"confidence_score": 0.65, "hedging_count": 4,
                           "guidance_direction": 0.5, "uncertainty_markers": 5},
        "semantic_stds":  {"confidence_score": 0.10, "hedging_count": 1.5,
                           "guidance_direction": 0.4, "uncertainty_markers": 2},
        "reaction_means": {"return": 0.13, "realized_vol": 0.32,
                           "max_drawdown": -0.05, "persistence": 0.78},
        "reaction_stds":  {"return": 0.05, "realized_vol": 0.06,
                           "max_drawdown": 0.03, "persistence": 0.10},
    },
    "D": {
        "name": "liquidity_stress",
        "macro_means": {"vix": 32.0, "yield_10y": 4.5, "yield_curve_slope": -0.6,
                        "credit_spread": 6.5, "dxy": 108.0},
        "macro_stds":  {"vix": 4.0, "yield_10y": 0.3, "yield_curve_slope": 0.25,
                        "credit_spread": 0.6, "dxy": 1.5},
        "micro_means": {"return_60d": -0.18, "realized_vol_60d": 0.55,
                        "drawdown_from_high": -0.25, "sector_return_60d": -0.15,
                        "relative_strength": 0.25},
        "micro_stds":  {"return_60d": 0.08, "realized_vol_60d": 0.10,
                        "drawdown_from_high": 0.08, "sector_return_60d": 0.06,
                        "relative_strength": 0.10},
        "semantic_means": {"confidence_score": 0.35, "hedging_count": 10,
                           "guidance_direction": -0.5, "uncertainty_markers": 12},
        "semantic_stds":  {"confidence_score": 0.10, "hedging_count": 2.5,
                           "guidance_direction": 0.5, "uncertainty_markers": 3},
        "reaction_means": {"return": -0.18, "realized_vol": 0.60,
                           "max_drawdown": -0.25, "persistence": 0.55},
        "reaction_stds":  {"return": 0.08, "realized_vol": 0.12,
                           "max_drawdown": 0.08, "persistence": 0.15},
    },
}


# ============================================================
# TRANSFORMS
# ============================================================

NUMERIC_BLOCKS = ("macro_means", "micro_means", "semantic_means")
STD_BLOCKS_INPUT = ("macro_stds", "micro_stds", "semantic_stds")
STD_BLOCKS_ALL = STD_BLOCKS_INPUT + ("reaction_stds",)


def scale_stds(clusters: dict, factor: float, include_reaction: bool = True) -> dict:
    out = copy.deepcopy(clusters)
    blocks = STD_BLOCKS_ALL if include_reaction else STD_BLOCKS_INPUT
    for cdef in out.values():
        for block in blocks:
            for k in cdef[block]:
                cdef[block][k] = cdef[block][k] * factor
    return out


def amplify_reaction_means(clusters: dict, factor: float) -> dict:
    """Move reaction means away from grand mean by `factor` (>1 amplifies separation)."""
    out = copy.deepcopy(clusters)
    keys = list(next(iter(out.values()))["reaction_means"].keys())
    means = np.array([[c["reaction_means"][k] for k in keys] for c in out.values()])
    grand = means.mean(axis=0)
    for cdef in out.values():
        for i, k in enumerate(keys):
            orig = cdef["reaction_means"][k]
            cdef["reaction_means"][k] = float(grand[i] + (orig - grand[i]) * factor)
    return out


def shrink_means_toward_grand_mean(clusters: dict, keep_fraction: float) -> dict:
    """For each macro/micro/semantic dimension, move each cluster mean toward
    the grand mean of that dimension across clusters. keep_fraction=0.65 keeps
    65% of the original offset → reduces inter-cluster mean distance by 35%."""
    out = copy.deepcopy(clusters)
    for block in NUMERIC_BLOCKS:
        keys = list(next(iter(out.values()))[block].keys())
        means = np.array([[c[block][k] for k in keys] for c in out.values()])
        grand = means.mean(axis=0)
        for cdef in out.values():
            for i, k in enumerate(keys):
                orig = cdef[block][k]
                cdef[block][k] = float(grand[i] + (orig - grand[i]) * keep_fraction)
    return out


def make_shared_macro_micro(clusters: dict) -> dict:
    out = copy.deepcopy(clusters)
    keys_macro = list(next(iter(out.values()))["macro_means"].keys())
    keys_micro = list(next(iter(out.values()))["micro_means"].keys())

    def pool(block_means_key, keys):
        all_means = np.array([[c[block_means_key][k] for k in keys] for c in out.values()])
        return all_means.mean(axis=0), all_means.std(axis=0)
    macro_mu, macro_sigma = pool("macro_means", keys_macro)
    micro_mu, micro_sigma = pool("micro_means", keys_micro)

    for cdef in out.values():
        for i, k in enumerate(keys_macro):
            cdef["macro_means"][k] = float(macro_mu[i])
            cdef["macro_stds"][k] = float(max(macro_sigma[i], 1e-3))
        for i, k in enumerate(keys_micro):
            cdef["micro_means"][k] = float(micro_mu[i])
            cdef["micro_stds"][k] = float(max(micro_sigma[i], 1e-3))
    return out


def make_reaction_only(clusters: dict, std_factor: float = 1.8) -> dict:
    out = make_shared_macro_micro(clusters)
    keys_sem = list(next(iter(out.values()))["semantic_means"].keys())
    all_means = np.array([[c["semantic_means"][k] for k in keys_sem] for c in out.values()])
    sem_mu = all_means.mean(axis=0); sem_sigma = all_means.std(axis=0)
    for cdef in out.values():
        for i, k in enumerate(keys_sem):
            cdef["semantic_means"][k] = float(sem_mu[i])
            cdef["semantic_stds"][k] = float(max(sem_sigma[i], 1e-3))
    out = scale_stds(out, std_factor)
    return out


# ============================================================
# SAMPLERS
# ============================================================

def sample_dict(means: dict, stds: dict) -> dict:
    return {k: float(np.random.normal(means[k], stds[k])) for k in means}


def clamp_event(macro, micro, semantic, reaction):
    g = semantic["guidance_direction"]
    if g < -0.33:
        semantic["guidance_direction"] = -1
    elif g > 0.33:
        semantic["guidance_direction"] = 1
    else:
        semantic["guidance_direction"] = 0
    semantic["hedging_count"] = max(0, int(round(semantic["hedging_count"])))
    semantic["uncertainty_markers"] = max(0, int(round(semantic["uncertainty_markers"])))
    semantic["confidence_score"] = float(np.clip(semantic["confidence_score"], 0, 1))
    macro["vix"] = max(8.0, macro["vix"])
    macro["credit_spread"] = max(1.0, macro["credit_spread"])
    micro["relative_strength"] = float(np.clip(micro["relative_strength"], 0, 1))
    micro["drawdown_from_high"] = min(0, micro["drawdown_from_high"])
    reaction["max_drawdown"] = min(0, reaction["max_drawdown"])
    reaction["persistence"] = float(np.clip(reaction["persistence"], 0, 1))


INTROS = [
    "", "On our call today, ", "As we discussed last quarter, ",
    "To frame our results, ", "Looking at the quarter just ended, ",
    "Let me start with the headline: ",
]
CLOSERS = [
    "", " We will provide more color in Q&A.",
    " Thank you for joining us today.", " We look forward to your questions.",
    " More details follow in the prepared remarks.",
    " We remain confident in our positioning through this period.",
]

def _vary_text(base: str) -> str:
    intro = random.choice(INTROS)
    closer = random.choice(CLOSERS)
    return (intro + base + closer).strip()


def sample_from_cluster(cluster_id, cluster_def, event_id, date_str, cross_pollinate: bool,
                        text_mix_other: float = 0.0):
    semantic = sample_dict(cluster_def["semantic_means"], cluster_def["semantic_stds"])
    macro = sample_dict(cluster_def["macro_means"], cluster_def["macro_stds"])
    micro = sample_dict(cluster_def["micro_means"], cluster_def["micro_stds"])
    reaction = sample_dict(cluster_def["reaction_means"], cluster_def["reaction_stds"])
    clamp_event(macro, micro, semantic, reaction)
    # Optional: pick text from a different cluster with probability text_mix_other
    src = cluster_id
    if text_mix_other > 0 and random.random() < text_mix_other:
        other = [c for c in TEXTS if c != cluster_id]
        src = random.choice(other)
    text = _vary_text(random.choice(TEXTS[src]))
    if cross_pollinate:
        ticker, sector = pick_ticker(cluster_id)
    else:
        # legacy: pick from original cluster tickers (tech for A, etc.)
        primary_sector = max(CLUSTER_SECTOR_MIX[cluster_id], key=CLUSTER_SECTOR_MIX[cluster_id].get)
        ticker = random.choice(SECTOR_TICKERS[primary_sector])
        sector = primary_sector
    return {
        "id": event_id, "ticker": ticker, "date": date_str,
        "event_type": "earnings", "sector": sector, "text": text,
        "macro_features": macro, "micro_features": micro,
        "semantic_features": semantic, "reaction_30d": reaction,
        "ground_truth_cluster": None,
    }


def _half_mix_text(text_x: str, text_y: str) -> str:
    """Combine first half of text_x with second half of text_y (sentence-based)."""
    def halves(t):
        sents = [s.strip() for s in t.split(".") if s.strip()]
        mid = max(1, len(sents) // 2)
        return ". ".join(sents[:mid]) + ".", ". ".join(sents[mid:]) + "."
    fx, _ = halves(text_x)
    _, sy = halves(text_y)
    return _vary_text((fx + " " + sy).strip())


def sample_hybrid(x_id, y_id, clusters, event_id, date_str, cross_pollinate: bool):
    cX, cY = clusters[x_id], clusters[y_id]
    macro = sample_dict(cX["macro_means"], cX["macro_stds"])
    micro = sample_dict(cX["micro_means"], cX["micro_stds"])
    semantic = sample_dict(cY["semantic_means"], cY["semantic_stds"])
    # Reaction = weighted 50/50 of X and Y reactions + moderate noise
    rX = sample_dict(cX["reaction_means"], cX["reaction_stds"])
    rY = sample_dict(cY["reaction_means"], cY["reaction_stds"])
    reaction = {}
    for k in rX:
        base = 0.5 * rX[k] + 0.5 * rY[k]
        # noise std = avg of X/Y stds for that dim
        sd = 0.5 * (cX["reaction_stds"][k] + cY["reaction_stds"][k])
        reaction[k] = float(base + np.random.normal(0, sd * 0.5))
    clamp_event(macro, micro, semantic, reaction)
    # Text = half template X + half template Y
    tX = random.choice(TEXTS[x_id])
    tY = random.choice(TEXTS[y_id])
    text = _half_mix_text(tX, tY)
    if cross_pollinate:
        ticker, sector = pick_ticker(x_id)
    else:
        primary_sector = max(CLUSTER_SECTOR_MIX[x_id], key=CLUSTER_SECTOR_MIX[x_id].get)
        ticker = random.choice(SECTOR_TICKERS[primary_sector])
        sector = primary_sector
    return {
        "id": event_id, "ticker": ticker, "date": date_str,
        "event_type": "earnings", "sector": sector, "text": text,
        "macro_features": macro, "micro_features": micro,
        "semantic_features": semantic, "reaction_30d": reaction,
        "ground_truth_cluster": "HYBRID",
        "hybrid_macro_from": x_id, "hybrid_semantic_from": y_id,
    }


def generate_noise_event(event_id, date_str):
    return {
        "id": event_id,
        "ticker": random.choice(["XYZ", "ABC", "DEF", "GHI", "JKL"]),
        "date": date_str, "event_type": "earnings", "sector": "mixed",
        "text": "Quarterly results were broadly in line with expectations. We continue to execute on our strategic priorities. Business trends remained relatively stable across segments. We maintain our prior outlook with minor adjustments.",
        "macro_features": {
            "vix": float(np.random.uniform(12, 28)),
            "yield_10y": float(np.random.uniform(3.5, 5.0)),
            "yield_curve_slope": float(np.random.uniform(-0.5, 0.5)),
            "credit_spread": float(np.random.uniform(2.5, 5.0)),
            "dxy": float(np.random.uniform(100, 108)),
        },
        "micro_features": {
            "return_60d": float(np.random.uniform(-0.10, 0.10)),
            "realized_vol_60d": float(np.random.uniform(0.25, 0.45)),
            "drawdown_from_high": float(np.random.uniform(-0.15, 0)),
            "sector_return_60d": float(np.random.uniform(-0.08, 0.10)),
            "relative_strength": float(np.random.uniform(0.3, 0.7)),
        },
        "semantic_features": {
            "confidence_score": float(np.random.uniform(0.45, 0.70)),
            "hedging_count": int(np.random.randint(3, 7)),
            "guidance_direction": int(np.random.choice([-1, 0, 1])),
            "uncertainty_markers": int(np.random.randint(4, 8)),
        },
        "reaction_30d": {
            "return": float(np.random.uniform(-0.06, 0.06)),
            "realized_vol": float(np.random.uniform(0.25, 0.45)),
            "max_drawdown": float(np.random.uniform(-0.10, 0)),
            "persistence": float(np.random.uniform(0.3, 0.7)),
        },
        "ground_truth_cluster": "NOISE",
    }


def random_date(start_year=2022, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta_days = (end - start).days
    return (start + timedelta(days=random.randint(0, delta_days))).strftime("%Y-%m-%d")


# ============================================================
# LEVEL CONFIG
# ============================================================

LEVEL_CONFIG = {
    1: dict(n_cl_tr=30, n_cl_te=10, n_noise_tr=12, n_noise_te=4,
            n_hyb_tr=0, n_hyb_te=0, std_factor=1.0, shrink_keep=1.0,
            cross_pollinate=False, transform=None, text_mix_other=0.0,
            description="base, ~9% noise (legacy tickers, 4 testi/cluster)"),
    2: dict(n_cl_tr=30, n_cl_te=10, n_noise_tr=30, n_noise_te=10,
            n_hyb_tr=0, n_hyb_te=0, std_factor=1.5, shrink_keep=0.65,
            cross_pollinate=True, transform=None, text_mix_other=0.0,
            description="stds x1.5, means shrink 35%, sector cross-pollination, rich text pool"),
    3: dict(n_cl_tr=30, n_cl_te=10, n_noise_tr=50, n_noise_te=17,
            n_hyb_tr=30, n_hyb_te=10, std_factor=2.0, shrink_keep=0.4875,
            cross_pollinate=True, transform=None, text_mix_other=0.0,
            description="stds x2.0, shrink 51%, +15% HYBRID with mixed reactions+text, ~25% noise"),
    4: dict(n_cl_tr=30, n_cl_te=10, n_noise_tr=20, n_noise_te=7,
            n_hyb_tr=0, n_hyb_te=0, std_factor=1.0, shrink_keep=1.0,
            cross_pollinate=True, transform="shared_macro_micro", text_mix_other=0.0,
            description="cluster differ ONLY on semantic+text+reaction; macro/micro pooled"),
    5: dict(n_cl_tr=30, n_cl_te=10, n_noise_tr=50, n_noise_te=17,
            n_hyb_tr=0, n_hyb_te=0, std_factor=1.8, shrink_keep=0.5,
            cross_pollinate=True, transform=None, text_mix_other=0.40,
            scale_reaction_stds=False, reaction_amplify=2.2,
            description="reaction-driven: features overlap (stds x1.8, shrink 50%), texts 60/40 mixed, reactions amplified x1.7"),
}


def build_clusters(level: int) -> dict:
    cfg = LEVEL_CONFIG[level]
    clusters = copy.deepcopy(CLUSTERS_BASE)
    if cfg["transform"] == "shared_macro_micro":
        clusters = make_shared_macro_micro(clusters)
    if cfg["shrink_keep"] != 1.0:
        clusters = shrink_means_toward_grand_mean(clusters, cfg["shrink_keep"])
    if cfg["std_factor"] != 1.0:
        clusters = scale_stds(clusters, cfg["std_factor"],
                              include_reaction=cfg.get("scale_reaction_stds", True))
    amp = cfg.get("reaction_amplify", 1.0)
    if amp != 1.0:
        clusters = amplify_reaction_means(clusters, amp)
    return clusters


def generate_dataset(level: int) -> list:
    random.seed(SEED)
    np.random.seed(SEED)
    cfg = LEVEL_CONFIG[level]
    clusters = build_clusters(level)
    cluster_ids = list(clusters.keys())
    cross = cfg["cross_pollinate"]

    events = []
    counter = 0

    for cid, cdef in clusters.items():
        for split, n in [("train", cfg["n_cl_tr"]), ("test", cfg["n_cl_te"])]:
            for _ in range(n):
                counter += 1
                ev = sample_from_cluster(cid, cdef, f"evt_{counter:04d}",
                                         random_date(), cross,
                                         text_mix_other=cfg.get("text_mix_other", 0.0))
                ev["ground_truth_cluster"] = cid
                ev["split"] = split
                events.append(ev)

    if cfg["n_hyb_tr"] or cfg["n_hyb_te"]:
        for split, n in [("train", cfg["n_hyb_tr"]), ("test", cfg["n_hyb_te"])]:
            for _ in range(n):
                counter += 1
                x_id = random.choice(cluster_ids)
                y_id = random.choice([c for c in cluster_ids if c != x_id])
                ev = sample_hybrid(x_id, y_id, clusters,
                                   f"evt_{counter:04d}", random_date(), cross)
                ev["split"] = split
                events.append(ev)

    for split, n in [("train", cfg["n_noise_tr"]), ("test", cfg["n_noise_te"])]:
        for _ in range(n):
            counter += 1
            ev = generate_noise_event(f"evt_{counter:04d}", random_date())
            ev["split"] = split
            events.append(ev)

    random.shuffle(events)
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--difficulty", "-d", type=int, default=1, choices=[1, 2, 3, 4, 5])
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    level = args.difficulty
    cfg = LEVEL_CONFIG[level]
    out_path = Path(args.out or f"data/mock_events_L{level}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    events = generate_dataset(level)

    n_train = sum(1 for e in events if e["split"] == "train")
    n_test = sum(1 for e in events if e["split"] == "test")
    cluster_counts = {}
    sector_counts: dict = {}
    for e in events:
        cluster_counts[e["ground_truth_cluster"]] = cluster_counts.get(e["ground_truth_cluster"], 0) + 1
        c = e["ground_truth_cluster"]
        if c not in sector_counts:
            sector_counts[c] = {}
        sector_counts[c][e["sector"]] = sector_counts[c].get(e["sector"], 0) + 1

    unique_texts = len(set(e["text"] for e in events))
    print(f"Level {level}: {cfg['description']}")
    print(f"Eventi totali: {len(events)} (train={n_train}, test={n_test})")
    print(f"Testi unici: {unique_texts}")
    for c, n in sorted(cluster_counts.items()):
        print(f"  {c}: {n}")
        if c in sector_counts and sector_counts[c]:
            sec_str = ", ".join(f"{s}={k}" for s, k in sorted(sector_counts[c].items(), key=lambda x: -x[1]))
            print(f"    sectors: {sec_str}")

    with open(out_path, "w") as f:
        json.dump(events, f, indent=2)
    print(f"Salvato in: {out_path} ({out_path.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
