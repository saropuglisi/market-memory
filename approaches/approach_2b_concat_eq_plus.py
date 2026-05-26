"""concat_eq+ — weighted structured retrieval with narrative tags.

Evolution of concat_eq (Discovery Phase primary engine). The composite
similarity score is a *weighted sum of 5 component similarities*:

    score(q, c) =   w_macro    × cosine(macro_z)
                  + w_tags     × jaccard(narrative_tags_q, narrative_tags_c)
                  + w_sector   × [ cosine(sector_behavior_z)
                                    + sector_match_bonus(GICS) ]
                  + w_pre      × cosine(pre_event_setup_z)
                  + w_vol      × cosine(volatility_structure_z)

Defaults: w_macro=0.35, w_tags=0.25, w_sector=0.20, w_pre=0.10, w_vol=0.10.

The score is *not* a single cosine on a concatenated vector — Jaccard on
binary tags and the categorical sector bonus are not cosine-compatible.
We therefore override `retrieve()`. For metric helpers that call
`encode_batch()` (self_consistency, reaction_corr), `encode()` still
returns a weighted concat vector so those metrics remain *approximations*
of the true score. The honest scoring is in `retrieve()` and in
`pairwise_score()`.

The 12 narrative tags are loaded from
    real_data/processed/sample_500_narrative_tags.json
keyed by event id. Events with no tags fall back to a zero vector.
"""
from __future__ import annotations
import json
import os
from typing import List, Dict, Any, Optional

import numpy as np
from numpy.linalg import norm

from .base import EpisodeEncoder, Standardizer

# ────────────────────────────────────────────────────────────────────────
# Feature key partitioning. Reuses raw event fields (no re-engineering).
# ────────────────────────────────────────────────────────────────────────
MACRO_KEYS         = ["vix", "yield_10y", "yield_curve_slope",
                      "credit_spread", "dxy"]
SECTOR_BEHAVIOR    = ["sector_return_60d", "relative_strength"]
PRE_EVENT_KEYS     = ["return_60d", "drawdown_from_high"]
VOLATILITY_KEYS    = ["realized_vol_60d"]

DEFAULT_WEIGHTS = {
    "macro":  0.35,
    "tags":   0.25,
    "sector": 0.20,
    "pre":    0.10,
    "vol":    0.10,
}
# Within the sector block, how much weight comes from the binary GICS match
# (rest goes to sector-behavior cosine).
SECTOR_MATCH_FRACTION = 0.6

TAG_JSON_DEFAULT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "real_data", "processed", "sample_500_narrative_tags.json"
)


def _get_macro(e: Dict[str, Any]) -> np.ndarray:
    m = e["macro_features"]
    return np.array([float(m[k]) for k in MACRO_KEYS], dtype=np.float32)


def _get_micro_subset(e: Dict[str, Any], keys) -> np.ndarray:
    m = e["micro_features"]
    return np.array([float(m[k]) for k in keys], dtype=np.float32)


def _jaccard(a: np.ndarray, b: np.ndarray) -> float:
    """Binary Jaccard. If both vectors are all-zero, return 0 (no info)."""
    inter = float(np.sum(np.minimum(a, b)))
    union = float(np.sum(np.maximum(a, b)))
    return inter / union if union > 0 else 0.0


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    n = norm(a) * norm(b)
    return float(np.dot(a, b) / n) if n > 0 else 0.0


class ConcatEqPlus(EpisodeEncoder):
    name = "concat_eq_plus"

    def __init__(self,
                 weights: Optional[Dict[str, float]] = None,
                 tag_json_path: str = TAG_JSON_DEFAULT,
                 sector_match_fraction: float = SECTOR_MATCH_FRACTION):
        self.weights = dict(DEFAULT_WEIGHTS, **(weights or {}))
        total = sum(self.weights.values())
        if abs(total - 1.0) > 1e-6:
            # Normalize to make weights sum to 1.0.
            for k in self.weights:
                self.weights[k] /= total
        self.sector_match_fraction = sector_match_fraction

        # Load tags
        self.tags_by_id: Dict[str, Dict[str, int]] = {}
        if os.path.exists(tag_json_path):
            with open(tag_json_path) as f:
                raw = json.load(f)
            for eid, d in raw.items():
                # Skip _status field
                self.tags_by_id[eid] = {k: int(v) for k, v in d.items() if k != "_status"}
            self.tag_keys = (sorted(next(iter(raw.values())).keys())
                             if raw else [])
            self.tag_keys = [k for k in self.tag_keys if k != "_status"]
        else:
            self.tag_keys = []
            print(f"[concat_eq+] WARN: no tags file at {tag_json_path}")

        # Standardizers fit at .fit()
        self.std_macro  = Standardizer()
        self.std_sector = Standardizer()
        self.std_pre    = Standardizer()
        self.std_vol    = Standardizer()

        # Sector vocabulary (GICS)
        self.sector_vocab: List[str] = []

        # Per-event pre-computed component vectors (filled by _index_events)
        self._cache: Dict[str, Dict[str, np.ndarray]] = {}

    # ── fit / encode ──────────────────────────────────────────────────────
    def fit(self, events: List[Dict[str, Any]]) -> None:
        macro  = np.stack([_get_macro(e) for e in events])
        sector = np.stack([_get_micro_subset(e, SECTOR_BEHAVIOR) for e in events])
        pre    = np.stack([_get_micro_subset(e, PRE_EVENT_KEYS) for e in events])
        vol    = np.stack([_get_micro_subset(e, VOLATILITY_KEYS) for e in events])
        self.std_macro.fit(macro)
        self.std_sector.fit(sector)
        self.std_pre.fit(pre)
        self.std_vol.fit(vol)
        self.sector_vocab = sorted({e["sector"] for e in events})
        for e in events:
            self._components(e)  # populate cache

    def _components(self, e: Dict[str, Any]) -> Dict[str, np.ndarray]:
        eid = e["id"]
        if eid in self._cache:
            return self._cache[eid]
        macro_z  = self.std_macro.transform(_get_macro(e)[None, :])[0]
        sector_z = self.std_sector.transform(_get_micro_subset(e, SECTOR_BEHAVIOR)[None, :])[0]
        pre_z    = self.std_pre.transform(_get_micro_subset(e, PRE_EVENT_KEYS)[None, :])[0]
        vol_z    = self.std_vol.transform(_get_micro_subset(e, VOLATILITY_KEYS)[None, :])[0]
        tag_d    = self.tags_by_id.get(eid, {})
        tag_vec  = np.array([tag_d.get(k, 0) for k in self.tag_keys], dtype=np.float32)
        comp = {
            "macro":  macro_z, "sector": sector_z, "pre": pre_z, "vol": vol_z,
            "tags":   tag_vec, "sector_gics": e["sector"],
        }
        self._cache[eid] = comp
        return comp

    def encode(self, event: Dict[str, Any]) -> np.ndarray:
        """Weighted concat vector (cosine-approximation of true score).

        Used by base helpers like self_consistency / reaction_corr that
        rely on cosine of encoder outputs. NOT used by retrieve(), which
        computes the exact weighted multi-component score.
        """
        c = self._components(event)
        # one-hot sector
        oh = np.zeros(len(self.sector_vocab), dtype=np.float32)
        if c["sector_gics"] in self.sector_vocab:
            oh[self.sector_vocab.index(c["sector_gics"])] = 1.0
        # weight each block by √w so dot product cross-term ≈ Σ w_k cos_k
        # for unit-norm blocks (approximate).
        def s(block, w):
            v = block.astype(np.float32)
            n = norm(v) + 1e-9
            return (v / n) * np.sqrt(max(w, 0.0))
        return np.concatenate([
            s(c["macro"],  self.weights["macro"]),
            s(c["tags"],   self.weights["tags"]),
            s(c["sector"], self.weights["sector"] * (1 - self.sector_match_fraction)),
            s(oh,          self.weights["sector"] * self.sector_match_fraction),
            s(c["pre"],    self.weights["pre"]),
            s(c["vol"],    self.weights["vol"]),
        ]).astype(np.float32)

    # ── true scoring ──────────────────────────────────────────────────────
    def pairwise_score(self, q_ev: Dict[str, Any], c_ev: Dict[str, Any]) -> float:
        qc = self._components(q_ev)
        cc = self._components(c_ev)
        s_macro  = _cosine(qc["macro"],  cc["macro"])
        s_tags   = _jaccard(qc["tags"],  cc["tags"])
        s_sec_b  = _cosine(qc["sector"], cc["sector"])
        s_match  = 1.0 if qc["sector_gics"] == cc["sector_gics"] else 0.0
        s_sector = (self.sector_match_fraction * s_match +
                    (1 - self.sector_match_fraction) * s_sec_b)
        s_pre    = _cosine(qc["pre"], cc["pre"])
        s_vol    = _cosine(qc["vol"], cc["vol"])
        w = self.weights
        return (w["macro"]  * s_macro +
                w["tags"]   * s_tags  +
                w["sector"] * s_sector +
                w["pre"]    * s_pre +
                w["vol"]    * s_vol)

    def score_breakdown(self, q_ev, c_ev) -> Dict[str, float]:
        qc = self._components(q_ev); cc = self._components(c_ev)
        return {
            "macro":  _cosine(qc["macro"],  cc["macro"]),
            "tags":   _jaccard(qc["tags"],  cc["tags"]),
            "sector_behavior": _cosine(qc["sector"], cc["sector"]),
            "sector_match":    1.0 if qc["sector_gics"] == cc["sector_gics"] else 0.0,
            "pre_event": _cosine(qc["pre"], cc["pre"]),
            "vol":       _cosine(qc["vol"], cc["vol"]),
            "total":     self.pairwise_score(q_ev, c_ev),
        }

    def retrieve(self, query_event: Dict[str, Any],
                 candidate_events: List[Dict[str, Any]],
                 top_k: int = 5) -> List[int]:
        scores = np.array([self.pairwise_score(query_event, c)
                           for c in candidate_events])
        return np.argsort(-scores)[:top_k].tolist()

    # encode_batch falls back to base impl (per-event encode)
