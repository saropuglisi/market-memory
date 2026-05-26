"""Approach 3 v2: contrastive learning with corrected pair definition.

Changes vs v1:
1. Reaction similarity: euclidean distance on z-score-normalized reaction
   vectors (z-score fit only on training events).
2. Positive/negative thresholds set on quantiles of the actual distance
   distribution: bottom 20% -> positives, top 20% -> negatives.
3. Logs distance histogram pre/post normalization so we can see whether
   the pair sets are balanced.
"""
from __future__ import annotations
from typing import List, Dict, Any
import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ..base import (EpisodeEncoder, SEED, vec_from, Standardizer, CACHE_DIR)
from ..approach_1_concat import ConcatBaseline
from .approach_3_contrastive import _MLP


def _reaction_distance_matrix(events: List[Dict[str, Any]], scaler: Standardizer):
    R = np.stack([vec_from(e, "reaction") for e in events]).astype(np.float32)
    Rz = scaler.transform(R)
    # pairwise euclidean
    diffs = Rz[:, None, :] - Rz[None, :, :]
    return np.linalg.norm(diffs, axis=-1).astype(np.float32), R, Rz


def _log_distance_dist(label: str, dist_mat: np.ndarray, log_path: str):
    n = dist_mat.shape[0]
    iu = np.triu_indices(n, k=1)
    vals = dist_mat[iu]
    qs = np.quantile(vals, [0.0, 0.1, 0.2, 0.5, 0.8, 0.9, 1.0])
    lines = [
        f"=== {label} ===",
        f"n_pairs={len(vals)} mean={vals.mean():.4f} std={vals.std():.4f}",
        f"quantiles 0/10/20/50/80/90/100 = " + " ".join(f"{q:.3f}" for q in qs),
    ]
    print("\n".join(lines))
    with open(log_path, "a") as f:
        f.write("\n".join(lines) + "\n")
    return vals, qs


class ContrastiveEncoderV2(EpisodeEncoder):
    name = "contrastive_v2"

    def __init__(self, out_dim: int = 128, epochs: int = 80, lr: float = 1e-3,
                 pos_quantile: float = 0.20, neg_quantile: float = 0.80,
                 batch_size: int = 32, tau: float = 0.1):
        self.out_dim = out_dim
        self.epochs = epochs
        self.lr = lr
        self.pos_quantile = pos_quantile
        self.neg_quantile = neg_quantile
        self.batch_size = batch_size
        self.tau = tau
        self.backbone = ConcatBaseline(equalize_blocks=True)
        self.mlp: nn.Module | None = None
        self.reaction_scaler = Standardizer()
        self.log_path = os.path.join(CACHE_DIR, "contrastive_v2_distlog.txt")

    def fit(self, events: List[Dict[str, Any]]) -> None:
        torch.manual_seed(SEED)
        np.random.seed(SEED)
        self.backbone.fit(events)
        X = self.backbone.encode_batch(events)
        in_dim = X.shape[1]
        X_t = torch.from_numpy(X).float()
        n = len(events)

        # --- Step 1: log raw reaction-vector pairwise euclidean (pre z-score)
        with open(self.log_path, "w") as f:
            f.write(f"contrastive_v2 fit log\n")
        R_raw = np.stack([vec_from(e, "reaction") for e in events]).astype(np.float32)
        diffs_raw = R_raw[:, None, :] - R_raw[None, :, :]
        dist_raw = np.linalg.norm(diffs_raw, axis=-1)
        _log_distance_dist("RAW reaction euclidean (pre z-score)", dist_raw, self.log_path)

        # --- Step 2: z-score reaction, log again
        self.reaction_scaler.fit(R_raw)
        dist_z, _, _ = _reaction_distance_matrix(events, self.reaction_scaler)
        _log_distance_dist("Z-SCORED reaction euclidean", dist_z, self.log_path)

        # --- Step 3: quantile-based pair definition
        iu = np.triu_indices(n, k=1)
        vals = dist_z[iu]
        pos_thr = float(np.quantile(vals, self.pos_quantile))
        neg_thr = float(np.quantile(vals, self.neg_quantile))
        pos_mask = dist_z <= pos_thr
        neg_mask = dist_z >= neg_thr
        np.fill_diagonal(pos_mask, False)
        np.fill_diagonal(neg_mask, False)

        n_pairs = len(vals)
        n_pos = int(pos_mask[iu].sum())
        n_neg = int(neg_mask[iu].sum())
        msg = (f"thresholds: pos<={pos_thr:.4f} (q={self.pos_quantile}) "
               f"neg>={neg_thr:.4f} (q={self.neg_quantile}) | "
               f"pos pairs={n_pos} ({n_pos/n_pairs:.1%}) "
               f"neg pairs={n_neg} ({n_neg/n_pairs:.1%})")
        print(msg)
        with open(self.log_path, "a") as f:
            f.write(msg + "\n")

        pos_per_anchor = [np.where(pos_mask[i])[0].tolist() for i in range(n)]
        neg_per_anchor = [np.where(neg_mask[i])[0].tolist() for i in range(n)]
        valid = [i for i in range(n) if pos_per_anchor[i] and neg_per_anchor[i]]
        ppa = np.array([len(p) for p in pos_per_anchor])
        npa = np.array([len(p) for p in neg_per_anchor])
        msg2 = (f"per-anchor pos: mean={ppa.mean():.1f} min={ppa.min()} max={ppa.max()} | "
                f"per-anchor neg: mean={npa.mean():.1f} min={npa.min()} max={npa.max()} | "
                f"valid anchors (have both): {len(valid)}/{n}")
        print(msg2)
        with open(self.log_path, "a") as f:
            f.write(msg2 + "\n")

        if not valid:
            print(f"[{self.name}] no valid anchors -> fall back to backbone identity")
            self.mlp = None
            return

        # --- Step 4: triplet-style InfoNCE: anchor + positive + sampled negatives
        # For each anchor, build a batch of [pos, neg1..neg(K-1)] where K=batch_size.
        # logit target is 0 (the positive is first).
        self.mlp = _MLP(in_dim, self.out_dim)
        opt = torch.optim.Adam(self.mlp.parameters(), lr=self.lr)
        rng = np.random.default_rng(SEED)
        K = self.batch_size

        loss_history = []
        for epoch in range(self.epochs):
            rng.shuffle(valid)
            total = 0.0
            steps = 0
            for start in range(0, len(valid), K):
                anchors = valid[start:start + K]
                if not anchors:
                    continue
                pos_idx = np.array([int(rng.choice(pos_per_anchor[a])) for a in anchors])
                # For each anchor: sample K-1 explicit negatives
                neg_idx = np.array([rng.choice(neg_per_anchor[a], size=K - 1, replace=True)
                                    for a in anchors])  # [B, K-1]
                a_t = X_t[anchors]
                p_t = X_t[pos_idx]
                z_a = self.mlp(a_t)                       # [B, d]
                z_p = self.mlp(p_t)                       # [B, d]
                # Stack candidates per anchor: [B, K, d] = [positive, neg1..neg(K-1)]
                cand_idx = np.concatenate([pos_idx[:, None], neg_idx], axis=1)  # [B, K]
                cand_flat = X_t[cand_idx.reshape(-1)]
                z_c = self.mlp(cand_flat).reshape(len(anchors), K, -1)         # [B, K, d]
                # logits: a_b . c_{b,k} / tau
                logits = torch.einsum("bd,bkd->bk", z_a, z_c) / self.tau
                target = torch.zeros(len(anchors), dtype=torch.long)
                loss = F.cross_entropy(logits, target)
                opt.zero_grad()
                loss.backward()
                opt.step()
                total += loss.item()
                steps += 1
            avg = total / max(1, steps)
            loss_history.append(avg)
            if (epoch + 1) % 20 == 0:
                print(f"[{self.name}] epoch {epoch+1}/{self.epochs} loss={avg:.4f}")

        with open(self.log_path, "a") as f:
            f.write(f"final loss curve (every 5): " +
                    " ".join(f"{loss_history[i]:.3f}" for i in range(0, len(loss_history), 5)) +
                    "\n")
        self.mlp.eval()

    def encode(self, event: Dict[str, Any]) -> np.ndarray:
        x = self.backbone.encode(event)
        if self.mlp is None:
            return x
        with torch.no_grad():
            z = self.mlp(torch.from_numpy(x).float()[None, :])[0].numpy()
        return z.astype(np.float32)

    def encode_batch(self, events: List[Dict[str, Any]]) -> np.ndarray:
        X = self.backbone.encode_batch(events)
        if self.mlp is None:
            return X
        with torch.no_grad():
            Z = self.mlp(torch.from_numpy(X).float()).numpy()
        return Z.astype(np.float32)
