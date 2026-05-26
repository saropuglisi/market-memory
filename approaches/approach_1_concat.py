"""Approach 1: concatenated vector baseline."""
from __future__ import annotations
from typing import List, Dict, Any
import numpy as np
from numpy.linalg import norm

from .base import (EpisodeEncoder, Standardizer, embed_texts,
                   vec_from)


class ConcatBaseline(EpisodeEncoder):
    def __init__(self, equalize_blocks: bool = True):
        self.equalize_blocks = equalize_blocks
        self.name = f"concat_{'eq' if equalize_blocks else 'raw'}"
        self.std_macro = Standardizer()
        self.std_micro = Standardizer()
        self.std_sem = Standardizer()
        self.text_norm = 1.0
        self.block_norms = {"macro": 1.0, "micro": 1.0, "sem": 1.0, "text": 1.0}

    def fit(self, events: List[Dict[str, Any]]) -> None:
        macro = np.stack([vec_from(e, "macro") for e in events])
        micro = np.stack([vec_from(e, "micro") for e in events])
        sem = np.stack([vec_from(e, "semantic") for e in events])
        self.std_macro.fit(macro)
        self.std_micro.fit(micro)
        self.std_sem.fit(sem)
        text_emb = embed_texts([e["text"] for e in events])

        if self.equalize_blocks:
            # Average block norm across training; later divide each block by its mean norm
            self.block_norms["macro"] = float(np.mean(norm(self.std_macro.transform(macro), axis=1)) + 1e-9)
            self.block_norms["micro"] = float(np.mean(norm(self.std_micro.transform(micro), axis=1)) + 1e-9)
            self.block_norms["sem"] = float(np.mean(norm(self.std_sem.transform(sem), axis=1)) + 1e-9)
            self.block_norms["text"] = float(np.mean(norm(text_emb, axis=1)) + 1e-9)

    def encode(self, event: Dict[str, Any]) -> np.ndarray:
        macro = self.std_macro.transform(vec_from(event, "macro")[None, :])[0]
        micro = self.std_micro.transform(vec_from(event, "micro")[None, :])[0]
        sem = self.std_sem.transform(vec_from(event, "semantic")[None, :])[0]
        text = embed_texts([event["text"]])[0]
        if self.equalize_blocks:
            macro = macro / self.block_norms["macro"]
            micro = micro / self.block_norms["micro"]
            sem = sem / self.block_norms["sem"]
            text = text / self.block_norms["text"]
        return np.concatenate([text, macro, micro, sem]).astype(np.float32)

    def encode_batch(self, events: List[Dict[str, Any]]) -> np.ndarray:
        macro = self.std_macro.transform(np.stack([vec_from(e, "macro") for e in events]))
        micro = self.std_micro.transform(np.stack([vec_from(e, "micro") for e in events]))
        sem = self.std_sem.transform(np.stack([vec_from(e, "semantic") for e in events]))
        text = embed_texts([e["text"] for e in events])
        if self.equalize_blocks:
            macro = macro / self.block_norms["macro"]
            micro = micro / self.block_norms["micro"]
            sem = sem / self.block_norms["sem"]
            text = text / self.block_norms["text"]
        return np.concatenate([text, macro, micro, sem], axis=1).astype(np.float32)
