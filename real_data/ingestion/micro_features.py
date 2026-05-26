"""Micro features + reaction_30d via yfinance."""
from __future__ import annotations
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import yfinance as yf

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache", "prices")
os.makedirs(CACHE_DIR, exist_ok=True)

SECTOR_ETFS = {
    # GICS sector -> ETF
    "Information Technology": "XLK",
    "Health Care": "XLV",
    "Financials": "XLF",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Communication Services": "XLC",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Materials": "XLB",
}

SPY = "SPY"


def _cache_prices(ticker: str, start: str = "2017-01-01") -> pd.DataFrame:
    path = os.path.join(CACHE_DIR, f"{ticker.replace('^','_').replace('-','_')}.csv")
    if os.path.exists(path):
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        if len(df) > 0:
            return df
    for attempt in range(3):
        try:
            df = yf.download(ticker, start=start,
                             end=datetime.now().strftime("%Y-%m-%d"),
                             progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if len(df) > 0:
                df.to_csv(path)
                return df
        except Exception as e:
            print(f"[yf] {ticker} attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)
    # write empty marker to avoid retry
    pd.DataFrame().to_csv(path)
    return pd.DataFrame()


def _window_metrics(prices: pd.Series, end_date: str, n_days: int, prefix: str):
    """Compute return, realized vol, drawdown over n_days ending at end_date."""
    if prices.empty:
        return None
    d = pd.to_datetime(end_date)
    window = prices.loc[:d].dropna()
    if len(window) < n_days:
        return None
    window = window.iloc[-n_days:]
    rets = window.pct_change().dropna()
    cumret = (window.iloc[-1] / window.iloc[0]) - 1
    realized_vol = float(rets.std() * np.sqrt(252))
    high = window.cummax()
    dd = ((window - high) / high).min()
    return {"return": float(cumret), "realized_vol": realized_vol,
            "drawdown_from_high": float(dd)}


def _forward_window(prices: pd.Series, start_date: str, n_days: int):
    """Forward window: returns/vol/drawdown over the n_days AFTER start_date."""
    if prices.empty:
        return None
    d = pd.to_datetime(start_date)
    window = prices.loc[d:].dropna()
    if len(window) < n_days + 1:
        return None
    window = window.iloc[:n_days + 1]
    rets = window.pct_change().dropna()
    cumret = (window.iloc[-1] / window.iloc[0]) - 1
    realized_vol = float(rets.std() * np.sqrt(252))
    high = window.cummax()
    dd = ((window - high) / high).min()
    # persistence: fraction of post-event days with same sign as cumret
    same_sign = float(((rets * np.sign(cumret)) > 0).mean())
    return {"return": float(cumret), "realized_vol": realized_vol,
            "max_drawdown": float(dd), "persistence": same_sign}


def micro_features_for(ticker: str, date: str, sector: str | None) -> dict | None:
    prices = _cache_prices(ticker)
    if prices.empty or "Close" not in prices.columns:
        return None
    p = prices["Close"]
    m60 = _window_metrics(p, date, 60, "60d")
    if m60 is None:
        return None
    # all-time high to date
    d = pd.to_datetime(date)
    history = p.loc[:d].dropna()
    if history.empty:
        return None
    dd_from_alltime_high = float((history.iloc[-1] - history.max()) / history.max())
    # sector return 60d
    sector_ret = None
    rel_strength = None
    sector_etf = SECTOR_ETFS.get(sector or "")
    if sector_etf:
        sp = _cache_prices(sector_etf)
        if not sp.empty and "Close" in sp.columns:
            sec_m60 = _window_metrics(sp["Close"], date, 60, "60d")
            if sec_m60 is not None:
                sector_ret = sec_m60["return"]
    # relative strength vs SPY: 60d return ranked vs SPY 60d return -> map to [0,1]
    spy = _cache_prices(SPY)
    if not spy.empty:
        spy_m60 = _window_metrics(spy["Close"], date, 60, "60d")
        if spy_m60 is not None and spy_m60["return"] != 0:
            # simple: 0.5 + 0.5 * sign(asset_ret - spy_ret) * min(1, |delta|/0.20)
            delta = m60["return"] - spy_m60["return"]
            rel_strength = float(np.clip(0.5 + 0.5 * delta / 0.20, 0.0, 1.0))
    return {
        "return_60d": m60["return"],
        "realized_vol_60d": m60["realized_vol"],
        "drawdown_from_high": dd_from_alltime_high,
        "sector_return_60d": sector_ret if sector_ret is not None else m60["return"] * 0.5,
        "relative_strength": rel_strength if rel_strength is not None else 0.5,
    }


def reaction_30d_for(ticker: str, date: str) -> dict | None:
    prices = _cache_prices(ticker)
    if prices.empty or "Close" not in prices.columns:
        return None
    return _forward_window(prices["Close"], date, 30)
