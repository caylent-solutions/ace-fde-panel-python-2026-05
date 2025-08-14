from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine, SessionLocal
from app.models.user import User
from app.auth import hash_password

client = TestClient(app)


def test_login_happy_path():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    user = User(email="test@example.com", password_hash=hash_password("secret"))
    db.add(user)
    db.commit()
    db.close()

    resp = client.post("/login?email=test@example.com&password=secret")
    assert resp.status_code == 200
    assert "token" in resp.json()
