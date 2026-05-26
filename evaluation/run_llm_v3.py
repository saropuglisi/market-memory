"""Run only LLMStructuredEncoderV3 on L3, L4, L5. Capture fail count and cycle distribution per dataset."""
from __future__ import annotations
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from approaches import LLMStructuredEncoderV3
from approaches.approach_5_llm_struct_v2 import POLARITY, SURPRISE_MAG, DRIVER, ASYMM, CYCLE
from evaluation.metrics import (precision_at_k, reaction_similarity_correlation,
                                conditional_retrieval_quality, utility_at_k)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT, "results")


def evaluate(dataset_path: str):
    events = json.load(open(dataset_path))
    train = [e for e in events if e["split"] == "train"]
    test = [e for e in events if e["split"] == "test"]

    enc = LLMStructuredEncoderV3()
    fail_before = enc.fail_count

    t0 = time.time()
    enc.fit(train)
    # Encode test to populate cache for any new texts
    enc.encode_batch(test)
    fit_t = time.time() - t0

    t0 = time.time()
    p5, _ = precision_at_k(enc, train, test, k=5)
    p10, _ = precision_at_k(enc, train, test, k=10)
    rc = reaction_similarity_correlation(enc, test)
    util5 = utility_at_k(enc, train, test, k=5)
    cond = conditional_retrieval_quality(enc, train, test, {"vix": (18.0, 100.0)}, k=5)
    eval_t = time.time() - t0

    fail_count = enc.fail_count - fail_before

    # Per-dataset distribution: only events from this dataset's texts
    import hashlib
    keys_this = set(hashlib.md5(e["text"].encode()).hexdigest() for e in events)
    cache_this = {k: v for k, v in enc.cache.items() if k in keys_this}
    n = len(cache_this)

    def dist(field, vocab):
        cnt = Counter(o.get(field) for o in cache_this.values())
        return {v: cnt.get(v, 0) for v in vocab}

    distribution = {
        "event_polarity": dist("event_polarity", POLARITY),
        "surprise_magnitude": dist("surprise_magnitude", SURPRISE_MAG),
        "dominant_driver": dist("dominant_driver", DRIVER),
        "risk_asymmetry": dist("risk_asymmetry", ASYMM),
        "cycle_phase": dist("cycle_phase", CYCLE),
    }
    conf_counter = Counter(int(o["confidence_level"]) for o in cache_this.values())
    distribution["confidence_level"] = {str(i): conf_counter.get(i, 0) for i in range(1, 6)}

    n_calls = len([k for k in cache_this.keys()
                   if k not in {hashlib.md5(e["text"].encode()).hexdigest() for e in [] }])  # placeholder
    n_calls = n  # number of unique texts encoded
    fail_rate = (fail_count / n_calls) if n_calls else 0.0

    return {
        "dataset": dataset_path,
        "n_train": len(train), "n_test": len(test),
        "n_unique_texts": n_calls,
        "precision_at_5": round(p5, 4), "precision_at_10": round(p10, 4),
        "reaction_corr": round(rc, 4), "conditional_quality": round(cond, 4),
        "utility_at_5": round(util5, 4),
        "fit_time_s": round(fit_t, 2), "eval_time_s": round(eval_t, 2),
        "fail_count": fail_count, "fail_rate": round(fail_rate, 4),
        "distribution": distribution,
    }


def main():
    out_path = os.path.join(RESULTS_DIR, f"llm_v3_L3_L4_L5_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    results = {}
    for level in ["L3", "L4", "L5"]:
        path = os.path.join(ROOT, "data", f"mock_events_{level}.json")
        print(f"\n=== {level} on {path} ===")
        r = evaluate(path)
        results[level] = r
        print(f"  P@5={r['precision_at_5']}  ReactCorr={r['reaction_corr']}  Util@5={r['utility_at_5']}")
        print(f"  CondQual={r['conditional_quality']}  fail={r['fail_count']}/{r['n_unique_texts']} ({r['fail_rate']:.1%})")
        if r['fail_rate'] > 0.05:
            print(f"  ⚠️  FAIL RATE > 5% — stopping per user instruction")
            results[level]["aborted"] = True
            break
        cy = r["distribution"]["cycle_phase"]
        total = sum(cy.values())
        print(f"  cycle_phase: " + ", ".join(f"{k}={v} ({v/max(1,total):.0%})" for k, v in cy.items()))

    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nsaved: {out_path}")


if __name__ == "__main__":
    main()
