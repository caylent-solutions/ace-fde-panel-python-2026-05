"""Tests for the rehash-on-login migration."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.migrations import detect_legacy_hash, rehash_on_login
from app.auth.passwords import hash_password, is_legacy_hash
from app.db import Base
from app.models.user import User


def _legacy(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = factory()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_detect_legacy_hash_matches_is_legacy_hash() -> None:
    assert detect_legacy_hash(_legacy("x")) is True
    assert detect_legacy_hash(hash_password("x")) is False


def test_rehash_on_login_rewrites_legacy_hash_after_successful_verify(
    session: Session,
) -> None:
    user = User(email="alice@example.com", password_hash=_legacy("hunter2"))
    session.add(user)
    session.commit()

    rehashed = rehash_on_login(user, "hunter2", session)

    assert rehashed is True
    refreshed = session.query(User).filter(User.email == "alice@example.com").first()
    assert refreshed is not None
    assert is_legacy_hash(refreshed.password_hash) is False
    assert refreshed.password_hash.startswith(("$2a$", "$2b$"))


def test_rehash_on_login_is_noop_for_already_bcrypt_hash(session: Session) -> None:
    bcrypt_hash = hash_password("hunter2")
    user = User(email="bob@example.com", password_hash=bcrypt_hash)
    session.add(user)
    session.commit()

    rehashed = rehash_on_login(user, "hunter2", session)

    assert rehashed is False
    refreshed = session.query(User).filter(User.email == "bob@example.com").first()
    assert refreshed is not None
    assert refreshed.password_hash == bcrypt_hash


def test_rehash_on_login_skips_when_plaintext_does_not_match_legacy(
    session: Session,
) -> None:
    user = User(email="carol@example.com", password_hash=_legacy("real"))
    session.add(user)
    session.commit()

    rehashed = rehash_on_login(user, "wrong", session)

    assert rehashed is False
    refreshed = session.query(User).filter(User.email == "carol@example.com").first()
    assert refreshed is not None
    assert refreshed.password_hash == _legacy("real")
