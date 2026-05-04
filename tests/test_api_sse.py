import json
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from valura.main import app

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.asyncio
async def test_query_stream_portfolio_empty(monkeypatch):
    monkeypatch.setattr("valura.agents.portfolio_health.total_return_pct", lambda *a, **k: 1.0)
    u = json.loads((ROOT / "fixtures" / "users" / "user_004_empty.json").read_text())
    body = {
        "query": "How is my portfolio doing?",
        "session_id": "test-sess-1",
        "user": u,
    }
    lines: list[str] = []
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        async with ac.stream("POST", "/v1/query/stream", json=body, timeout=30) as r:
            assert r.status_code == 200
            async for line in r.aiter_lines():
                if line:
                    lines.append(line)
    text = "\n".join(lines)
    assert "event: metadata" in text
    assert "event: result" in text
    assert "event: done" in text or "error" in text
