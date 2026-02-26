"""Money value type with explicit currency.

Holding amounts as `Money(amount, currency)` rather than bare floats
makes the eventual multi-currency expansion a type-system change
rather than a hunt for arithmetic call sites. `Decimal` under the
hood keeps rounding deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


_CENT = Decimal("0.01")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError("amount must be a Decimal")
        if not self.currency:
            raise ValueError("currency must be a non-empty ISO 4217 code")

    @classmethod
    def usd(cls, amount: Decimal | int | str) -> "Money":
        return cls(amount=Decimal(amount), currency="USD")

    @classmethod
    def zero(cls, currency: str = "USD") -> "Money":
        return cls(amount=Decimal("0"), currency=currency)

    def _check_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"currency mismatch: {self.currency} vs {other.currency}"
            )

    def __add__(self, other: "Money") -> "Money":
        self._check_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._check_same_currency(other)
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __mul__(self, factor: Decimal | int) -> "Money":
        return Money(
            amount=self.amount * Decimal(factor),
            currency=self.currency,
        )

    def quantize_cents(self) -> "Money":
        rounded = self.amount.quantize(_CENT, rounding=ROUND_HALF_UP)
        return Money(amount=rounded, currency=self.currency)

    def __str__(self) -> str:
        rounded = self.amount.quantize(_CENT, rounding=ROUND_HALF_UP)
        return f"{rounded} {self.currency}"
