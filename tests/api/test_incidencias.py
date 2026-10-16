import json

import pytest

from app.ai.base import AIClient, AIError
from app.api.deps import get_cliente_ia
from app.core.config import settings
from app.main import app


class IADoble(AIClient):
    def __init__(self, respuesta: str | Exception):
        self._respuesta = respuesta
        self.llamadas = 0

    def generate(self, prompt: str) -> str:
        self.llamadas += 1
        if isinstance(self._respuesta, Exception):
            raise self._respuesta
        return self._respuesta


CLASIFICACION = json.dumps(
    {"categoria": "hardware", "prioridad": "alta", "ruta": "soporte_tecnico"}
)


@pytest.fixture
def con_ia(client):
    """Sustituye el cliente de IA del router por un doble; devuelve una función para fijarlo."""

    def fijar(respuesta):
        doble = IADoble(respuesta)
        app.dependency_overrides[get_cliente_ia] = lambda: doble
        return doble

    return fijar


def test_incidencia_clasificada_por_la_ia(client, con_ia):
    ia = con_ia(CLASIFICACION)

    response = client.post("/api/incidencias", json={"texto": "El proyector no enciende"})

    assert response.status_code == 201
    data = response.json()["data"]
    assert response.json()["ok"] is True
    assert data["estado"] == "clasificada"
    assert data["categoria"] == "hardware"
    assert data["prioridad"] == "alta"
    assert data["ruta"] == "soporte_tecnico"
    assert data["origen_ia"] is True
    assert data["texto"] == "El proyector no enciende"
    assert ia.llamadas == 1


@pytest.mark.parametrize(
    "respuesta",
    [AIError("timeout"), "no es json", json.dumps({"categoria": "inventada"})],
    ids=["ia_caida", "salida_no_json", "valor_fuera_de_lista"],
)
def test_incidencia_queda_pendiente_si_la_ia_falla_sin_error_para_el_usuario(
    client, con_ia, respuesta
):
    con_ia(respuesta)

    response = client.post("/api/incidencias", json={"texto": "Fuga de agua en el baño"})

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["estado"] == "pendiente_revision"
    assert data["categoria"] is None
    assert data["prioridad"] is None
    assert data["origen_ia"] is False


def test_sin_clave_de_ia_la_incidencia_queda_pendiente_y_no_da_500(client, monkeypatch):
    """Sin sustituir la dependencia: usa la configuración real con la clave vacía."""
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

    response = client.post("/api/incidencias", json={"texto": "La red del aula no funciona"})

    assert response.status_code == 201
    assert response.json()["data"]["estado"] == "pendiente_revision"


@pytest.mark.parametrize("cuerpo", [{}, {"texto": ""}, {"texto": 123}])
def test_incidencia_con_datos_invalidos_devuelve_422(client, con_ia, cuerpo):
    con_ia(CLASIFICACION)

    response = client.post("/api/incidencias", json=cuerpo)

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"


def test_incidencia_solo_con_espacios_devuelve_422(client, con_ia):
    con_ia(CLASIFICACION)

    response = client.post("/api/incidencias", json={"texto": "   "})

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"


def test_listar_incidencias_y_filtrar(client, con_ia):
    con_ia(CLASIFICACION)
    client.post("/api/incidencias", json={"texto": "Clasificada"})
    con_ia(AIError("caída"))
    client.post("/api/incidencias", json={"texto": "Pendiente"})

    todas = client.get("/api/incidencias").json()
    pendientes = client.get("/api/incidencias?estado=pendiente_revision").json()
    hardware = client.get("/api/incidencias?categoria=hardware").json()

    assert todas["ok"] is True and len(todas["data"]) == 2
    assert [i["texto"] for i in pendientes["data"]] == ["Pendiente"]
    assert [i["texto"] for i in hardware["data"]] == ["Clasificada"]


def test_listar_incidencias_vacio(client):
    assert client.get("/api/incidencias").json() == {"ok": True, "data": []}


@pytest.mark.parametrize("query", ["estado=inventado", "categoria=inventada"])
def test_listar_con_filtro_invalido_devuelve_422(client, query):
    response = client.get(f"/api/incidencias?{query}")

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"


def test_swagger_documenta_incidencias(client):
    rutas = client.get("/openapi.json").json()["paths"]

    assert {"get", "post"} <= set(rutas["/api/incidencias"])
