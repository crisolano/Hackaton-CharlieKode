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


def _html_parcial(codigo):
    from starlette.requests import Request

    from app.web.errors import _parcial_error

    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
    return _parcial_error(request, codigo, "Mensaje", 400).body.decode()


def test_parcial_de_error_muestra_titulo_por_codigo_y_oculta_el_codigo():
    r = client.get("/ocupada", headers=HTMX)
    assert "Esa sala ya está reservada" in r.text
    assert 'data-codigo="SALA_OCUPADA"' in r.text
    assert "Código:" not in r.text


def test_codigo_desconocido_usa_el_titulo_por_defecto():
    assert "No se pudo completar la acción" in _html_parcial("OTRO_CODIGO")


def test_titulos_de_todos_los_codigos_del_contrato():
    esperados = {
        "AFORO_EXCEDIDO": "Demasiadas personas para esta sala",
        "SALA_OCUPADA": "Esa sala ya está reservada",
        "DATOS_INVALIDOS": "Revisa el formulario",
        "NO_ENCONTRADO": "No encontramos esa sala",
        "RECURSO_NO_DISPONIBLE": "Sala no disponible",
        "ERROR_INTERNO": "Algo salió mal",
    }
    for codigo, titulo in esperados.items():
        assert titulo in _html_parcial(codigo)
