from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.ai.base import AIClient
from app.ai.triage import triar_incidencia
from app.core.config import IncidenciaEstado
from app.core.errors import DatosInvalidos, NoEncontrado
from app.models import Incidencia
from app.schemas import IncidenciaCreate


def obtener_incidencia(db: Session, incidencia_id: int) -> Incidencia:
    """
    Obtiene una incidencia por su ID. Lanza NoEncontrado si no existe.
    """
    incidencia = db.query(Incidencia).filter(Incidencia.id == incidencia_id).first()
    if incidencia is None:
        raise NoEncontrado(recurso="incidencia", id=incidencia_id)
    return incidencia


def listar_incidencias(
    db: Session,
    estado: str | None = None,
    categoria: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Incidencia]:
    """
    Lista las incidencias registradas con filtros opcionales por estado y/o categoría.
    """
    query = db.query(Incidencia)
    if estado is not None:
        query = query.filter(Incidencia.estado == estado)
    if categoria is not None:
        query = query.filter(Incidencia.categoria == categoria)
    return query.order_by(Incidencia.id.desc()).offset(offset).limit(limit).all()


def crear_incidencia(
    db: Session,
    datos: IncidenciaCreate,
    ai_client: AIClient | None = None,
) -> Incidencia:
    """
    Registra y persiste una incidencia en texto libre.

    Si se provee un cliente de IA (`ai_client`), intenta realizar el triaje inteligente.
    Si el cliente no se proporciona, o si falla (timeout, error de proveedor o formato inválido),
    la incidencia queda guardada con estado `pendiente_revision` y `origen_ia=False`,
    asegurando que el sistema nunca invente clasificaciones fijas.
    """
    texto = datos.texto.strip()
    if not texto:
        raise DatosInvalidos(mensaje="El texto de la incidencia no puede estar vacío.")

    nueva_incidencia = Incidencia(
        texto=texto,
        categoria=None,
        prioridad=None,
        ruta=None,
        estado=IncidenciaEstado.PENDIENTE_REVISION.value,
        origen_ia=False,
    )

    if ai_client is not None:
        # triar_incidencia ya convierte los fallos de la IA en `pendiente_revision`.
        resultado = triar_incidencia(texto, ai_client)
        nueva_incidencia.categoria = resultado.categoria
        nueva_incidencia.prioridad = resultado.prioridad
        nueva_incidencia.ruta = resultado.ruta
        nueva_incidencia.estado = resultado.estado
        nueva_incidencia.origen_ia = resultado.origen_ia

    db.add(nueva_incidencia)
    db.commit()
    db.refresh(nueva_incidencia)
    return nueva_incidencia


def actualizar_estado_incidencia(
    db: Session,
    incidencia_id: int,
    nuevo_estado: str,
) -> Incidencia:
    """
    Actualiza el estado de una incidencia (ej. clasificada -> en_proceso -> resuelta).
    """
    incidencia = obtener_incidencia(db, incidencia_id)
    estados_validos = {e.value for e in IncidenciaEstado}
    if nuevo_estado not in estados_validos:
        raise DatosInvalidos(mensaje=f"Estado de incidencia no válido: '{nuevo_estado}'")

    incidencia.estado = nuevo_estado
    db.commit()
    db.refresh(incidencia)
    return incidencia
