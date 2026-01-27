"""Tests for RunRepository, including transactional rollback."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.run import Run
from app.repositories.runs import RunRepository


def test_create_and_get_run(session: Session) -> None:
    repo = RunRepository(session)
    created = repo.create(Run(workflow_id=1, status="pending", output=""))
    assert created.id is not None

    fetched = repo.get(created.id)
    assert fetched is not None
    assert fetched.workflow_id == 1
    assert fetched.status == "pending"


def test_list_for_workflow_filters_by_workflow(session: Session) -> None:
    repo = RunRepository(session)
    repo.create(Run(workflow_id=1, status="completed", output="ok"))
    repo.create(Run(workflow_id=2, status="completed", output="ok"))
    repo.create(Run(workflow_id=1, status="failed", output="err"))

    rows = repo.list_for_workflow(1)
    assert len(rows) == 2
    assert {r.status for r in rows} == {"completed", "failed"}


def test_delete_removes_run(session: Session) -> None:
    repo = RunRepository(session)
    created = repo.create(Run(workflow_id=1, status="pending", output=""))

    assert repo.delete(created.id) is True
    assert repo.get(created.id) is None
    assert repo.delete(created.id) is False


def test_failed_create_rolls_back_session(session: Session) -> None:
    repo = RunRepository(session)
    repo.create(Run(workflow_id=1, status="completed", output="kept"))

    bad = Run(workflow_id=None, status="pending", output="")  # NOT NULL violation
    with pytest.raises(SQLAlchemyError):
        repo.create(bad)
    session.rollback()

    rows = repo.list()
    assert len(rows) == 1
    assert rows[0].output == "kept"
