import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


@pytest.fixture
def con_api_key(monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "secreta")


def test_api_abierta_si_no_hay_api_key(client: TestClient):
    assert client.get("/api/equipos").status_code == 200


def test_api_rechaza_sin_clave(client: TestClient, con_api_key):
    r = client.get("/api/incidencias")
    assert r.status_code == 401
    assert r.json()["codigo"] == "NO_AUTORIZADO"


def test_api_rechaza_clave_incorrecta(client: TestClient, con_api_key):
    assert client.get("/api/equipos", headers={"X-API-Key": "otra"}).status_code == 401


def test_api_acepta_clave_correcta(client: TestClient, con_api_key):
    assert client.get("/api/equipos", headers={"X-API-Key": "secreta"}).status_code == 200


def test_health_no_exige_clave(client: TestClient, con_api_key):
    assert client.get("/health").status_code == 200


def test_texto_demasiado_largo_se_rechaza(client: TestClient):
    r = client.post("/api/incidencias", json={"texto": "x" * 2001})
    assert r.status_code == 422


def test_error_de_validacion_no_devuelve_el_dato_enviado(client: TestClient):
    r = client.post("/api/prestamos", json={"equipo_id": 0, "solicitante": "Ana Secreta"})
    assert r.status_code == 422
    assert "Ana Secreta" not in r.text


def test_limite_de_incidencias_por_minuto(client: TestClient, monkeypatch):
    monkeypatch.setattr(settings, "INCIDENCIAS_POR_MINUTO", 2)
    codigos = [
        client.post("/api/incidencias", json={"texto": "falla"}).status_code for _ in range(3)
    ]
    assert codigos == [201, 201, 429]


def test_paginacion_de_equipos(client: TestClient):
    assert client.get("/api/equipos?limit=0").status_code == 422
    assert client.get("/api/equipos?limit=1&offset=0").status_code == 200
