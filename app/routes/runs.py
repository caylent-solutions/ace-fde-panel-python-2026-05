from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.run import Run

runs_router = APIRouter(prefix="/runs", tags=["runs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@runs_router.get("")
def list_runs(db: Session = Depends(get_db)) -> list[dict]:
    runs = db.query(Run).all()
    return [{"id": r.id, "workflow_id": r.workflow_id, "status": r.status} for r in runs]


@runs_router.get("/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)) -> dict:
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return {"id": run.id, "workflow_id": run.workflow_id, "status": run.status, "output": run.output}


@runs_router.get("/{run_id}/steps")
def get_run_steps(run_id: int, db: Session = Depends(get_db)) -> dict:
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return {"run_id": run_id, "steps": []}
