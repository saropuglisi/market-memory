"""Runner: fit all encoders, evaluate, dump JSON + markdown + plots + UMAP."""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from typing import List, Dict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from approaches import ConcatBaseline, FactorizedMultiStage, GraphEncoder
# Archived encoders (kept for historical comparison runs). See approaches/archived/README_*.md.
from approaches.archived.approach_3_contrastive import ContrastiveEncoder
from approaches.archived.approach_3_contrastive_v2 import ContrastiveEncoderV2
from approaches.archived.approach_3_contrastive_v3 import ContrastiveEncoderV3
from approaches.archived.approach_5_llm_struct import LLMStructuredEncoder
from approaches.archived.approach_5_llm_struct_v2 import LLMStructuredEncoderV2
from approaches.archived.approach_5_llm_struct_v3 import LLMStructuredEncoderV3
from evaluation.metrics import (precision_at_k, reaction_similarity_correlation,
                                conditional_retrieval_quality, utility_at_k)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def load_events(dataset_path: str):
    with open(dataset_path) as f:
        events = json.load(f)
    train = [e for e in events if e["split"] == "train"]
    test = [e for e in events if e["split"] == "test"]
    return events, train, test


def infer_level(dataset_path: str) -> str:
    m = re.search(r"_L(\d+)", os.path.basename(dataset_path))
    return f"L{m.group(1)}" if m else "Lx"


def build_encoders():
    return [
        ConcatBaseline(equalize_blocks=False),
        ConcatBaseline(equalize_blocks=True),
        FactorizedMultiStage(),
        ContrastiveEncoder(epochs=80),
        ContrastiveEncoderV2(epochs=80),
        ContrastiveEncoderV3(),
        GraphEncoder(),
        LLMStructuredEncoder(),
        LLMStructuredEncoderV2(),
        LLMStructuredEncoderV3(),
    ]


def evaluate_one(enc, train, test, macro_filter):
    t0 = time.time()
    enc.fit(train)
    fit_time = time.time() - t0

    t0 = time.time()
    p5, _ = precision_at_k(enc, train, test, k=5)
    p10, _ = precision_at_k(enc, train, test, k=10)
    react_corr = reaction_similarity_correlation(enc, test)
    cond = conditional_retrieval_quality(enc, train, test, macro_filter, k=5)
    util5 = utility_at_k(enc, train, test, k=5)
    eval_time = time.time() - t0

    notes = []
    if getattr(enc, "experimental", False):
        notes.append("experimental")
    if getattr(enc, "use_mock", False):
        notes.append("LLM mock fallback")
    if getattr(enc, "fail_count", 0):
        notes.append(f"{enc.fail_count} LLM failures")

    extras = {}
    if hasattr(enc, "cache") and isinstance(enc.cache, dict) and enc.cache:
        from collections import Counter
        first = next(iter(enc.cache.values()))
        for field in first.keys():
            cnt = Counter(o.get(field) for o in enc.cache.values())
            extras[field] = {str(k): v for k, v in cnt.items()}
    return {
        "name": enc.name,
        "precision_at_5": round(p5, 4),
        "precision_at_10": round(p10, 4),
        "reaction_corr": round(react_corr, 4),
        "conditional_quality": round(cond, 4),
        "utility_at_5": round(util5, 4),
        "fit_time_s": round(fit_time, 2),
        "eval_time_s": round(eval_time, 2),
        "wall_time_s": round(fit_time + eval_time, 2),
        "notes": "; ".join(notes) or "-",
        "extras": extras,
    }


def write_markdown_table(rows, path):
    headers = ["Approach", "P@5", "P@10", "ReactCorr", "CondQual", "Util@5",
               "Fit(s)", "Eval(s)", "Wall(s)", "Notes"]
    keys = ["name", "precision_at_5", "precision_at_10", "reaction_corr",
            "conditional_quality", "utility_at_5",
            "fit_time_s", "eval_time_s", "wall_time_s", "notes"]
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(k, "-")) for k in keys) + " |")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def make_plots(rows, encoders, train, test, tag):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = [r["name"] for r in rows]
    p5 = [r["precision_at_5"] for r in rows]
    rcorr = [r["reaction_corr"] for r in rows]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].barh(names, p5, color="steelblue")
    axes[0].set_xlabel("Precision@5")
    axes[0].set_title("Cluster retrieval P@5")
    axes[0].axvline(1/4, color="red", ls="--", lw=1, label="random (4 clusters)")
    axes[0].legend()

    axes[1].barh(names, rcorr, color="darkorange")
    axes[1].set_xlabel("Spearman corr (enc-sim vs reaction-sim)")
    axes[1].set_title("Reaction similarity correlation")
    plt.tight_layout()
    bar_path = os.path.join(RESULTS_DIR, f"bars_{tag}.png")
    plt.savefig(bar_path, dpi=120)
    plt.close()

    # UMAP per encoder on train+test
    import umap
    all_events = train + test
    clusters = [e["ground_truth_cluster"] for e in all_events]
    splits = [e["split"] for e in all_events]
    uniq_c = sorted(set(clusters))
    cmap = plt.get_cmap("tab10")
    color_for = {c: cmap(i) for i, c in enumerate(uniq_c)}

    n = len(encoders)
    cols = 3
    rows_n = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows_n, cols, figsize=(6 * cols, 5 * rows_n))
    axes = np.array(axes).reshape(-1)
    for ax, enc in zip(axes, encoders):
        try:
            Z = enc.encode_batch(all_events)
            reducer = umap.UMAP(n_components=2, random_state=42,
                                n_neighbors=min(15, len(all_events) - 1))
            X2 = reducer.fit_transform(Z)
            for c in uniq_c:
                idx = [i for i, cc in enumerate(clusters) if cc == c]
                ax.scatter(X2[idx, 0], X2[idx, 1], s=18,
                           c=[color_for[c]], label=c, alpha=0.75,
                           edgecolors="black", linewidths=0.3)
            ax.set_title(enc.name)
            ax.legend(loc="best", fontsize=8)
        except Exception as e:
            ax.set_title(f"{enc.name} (UMAP failed: {e})")
    for ax in axes[len(encoders):]:
        ax.axis("off")
    plt.tight_layout()
    umap_path = os.path.join(RESULTS_DIR, f"umap_{tag}.png")
    plt.savefig(umap_path, dpi=110)
    plt.close()

    return bar_path, umap_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=os.path.join(ROOT, "data", "mock_events_L1.json"),
                    help="path to dataset JSON")
    ap.add_argument("--skip", action="append", default=[],
                    help="approach name(s) to skip (repeatable)")
    args = ap.parse_args()

    events, train, test = load_events(args.dataset)
    level = infer_level(args.dataset)
    skip = set(args.skip)
    print(f"[{level}] dataset={args.dataset}")
    print(f"Loaded {len(events)} events ({len(train)} train / {len(test)} test). Skip: {sorted(skip) or 'none'}")

    macro_filter = {"vix": (18.0, 100.0)}

    encoders = [e for e in build_encoders() if e.name not in skip]
    rows = []
    fitted = []
    for enc in encoders:
        print(f"\n=== {enc.name} ===")
        try:
            row = evaluate_one(enc, train, test, macro_filter)
            print(row)
            rows.append(row)
            fitted.append(enc)
        except Exception as e:
            import traceback
            traceback.print_exc()
            rows.append({
                "name": enc.name, "precision_at_5": None, "precision_at_10": None,
                "reaction_corr": None, "conditional_quality": None,
                "fit_time_s": None, "eval_time_s": None, "wall_time_s": None,
                "notes": f"ERROR: {e}",
            })

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    tag = f"{level}_{ts}"
    json_path = os.path.join(RESULTS_DIR, f"run_{tag}.json")
    md_path = os.path.join(RESULTS_DIR, f"run_{tag}.md")
    with open(json_path, "w") as f:
        json.dump({"timestamp": ts, "level": level, "dataset": args.dataset,
                   "macro_filter": macro_filter,
                   "n_train": len(train), "n_test": len(test),
                   "results": rows}, f, indent=2)
    write_markdown_table(rows, md_path)

    bar_path, umap_path = make_plots(rows, fitted, train, test, tag)

    print(f"\nResults JSON: {json_path}")
    print(f"Results MD  : {md_path}")
    print(f"Bars plot   : {bar_path}")
    print(f"UMAP plot   : {umap_path}")

    with open(md_path) as f:
        print("\n" + f.read())


if __name__ == "__main__":
    main()
