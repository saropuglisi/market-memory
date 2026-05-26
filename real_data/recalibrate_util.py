"""Recalibrate Util@K threshold (P25 vs P50) on existing run_500 results.

No re-encoding — uses pre-computed retrievals + reaction vectors from
sample_500.json. Loads first available run_500_*.json, computes both P25 and
P50 versions of utility@5 (real-data, no cluster), plus random baselines.
Saves to run_500_recalibrated_<timestamp>.json.
"""
from __future__ import annotations
import glob
import json
import os
import random
import sys
from datetime import datetime
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from real_data.metrics_real import utility_at_k_real_threshold, random_baseline_utility

REAL_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(REAL_DIR, "results")
SEED = 42


def stratified_split(events, train_frac=0.7, seed=42):
    rng = random.Random(seed)
    by_sector = {}
    for e in events:
        by_sector.setdefault(e["sector"], []).append(e)
    train, test = [], []
    for sector, evs in by_sector.items():
        rng.shuffle(evs)
        cut = int(len(evs) * train_frac)
        train.extend(evs[:cut])
        test.extend(evs[cut:])
    rng.shuffle(train); rng.shuffle(test)
    return train, test


def main():
    # Locate latest run_500_*.json (exclude already recalibrated)
    cands = sorted(glob.glob(os.path.join(RESULTS_DIR, "run_500_*.json")))
    cands = [c for c in cands if "recalibrated" not in c]
    if not cands:
        print("No run_500_*.json found.")
        sys.exit(1)
    run_path = cands[-1]
    print(f"loading {run_path}")
    with open(run_path) as f:
        run = json.load(f)

    with open(os.path.join(REAL_DIR, "processed", "sample_500.json")) as f:
        events = json.load(f)

    # Reproduce the same split used in the original run.
    train, test = stratified_split(events, train_frac=0.7, seed=SEED)
    assert len(train) == run["n_train"] and len(test) == run["n_test"], \
        f"split mismatch: {len(train)}/{len(test)} vs {run['n_train']}/{run['n_test']}"

    # Build per-encoder retrievals dict {query_id: [retrieved_train_id, ...]}.
    encoders = ["concat_eq", "contrastive_v2", "llm_v3"]
    retr_by_enc = {enc: {} for enc in encoders}
    for qid, info in run["retrievals"].items():
        for enc, top in info["top5"].items():
            retr_by_enc[enc][qid] = [t["id"] for t in top]

    # Compute random baseline once per percentile (identical for all encoders).
    rand_p25 = random_baseline_utility(train, test, k=5, percentile=0.25, seed=SEED)
    rand_p50 = random_baseline_utility(train, test, k=5, percentile=0.50, seed=SEED)
    print(f"random baseline util@5 — P25={rand_p25:.4f}  P50={rand_p50:.4f}")

    # Recompute per encoder.
    rows = []
    for enc in encoders:
        retr = retr_by_enc[enc]
        u_p25 = utility_at_k_real_threshold(train, test, retr, percentile=0.25)
        u_p50 = utility_at_k_real_threshold(train, test, retr, percentile=0.50)
        rows.append({
            "encoder": enc,
            "util_at_5_p25": round(u_p25, 4),
            "util_at_5_p25_lift": round(u_p25 - rand_p25, 4),
            "util_at_5_p50": round(u_p50, 4),
            "util_at_5_p50_lift": round(u_p50 - rand_p50, 4),
        })
        print(f"  {enc:18s}  P25={u_p25:.4f} (lift {u_p25-rand_p25:+.4f})  "
              f"P50={u_p50:.4f} (lift {u_p50-rand_p50:+.4f})")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = {
        "source_run": os.path.basename(run_path),
        "n_train": len(train),
        "n_test": len(test),
        "k": 5,
        "random_baseline_p25": round(rand_p25, 4),
        "random_baseline_p50": round(rand_p50, 4),
        "results": rows,
    }
    out_path = os.path.join(RESULTS_DIR, f"run_500_recalibrated_{ts}.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nsaved {out_path}")

    # Markdown table
    md = ["# Util@K recalibration — N=500\n",
          f"Source: `{os.path.basename(run_path)}`\n",
          f"Random baseline util@5 (no encoder, K=5 uniform draws): P25={rand_p25:.4f}, P50={rand_p50:.4f}\n",
          "| Encoder | Util@5 P25 | Lift vs random | Util@5 P50 (old) | Lift vs random |",
          "|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['encoder']} | {r['util_at_5_p25']} | {r['util_at_5_p25_lift']:+.4f} | "
                  f"{r['util_at_5_p50']} | {r['util_at_5_p50_lift']:+.4f} |")
    md_path = out_path.replace(".json", ".md")
    with open(md_path, "w") as f:
        f.write("\n".join(md))
    print(f"saved {md_path}")
    print("\n" + "\n".join(md))


if __name__ == "__main__":
    main()
