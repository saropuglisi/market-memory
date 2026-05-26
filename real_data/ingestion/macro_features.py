"""Macro features alla data dell'evento.
- VIX (FRED VIXCLS)
- yield_10y (FRED DGS10)
- yield_curve_slope = DGS10 - DGS2 (FRED)
- credit_spread (FRED BAMLH0A0HYM2 — HY OAS)
- dxy (yfinance DX-Y.NYB)
Tutte forward-fill al precedente trading day se mancanti.
"""
from __future__ import annotations
import os
import ssl
import pandas as pd
from datetime import datetime, timedelta

import certifi
# Force SSL to use certifi bundle for libraries that use urllib (fredapi)
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

from fredapi import Fred
import yfinance as yf

from .config import FRED_API_KEY

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache", "fred")
os.makedirs(CACHE_DIR, exist_ok=True)

_FRED_SERIES = {
    "vix": "VIXCLS",
    "yield_10y": "DGS10",
    "yield_2y": "DGS2",
    # BAMLH0A0HYM2 (HY OAS) ICE-licensed: FRED returns only ~2y window. Use BAA10Y
    # (Moody's Baa - 10y Treasury, free daily from 1986) as credit-spread proxy.
    "credit_spread": "BAA10Y",
}

_fred = Fred(api_key=FRED_API_KEY)
_cache: dict[str, pd.Series] = {}


def _load_fred(series_id: str) -> pd.Series:
    if series_id in _cache:
        return _cache[series_id]
    path = os.path.join(CACHE_DIR, f"{series_id}.csv")
    if os.path.exists(path):
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        s = df["value"]
    else:
        s = _fred.get_series(series_id, observation_start="2017-01-01")
        s.name = "value"
        s.to_frame().to_csv(path)
    s.index = pd.to_datetime(s.index)
    s = s.sort_index()
    _cache[series_id] = s
    return s


def _load_dxy() -> pd.Series:
    """DXY via yfinance, cached on disk."""
    path = os.path.join(CACHE_DIR, "dxy_yf.csv")
    if "dxy" in _cache:
        return _cache["dxy"]
    if os.path.exists(path):
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        s = df["Close"]
    else:
        df = yf.download("DX-Y.NYB", start="2017-01-01", end=datetime.now().strftime("%Y-%m-%d"),
                         progress=False, auto_adjust=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.to_csv(path)
        s = df["Close"]
    s.index = pd.to_datetime(s.index)
    s = s.sort_index()
    _cache["dxy"] = s
    return s


def value_on_or_before(s: pd.Series, date: str) -> float | None:
    d = pd.to_datetime(date)
    window = s.loc[:d].dropna()
    if window.empty:
        return None
    return float(window.iloc[-1])


def macro_features_for(date: str) -> dict:
    """Return dict matching MACRO_KEYS schema, or fill with None on missing."""
    out = {}
    vix = value_on_or_before(_load_fred(_FRED_SERIES["vix"]), date)
    y10 = value_on_or_before(_load_fred(_FRED_SERIES["yield_10y"]), date)
    y2 = value_on_or_before(_load_fred(_FRED_SERIES["yield_2y"]), date)
    cs = value_on_or_before(_load_fred(_FRED_SERIES["credit_spread"]), date)
    dxy = value_on_or_before(_load_dxy(), date)
    out["vix"] = vix
    out["yield_10y"] = y10
    out["yield_curve_slope"] = (y10 - y2) if (y10 is not None and y2 is not None) else None
    out["credit_spread"] = cs
    out["dxy"] = dxy
    return out
