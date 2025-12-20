from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine, SessionLocal
from app.models.run import Run

client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.query(Run).delete()
    db.add(Run(workflow_id=1, status="completed", output="done"))
    db.commit()
    db.close()


def test_list_runs():
    resp = client.get("/runs")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["status"] == "completed"


def test_get_run_detail():
    db = SessionLocal()
    run = db.query(Run).first()
    run_id = run.id
    db.close()

    resp = client.get(f"/runs/{run_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == run_id
    assert data["output"] == "done"


def test_get_run_steps():
    db = SessionLocal()
    run = db.query(Run).first()
    run_id = run.id
    db.close()

    resp = client.get(f"/runs/{run_id}/steps")
    assert resp.status_code == 200
    data = resp.json()
    assert data["run_id"] == run_id
    assert "steps" in data
