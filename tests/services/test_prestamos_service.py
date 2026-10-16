from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.core.config import EquipoEstado
from app.core.errors import DatosInvalidos, NoEncontrado, RecursoNoDisponible
from app.models import Equipo
from app.schemas import PrestamoCreate
from app.services.prestamos import (
    crear_prestamo,
    listar_equipos,
    listar_prestamos,
    obtener_equipo,
    registrar_devolucion,
)


def test_obtener_equipo_existente_e_inexistente(db: Session):
    eq = Equipo(nombre="Laptop #1", estado=EquipoEstado.DISPONIBLE.value)
    db.add(eq)
    db.commit()
    db.refresh(eq)

    encontrado = obtener_equipo(db, eq.id)
    assert encontrado.nombre == "Laptop #1"

    with pytest.raises(NoEncontrado) as exc_info:
        obtener_equipo(db, 9999)
    assert exc_info.value.codigo == "NO_ENCONTRADO"


def test_listar_equipos_y_filtro_por_estado(db: Session):
    db.add_all(
        [
            Equipo(nombre="Equipo A", estado=EquipoEstado.DISPONIBLE.value),
            Equipo(nombre="Equipo B", estado=EquipoEstado.PRESTADO.value),
            Equipo(nombre="Equipo C", estado=EquipoEstado.DISPONIBLE.value),
        ]
    )
    db.commit()

    todos = listar_equipos(db)
    assert len(todos) == 3

    disponibles = listar_equipos(db, estado=EquipoEstado.DISPONIBLE.value)
    assert len(disponibles) == 2
    assert all(e.estado == EquipoEstado.DISPONIBLE.value for e in disponibles)


def test_crear_prestamo_exitoso_cambia_estado(db: Session):
    eq = Equipo(nombre="Proyector Sala 1", estado=EquipoEstado.DISPONIBLE.value)
    db.add(eq)
    db.commit()
    db.refresh(eq)

    inicio = datetime(2026, 10, 16, 10, 0)
    fin_previsto = inicio + timedelta(hours=4)

    datos = PrestamoCreate(
        equipo_id=eq.id,
        solicitante="Maria Becerra",
        fecha_devolucion=fin_previsto,
    )

    prestamo = crear_prestamo(db, datos, fecha_inicio=inicio)

    assert prestamo.id is not None
    assert prestamo.solicitante == "Maria Becerra"
    assert prestamo.devuelto_en is None
    # El equipo debe pasar a estado PRESTADO
    db.refresh(eq)
    assert eq.estado == EquipoEstado.PRESTADO.value


def test_crear_prestamo_rechazo_r3_equipo_ya_prestado(db: Session):
    eq = Equipo(nombre="Camara Reflex", estado=EquipoEstado.DISPONIBLE.value)
    db.add(eq)
    db.commit()
    db.refresh(eq)

    inicio = datetime(2026, 10, 16, 10, 0)
    fin = inicio + timedelta(days=1)

    datos = PrestamoCreate(
        equipo_id=eq.id,
        solicitante="Juan Perez",
        fecha_devolucion=fin,
    )
    crear_prestamo(db, datos, fecha_inicio=inicio)

    # Segundo intento con el mismo equipo debe fallar por R3
    with pytest.raises(RecursoNoDisponible) as exc_info:
        crear_prestamo(
            db,
            PrestamoCreate(
                equipo_id=eq.id,
                solicitante="Otro Solicitante",
                fecha_devolucion=fin + timedelta(days=1),
            ),
            fecha_inicio=inicio + timedelta(hours=1),
        )

    assert exc_info.value.codigo == "RECURSO_NO_DISPONIBLE"
    assert exc_info.value.detalles == {"estado": EquipoEstado.PRESTADO.value}


def test_crear_prestamo_rechazo_equipo_inhabilitado_o_danado(db: Session):
    eq_danado = Equipo(nombre="Microfono Roto", estado=EquipoEstado.DANADO.value)
    eq_inhab = Equipo(nombre="Parlante Bloqueado", estado=EquipoEstado.INHABILITADO.value)
    db.add_all([eq_danado, eq_inhab])
    db.commit()

    fin = datetime.now() + timedelta(days=2)

    with pytest.raises(RecursoNoDisponible):
        crear_prestamo(
            db,
            PrestamoCreate(equipo_id=eq_danado.id, solicitante="A", fecha_devolucion=fin),
        )

    with pytest.raises(RecursoNoDisponible):
        crear_prestamo(
            db,
            PrestamoCreate(equipo_id=eq_inhab.id, solicitante="B", fecha_devolucion=fin),
        )


def test_crear_prestamo_fecha_devolucion_invalida(db: Session):
    eq = Equipo(nombre="Tablet 1", estado=EquipoEstado.DISPONIBLE.value)
    db.add(eq)
    db.commit()

    inicio = datetime(2026, 10, 16, 12, 0)
    fin_pasado = inicio - timedelta(hours=1)

    with pytest.raises(DatosInvalidos):
        crear_prestamo(
            db,
            PrestamoCreate(equipo_id=eq.id, solicitante="Ana", fecha_devolucion=fin_pasado),
            fecha_inicio=inicio,
        )


def test_registrar_devolucion_exitosa(db: Session):
    eq = Equipo(nombre="Kit Arduino", estado=EquipoEstado.DISPONIBLE.value)
    db.add(eq)
    db.commit()

    inicio = datetime(2026, 10, 16, 8, 0)
    fin = inicio + timedelta(days=1)
    prestamo = crear_prestamo(
        db,
        PrestamoCreate(equipo_id=eq.id, solicitante="Carlos", fecha_devolucion=fin),
        fecha_inicio=inicio,
    )

    fecha_real_devolucion = inicio + timedelta(hours=5)
    prestamo_devuelto = registrar_devolucion(
        db, prestamo.id, fecha_devolucion_real=fecha_real_devolucion
    )

    assert prestamo_devuelto.devuelto_en == fecha_real_devolucion
    db.refresh(eq)
    # Debe volver a DISPONIBLE
    assert eq.estado == EquipoEstado.DISPONIBLE.value


def test_registrar_devolucion_ya_devuelto_o_inexistente(db: Session):
    with pytest.raises(NoEncontrado):
        registrar_devolucion(db, prestamo_id=9999)

    eq = Equipo(nombre="Pizarra Wacom", estado=EquipoEstado.DISPONIBLE.value)
    db.add(eq)
    db.commit()

    prestamo = crear_prestamo(
        db,
        PrestamoCreate(
            equipo_id=eq.id,
            solicitante="Diana",
            fecha_devolucion=datetime.now() + timedelta(days=1),
        ),
    )
    registrar_devolucion(db, prestamo.id)

    # Segundo intento debe dar error de datos invalidos
    with pytest.raises(DatosInvalidos):
        registrar_devolucion(db, prestamo.id)


def test_listar_prestamos_filtros(db: Session):
    eq1 = Equipo(nombre="Eq 1", estado=EquipoEstado.DISPONIBLE.value)
    eq2 = Equipo(nombre="Eq 2", estado=EquipoEstado.DISPONIBLE.value)
    db.add_all([eq1, eq2])
    db.commit()

    p1 = crear_prestamo(
        db,
        PrestamoCreate(
            equipo_id=eq1.id,
            solicitante="S1",
            fecha_devolucion=datetime.now() + timedelta(days=1),
        ),
    )
    p2 = crear_prestamo(
        db,
        PrestamoCreate(
            equipo_id=eq2.id,
            solicitante="S2",
            fecha_devolucion=datetime.now() + timedelta(days=2),
        ),
    )

    registrar_devolucion(db, p1.id)

    todos = listar_prestamos(db)
    assert len(todos) == 2

    activos = listar_prestamos(db, solo_activos=True)
    assert len(activos) == 1
    assert activos[0].id == p2.id

    por_eq1 = listar_prestamos(db, equipo_id=eq1.id)
    assert len(por_eq1) == 1
    assert por_eq1[0].id == p1.id
