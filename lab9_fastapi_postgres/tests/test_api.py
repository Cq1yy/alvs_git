import os

import pytest
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
from fastapi.testclient import TestClient

# В тестах используем SQLite, чтобы они работали без внешней БД.

from app.main import app  # noqa: E402
from app.db import init_db  # noqa: E402


@pytest.fixture(autouse=True)
def _init() -> None:
    init_db()


def test_root_returns_html() -> None:
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert "ЛР №9" in r.text


def test_create_and_list_user() -> None:
    client = TestClient(app)

    r = client.post("/api/users", json={"username": "alice", "email": "alice@example.com"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "alice"

    r = client.get("/api/users")
    assert r.status_code == 200
    users = r.json()
    assert len(users) == 1
    assert users[0]["email"] == "alice@example.com"


def test_login_logging_and_auth() -> None:
    client = TestClient(app)

    r = client.post("/api/auth/login", json={"username": "bob", "password": "wrong"})
    assert r.status_code == 401

    r = client.post("/api/auth/login", json={"username": "bob", "password": "secret"})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
