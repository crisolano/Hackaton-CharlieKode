from sqlalchemy.orm import Session

from app.core.errors import NoEncontrado
from app.models import Reserva, Sala
from app.rules import validar_aforo, validar_sala_disponible, validar_solapamiento
from app.schemas import ReservaCreate


def obtener_sala(db: Session, sala_id: int) -> Sala:
    """
    Obtiene una sala por su ID. Lanza NoEncontrado si no existe.
    """
    sala = db.query(Sala).filter(Sala.id == sala_id).first()
    if sala is None:
        raise NoEncontrado(recurso="sala", id=sala_id)
    return sala


def listar_salas(db: Session) -> list[Sala]:
    """
    Lista todas las salas registradas, ordenadas por nombre.
    """
    return db.query(Sala).order_by(Sala.nombre.asc()).all()


def crear_reserva(db: Session, datos: ReservaCreate) -> Reserva:
    """
    Crea y persiste una nueva reserva aplicando las reglas de negocio:
    - R1: Aforo máximo permitido.
    - R2: Sin solapamiento de horarios en la misma sala.
    """
    sala = obtener_sala(db, datos.sala_id)

    # Regla R3: la sala debe estar activa
    validar_sala_disponible(sala_id=sala.id, estado=sala.estado)

    # Regla R1: Validar capacidad de la sala
    validar_aforo(
        asistentes=datos.asistentes,
        aforo_maximo=sala.aforo,
        nombre_sala=sala.nombre,
    )

    # Regla R2: Validar solapamiento con reservas existentes de la sala
    reservas_existentes = db.query(Reserva).filter(Reserva.sala_id == sala.id).all()
    intervalos = [(r.inicio, r.fin) for r in reservas_existentes]
    validar_solapamiento(
        inicio=datos.inicio,
        fin=datos.fin,
        reservas_existentes=intervalos,
        nombre_sala=sala.nombre,
    )

    nueva_reserva = Reserva(
        sala_id=datos.sala_id,
        inicio=datos.inicio,
        fin=datos.fin,
        asistentes=datos.asistentes,
        responsable=datos.responsable,
    )
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    return nueva_reserva


def listar_reservas(db: Session, sala_id: int | None = None) -> list[Reserva]:
    """
    Lista las reservas registradas, con filtro opcional por sala, ordenadas por fecha de inicio.
    """
    query = db.query(Reserva)
    if sala_id is not None:
        query = query.filter(Reserva.sala_id == sala_id)
    return query.order_by(Reserva.inicio.asc()).all()
