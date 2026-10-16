from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.core.config import SalaEstado
from app.core.errors import AforoExcedido, NoEncontrado, RecursoNoDisponible, SalaOcupada
from app.models import Reserva, Sala
from app.schemas import ReservaCreate
from app.services import (
    crear_reserva,
    listar_reservas,
    listar_salas,
    obtener_sala,
)


def test_obtener_sala_exitosa(db: Session):
    sala = Sala(nombre="Sala Mock", aforo=20)
    db.add(sala)
    db.commit()
    db.refresh(sala)

    resultado = obtener_sala(db, sala.id)
    assert resultado.id == sala.id
    assert resultado.nombre == "Sala Mock"


def test_obtener_sala_inexistente(db: Session):
    with pytest.raises(NoEncontrado) as exc_info:
        obtener_sala(db, 9999)
    assert exc_info.value.codigo == "NO_ENCONTRADO"
    assert exc_info.value.status_code == 404
    assert "9999" in exc_info.value.mensaje


def test_listar_salas(db: Session):
    sala_b = Sala(nombre="Beta Sala", aforo=15)
    sala_a = Sala(nombre="Alfa Sala", aforo=25)
    db.add_all([sala_b, sala_a])
    db.commit()

    salas = listar_salas(db)
    nombres = [s.nombre for s in salas]
    assert nombres == ["Alfa Sala", "Beta Sala"]


def test_crear_reserva_exitosa(db: Session):
    sala = Sala(nombre="Sala Innovacion", aforo=30)
    db.add(sala)
    db.commit()
    db.refresh(sala)

    datos = ReservaCreate(
        sala_id=sala.id,
        inicio=datetime(2026, 10, 16, 9, 0),
        fin=datetime(2026, 10, 16, 11, 0),
        asistentes=25,
        responsable="Santiago Perez",
    )
    reserva = crear_reserva(db, datos)

    assert reserva.id is not None
    assert reserva.sala_id == sala.id
    assert reserva.asistentes == 25
    assert reserva.responsable == "Santiago Perez"

    # Verificar persistencia en base de datos
    guardada = db.query(Reserva).filter(Reserva.id == reserva.id).first()
    assert guardada is not None
    assert guardada.asistentes == 25


def test_crear_reserva_sala_inexistente(db: Session):
    datos = ReservaCreate(
        sala_id=888,
        inicio=datetime(2026, 10, 16, 9, 0),
        fin=datetime(2026, 10, 16, 11, 0),
        asistentes=5,
        responsable="Tester",
    )
    with pytest.raises(NoEncontrado):
        crear_reserva(db, datos)

    assert db.query(Reserva).count() == 0


def test_crear_reserva_rechazo_aforo(db: Session):
    sala = Sala(nombre="Sala Pequena", aforo=10)
    db.add(sala)
    db.commit()
    db.refresh(sala)

    datos = ReservaCreate(
        sala_id=sala.id,
        inicio=datetime(2026, 10, 16, 14, 0),
        fin=datetime(2026, 10, 16, 16, 0),
        asistentes=12,  # Excede aforo de 10
        responsable="Grupo Grande",
    )
    with pytest.raises(AforoExcedido) as exc_info:
        crear_reserva(db, datos)

    assert exc_info.value.codigo == "AFORO_EXCEDIDO"
    assert "Sala Pequena" in exc_info.value.mensaje
    # Integridad: no debe persistirse ninguna reserva
    assert db.query(Reserva).count() == 0


def test_crear_reserva_rechazo_solapamiento(db: Session):
    sala = Sala(nombre="Sala Concurrente", aforo=50)
    db.add(sala)
    db.commit()
    db.refresh(sala)

    # Primera reserva: 10:00 a 12:00
    reserva1 = ReservaCreate(
        sala_id=sala.id,
        inicio=datetime(2026, 10, 16, 10, 0),
        fin=datetime(2026, 10, 16, 12, 0),
        asistentes=20,
        responsable="Primera Reserva",
    )
    crear_reserva(db, reserva1)

    # Intento de segunda reserva: 11:00 a 13:00 (se solapa)
    reserva2 = ReservaCreate(
        sala_id=sala.id,
        inicio=datetime(2026, 10, 16, 11, 0),
        fin=datetime(2026, 10, 16, 13, 0),
        asistentes=20,
        responsable="Segunda Reserva Conflicto",
    )
    with pytest.raises(SalaOcupada) as exc_info:
        crear_reserva(db, reserva2)

    assert exc_info.value.codigo == "SALA_OCUPADA"
    assert "Sala Concurrente" in exc_info.value.mensaje
    # Solo debe existir la primera reserva
    assert db.query(Reserva).count() == 1


def test_crear_reserva_horarios_contiguos_exitosa(db: Session):
    sala = Sala(nombre="Sala Horarios", aforo=40)
    db.add(sala)
    db.commit()
    db.refresh(sala)

    # Reserva 1: 08:00 a 10:00
    r1 = crear_reserva(
        db,
        ReservaCreate(
            sala_id=sala.id,
            inicio=datetime(2026, 10, 16, 8, 0),
            fin=datetime(2026, 10, 16, 10, 0),
            asistentes=15,
            responsable="Bloque 1",
        ),
    )
    # Reserva 2 inmediatamente después: 10:00 a 12:00
    r2 = crear_reserva(
        db,
        ReservaCreate(
            sala_id=sala.id,
            inicio=datetime(2026, 10, 16, 10, 0),
            fin=datetime(2026, 10, 16, 12, 0),
            asistentes=15,
            responsable="Bloque 2",
        ),
    )

    assert r1.id is not None
    assert r2.id is not None
    assert db.query(Reserva).count() == 2


def test_crear_reserva_mismo_horario_salas_distintas(db: Session):
    sala1 = Sala(nombre="Sala A", aforo=20)
    sala2 = Sala(nombre="Sala B", aforo=20)
    db.add_all([sala1, sala2])
    db.commit()
    db.refresh(sala1)
    db.refresh(sala2)

    mismo_inicio = datetime(2026, 10, 16, 14, 0)
    mismo_fin = datetime(2026, 10, 16, 16, 0)

    r1 = crear_reserva(
        db,
        ReservaCreate(
            sala_id=sala1.id,
            inicio=mismo_inicio,
            fin=mismo_fin,
            asistentes=10,
            responsable="Equipo 1",
        ),
    )
    r2 = crear_reserva(
        db,
        ReservaCreate(
            sala_id=sala2.id,
            inicio=mismo_inicio,
            fin=mismo_fin,
            asistentes=10,
            responsable="Equipo 2",
        ),
    )

    assert r1.id != r2.id
    assert db.query(Reserva).count() == 2


def test_listar_reservas_y_filtro(db: Session):
    sala1 = Sala(nombre="Sala Uno", aforo=30)
    sala2 = Sala(nombre="Sala Dos", aforo=30)
    db.add_all([sala1, sala2])
    db.commit()
    db.refresh(sala1)
    db.refresh(sala2)

    crear_reserva(
        db,
        ReservaCreate(
            sala_id=sala1.id,
            inicio=datetime(2026, 10, 16, 10, 0),
            fin=datetime(2026, 10, 16, 11, 0),
            asistentes=5,
            responsable="User 1",
        ),
    )
    crear_reserva(
        db,
        ReservaCreate(
            sala_id=sala2.id,
            inicio=datetime(2026, 10, 16, 9, 0),
            fin=datetime(2026, 10, 16, 10, 0),
            asistentes=5,
            responsable="User 2",
        ),
    )

    todas = listar_reservas(db)
    assert len(todas) == 2
    # Ordenadas por inicio: la de las 09:00 viene primero
    assert todas[0].responsable == "User 2"
    assert todas[1].responsable == "User 1"

    solo_sala1 = listar_reservas(db, sala_id=sala1.id)
    assert len(solo_sala1) == 1
    assert solo_sala1[0].responsable == "User 1"


def test_crear_reserva_rechazo_sala_inhabilitada(db: Session):
    sala = Sala(nombre="Sala Mantenimiento", aforo=20, estado=SalaEstado.INHABILITADA.value)
    db.add(sala)
    db.commit()
    db.refresh(sala)

    reserva = ReservaCreate(
        sala_id=sala.id,
        inicio=datetime(2026, 10, 16, 10, 0),
        fin=datetime(2026, 10, 16, 12, 0),
        asistentes=5,
        responsable="Responsable Test",
    )

    with pytest.raises(RecursoNoDisponible) as exc_info:
        crear_reserva(db, reserva)

    assert exc_info.value.codigo == "RECURSO_NO_DISPONIBLE"
    assert exc_info.value.detalles == {"estado": SalaEstado.INHABILITADA.value}
    assert db.query(Reserva).count() == 0
