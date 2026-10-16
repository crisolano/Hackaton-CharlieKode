from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import EquipoEstado, IncidenciaEstado
from app.models import Equipo, Incidencia, Prestamo
from app.schemas import (
    EquipoCreate,
    EquipoRead,
    IncidenciaCreate,
    IncidenciaRead,
    PrestamoCreate,
    PrestamoRead,
)


def test_equipo_estado_por_defecto_y_relacion(db: Session):
    equipo = Equipo(nombre="Proyector 1")
    db.add(equipo)
    db.commit()
    db.refresh(equipo)

    assert equipo.id is not None
    assert equipo.estado == EquipoEstado.DISPONIBLE.value
    assert equipo.prestamos == []


def test_nombre_equipo_unico(db: Session):
    db.add(Equipo(nombre="Portatil 1"))
    db.commit()
    db.add(Equipo(nombre="Portatil 1"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_prestamo_relacionado_con_equipo(db: Session):
    equipo = Equipo(nombre="Camara 1")
    db.add(equipo)
    db.commit()
    ahora = datetime(2026, 10, 16, 10, 0)
    prestamo = Prestamo(
        equipo_id=equipo.id,
        solicitante="Luis Gomez",
        fecha_inicio=ahora,
        fecha_devolucion=ahora + timedelta(days=1),
    )
    db.add(prestamo)
    db.commit()
    db.refresh(equipo)

    assert equipo.prestamos[0].solicitante == "Luis Gomez"
    assert equipo.prestamos[0].devuelto_en is None
    assert prestamo.equipo.nombre == "Camara 1"


def test_incidencia_pendiente_por_defecto(db: Session):
    incidencia = Incidencia(texto="El proyector no enciende")
    db.add(incidencia)
    db.commit()
    db.refresh(incidencia)

    assert incidencia.estado == IncidenciaEstado.PENDIENTE_REVISION.value
    assert incidencia.origen_ia is False
    assert incidencia.categoria is None
    assert incidencia.prioridad is None
    assert incidencia.ruta is None


def test_incidencia_read_valida_valores_permitidos(db: Session):
    incidencia = Incidencia(
        texto="Sin red",
        categoria="red",
        prioridad="alta",
        ruta="soporte_tecnico",
        estado="clasificada",
        origen_ia=True,
    )
    db.add(incidencia)
    db.commit()
    db.refresh(incidencia)

    leida = IncidenciaRead.model_validate(incidencia)
    assert leida.categoria == "red"
    assert leida.ruta == "soporte_tecnico"

    with pytest.raises(ValidationError):
        IncidenciaRead(id=1, texto="x", categoria="inventada", estado="clasificada", origen_ia=True)


def test_esquemas_equipo(db: Session):
    with pytest.raises(ValidationError):
        EquipoCreate(nombre="")
    with pytest.raises(ValidationError):
        EquipoCreate(nombre="X", estado="roto")

    equipo = Equipo(nombre="Tablet 1")
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    assert EquipoRead.model_validate(equipo).estado == EquipoEstado.DISPONIBLE


def test_esquemas_prestamo_e_incidencia_create():
    with pytest.raises(ValidationError):
        PrestamoCreate(equipo_id=0, solicitante="A", fecha_devolucion=datetime(2026, 10, 17))
    with pytest.raises(ValidationError):
        PrestamoCreate(equipo_id=1, solicitante="", fecha_devolucion=datetime(2026, 10, 17))
    with pytest.raises(ValidationError):
        IncidenciaCreate(texto="")

    ok = PrestamoCreate(equipo_id=1, solicitante="A", fecha_devolucion=datetime(2026, 10, 17))
    assert ok.equipo_id == 1
    assert PrestamoRead.model_fields["devuelto_en"].default is None
