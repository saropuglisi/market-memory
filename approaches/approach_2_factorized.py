"""Approach 2: factorized multi-stage retrieval."""
from __future__ import annotations
from typing import List, Dict, Any, Optional
import numpy as np
from numpy.linalg import norm

from .base import (EpisodeEncoder, Standardizer, embed_texts, vec_from)


class FactorizedMultiStage(EpisodeEncoder):
    name = "factorized"

    def __init__(self, stage1_keep: float = 0.30, stage2_keep: float = 0.20,
                 w_text: float = 0.7, w_sem: float = 0.3):
        self.stage1_keep = stage1_keep
        self.stage2_keep = stage2_keep
        self.w_text = w_text
        self.w_sem = w_sem
        self.std_macro = Standardizer()
        self.std_micro = Standardizer()
        self.std_sem = Standardizer()

    def fit(self, events: List[Dict[str, Any]]) -> None:
        self.std_macro.fit(np.stack([vec_from(e, "macro") for e in events]))
        self.std_micro.fit(np.stack([vec_from(e, "micro") for e in events]))
        self.std_sem.fit(np.stack([vec_from(e, "semantic") for e in events]))
        # warm text cache
        embed_texts([e["text"] for e in events])

    def _blocks(self, event: Dict[str, Any]):
        macro = self.std_macro.transform(vec_from(event, "macro")[None, :])[0]
        micro = self.std_micro.transform(vec_from(event, "micro")[None, :])[0]
        sem = self.std_sem.transform(vec_from(event, "semantic")[None, :])[0]
        text = embed_texts([event["text"]])[0]
        return macro, micro, sem, text

    def encode(self, event: Dict[str, Any]) -> np.ndarray:
        """Concatenate equally-weighted blocks for default similarity use cases.
        Retrieval below uses staged filtering instead."""
        macro, micro, sem, text = self._blocks(event)
        macro_n = macro / (norm(macro) + 1e-9)
        micro_n = micro / (norm(micro) + 1e-9)
        sem_n = sem / (norm(sem) + 1e-9)
        text_n = text / (norm(text) + 1e-9)
        return np.concatenate([text_n, macro_n, micro_n, sem_n]).astype(np.float32)

    def retrieve(self, query_event: Dict[str, Any],
                 candidate_events: List[Dict[str, Any]],
                 top_k: int = 5,
                 macro_filter: Optional[Dict[str, tuple]] = None) -> List[int]:
        """Multi-stage retrieval.
        macro_filter: optional dict like {"vix": (low, high)} for conditional retrieval.
        """
        if not candidate_events:
            return []
        q_macro, q_micro, q_sem, q_text = self._blocks(query_event)
        c_macro = self.std_macro.transform(np.stack([vec_from(e, "macro") for e in candidate_events]))
        c_micro = self.std_micro.transform(np.stack([vec_from(e, "micro") for e in candidate_events]))
        c_sem = self.std_sem.transform(np.stack([vec_from(e, "semantic") for e in candidate_events]))
        c_text = embed_texts([e["text"] for e in candidate_events])

        idx_all = np.arange(len(candidate_events))

        # Optional macro-regime filter (raw values, not standardized)
        if macro_filter:
            from .base import MACRO_KEYS
            mask = np.ones(len(candidate_events), dtype=bool)
            for k, (lo, hi) in macro_filter.items():
                col = MACRO_KEYS.index(k)
                raw = np.array([e["macro_features"][k] for e in candidate_events])
                mask &= (raw >= lo) & (raw <= hi)
            idx_all = idx_all[mask]
            if len(idx_all) == 0:
                return []

        # Stage 1: macro distance
        d_macro = norm(c_macro[idx_all] - q_macro, axis=1)
        n1 = max(top_k, int(len(idx_all) * self.stage1_keep))
        keep1 = idx_all[np.argsort(d_macro)[:n1]]

        # Stage 2: micro distance
        d_micro = norm(c_micro[keep1] - q_micro, axis=1)
        n2 = max(top_k, int(len(keep1) * self.stage2_keep))
        keep2 = keep1[np.argsort(d_micro)[:n2]]

        # Stage 3: text + semantic cosine similarity
        def cos(A, b):
            return (A @ b) / (norm(A, axis=1) * norm(b) + 1e-9)
        s_text = cos(c_text[keep2], q_text)
        s_sem = cos(c_sem[keep2], q_sem)
        score = self.w_text * s_text + self.w_sem * s_sem
        order = np.argsort(-score)
        return keep2[order][:top_k].tolist()
