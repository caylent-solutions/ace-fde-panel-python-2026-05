"""API key authentication dependency.

Validates an `X-API-Key` header against the api_keys table via the
APIKeyRepository. Designed to be the single shared dependency for
all protected routes so adding rate limiting, scope checks, or
audit logging in a follow-up touches one place.
"""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.api_key import ApiKey
from app.repositories.api_keys import APIKeyRepository


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def api_key_auth(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> ApiKey:
    if x_api_key is None or not x_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing api key",
        )
    repo = APIKeyRepository(db)
    key = repo.get_by_key(x_api_key)
    if key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid api key",
        )
    # TODO: rate limiting
    return key
