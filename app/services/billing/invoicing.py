"""Invoice generation from usage aggregates.

Produces a monthly invoice using the Money type. The line-item
shape here is what the eventual PDF renderer will consume — keeping
the data layer stable while the rendering side is still pending.
"""

from __future__ import annotations

import builtins
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from .money import Money
from .usage import UsageAggregate, UsageWindow


class PriceTable(BaseModel):
    """Per-metric unit prices in a single currency."""

    model_config = ConfigDict(frozen=True)

    currency: str = "USD"
    unit_prices: dict[str, Decimal] = Field(default_factory=dict)

    def price_for(self, metric: str) -> Decimal:
        if metric not in self.unit_prices:
            raise KeyError(f"no unit price configured for metric: {metric}")
        return self.unit_prices[metric]


class InvoiceLineItem(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    metric: str
    quantity: int
    unit_price: Money
    subtotal: Money


class Invoice(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    id: UUID
    account_id: UUID
    window: UsageWindow
    line_items: tuple[InvoiceLineItem, ...]
    total: Money
    issued_at: datetime


def generate_invoice(
    account_id: UUID,
    window: UsageWindow,
    aggregates: builtins.list[UsageAggregate],
    prices: PriceTable,
    issued_at: datetime | None = None,
) -> Invoice:
    line_items: builtins.list[InvoiceLineItem] = []
    running_total = Money.zero(currency=prices.currency)
    for aggregate in aggregates:
        unit_price = Money(
            amount=prices.price_for(aggregate.metric),
            currency=prices.currency,
        )
        subtotal = (unit_price * aggregate.quantity).quantize_cents()
        line_items.append(
            InvoiceLineItem(
                metric=aggregate.metric,
                quantity=aggregate.quantity,
                unit_price=unit_price,
                subtotal=subtotal,
            )
        )
        running_total = running_total + subtotal
    return Invoice(
        id=uuid4(),
        account_id=account_id,
        window=window,
        line_items=tuple(line_items),
        total=running_total.quantize_cents(),
        issued_at=issued_at or datetime.now(tz=timezone.utc),
    )
