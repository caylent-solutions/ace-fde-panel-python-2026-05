"""SQLAlchemy-backed repository for the Workflow model."""

from __future__ import annotations

import builtins

from sqlalchemy.orm import Session

from app.models.workflow import Workflow


class WorkflowRepository:
    """Concrete WorkflowRepository over a SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, entity_id: int) -> "Workflow | None":
        return self._session.query(Workflow).filter(Workflow.id == entity_id).first()

    def list(self) -> builtins.list[Workflow]:
        return self._session.query(Workflow).all()

    def create(self, entity: Workflow) -> Workflow:
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

    def list_for_user(self, user_id: int) -> builtins.list[Workflow]:
        return self._session.query(Workflow).filter(Workflow.user_id == user_id).all()
