from app.web.routes import NAV_ITEMS


def test_index_renderiza_base_con_tailwind_y_htmx(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "cdn.tailwindcss.com" in r.text
    assert "htmx.org" in r.text


def test_htmx_con_integridad(client):
    r = client.get("/")
    assert 'integrity="sha384-' in r.text
    assert 'crossorigin="anonymous"' in r.text


def test_nav_items_es_inmutable():
    assert isinstance(NAV_ITEMS, tuple)


def test_static_servido(client):
    r = client.get("/static/app.css")
    assert r.status_code == 200
    assert "htmx-indicator" in r.text


def test_health_sigue_funcionando(client):
    assert client.get("/health").json()["ok"] is True
