"""Approach 3 v3: contrastive with anti-overfitting regularization.

Changes vs v2:
- Adam weight_decay = 0.02
- Dropout 0.25 between MLP layers
- Early stopping: loss < 0.05 OR no improvement for 10 epochs OR max 100 epochs
- Feature augmentation: gaussian noise std = 5% of per-feature std, only during fit
- Loss curve logged to cache/contrastive_v3_loss_curve.json
"""
from __future__ import annotations
from typing import List, Dict, Any
import json
import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ..base import (EpisodeEncoder, SEED, vec_from, Standardizer, CACHE_DIR)
from ..approach_1_concat import ConcatBaseline


class _MLPDrop(nn.Module):
    def __init__(self, in_dim: int, out_dim: int = 128, hidden: int = 256,
                 dropout: float = 0.25):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(hidden, hidden), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        z = self.net(x)
        return F.normalize(z, dim=-1)


class ContrastiveEncoderV3(EpisodeEncoder):
    name = "contrastive_v3"

    def __init__(self, out_dim: int = 128, max_epochs: int = 100, lr: float = 1e-3,
                 weight_decay: float = 0.02, dropout: float = 0.25,
                 pos_quantile: float = 0.20, neg_quantile: float = 0.80,
                 batch_size: int = 32, tau: float = 0.1,
                 noise_frac: float = 0.05, patience: int = 10,
                 early_stop_loss: float = 0.05):
        self.out_dim = out_dim
        self.max_epochs = max_epochs
        self.lr = lr
        self.weight_decay = weight_decay
        self.dropout = dropout
        self.pos_quantile = pos_quantile
        self.neg_quantile = neg_quantile
        self.batch_size = batch_size
        self.tau = tau
        self.noise_frac = noise_frac
        self.patience = patience
        self.early_stop_loss = early_stop_loss
        self.backbone = ConcatBaseline(equalize_blocks=True)
        self.mlp: nn.Module | None = None
        self.reaction_scaler = Standardizer()
        self.loss_curve_path = os.path.join(CACHE_DIR, "contrastive_v3_loss_curve.json")
        self.feature_std: np.ndarray | None = None

    def fit(self, events: List[Dict[str, Any]]) -> None:
        torch.manual_seed(SEED)
        np.random.seed(SEED)
        self.backbone.fit(events)
        X = self.backbone.encode_batch(events)
        in_dim = X.shape[1]
        X_t = torch.from_numpy(X).float()
        n = len(events)

        # Per-feature std for noise augmentation
        self.feature_std = X.std(axis=0).astype(np.float32) + 1e-9

        # Build pair labels via z-score reaction euclidean + quantile thresholds (v2 mechanics)
        R = np.stack([vec_from(e, "reaction") for e in events]).astype(np.float32)
        self.reaction_scaler.fit(R)
        Rz = self.reaction_scaler.transform(R)
        diffs = Rz[:, None, :] - Rz[None, :, :]
        dist = np.linalg.norm(diffs, axis=-1)
        iu = np.triu_indices(n, k=1)
        vals = dist[iu]
        pos_thr = float(np.quantile(vals, self.pos_quantile))
        neg_thr = float(np.quantile(vals, self.neg_quantile))
        pos_mask = dist <= pos_thr
        neg_mask = dist >= neg_thr
        np.fill_diagonal(pos_mask, False)
        np.fill_diagonal(neg_mask, False)

        pos_per = [np.where(pos_mask[i])[0].tolist() for i in range(n)]
        neg_per = [np.where(neg_mask[i])[0].tolist() for i in range(n)]
        valid = [i for i in range(n) if pos_per[i] and neg_per[i]]
        if not valid:
            print(f"[{self.name}] no valid anchors -> identity backbone")
            self.mlp = None
            return

        self.mlp = _MLPDrop(in_dim, self.out_dim, dropout=self.dropout)
        opt = torch.optim.Adam(self.mlp.parameters(), lr=self.lr,
                               weight_decay=self.weight_decay)
        rng = np.random.default_rng(SEED)
        K = self.batch_size
        feat_std_t = torch.from_numpy(self.feature_std).float()

        loss_history: list[float] = []
        best_loss = float("inf")
        bad_epochs = 0
        stop_reason = "max_epochs"

        for epoch in range(self.max_epochs):
            self.mlp.train()
            rng.shuffle(valid)
            total = 0.0
            steps = 0
            for start in range(0, len(valid), K):
                anchors = valid[start:start + K]
                if not anchors:
                    continue
                pos_idx = np.array([int(rng.choice(pos_per[a])) for a in anchors])
                neg_idx = np.array([rng.choice(neg_per[a], size=K - 1, replace=True)
                                    for a in anchors])
                cand_idx = np.concatenate([pos_idx[:, None], neg_idx], axis=1)  # [B, K]

                # Feature augmentation: gaussian noise * 5% per-feature std, ONLY during training
                a_t = X_t[anchors] + torch.randn_like(X_t[anchors]) * feat_std_t * self.noise_frac
                z_a = self.mlp(a_t)

                cand_flat = X_t[cand_idx.reshape(-1)]
                cand_flat = cand_flat + torch.randn_like(cand_flat) * feat_std_t * self.noise_frac
                z_c = self.mlp(cand_flat).reshape(len(anchors), K, -1)

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
            if (epoch + 1) % 10 == 0:
                print(f"[{self.name}] epoch {epoch+1}/{self.max_epochs} loss={avg:.4f}")

            # Early stopping
            if avg < self.early_stop_loss:
                stop_reason = f"loss<{self.early_stop_loss}@epoch{epoch+1}"
                break
            if avg < best_loss - 1e-4:
                best_loss = avg
                bad_epochs = 0
            else:
                bad_epochs += 1
                if bad_epochs >= self.patience:
                    stop_reason = f"no_improve_{self.patience}@epoch{epoch+1}"
                    break

        self.mlp.eval()

        # Persist loss curve
        try:
            existing = {}
            if os.path.exists(self.loss_curve_path):
                with open(self.loss_curve_path) as f:
                    existing = json.load(f)
        except Exception:
            existing = {}
        run_key = f"n_train={n}_stop={stop_reason}"
        existing[run_key] = {"loss_per_epoch": loss_history,
                             "stop_reason": stop_reason,
                             "final_loss": loss_history[-1] if loss_history else None,
                             "epochs_run": len(loss_history),
                             "valid_anchors": len(valid),
                             "total_anchors": n,
                             "pos_threshold": pos_thr,
                             "neg_threshold": neg_thr}
        with open(self.loss_curve_path, "w") as f:
            json.dump(existing, f, indent=2)
        print(f"[{self.name}] stop={stop_reason} epochs={len(loss_history)} final_loss={loss_history[-1]:.4f}")

    def encode(self, event: Dict[str, Any]) -> np.ndarray:
        x = self.backbone.encode(event)
        if self.mlp is None:
            return x
        self.mlp.eval()
        with torch.no_grad():
            z = self.mlp(torch.from_numpy(x).float()[None, :])[0].numpy()
        return z.astype(np.float32)

    def encode_batch(self, events: List[Dict[str, Any]]) -> np.ndarray:
        X = self.backbone.encode_batch(events)
        if self.mlp is None:
            return X
        self.mlp.eval()
        with torch.no_grad():
            Z = self.mlp(torch.from_numpy(X).float()).numpy()
        return Z.astype(np.float32)
