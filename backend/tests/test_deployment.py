from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from starlette.responses import Response

from app.api.auth import _set_auth_cookie
from app.core.config import Settings, settings
from app.core.deps import get_current_user, get_db
from app.core.spa import SPAStaticFiles
from app.core.web_security import CookieOriginMiddleware
from app.main import app
from app.services import execution


def production(**overrides):
    values = dict(ENVIRONMENT="production", SECRET_KEY="s" * 40, SESSION_SECRET="t" * 40,
                  COOKIE_SECURE=True, FRONTEND_URL="https://learn.example.com",
                  BACKEND_CORS_ORIGINS=["https://learn.example.com"],
                  TRUSTED_HOSTS=["learn.example.com"], SANDBOX_MODE="disabled", PUBLIC_API_ENABLED=False)
    values.update(overrides)
    return Settings(_env_file=None, **values)


@pytest.mark.parametrize("overrides", [
    {"COOKIE_SECURE": False}, {"SECRET_KEY": "change-me"}, {"SESSION_SECRET": "short"},
    {"SANDBOX_MODE": "local"}, {"TRUSTED_HOSTS": ["*"]},
    {"BACKEND_CORS_ORIGINS": ["*"]}, {"BACKEND_CORS_ORIGINS": ["http://learn.example.com"]},
    {"FRONTEND_URL": "http://learn.example.com"}, {"PUBLIC_API_ENABLED": True, "PUBLIC_API_KEY": "pylearn-demo"},
    {"SANDBOX_MODE": "remote", "SANDBOX_RUNNER_URL": "http://runner.example.com", "SANDBOX_RUNNER_KEY": "r" * 40},
])
def test_production_rejects_unsafe_configuration(overrides):
    with pytest.raises(ValidationError):
        production(**overrides)


def test_remote_production_configuration_and_secure_cookie(monkeypatch):
    assert production(SANDBOX_MODE="remote", SANDBOX_RUNNER_URL="https://runner.example.com",
                      SANDBOX_RUNNER_KEY="r" * 40).COOKIE_SECURE
    monkeypatch.setattr(settings, "COOKIE_SECURE", True)
    monkeypatch.setattr(settings, "COOKIE_SAMESITE", "none")
    response = Response()
    _set_auth_cookie(response, "token")
    cookie = response.headers["set-cookie"].lower()
    assert "secure" in cookie and "httponly" in cookie and "samesite=none" in cookie
    assert "domain=" not in cookie


def test_cookie_mutations_reject_foreign_and_missing_origins():
    test_app = FastAPI()
    test_app.add_middleware(CookieOriginMiddleware)
    @test_app.post("/api/change")
    def change():
        return {"ok": True}
    with TestClient(test_app) as client:
        client.cookies.set("access_token", "token")
        assert client.post("/api/change", headers={"Origin": "https://attacker.invalid"}).status_code == 403
        assert client.post("/api/change").status_code == 403
        assert client.post("/api/change", headers={"Origin": "http://testserver"}).status_code == 200
        assert client.post("/api/change", headers={"X-CSRF-Protection": "1"}).status_code == 200


def test_spa_supports_deep_links_without_masking_api_or_asset_404s(tmp_path):
    (tmp_path / "index.html").write_text("<html>React app</html>")
    test_app = FastAPI()
    test_app.mount("/", SPAStaticFiles(directory=tmp_path, html=True))
    with TestClient(test_app) as client:
        assert "React app" in client.get("/dashboard").text
        assert client.get("/api/missing").status_code == 404
        assert client.get("/assets/missing.js").status_code == 404


def test_runner_outage_is_503_and_never_falls_back_to_local(monkeypatch):
    monkeypatch.setattr(settings, "SANDBOX_MODE", "remote")
    def outage(*args):
        raise execution.SandboxUnavailable("The isolated Python runner is unavailable.")
    monkeypatch.setattr(execution, "_remote_execution", outage)
    monkeypatch.setattr(execution, "_run_local", lambda *args: pytest.fail("Unsafe local fallback"))
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=901)
    try:
        with TestClient(app) as client:
            assert client.post("/api/run", json={"code": "print(1)"}).status_code == 503
    finally:
        app.dependency_overrides.clear()


def test_disabled_runner_and_runtime_production_guard(monkeypatch):
    monkeypatch.setattr(settings, "SANDBOX_MODE", "disabled")
    with pytest.raises(execution.SandboxUnavailable):
        execution.run_python_code("print(1)")
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "SANDBOX_MODE", "local")
    with pytest.raises(execution.SandboxUnavailable):
        execution.run_python_code("print(1)")


def test_remote_response_validation_rejects_malformed_images():
    with pytest.raises(execution.SandboxUnavailable):
        execution._execution_result(dict(stdout="", stderr="", timed_out=False, error=False,
                                         images=["data:image/png;base64,not-a-png"]))


def test_public_runner_can_be_disabled(monkeypatch):
    monkeypatch.setattr(settings, "PUBLIC_API_ENABLED", False)
    with TestClient(app) as client:
        assert client.post("/api/public/run", json={"code": "print(1)"}).status_code == 404
        assert client.get("/demo").status_code == 404


def test_https_login_me_and_logout_with_host_only_cookies(db, monkeypatch):
    monkeypatch.setattr(settings, "COOKIE_SECURE", True)
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://testserver")
    app.dependency_overrides[get_db] = lambda: db
    try:
        with TestClient(app, base_url="https://testserver", headers={"X-CSRF-Protection": "1"}) as client:
            response = client.post("/api/auth/signup", json={"email": "hosted@example.com",
                                   "password": "DemoPassword!123", "full_name": "Hosted Learner"})
            assert response.status_code == 201
            assert "Secure" in response.headers["set-cookie"]
            assert client.get("/api/auth/me").json()["email"] == "hosted@example.com"
            assert client.post("/api/auth/logout").status_code == 200
            assert client.get("/api/auth/me").status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_runner_outage_does_not_save_a_failed_submission(db, monkeypatch):
    from app.models.progress import CodeSubmission
    from tests.conftest import make_user
    user = make_user(db)
    monkeypatch.setattr(settings, "SANDBOX_MODE", "disabled")
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db
    try:
        with TestClient(app) as client:
            response = client.post("/api/problems/module-1-introduction-to-python/09-add-two-numbers/submit",
                                   json={"code": "print(3)"})
            assert response.status_code == 503
            assert db.query(CodeSubmission).count() == 0
            assert client.post("/api/problems/module-1-introduction-to-python/09-add-two-numbers/submit",
                               json={"code": "x" * 20001}).status_code == 422
    finally:
        app.dependency_overrides.clear()
