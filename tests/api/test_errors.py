import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.errors import (
    AforoExcedido,
    DatosInvalidos,
    NoEncontrado,
    RecursoNoDisponible,
    SalaOcupada,
    setup_exception_handlers,
)


class _Payload(BaseModel):
    asistentes: int


def _build_client() -> TestClient:
    app = FastAPI()
    setup_exception_handlers(app)

    @app.get("/aforo")
    def aforo():
        raise AforoExcedido(mensaje="La sala admite 20 personas y se pidieron 30.")

    @app.get("/ocupada")
    def ocupada():
        raise SalaOcupada()

    @app.get("/recurso")
    def recurso():
        raise RecursoNoDisponible()

    @app.get("/noexiste")
    def noexiste():
        raise NoEncontrado()

    @app.get("/invalidos")
    def invalidos():
        raise DatosInvalidos()

    @app.get("/boom")
    def boom():
        raise RuntimeError("detalle interno secreto")

    @app.post("/validar")
    def validar(payload: _Payload):
        return {"ok": True, "data": payload.model_dump()}

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module")
def client() -> TestClient:
    return _build_client()


@pytest.mark.parametrize(
    ("ruta", "http", "codigo"),
    [
        ("/aforo", 422, "AFORO_EXCEDIDO"),
        ("/ocupada", 409, "SALA_OCUPADA"),
        ("/recurso", 409, "RECURSO_NO_DISPONIBLE"),
        ("/noexiste", 404, "NO_ENCONTRADO"),
        ("/invalidos", 422, "DATOS_INVALIDOS"),
    ],
)
def test_excepciones_de_dominio_usan_formato_estandar(client, ruta, http, codigo):
    response = client.get(ruta)
    assert response.status_code == http
    data = response.json()
    assert data["ok"] is False
    assert data["codigo"] == codigo
    assert data["mensaje"]


def test_mensaje_personalizado_se_conserva(client):
    data = client.get("/aforo").json()
    assert data["mensaje"] == "La sala admite 20 personas y se pidieron 30."


def test_validacion_pydantic_devuelve_datos_invalidos(client):
    response = client.post("/validar", json={"asistentes": "no-es-numero"})
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["codigo"] == "DATOS_INVALIDOS"


def test_ruta_inexistente_devuelve_no_encontrado(client):
    response = client.get("/ruta-que-no-existe")
    assert response.status_code == 404
    data = response.json()
    assert data["ok"] is False
    assert data["codigo"] == "NO_ENCONTRADO"


def test_excepcion_no_controlada_no_expone_detalles(client):
    response = client.get("/boom")
    assert response.status_code == 500
    data = response.json()
    assert data["ok"] is False
    assert data["codigo"] == "ERROR_INTERNO"
    assert "secreto" not in response.text
