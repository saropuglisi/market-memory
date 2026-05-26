"""Approach 4: graph-based encoder (minimal placeholder).

Builds sector + ticker co-occurrence graph; uses spectral embedding of the
adjacency as node features. Concatenated with standardized numeric blocks.
Marked experimental.
"""
from __future__ import annotations
from typing import List, Dict, Any
import numpy as np

from .base import (EpisodeEncoder, Standardizer, vec_from, SEED)


class GraphEncoder(EpisodeEncoder):
    name = "graph_experimental"
    experimental = True

    def __init__(self, emb_dim: int = 16):
        self.emb_dim = emb_dim
        self.std_macro = Standardizer()
        self.std_micro = Standardizer()
        self.std_sem = Standardizer()
        self.ticker_to_vec: Dict[str, np.ndarray] = {}
        self.sector_to_vec: Dict[str, np.ndarray] = {}

    def fit(self, events: List[Dict[str, Any]]) -> None:
        rng = np.random.default_rng(SEED)
        self.std_macro.fit(np.stack([vec_from(e, "macro") for e in events]))
        self.std_micro.fit(np.stack([vec_from(e, "micro") for e in events]))
        self.std_sem.fit(np.stack([vec_from(e, "semantic") for e in events]))

        tickers = sorted({e["ticker"] for e in events})
        sectors = sorted({e["sector"] for e in events})

        # Random projection per node as a stand-in for node2vec; ticker shares sector dim
        # so same-sector tickers get correlated embeddings.
        sector_basis = {s: rng.standard_normal(self.emb_dim).astype(np.float32) for s in sectors}
        for t in tickers:
            sectors_for_t = [e["sector"] for e in events if e["ticker"] == t]
            s = sectors_for_t[0] if sectors_for_t else sectors[0]
            jitter = rng.standard_normal(self.emb_dim).astype(np.float32) * 0.3
            self.ticker_to_vec[t] = sector_basis[s] + jitter
        self.sector_to_vec = sector_basis

    def encode(self, event: Dict[str, Any]) -> np.ndarray:
        macro = self.std_macro.transform(vec_from(event, "macro")[None, :])[0]
        micro = self.std_micro.transform(vec_from(event, "micro")[None, :])[0]
        sem = self.std_sem.transform(vec_from(event, "semantic")[None, :])[0]
        t_vec = self.ticker_to_vec.get(event["ticker"],
                                       self.sector_to_vec.get(event["sector"],
                                                              np.zeros(self.emb_dim, dtype=np.float32)))
        s_vec = self.sector_to_vec.get(event["sector"],
                                       np.zeros(self.emb_dim, dtype=np.float32))
        return np.concatenate([macro, micro, sem, t_vec, s_vec]).astype(np.float32)
