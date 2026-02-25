"""Tests for usage tracking and aggregation across windows."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.services.billing.usage import (
    InMemoryUsageBackend,
    UsageEvent,
    UsageTracker,
    UsageWindow,
)


WINDOW_START = datetime(2026, 2, 1, tzinfo=timezone.utc)
WINDOW_END = datetime(2026, 3, 1, tzinfo=timezone.utc)


def _window() -> UsageWindow:
    return UsageWindow(start=WINDOW_START, end=WINDOW_END)


def test_record_then_aggregate_sums_quantities_per_metric() -> None:
    tracker = UsageTracker()
    account = uuid4()
    tracker.record(account, "workflow_runs", 5, occurred_at=WINDOW_START + timedelta(days=1))
    tracker.record(account, "workflow_runs", 3, occurred_at=WINDOW_START + timedelta(days=2))
    tracker.record(account, "api_calls", 100, occurred_at=WINDOW_START + timedelta(hours=1))

    aggregates = tracker.aggregate(account, _window())
    by_metric = {a.metric: a.quantity for a in aggregates}

    assert by_metric == {"workflow_runs": 8, "api_calls": 100}
    assert all(a.account_id == account for a in aggregates)
    assert all(a.window == _window() for a in aggregates)


def test_event_at_exact_window_start_is_included() -> None:
    tracker = UsageTracker()
    account = uuid4()
    tracker.record(account, "api_calls", 1, occurred_at=WINDOW_START)

    aggregates = tracker.aggregate(account, _window())
    assert len(aggregates) == 1
    assert aggregates[0].quantity == 1


def test_event_at_exact_window_end_is_excluded() -> None:
    tracker = UsageTracker()
    account = uuid4()
    tracker.record(account, "api_calls", 1, occurred_at=WINDOW_END)

    aggregates = tracker.aggregate(account, _window())
    assert aggregates == []


def test_events_outside_window_are_excluded() -> None:
    tracker = UsageTracker()
    account = uuid4()
    tracker.record(account, "api_calls", 1, occurred_at=WINDOW_START - timedelta(seconds=1))
    tracker.record(account, "api_calls", 1, occurred_at=WINDOW_END + timedelta(seconds=1))
    tracker.record(account, "api_calls", 5, occurred_at=WINDOW_START + timedelta(days=15))

    aggregates = tracker.aggregate(account, _window())
    assert [a.quantity for a in aggregates] == [5]


def test_aggregation_isolated_per_account() -> None:
    tracker = UsageTracker()
    account_a = uuid4()
    account_b = uuid4()
    tracker.record(account_a, "api_calls", 10, occurred_at=WINDOW_START + timedelta(days=1))
    tracker.record(account_b, "api_calls", 99, occurred_at=WINDOW_START + timedelta(days=1))

    aggregates_a = tracker.aggregate(account_a, _window())
    aggregates_b = tracker.aggregate(account_b, _window())
    assert [a.quantity for a in aggregates_a] == [10]
    assert [a.quantity for a in aggregates_b] == [99]


def test_record_rejects_negative_quantity() -> None:
    tracker = UsageTracker()
    with pytest.raises(ValueError):
        tracker.record(uuid4(), "api_calls", -1)


def test_zero_quantity_event_is_recorded_but_does_not_affect_total() -> None:
    tracker = UsageTracker()
    account = uuid4()
    tracker.record(account, "api_calls", 0, occurred_at=WINDOW_START + timedelta(days=1))
    tracker.record(account, "api_calls", 4, occurred_at=WINDOW_START + timedelta(days=2))

    aggregates = tracker.aggregate(account, _window())
    assert [a.quantity for a in aggregates] == [4]


def test_custom_backend_is_used_when_provided() -> None:
    backend = InMemoryUsageBackend()
    tracker = UsageTracker(backend=backend)
    account = uuid4()
    tracker.record(account, "metric", 7, occurred_at=WINDOW_START + timedelta(days=1))

    direct = backend.events_for(account, _window())
    assert len(direct) == 1
    assert isinstance(direct[0], UsageEvent)
    assert direct[0].quantity == 7
