"""Blind A/B test generator for concat_eq vs contrastive_v2.

Selects 15 test queries stratified by macro-sector (10 single-sector + 5 mix),
fetches top-3 analogs from each encoder, deduplicates overlaps (noting "picked
by both"), shuffles labels A-F with a fixed seed, and emits two files:

  blind_test_<ts>.md       — for human evaluation (no encoder names)
  blind_test_<ts>_KEY.md   — id -> encoder mapping (DO NOT open before eval)

Usage:
  python -m evaluation.qualitative.blind_ab_test
"""
from __future__ import annotations
import glob
import json
import os
import random
import string
import sys
from datetime import datetime
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

REAL_DIR = os.path.join(ROOT, "real_data")
RESULTS_DIR = os.path.join(REAL_DIR, "results")
PROCESSED = os.path.join(REAL_DIR, "processed")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

SEED = 42
TOP_K_PER_ENCODER = 3

# Map GICS sectors → macro buckets for stratification.
MACRO_BUCKET = {
    "Information Technology": "Tech",
    "Communication Services": "Tech",
    "Health Care": "Healthcare",
    "Financials": "Financial",
    "Real Estate": "Financial",
    "Energy": "Energy",
    "Utilities": "Energy",
    "Materials": "Energy",
    "Consumer Discretionary": "Consumer",
    "Consumer Staples": "Consumer",
    "Industrials": "Mix",
}
SINGLE_SECTOR_BUCKETS = ["Tech", "Healthcare", "Financial", "Energy", "Consumer"]
# 2 queries per single-sector bucket + 5 mix = 15 total.
N_PER_BUCKET = 2
N_MIX = 5


def stratified_split(events, train_frac=0.7, seed=42):
    rng = random.Random(seed)
    by_sector = {}
    for e in events:
        by_sector.setdefault(e["sector"], []).append(e)
    train, test = [], []
    for evs in by_sector.values():
        rng.shuffle(evs)
        cut = int(len(evs) * train_frac)
        train.extend(evs[:cut])
        test.extend(evs[cut:])
    rng.shuffle(train); rng.shuffle(test)
    return train, test


def pick_queries(test_events, rng):
    by_bucket = defaultdict(list)
    for e in test_events:
        by_bucket[MACRO_BUCKET.get(e["sector"], "Mix")].append(e)
    chosen = []
    for b in SINGLE_SECTOR_BUCKETS:
        pool = by_bucket.get(b, [])
        rng.shuffle(pool)
        chosen.extend(pool[:N_PER_BUCKET])
    mix_pool = by_bucket.get("Mix", []).copy()
    rng.shuffle(mix_pool)
    chosen.extend(mix_pool[:N_MIX])
    return chosen


def latest_run_500():
    cands = sorted(glob.glob(os.path.join(RESULTS_DIR, "run_500_*.json")))
    cands = [c for c in cands if "recalibrated" not in c]
    if not cands:
        raise SystemExit("No run_500_*.json found.")
    return cands[-1]


def fmt_reaction(r):
    return f"ret={r['return']:+.3f} / vol={r['realized_vol']:.2f} / dd={r['max_drawdown']:.2f} / pers={r['persistence']:.2f}"


def fmt_macro(m):
    return f"VIX={m['vix']:.1f}, yield_10y={m['yield_10y']:.2f}, slope={m['yield_curve_slope']:+.2f}, credit={m['credit_spread']:.2f}"


SCALE_HEADER = """\
# Blind A/B Evaluation — concat_eq vs contrastive_v2

**DO NOT** open `blind_test_*_KEY.md` until ALL valuations below are completed.

## Valuation scales (1–5)

- **Utility** — usefulness to an analyst thinking about the query.
  1=irrelevant, 3=plausible but generic, 5=specific, actionable insight.
- **Insight non-banale** — how non-obvious is the analog?
  1=trivial (same ticker prev quarter), 3=reasonable but easy, 5=cross-ticker /
  cross-time and not obvious.
- **Transferability** — are the reaction patterns observed in the analog
  actually transferable to the query?
  1=context too different, 5=high transferability.

After completing this file, run:

```
python -m evaluation.qualitative.analyze_blind_results <this-file> <KEY-file>
```

---
"""


def render_blind(queries, retr_by_enc, train_index, rng):
    lines = [SCALE_HEADER]
    key_lines = ["# Blind A/B test — KEY (id → encoder)\n\nDo not consult before evaluation.\n"]
    for qi, q in enumerate(queries, start=1):
        # Gather candidates: top-3 each encoder, with provenance.
        # Track multi-encoder picks for dedup.
        prov = defaultdict(list)  # train_id -> [encoder_name, ...]
        rank_in_enc = {}          # (encoder, train_id) -> rank (1-based)
        for enc in ("concat_eq", "contrastive_v2"):
            ids = retr_by_enc[enc].get(q["id"], [])[:TOP_K_PER_ENCODER]
            for rank, tid in enumerate(ids, start=1):
                prov[tid].append(enc)
                rank_in_enc[(enc, tid)] = rank
        unique_ids = list(prov.keys())
        rng.shuffle(unique_ids)
        # Assign labels A, B, C, ...
        labels = list(string.ascii_uppercase)[:len(unique_ids)]

        # Render query block
        bucket = MACRO_BUCKET.get(q["sector"], "Mix")
        snippet = (q.get("text") or "").replace("\n", " ")[:500]
        lines.append(f"\n## Query #{qi}: {q['ticker']} {q['date']} — {q['sector']} ({bucket})\n")
        lines.append(f"**Text (first 500 chars):**\n> {snippet}\n")
        lines.append(f"**Macro context**: {fmt_macro(q['macro_features'])}\n")
        lines.append(f"**Reaction observed (30d)**: {fmt_reaction(q['reaction_30d'])}\n")
        lines.append(f"\n### Candidate analogs (randomized order; {len(unique_ids)} unique):\n")
        lines.append("| ID | Ticker | Date | Sector | Reaction (ret/vol/dd) | Text snippet |")
        lines.append("|----|--------|------|--------|----------------------|--------------|")
        for lbl, tid in zip(labels, unique_ids):
            e = train_index[tid]
            r = e["reaction_30d"]
            txt = (e.get("text") or "").replace("\n", " ").replace("|", "/")[:300]
            lines.append(f"| {lbl} | {e['ticker']} | {e['date']} | {e['sector']} | "
                         f"{r['return']:+.3f} / {r['realized_vol']:.2f} / {r['max_drawdown']:.2f} | {txt} |")
        lines.append("\n### Evaluation (fill in by hand):\n")
        lines.append("| ID | Utility (1-5) | Insight non-banale (1-5) | Transferability (1-5) | Notes |")
        lines.append("|----|---------------|--------------------------|----------------------|-------|")
        for lbl in labels:
            lines.append(f"| {lbl} |               |                          |                      |       |")

        # KEY content
        key_lines.append(f"\n## Query #{qi}: {q['ticker']} {q['date']} ({bucket})\n")
        key_lines.append("| ID | Train event | Encoder(s) | Rank(s) |")
        key_lines.append("|----|-------------|------------|---------|")
        for lbl, tid in zip(labels, unique_ids):
            e = train_index[tid]
            encs = prov[tid]
            tag = " + ".join(encs) if len(encs) > 1 else encs[0]
            ranks = ", ".join(f"{en}#{rank_in_enc[(en,tid)]}" for en in encs)
            picked_both = " (picked by both)" if len(encs) > 1 else ""
            key_lines.append(f"| {lbl} | {e['ticker']} {e['date']} | {tag}{picked_both} | {ranks} |")

    return "\n".join(lines), "\n".join(key_lines)


def main():
    run_path = latest_run_500()
    print(f"using {os.path.basename(run_path)}")
    with open(run_path) as f:
        run = json.load(f)
    with open(os.path.join(PROCESSED, "sample_500.json")) as f:
        events = json.load(f)
    train, test = stratified_split(events, train_frac=0.7, seed=SEED)
    train_index = {e["id"]: e for e in train}

    # Reorganize retrievals.
    retr_by_enc = {"concat_eq": {}, "contrastive_v2": {}}
    for qid, info in run["retrievals"].items():
        for enc, top in info["top5"].items():
            if enc in retr_by_enc:
                retr_by_enc[enc][qid] = [t["id"] for t in top]

    rng = random.Random(SEED + 1)  # different seed from split
    queries = pick_queries(test, rng)
    # Use a *separate* rng for label-shuffling so query order doesn't affect it.
    label_rng = random.Random(SEED + 2)
    blind_md, key_md = render_blind(queries, retr_by_enc, train_index, label_rng)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    blind_path = os.path.join(OUT_DIR, f"blind_test_{ts}.md")
    key_path = os.path.join(OUT_DIR, f"blind_test_{ts}_KEY.md")
    with open(blind_path, "w") as f:
        f.write(blind_md)
    with open(key_path, "w") as f:
        f.write(key_md)
    print(f"\n  EVAL FILE:  {blind_path}")
    print(f"  KEY FILE:   {key_path}")
    print(f"\n  {len(queries)} queries, ~{TOP_K_PER_ENCODER*2} analogs each (deduped).")
    print(f"\n  >>> Open the EVAL FILE to evaluate. DO NOT open the KEY file until evaluation is complete. <<<")


if __name__ == "__main__":
    main()
