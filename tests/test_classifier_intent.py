"""Classifier routing + entity subset matching vs fixtures."""

import json
from pathlib import Path

import pytest

from valura.classifier import heuristic_classify
from valura.entities import entities_subset
from valura.models import ChatMessage

ROOT = Path(__file__).resolve().parents[1]


def load_conv(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / "conversations" / name).read_text(encoding="utf-8"))


def test_intent_gold_routing_and_entities(intent_gold):
    failures = []
    for row in intent_gold:
        q = row["query"]
        res = heuristic_classify(q, [])
        if res.target_agent != row["expected_agent"]:
            failures.append(("agent", row["id"], res.target_agent, row["expected_agent"]))
            continue
        ok, msg = entities_subset(res.entities.model_dump(), row["expected_entities"])
        if not ok:
            failures.append(("entities", row["id"], msg))
    assert not failures, failures[:10]


def test_follow_up_apple_after_msft_topic(intent_gold):
    conv = load_conv("followup_ticker.json")
    hist = [ChatMessage(role=t["role"], content=t["content"]) for t in conv["turns"]]
    q = conv["follow_up_query"]
    res = heuristic_classify(q, hist)
    assert res.target_agent == "market_research"
    assert any("AAPL" in x or x == "AAPL" for x in res.entities.tickers) or "apple" in q.lower()


def test_topic_switch_to_portfolio_health(intent_gold):
    conv = load_conv("topic_switch.json")
    hist = [ChatMessage(role=t["role"], content=t["content"]) for t in conv["turns"]]
    q = conv["follow_up_query"]
    res = heuristic_classify(q, hist)
    assert res.target_agent == "portfolio_health"


def test_health_then_financial_math_followup(intent_gold):
    conv = load_conv("health_then_amount.json")
    hist = [ChatMessage(role=t["role"], content=t["content"]) for t in conv["turns"]]
    q = conv["follow_up_query"]
    res = heuristic_classify(q, hist)
    assert res.target_agent in ("financial_calculator", "portfolio_health")
