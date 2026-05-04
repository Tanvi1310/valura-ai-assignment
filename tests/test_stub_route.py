import pytest

from valura.agents.stub import run_stub
from valura.models import ClassificationResult, ExtractedEntities


@pytest.mark.asyncio
async def test_stub_streams_without_crash():
    cls = ClassificationResult(
        intent="x",
        entities=ExtractedEntities(tickers=["MSFT"]),
        target_agent="market_research",
    )
    parts = []
    async for k, p in run_stub(cls):
        parts.append((k, p))
    assert any(k == "result" for k, _ in parts)
