"""Tests for APIKeyRepository, including transactional rollback."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.api_key import ApiKey
from app.repositories.api_keys import APIKeyRepository


def test_create_and_get_by_key(session: Session) -> None:
    repo = APIKeyRepository(session)
    created = repo.create(ApiKey(key="ak_abc123", user_id=1, name="ci"))
    assert created.id is not None

    fetched = repo.get_by_key("ak_abc123")
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "ci"


def test_list_for_user_filters_by_user(session: Session) -> None:
    repo = APIKeyRepository(session)
    repo.create(ApiKey(key="ak_alice_1", user_id=1, name="laptop"))
    repo.create(ApiKey(key="ak_alice_2", user_id=1, name="ci"))
    repo.create(ApiKey(key="ak_bob_1", user_id=2, name="laptop"))

    rows = repo.list_for_user(1)
    assert {r.key for r in rows} == {"ak_alice_1", "ak_alice_2"}


def test_unique_key_violation_rolls_back(session: Session) -> None:
    repo = APIKeyRepository(session)
    repo.create(ApiKey(key="ak_dup", user_id=1, name="first"))

    with pytest.raises(SQLAlchemyError):
        repo.create(ApiKey(key="ak_dup", user_id=2, name="duplicate"))
    session.rollback()

    rows = repo.list()
    assert len(rows) == 1
    assert rows[0].name == "first"


def test_delete_removes_key(session: Session) -> None:
    repo = APIKeyRepository(session)
    created = repo.create(ApiKey(key="ak_delete_me", user_id=1, name="temp"))

    assert repo.delete(created.id) is True
    assert repo.get(created.id) is None
    assert repo.delete(created.id) is False
