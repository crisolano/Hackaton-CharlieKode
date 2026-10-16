from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_index_renderiza_base_con_tailwind_y_htmx():
    r = client.get("/")
    assert r.status_code == 200
    assert "cdn.tailwindcss.com" in r.text
    assert "htmx.org" in r.text


def test_static_servido():
    r = client.get("/static/app.css")
    assert r.status_code == 200
    assert "htmx-indicator" in r.text


def test_health_sigue_funcionando():
    assert client.get("/health").json()["ok"] is True
