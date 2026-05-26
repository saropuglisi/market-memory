"""Approach 3: contrastive learning on reaction-similar pairs."""
from __future__ import annotations
from typing import List, Dict, Any
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ..base import (EpisodeEncoder, SEED, REACTION_KEYS, vec_from)
from ..approach_1_concat import ConcatBaseline


class _MLP(nn.Module):
    def __init__(self, in_dim: int, out_dim: int = 128, hidden: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        z = self.net(x)
        return F.normalize(z, dim=-1)


def _reaction_cos(events: List[Dict[str, Any]]) -> np.ndarray:
    R = np.stack([vec_from(e, "reaction") for e in events]).astype(np.float32)
    R = R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-9)
    return R @ R.T


class ContrastiveEncoder(EpisodeEncoder):
    name = "contrastive"

    def __init__(self, out_dim: int = 128, epochs: int = 80, lr: float = 1e-3,
                 pos_thresh: float = 0.7, neg_thresh: float = 0.0,
                 batch_size: int = 32, tau: float = 0.1):
        self.out_dim = out_dim
        self.epochs = epochs
        self.lr = lr
        self.pos_thresh = pos_thresh
        self.neg_thresh = neg_thresh
        self.batch_size = batch_size
        self.tau = tau
        self.backbone = ConcatBaseline(equalize_blocks=True)
        self.mlp: nn.Module | None = None

    def fit(self, events: List[Dict[str, Any]]) -> None:
        torch.manual_seed(SEED)
        np.random.seed(SEED)
        # Train only on events with split == "train" (caller already filters)
        self.backbone.fit(events)
        X = self.backbone.encode_batch(events)
        in_dim = X.shape[1]
        X_t = torch.from_numpy(X).float()

        # Build pair labels from reaction similarity
        sim = _reaction_cos(events)
        n = len(events)
        pos = sim > self.pos_thresh
        neg = sim < self.neg_thresh
        np.fill_diagonal(pos, False)

        # InfoNCE-style: for each anchor, sample positives + use rest of batch as negatives
        pos_idx_per_anchor = [np.where(pos[i])[0].tolist() for i in range(n)]
        valid_anchors = [i for i, p in enumerate(pos_idx_per_anchor) if p]
        if not valid_anchors:
            print(f"[{self.name}] No positive pairs at thresh={self.pos_thresh}, fall back to identity")
            self.mlp = None
            self._in_dim = in_dim
            return

        self.mlp = _MLP(in_dim, self.out_dim)
        opt = torch.optim.Adam(self.mlp.parameters(), lr=self.lr)
        rng = np.random.default_rng(SEED)

        for epoch in range(self.epochs):
            rng.shuffle(valid_anchors)
            total_loss = 0.0
            steps = 0
            for start in range(0, len(valid_anchors), self.batch_size):
                anchors = valid_anchors[start:start + self.batch_size]
                positives = [int(rng.choice(pos_idx_per_anchor[a])) for a in anchors]
                a_t = X_t[anchors]
                p_t = X_t[positives]
                # Other anchors in batch serve as in-batch negatives
                z_a = self.mlp(a_t)
                z_p = self.mlp(p_t)
                # logits: a_i . p_j / tau, target = i
                logits = z_a @ z_p.T / self.tau
                target = torch.arange(len(anchors))
                loss = F.cross_entropy(logits, target)
                opt.zero_grad()
                loss.backward()
                opt.step()
                total_loss += loss.item()
                steps += 1
            if (epoch + 1) % 20 == 0:
                print(f"[{self.name}] epoch {epoch+1}/{self.epochs} loss={total_loss/max(1,steps):.4f}")
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
