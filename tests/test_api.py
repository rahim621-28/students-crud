import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def make(**kw):
    body = {"name": "Test", "date_of_birth": "2004-01-01", "email": "t@example.com"}
    body.update(kw)
    return client.post("/students", json=body)


def test_create_and_get():
    r = make()
    assert r.status_code == 201
    sid = r.json()["id"]
    assert client.get(f"/students/{sid}").json()["name"] == "Test"


def test_list_and_filter():
    make(); make(name="Zed", email="z@example.com", date_of_birth="2006-02-02")
    assert len(client.get("/students").json()) == 2
    assert len(client.get("/students?born_after=2005-01-01").json()) == 1
    assert len(client.get("/students?name=zed").json()) == 1


def test_update():
    sid = make().json()["id"]
    r = client.patch(f"/students/{sid}", json={"course": "AI"})
    assert r.status_code == 200 and r.json()["course"] == "AI"


def test_delete():
    sid = make().json()["id"]
    assert client.delete(f"/students/{sid}").status_code == 204
    assert client.get(f"/students/{sid}").status_code == 404


def test_validation_and_errors():
    assert make(email="bad").status_code == 422
    assert client.post("/students", json={"name": "x", "date_of_birth": "2004-01-01"}).status_code == 422
    assert make().status_code == 201
    assert make().status_code == 409
    assert client.get("/students/999").status_code == 404
    assert client.delete("/students/999").status_code == 404
