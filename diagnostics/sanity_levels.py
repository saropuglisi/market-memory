"""Sanity check per livelli L3/L4/L5: gap intra/inter per blocco di feature."""
from __future__ import annotations
import json
import os
import sys
import numpy as np
from numpy.linalg import norm

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from approaches.base import vec_from


def gap(events, blocks):
    train = [e for e in events if e["split"] == "train"
             and e["ground_truth_cluster"] in ("A", "B", "C", "D")]
    X = np.concatenate([np.stack([vec_from(e, b) for e in train]) for b in blocks], axis=1)
    mu = X.mean(axis=0); sd = X.std(axis=0) + 1e-9
    Xz = (X - mu) / sd
    c = [e["ground_truth_cluster"] for e in train]
    n = len(Xz)
    diffs = Xz[:, None, :] - Xz[None, :, :]
    d = norm(diffs, axis=-1)
    intra = []; inter = []
    for i in range(n):
        for j in range(i+1, n):
            (intra if c[i] == c[j] else inter).append(d[i, j])
    return float(np.mean(intra)), float(np.mean(inter))


def check(path, label, expectations):
    events = json.load(open(path))
    texts = len(set(e["text"] for e in events))
    counts = {}
    sectors = {}
    for e in events:
        c = e["ground_truth_cluster"]
        counts[c] = counts.get(c, 0) + 1
        if c not in ("NOISE", "HYBRID"):
            sectors.setdefault(c, set()).add(e["sector"])
    n_total = len(events)
    print(f"=== {label} ===")
    print(f"  n={n_total}  unique_texts={texts}  clusters={dict(sorted(counts.items()))}")
    print(f"  sectors/cluster: " + ", ".join(f"{k}={len(v)}" for k, v in sorted(sectors.items())))
    for label2, blocks in [("macro+micro+semantic", ["macro", "micro", "semantic"]),
                           ("macro+micro only",      ["macro", "micro"]),
                           ("semantic only",         ["semantic"]),
                           ("reaction only",         ["reaction"])]:
        intra, inter = gap(events, blocks)
        gap_v = inter - intra
        target = expectations.get(label2)
        mark = ""
        if target:
            lo, hi = target
            mark = " ✓" if lo <= gap_v <= hi else f"  [target {lo}-{hi}]"
        print(f"  gap[{label2:24s}] intra={intra:.2f} inter={inter:.2f} GAP={gap_v:+.2f}{mark}")
    print()


if __name__ == "__main__":
    # Expectations: blocks -> (lo, hi) target gap
    check("data/mock_events_L1.json", "L1", {
        "macro+micro+semantic": (3.0, 3.6),
    })
    check("data/mock_events_L2.json", "L2 v2", {
        "macro+micro+semantic": (1.0, 1.7),
    })
    check("data/mock_events_L3.json", "L3 (hybrid + std x2 + shrink 51%)", {
        "macro+micro+semantic": (0.6, 1.2),
    })
    check("data/mock_events_L4.json", "L4 (shared macro/micro)", {
        "macro+micro only": (-0.5, 0.5),
        "semantic only": (1.0, 2.0),
    })
    check("data/mock_events_L5.json", "L5 (reaction-driven)", {
        "macro+micro+semantic": (0.3, 1.0),
        "reaction only": (2.0, 5.0),
    })
