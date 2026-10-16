import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

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

    @app.post("/solo-post")
    def solo_post():
        return {"ok": True}

    @app.get("/http503")
    def http503():
        raise StarletteHTTPException(status_code=503, detail="detalle interno secreto")

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


def test_error_http_5xx_usa_error_interno_sin_exponer_detalle(client):
    response = client.get("/http503")
    assert response.status_code == 503
    data = response.json()
    assert data["ok"] is False
    assert data["codigo"] == "ERROR_INTERNO"
    assert "secreto" not in response.text


def test_otros_errores_http_conservan_su_estado_y_no_se_etiquetan_como_datos_invalidos(client):
    response = client.get("/solo-post")
    assert response.status_code == 405
    assert response.json().get("codigo") != "DATOS_INVALIDOS"


def test_excepcion_no_controlada_se_registra_en_el_log_sin_filtrarse_a_la_respuesta(client, caplog):
    with caplog.at_level(logging.ERROR, logger="app.core.errors"):
        response = client.get("/boom")
    assert "secreto" not in response.text
    assert "GET /boom" in caplog.text
    assert "RuntimeError" in caplog.text
    assert "detalle interno secreto" in caplog.text


def test_error_http_5xx_se_registra_en_el_log(client, caplog):
    with caplog.at_level(logging.ERROR, logger="app.core.errors"):
        client.get("/http503")
    assert "503" in caplog.text
    assert "/http503" in caplog.text


def test_app_real_registra_los_handlers_de_error():
    from app.main import app

    response = TestClient(app).get("/ruta-que-no-existe")
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
