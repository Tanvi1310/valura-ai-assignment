import pytest

from valura.agents.portfolio_health import run_portfolio_health
from valura.classifier import heuristic_classify
from valura.models import ClassificationResult, ExtractedEntities, UserProfile


@pytest.mark.asyncio
async def test_empty_portfolio_build_message(monkeypatch, user_empty):
    monkeypatch.setattr(
        "valura.agents.portfolio_health.total_return_pct",
        lambda *a, **k: 5.0,
    )
    user = UserProfile(**user_empty)
    cls = heuristic_classify("How is my portfolio?", [])
    out = []
    async for ev in run_portfolio_health(user, cls):
        out.append(ev)
    kinds = [o[0] for o in out]
    assert "result" in kinds
    final = [p for k, p in out if k == "result"][0]
    struct = final["structured"]
    assert struct["concentration_risk"]["flag"] == "n/a"
    assert "disclaimer" in struct["disclaimer"].lower() or struct["disclaimer"]
    assert any("goal" in o["text"].lower() or "start" in o["text"].lower() for o in struct["observations"])


@pytest.mark.asyncio
async def test_weighted_portfolio_structure(monkeypatch):
    monkeypatch.setattr(
        "valura.agents.portfolio_health.total_return_pct",
        lambda symbol, start, end: {"NVDA": 10.0, "MSFT": 5.0, "^GSPC": 8.0}.get(symbol, 2.0),
    )
    user = UserProfile(
        user_id="u",
        base_currency="USD",
        holdings=[
            {"ticker": "NVDA", "weight_pct": 60.0},
            {"ticker": "MSFT", "weight_pct": 40.0},
        ],
    )
    cls = ClassificationResult(
        intent="t",
        entities=ExtractedEntities(),
        target_agent="portfolio_health",
    )
    chunks = []
    async for ev in run_portfolio_health(user, cls):
        chunks.append(ev)
    res = [p for k, p in chunks if k == "result"][0]["structured"]
    assert res["concentration_risk"]["top_position_pct"] == 60.0
    assert "benchmark_comparison" in res
