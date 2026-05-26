"""Convert a blind_test_<ts>.md into the JSON format consumed by serve_review.py.

Pulls per-event price series (0..90 days post-event) via yfinance with
aggressive caching under real_data/cache/prices/.

Usage:
  python -m evaluation.qualitative.prepare_review_data evaluation/qualitative/blind_test_20260525_175053.md
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from real_data.ingestion.micro_features import _cache_prices  # noqa: E402

REAL_DIR = os.path.join(ROOT, "real_data")
PROCESSED = os.path.join(REAL_DIR, "processed")
OUT_DIR = os.path.join(ROOT, "evaluation", "qualitative", "reviews")
os.makedirs(OUT_DIR, exist_ok=True)

PRICE_DAYS = 90

QUERY_RE = re.compile(
    r"^## Query #(\d+):\s+(\S+)\s+(\d{4}-\d{2}-\d{2})\s+—\s+([^\(]+)\s+\(([^\)]+)\)",
    re.MULTILINE,
)
CAND_ROW_RE = re.compile(
    r"^\|\s*([A-Z])\s*\|\s*([^\s|]+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|"
    r"\s*([+-][\d.]+)\s*/\s*([\d.]+)\s*/\s*([+-]?[\d.]+)\s*\|\s*(.*?)\s*\|$"
)
QUERY_TEXT_RE = re.compile(r"^>\s*(.+)$", re.MULTILINE)
MACRO_RE = re.compile(
    r"VIX=([\d.]+),\s*yield_10y=([\d.\-+]+),\s*slope=([+\-][\d.]+),\s*credit=([\d.]+)"
)
REACTION_RE = re.compile(
    r"ret=([+\-][\d.]+)\s*/\s*vol=([\d.]+)\s*/\s*dd=([+\-]?[\d.]+)\s*/\s*pers=([\d.]+)"
)


def parse_md(path: str):
    with open(path) as f:
        text = f.read()
    parts = re.split(r"(?=^## Query #\d+:)", text, flags=re.MULTILINE)
    queries = []
    for part in parts:
        m = QUERY_RE.search(part)
        if not m:
            continue
        q_idx = int(m.group(1))
        q_ticker = m.group(2)
        q_date = m.group(3)
        q_sector = m.group(4).strip()
        q_bucket = m.group(5).strip()
        # Find query text (the "> ..." line after "**Text (first 500 chars):**")
        snippet = ""
        if "**Text" in part:
            tail = part.split("**Text", 1)[1]
            m2 = QUERY_TEXT_RE.search(tail)
            if m2:
                snippet = m2.group(1).strip()
        # Macro + reaction lines
        macro = None
        m_mac = MACRO_RE.search(part)
        if m_mac:
            macro = {"vix": float(m_mac.group(1)), "yield_10y": float(m_mac.group(2)),
                     "slope": float(m_mac.group(3)), "credit_spread": float(m_mac.group(4))}
        reaction = None
        m_re = REACTION_RE.search(part)
        if m_re:
            reaction = {"return": float(m_re.group(1)), "vol": float(m_re.group(2)),
                        "max_dd": float(m_re.group(3)), "persistence": float(m_re.group(4))}
        # Candidate rows — between "### Candidate analogs" and "### Evaluation"
        cands = []
        if "### Candidate" in part:
            after = part.split("### Candidate", 1)[1]
            cand_section = after.split("### Evaluation", 1)[0]
            for line in cand_section.splitlines():
                mm = CAND_ROW_RE.match(line.strip())
                if mm:
                    cands.append({
                        "label": mm.group(1),
                        "ticker": mm.group(2),
                        "date": mm.group(3),
                        "sector_gics": mm.group(4).strip(),
                        "reaction_30d": {
                            "return": float(mm.group(5)),
                            "vol": float(mm.group(6)),
                            "max_dd": float(mm.group(7)),
                        },
                        "text_summary": mm.group(8).strip(),
                    })
        queries.append({
            "query_id": q_idx,
            "ticker": q_ticker, "date": q_date,
            "sector_gics": q_sector, "macro_bucket": q_bucket,
            "macro": macro, "reaction_30d": reaction,
            "text_summary": snippet,
            "candidates": cands,
        })
    return queries


def price_series_after(ticker: str, event_date: str, days: int = PRICE_DAYS):
    """Return [{day:int, price:float, date:str}] starting at event_date for `days` calendar days."""
    try:
        df = _cache_prices(ticker)
    except Exception as e:
        print(f"  [yf] {ticker} cache error: {e}")
        return []
    if df is None or df.empty or "Close" not in df.columns:
        return []
    d0 = pd.to_datetime(event_date)
    end = d0 + timedelta(days=days + 7)  # buffer for weekends
    win = df.loc[d0:end, "Close"].dropna()
    if win.empty:
        return []
    base_date = win.index[0]
    out = []
    for ts, px in win.items():
        delta = (ts - base_date).days
        if delta > days:
            break
        out.append({"day": int(delta), "date": ts.strftime("%Y-%m-%d"), "price": float(px)})
    return out


def enrich_with_event_data(query: dict, by_ticker_date: dict):
    """Use sample_500.json data to augment text_summary with cleaner snippet if available."""
    key = (query["ticker"], query["date"])
    ev = by_ticker_date.get(key)
    if ev:
        # Replace markdown snippet with the longer event text (first 600 chars)
        txt = (ev.get("text") or "").strip()
        if txt:
            query["text_summary"] = txt[:600]
    return query


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md_path", help="Path to blind_test_<ts>.md")
    ap.add_argument("--skip-prices", action="store_true",
                    help="Skip price downloads (useful for debugging the parser)")
    args = ap.parse_args()

    base = os.path.splitext(os.path.basename(args.md_path))[0]
    print(f"parsing {args.md_path}")
    queries = parse_md(args.md_path)
    print(f"  {len(queries)} queries parsed")

    # Load sample_500 for richer text
    try:
        with open(os.path.join(PROCESSED, "sample_500.json")) as f:
            events = json.load(f)
        by_td = {(e["ticker"], e["date"]): e for e in events}
    except FileNotFoundError:
        by_td = {}

    n_series = 0
    for q in queries:
        enrich_with_event_data(q, by_td)
        if not args.skip_prices:
            q["price_series_post_event"] = price_series_after(q["ticker"], q["date"])
            n_series += 1 if q["price_series_post_event"] else 0
        for c in q["candidates"]:
            ev = by_td.get((c["ticker"], c["date"]))
            if ev:
                txt = (ev.get("text") or "").strip()
                if txt:
                    c["text_summary"] = txt[:400]
            if not args.skip_prices:
                c["price_series_post_event"] = price_series_after(c["ticker"], c["date"])
                n_series += 1 if c["price_series_post_event"] else 0

    out = {
        "review_id": base,
        "source_md": os.path.basename(args.md_path),
        "key_file": base + "_KEY.md",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "queries": [
            {
                "query_id": q["query_id"],
                "event": {
                    "ticker": q["ticker"], "date": q["date"],
                    "sector_gics": q["sector_gics"],
                    "macro_bucket": q.get("macro_bucket"),
                    "text_summary": q["text_summary"],
                    "macro": q["macro"], "reaction_30d": q["reaction_30d"],
                    "price_series_post_event": q.get("price_series_post_event", []),
                },
                "candidates": q["candidates"],
            } for q in queries
        ],
    }
    out_path = os.path.join(OUT_DIR, f"{base}_data.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  fetched {n_series} price series (cached when possible)")
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
