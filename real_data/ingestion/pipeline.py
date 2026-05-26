"""Build sample_50 dataset: discover 8-K Item 2.02 filings, parse, compute features.

Strategy:
- universe: S&P 500 (with GICS sector from Wikipedia)
- stratified candidate pool by year × sector
- for each candidate (ticker, target_window), find 8-K Item 2.02 in SEC EDGAR
- download primary + ex-99 exhibit, parse press release text
- compute macro/micro/semantic/reaction
- accept first 50 that succeed end-to-end
"""
from __future__ import annotations
import json
import os
import random
import sys
import warnings
from datetime import datetime, timedelta

import pandas as pd

from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from .sec_edgar import (load_ticker_to_cik, list_8k_filings, list_filing_exhibits,
                        download_filing, download_exhibits)
from .parser import parse_filing, parse_press_release, select_press_release_exhibits
from .macro_features import macro_features_for
from .micro_features import micro_features_for, reaction_30d_for
from .semantic_features import semantic_features_for
from .text_cleaning import clean_text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP500_PATH = os.path.join(ROOT, "raw", "sp500.csv")
PROCESSED = os.path.join(ROOT, "processed")
os.makedirs(PROCESSED, exist_ok=True)

YEARS = list(range(2018, 2025))  # 2018..2024 inclusive
TARGET_N = int(os.environ.get("TARGET_N", 50))
SEED = 42
TEXT_CAP = int(os.environ.get("TEXT_CAP", 5000))   # post-clean cap
MIN_TEXT_LEN = int(os.environ.get("MIN_TEXT_LEN", 500))
OVERSAMPLE_MULT = int(os.environ.get("OVERSAMPLE_MULT", 4))
OUT_NAME = os.environ.get("OUT_NAME", "sample_50.json")


def candidate_pool(rng: random.Random, target: int = 100) -> list[dict]:
    """Stratified candidate (ticker, year, target_date)."""
    sp = pd.read_csv(SP500_PATH)
    sp["Symbol"] = sp["Symbol"].str.replace(".", "-", regex=False)  # BRK.B -> BRK-B for yfinance
    sectors = sp["GICS Sector"].unique().tolist()
    # Per year, sample 'target/len(YEARS)' tickers stratified by sector
    per_year = max(1, target // len(YEARS) + 1)
    candidates = []
    for year in YEARS:
        # bucket by sector, sample 1-2 per sector
        per_sector = max(1, per_year // len(sectors) + 1)
        for sector in sectors:
            sec_tickers = sp[sp["GICS Sector"] == sector]["Symbol"].tolist()
            rng.shuffle(sec_tickers)
            for t in sec_tickers[:per_sector]:
                # pick a quarter-end window center: 4 windows per year
                q = rng.choice([1, 2, 3, 4])
                # quarter-end dates ~ end of Mar/Jun/Sep/Dec; earnings filings 3-7 weeks after
                qend = {1: f"{year}-03-31", 2: f"{year}-06-30", 3: f"{year}-09-30", 4: f"{year}-12-31"}[q]
                # target window center ~ qend + 30 days
                center = (pd.to_datetime(qend) + timedelta(days=30)).strftime("%Y-%m-%d")
                candidates.append({"ticker": t, "sector": sector, "year": year,
                                   "quarter": f"{year}Q{q}", "target_center": center})
    rng.shuffle(candidates)
    return candidates[:target * OVERSAMPLE_MULT]  # over-sample for filtering


def find_8k_with_item202(cik: str, target_center: str, window_days: int = 60):
    """Return first 8-K Item 2.02 filing closest to target_center within window."""
    d = pd.to_datetime(target_center)
    date_from = (d - timedelta(days=window_days)).strftime("%Y-%m-%d")
    date_to = (d + timedelta(days=window_days)).strftime("%Y-%m-%d")
    filings = list_8k_filings(cik, date_from, date_to)
    cands = [f for f in filings if "2.02" in str(f.get("items", ""))]
    if not cands:
        return None
    # pick the one closest to target center
    cands.sort(key=lambda f: abs((pd.to_datetime(f["filing_date"]) - d).days))
    return cands[0]


def build_episode(cand: dict, cik_map: dict) -> dict | None:
    ticker = cand["ticker"]
    info = cik_map.get(ticker.replace("-", ".").upper()) or cik_map.get(ticker.upper())
    if not info:
        return None
    cik = info["cik"]
    f = find_8k_with_item202(cik, cand["target_center"])
    if f is None:
        return None
    # Get exhibits, pick press release
    try:
        exhibits = list_filing_exhibits(cik, f["accession"])
    except Exception as e:
        print(f"[skip] {ticker} exhibits failed: {e}")
        return None
    press_names = select_press_release_exhibits(exhibits)
    text = ""
    text_full = ""
    if press_names:
        try:
            paths = download_exhibits(cik, f["accession"], press_names[:1])
            if paths:
                full = open(paths[0][0], encoding="utf-8", errors="ignore").read()
                text_full = parse_press_release(full)
        except Exception as e:
            print(f"[skip] {ticker} press download failed: {e}")
            return None
    if not text_full:
        # fallback: parse primary doc Item 2.02 section
        try:
            path, _ = download_filing(cik, f["accession"], f["primary_doc"])
            html = open(path, encoding="utf-8", errors="ignore").read()
            parsed = parse_filing(html)
            text_full = parsed["item_202_text"] or parsed["raw_text"]
        except Exception as e:
            print(f"[skip] {ticker} primary parse failed: {e}")
            return None
    if not text_full.strip():
        return None

    # Apply boilerplate cleaning, then cap
    cleaned, clean_stats = clean_text(text_full)
    if len(cleaned) < MIN_TEXT_LEN:
        print(f"[skip] {ticker} {f['filing_date']} cleaned text too short ({len(cleaned)} < {MIN_TEXT_LEN})")
        return None
    text = cleaned[:TEXT_CAP]

    date = f["filing_date"]
    # features
    macro = macro_features_for(date)
    micro = micro_features_for(ticker.replace(".", "-"), date, cand["sector"])
    reaction = reaction_30d_for(ticker.replace(".", "-"), date)
    semantic = semantic_features_for(text)

    if any(x is None for x in (macro, micro, reaction)):
        print(f"[skip] {ticker} {date} missing features: macro={macro is not None} micro={micro is not None} react={reaction is not None}")
        return None
    if any(v is None for v in macro.values()):
        print(f"[skip] {ticker} {date} macro has None: {macro}")
        return None

    ep_id = f"{ticker}_{cand['quarter']}_8K_{date.replace('-','')}"
    return {
        "id": ep_id,
        "ticker": ticker,
        "date": date,
        "event_type": "earnings_8k",
        "sector": cand["sector"],
        "cik": cik,
        "text": text,
        "text_full": text_full,
        "text_clean_stats": clean_stats,
        "macro_features": macro,
        "micro_features": micro,
        "semantic_features": semantic,
        "reaction_30d": reaction,
        "filing_url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{f['accession'].replace('-','')}/",
        "accession": f["accession"],
        "quarter": cand["quarter"],
    }


def main():
    rng = random.Random(SEED)
    cik_map = load_ticker_to_cik()
    candidates = candidate_pool(rng, target=TARGET_N * OVERSAMPLE_MULT)
    print(f"target N={TARGET_N}, cap={TEXT_CAP}, min_len={MIN_TEXT_LEN}, candidates: {len(candidates)}")

    accepted = []
    failed = []
    for i, cand in enumerate(candidates):
        if len(accepted) >= TARGET_N:
            break
        try:
            ep = build_episode(cand, cik_map)
            if ep:
                accepted.append(ep)
                print(f"  [{len(accepted)}/{TARGET_N}] {ep['ticker']} {ep['date']} sector={ep['sector']}")
            else:
                failed.append({"ticker": cand["ticker"], "sector": cand["sector"], "target": cand["target_center"]})
        except Exception as e:
            print(f"[err] {cand['ticker']} {cand['target_center']}: {e}")
            failed.append({"ticker": cand["ticker"], "error": str(e)})

    out_path = os.path.join(PROCESSED, OUT_NAME)
    with open(out_path, "w") as f:
        json.dump(accepted, f, indent=2)
    print(f"\nSaved {len(accepted)} events to {out_path}")
    print(f"Failed candidates: {len(failed)}")

    # Metadata
    meta = {
        "n_events": len(accepted),
        "n_failed_candidates": len(failed),
        "year_dist": {},
        "sector_dist": {},
        "feature_stats": {},
    }
    if accepted:
        for ep in accepted:
            y = ep["date"][:4]
            meta["year_dist"][y] = meta["year_dist"].get(y, 0) + 1
            meta["sector_dist"][ep["sector"]] = meta["sector_dist"].get(ep["sector"], 0) + 1
        for block in ("macro_features", "micro_features", "semantic_features", "reaction_30d"):
            vals = {}
            for ep in accepted:
                for k, v in ep[block].items():
                    if v is None:
                        continue
                    vals.setdefault(k, []).append(float(v))
            meta["feature_stats"][block] = {k: {"mean": sum(v)/len(v), "min": min(v), "max": max(v)}
                                              for k, v in vals.items() if v}
    # Aggregate cleaning stats
    if accepted:
        rem_pcts = [ep["text_clean_stats"]["removed_pct"] for ep in accepted if "text_clean_stats" in ep]
        clean_lens = [ep["text_clean_stats"]["clean_len"] for ep in accepted if "text_clean_stats" in ep]
        if rem_pcts:
            meta["cleaning_stats"] = {
                "removed_pct_mean": round(sum(rem_pcts)/len(rem_pcts), 2),
                "removed_pct_max": round(max(rem_pcts), 2),
                "clean_len_mean": int(sum(clean_lens)/len(clean_lens)),
                "clean_len_min": min(clean_lens),
                "clean_len_max": max(clean_lens),
            }
        # guidance distrib
        gd_dist = {}
        for ep in accepted:
            v = ep["semantic_features"]["guidance_direction"]
            gd_dist[v] = gd_dist.get(v, 0) + 1
        meta["guidance_distribution"] = gd_dist
    meta_name = OUT_NAME.replace(".json", "_metadata.json")
    with open(os.path.join(PROCESSED, meta_name), "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Metadata saved to {meta_name}.")


if __name__ == "__main__":
    main()
