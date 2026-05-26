"""Common interface + shared utilities for all encoders."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import hashlib
import json
import os
import random

import numpy as np

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

MACRO_KEYS = ["vix", "yield_10y", "yield_curve_slope", "credit_spread", "dxy"]
MICRO_KEYS = ["return_60d", "realized_vol_60d", "drawdown_from_high",
              "sector_return_60d", "relative_strength"]
SEMANTIC_KEYS = ["confidence_score", "hedging_count", "guidance_direction",
                 "uncertainty_markers"]
REACTION_KEYS = ["return", "realized_vol", "max_drawdown", "persistence"]

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def vec_from(event: Dict[str, Any], block: str) -> np.ndarray:
    keys = {"macro": MACRO_KEYS, "micro": MICRO_KEYS,
            "semantic": SEMANTIC_KEYS, "reaction": REACTION_KEYS}[block]
    src = event["macro_features" if block == "macro" else
                "micro_features" if block == "micro" else
                "semantic_features" if block == "semantic" else
                "reaction_30d"]
    return np.array([float(src[k]) for k in keys], dtype=np.float32)


class _TextEmbedderSingleton:
    _model = None
    _cache: Dict[str, np.ndarray] = {}
    _cache_path = os.path.join(CACHE_DIR, "text_emb_minilm.npz")

    @classmethod
    def model(cls):
        if cls._model is None:
            from sentence_transformers import SentenceTransformer
            cls._model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        return cls._model

    @classmethod
    def _load_disk(cls):
        if cls._cache:
            return
        if os.path.exists(cls._cache_path):
            data = np.load(cls._cache_path, allow_pickle=True)
            keys = data["keys"]
            vecs = data["vecs"]
            cls._cache = {str(k): v for k, v in zip(keys, vecs)}

    @classmethod
    def _save_disk(cls):
        if not cls._cache:
            return
        keys = np.array(list(cls._cache.keys()))
        vecs = np.array(list(cls._cache.values()), dtype=np.float32)
        np.savez(cls._cache_path, keys=keys, vecs=vecs)

    @classmethod
    def embed(cls, texts: List[str]) -> np.ndarray:
        cls._load_disk()
        missing = [t for t in texts if _hash(t) not in cls._cache]
        if missing:
            new_vecs = cls.model().encode(missing, show_progress_bar=False,
                                           convert_to_numpy=True,
                                           normalize_embeddings=False)
            for t, v in zip(missing, new_vecs):
                cls._cache[_hash(t)] = v.astype(np.float32)
            cls._save_disk()
        return np.stack([cls._cache[_hash(t)] for t in texts])


def _hash(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def embed_texts(texts: List[str]) -> np.ndarray:
    return _TextEmbedderSingleton.embed(texts)


class EpisodeEncoder(ABC):
    name: str = "abstract"

    @abstractmethod
    def fit(self, events: List[Dict[str, Any]]) -> None:
        ...

    @abstractmethod
    def encode(self, event: Dict[str, Any]) -> np.ndarray:
        ...

    def encode_batch(self, events: List[Dict[str, Any]]) -> np.ndarray:
        return np.stack([self.encode(e) for e in events])

    def similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        from numpy.linalg import norm
        return float(np.dot(vec_a, vec_b) / (norm(vec_a) * norm(vec_b) + 1e-9))

    def retrieve(self, query_event: Dict[str, Any],
                 candidate_events: List[Dict[str, Any]],
                 top_k: int = 5) -> List[int]:
        q = self.encode(query_event)
        cands = self.encode_batch(candidate_events)
        sims = np.array([self.similarity(q, c) for c in cands])
        return np.argsort(-sims)[:top_k].tolist()


class Standardizer:
    """Per-block z-score normalization fit on training set."""
    def __init__(self):
        self.mu: Optional[np.ndarray] = None
        self.sigma: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray):
        self.mu = X.mean(axis=0)
        self.sigma = X.std(axis=0) + 1e-9

    def transform(self, X: np.ndarray) -> np.ndarray:
        return (X - self.mu) / self.sigma
