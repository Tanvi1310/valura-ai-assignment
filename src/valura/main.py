"""FastAPI app — SSE-only API surface."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from valura.models import QueryRequest
from valura.pipeline import run_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Valura AI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/query/stream")
async def query_stream(req: QueryRequest) -> EventSourceResponse:
    """Run full pipeline; response is always text/event-stream (SSE)."""

    async def event_source() -> AsyncIterator[dict[str, str | None]]:
        try:
            async for item in run_pipeline(req):
                ev = item.get("event", "message")
                data = item.get("data", "")
                yield {"event": str(ev), "data": str(data), "id": None, "retry": None}
        except Exception as exc:  # noqa: BLE001
            import json

            logger.exception("pipeline error: %s", exc)
            yield {
                "event": "error",
                "data": json.dumps(
                    {"code": "internal_error", "message": "An unexpected error occurred during processing."}
                ),
            }

    return EventSourceResponse(event_source())
