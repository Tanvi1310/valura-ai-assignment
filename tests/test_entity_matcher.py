"""Normalization rules documented in fixtures/README.md — subset matcher."""

from valura.entities import entities_subset, normalize_ticker


def test_ticker_normalization():
    assert normalize_ticker("ASML.AS") == normalize_ticker("ASML")
    assert normalize_ticker("aapl") == normalize_ticker("AAPL.US")


def test_numeric_tolerance():
    actual = {"tickers": [], "topics": [], "sectors": [], "amount": 103.0, "rate": None, "period_years": None}
    expected = {"tickers": [], "topics": [], "sectors": [], "amount": 100.0, "rate": None, "period_years": None}
    ok, _ = entities_subset(actual, expected)
    assert ok


def test_topic_subset():
    actual = {"tickers": [], "topics": ["liquidity", "extra"], "sectors": [], "amount": None, "rate": None, "period_years": None}
    expected = {"tickers": [], "topics": ["liquidity"], "sectors": [], "amount": None, "rate": None, "period_years": None}
    ok, _ = entities_subset(actual, expected)
    assert ok
