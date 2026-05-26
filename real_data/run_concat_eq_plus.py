"""Run concat_eq+ vs concat_eq on sample_500.

- Loads sample_500.json + narrative_tags JSON
- 70/30 stratified split (seed=42), same as previous runs
- Fits both encoders, evaluates with the full statistical metric suite
- Saves run_500_concat_eq_plus_<ts>.json + markdown table

Usage:
  python -m real_data.run_concat_eq_plus
"""
from __future__ import annotations
import json
import os
import sys
import time
import random
from collections import Counter
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from approaches.approach_1_concat import ConcatBaseline
from approaches.approach_2b_concat_eq_plus import ConcatEqPlus
from real_data.metrics_real import (
    self_consistency_at_k, reaction_corr_real,
    utility_at_k_real, utility_at_k_real_threshold,
    random_baseline_utility,
    conditional_quality_real, temporal_diversity,
)

REAL = os.path.dirname(os.path.abspath(__file__))
PROCESSED = os.path.join(REAL, "processed")
RESULTS = os.path.join(REAL, "results")
os.makedirs(RESULTS, exist_ok=True)


def stratified_split(events, train_frac=0.7, seed=42):
    rng = random.Random(seed)
    by_sec = {}
    for e in events:
        by_sec.setdefault(e["sector"], []).append(e)
    train, test = [], []
    for evs in by_sec.values():
        rng.shuffle(evs)
        cut = int(len(evs) * train_frac)
        train.extend(evs[:cut])
        test.extend(evs[cut:])
    rng.shuffle(train); rng.shuffle(test)
    return train, test


def evaluate(enc, train, test):
    t0 = time.time(); enc.fit(train); fit_t = time.time() - t0
    t0 = time.time()
    sc = self_consistency_at_k(enc, train, test, k=5)
    rc = reaction_corr_real(enc, test)
    util_spearman = utility_at_k_real(enc, train, test, k=5)
    cond = conditional_quality_real(enc, train, test, {"vix": (18.0, 100.0)}, k=5)
    td = temporal_diversity(enc, train, test, k=5)
    # Build retrievals → util threshold P25/P50 + retrievals dump
    retr = {}
    for q in test:
        idx = enc.retrieve(q, train, top_k=5)
        retr[q["id"]] = [train[i]["id"] for i in idx]
    u25 = utility_at_k_real_threshold(train, test, retr, percentile=0.25)
    u50 = utility_at_k_real_threshold(train, test, retr, percentile=0.50)
    eval_t = time.time() - t0
    return {
        "name": enc.name,
        "self_consistency": round(sc["self_consistency"], 4),
        "random_baseline": round(sc["random_baseline"], 4),
        "sc_lift": round(sc["lift"], 4),
        "reaction_corr": round(rc, 4),
        "utility_spearman_top5": round(util_spearman, 4),
        "util_p25": round(u25, 4),
        "util_p50": round(u50, 4),
        "conditional_quality": round(cond, 4),
        "temporal_diversity_days": round(td, 1),
        "fit_s": round(fit_t, 1),
        "eval_s": round(eval_t, 1),
        "retrievals": retr,
    }


def main():
    with open(os.path.join(PROCESSED, "sample_500.json")) as f:
        events = json.load(f)
    print(f"loaded {len(events)} events")
    train, test = stratified_split(events, 0.7, seed=42)
    print(f"split: {len(train)} train / {len(test)} test")
    print(f"  train sectors: {dict(Counter(e['sector'] for e in train))}")

    encoders = {
        "concat_eq":      ConcatBaseline(equalize_blocks=True),
        "concat_eq_plus": ConcatEqPlus(),
    }
    results = {}
    for name, enc in encoders.items():
        print(f"\n=== {name} ===")
        r = evaluate(enc, train, test)
        results[name] = r
        cells = {k: r[k] for k in r if k != "retrievals"}
        for k, v in cells.items():
            print(f"  {k:<28} {v}")

    # Random baseline utility (cached compute, share for both)
    rand_u25 = random_baseline_utility(train, test, k=5, percentile=0.25, n_random=200, seed=42)
    rand_u50 = random_baseline_utility(train, test, k=5, percentile=0.50, n_random=200, seed=42)

    # ── comparison table ──────────────────────────────────────────────
    base = results["concat_eq"]; plus = results["concat_eq_plus"]
    cmp_rows = [
        ("ReactCorr",                  base["reaction_corr"], plus["reaction_corr"]),
        ("Util@5 P25",                 base["util_p25"],      plus["util_p25"]),
        ("Util@5 P50",                 base["util_p50"],      plus["util_p50"]),
        ("Util Spearman top5",         base["utility_spearman_top5"], plus["utility_spearman_top5"]),
        ("SelfCons",                   base["self_consistency"], plus["self_consistency"]),
        ("SelfCons Lift vs Random",    base["sc_lift"],       plus["sc_lift"]),
        ("CondQual (VIX>18)",          base["conditional_quality"], plus["conditional_quality"]),
        ("TempDiv (days)",             base["temporal_diversity_days"], plus["temporal_diversity_days"]),
    ]
    print(f"\n{'Metric':<28} | {'concat_eq':>10} | {'concat_eq+':>10} |    Δ")
    print("-" * 70)
    for name, b, p in cmp_rows:
        delta = p - b
        sign = "+" if delta >= 0 else ""
        print(f"{name:<28} | {b:>10.4f} | {p:>10.4f} | {sign}{delta:.4f}")
    print(f"\n(random baseline) Util@5 P25={rand_u25:.4f}  P50={rand_u50:.4f}")

    # ── save ──────────────────────────────────────────────────────────
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = {
        "timestamp": ts,
        "n_train": len(train), "n_test": len(test),
        "random_baseline_util_p25": rand_u25,
        "random_baseline_util_p50": rand_u50,
        "results": {
            "concat_eq":      {k: v for k, v in base.items() if k != "retrievals"},
            "concat_eq_plus": {k: v for k, v in plus.items() if k != "retrievals"},
        },
        "retrievals": {
            "concat_eq":      base["retrievals"],
            "concat_eq_plus": plus["retrievals"],
        },
    }
    json_path = os.path.join(RESULTS, f"run_500_concat_eq_plus_{ts}.json")
    md_path   = os.path.join(RESULTS, f"run_500_concat_eq_plus_{ts}.md")
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2)

    md = ["# concat_eq+ vs concat_eq — sample_500", "",
          f"N train={len(train)}  N test={len(test)}  ts={ts}",
          "",
          f"| Metric | concat_eq | concat_eq+ | Δ |",
          "|---|---|---|---|"]
    for name, b, p in cmp_rows:
        delta = p - b
        sign = "+" if delta >= 0 else ""
        md.append(f"| {name} | {b:.4f} | {p:.4f} | {sign}{delta:.4f} |")
    md.append("")
    md.append(f"_random baseline Util@5 P25={rand_u25:.4f}  P50={rand_u50:.4f}_")
    with open(md_path, "w") as f:
        f.write("\n".join(md))
    print(f"\nsaved {json_path}")
    print(f"saved {md_path}")


if __name__ == "__main__":
    main()
