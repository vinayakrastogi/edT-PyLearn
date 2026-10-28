"""API tests with a fake logged-in user (no database needed for these routes)."""
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core.deps import get_current_user
from app.main import app

STUDENT = SimpleNamespace(id=1, role="student", email="s@example.com", full_name="Stu")
FACULTY = SimpleNamespace(id=2, role="faculty", email="f@example.com", full_name="Fac")


@pytest.fixture
def client():
    app.dependency_overrides.clear()
    yield TestClient(app)
    app.dependency_overrides.clear()


def login_as(user):
    app.dependency_overrides[get_current_user] = lambda: user


def test_modules_list_has_full_curriculum(client):
    modules = client.get("/api/modules").json()
    real = [m for m in modules if not m["is_generative"]]
    assert len(real) == 10
    assert all(m["doc_count"] >= 7 for m in real)
    assert all(m["problem_count"] >= 8 for m in real)


def test_doc_returns_markdown_not_html(client):
    doc = client.get("/api/modules/module-1-introduction-to-python/docs/01-getting-started-with-python").json()
    assert doc["content_md"].startswith("# Getting Started")
    assert "content_html" not in doc
    assert doc["read_minutes"] >= 1


def test_path_traversal_is_rejected(client):
    assert client.get("/api/modules/..%2F..%2Fetc").status_code in (400, 404)
    assert client.get("/api/modules/module-1-introduction-to-python/docs/..%2F..%2Fmodule.yaml").status_code in (400, 404)


def test_quiz_hides_answers_and_explanations(client):
    login_as(STUDENT)
    quiz = client.get("/api/quiz/module-1-introduction-to-python").json()
    assert len(quiz["questions"]) >= 20
    for q in quiz["questions"]:
        assert "correct_answer" not in q
        assert "explanation" not in q


def test_problem_hides_hidden_tests_but_exposes_kind_and_hints(client):
    login_as(STUDENT)
    p = client.get("/api/problems/module-1-introduction-to-python/08-greet-user").json()
    assert p["type"] == "program"
    assert "hidden_tests" not in p and "solution_code" not in p
    assert p["visible_tests"][0]["stdin"] == "Asha\n"
    q = client.get("/api/problems/module-1-introduction-to-python/09-add-two-numbers").json()
    assert q["hints"]


def test_run_endpoint_runs_code_and_returns_images(client):
    login_as(STUDENT)
    r = client.post("/api/run", json={"code": "print(1 + 1)"})
    assert r.status_code == 200 and r.json()["stdout"].strip() == "2"

    r = client.post("/api/run", json={"code": "name = input()\nprint('Hi', name)", "stdin": "Ada\n"})
    assert r.json()["stdout"].strip() == "Hi Ada"

    chart = "import matplotlib.pyplot as plt\nplt.plot([1, 2, 3])\nplt.savefig('c.png')"
    r = client.post("/api/run", json={"code": chart})
    assert r.json()["images"][0].startswith("data:image/png;base64,")


def test_run_endpoint_reports_errors_and_limits_size(client):
    login_as(STUDENT)
    r = client.post("/api/run", json={"code": "1/0"})
    assert "ZeroDivisionError" in r.json()["stderr"]
    assert client.post("/api/run", json={"code": "x" * 30000}).status_code == 422


def test_run_requires_login(client):
    assert client.post("/api/run", json={"code": "print(1)"}).status_code == 401


def test_generate_and_delete_require_faculty(client):
    login_as(STUDENT)
    assert client.post("/api/generate/from-topic", json={"topic": "loops"}).status_code == 403
    assert client.post("/api/generate/from-text", json={"text": "hello"}).status_code == 403
    assert client.delete("/api/modules/generated-abc").status_code == 403


def test_generate_and_delete_reject_anonymous(client):
    assert client.post("/api/generate/from-topic", json={"topic": "loops"}).status_code == 401
    assert client.delete("/api/modules/generated-abc").status_code == 401


def test_core_modules_cannot_be_deleted_even_by_faculty(client):
    login_as(FACULTY)
    assert client.delete("/api/modules/module-1-introduction-to-python").status_code == 403


def test_url_generator_blocks_private_addresses(client):
    login_as(FACULTY)
    r = client.post("/api/generate/from-url", json={"url": "http://127.0.0.1:8000/secret"})
    assert r.status_code == 400
