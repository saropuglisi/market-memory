"""Sanity-check narrative tags after extraction.

Reads  real_data/processed/sample_500_narrative_tags.json
Writes real_data/processed/narrative_tags_validation.md
       (also printed to stdout)

Checks:
- frequency of each tag (% of events with tag=1)
- pairwise correlation matrix (12×12)
- contradiction count for each mutually-exclusive pair
- distribution of active tags per event
- coverage status counts (ok / partial / parsing_failed / no_summary)

If suspicious (freq 0% or 95%, freq>20% contradictions, mean active >7),
prints a "REVIEW NEEDED" header at top.
"""
from __future__ import annotations
import json
import os
import sys
from collections import Counter

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from real_data.narrative_tags import TAG_KEYS, MUTUALLY_EXCLUSIVE_PAIRS

PROCESSED = os.path.join(ROOT, "real_data", "processed")
TAGS_PATH = os.path.join(PROCESSED, "sample_500_narrative_tags.json")
OUT_PATH  = os.path.join(PROCESSED, "narrative_tags_validation.md")


def main():
    if not os.path.exists(TAGS_PATH):
        print(f"Missing {TAGS_PATH}")
        sys.exit(1)
    with open(TAGS_PATH) as f:
        raw = json.load(f)
    n = len(raw)
    if n == 0:
        print("Empty tags file")
        sys.exit(1)

    # Build matrix M (n × 12)
    M = np.array([[d.get(k, 0) for k in TAG_KEYS] for d in raw.values()],
                 dtype=np.int8)
    status = Counter(d.get("_status", "unknown") for d in raw.values())

    # Frequencies
    freq = M.mean(axis=0)
    # Active tags per event
    per_event = M.sum(axis=1)

    # Pairwise correlation (Pearson on binary -> phi coefficient)
    Mc = M - M.mean(axis=0)
    denom = np.sqrt((Mc**2).sum(axis=0))[:, None] @ np.sqrt((Mc**2).sum(axis=0))[None, :]
    corr = np.where(denom > 0, (Mc.T @ Mc) / denom, 0.0)

    # Mutually-exclusive contradictions
    contradictions = []
    for a, b in MUTUALLY_EXCLUSIVE_PAIRS:
        ia, ib = TAG_KEYS.index(a), TAG_KEYS.index(b)
        c = int(((M[:, ia] == 1) & (M[:, ib] == 1)).sum())
        contradictions.append((a, b, c, c / n))

    # Warnings
    warns = []
    for k, f in zip(TAG_KEYS, freq):
        if f == 0.0:
            warns.append(f"tag `{k}` never seen (freq 0%) — useless")
        elif f >= 0.95:
            warns.append(f"tag `{k}` near-ubiquitous (freq {f*100:.1f}%) — useless")
    for a, b, c, frac in contradictions:
        if frac >= 0.10:
            warns.append(f"contradiction {a}+{b} = {c} events ({frac*100:.1f}%) — high")
    mean_active = float(per_event.mean())
    if mean_active < 1.0:
        warns.append(f"avg active tags per event = {mean_active:.2f} — under-extracted")
    if mean_active > 7.0:
        warns.append(f"avg active tags per event = {mean_active:.2f} — over-extracted")

    # Build report
    lines = ["# Narrative tags — validation report", ""]
    if warns:
        lines.append("## ⚠️  REVIEW NEEDED")
        lines.append("")
        for w in warns:
            lines.append(f"- {w}")
        lines.append("")
    else:
        lines.append("✓ no critical issues flagged.")
        lines.append("")

    lines.append(f"events: {n}  |  status: {dict(status)}")
    lines.append("")
    lines.append("## Tag frequency")
    lines.append("")
    lines.append("| tag | freq | count |")
    lines.append("|---|---|---|")
    for k, f in sorted(zip(TAG_KEYS, freq), key=lambda x: -x[1]):
        lines.append(f"| {k} | {f*100:5.1f}% | {int(f*n)} |")
    lines.append("")

    lines.append("## Active tags per event")
    lines.append("")
    lines.append(f"- mean={per_event.mean():.2f}  median={int(np.median(per_event))}  "
                 f"min={int(per_event.min())}  max={int(per_event.max())}")
    hist = Counter(int(x) for x in per_event)
    lines.append("- distribution: " + "  ".join(f"{k}→{hist[k]}" for k in sorted(hist)))
    lines.append("")

    lines.append("## Mutually-exclusive contradictions")
    lines.append("")
    lines.append("| pair | count | % |")
    lines.append("|---|---|---|")
    for a, b, c, frac in contradictions:
        lines.append(f"| {a} + {b} | {c} | {frac*100:.1f}% |")
    lines.append("")

    lines.append("## Pairwise correlation (φ)")
    lines.append("")
    header = "| | " + " | ".join(TAG_KEYS) + " |"
    sep    = "|---|" + "---|" * len(TAG_KEYS)
    lines.append(header); lines.append(sep)
    for i, k in enumerate(TAG_KEYS):
        row = " | ".join(f"{corr[i,j]:+.2f}" for j in range(len(TAG_KEYS)))
        lines.append(f"| **{k}** | {row} |")
    lines.append("")

    report = "\n".join(lines)
    with open(OUT_PATH, "w") as f:
        f.write(report)
    print(report)
    print(f"\nsaved {OUT_PATH}")
    if warns:
        print("\n!!! warnings present — review before proceeding")
        sys.exit(2)


if __name__ == "__main__":
    main()
