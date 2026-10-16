import pytest
from fastapi.testclient import TestClient

from app.core.config import EquipoEstado
from app.core.database import get_db
from app.main import app
from app.models import Equipo, Prestamo

HTMX = {"HX-Request": "true"}
DEVOLUCION_FUTURA = "2099-01-15T10:00"


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def equipos_de_prueba(db):
    equipos = [
        Equipo(nombre="Portátil 01"),
        Equipo(nombre="Proyector 02"),
        Equipo(nombre="Cámara 03", estado=EquipoEstado.DANADO.value),
    ]
    db.add_all(equipos)
    db.commit()
    return equipos


def _datos(equipo, **cambios):
    datos = {
        "equipo_id": str(equipo.id),
        "solicitante": "Ana Pérez",
        "fecha_devolucion": DEVOLUCION_FUTURA,
    }
    datos.update(cambios)
    return datos


def _prestar(client, equipo, **cambios):
    return client.post("/equipos/prestar", data=_datos(equipo, **cambios), headers=HTMX)


def test_pagina_equipos_muestra_inventario_desde_la_bd(client, equipos_de_prueba):
    r = client.get("/equipos")
    assert r.status_code == 200
    for equipo in equipos_de_prueba:
        assert f'<td class="px-4 py-2">{equipo.nombre}</td>' in r.text


def test_selector_solo_ofrece_equipos_disponibles(client, equipos_de_prueba):
    portatil, proyector, camara = equipos_de_prueba
    html = client.get("/equipos").text
    assert f'<option value="{portatil.id}">' in html
    assert f'<option value="{proyector.id}">' in html
    assert f'<option value="{camara.id}">' not in html


def test_pagina_equipos_sin_datos_no_inventa_equipos(client):
    r = client.get("/equipos")
    assert r.status_code == 200
    assert "No hay equipos registrados." in r.text
    assert "No hay equipos disponibles para préstamo." in r.text


def test_navegacion_incluye_equipos(client):
    assert 'href="/equipos"' in client.get("/").text


def test_prestamo_valido_cambia_estado_y_refresca_el_panel(client, db, equipos_de_prueba):
    portatil = equipos_de_prueba[0]
    r = _prestar(client, portatil)
    assert r.status_code == 200
    assert "Préstamo registrado" in r.text
    assert 'hx-swap-oob="true"' in r.text
    assert "Registrar devolución" in r.text
    db.refresh(portatil)
    assert portatil.estado == EquipoEstado.PRESTADO.value
    assert db.query(Prestamo).count() == 1


def test_no_se_puede_prestar_un_equipo_ya_prestado(client, db, equipos_de_prueba):
    portatil = equipos_de_prueba[0]
    assert _prestar(client, portatil).status_code == 200
    r = _prestar(client, portatil, solicitante="Luis")
    assert r.status_code == 409
    assert "RECURSO_NO_DISPONIBLE" in r.text
    assert db.query(Prestamo).count() == 1


def test_no_se_puede_prestar_un_equipo_danado(client, db, equipos_de_prueba):
    r = _prestar(client, equipos_de_prueba[2])
    assert r.status_code == 409
    assert "RECURSO_NO_DISPONIBLE" in r.text
    assert db.query(Prestamo).count() == 0


def test_devolucion_libera_el_equipo(client, db, equipos_de_prueba):
    portatil = equipos_de_prueba[0]
    _prestar(client, portatil)
    prestamo = db.query(Prestamo).one()
    r = client.post(f"/equipos/prestamos/{prestamo.id}/devolucion", headers=HTMX)
    assert r.status_code == 200
    assert "Devolución registrada" in r.text
    db.refresh(portatil)
    db.refresh(prestamo)
    assert portatil.estado == EquipoEstado.DISPONIBLE.value
    assert prestamo.devuelto_en is not None


def test_devolucion_repetida_muestra_error(client, db, equipos_de_prueba):
    _prestar(client, equipos_de_prueba[0])
    prestamo = db.query(Prestamo).one()
    url = f"/equipos/prestamos/{prestamo.id}/devolucion"
    assert client.post(url, headers=HTMX).status_code == 200
    r = client.post(url, headers=HTMX)
    assert r.status_code == 422
    assert "DATOS_INVALIDOS" in r.text


def test_devolucion_de_prestamo_inexistente(client):
    r = client.post("/equipos/prestamos/999/devolucion", headers=HTMX)
    assert r.status_code == 404
    assert "NO_ENCONTRADO" in r.text


def test_fecha_de_devolucion_pasada_muestra_error(client, db, equipos_de_prueba):
    r = _prestar(client, equipos_de_prueba[0], fecha_devolucion="2000-01-01T10:00")
    assert r.status_code == 422
    assert "DATOS_INVALIDOS" in r.text
    assert db.query(Prestamo).count() == 0


def test_formulario_vacio_devuelve_datos_invalidos_sin_eco_de_entrada(client):
    r = client.post("/equipos/prestar", data={"solicitante": "x-dato-enviado"}, headers=HTMX)
    assert r.status_code == 422
    assert "DATOS_INVALIDOS" in r.text
    assert "x-dato-enviado" not in r.text


def test_solicitante_se_escapa_en_la_respuesta(client, equipos_de_prueba):
    r = _prestar(client, equipos_de_prueba[0], solicitante="<script>alert(1)</script>")
    assert r.status_code == 200
    assert "<script>alert(1)</script>" not in r.text
    assert "&lt;script&gt;" in r.text


def test_formularios_declaran_post_como_respaldo_sin_htmx(client, db, equipos_de_prueba):
    _prestar(client, equipos_de_prueba[0])
    html = client.get("/equipos").text
    assert 'action="/equipos/prestar"' in html
    assert 'action="/equipos/prestamos/' in html
