from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.core.errors import (
    AppException,
    NoEncontrado,
    setup_exception_handlers,
)

app_errors = FastAPI()
setup_exception_handlers(app_errors)


class SensitiveDataModel(BaseModel):
    token_secreto: int = Field(..., description="Debe ser un entero")


@app_errors.get("/error-dominio")
def endpoint_error_dominio():
    raise NoEncontrado("Sala no encontrada")


@app_errors.get("/error-personalizado")
def endpoint_error_personalizado():
    raise AppException(codigo="DATOS_INVALIDOS", mensaje="Datos inconsistentes", status_code=400)


@app_errors.post("/validar-sensible")
def endpoint_validar_sensible(data: SensitiveDataModel):
    return {"ok": True}


@app_errors.get("/error-no-controlado")
def endpoint_error_no_controlado():
    raise RuntimeError("Fallo inesperado")


client = TestClient(app_errors, raise_server_exceptions=False)


def test_manejador_error_dominio():
    response = client.get("/error-dominio")
    assert response.status_code == 404
    data = response.json()
    assert data["ok"] is False
    assert data["codigo"] == "NO_ENCONTRADO"
    assert "Sala no encontrada" in data["mensaje"]


def test_manejador_error_personalizado():
    response = client.get("/error-personalizado")
    assert response.status_code == 400
    data = response.json()
    assert data["ok"] is False
    assert data["codigo"] == "DATOS_INVALIDOS"
    assert data["mensaje"] == "Datos inconsistentes"


def test_manejador_validacion_sanitiza_datos_sensibles():
    # Enviamos un valor que falla validación pero que podría ser sensible
    payload = {"token_secreto": "clave_super_secreta_que_no_debe_filtrarse"}
    response = client.post("/validar-sensible", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["codigo"] == "DATOS_INVALIDOS"
    assert "detalles" in data

    # Verificar que el valor del secreto no se expone en ninguna parte de la respuesta
    assert "clave_super_secreta_que_no_debe_filtrarse" not in response.text

    # Verificar que la estructura de detalles contiene loc, msg y type, pero NO 'input'
    for detalle in data["detalles"]:
        assert "loc" in detalle
        assert "msg" in detalle
        assert "type" in detalle
        assert "input" not in detalle


def test_manejador_error_no_controlado():
    response = client.get("/error-no-controlado")
    assert response.status_code == 500
    data = response.json()
    assert data["ok"] is False
    assert data["codigo"] == "ERROR_INTERNO"
