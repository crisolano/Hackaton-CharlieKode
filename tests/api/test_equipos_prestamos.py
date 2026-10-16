from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.core.config import EquipoEstado
from app.models import Equipo


def _equipo(db: Session, nombre: str = "Equipo de prueba", estado: EquipoEstado = None) -> Equipo:
    equipo = Equipo(nombre=nombre, estado=(estado or EquipoEstado.DISPONIBLE).value)
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo


def _prestamo(equipo_id: int, dias: int = 1) -> dict:
    devolucion = (datetime.now() + timedelta(days=dias)).replace(microsecond=0)
    return {
        "equipo_id": equipo_id,
        "solicitante": "Solicitante de prueba",
        "fecha_devolucion": devolucion.isoformat(),
    }


# --- GET /api/equipos -------------------------------------------------------------------


def test_listar_equipos_vacio(client):
    assert client.get("/api/equipos").json() == {"ok": True, "data": []}


def test_listar_equipos_con_estado_ordenados_por_nombre(client, db: Session):
    _equipo(db, "Beta")
    _equipo(db, "Alfa", EquipoEstado.DANADO)

    body = client.get("/api/equipos").json()

    assert body["ok"] is True
    assert [e["nombre"] for e in body["data"]] == ["Alfa", "Beta"]
    assert body["data"][0]["estado"] == "danado"
    assert {"id", "nombre", "estado"} == set(body["data"][0])


def test_listar_equipos_filtrados_por_estado(client, db: Session):
    _equipo(db, "Disponible")
    _equipo(db, "Roto", EquipoEstado.DANADO)

    body = client.get("/api/equipos?estado=disponible").json()

    assert [e["nombre"] for e in body["data"]] == ["Disponible"]


def test_listar_equipos_con_estado_invalido_devuelve_422(client):
    response = client.get("/api/equipos?estado=inventado")

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"


# --- POST /api/prestamos ----------------------------------------------------------------


def test_prestar_equipo_disponible(client, db: Session):
    equipo = _equipo(db)

    response = client.post("/api/prestamos", json=_prestamo(equipo.id))

    assert response.status_code == 201
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["equipo_id"] == equipo.id
    assert body["data"]["devuelto_en"] is None
    estado = client.get("/api/equipos").json()["data"][0]["estado"]
    assert estado == "prestado"


def test_prestar_equipo_ya_prestado_devuelve_409(client, db: Session):
    equipo = _equipo(db)
    assert client.post("/api/prestamos", json=_prestamo(equipo.id)).status_code == 201

    response = client.post("/api/prestamos", json=_prestamo(equipo.id))

    assert response.status_code == 409
    body = response.json()
    assert body["ok"] is False
    assert body["codigo"] == "RECURSO_NO_DISPONIBLE"


@pytest.mark.parametrize("estado", [EquipoEstado.DANADO, EquipoEstado.INHABILITADO])
def test_prestar_equipo_danado_o_inhabilitado_devuelve_409(client, db: Session, estado):
    equipo = _equipo(db, estado=estado)

    response = client.post("/api/prestamos", json=_prestamo(equipo.id))

    assert response.status_code == 409
    assert response.json()["codigo"] == "RECURSO_NO_DISPONIBLE"


def test_prestar_equipo_inexistente_devuelve_404(client):
    response = client.post("/api/prestamos", json=_prestamo(9999))

    assert response.status_code == 404
    body = response.json()
    assert body["codigo"] == "NO_ENCONTRADO"
    assert "9999" in body["mensaje"]


def test_prestar_con_devolucion_en_el_pasado_devuelve_422(client, db: Session):
    equipo = _equipo(db)

    response = client.post("/api/prestamos", json=_prestamo(equipo.id, dias=-1))

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"


@pytest.mark.parametrize(
    "cambio",
    [
        {"equipo_id": 0},
        {"solicitante": ""},
        {"fecha_devolucion": "2030-01-01T10:00:00Z"},  # con zona horaria
        {"fecha_devolucion": "no-es-fecha"},
    ],
)
def test_prestamo_con_datos_invalidos_devuelve_422(client, db: Session, cambio):
    equipo = _equipo(db)

    response = client.post("/api/prestamos", json={**_prestamo(equipo.id), **cambio})

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"


# --- POST /api/prestamos/{id}/devolucion ------------------------------------------------


def test_devolver_prestamo_deja_el_equipo_disponible(client, db: Session):
    equipo = _equipo(db)
    prestamo_id = client.post("/api/prestamos", json=_prestamo(equipo.id)).json()["data"]["id"]

    response = client.post(f"/api/prestamos/{prestamo_id}/devolucion")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["devuelto_en"] is not None
    assert client.get("/api/equipos").json()["data"][0]["estado"] == "disponible"


def test_equipo_devuelto_se_puede_volver_a_prestar(client, db: Session):
    equipo = _equipo(db)
    prestamo_id = client.post("/api/prestamos", json=_prestamo(equipo.id)).json()["data"]["id"]
    client.post(f"/api/prestamos/{prestamo_id}/devolucion")

    assert client.post("/api/prestamos", json=_prestamo(equipo.id)).status_code == 201


def test_devolver_dos_veces_devuelve_422(client, db: Session):
    equipo = _equipo(db)
    prestamo_id = client.post("/api/prestamos", json=_prestamo(equipo.id)).json()["data"]["id"]
    client.post(f"/api/prestamos/{prestamo_id}/devolucion")

    response = client.post(f"/api/prestamos/{prestamo_id}/devolucion")

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"


def test_devolver_prestamo_inexistente_devuelve_404(client):
    response = client.post("/api/prestamos/9999/devolucion")

    assert response.status_code == 404
    assert response.json()["codigo"] == "NO_ENCONTRADO"


def test_devolver_con_id_invalido_devuelve_422(client):
    response = client.post("/api/prestamos/0/devolucion")

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"


def test_swagger_documenta_equipos_y_prestamos(client):
    rutas = client.get("/openapi.json").json()["paths"]

    assert "get" in rutas["/api/equipos"]
    assert "post" in rutas["/api/prestamos"]
    assert "post" in rutas["/api/prestamos/{prestamo_id}/devolucion"]
