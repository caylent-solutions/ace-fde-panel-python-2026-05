from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_slack_hook_ok():
    resp = client.post("/hooks/slack", json={"type": "event_callback", "event": {}})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
