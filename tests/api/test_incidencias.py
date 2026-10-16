import json

import pytest
from sqlalchemy.orm import Session

from app.ai.base import AIClient, AIError
from app.api.deps import get_cliente_ia
from app.core.config import settings
from app.main import app
from app.models import Incidencia


class IADoble(AIClient):
    def __init__(self, respuesta: str | Exception):
        self._respuesta = respuesta
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
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


def _guardada(db: Session, incidencia_id: int) -> Incidencia | None:
    """Lee la incidencia tras descartar lo no confirmado: solo existe si hubo commit."""
    db.rollback()
    db.expire_all()
    return db.get(Incidencia, incidencia_id)


def _crear(client, texto: str) -> dict:
    response = client.post("/api/incidencias", json={"texto": texto})
    assert response.status_code == 201, response.text
    return response.json()["data"]


# --- POST /api/incidencias --------------------------------------------------------------


def test_incidencia_clasificada_por_la_ia_se_devuelve_y_se_guarda(client, con_ia, db: Session):
    ia = con_ia(CLASIFICACION)

    response = client.post("/api/incidencias", json={"texto": "El proyector no enciende"})

    assert response.status_code == 201
    assert response.json()["ok"] is True
    data = response.json()["data"]
    assert data["estado"] == "clasificada"
    assert data["categoria"] == "hardware"
    assert data["prioridad"] == "alta"
    assert data["ruta"] == "soporte_tecnico"
    assert data["origen_ia"] is True
    assert data["texto"] == "El proyector no enciende"
    assert len(ia.prompts) == 1
    assert "El proyector no enciende" in ia.prompts[0]

    guardada = _guardada(db, data["id"])
    assert guardada is not None
    assert (guardada.categoria, guardada.prioridad, guardada.ruta) == (
        "hardware",
        "alta",
        "soporte_tecnico",
    )
    assert guardada.estado == "clasificada"
    assert guardada.origen_ia is True


@pytest.mark.parametrize(
    "respuesta",
    [AIError("timeout"), "no es json", json.dumps({"categoria": "inventada"})],
    ids=["ia_caida", "salida_no_json", "valor_fuera_de_lista"],
)
def test_incidencia_queda_pendiente_si_la_ia_falla_sin_error_para_el_usuario(
    client, con_ia, db: Session, respuesta
):
    con_ia(respuesta)

    response = client.post("/api/incidencias", json={"texto": "Fuga de agua en el baño"})

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["estado"] == "pendiente_revision"
    assert data["ruta"] == "revision_manual"
    assert data["categoria"] is None
    assert data["prioridad"] is None
    assert data["origen_ia"] is False

    guardada = _guardada(db, data["id"])
    assert guardada is not None
    assert guardada.estado == "pendiente_revision"
    assert guardada.ruta == "revision_manual"
    assert guardada.categoria is None and guardada.prioridad is None
    assert guardada.origen_ia is False


def test_sin_clave_de_ia_la_incidencia_queda_pendiente_y_no_da_500(
    client, monkeypatch, db: Session
):
    """Sin sustituir la dependencia: usa la configuración real con la clave vacía."""
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

    response = client.post("/api/incidencias", json={"texto": "La red del aula no funciona"})

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["estado"] == "pendiente_revision"
    assert data["ruta"] == "revision_manual"
    assert data["categoria"] is None
    assert data["prioridad"] is None
    assert data["origen_ia"] is False
    guardada = _guardada(db, data["id"])
    assert guardada is not None and guardada.estado == "pendiente_revision"


def test_el_texto_se_guarda_sin_espacios_alrededor(client, con_ia, db: Session):
    con_ia(CLASIFICACION)

    data = _crear(client, "   El aire acondicionado gotea   ")

    assert data["texto"] == "El aire acondicionado gotea"
    assert _guardada(db, data["id"]).texto == "El aire acondicionado gotea"


@pytest.mark.parametrize("cuerpo", [{}, {"texto": ""}, {"texto": 123}])
def test_incidencia_con_datos_invalidos_devuelve_422(client, con_ia, cuerpo):
    con_ia(CLASIFICACION)

    response = client.post("/api/incidencias", json=cuerpo)

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"


def test_incidencia_solo_con_espacios_devuelve_422_y_no_llama_a_la_ia(client, con_ia):
    ia = con_ia(CLASIFICACION)

    response = client.post("/api/incidencias", json={"texto": "   "})

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"
    assert ia.prompts == []


# --- GET /api/incidencias ---------------------------------------------------------------


def test_listar_incidencias_mas_recientes_primero(client, con_ia):
    con_ia(CLASIFICACION)
    primera = _crear(client, "Primera")
    segunda = _crear(client, "Segunda")

    data = client.get("/api/incidencias").json()["data"]

    assert [i["id"] for i in data] == [segunda["id"], primera["id"]]


def test_listar_incidencias_y_filtrar(client, con_ia):
    con_ia(CLASIFICACION)
    _crear(client, "Clasificada")
    con_ia(AIError("caída"))
    _crear(client, "Pendiente")

    todas = client.get("/api/incidencias").json()
    pendientes = client.get("/api/incidencias?estado=pendiente_revision").json()
    clasificadas = client.get("/api/incidencias?estado=clasificada").json()
    hardware = client.get("/api/incidencias?categoria=hardware").json()
    combinado = client.get("/api/incidencias?estado=clasificada&categoria=hardware").json()
    sin_resultado = client.get("/api/incidencias?estado=pendiente_revision&categoria=hardware")

    assert todas["ok"] is True and len(todas["data"]) == 2
    assert [i["texto"] for i in pendientes["data"]] == ["Pendiente"]
    assert [i["texto"] for i in clasificadas["data"]] == ["Clasificada"]
    assert [i["texto"] for i in hardware["data"]] == ["Clasificada"]
    assert [i["texto"] for i in combinado["data"]] == ["Clasificada"]
    assert sin_resultado.json() == {"ok": True, "data": []}


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
    respuestas_post = rutas["/api/incidencias"]["post"]["responses"]
    assert "201" in respuestas_post
