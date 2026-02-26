"""Usage tracking for per-account metering.

A single tracker funnels every usage event so the eventual
per-account aggregation pipeline has one extension point. The
in-memory backend is the default; production deployments swap
in a persistent store via the protocol.
"""

from __future__ import annotations

import builtins
from collections import defaultdict
from datetime import datetime, timezone
from threading import Lock
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UsageEvent(BaseModel):
    """A single recorded unit of usage."""

    model_config = ConfigDict(frozen=True)

    account_id: UUID
    metric: str
    quantity: int = Field(ge=0)
    occurred_at: datetime


class UsageWindow(BaseModel):
    """Half-open billing window [start, end)."""

    model_config = ConfigDict(frozen=True)

    start: datetime
    end: datetime


class UsageAggregate(BaseModel):
    """Total quantity for a (metric) within a billing window."""

    model_config = ConfigDict(frozen=True)

    account_id: UUID
    metric: str
    window: UsageWindow
    quantity: int


class UsageBackend(Protocol):
    def record(self, event: UsageEvent) -> None: ...

    def events_for(
        self,
        account_id: UUID,
        window: UsageWindow,
    ) -> builtins.list[UsageEvent]: ...


class InMemoryUsageBackend:
    """Thread-safe in-memory storage for usage events."""

    def __init__(self) -> None:
        self._events: dict[UUID, builtins.list[UsageEvent]] = defaultdict(list)
        self._lock = Lock()

    def record(self, event: UsageEvent) -> None:
        with self._lock:
            self._events[event.account_id].append(event)

    def events_for(
        self,
        account_id: UUID,
        window: UsageWindow,
    ) -> builtins.list[UsageEvent]:
        with self._lock:
            return [
                e
                for e in self._events.get(account_id, [])
                if window.start <= e.occurred_at < window.end
            ]


class UsageTracker:
    """Records usage events and aggregates by metric within a window."""

    def __init__(self, backend: UsageBackend | None = None) -> None:
        self._backend = backend if backend is not None else InMemoryUsageBackend()

    def record(
        self,
        account_id: UUID,
        metric: str,
        quantity: int,
        occurred_at: datetime | None = None,
    ) -> UsageEvent:
        if quantity < 0:
            raise ValueError("quantity must be non-negative")
        event = UsageEvent(
            account_id=account_id,
            metric=metric,
            quantity=quantity,
            occurred_at=occurred_at or datetime.now(tz=timezone.utc),
        )
        self._backend.record(event)
        return event

    def aggregate(
        self,
        account_id: UUID,
        window: UsageWindow,
    ) -> builtins.list[UsageAggregate]:
        events = self._backend.events_for(account_id, window)
        totals: dict[str, int] = defaultdict(int)
        for event in events:
            totals[event.metric] += event.quantity
        return [
            UsageAggregate(
                account_id=account_id,
                metric=metric,
                window=window,
                quantity=quantity,
            )
            for metric, quantity in sorted(totals.items())
        ]
