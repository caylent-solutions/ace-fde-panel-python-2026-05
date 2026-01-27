"""SQLAlchemy-backed repository for the ApiKey model."""

from __future__ import annotations

import builtins

from sqlalchemy.orm import Session

from app.models.api_key import ApiKey


class APIKeyRepository:
    """Concrete APIKeyRepository over a SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, entity_id: int) -> "ApiKey | None":
        return self._session.query(ApiKey).filter(ApiKey.id == entity_id).first()

    def list(self) -> builtins.list[ApiKey]:
        return self._session.query(ApiKey).all()

    def create(self, entity: ApiKey) -> ApiKey:
        self._session.add(entity)
        self._session.commit()
        self._session.refresh(entity)
        return entity

    def delete(self, entity_id: int) -> bool:
        existing = self.get(entity_id)
        if existing is None:
            return False
        self._session.delete(existing)
        self._session.commit()
        return True

    def get_by_key(self, key: str) -> "ApiKey | None":
        return self._session.query(ApiKey).filter(ApiKey.key == key).first()

    def list_for_user(self, user_id: int) -> builtins.list[ApiKey]:
        return self._session.query(ApiKey).filter(ApiKey.user_id == user_id).all()
