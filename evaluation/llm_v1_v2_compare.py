"""LLM v1 vs v2 comparison on Level 1.

Reports:
(a) failure counts (LLM call → mock fallback)
(b) per-field value distribution from the cache
(c) P@5, ReactCorr, utility@5 deltas vs backbone (concat_eq)
"""
from __future__ import annotations
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from approaches import (ConcatBaseline, LLMStructuredEncoder, LLMStructuredEncoderV2)
from approaches.approach_5_llm_struct import (NARRATIVES, SURPRISES, ASYMM as ASYMM_V1,
                                              CYCLE as CYCLE_V1)
from approaches.approach_5_llm_struct_v2 import (POLARITY, SURPRISE_MAG, DRIVER,
                                                 ASYMM, CYCLE)
from evaluation.metrics import (precision_at_k, reaction_similarity_correlation,
                                utility_at_k)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "mock_events.json")
RESULTS_DIR = os.path.join(ROOT, "results")


V1_VOCABS = {"dominant_narrative": NARRATIVES, "surprise_type": SURPRISES,
             "risk_asymmetry": ASYMM_V1, "implicit_cycle_phase": CYCLE_V1}
V2_VOCABS = {"event_polarity": POLARITY, "surprise_magnitude": SURPRISE_MAG,
             "dominant_driver": DRIVER, "risk_asymmetry": ASYMM,
             "cycle_phase": CYCLE}


def distribution(cache: dict, vocabs: dict):
    out = {}
    n = len(cache)
    for field, vocab in vocabs.items():
        cnt = Counter(o.get(field) for o in cache.values())
        out[field] = {v: cnt.get(v, 0) for v in vocab}
        oov = sum(v for k, v in cnt.items() if k not in vocab)
        if oov:
            out[field]["__oov__"] = oov
        # confidence handled separately below
    if "confidence_level" in next(iter(cache.values()), {}):
        conf = Counter(int(o["confidence_level"]) for o in cache.values())
        out["confidence_level"] = {i: conf.get(i, 0) for i in range(1, 6)}
    return out, n


def evaluate(enc, train, test):
    t0 = time.time()
    enc.fit(train)
    fit_t = time.time() - t0
    t0 = time.time()
    p5, _ = precision_at_k(enc, train, test, k=5)
    react = reaction_similarity_correlation(enc, test)
    util5 = utility_at_k(enc, train, test, k=5)
    eval_t = time.time() - t0
    return {"name": enc.name, "P@5": round(p5, 4), "ReactCorr": round(react, 4),
            "Utility@5": round(util5, 4), "fit_s": round(fit_t, 1),
            "eval_s": round(eval_t, 1), "fail_count": getattr(enc, "fail_count", 0),
            "use_mock": getattr(enc, "use_mock", False)}


def main():
    events = json.load(open(DATA))
    train = [e for e in events if e["split"] == "train"]
    test = [e for e in events if e["split"] == "test"]

    backbone = ConcatBaseline(equalize_blocks=True)
    v1 = LLMStructuredEncoder()
    v2 = LLMStructuredEncoderV2()

    r_back = evaluate(backbone, train, test)
    r_v1 = evaluate(v1, train, test)
    r_v2 = evaluate(v2, train, test)

    dist_v1, n_v1 = distribution(v1.cache, V1_VOCABS)
    dist_v2, n_v2 = distribution(v2.cache, V2_VOCABS)

    print("\n=== METRICS on Level 1 ===")
    keys = ["name", "P@5", "ReactCorr", "Utility@5", "fail_count", "fit_s", "eval_s"]
    print(" | ".join(f"{k:>14}" for k in keys))
    for r in [r_back, r_v1, r_v2]:
        print(" | ".join(f"{str(r[k]):>14}" for k in keys))

    def print_dist(label, dist, n):
        print(f"\n--- {label} (n={n}) ---")
        for field, counts in dist.items():
            total = sum(counts.values())
            parts = [f"{v}={c} ({c/max(1,total):.0%})" for v, c in counts.items() if c > 0]
            print(f"  {field}: {', '.join(parts) or '(empty)'}")

    print_dist("v1 cache distribution", dist_v1, n_v1)
    print_dist("v2 cache distribution", dist_v2, n_v2)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = {
        "timestamp": ts,
        "metrics": [r_back, r_v1, r_v2],
        "v1_distribution": dist_v1,
        "v2_distribution": dist_v2,
    }
    out_path = os.path.join(RESULTS_DIR, f"llm_v1_v2_compare_{ts}.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=int)
    print(f"\nsaved: {out_path}")


if __name__ == "__main__":
    main()
