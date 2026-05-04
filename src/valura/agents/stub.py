"""Stub responses for agents not implemented in this build."""

from __future__ import annotations

from typing import Any, AsyncIterator

from valura.models import ClassificationResult, StubAgentPayload


async def run_stub(classification: ClassificationResult) -> AsyncIterator[tuple[str, dict[str, Any]]]:
    payload = StubAgentPayload(
        intent=classification.intent,
        entities=classification.entities,
        target_agent=classification.target_agent,
        message=(
            f"The '{classification.target_agent}' specialist is not implemented in this demo build. "
            "Routing and classification succeeded; extend `src/valura/agents/` to add behavior."
        ),
    )
    text = payload.message
    yield ("delta", {"text": text})
    yield ("result", {"stub": payload.model_dump(), "narrative": text})
