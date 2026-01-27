"""Tests for WorkflowRepository, including transactional rollback."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.workflow import Workflow
from app.repositories.workflows import WorkflowRepository


def test_create_and_get_workflow(session: Session) -> None:
    repo = WorkflowRepository(session)
    created = repo.create(
        Workflow(user_id=1, name="weekly-rollup", definition="{}")
    )
    assert created.id is not None

    fetched = repo.get(created.id)
    assert fetched is not None
    assert fetched.name == "weekly-rollup"
    assert fetched.user_id == 1


def test_list_returns_all_workflows(session: Session) -> None:
    repo = WorkflowRepository(session)
    repo.create(Workflow(user_id=1, name="a", definition="{}"))
    repo.create(Workflow(user_id=1, name="b", definition="{}"))

    rows = repo.list()
    assert len(rows) == 2
    assert {r.name for r in rows} == {"a", "b"}


def test_list_for_user_filters_by_user(session: Session) -> None:
    repo = WorkflowRepository(session)
    repo.create(Workflow(user_id=1, name="alice-1", definition="{}"))
    repo.create(Workflow(user_id=2, name="bob-1", definition="{}"))

    rows = repo.list_for_user(1)
    assert [r.name for r in rows] == ["alice-1"]


def test_delete_removes_workflow(session: Session) -> None:
    repo = WorkflowRepository(session)
    created = repo.create(Workflow(user_id=1, name="ephemeral", definition="{}"))

    assert repo.delete(created.id) is True
    assert repo.get(created.id) is None
    assert repo.delete(created.id) is False


def test_failed_create_rolls_back_session(session: Session) -> None:
    repo = WorkflowRepository(session)
    repo.create(Workflow(user_id=1, name="kept", definition="{}"))

    bad = Workflow(user_id=1, name=None, definition="{}")  # NOT NULL violation
    with pytest.raises(SQLAlchemyError):
        repo.create(bad)
    session.rollback()

    rows = repo.list()
    assert len(rows) == 1
    assert rows[0].name == "kept"
