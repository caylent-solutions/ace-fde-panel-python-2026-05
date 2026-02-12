"""Tests for the api_key_auth FastAPI dependency."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.api_key import api_key_auth, get_db
from app.db import Base
from app.models.api_key import ApiKey
from app.models.run import Run as _Run
from app.models.workflow import Workflow as _Workflow

_REGISTERED = (_Run, _Workflow)


@pytest.fixture
def session_factory() -> Iterator[sessionmaker[Session]]:
    assert _REGISTERED  # keep model imports live for table registration
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    seed_db = factory()
    seed_db.add(ApiKey(key="ak_valid_xyz", user_id=1, name="ci"))
    seed_db.commit()
    seed_db.close()
    try:
        yield factory
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> Iterator[TestClient]:
    test_app = FastAPI()

    def _override_db() -> Iterator[Session]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    @test_app.get("/protected")
    def protected(caller: ApiKey = Depends(api_key_auth)) -> dict[str, str]:
        return {"caller_key_name": caller.name}

    test_app.dependency_overrides[get_db] = _override_db
    yield TestClient(test_app)


def test_valid_key_grants_access(client: TestClient) -> None:
    resp = client.get("/protected", headers={"X-API-Key": "ak_valid_xyz"})
    assert resp.status_code == 200
    assert resp.json() == {"caller_key_name": "ci"}


def test_invalid_key_is_rejected(client: TestClient) -> None:
    resp = client.get("/protected", headers={"X-API-Key": "ak_does_not_exist"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "invalid api key"


def test_missing_key_is_rejected(client: TestClient) -> None:
    resp = client.get("/protected")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "missing api key"


def test_empty_key_header_is_rejected(client: TestClient) -> None:
    resp = client.get("/protected", headers={"X-API-Key": "   "})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "missing api key"


def test_api_key_model_has_requests_per_minute_field() -> None:
    key = ApiKey(key="ak_check", user_id=1, name="probe", requests_per_minute=60)
    assert key.requests_per_minute == 60

    default_key = ApiKey(key="ak_default", user_id=1, name="probe2")
    assert default_key.requests_per_minute is None
