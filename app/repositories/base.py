"""Base repository protocol.

The protocol exists so the service layer can depend on a thin
abstraction rather than concrete SQLAlchemy classes — tests can
substitute in-memory fakes without touching production code.
"""

from __future__ import annotations

from typing import Protocol, TypeVar

T = TypeVar("T")


class Repository(Protocol[T]):
    """Common surface for per-entity repositories."""

    def get(self, entity_id: int) -> T | None: ...

    def list(self) -> list[T]: ...

    def create(self, entity: T) -> T: ...

    def delete(self, entity_id: int) -> bool: ...
