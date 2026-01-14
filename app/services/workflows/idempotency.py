"""Idempotency key store for workflow run requests.

The in-memory implementation is a placeholder for development and
single-process deployments. The interface is shaped to swap to a
Redis-backed implementation without touching the runner — anything
that satisfies the protocol can be injected.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Callable, Protocol

from .models import WorkflowRun


@dataclass(frozen=True)
class _Entry:
    run: WorkflowRun
    expires_at: datetime


def _default_clock() -> datetime:
    return datetime.now(tz=timezone.utc)


class IdempotencyStore(Protocol):
    """Persistence surface for replay-safe workflow runs."""

    def get(self, key: str) -> WorkflowRun | None: ...

    def put(self, key: str, run: WorkflowRun) -> None: ...


class InMemoryIdempotencyStore:
    """TTL-backed in-memory store keyed by idempotency token.

    Thread-safe for concurrent runner invocations within a single
    process. Not suitable for multi-process deployments — those need
    a shared backend like Redis.
    """

    def __init__(
        self,
        ttl: timedelta,
        clock: Callable[[], datetime] = _default_clock,
    ) -> None:
        if ttl <= timedelta(0):
            raise ValueError("ttl must be positive")
        self._ttl = ttl
        self._clock = clock
        self._entries: dict[str, _Entry] = {}
        self._lock = Lock()

    def get(self, key: str) -> WorkflowRun | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if self._clock() >= entry.expires_at:
                del self._entries[key]
                return None
            return entry.run

    def put(self, key: str, run: WorkflowRun) -> None:
        with self._lock:
            self._entries[key] = _Entry(
                run=run,
                expires_at=self._clock() + self._ttl,
            )
