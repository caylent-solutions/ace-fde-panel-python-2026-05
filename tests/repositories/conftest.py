"""Shared SQLAlchemy fixture for repository tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models.api_key import ApiKey
from app.models.run import Run
from app.models.workflow import Workflow

_REGISTERED_MODELS = (ApiKey, Run, Workflow)


@pytest.fixture
def session() -> Iterator[Session]:
    assert _REGISTERED_MODELS  # keep imports live for table registration
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
