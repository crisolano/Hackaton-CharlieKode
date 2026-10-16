import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models import Incidencia

HTMX = {"HX-Request": "true"}


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_pagina_incidencias_carga_correctamente(client):
    r = client.get("/incidencias")
    assert r.status_code == 200
    assert "Gestión de incidencias" in r.text
    assert "Reportar nueva incidencia" in r.text
    assert "texto-incidencia" in r.text
    assert 'action="/incidencias/reportar"' in r.text


def test_navegacion_incluye_incidencias(client):
    r = client.get("/")
    assert r.status_code == 200
    assert 'href="/incidencias"' in r.text


def test_reportar_incidencia_htmx_persiste_y_refresca_panel(client, db):
    r = client.post(
        "/incidencias/reportar",
        data={"texto": "El proyector del salón Cosmos no enciende y huele a quemado"},
        headers=HTMX,
    )
    assert r.status_code == 200
    assert "Incidencia registrada" in r.text
    assert 'hx-swap-oob="true"' in r.text
    assert "El proyector del salón Cosmos" in r.text

    # Verifica persistencia en la base de datos
    incidencia = db.query(Incidencia).first()
    assert incidencia is not None
    assert "Cosmos" in incidencia.texto


def test_reportar_incidencia_texto_vacio_muestra_error(client):
    r = client.post(
        "/incidencias/reportar",
        data={"texto": ""},
        headers=HTMX,
    )
    assert r.status_code == 422
    assert "DATOS_INVALIDOS" in r.text
