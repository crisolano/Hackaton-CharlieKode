import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.errors import MSG_ERROR_RANGO_HORARIO
from app.main import app
from app.models import Reserva, Sala

HTMX = {"HX-Request": "true"}


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def salas_de_prueba(db):
    salas = [Sala(nombre="Sala Uno", aforo=10), Sala(nombre="Sala Dos", aforo=40)]
    db.add_all(salas)
    db.commit()
    return salas


def _datos(sala, **cambios):
    datos = {
        "sala_id": str(sala.id),
        "inicio": "2026-10-16T14:00",
        "fin": "2026-10-16T16:00",
        "asistentes": "5",
        "responsable": "Ana Pérez",
    }
    datos.update(cambios)
    return datos


def test_pagina_salas_muestra_la_tabla_y_el_selector_desde_la_bd(client, salas_de_prueba):
    r = client.get("/salas")
    assert r.status_code == 200
    for sala in salas_de_prueba:
        assert f'<td class="px-4 py-2">{sala.nombre}</td>' in r.text
        assert f'<option value="{sala.id}">{sala.nombre} (aforo {sala.aforo})</option>' in r.text


def test_pagina_salas_sin_datos_no_inventa_salas(client):
    r = client.get("/salas")
    assert r.status_code == 200
    assert "No hay salas registradas." in r.text
    assert '<option value="1"' not in r.text


def test_navegacion_incluye_espacios(client):
    r = client.get("/")
    assert 'href="/salas"' in r.text


def test_reserva_valida_devuelve_parcial_de_exito_y_persiste(client, db, salas_de_prueba):
    r = client.post("/salas/reservar", data=_datos(salas_de_prueba[0]), headers=HTMX)
    assert r.status_code == 200
    assert "Reserva creada" in r.text
    assert 'hx-swap-oob="true"' in r.text
    assert db.query(Reserva).count() == 1


def test_aforo_excedido_muestra_el_error_en_pantalla(client, db, salas_de_prueba):
    datos = _datos(salas_de_prueba[0], asistentes="30")
    r = client.post("/salas/reservar", data=datos, headers=HTMX)
    assert r.status_code == 422
    assert "AFORO_EXCEDIDO" in r.text
    assert "Sala Uno" in r.text
    assert db.query(Reserva).count() == 0


def test_solapamiento_muestra_sala_ocupada(client, db, salas_de_prueba):
    sala = salas_de_prueba[0]
    assert client.post("/salas/reservar", data=_datos(sala), headers=HTMX).status_code == 200
    r = client.post("/salas/reservar", data=_datos(sala, inicio="2026-10-16T15:00"), headers=HTMX)
    assert r.status_code == 409
    assert "SALA_OCUPADA" in r.text
    assert db.query(Reserva).count() == 1


def test_reservas_contiguas_no_se_solapan(client, salas_de_prueba):
    sala = salas_de_prueba[0]
    client.post("/salas/reservar", data=_datos(sala), headers=HTMX)
    contigua = _datos(sala, inicio="2026-10-16T16:00", fin="2026-10-16T17:00")
    assert client.post("/salas/reservar", data=contigua, headers=HTMX).status_code == 200


def test_rango_horario_invalido_muestra_el_mensaje_del_esquema(client, salas_de_prueba):
    datos = _datos(salas_de_prueba[0], inicio="2026-10-16T16:00", fin="2026-10-16T14:00")
    r = client.post("/salas/reservar", data=datos, headers=HTMX)
    assert r.status_code == 422
    assert "DATOS_INVALIDOS" in r.text
    assert MSG_ERROR_RANGO_HORARIO in r.text


def test_formulario_vacio_devuelve_datos_invalidos_sin_eco_de_entrada(client):
    r = client.post("/salas/reservar", data={"responsable": "x-dato-enviado"}, headers=HTMX)
    assert r.status_code == 422
    assert "DATOS_INVALIDOS" in r.text
    assert "x-dato-enviado" not in r.text


def test_sala_inexistente_devuelve_no_encontrado(client, salas_de_prueba):
    r = client.post("/salas/reservar", data=_datos(salas_de_prueba[0], sala_id="999"), headers=HTMX)
    assert r.status_code == 404
    assert "NO_ENCONTRADO" in r.text


def test_responsable_se_escapa_en_la_respuesta(client, salas_de_prueba):
    datos = _datos(salas_de_prueba[0], responsable="<script>alert(1)</script>")
    r = client.post("/salas/reservar", data=datos, headers=HTMX)
    assert r.status_code == 200
    assert "<script>alert(1)</script>" not in r.text
    assert "&lt;script&gt;" in r.text


def test_formulario_funciona_sin_htmx_con_post_y_no_con_get(client, salas_de_prueba):
    html = client.get("/salas").text
    assert 'method="post"' in html
    assert 'action="/salas/reservar"' in html
