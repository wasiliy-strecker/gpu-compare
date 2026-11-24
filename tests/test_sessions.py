from fastapi.testclient import TestClient
from gpu_compare.api import app
from gpu_compare.config import settings
from gpu_compare.migrate import migrate


def test_standalone_session_cookie_and_csrf(monkeypatch):
    migrate()
    monkeypatch.setattr(settings(), "app_mode", "demo")
    with TestClient(app, base_url="https://testserver") as client:
        origin = {"Origin": settings().public_origin}
        assert client.post("/api/demo-sessions").status_code == 403
        response = client.post("/api/demo-sessions", headers=origin)
        assert response.status_code == 200
        cookie = response.headers["set-cookie"]
        assert "gpu_compare_session=" in cookie and "HttpOnly" in cookie and "Secure" in cookie
        assert client.get("/api/benchmarks/workspace").status_code == 200
        assert client.delete("/api/demo-sessions/current", headers=origin).status_code == 403
        headers = {**origin, "X-CSRF-Token": response.json()["csrf_token"]}
        assert client.delete("/api/demo-sessions/current", headers=headers).status_code == 200
        assert client.get("/api/benchmarks/workspace").status_code == 401
