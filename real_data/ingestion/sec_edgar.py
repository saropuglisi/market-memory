"""SEC EDGAR access: list 8-K filings by ticker + download.

Uses the EDGAR submissions API + direct filing archive download. Policy: max 10
req/sec, User-Agent required.
"""
from __future__ import annotations
import json
import os
import time
import hashlib
from typing import Optional

import requests

from .config import SEC_USER_AGENT, SEC_RATE_LIMIT_PER_SEC

CACHE_ROOT = os.path.join(os.path.dirname(__file__), "..", "raw", "sec")
TICKER_MAP_PATH = os.path.join(CACHE_ROOT, "company_tickers.json")
os.makedirs(CACHE_ROOT, exist_ok=True)

_HEADERS = {"User-Agent": SEC_USER_AGENT, "Accept-Encoding": "gzip, deflate"}
_min_interval = 1.0 / SEC_RATE_LIMIT_PER_SEC
_last_req = [0.0]


def _throttle():
    now = time.time()
    dt = now - _last_req[0]
    if dt < _min_interval:
        time.sleep(_min_interval - dt)
    _last_req[0] = time.time()


def _get(url: str, max_retries: int = 3) -> requests.Response:
    for attempt in range(max_retries):
        _throttle()
        r = requests.get(url, headers=_HEADERS, timeout=30)
        if r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError(f"failed after {max_retries} retries: {url}")


def load_ticker_to_cik() -> dict:
    """Map ticker uppercase -> {cik, name}."""
    if os.path.exists(TICKER_MAP_PATH):
        with open(TICKER_MAP_PATH) as f:
            return json.load(f)
    r = _get("https://www.sec.gov/files/company_tickers.json")
    data = r.json()
    out = {}
    for _, entry in data.items():
        out[entry["ticker"].upper()] = {
            "cik": str(entry["cik_str"]).zfill(10),
            "name": entry["title"],
        }
    with open(TICKER_MAP_PATH, "w") as f:
        json.dump(out, f)
    return out


def get_submissions(cik: str) -> dict:
    """Get SEC submissions JSON for a CIK; cache locally."""
    cache_path = os.path.join(CACHE_ROOT, f"submissions_{cik}.json")
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return json.load(f)
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    r = _get(url)
    data = r.json()
    with open(cache_path, "w") as f:
        json.dump(data, f)
    return data


def list_8k_filings(cik: str, date_from: str, date_to: str) -> list[dict]:
    """Return list of dicts: {accession, filing_date, primary_doc, items, form}.
    Filters to form == '8-K' in date range."""
    sub = get_submissions(cik)
    recent = sub.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accs = recent.get("accessionNumber", [])
    dates = recent.get("filingDate", [])
    primary_docs = recent.get("primaryDocument", [])
    items = recent.get("items", [])
    out = []
    for i, form in enumerate(forms):
        if form != "8-K":
            continue
        fd = dates[i]
        if fd < date_from or fd > date_to:
            continue
        out.append({
            "accession": accs[i],
            "filing_date": fd,
            "primary_doc": primary_docs[i] if i < len(primary_docs) else "",
            "items": items[i] if i < len(items) else "",
            "form": form,
        })
    return out


def download_filing(cik: str, accession: str, primary_doc: str) -> tuple[str, str]:
    """Returns (local_path, url). Caches HTML."""
    acc_nodash = accession.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_nodash}/{primary_doc}"
    fname = hashlib.md5(url.encode()).hexdigest() + ".html"
    path = os.path.join(CACHE_ROOT, "filings", fname)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        r = _get(url)
        with open(path, "wb") as f:
            f.write(r.content)
    return path, url


def list_filing_exhibits(cik: str, accession: str) -> list[dict]:
    """Returns [{name, type, last_modified, size}] of all files in the filing."""
    acc_nodash = accession.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_nodash}/"
    # Use index.json (machine-readable)
    idx_url = url + "index.json"
    r = _get(idx_url)
    data = r.json()
    return data.get("directory", {}).get("item", [])


def download_exhibits(cik: str, accession: str, exhibit_names: list[str]) -> list[tuple[str, str]]:
    """Download a list of exhibit filenames. Returns list of (path, url)."""
    acc_nodash = accession.replace("-", "")
    out = []
    for name in exhibit_names:
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_nodash}/{name}"
        fname = hashlib.md5(url.encode()).hexdigest() + os.path.splitext(name)[1]
        path = os.path.join(CACHE_ROOT, "filings", fname)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            try:
                r = _get(url)
                with open(path, "wb") as f:
                    f.write(r.content)
            except Exception as e:
                print(f"[sec] exhibit fetch failed {url}: {e}")
                continue
        out.append((path, url))
    return out
