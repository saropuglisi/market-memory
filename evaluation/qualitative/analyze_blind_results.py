"""Aggregate blind A/B test results.

Two input formats supported:

  1) Web UI (preferred): JSON responses file produced by serve_review.py
     evaluation/qualitative/reviews/<id>_responses.json
     plus the KEY markdown file.

  2) Legacy markdown: a hand-filled blind_test_<ts>.md + KEY file.

Usage (web UI):
  python -m evaluation.qualitative.analyze_blind_results
      --responses evaluation/qualitative/reviews/<id>_responses.json
      --key evaluation/qualitative/blind_test_<ts>_KEY.md

Usage (legacy markdown):
  python -m evaluation.qualitative.analyze_blind_results
      --eval-md evaluation/qualitative/blind_test_<ts>.md
      --key evaluation/qualitative/blind_test_<ts>_KEY.md

If invoked with no flags and only one *_responses.json + KEY pair exists in
evaluation/qualitative/, it picks them automatically.

DO NOT run before the eval file is completed.
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from statistics import mean

try:
    from scipy.stats import mannwhitneyu
except ImportError:
    mannwhitneyu = None


QUERY_RE = re.compile(r"^## Query #(\d+):", re.MULTILINE)
EVAL_ROW_RE = re.compile(r"^\|\s*([A-Z])\s*\|\s*([\d.]*)\s*\|\s*([\d.]*)\s*\|\s*([\d.]*)\s*\|\s*(.*?)\s*\|$")
KEY_ROW_RE = re.compile(r"^\|\s*([A-Z])\s*\|\s*[^|]+\|\s*([^|]+?)\s*\|\s*[^|]*\|$")


def parse_eval(path):
    """Return {query_idx: {label: {utility, insight, transfer, notes}}}."""
    with open(path) as f:
        text = f.read()
    out = {}
    # Split by query
    parts = re.split(r"(?=^## Query #\d+:)", text, flags=re.MULTILINE)
    for part in parts:
        m = QUERY_RE.search(part)
        if not m:
            continue
        q_idx = int(m.group(1))
        # Find the "Evaluation" table (last 6 rows after the eval header)
        eval_section = part.split("### Evaluation")[-1] if "### Evaluation" in part else ""
        rows = {}
        for line in eval_section.splitlines():
            mm = EVAL_ROW_RE.match(line.strip())
            if mm:
                lbl, u, ins, tr, notes = mm.groups()
                if not (u or ins or tr):  # all empty, skip
                    continue
                try:
                    rows[lbl] = {
                        "utility": float(u) if u else None,
                        "insight": float(ins) if ins else None,
                        "transfer": float(tr) if tr else None,
                        "notes": notes.strip(),
                    }
                except ValueError:
                    pass
        out[q_idx] = rows
    return out


def parse_key(path):
    """Return {query_idx: {label: encoder_label}} where encoder_label is
    'concat_eq', 'contrastive_v2', or 'concat_eq + contrastive_v2'."""
    with open(path) as f:
        text = f.read()
    out = {}
    parts = re.split(r"(?=^## Query #\d+:)", text, flags=re.MULTILINE)
    for part in parts:
        m = QUERY_RE.search(part)
        if not m:
            continue
        q_idx = int(m.group(1))
        rows = {}
        for line in part.splitlines():
            mm = KEY_ROW_RE.match(line.strip())
            if mm:
                lbl, enc = mm.groups()
                # Strip "(picked by both)" suffix and rank info
                enc_clean = enc.replace("(picked by both)", "").strip()
                rows[lbl] = enc_clean
        out[q_idx] = rows
    return out


def aggregate(evaluations, keys):
    """Return {encoder: {metric: [values across all labelled rows]}}.
    Rows picked by both encoders contribute to both encoder buckets."""
    per_enc = defaultdict(lambda: defaultdict(list))
    for q_idx, rows in evaluations.items():
        key_map = keys.get(q_idx, {})
        for lbl, vals in rows.items():
            enc_str = key_map.get(lbl, "")
            enc_set = [e.strip() for e in enc_str.split("+")] if enc_str else []
            for enc in enc_set:
                if not enc:
                    continue
                for metric in ("utility", "insight", "transfer"):
                    v = vals.get(metric)
                    if v is not None:
                        per_enc[enc][metric].append(v)
    return per_enc


def report(per_enc):
    metrics = ("utility", "insight", "transfer")
    encs = sorted(per_enc.keys())
    print("\n=== Aggregate (mean ± n) ===")
    print(f"{'encoder':<22} | " + " | ".join(f"{m:<22}" for m in metrics))
    for enc in encs:
        cells = []
        for m in metrics:
            vals = per_enc[enc][m]
            cell = f"{mean(vals):.2f} (n={len(vals)})" if vals else "n/a"
            cells.append(f"{cell:<22}")
        print(f"{enc:<22} | " + " | ".join(cells))

    print("\n=== Distribution (high >=4 / low <=2) ===")
    for enc in encs:
        line = [f"{enc:<22}"]
        for m in metrics:
            vals = per_enc[enc][m]
            hi = sum(1 for v in vals if v >= 4)
            lo = sum(1 for v in vals if v <= 2)
            line.append(f"{m}: hi={hi} lo={lo} (n={len(vals)})")
        print(" | ".join(line))

    if mannwhitneyu is None:
        print("\nscipy not installed — skip Mann-Whitney U.")
        return
    if len(encs) < 2:
        return
    print("\n=== Mann-Whitney U (two-sided) ===")
    a, b = encs[:2]
    for m in metrics:
        va, vb = per_enc[a][m], per_enc[b][m]
        if len(va) < 3 or len(vb) < 3:
            print(f"  {m}: not enough samples ({len(va)} vs {len(vb)})")
            continue
        try:
            stat, p = mannwhitneyu(va, vb, alternative="two-sided")
            sig = "**" if p < 0.05 else ("." if p < 0.1 else "")
            print(f"  {m:<10}  {a} vs {b}: U={stat:.1f}  p={p:.4f}  {sig}")
        except Exception as e:
            print(f"  {m}: error {e}")


def parse_json_responses(path):
    """Convert serve_review.py JSON to the same shape as parse_eval()."""
    with open(path) as f:
        data = json.load(f)
    out = {}
    for r in data.get("responses", []):
        if r.get("skipped"):
            continue
        qid = int(r["query_id"])
        out.setdefault(qid, {})[r["candidate_label"]] = {
            "utility": float(r["utility"]),
            "insight": float(r["insight"]),
            "transfer": float(r["transferability"]),
            "notes": r.get("notes", ""),
        }
    return out


def autodetect():
    here = os.path.dirname(os.path.abspath(__file__))
    resp = sorted(glob.glob(os.path.join(here, "reviews", "*_responses.json")))
    keys = sorted(glob.glob(os.path.join(here, "*_KEY.md")))
    return (resp[-1] if resp else None, keys[-1] if keys else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--responses", help="JSON responses file from serve_review.py")
    ap.add_argument("--eval-md", help="legacy filled-in markdown")
    ap.add_argument("--key", help="blind_test_<ts>_KEY.md")
    ap.add_argument("legacy_positional", nargs="*", help="(legacy) eval.md key.md")
    args = ap.parse_args()

    # Backward-compat: positional [eval.md, key.md]
    if args.legacy_positional and not (args.responses or args.eval_md):
        if len(args.legacy_positional) >= 2:
            args.eval_md = args.legacy_positional[0]
            args.key = args.legacy_positional[1]

    if not (args.responses or args.eval_md):
        r, k = autodetect()
        args.responses = r; args.key = args.key or k
        if r and k:
            print(f"auto: responses={r}\n      key={k}")
    if not args.key:
        print("Missing --key.")
        sys.exit(1)

    if args.responses:
        evals = parse_json_responses(args.responses)
    else:
        evals = parse_eval(args.eval_md)
    keys = parse_key(args.key)

    n_eval_rows = sum(len(r) for r in evals.values())
    if n_eval_rows == 0:
        print("No filled-in rows found.")
        sys.exit(1)
    print(f"parsed {len(evals)} queries, {n_eval_rows} filled rows.")
    per_enc = aggregate(evals, keys)
    report(per_enc)


if __name__ == "__main__":
    main()
