from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import SalaEstado
from app.models import Reserva, Sala
from app.schemas import ReservaCreate, ReservaRead, SalaCreate, SalaRead


def test_persistencia_sala(db: Session):
    nueva_sala = Sala(nombre="Sala Pruebas", aforo=25, estado=SalaEstado.ACTIVA.value)
    db.add(nueva_sala)
    db.commit()
    db.refresh(nueva_sala)

    assert nueva_sala.id is not None
    assert nueva_sala.nombre == "Sala Pruebas"
    assert nueva_sala.aforo == 25
    assert nueva_sala.estado == SalaEstado.ACTIVA.value
    assert nueva_sala.reservas == []


def test_nombre_sala_unico(db: Session):
    sala1 = Sala(nombre="Sala Unica", aforo=10)
    db.add(sala1)
    db.commit()

    sala2 = Sala(nombre="Sala Unica", aforo=15)
    db.add(sala2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_persistencia_reserva_y_relacion(db: Session):
    sala = Sala(nombre="Sala Con Reservas", aforo=30)
    db.add(sala)
    db.commit()
    db.refresh(sala)

    reserva = Reserva(
        sala_id=sala.id,
        inicio=datetime(2026, 10, 16, 10, 0),
        fin=datetime(2026, 10, 16, 12, 0),
        asistentes=20,
        responsable="Carlos Developer",
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)

    assert reserva.id is not None
    assert reserva.sala_id == sala.id
    assert reserva.sala.nombre == "Sala Con Reservas"
    assert len(sala.reservas) == 1
    assert sala.reservas[0].id == reserva.id


def test_schema_sala_valido():
    sala_in = SalaCreate(nombre="Apolo Test", aforo=15)
    assert sala_in.nombre == "Apolo Test"
    assert sala_in.aforo == 15
    assert sala_in.estado == SalaEstado.ACTIVA

    sala_read = SalaRead(id=1, nombre="Apolo Test", aforo=15, estado=SalaEstado.ACTIVA)
    assert sala_read.id == 1


def test_schema_reserva_valido():
    reserva_in = ReservaCreate(
        sala_id=1,
        inicio=datetime(2026, 10, 16, 8, 0),
        fin=datetime(2026, 10, 16, 10, 0),
        asistentes=10,
        responsable="Maria Gomez",
    )
    assert reserva_in.sala_id == 1
    assert reserva_in.asistentes == 10

    reserva_read = ReservaRead(
        id=99,
        sala_id=1,
        inicio=datetime(2026, 10, 16, 8, 0),
        fin=datetime(2026, 10, 16, 10, 0),
        asistentes=10,
        responsable="Maria Gomez",
    )
    assert reserva_read.id == 99


def test_schema_reserva_rechaza_asistentes_menor_a_uno():
    with pytest.raises(ValidationError) as exc_info:
        ReservaCreate(
            sala_id=1,
            inicio=datetime(2026, 10, 16, 8, 0),
            fin=datetime(2026, 10, 16, 10, 0),
            asistentes=0,
            responsable="Tester",
        )
    assert "asistentes" in str(exc_info.value)


def test_schema_reserva_rechaza_horario_invalido():
    with pytest.raises(ValidationError) as exc_info:
        ReservaCreate(
            sala_id=1,
            inicio=datetime(2026, 10, 16, 12, 0),
            fin=datetime(2026, 10, 16, 10, 0),
            asistentes=5,
            responsable="Tester",
        )
    assert "La fecha de inicio debe ser anterior a la fecha de fin" in str(exc_info.value)

    # Caso límite: inicio == fin
    with pytest.raises(ValidationError) as exc_info:
        ReservaCreate(
            sala_id=1,
            inicio=datetime(2026, 10, 16, 10, 0),
            fin=datetime(2026, 10, 16, 10, 0),
            asistentes=5,
            responsable="Tester",
        )
    assert "La fecha de inicio debe ser anterior a la fecha de fin" in str(exc_info.value)


def test_schema_reserva_rechaza_fechas_con_timezone():
    with pytest.raises(ValidationError) as exc_info:
        ReservaCreate(
            sala_id=1,
            inicio=datetime(2026, 10, 16, 10, 0, tzinfo=UTC),
            fin=datetime(2026, 10, 16, 12, 0),
            asistentes=5,
            responsable="Tester",
        )
    assert "naive" in str(exc_info.value)
