"""Evaluation metrics."""
from __future__ import annotations
from typing import List, Dict, Any, Tuple
import numpy as np
from numpy.linalg import norm
from scipy.stats import spearmanr

from approaches.base import vec_from


def precision_at_k(encoder, train_events: List[Dict], test_events: List[Dict],
                   k: int = 5) -> Tuple[float, List[float]]:
    """Avg Precision@K using cluster membership as relevance signal.
    Skips test events with cluster == 'NOISE' (no positives expected)."""
    per_event = []
    for q in test_events:
        if q.get("ground_truth_cluster") in ("NOISE", "HYBRID"):
            continue
        top_idx = encoder.retrieve(q, train_events, top_k=k)
        retrieved = [train_events[i]["ground_truth_cluster"] for i in top_idx]
        correct = sum(1 for c in retrieved if c == q["ground_truth_cluster"])
        per_event.append(correct / k)
    if not per_event:
        return 0.0, []
    return float(np.mean(per_event)), per_event


def reaction_similarity_correlation(encoder, test_events: List[Dict]) -> float:
    """Spearman between encoding cosine and reaction-vector similarity on test pairs."""
    Z = encoder.encode_batch(test_events)
    R = np.stack([vec_from(e, "reaction") for e in test_events]).astype(np.float32)

    Zn = Z / (norm(Z, axis=1, keepdims=True) + 1e-9)
    enc_sim_mat = Zn @ Zn.T

    # reaction similarity: 1 - normalized euclidean
    diffs = R[:, None, :] - R[None, :, :]
    dist = norm(diffs, axis=-1)
    max_d = dist.max() + 1e-9
    react_sim_mat = 1.0 - dist / max_d

    n = len(test_events)
    iu = np.triu_indices(n, k=1)
    rho, _ = spearmanr(enc_sim_mat[iu], react_sim_mat[iu])
    return float(rho) if rho == rho else 0.0  # NaN guard


def _utility_at_k_threshold(encoder, train_events, test_events, k, percentile):
    """Mock utility@K with configurable percentile threshold.
    Each retrieved analog scores 1 iff BOTH:
      (i) same ground_truth_cluster as the query, AND
      (ii) reaction-euclidean(query, retrieved) <= P{percentile} of train pair dists.
    Skips NOISE and HYBRID test queries."""
    R_train = np.stack([vec_from(e, "reaction") for e in train_events]).astype(np.float32)
    mu = R_train.mean(axis=0); sd = R_train.std(axis=0) + 1e-9
    R_train_z = (R_train - mu) / sd
    n = len(R_train_z)
    diffs = R_train_z[:, None, :] - R_train_z[None, :, :]
    pair_d = norm(diffs, axis=-1)
    iu = np.triu_indices(n, k=1)
    thr = float(np.quantile(pair_d[iu], percentile))

    scores = []
    for q in test_events:
        c_q = q.get("ground_truth_cluster")
        if c_q in ("NOISE", "HYBRID"):
            continue
        idx = encoder.retrieve(q, train_events, top_k=k)
        if not idx:
            continue
        r_q_z = (vec_from(q, "reaction") - mu) / sd
        good = 0
        for i in idx:
            same_cluster = train_events[i].get("ground_truth_cluster") == c_q
            d = float(norm(R_train_z[i] - r_q_z))
            good += int(same_cluster and (d <= thr))
        scores.append(good / len(idx))
    return float(np.mean(scores)) if scores else 0.0


def utility_at_k_p50(encoder, train_events: List[Dict], test_events: List[Dict],
                     k: int = 5) -> float:
    """Mock utility@K with P50 reaction-distance threshold (original, looser)."""
    return _utility_at_k_threshold(encoder, train_events, test_events, k, 0.50)


def utility_at_k_p25(encoder, train_events: List[Dict], test_events: List[Dict],
                     k: int = 5) -> float:
    """Mock utility@K with P25 threshold (top-quartile reaction-similarity).
    Default from 2026-05-25; tighter than P50, better calibrated on real data."""
    return _utility_at_k_threshold(encoder, train_events, test_events, k, 0.25)


# Backward compat: previous name pointed to P50 implementation.
utility_at_k = utility_at_k_p50


def conditional_retrieval_quality(encoder, train_events: List[Dict],
                                  test_events: List[Dict],
                                  macro_filter: Dict[str, tuple],
                                  k: int = 5) -> float:
    """Fraction of retrieved analogs that respect the macro filter.
    Only meaningful for encoders supporting macro_filter kwarg (Approach 2)."""
    import inspect
    sig = inspect.signature(encoder.retrieve)
    supports = "macro_filter" in sig.parameters
    fracs = []
    for q in test_events:
        if q.get("ground_truth_cluster") in ("NOISE", "HYBRID"):
            continue
        if supports:
            idx = encoder.retrieve(q, train_events, top_k=k, macro_filter=macro_filter)
        else:
            idx = encoder.retrieve(q, train_events, top_k=k)
        if not idx:
            continue
        ok = 0
        for i in idx:
            cand = train_events[i]
            inside = all(lo <= cand["macro_features"][key] <= hi
                         for key, (lo, hi) in macro_filter.items())
            ok += int(inside)
        fracs.append(ok / len(idx))
    return float(np.mean(fracs)) if fracs else 0.0
