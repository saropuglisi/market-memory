"""Analyze blind_test_v2 results: 3 groups × 4 metrics.

Reads:
  - responses JSON  (evaluation/qualitative/reviews/<id>_responses.json)
  - KEY markdown    (evaluation/qualitative/<id>_KEY.md)
  - data JSON       (evaluation/qualitative/reviews/<id>_data.json) — for
                    text/summary lookup in the Hard Failures section

Reports:
  - per-metric × per-encoder summary (mean, median, n, hi/lo)
  - Kruskal-Wallis across the 3 encoder groups (per metric)
  - Pairwise Mann-Whitney U (per metric)
  - Hard Failures: candidates with mean(4 metrics) <= 2 — encoder, text dump
  - Top Performers: candidates with mean(4 metrics) >= 4

Usage:
  python -m evaluation.qualitative.analyze_blind_results_v2 \
      [--responses ...] [--key ...] [--data ...] [--out report.md]

With no args, picks the most recent blind_test_v2_* trio.
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from statistics import mean, median

try:
    from scipy.stats import mannwhitneyu, kruskal
except ImportError:
    mannwhitneyu = kruskal = None

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEWS = os.path.join(HERE, "reviews")

METRICS = ["same_dynamic", "same_regime", "same_surprise", "mental_precedent"]
GROUPS = ["contrastive_v2", "concat_eq", "random"]

QUERY_RE = re.compile(r"^## Query #(\d+):", re.MULTILINE)
KEY_ROW_RE = re.compile(
    r"^\|\s*([A-Z])\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*([XYZ])\s*\|\s*$"
)


def parse_key(path):
    """Return {query_idx: {label: [encoder, ...]}}. Multi-encoder picks
    have multiple entries (split on ' + ')."""
    with open(path) as f:
        text = f.read()
    out = {}
    parts = re.split(r"(?=^## Query #\d+:)", text, flags=re.MULTILINE)
    for part in parts:
        m = QUERY_RE.search(part)
        if not m:
            continue
        qid = int(m.group(1))
        rows = {}
        for line in part.splitlines():
            mm = KEY_ROW_RE.match(line.strip())
            if mm:
                lbl = mm.group(1)
                enc_str = mm.group(3).replace("(picked by both)", "").strip()
                encs = [e.strip() for e in enc_str.split("+") if e.strip()]
                rows[lbl] = encs
        out[qid] = rows
    return out


def parse_responses(path):
    """Return {qid: {label: {ratings:{}, notes, cannot_evaluate}}}."""
    with open(path) as f:
        data = json.load(f)
    out = {}
    for r in data.get("responses", []):
        if r.get("skipped"):
            continue
        qid = int(r["query_id"])
        bucket = {"notes": r.get("notes", ""), "cannot_evaluate": bool(r.get("cannot_evaluate")),
                  "ratings": dict(r.get("ratings") or {})}
        # legacy v1 fields
        for k in ("utility", "insight", "transferability"):
            if r.get(k) is not None and k not in bucket["ratings"]:
                bucket["ratings"][k] = r[k]
        out.setdefault(qid, {})[r["candidate_label"]] = bucket
    return out


def aggregate(responses, keys):
    """{encoder: {metric: [values]}}. Multi-encoder picks contribute to all
    encoders. Skip cannot_evaluate."""
    per = defaultdict(lambda: defaultdict(list))
    for qid, rows in responses.items():
        key_map = keys.get(qid, {})
        for lbl, val in rows.items():
            if val.get("cannot_evaluate"):
                continue
            encs = key_map.get(lbl, [])
            for enc in encs:
                for m in METRICS:
                    v = val["ratings"].get(m)
                    if v is not None:
                        per[enc][m].append(float(v))
    return per


def candidate_means(responses, keys):
    """List of {qid, lbl, encs, mean, ratings, notes}."""
    out = []
    for qid, rows in responses.items():
        for lbl, val in rows.items():
            if val.get("cannot_evaluate"):
                continue
            vals = [val["ratings"].get(m) for m in METRICS]
            vals = [v for v in vals if v is not None]
            if not vals:
                continue
            out.append({
                "qid": qid, "label": lbl,
                "encs": keys.get(qid, {}).get(lbl, []),
                "mean": sum(vals)/len(vals),
                "ratings": val["ratings"],
                "notes": val.get("notes", ""),
            })
    return out


def find_in_data(data, qid, lbl):
    """Return (query_event, candidate_dict) from data json."""
    for q in data.get("queries", []):
        if int(q["query_id"]) == qid:
            for c in q["candidates"]:
                if c["label"] == lbl:
                    return q["event"], c
    return None, None


def build_report(responses, keys, data, run_meta):
    lines = ["# Blind Test V2 — Analysis Report", ""]
    lines.append(f"- responses : {run_meta['responses']}")
    lines.append(f"- key       : {run_meta['key']}")
    lines.append(f"- data      : {run_meta['data']}")
    n_eval = sum(len(r) for r in responses.values())
    n_ce = sum(1 for rows in responses.values() for v in rows.values() if v.get("cannot_evaluate"))
    lines.append(f"- queries with answers: {len(responses)}; total rated rows: {n_eval}; cannot_evaluate: {n_ce}")
    lines.append("")

    per = aggregate(responses, keys)

    # ---- Summary table ----
    lines.append("## Per encoder × metric")
    lines.append("")
    header = "| encoder | " + " | ".join(METRICS) + " |"
    sep = "|---|" + "---|" * len(METRICS)
    lines.append(header); lines.append(sep)
    for enc in GROUPS:
        cells = []
        for m in METRICS:
            v = per[enc][m]
            cells.append(f"{mean(v):.2f} (med {median(v):.1f}, n={len(v)})" if v else "n/a")
        lines.append(f"| **{enc}** | " + " | ".join(cells) + " |")
    lines.append("")

    lines.append("### High (≥4) / Low (≤2) per encoder × metric")
    lines.append("")
    lines.append("| encoder | metric | hi | lo | n |")
    lines.append("|---|---|---|---|---|")
    for enc in GROUPS:
        for m in METRICS:
            v = per[enc][m]
            hi = sum(1 for x in v if x >= 4); lo = sum(1 for x in v if x <= 2)
            lines.append(f"| {enc} | {m} | {hi} | {lo} | {len(v)} |")
    lines.append("")

    # ---- Stats ----
    lines.append("## Statistical tests")
    lines.append("")
    if kruskal is None:
        lines.append("_scipy not installed — install scipy to enable tests._")
    else:
        lines.append("### Kruskal-Wallis (3-way) per metric")
        lines.append("")
        lines.append("| metric | H | p | significant |")
        lines.append("|---|---|---|---|")
        for m in METRICS:
            samples = [per[enc][m] for enc in GROUPS if per[enc][m]]
            if len(samples) < 3 or min(len(s) for s in samples) < 3:
                lines.append(f"| {m} | n/a | n/a | insufficient n |")
                continue
            try:
                stat, p = kruskal(*samples)
                sig = "**p<0.05**" if p < 0.05 else ("p<0.1" if p < 0.1 else "ns")
                lines.append(f"| {m} | {stat:.3f} | {p:.4f} | {sig} |")
            except Exception as e:
                lines.append(f"| {m} | err | {e} | |")
        lines.append("")

        lines.append("### Pairwise Mann-Whitney U (two-sided)")
        lines.append("")
        lines.append("| metric | pair | U | p | sig |")
        lines.append("|---|---|---|---|---|")
        pairs = [("contrastive_v2","concat_eq"),
                 ("contrastive_v2","random"),
                 ("concat_eq","random")]
        for m in METRICS:
            for a, b in pairs:
                va, vb = per[a][m], per[b][m]
                if len(va) < 3 or len(vb) < 3:
                    lines.append(f"| {m} | {a} vs {b} | - | - | insufficient |")
                    continue
                try:
                    stat, p = mannwhitneyu(va, vb, alternative="two-sided")
                    sig = "**" if p < 0.05 else ("." if p < 0.1 else "")
                    lines.append(f"| {m} | {a} vs {b} | {stat:.1f} | {p:.4f} | {sig} |")
                except Exception as e:
                    lines.append(f"| {m} | {a} vs {b} | err | {e} | |")
        lines.append("")

    # ---- Hard failures + top performers ----
    cm = candidate_means(responses, keys)
    cm.sort(key=lambda x: x["mean"])
    hard = [c for c in cm if c["mean"] <= 2.0]
    top  = [c for c in cm if c["mean"] >= 4.0]

    lines.append(f"## Hard Failures (mean of 4 metrics ≤ 2.0)  —  {len(hard)} candidates")
    lines.append("")
    for c in hard:
        ev, cand = find_in_data(data, c["qid"], c["label"])
        q_t = f"{ev['ticker']} {ev['date']}" if ev else "?"
        c_t = f"{cand['ticker']} {cand['date']}  ({cand['sector_gics']})" if cand else "?"
        ratings = "  ".join(f"{m}={c['ratings'].get(m,'-')}" for m in METRICS)
        lines.append(f"### Q{c['qid']} {q_t} → label {c['label']}: {c_t}")
        lines.append(f"- encoders: **{', '.join(c['encs']) or '?'}**  | mean={c['mean']:.2f}")
        lines.append(f"- {ratings}")
        if c["notes"]:
            lines.append(f"- notes: _{c['notes']}_")
        if cand:
            summ = (cand.get("narrative_summary") or "").strip()
            lines.append(f"- summary: {summ}")
            txt = (cand.get("text_full") or "").strip().replace("\n", " ")[:600]
            lines.append(f"- text[:600]: > {txt}")
        lines.append("")

    lines.append(f"## Top Performers (mean of 4 metrics ≥ 4.0)  —  {len(top)} candidates")
    lines.append("")
    for c in sorted(top, key=lambda x: -x["mean"]):
        ev, cand = find_in_data(data, c["qid"], c["label"])
        q_t = f"{ev['ticker']} {ev['date']}" if ev else "?"
        c_t = f"{cand['ticker']} {cand['date']}  ({cand['sector_gics']})" if cand else "?"
        ratings = "  ".join(f"{m}={c['ratings'].get(m,'-')}" for m in METRICS)
        lines.append(f"### Q{c['qid']} {q_t} → label {c['label']}: {c_t}")
        lines.append(f"- encoders: **{', '.join(c['encs']) or '?'}**  | mean={c['mean']:.2f}")
        lines.append(f"- {ratings}")
        if c["notes"]:
            lines.append(f"- notes: _{c['notes']}_")
        if cand:
            summ = (cand.get("narrative_summary") or "").strip()
            lines.append(f"- summary: {summ}")
        lines.append("")

    # ---- Encoder share among hard/top ----
    def enc_share(group):
        share = defaultdict(int)
        for c in group:
            for e in c["encs"]:
                share[e] += 1
        return share
    lines.append("## Encoder share among Hard Failures / Top Performers")
    lines.append("")
    lines.append("| encoder | hard count | top count |")
    lines.append("|---|---|---|")
    sh_h = enc_share(hard); sh_t = enc_share(top)
    for enc in GROUPS:
        lines.append(f"| {enc} | {sh_h.get(enc,0)} | {sh_t.get(enc,0)} |")
    lines.append("")

    return "\n".join(lines)


def autopick():
    resp = sorted(glob.glob(os.path.join(REVIEWS, "blind_test_v2_*_responses.json")))
    data = sorted(glob.glob(os.path.join(REVIEWS, "blind_test_v2_*_data.json")))
    keys = sorted(glob.glob(os.path.join(HERE, "blind_test_v2_*_KEY.md")))
    return (resp[-1] if resp else None,
            keys[-1] if keys else None,
            data[-1] if data else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--responses"); ap.add_argument("--key")
    ap.add_argument("--data"); ap.add_argument("--out")
    args = ap.parse_args()
    r, k, d = autopick()
    args.responses = args.responses or r
    args.key = args.key or k
    args.data = args.data or d
    missing = [n for n, v in [("responses",args.responses),("key",args.key),("data",args.data)] if not v]
    if missing:
        print(f"Missing: {missing}")
        sys.exit(1)
    print(f"responses: {args.responses}\nkey      : {args.key}\ndata     : {args.data}")
    responses = parse_responses(args.responses)
    keys = parse_key(args.key)
    with open(args.data) as f:
        data = json.load(f)
    report = build_report(responses, keys, data, {
        "responses": os.path.basename(args.responses),
        "key": os.path.basename(args.key),
        "data": os.path.basename(args.data),
    })
    out_path = args.out or args.responses.replace("_responses.json", "_REPORT.md")
    with open(out_path, "w") as f:
        f.write(report)
    print(f"\nreport: {out_path}")
    # Echo summary table to stdout
    print("\n=== Summary ===")
    per = aggregate(responses, keys)
    for enc in GROUPS:
        cells = []
        for m in METRICS:
            v = per[enc][m]
            cells.append(f"{m}={mean(v):.2f}(n={len(v)})" if v else f"{m}=n/a")
        print(f"  {enc:<18} | " + "  ".join(cells))


if __name__ == "__main__":
    main()
