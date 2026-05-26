"""Sanity check del nuovo L2: testi unici, sector diversity, intra/inter gap."""
from __future__ import annotations
import json
import os
import sys
import numpy as np
from numpy.linalg import norm

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from approaches.base import vec_from, MACRO_KEYS, MICRO_KEYS, SEMANTIC_KEYS


def check(path: str, label: str):
    events = json.load(open(path))
    train = [e for e in events if e["split"] == "train"]
    # Standardize numeric features (z-score on train) and compute intra vs inter cluster distance
    def stack(block):
        return np.stack([vec_from(e, block) for e in train])
    X = np.concatenate([stack("macro"), stack("micro"), stack("semantic")], axis=1)
    mu = X.mean(axis=0); sd = X.std(axis=0) + 1e-9
    Xz = (X - mu) / sd
    clusters = [e["ground_truth_cluster"] for e in train]

    valid_idx = [i for i, c in enumerate(clusters) if c in ("A", "B", "C", "D")]
    Xv = Xz[valid_idx]; cv = [clusters[i] for i in valid_idx]
    n = len(Xv)
    diffs = Xv[:, None, :] - Xv[None, :, :]
    d = norm(diffs, axis=-1)
    intra = []
    inter = []
    for i in range(n):
        for j in range(i+1, n):
            (intra if cv[i] == cv[j] else inter).append(d[i, j])
    intra_m = float(np.mean(intra)); inter_m = float(np.mean(inter))

    texts_total = len(set(e["text"] for e in events))
    sectors_per_cluster = {}
    for e in events:
        c = e["ground_truth_cluster"]
        if c in ("NOISE", "HYBRID"):
            continue
        sectors_per_cluster.setdefault(c, set()).add(e["sector"])

    print(f"=== {label} ===")
    print(f"  unique texts (total): {texts_total}  [target >= 100]")
    print(f"  sectors per cluster: " + ", ".join(f"{k}={len(v)}" for k, v in sorted(sectors_per_cluster.items()))
          + "  [target >= 3 ciascuno]")
    print(f"  intra-cluster mean dist (z-scored): {intra_m:.3f}")
    print(f"  inter-cluster mean dist (z-scored): {inter_m:.3f}")
    print(f"  gap (inter - intra): {inter_m - intra_m:.3f}  [target ~1.0-1.5; L1 was ~3.2]")
    return texts_total, sectors_per_cluster, intra_m, inter_m


if __name__ == "__main__":
    check("data/mock_events_L1.json", "L1 (original)")
    print()
    check("data/mock_events_L2.json", "L2 v2 (new)")
    print()
    check("data/mock_events_L2_v1_archived.json", "L2 v1 (archived)")
