import os

# main.py가 import 시점에 DATABASE_URL을 읽고 DB에 연결하므로, import 전에 테스트용 SQLite로 지정
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from main import app, BASE, engine

client = TestClient(app)


def setup_module(module):
    # 매 테스트 실행마다 깨끗한 테이블에서 시작
    BASE.metadata.drop_all(bind=engine)
    BASE.metadata.create_all(bind=engine)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_user():
    r = client.post("/users", json={"name": "kong", "email": "kong@test.com"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "kong"
    assert body["email"] == "kong@test.com"
    assert "id" in body


def test_duplicate_email_rejected():
    r = client.post("/users", json={"name": "other", "email": "kong@test.com"})
    assert r.status_code == 400


def test_get_user():
    created = client.post("/users", json={"name": "lee", "email": "lee@test.com"}).json()
    r = client.get(f"/users/{created['id']}")
    assert r.status_code == 200
    assert r.json()["email"] == "lee@test.com"


def test_get_missing_user():
    r = client.get("/users/99999")
    assert r.status_code == 404


def test_update_user():
    created = client.post("/users", json={"name": "park", "email": "park@test.com"}).json()
    r = client.put(f"/users/{created['id']}", json={"name": "park2", "email": "park2@test.com"})
    assert r.status_code == 200
    assert r.json()["name"] == "park2"


def test_delete_user():
    created = client.post("/users", json={"name": "choi", "email": "choi@test.com"}).json()
    r = client.delete(f"/users/{created['id']}")
    assert r.status_code == 204
    assert client.get(f"/users/{created['id']}").status_code == 404
