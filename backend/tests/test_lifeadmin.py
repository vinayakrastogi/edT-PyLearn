import json
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from starlette.responses import Response

from app.api.auth import _set_auth_cookie
from app.core.config import settings
from app.core.deps import get_current_user
from app.main import app
from app.services import lifeadmin

PATH = "/api/notes/module-1-introduction-to-python/01-getting-started-with-python"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(settings, "LIFEADMIN_API_KEY", "a" * 40)
    monkeypatch.setattr(settings, "LIFEADMIN_CLIENT_ID", "school-a")
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=7, email="demostudent@example.com")
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def mock_http(monkeypatch, handler):
    real_client = httpx.AsyncClient
    monkeypatch.setattr(lifeadmin.httpx, "AsyncClient",
                        lambda **kwargs: real_client(**kwargs, transport=httpx.MockTransport(handler)))


def test_learner_identity_and_lesson_are_server_controlled(client, monkeypatch):
    requests = []
    note_id = str(uuid4())

    def remote(request):
        requests.append(request)
        assert request.headers["X-API-Key"] == settings.LIFEADMIN_API_KEY
        assert request.headers["ngrok-skip-browser-warning"] == "1"
        data = json.loads(request.content)
        assert data["owner_id"] == "school-a:7"
        assert data["owner_email"] == "demostudent@example.com"
        assert data["resource_id"] == "module-1-introduction-to-python/01-getting-started-with-python"
        assert data["title"] == "Getting Started with Python"
        return httpx.Response(201, json={"id": note_id, "created_at": "2026-10-24T10:00:00+00:00", **data})

    mock_http(monkeypatch, remote)
    response = client.post(PATH, json={"content": "Use print()", "request_id": str(uuid4())})
    assert response.status_code == 201
    assert response.json()["id"] == note_id
    assert "owner_id" not in response.json()
    assert client.post(PATH, json={"content": "note", "request_id": str(uuid4()), "owner_id": "other"}).status_code == 422
    assert len(requests) == 1


def test_list_and_delete_pass_only_current_owner(client, monkeypatch):
    def remote(request):
        assert request.url.params["owner_id"] == "school-a:7"
        assert request.url.params["owner_email"] == "demostudent@example.com"
        if request.method == "DELETE":
            return httpx.Response(204)
        assert request.url.params["resource_id"].endswith("/01-getting-started-with-python")
        return httpx.Response(200, json=[])
    mock_http(monkeypatch, remote)
    assert client.get(PATH).json() == {"notes": []}
    assert client.delete(f"/api/notes/{uuid4()}").status_code == 204


@pytest.mark.parametrize("failure,expected", [("timeout", 504), ("offline", 503),
                                              (401, 503), (409, 409), (500, 502), ("bad-json", 502)])
def test_remote_errors_are_actionable_and_hide_remote_details(client, monkeypatch, failure, expected):
    def remote(request):
        if failure == "timeout":
            raise httpx.ReadTimeout("secret", request=request)
        if failure == "offline":
            raise httpx.ConnectError("secret", request=request)
        if failure == "bad-json":
            return httpx.Response(200, json={"unexpected": "secret"})
        return httpx.Response(failure, text="secret")
    mock_http(monkeypatch, remote)
    response = client.get(PATH)
    assert response.status_code == expected
    assert "secret" not in response.text


def test_disabled_service_and_invalid_lesson(client, monkeypatch):
    monkeypatch.setattr(settings, "LIFEADMIN_API_KEY", "")
    assert client.get(PATH).status_code == 503
    assert client.get("/api/notes/missing/lesson").status_code == 404


def test_authentication_is_required(client):
    app.dependency_overrides.clear()
    assert client.get(PATH).status_code == 401
    assert client.post(PATH, json={"content": "note", "request_id": str(uuid4())}).status_code == 401
    assert client.delete(f"/api/notes/{uuid4()}").status_code == 401


def test_auth_cookie_can_be_used_on_lan_hosts():
    response = Response()
    _set_auth_cookie(response, "test-token")
    cookie = response.headers["set-cookie"].lower()
    assert "domain=" not in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie


def test_starting_service_retries_the_identical_note_request(client, monkeypatch):
    requests = []
    note_id = str(uuid4())
    pause = AsyncMock()
    monkeypatch.setattr(lifeadmin, "sleep", pause)

    def remote(request):
        requests.append(request)
        if len(requests) <= 2:
            return httpx.Response(502, text="Host starting")
        data = json.loads(request.content)
        return httpx.Response(201, json={"id": note_id, "created_at": "2026-10-29T05:00:00+00:00", **data})

    mock_http(monkeypatch, remote)
    response = client.post(PATH, json={"content": "Keep this draft", "request_id": str(uuid4())})
    assert response.status_code == 201
    assert response.json()["id"] == note_id
    assert len(requests) == 3
    assert len({request.content for request in requests}) == 1
    assert pause.await_count == 2


@pytest.mark.parametrize("status", [502, 503, 504])
def test_gateway_outage_has_bounded_retries_and_a_useful_message(client, monkeypatch, status):
    calls = []
    monkeypatch.setattr(lifeadmin, "sleep", AsyncMock())

    def remote(request):
        calls.append(request)
        return httpx.Response(status, text="private hosting diagnostics")

    mock_http(monkeypatch, remote)
    response = client.get(PATH)
    assert response.status_code == 503
    assert "starting or temporarily unavailable" in response.json()["detail"]
    assert "private hosting diagnostics" not in response.text
    assert len(calls) == 7


def test_configuration_503_is_not_retried(client, monkeypatch):
    pause = AsyncMock()
    monkeypatch.setattr(lifeadmin, "sleep", pause)
    mock_http(monkeypatch, lambda request: httpx.Response(503, json={"detail": "private configuration"}))
    response = client.get(PATH)
    assert response.status_code == 503
    assert "API key" in response.json()["detail"]
    pause.assert_not_awaited()


def test_startup_retries_share_the_overall_deadline(client, monkeypatch):
    monkeypatch.setattr(settings, "LIFEADMIN_TIMEOUT_SECONDS", 0.02)
    mock_http(monkeypatch, lambda request: httpx.Response(502, text="Host starting"))
    response = client.get(PATH)
    assert response.status_code == 504
    assert "Retry with the same note" in response.json()["detail"]
