"""Blind test v2 generator with 3-way structure:

  Group X : contrastive_v2 top-3
  Group Y : concat_eq      top-3
  Group Z : 3 random train events (no temporal filter)

The X/Y/Z labels themselves are *also* permuted per-query (mapping written
to KEY), so the human evaluator cannot memorize "X = contrastive" across
queries.

Adds for each candidate:
  - narrative_summary (from real_data/processed/sample_500_summaries.json)
  - text_full         (cleaned full text)
  - price series 0-90d post-event

Output: directly produces the *_data.json consumed by serve_review.py (no
intermediate markdown step) plus a sibling *_KEY.md.

Usage:
  python -m evaluation.qualitative.blind_test_v2_generator
"""
from __future__ import annotations
import glob
import json
import os
import random
import string
import sys
from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from real_data.ingestion.micro_features import _cache_prices  # noqa: E402

REAL_DIR = os.path.join(ROOT, "real_data")
RESULTS_DIR = os.path.join(REAL_DIR, "results")
PROCESSED = os.path.join(REAL_DIR, "processed")
QUAL_DIR = os.path.join(ROOT, "evaluation", "qualitative")
REVIEWS_DIR = os.path.join(QUAL_DIR, "reviews")
os.makedirs(REVIEWS_DIR, exist_ok=True)

SEED = 42
TOP_K = 3
N_RANDOM = 3
PRICE_DAYS = 90

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
SINGLE = ["Tech", "Healthcare", "Financial", "Energy", "Consumer"]
N_PER = 2
N_MIX = 5

GROUPS = ["contrastive_v2", "concat_eq", "random"]


# ---------- helpers ------------------------------------------------------
def latest_run_500():
    cands = sorted(glob.glob(os.path.join(RESULTS_DIR, "run_500_*.json")))
    cands = [c for c in cands if "recalibrated" not in c]
    if not cands:
        raise SystemExit("No run_500_*.json found.")
    return cands[-1]


def stratified_split(events, train_frac=0.7, seed=42):
    rng = random.Random(seed)
    by_sec = defaultdict(list)
    for e in events:
        by_sec[e["sector"]].append(e)
    train, test = [], []
    for evs in by_sec.values():
        rng.shuffle(evs)
        cut = int(len(evs) * train_frac)
        train.extend(evs[:cut])
        test.extend(evs[cut:])
    rng.shuffle(train); rng.shuffle(test)
    return train, test


def pick_queries(test, rng):
    by_b = defaultdict(list)
    for e in test:
        by_b[MACRO_BUCKET.get(e["sector"], "Mix")].append(e)
    out = []
    for b in SINGLE:
        pool = by_b.get(b, []).copy()
        rng.shuffle(pool)
        out.extend(pool[:N_PER])
    mix = by_b.get("Mix", []).copy()
    rng.shuffle(mix)
    out.extend(mix[:N_MIX])
    return out


def price_series(ticker, date_str, days=PRICE_DAYS):
    try:
        df = _cache_prices(ticker)
    except Exception:
        return []
    if df is None or df.empty or "Close" not in df.columns:
        return []
    d0 = pd.to_datetime(date_str)
    end = d0 + timedelta(days=days + 7)
    win = df.loc[d0:end, "Close"].dropna()
    if win.empty:
        return []
    base = win.index[0]
    out = []
    for ts, px in win.items():
        delta = (ts - base).days
        if delta > days:
            break
        out.append({"day": int(delta), "date": ts.strftime("%Y-%m-%d"), "price": float(px)})
    return out


def candidate_dict(ev, summary, label, group_label):
    r = ev["reaction_30d"]
    m = ev["macro_features"]
    return {
        "label": label,
        "group_label": group_label,   # X / Y / Z (NOT the encoder name)
        "ticker": ev["ticker"],
        "date": ev["date"],
        "sector_gics": ev["sector"],
        "macro": {
            "vix": m["vix"], "yield_10y": m["yield_10y"],
            "slope": m["yield_curve_slope"], "credit_spread": m["credit_spread"],
        },
        "reaction_30d": {
            "return": r["return"], "vol": r["realized_vol"],
            "max_dd": r["max_drawdown"], "persistence": r["persistence"],
        },
        "narrative_summary": summary or "[summary unavailable]",
        "text_full": ev.get("text") or "",
        "price_series_post_event": price_series(ev["ticker"], ev["date"]),
    }


# ---------- main ---------------------------------------------------------
def main():
    run_path = latest_run_500()
    print(f"using retrieval run: {os.path.basename(run_path)}")
    with open(run_path) as f:
        run = json.load(f)
    with open(os.path.join(PROCESSED, "sample_500.json")) as f:
        events = json.load(f)
    summ_path = os.path.join(PROCESSED, "sample_500_summaries.json")
    if os.path.exists(summ_path):
        with open(summ_path) as f:
            summaries = json.load(f)
        print(f"summaries loaded: {len(summaries)}")
    else:
        summaries = {}
        print("WARN: no summaries file — candidates will show [summary unavailable]")

    train, test = stratified_split(events, train_frac=0.7, seed=SEED)
    train_index = {e["id"]: e for e in train}
    train_ids = list(train_index.keys())

    # Retrievals per encoder
    retr = {"concat_eq": {}, "contrastive_v2": {}}
    for qid, info in run["retrievals"].items():
        for enc, top in info["top5"].items():
            if enc in retr:
                retr[enc][qid] = [t["id"] for t in top]

    rng = random.Random(SEED + 1)
    queries = pick_queries(test, rng)

    label_rng = random.Random(SEED + 2)
    random_rng = random.Random(SEED + 3)
    group_rng = random.Random(SEED + 4)

    out_queries = []
    key_lines = [
        "# Blind test V2 — KEY (id → encoder + group)\n",
        "Do not consult before evaluation.\n",
        "Groups: contrastive_v2, concat_eq, random. Group letters X/Y/Z permuted per query.\n",
    ]

    for qi, q in enumerate(queries, start=1):
        # Encoder picks
        ce_ids = retr["concat_eq"].get(q["id"], [])[:TOP_K]
        cv_ids = retr["contrastive_v2"].get(q["id"], [])[:TOP_K]
        # Random pool: exclude same ticker + already picked ids
        used = set(ce_ids) | set(cv_ids)
        pool = [tid for tid in train_ids
                if tid not in used and train_index[tid]["ticker"] != q["ticker"]]
        random_rng.shuffle(pool)
        rnd_ids = pool[:N_RANDOM]

        # group_label permutation: shuffle X/Y/Z across the 3 encoder groups
        group_letters = ["X", "Y", "Z"]
        group_rng.shuffle(group_letters)
        # mapping: encoder_name -> group_letter
        enc_to_letter = dict(zip(GROUPS, group_letters))

        # Build candidates. Track provenance for KEY.
        prov = defaultdict(list)   # tid -> [encoder...]
        rank_in_enc = {}           # (enc, tid) -> rank
        for enc, ids in [("contrastive_v2", cv_ids), ("concat_eq", ce_ids), ("random", rnd_ids)]:
            for rk, tid in enumerate(ids, start=1):
                prov[tid].append(enc)
                rank_in_enc[(enc, tid)] = rk

        # If the same id is picked by multiple encoders, keep ONE card and
        # assign group_label of the FIRST encoder in GROUPS priority order.
        unique_ids = list(prov.keys())
        label_rng.shuffle(unique_ids)
        ascii_labels = list(string.ascii_uppercase)[:len(unique_ids)]

        cands = []
        for lbl, tid in zip(ascii_labels, unique_ids):
            ev = train_index[tid]
            encs = prov[tid]
            primary_enc = encs[0]  # first in GROUPS order (we appended in that order)
            cands.append(candidate_dict(
                ev, summaries.get(tid), lbl, enc_to_letter[primary_enc]
            ))

        bucket = MACRO_BUCKET.get(q["sector"], "Mix")
        q_summary = summaries.get(q["id"]) or "[summary unavailable]"
        q_macro = q["macro_features"]; q_react = q["reaction_30d"]
        out_queries.append({
            "query_id": qi,
            "event": {
                "ticker": q["ticker"], "date": q["date"],
                "sector_gics": q["sector"], "macro_bucket": bucket,
                "narrative_summary": q_summary,
                "text_full": q.get("text") or "",
                "macro": {
                    "vix": q_macro["vix"], "yield_10y": q_macro["yield_10y"],
                    "slope": q_macro["yield_curve_slope"],
                    "credit_spread": q_macro["credit_spread"],
                },
                "reaction_30d": {
                    "return": q_react["return"], "vol": q_react["realized_vol"],
                    "max_dd": q_react["max_drawdown"], "persistence": q_react["persistence"],
                },
                "price_series_post_event": price_series(q["ticker"], q["date"]),
            },
            "candidates": cands,
        })

        # KEY section
        key_lines.append(f"\n## Query #{qi}: {q['ticker']} {q['date']} ({bucket})\n")
        key_lines.append(f"Group mapping: contrastive_v2={enc_to_letter['contrastive_v2']}, "
                         f"concat_eq={enc_to_letter['concat_eq']}, random={enc_to_letter['random']}\n")
        key_lines.append("| Label | Train event | Encoder(s) | Rank(s) | Group letter |")
        key_lines.append("|-------|-------------|------------|---------|--------------|")
        for lbl, tid in zip(ascii_labels, unique_ids):
            ev = train_index[tid]
            encs = prov[tid]
            tag = " + ".join(encs) if len(encs) > 1 else encs[0]
            ranks = ", ".join(f"{en}#{rank_in_enc[(en,tid)]}" for en in encs)
            primary = encs[0]
            key_lines.append(f"| {lbl} | {ev['ticker']} {ev['date']} | {tag} | {ranks} "
                             f"| {enc_to_letter[primary]} |")

        print(f"  Q{qi:02d} {q['ticker']} {q['date']:>10}  cands={len(cands)} "
              f"(ce={len(ce_ids)} cv={len(cv_ids)} rnd={len(rnd_ids)})")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    review_id = f"blind_test_v2_{ts}"
    data_path = os.path.join(REVIEWS_DIR, f"{review_id}_data.json")
    key_path = os.path.join(QUAL_DIR, f"{review_id}_KEY.md")

    out = {
        "review_id": review_id,
        "version": 2,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "key_file": os.path.basename(key_path),
        "groups": GROUPS,
        "metrics": [
            {"key": "same_dynamic", "label": "Stessa dinamica economica sottostante"},
            {"key": "same_regime",  "label": "Stesso market regime (vol, liquidità, sentiment)"},
            {"key": "same_surprise","label": "Stesso tipo di sorpresa rispetto alle aspettative"},
            {"key": "mental_precedent", "label": "Utile come precedente mentale per ragionare sulla query"},
        ],
        "queries": out_queries,
    }
    with open(data_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    with open(key_path, "w") as f:
        f.write("\n".join(key_lines))

    print(f"\n  DATA :  {data_path}")
    print(f"  KEY  :  {key_path}")
    print(f"\n  {len(out_queries)} queries built. DO NOT open the KEY file before evaluation.")


if __name__ == "__main__":
    main()
