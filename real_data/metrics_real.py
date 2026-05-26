"""Metrics adatte ai dati reali (no ground_truth_cluster).

- self_consistency_at_k: similarità media intra-top-K vs random baseline.
- reaction_corr_real: Spearman tra encoding-sim e reaction-sim (uguale al mock,
  ma su pair test-test reali).
- utility_at_k_real: Spearman tra rank-by-encoding-sim e rank-by-reaction-sim
  sui top-K.
- conditional_quality_real: frazione dei top-K che soddisfa un filtro macro.
- temporal_diversity: std (in giorni) delle date dei top-K.
"""
from __future__ import annotations
from typing import List, Dict
import numpy as np
from numpy.linalg import norm
from scipy.stats import spearmanr
from datetime import datetime
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from approaches.base import vec_from


def _encode_sim_matrix(Z):
    Zn = Z / (norm(Z, axis=1, keepdims=True) + 1e-9)
    return Zn @ Zn.T


def _reaction_dist_matrix(events: List[Dict]) -> np.ndarray:
    R = np.stack([vec_from(e, "reaction") for e in events]).astype(np.float32)
    mu = R.mean(axis=0); sd = R.std(axis=0) + 1e-9
    Rz = (R - mu) / sd
    diffs = Rz[:, None, :] - Rz[None, :, :]
    return norm(diffs, axis=-1)


def self_consistency_at_k(encoder, train_events: List[Dict], test_events: List[Dict],
                          k: int = 5, n_random: int = 50, seed: int = 42) -> dict:
    """Avg intra-top-K cosine sim vs avg cos sim of random K-subset.
    Returns {self_consistency, random_baseline, lift}."""
    rng = np.random.default_rng(seed)
    Z_train = encoder.encode_batch(train_events)
    Zn = Z_train / (norm(Z_train, axis=1, keepdims=True) + 1e-9)
    sim_train = Zn @ Zn.T

    def mean_intra(idxs):
        if len(idxs) < 2:
            return 0.0
        s = sim_train[np.ix_(idxs, idxs)]
        iu = np.triu_indices(len(idxs), k=1)
        return float(s[iu].mean())

    sc_values = []
    rand_values = []
    n_train = len(train_events)
    for q in test_events:
        idx = encoder.retrieve(q, train_events, top_k=k)
        if not idx:
            continue
        sc_values.append(mean_intra(idx))
    for _ in range(n_random):
        idx = rng.choice(n_train, size=k, replace=False).tolist()
        rand_values.append(mean_intra(idx))
    sc = float(np.mean(sc_values)) if sc_values else 0.0
    rb = float(np.mean(rand_values)) if rand_values else 0.0
    return {"self_consistency": sc, "random_baseline": rb, "lift": sc - rb}


def reaction_corr_real(encoder, test_events: List[Dict]) -> float:
    if len(test_events) < 2:
        return 0.0
    Z = encoder.encode_batch(test_events)
    enc_sim = _encode_sim_matrix(Z)
    rd = _reaction_dist_matrix(test_events)
    react_sim = 1.0 - rd / (rd.max() + 1e-9)
    iu = np.triu_indices(len(test_events), k=1)
    rho, _ = spearmanr(enc_sim[iu], react_sim[iu])
    return float(rho) if rho == rho else 0.0


def utility_at_k_real(encoder, train_events: List[Dict], test_events: List[Dict],
                     k: int = 5) -> float:
    """Per ogni query test, Spearman tra rank-by-encoding-sim e
    rank-by-reaction-sim sui top-K retrieved. Aggregate mean."""
    R_train = np.stack([vec_from(e, "reaction") for e in train_events]).astype(np.float32)
    mu = R_train.mean(axis=0); sd = R_train.std(axis=0) + 1e-9
    R_train_z = (R_train - mu) / sd
    rhos = []
    for q in test_events:
        idx = encoder.retrieve(q, train_events, top_k=k)
        if len(idx) < 2:
            continue
        q_v = encoder.encode(q)
        # encoding sims
        cv = encoder.encode_batch([train_events[i] for i in idx])
        enc_sims = []
        for i, c in enumerate(cv):
            enc_sims.append(float(np.dot(q_v, c) / (norm(q_v) * norm(c) + 1e-9)))
        # reaction sims
        r_q_z = (vec_from(q, "reaction") - mu) / sd
        react_sims = []
        for i in idx:
            d = float(norm(R_train_z[i] - r_q_z))
            react_sims.append(-d)  # negate so higher = closer
        rho, _ = spearmanr(enc_sims, react_sims)
        if rho == rho:
            rhos.append(rho)
    return float(np.mean(rhos)) if rhos else 0.0


def utility_at_k_real_threshold(train_events: List[Dict], test_events: List[Dict],
                                retrievals: Dict, percentile: float = 0.25) -> float:
    """Real-data utility@K (no ground-truth cluster). Score = fraction of top-K
    retrieved whose z-scored reaction-distance to the query is <= P{percentile}
    of train pair distances.

    `retrievals`: {query_id: [retrieved_train_id, ...]} from a saved run.
    No encoder needed — uses pre-computed retrievals + reaction vectors.
    """
    R_train = np.stack([vec_from(e, "reaction") for e in train_events]).astype(np.float32)
    mu = R_train.mean(axis=0); sd = R_train.std(axis=0) + 1e-9
    R_train_z = (R_train - mu) / sd
    n = len(R_train_z)
    diffs = R_train_z[:, None, :] - R_train_z[None, :, :]
    pair_d = norm(diffs, axis=-1)
    iu = np.triu_indices(n, k=1)
    thr = float(np.quantile(pair_d[iu], percentile))

    id_to_train_idx = {e["id"]: i for i, e in enumerate(train_events)}
    scores = []
    for q in test_events:
        retr_ids = retrievals.get(q["id"])
        if not retr_ids:
            continue
        r_q_z = (vec_from(q, "reaction") - mu) / sd
        good = 0; total = 0
        for rid in retr_ids:
            ti = id_to_train_idx.get(rid)
            if ti is None:
                continue
            d = float(norm(R_train_z[ti] - r_q_z))
            good += int(d <= thr)
            total += 1
        if total:
            scores.append(good / total)
    return float(np.mean(scores)) if scores else 0.0


def random_baseline_utility(train_events: List[Dict], test_events: List[Dict],
                            k: int = 5, percentile: float = 0.25,
                            n_random: int = 200, seed: int = 42) -> float:
    """Expected utility@K threshold under random K-subset retrieval.
    Same threshold definition as utility_at_k_real_threshold."""
    rng = np.random.default_rng(seed)
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
        r_q_z = (vec_from(q, "reaction") - mu) / sd
        for _ in range(n_random):
            idxs = rng.choice(n, size=k, replace=False)
            good = sum(int(float(norm(R_train_z[i] - r_q_z)) <= thr) for i in idxs)
            scores.append(good / k)
    return float(np.mean(scores)) if scores else 0.0


def conditional_quality_real(encoder, train_events, test_events,
                             macro_filter: Dict[str, tuple], k: int = 5) -> float:
    """Frazione dei top-K che rispetta filtro macro."""
    import inspect
    sig = inspect.signature(encoder.retrieve)
    supports = "macro_filter" in sig.parameters
    fracs = []
    for q in test_events:
        if supports:
            idx = encoder.retrieve(q, train_events, top_k=k, macro_filter=macro_filter)
        else:
            idx = encoder.retrieve(q, train_events, top_k=k)
        if not idx:
            continue
        ok = 0
        for i in idx:
            c = train_events[i]
            inside = all(lo <= c["macro_features"][key] <= hi for key, (lo, hi) in macro_filter.items())
            ok += int(inside)
        fracs.append(ok / len(idx))
    return float(np.mean(fracs)) if fracs else 0.0


def temporal_diversity(encoder, train_events, test_events, k: int = 5) -> float:
    """Avg std (in giorni) delle date dei top-K retrieved across queries."""
    stds = []
    for q in test_events:
        idx = encoder.retrieve(q, train_events, top_k=k)
        if len(idx) < 2:
            continue
        dates = [pd.to_datetime(train_events[i]["date"]) for i in idx]
        days = [(d - dates[0]).total_seconds() / 86400 for d in dates]
        stds.append(float(np.std(days)))
    return float(np.mean(stds)) if stds else 0.0
