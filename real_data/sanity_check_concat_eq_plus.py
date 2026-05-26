"""Eyeball top-3 retrievals: concat_eq vs concat_eq+ on 5 sample queries.

Reads the most recent run_500_concat_eq_plus_*.json and prints side-by-side
comparison + delta counts. Useful to spot bugs (100% identical = something
is wrong; 100% different = also suspicious).
"""
from __future__ import annotations
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

REAL = os.path.dirname(os.path.abspath(__file__))
PROCESSED = os.path.join(REAL, "processed")
RESULTS = os.path.join(REAL, "results")


def latest():
    cands = sorted(glob.glob(os.path.join(RESULTS, "run_500_concat_eq_plus_*.json")))
    if not cands:
        print("No run_500_concat_eq_plus_*.json found. Run run_concat_eq_plus.py first.")
        sys.exit(1)
    return cands[-1]


def main():
    path = latest()
    with open(path) as f:
        run = json.load(f)
    with open(os.path.join(PROCESSED, "sample_500.json")) as f:
        events = json.load(f)
    idx = {e["id"]: e for e in events}

    ce  = run["retrievals"]["concat_eq"]
    cep = run["retrievals"]["concat_eq_plus"]

    # Pick 5 sample queries (deterministic)
    qids = list(ce.keys())[:5]
    print(f"loaded {os.path.basename(path)}  ({len(ce)} queries)\n")

    total_same = total = 0
    overlap_dist = []
    for qid in ce.keys():
        a = set(ce[qid][:3]); b = set(cep[qid][:3])
        overlap_dist.append(len(a & b))
        total_same += len(a & b); total += 3
    print(f"Overall top-3 overlap: mean={sum(overlap_dist)/len(overlap_dist):.2f}/3"
          f"  ({100*total_same/total:.1f}% identical positions)")
    from collections import Counter
    print(f"Per-query overlap distribution (count of shared top-3): {dict(Counter(overlap_dist))}\n")

    for qid in qids:
        q = idx[qid]
        print(f"━━━━━ {q['ticker']} {q['date']}  ({q['sector']}) ━━━━━")
        print(f"  ID {qid}")
        a3 = ce[qid][:3]
        b3 = cep[qid][:3]
        print(f"  concat_eq  top-3:")
        for tid in a3:
            e = idx[tid]
            mark = "★" if tid in b3 else " "
            print(f"    {mark} {e['ticker']:<6} {e['date']} ({e['sector']:<22}) {tid}")
        print(f"  concat_eq+ top-3:")
        for tid in b3:
            e = idx[tid]
            mark = "★" if tid in a3 else " "
            print(f"    {mark} {e['ticker']:<6} {e['date']} ({e['sector']:<22}) {tid}")
        new = [t for t in b3 if t not in a3]
        kept = [t for t in b3 if t in a3]
        print(f"  → kept {len(kept)}/3, swapped in {len(new)}\n")


if __name__ == "__main__":
    main()
