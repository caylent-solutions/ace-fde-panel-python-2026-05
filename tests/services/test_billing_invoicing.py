"""Tests for invoice generation, focused on rounding edge cases."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.services.billing.invoicing import PriceTable, generate_invoice
from app.services.billing.money import Money
from app.services.billing.usage import UsageAggregate, UsageWindow


def _window() -> UsageWindow:
    return UsageWindow(
        start=datetime(2026, 2, 1, tzinfo=timezone.utc),
        end=datetime(2026, 3, 1, tzinfo=timezone.utc),
    )


def _aggregate(account_id, metric: str, quantity: int) -> UsageAggregate:
    return UsageAggregate(
        account_id=account_id,
        metric=metric,
        window=_window(),
        quantity=quantity,
    )


def test_invoice_with_no_aggregates_has_zero_total() -> None:
    account = uuid4()
    prices = PriceTable(unit_prices={"api_calls": Decimal("0.01")})
    invoice = generate_invoice(account, _window(), [], prices)

    assert invoice.line_items == ()
    assert invoice.total == Money(amount=Decimal("0.00"), currency="USD")


def test_subtotal_rounds_half_up_to_cents() -> None:
    account = uuid4()
    prices = PriceTable(unit_prices={"api_calls": Decimal("0.005")})
    invoice = generate_invoice(
        account, _window(), [_aggregate(account, "api_calls", 1)], prices
    )

    assert invoice.line_items[0].subtotal == Money(amount=Decimal("0.01"), currency="USD")
    assert invoice.total == Money(amount=Decimal("0.01"), currency="USD")


def test_subtotal_rounds_half_up_negative_fraction() -> None:
    account = uuid4()
    prices = PriceTable(unit_prices={"api_calls": Decimal("0.0049")})
    invoice = generate_invoice(
        account, _window(), [_aggregate(account, "api_calls", 1)], prices
    )

    assert invoice.line_items[0].subtotal == Money(amount=Decimal("0.00"), currency="USD")


def test_total_sums_rounded_subtotals_per_line() -> None:
    account = uuid4()
    prices = PriceTable(
        unit_prices={
            "metric_a": Decimal("0.0125"),
            "metric_b": Decimal("0.001"),
        }
    )
    aggregates = [
        _aggregate(account, "metric_a", 4),
        _aggregate(account, "metric_b", 7),
    ]
    invoice = generate_invoice(account, _window(), aggregates, prices)

    by_metric = {li.metric: li.subtotal for li in invoice.line_items}
    assert by_metric["metric_a"] == Money(amount=Decimal("0.05"), currency="USD")
    assert by_metric["metric_b"] == Money(amount=Decimal("0.01"), currency="USD")
    assert invoice.total == Money(amount=Decimal("0.06"), currency="USD")


def test_unknown_metric_raises_keyerror() -> None:
    account = uuid4()
    prices = PriceTable(unit_prices={"api_calls": Decimal("0.01")})
    with pytest.raises(KeyError):
        generate_invoice(
            account,
            _window(),
            [_aggregate(account, "unmapped_metric", 1)],
            prices,
        )


def test_high_quantity_keeps_decimal_precision() -> None:
    account = uuid4()
    prices = PriceTable(unit_prices={"api_calls": Decimal("0.000123")})
    invoice = generate_invoice(
        account, _window(), [_aggregate(account, "api_calls", 1_000_000)], prices
    )

    assert invoice.line_items[0].subtotal == Money(amount=Decimal("123.00"), currency="USD")
    assert invoice.total == Money(amount=Decimal("123.00"), currency="USD")


def test_zero_quantity_aggregate_yields_zero_subtotal() -> None:
    account = uuid4()
    prices = PriceTable(unit_prices={"api_calls": Decimal("0.01")})
    invoice = generate_invoice(
        account, _window(), [_aggregate(account, "api_calls", 0)], prices
    )

    assert invoice.line_items[0].subtotal == Money(amount=Decimal("0.00"), currency="USD")
    assert invoice.total == Money(amount=Decimal("0.00"), currency="USD")
