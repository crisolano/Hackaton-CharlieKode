from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import SalaOcupada, setup_exception_handlers
from app.web.errors import setup_htmx_error_handlers

app = FastAPI()
setup_exception_handlers(app)
setup_htmx_error_handlers(app)


@app.get("/ocupada")
def ocupada():
    raise SalaOcupada()


@app.get("/validar")
def validar(n: int):
    return {"n": n}


client = TestClient(app)
HTMX = {"HX-Request": "true"}


def test_error_de_dominio_htmx_devuelve_parcial_html():
    r = client.get("/ocupada", headers=HTMX)
    assert r.status_code == 409
    assert "text/html" in r.headers["content-type"]
    assert "SALA_OCUPADA" in r.text


def test_error_de_dominio_sin_htmx_sigue_siendo_json():
    r = client.get("/ocupada")
    assert r.status_code == 409
    assert r.json()["codigo"] == "SALA_OCUPADA"


def test_validacion_htmx_no_expone_datos_enviados():
    r = client.get("/validar?n=valor-secreto", headers=HTMX)
    assert r.status_code == 422
    assert "DATOS_INVALIDOS" in r.text
    assert "valor-secreto" not in r.text


def test_validacion_sin_htmx_sigue_siendo_json():
    r = client.get("/validar?n=x")
    assert r.status_code == 422
    assert r.json()["codigo"] == "DATOS_INVALIDOS"
