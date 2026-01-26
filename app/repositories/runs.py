"""SQLAlchemy-backed repository for the Run model."""

from __future__ import annotations

import builtins

from sqlalchemy.orm import Session

from app.models.run import Run


class RunRepository:
    """Concrete RunRepository over a SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, entity_id: int) -> "Run | None":
        return self._session.query(Run).filter(Run.id == entity_id).first()

    def list(self) -> builtins.list[Run]:
        return self._session.query(Run).all()

    def create(self, entity: Run) -> Run:
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

    def list_for_workflow(self, workflow_id: int) -> builtins.list[Run]:
        return self._session.query(Run).filter(Run.workflow_id == workflow_id).all()
