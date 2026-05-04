"""Market data access — yfinance (no hardcoded prices in source)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta

import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class ReturnSeries:
    symbol: str
    total_return_pct: float | None


def total_return_pct(symbol: str, start: date, end: date) -> float | None:
    try:
        t = yf.Ticker(symbol)
        hist = t.history(start=start, end=end, auto_adjust=True)
        if hist is None or hist.empty or len(hist) < 2:
            return None
        first = float(hist["Close"].iloc[0])
        last = float(hist["Close"].iloc[-1])
        if first <= 0:
            return None
        return (last / first - 1.0) * 100.0
    except Exception as exc:  # noqa: BLE001
        logger.debug("yfinance error for %s: %s", symbol, exc)
        return None


def default_range() -> tuple[date, date]:
    end = date.today()
    start = end - timedelta(days=365)
    return start, end


def benchmark_for_currency(base: str) -> str:
    if base.upper() in ("EUR", "GBP"):
        return "^STOXX50E"
    return "^GSPC"
