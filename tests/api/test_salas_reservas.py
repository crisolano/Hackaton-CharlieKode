import pytest
from sqlalchemy.orm import Session

from app.models import Sala


def _reserva(sala_id: int, inicio: str, fin: str, asistentes: int = 10, **extra) -> dict:
    return {
        "sala_id": sala_id,
        "inicio": inicio,
        "fin": fin,
        "asistentes": asistentes,
        "responsable": "Responsable de prueba",
        **extra,
    }


# --- GET /api/salas ---------------------------------------------------------------------


def test_listar_salas_vacio(client):
    response = client.get("/api/salas")
    assert response.status_code == 200
    assert response.json() == {"ok": True, "data": []}


def test_listar_salas_devuelve_aforo_y_estado_ordenadas_por_nombre(client, db: Session):
    db.add_all([Sala(nombre="Beta", aforo=15), Sala(nombre="Alfa", aforo=25)])
    db.commit()

    body = client.get("/api/salas").json()

    assert body["ok"] is True
    assert [s["nombre"] for s in body["data"]] == ["Alfa", "Beta"]
    assert body["data"][0]["aforo"] == 25
    assert body["data"][0]["estado"] == "activa"
    assert {"id", "nombre", "aforo", "estado"} == set(body["data"][0])


# --- POST /api/reservas -----------------------------------------------------------------


def test_crear_reserva_valida(client, sala):
    response = client.post(
        "/api/reservas", json=_reserva(sala.id, "2026-10-16T14:00:00", "2026-10-16T16:00:00")
    )

    assert response.status_code == 201
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["id"] >= 1
    assert body["data"]["sala_id"] == sala.id
    assert body["data"]["inicio"] == "2026-10-16T14:00:00"
    assert body["data"]["asistentes"] == 10


def test_crear_reserva_con_aforo_excedido_devuelve_422(client, sala):
    response = client.post(
        "/api/reservas",
        json=_reserva(sala.id, "2026-10-16T14:00:00", "2026-10-16T16:00:00", asistentes=30),
    )

    assert response.status_code == 422
    body = response.json()
    assert body["ok"] is False
    assert body["codigo"] == "AFORO_EXCEDIDO"
    assert sala.nombre in body["mensaje"]
    assert "20" in body["mensaje"] and "30" in body["mensaje"]


def test_crear_reserva_en_sala_ocupada_devuelve_409(client, sala):
    primera = _reserva(sala.id, "2026-10-16T14:00:00", "2026-10-16T16:00:00")
    assert client.post("/api/reservas", json=primera).status_code == 201

    solapada = _reserva(sala.id, "2026-10-16T15:00:00", "2026-10-16T17:00:00")
    response = client.post("/api/reservas", json=solapada)

    assert response.status_code == 409
    body = response.json()
    assert body["ok"] is False
    assert body["codigo"] == "SALA_OCUPADA"
    assert sala.nombre in body["mensaje"]


def test_reservas_contiguas_no_se_solapan(client, sala):
    client.post(
        "/api/reservas", json=_reserva(sala.id, "2026-10-16T14:00:00", "2026-10-16T16:00:00")
    )

    contigua = _reserva(sala.id, "2026-10-16T16:00:00", "2026-10-16T18:00:00")

    assert client.post("/api/reservas", json=contigua).status_code == 201


def test_misma_franja_en_otra_sala_es_valida(client, db: Session, sala):
    otra = Sala(nombre="Otra sala", aforo=20)
    db.add(otra)
    db.commit()
    db.refresh(otra)
    client.post(
        "/api/reservas", json=_reserva(sala.id, "2026-10-16T14:00:00", "2026-10-16T16:00:00")
    )

    response = client.post(
        "/api/reservas", json=_reserva(otra.id, "2026-10-16T14:00:00", "2026-10-16T16:00:00")
    )

    assert response.status_code == 201


def test_crear_reserva_en_sala_inexistente_devuelve_404(client):
    response = client.post(
        "/api/reservas", json=_reserva(9999, "2026-10-16T14:00:00", "2026-10-16T16:00:00")
    )

    assert response.status_code == 404
    body = response.json()
    assert body["ok"] is False
    assert body["codigo"] == "NO_ENCONTRADO"
    assert "9999" in body["mensaje"]


@pytest.mark.parametrize(
    "cuerpo",
    [
        {"inicio": "2026-10-16T16:00:00", "fin": "2026-10-16T14:00:00"},  # inicio > fin
        {"inicio": "2026-10-16T14:00:00", "fin": "2026-10-16T14:00:00"},  # inicio == fin
        {"inicio": "2026-10-16T14:00:00Z", "fin": "2026-10-16T16:00:00Z"},  # con zona horaria
        {"asistentes": 0},
        {"responsable": ""},
        {"sala_id": 0},
    ],
)
def test_datos_invalidos_devuelven_422_con_el_formato_estandar(client, sala, cuerpo):
    base = _reserva(sala.id, "2026-10-16T14:00:00", "2026-10-16T16:00:00")

    response = client.post("/api/reservas", json={**base, **cuerpo})

    assert response.status_code == 422
    body = response.json()
    assert body["ok"] is False
    assert body["codigo"] == "DATOS_INVALIDOS"


def test_crear_reserva_sin_campos_obligatorios_devuelve_422(client):
    response = client.post("/api/reservas", json={})

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"


# --- GET /api/reservas ------------------------------------------------------------------


def test_listar_reservas_ordenadas_por_inicio_y_filtradas_por_sala(client, db: Session, sala):
    otra = Sala(nombre="Otra sala", aforo=20)
    db.add(otra)
    db.commit()
    db.refresh(otra)
    tarde = _reserva(sala.id, "2026-10-16T16:00:00", "2026-10-16T17:00:00")
    temprano = _reserva(sala.id, "2026-10-16T08:00:00", "2026-10-16T09:00:00")
    ajena = _reserva(otra.id, "2026-10-16T10:00:00", "2026-10-16T11:00:00")
    for cuerpo in (tarde, temprano, ajena):
        assert client.post("/api/reservas", json=cuerpo).status_code == 201

    todas = client.get("/api/reservas").json()
    de_la_sala = client.get(f"/api/reservas?sala_id={sala.id}").json()

    assert todas["ok"] is True and len(todas["data"]) == 3
    assert [r["inicio"] for r in de_la_sala["data"]] == [
        "2026-10-16T08:00:00",
        "2026-10-16T16:00:00",
    ]


def test_listar_reservas_con_sala_id_invalido_devuelve_422(client):
    response = client.get("/api/reservas?sala_id=0")

    assert response.status_code == 422
    assert response.json()["codigo"] == "DATOS_INVALIDOS"


def test_listar_reservas_vacio(client):
    assert client.get("/api/reservas").json() == {"ok": True, "data": []}


# --- Contrato general -------------------------------------------------------------------


def test_health_sigue_disponible(client):
    assert client.get("/health").json()["status"] == "healthy"


def test_swagger_documenta_los_endpoints_de_la_api(client):
    rutas = client.get("/openapi.json").json()["paths"]

    assert "get" in rutas["/api/salas"]
    assert {"get", "post"} <= set(rutas["/api/reservas"])
