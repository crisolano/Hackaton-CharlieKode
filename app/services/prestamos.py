from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import EquipoEstado
from app.core.errors import DatosInvalidos, NoEncontrado, RecursoNoDisponible
from app.models import Equipo, Prestamo
from app.rules import validar_equipo_disponible
from app.schemas import PrestamoCreate


def obtener_equipo(db: Session, equipo_id: int) -> Equipo:
    """
    Obtiene un equipo por su ID. Lanza NoEncontrado si no existe.
    """
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if equipo is None:
        raise NoEncontrado(recurso="equipo", id=equipo_id)
    return equipo


def listar_equipos(
    db: Session, estado: str | None = None, limit: int = 100, offset: int = 0
) -> list[Equipo]:
    """
    Lista todos los equipos registrados, opcionalmente filtrados por estado.
    """
    query = db.query(Equipo)
    if estado is not None:
        query = query.filter(Equipo.estado == estado)
    return query.order_by(Equipo.nombre.asc()).offset(offset).limit(limit).all()


def obtener_prestamo(db: Session, prestamo_id: int) -> Prestamo:
    """
    Obtiene un préstamo por su ID. Lanza NoEncontrado si no existe.
    """
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if prestamo is None:
        raise NoEncontrado(recurso="prestamo", id=prestamo_id)
    return prestamo


def listar_prestamos(
    db: Session,
    equipo_id: int | None = None,
    solo_activos: bool = False,
) -> list[Prestamo]:
    """
    Lista préstamos registrados, con filtro opcional por equipo o por estado activo.
    """
    query = db.query(Prestamo)
    if equipo_id is not None:
        query = query.filter(Prestamo.equipo_id == equipo_id)
    if solo_activos:
        query = query.filter(Prestamo.devuelto_en.is_(None))
    return query.order_by(Prestamo.fecha_inicio.desc()).all()


def crear_prestamo(
    db: Session,
    datos: PrestamoCreate,
    fecha_inicio: datetime | None = None,
) -> Prestamo:
    """
    Registra un nuevo préstamo de equipo aplicando la regla de negocio R3:
    - El equipo debe existir y estar disponible (no prestado, dañado o inhabilitado).
    - Cambia el estado del equipo a PRESTADO.
    """
    equipo = obtener_equipo(db, datos.equipo_id)

    # Validar regla R3 para equipos
    validar_equipo_disponible(equipo_id=equipo.id, estado=equipo.estado)

    ahora = fecha_inicio or datetime.now()

    if datos.fecha_devolucion <= ahora:
        raise DatosInvalidos(
            mensaje="La fecha estimada de devolución debe ser posterior al inicio del préstamo."
        )

    # Cambio atómico: si otra petición ganó la carrera, 0 filas y se rechaza (R3).
    filas = (
        db.query(Equipo)
        .filter(Equipo.id == equipo.id, Equipo.estado == EquipoEstado.DISPONIBLE.value)
        .update({"estado": EquipoEstado.PRESTADO.value}, synchronize_session=False)
    )
    if filas == 0:
        db.rollback()
        raise RecursoNoDisponible(recurso="equipo", id=datos.equipo_id)

    nuevo_prestamo = Prestamo(
        equipo_id=datos.equipo_id,
        solicitante=datos.solicitante,
        fecha_inicio=ahora,
        fecha_devolucion=datos.fecha_devolucion,
        devuelto_en=None,
    )

    db.add(nuevo_prestamo)
    db.commit()
    db.refresh(nuevo_prestamo)
    db.refresh(equipo)

    return nuevo_prestamo


def registrar_devolucion(
    db: Session,
    prestamo_id: int,
    fecha_devolucion_real: datetime | None = None,
) -> Prestamo:
    """
    Registra la devolución de un préstamo de equipo:
    - Verifica que el préstamo exista.
    - Valida que no haya sido devuelto previamente.
    - Actualiza devuelto_en con la fecha actual o provista.
    - Cambia el estado del equipo nuevamente a DISPONIBLE.
    """
    prestamo = obtener_prestamo(db, prestamo_id)

    ahora = fecha_devolucion_real or datetime.now()
    # Cierre atómico: solo una petición puede devolver el mismo préstamo.
    filas = (
        db.query(Prestamo)
        .filter(Prestamo.id == prestamo_id, Prestamo.devuelto_en.is_(None))
        .update({"devuelto_en": ahora}, synchronize_session=False)
    )
    if filas == 0:
        db.rollback()
        raise DatosInvalidos(mensaje=f"El préstamo #{prestamo_id} ya fue devuelto.")

    equipo = obtener_equipo(db, prestamo.equipo_id)
    equipo.estado = EquipoEstado.DISPONIBLE.value

    db.commit()
    db.refresh(prestamo)
    db.refresh(equipo)

    return prestamo
