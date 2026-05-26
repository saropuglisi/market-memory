"""Diagnose why ContrastiveEncoder has low ReactCorr.

Hypotheses to test:
- H1: positives are too dense (in-batch negatives are often valid positives)
       -> InfoNCE has no clean negative signal.
- H2: MLP collapses embeddings within cluster, destroying fine-grained
       reaction-similarity ordering even though P@K stays high.
- H3: Loss never moves: training is effectively no-op + normalization,
       which can still degrade reaction_corr vs unnormalized backbone.
"""
from __future__ import annotations
import json
import os
import sys

import numpy as np
from numpy.linalg import norm
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from approaches import ConcatBaseline, ContrastiveEncoder
from approaches.base import vec_from, REACTION_KEYS

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "mock_events.json")


def reaction_cos(events):
    R = np.stack([vec_from(e, "reaction") for e in events]).astype(np.float32)
    R = R / (norm(R, axis=1, keepdims=True) + 1e-9)
    return R @ R.T


def reaction_sim_normed_dist(events):
    R = np.stack([vec_from(e, "reaction") for e in events]).astype(np.float32)
    diffs = R[:, None, :] - R[None, :, :]
    d = norm(diffs, axis=-1)
    return 1 - d / (d.max() + 1e-9)


def main():
    events = json.load(open(DATA))
    train = [e for e in events if e["split"] == "train"]
    test = [e for e in events if e["split"] == "test"]

    # --- H1: positive density
    cos_train = reaction_cos(train)
    n = len(train)
    iu = np.triu_indices(n, k=1)
    pos_mask = cos_train > 0.7
    neg_mask = cos_train < 0.0
    np.fill_diagonal(pos_mask, False)
    n_pairs = n * (n - 1) // 2
    n_pos = int(pos_mask[iu].sum())
    n_neg = int(neg_mask[iu].sum())
    print(f"[H1] train pairs: {n_pairs} total | positives (cos>0.7): {n_pos} ({n_pos/n_pairs:.1%}) | "
          f"negatives (cos<0.0): {n_neg} ({n_neg/n_pairs:.1%})")
    pos_per_anchor = pos_mask.sum(axis=1)
    print(f"      positives per anchor: mean={pos_per_anchor.mean():.1f} "
          f"median={np.median(pos_per_anchor):.0f} min={pos_per_anchor.min()} max={pos_per_anchor.max()}")
    print(f"      anchors with 0 positives: {(pos_per_anchor == 0).sum()}/{n}")
    # P(in-batch negative is actually a positive)
    batch_size = 32
    print(f"      with batch_size={batch_size}, expected positive collisions "
          f"per anchor among batch negatives: ~{(batch_size-1) * pos_per_anchor.mean() / n:.2f}")

    # By cluster
    clusters = sorted(set(e["ground_truth_cluster"] for e in train))
    print(f"      cluster distribution train: {{c: sum(e['ground_truth_cluster']==c for e in train) for c in clusters}}")
    for c in clusters:
        idx = [i for i, e in enumerate(train) if e["ground_truth_cluster"] == c]
        if len(idx) < 2:
            continue
        sub = cos_train[np.ix_(idx, idx)]
        triu_sub = sub[np.triu_indices(len(idx), k=1)]
        print(f"      cluster {c}: n={len(idx)} | mean reaction-cos within: {triu_sub.mean():.3f} "
              f"| frac>0.7 within: {(triu_sub>0.7).mean():.1%}")

    # --- H2/H3: train both encoders, compare embeddings
    backbone = ConcatBaseline(equalize_blocks=True)
    backbone.fit(train)
    Z_back_test = backbone.encode_batch(test)

    contr = ContrastiveEncoder(epochs=80)
    contr.fit(train)
    Z_cont_test = contr.encode_batch(test)

    R_test_sim = reaction_sim_normed_dist(test)
    iu_t = np.triu_indices(len(test), k=1)

    def enc_sim(Z):
        Zn = Z / (norm(Z, axis=1, keepdims=True) + 1e-9)
        return Zn @ Zn.T

    sim_back = enc_sim(Z_back_test)
    sim_cont = enc_sim(Z_cont_test)
    rho_back, _ = spearmanr(sim_back[iu_t], R_test_sim[iu_t])
    rho_cont, _ = spearmanr(sim_cont[iu_t], R_test_sim[iu_t])
    print(f"\n[H2/H3] ReactCorr backbone(eq concat) test = {rho_back:.4f}")
    print(f"[H2/H3] ReactCorr contrastive      test = {rho_cont:.4f}")

    # Within-cluster spread: if MLP collapses points, within-cluster pairwise sim ~ 1
    test_clusters = [e["ground_truth_cluster"] for e in test]
    for label, S in [("backbone", sim_back), ("contrastive", sim_cont)]:
        for c in sorted(set(test_clusters)):
            idx = [i for i, cc in enumerate(test_clusters) if cc == c]
            if len(idx) < 2:
                continue
            sub = S[np.ix_(idx, idx)]
            tri = sub[np.triu_indices(len(idx), k=1)]
            print(f"      {label}/{c}: within-cluster sim mean={tri.mean():.3f} std={tri.std():.3f} "
                  f"min={tri.min():.3f} (n={len(idx)})")

    # Cross-cluster
    for label, S in [("backbone", sim_back), ("contrastive", sim_cont)]:
        cross_vals = []
        within_vals = []
        for i in range(len(test)):
            for j in range(i + 1, len(test)):
                if test_clusters[i] == test_clusters[j]:
                    within_vals.append(S[i, j])
                else:
                    cross_vals.append(S[i, j])
        print(f"      {label}: within-cluster mean sim={np.mean(within_vals):.3f} "
              f"| cross-cluster mean sim={np.mean(cross_vals):.3f} "
              f"| gap={np.mean(within_vals)-np.mean(cross_vals):.3f}")


if __name__ == "__main__":
    main()
