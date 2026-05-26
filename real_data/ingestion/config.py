"""Config + secrets. Reads env or local config; do NOT commit secrets."""
from __future__ import annotations
import os

# Prefer env, fallback to baked-in (user-provided in conversation).
FRED_API_KEY = os.environ.get("FRED_API_KEY", "9962415d3d5b7a34501e6d3458bf9acb")

SEC_USER_AGENT = os.environ.get(
    "SEC_USER_AGENT",
    "Roberto Pasquale robertopasquale94@gmail.com",
)

# SEC EDGAR policy: max 10 req/sec
SEC_RATE_LIMIT_PER_SEC = 8  # conservative
