"""End-to-end pipeline: safety → classify → route → stream."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from valura.agents.portfolio_health import run_portfolio_health
from valura.agents.stub import run_stub
from valura.classifier import classify_intent
from valura.config import settings
from valura.models import ChatMessage, QueryRequest
from valura.safety import evaluate_safety
from valura.session_store import append_message, get_history

logger = logging.getLogger(__name__)


async def run_pipeline(req: QueryRequest) -> AsyncIterator[dict[str, Any]]:
    """Yield SSE-shaped dicts: {event: str, data: str JSON}."""
    t_budget = min(20.0, settings.pipeline_timeout_seconds)

    history = get_history(req.session_id)
    append_message(req.session_id, ChatMessage(role="user", content=req.query))

    safety = evaluate_safety(req.query)
    if safety.blocked:
        yield {
            "event": "metadata",
            "data": json.dumps(
                {
                    "safety": {"blocked": True, "category": safety.category, "message": safety.message},
                    "classification": None,
                }
            ),
        }
        yield {
            "event": "error",
            "data": json.dumps(
                {"code": "safety_block", "message": safety.message, "category": safety.category}
            ),
        }
        return

    try:
        classification = await asyncio.wait_for(
            classify_intent(req.query, history),
            timeout=t_budget,
        )
    except asyncio.TimeoutError:
        yield {
            "event": "error",
            "data": json.dumps(
                {"code": "timeout", "message": "Classification timed out; retry with a shorter prompt."}
            ),
        }
        return

    meta = {
        "safety": {"blocked": False},
        "classification": {
            "intent": classification.intent,
            "target_agent": classification.target_agent,
            "entities": classification.entities.model_dump(),
            "safety_verdict": classification.safety_verdict,
        },
    }
    yield {"event": "metadata", "data": json.dumps(meta)}

    agent = classification.target_agent
    if agent == "portfolio_health":
        agen = run_portfolio_health(req.user, classification)
    else:
        agen = run_stub(classification)

    async for kind, payload in agen:
        if kind == "delta":
            yield {"event": "chunk", "data": json.dumps({"text": payload["text"]})}
        elif kind == "result":
            yield {"event": "result", "data": json.dumps(payload)}
            narrative = payload.get("narrative", "")
            append_message(req.session_id, ChatMessage(role="assistant", content=narrative[:8000]))
            yield {"event": "done", "data": json.dumps({"ok": True})}
