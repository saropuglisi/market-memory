"""CLI tool for manually annotating narrative tags on 25 stratified events.

Picks 25 events from sample_500 stratified by sector × year × VIX regime.
For each event, shows ticker/date/sector/summary/full-text excerpt, then
prompts the user to annotate each tag (1=YES, 0=NO, enter=default 0).

Annotations are saved incrementally to manual_tags_validation.json after
every event, so the session is resume-friendly: re-running picks up where
you left off.

Usage:
  python -m real_data.manual_validation [--n 25] [--reset]
"""
from __future__ import annotations
import argparse
import json
import os
import random
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from real_data.narrative_tags_v2 import (
    NARRATIVE_TAGS_V2, TAG_KEYS_V2, CATEGORIES_V2,
)

PROCESSED = os.path.join(ROOT, "real_data", "processed")
EVENTS_PATH = os.path.join(PROCESSED, "sample_500.json")
SUMMARIES_PATH = os.path.join(PROCESSED, "sample_500_summaries.json")
OUT_PATH = os.path.join(PROCESSED, "manual_tags_validation.json")

SEED = 42
EXCERPT_CHARS = 2000
SHOW_MORE_CHARS = 4000   # additional shown if user asks "y"


def stratified_pick(events, n=25, seed=SEED):
    """Pick n events stratified by sector × year × VIX regime.

    VIX regime buckets: low(<15), mid(15-22), high(22-30), crisis(>30).
    Tries to spread the sample across all combinations available, then
    fills remaining slots randomly.
    """
    rng = random.Random(seed)

    def vix_bucket(v):
        if v < 15: return "low"
        if v < 22: return "mid"
        if v < 30: return "high"
        return "crisis"

    by_strat = defaultdict(list)
    for e in events:
        yr = e["date"][:4]
        vb = vix_bucket(e["macro_features"]["vix"])
        by_strat[(e["sector"], yr[:3] + "x", vb)].append(e)   # year decade-ish bucket too coarse; use year directly:
    by_strat = defaultdict(list)
    for e in events:
        yr = e["date"][:4]
        vb = vix_bucket(e["macro_features"]["vix"])
        by_strat[(e["sector"], yr, vb)].append(e)

    # Round-robin: 1 from each stratum, then 2nd round, etc., until n.
    buckets = list(by_strat.values())
    for b in buckets:
        rng.shuffle(b)
    rng.shuffle(buckets)
    picked = []
    cursor = 0
    while len(picked) < n and any(buckets):
        b = buckets[cursor % len(buckets)]
        if b:
            picked.append(b.pop(0))
        cursor += 1
        if cursor > len(buckets) * 10:
            break  # safety
    # Fill remaining if needed
    if len(picked) < n:
        rest = [e for e in events if e not in picked]
        rng.shuffle(rest)
        picked.extend(rest[:n - len(picked)])
    return picked[:n]


def load_annotations():
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH) as f:
            return json.load(f)
    return {"annotations": {}, "meta": {"tag_keys": TAG_KEYS_V2, "n_target": 25}}


def save_annotations(data):
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, OUT_PATH)


def prompt_tags(event, current=None):
    """Return dict {tag: 0/1} for one event."""
    current = current or {}
    result = {}
    print(f"\n  Annotate tags (1=yes, 0=no, Enter=default 0, ?=show description, q=quit):")
    for cat, tags in CATEGORIES_V2.items():
        print(f"\n    [{cat}]")
        for tag in tags:
            default = current.get(tag, 0)
            while True:
                ans = input(f"      {tag:<22} [{default}]: ").strip().lower()
                if ans == "?":
                    print(f"          → {NARRATIVE_TAGS_V2[tag]}")
                    continue
                if ans == "q":
                    return None
                if ans == "":
                    result[tag] = int(default)
                    break
                if ans in ("0", "1"):
                    result[tag] = int(ans)
                    break
                print(f"          (invalid: type 0, 1, ?, q, or Enter)")
    return result


def show_event(e, summary, idx, total):
    print("\n" + "═" * 78)
    print(f"  Event {idx+1}/{total}   id={e['id']}")
    print(f"  {e['ticker']}  {e['date']}  ({e['sector']})")
    print(f"  Macro: VIX={e['macro_features']['vix']:.1f}  "
          f"yield_10y={e['macro_features']['yield_10y']:.2f}  "
          f"credit={e['macro_features']['credit_spread']:.2f}")
    print("─" * 78)
    print(f"  SUMMARY:")
    print(f"    {summary}")
    print("─" * 78)
    text = (e.get("text") or "").strip()
    print(f"  FULL TEXT EXCERPT (first {EXCERPT_CHARS} chars of {len(text)}):")
    print()
    print(text[:EXCERPT_CHARS])
    print()
    cursor = EXCERPT_CHARS
    while cursor < len(text):
        more = input(f"  Show next {SHOW_MORE_CHARS} chars? (y/n) [n]: ").strip().lower()
        if more != "y":
            break
        print()
        print(text[cursor:cursor + SHOW_MORE_CHARS])
        print()
        cursor += SHOW_MORE_CHARS
    print("─" * 78)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=25, help="number of events to annotate (default 25)")
    ap.add_argument("--reset", action="store_true", help="discard existing annotations")
    args = ap.parse_args()

    if args.reset and os.path.exists(OUT_PATH):
        os.remove(OUT_PATH)

    with open(EVENTS_PATH) as f:
        events = json.load(f)
    summaries = {}
    if os.path.exists(SUMMARIES_PATH):
        with open(SUMMARIES_PATH) as f:
            summaries = json.load(f)

    picks = stratified_pick(events, n=args.n)
    print(f"Picked {len(picks)} events (stratified by sector × year × VIX regime, seed={SEED})")
    print(f"Annotations file: {OUT_PATH}")

    data = load_annotations()
    annotated = data["annotations"]
    todo = [(i, e) for i, e in enumerate(picks) if e["id"] not in annotated]
    print(f"already annotated: {len(annotated)}   todo: {len(todo)}\n")
    if not todo:
        print("All events already annotated. Done.")
        return

    for i, e in todo:
        summary = summaries.get(e["id"], "[no summary available]")
        show_event(e, summary, i, len(picks))
        result = prompt_tags(e)
        if result is None:
            print("\nQuit signal received. Annotations saved so far.")
            break
        annotated[e["id"]] = {
            **result,
            "_ticker": e["ticker"], "_date": e["date"], "_sector": e["sector"],
        }
        save_annotations(data)
        print(f"  ✓ saved  ({len(annotated)}/{len(picks)})")

    print(f"\nDone. {len(annotated)}/{len(picks)} annotated.")
    print(f"File: {OUT_PATH}")


if __name__ == "__main__":
    main()
