from fastapi import APIRouter
from app.db import SessionLocal

router = APIRouter(prefix="/admin")


@router.get("/audit_log")
def audit_log(q: str = ""):
    db = SessionLocal()
    results = db.execute(f"SELECT id, event_type, user_id, payload, created_at FROM audit_logs WHERE event_type LIKE '%{q}%'").fetchall()
    return [dict(r._mapping) for r in results]
