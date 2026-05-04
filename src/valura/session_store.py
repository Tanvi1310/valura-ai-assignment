"""In-memory session memory (demo)."""

from __future__ import annotations

from collections import defaultdict, deque
from threading import RLock

from valura.models import ChatMessage

_MAX_TURNS = 20
_store: dict[str, deque[ChatMessage]] = defaultdict(lambda: deque(maxlen=_MAX_TURNS * 2))
_lock = RLock()


def append_message(session_id: str, message: ChatMessage) -> None:
    with _lock:
        _store[session_id].append(message)


def get_history(session_id: str) -> list[ChatMessage]:
    with _lock:
        return list(_store[session_id])
