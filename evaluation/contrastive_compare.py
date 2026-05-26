"""Side-by-side comparison of contrastive v1 vs v2 on Level 1."""
from __future__ import annotations
import json
import os
import sys
import time
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from approaches import ConcatBaseline
from approaches.archived.approach_3_contrastive import ContrastiveEncoder
from approaches.archived.approach_3_contrastive_v2 import ContrastiveEncoderV2
from evaluation.metrics import (precision_at_k, reaction_similarity_correlation,
                                conditional_retrieval_quality)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "mock_events.json")
RESULTS_DIR = os.path.join(ROOT, "results")


def evaluate(enc, train, test):
    t0 = time.time()
    enc.fit(train)
    fit_t = time.time() - t0
    t0 = time.time()
    p5, _ = precision_at_k(enc, train, test, k=5)
    p10, _ = precision_at_k(enc, train, test, k=10)
    react = reaction_similarity_correlation(enc, test)
    cond = conditional_retrieval_quality(enc, train, test,
                                         {"vix": (18.0, 100.0)}, k=5)
    eval_t = time.time() - t0
    return {"name": enc.name, "P@5": round(p5, 4), "P@10": round(p10, 4),
            "ReactCorr": round(react, 4), "CondQual": round(cond, 4),
            "fit_s": round(fit_t, 2), "eval_s": round(eval_t, 2)}


def main():
    events = json.load(open(DATA))
    train = [e for e in events if e["split"] == "train"]
    test = [e for e in events if e["split"] == "test"]

    # Baseline reference (concat_eq)
    backbone = ConcatBaseline(equalize_blocks=True)
    r0 = evaluate(backbone, train, test)
    r1 = evaluate(ContrastiveEncoder(epochs=80), train, test)
    r2 = evaluate(ContrastiveEncoderV2(epochs=80), train, test)

    print("\n=== SIDE-BY-SIDE on Level 1 (easy) ===")
    headers = list(r0.keys())
    print(" | ".join(f"{h:>13}" for h in headers))
    for r in [r0, r1, r2]:
        print(" | ".join(f"{str(r[h]):>13}" for h in headers))

    # UMAP plot for contrastive v1, v2, backbone
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import umap

    all_events = train + test
    clusters = [e["ground_truth_cluster"] for e in all_events]
    uniq_c = sorted(set(clusters))
    cmap = plt.get_cmap("tab10")
    color_for = {c: cmap(i) for i, c in enumerate(uniq_c)}

    encs = [backbone, ContrastiveEncoder(epochs=80), ContrastiveEncoderV2(epochs=80)]
    # Re-fit because we want fresh state for plotting (deterministic anyway with seed)
    for e in encs:
        e.fit(train)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, enc in zip(axes, encs):
        Z = enc.encode_batch(all_events)
        red = umap.UMAP(n_components=2, random_state=42,
                        n_neighbors=min(15, len(all_events) - 1))
        X2 = red.fit_transform(Z)
        for c in uniq_c:
            idx = [i for i, cc in enumerate(clusters) if cc == c]
            ax.scatter(X2[idx, 0], X2[idx, 1], s=18, c=[color_for[c]],
                       label=c, alpha=0.75, edgecolors="black", linewidths=0.3)
        ax.set_title(enc.name)
        ax.legend(fontsize=8)
    plt.tight_layout()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(RESULTS_DIR, f"contrastive_compare_umap_{ts}.png")
    plt.savefig(out, dpi=120)
    plt.close()
    print(f"\nUMAP saved: {out}")

    # Dump JSON
    json_out = os.path.join(RESULTS_DIR, f"contrastive_compare_{ts}.json")
    with open(json_out, "w") as f:
        json.dump({"timestamp": ts, "results": [r0, r1, r2]}, f, indent=2)
    print(f"JSON saved: {json_out}")


if __name__ == "__main__":
    main()
