"""Adapter: gira concat_eq, contrastive_v2, llm_v3 sul dataset reale.

Carica sample_50.json, splitta 70/30 con seed=42, fit + evaluate + dump.
"""
from __future__ import annotations
import json
import os
import sys
import time
import random
from datetime import datetime
from collections import Counter

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from approaches import ConcatBaseline
# Archived encoders (kept for historical comparison runs). See approaches/archived/README_*.md.
from approaches.archived.approach_3_contrastive_v2 import ContrastiveEncoderV2
from approaches.archived.approach_5_llm_struct_v3 import LLMStructuredEncoderV3
from real_data.metrics_real import (self_consistency_at_k, reaction_corr_real,
                                     utility_at_k_real, conditional_quality_real,
                                     temporal_diversity)

REAL_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(REAL_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


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


def evaluate(enc, train, test):
    t0 = time.time()
    enc.fit(train)
    fit_t = time.time() - t0
    t0 = time.time()
    sc = self_consistency_at_k(enc, train, test, k=5)
    rc = reaction_corr_real(enc, test)
    util = utility_at_k_real(enc, train, test, k=5)
    cond = conditional_quality_real(enc, train, test, {"vix": (18.0, 100.0)}, k=5)
    td = temporal_diversity(enc, train, test, k=5)
    eval_t = time.time() - t0
    return {
        "name": enc.name,
        "self_consistency": round(sc["self_consistency"], 4),
        "random_baseline": round(sc["random_baseline"], 4),
        "sc_lift": round(sc["lift"], 4),
        "reaction_corr": round(rc, 4),
        "utility_at_5": round(util, 4),
        "conditional_quality": round(cond, 4),
        "temporal_diversity_days": round(td, 1),
        "fit_s": round(fit_t, 1),
        "eval_s": round(eval_t, 1),
        "fail_count": getattr(enc, "fail_count", 0),
    }


def retrievals(encoders, train, test, k=5):
    out = {}
    for q in test:
        per_enc = {}
        for name, enc in encoders.items():
            idx = enc.retrieve(q, train, top_k=k)
            per_enc[name] = [{"id": train[i]["id"], "ticker": train[i]["ticker"],
                              "sector": train[i]["sector"], "date": train[i]["date"]}
                             for i in idx]
        out[q["id"]] = {"query": {"id": q["id"], "ticker": q["ticker"],
                                  "sector": q["sector"], "date": q["date"]},
                        "top5": per_enc}
    return out


def main():
    dataset = os.environ.get("DATASET", "sample_50.json")
    tag = os.environ.get("RUN_TAG", "real")
    with open(os.path.join(REAL_DIR, "processed", dataset)) as f:
        events = json.load(f)
    print(f"loaded {len(events)} events from {dataset}")

    train, test = stratified_split(events, train_frac=0.7, seed=42)
    print(f"split: {len(train)} train / {len(test)} test")
    sec_train = Counter(e["sector"] for e in train)
    sec_test = Counter(e["sector"] for e in test)
    print(f"  train sectors: {dict(sec_train)}")
    print(f"  test sectors:  {dict(sec_test)}")

    encoders = {
        "concat_eq": ConcatBaseline(equalize_blocks=True),
        "contrastive_v2": ContrastiveEncoderV2(epochs=80),
        "llm_v3": LLMStructuredEncoderV3(),
    }
    rows = []
    fitted = {}
    for name, enc in encoders.items():
        print(f"\n=== {name} ===")
        r = evaluate(enc, train, test)
        rows.append(r)
        fitted[name] = enc
        print(r)

    retr = retrievals(fitted, train, test, k=5)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = {
        "timestamp": ts,
        "n_train": len(train), "n_test": len(test),
        "results": rows,
        "retrievals": retr,
    }
    out_path = os.path.join(RESULTS_DIR, f"run_{tag}_{ts}.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nsaved {out_path}")
    # markdown table
    md = ["| Approach | SelfCons | Rand | Lift | ReactCorr | Util@5 | CondQual | TempDiv(d) | Fit(s) | Eval(s) | Fail |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['name']} | {r['self_consistency']} | {r['random_baseline']} | {r['sc_lift']} | "
                  f"{r['reaction_corr']} | {r['utility_at_5']} | {r['conditional_quality']} | "
                  f"{r['temporal_diversity_days']} | {r['fit_s']} | {r['eval_s']} | {r['fail_count']} |")
    with open(os.path.join(RESULTS_DIR, f"run_{tag}_{ts}.md"), "w") as f:
        f.write("\n".join(md))
    print("\n" + "\n".join(md))


if __name__ == "__main__":
    main()
