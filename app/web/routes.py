import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated, NamedTuple

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.errors import ERROR_MESSAGES, AppException, DatosInvalidos
from app.schemas import ReservaCreate
from app.services.reservas import crear_reserva, listar_reservas, listar_salas
from app.web.presentacion import (
    construir_reservas_vista,
    construir_resumen,
    construir_salas_vista,
    formatear_fecha_hora,
    formatear_hora,
)

logger = logging.getLogger(__name__)

WEB_DIR = Path(__file__).resolve().parent
STATIC_DIR = WEB_DIR / "static"

templates = Jinja2Templates(directory=WEB_DIR / "templates")
templates.env.filters["fecha_hora"] = formatear_fecha_hora
templates.env.filters["hora"] = formatear_hora

_HUELLAS_ESTATICOS: dict[str, str | None] = {}


def huella_estatico(nombre: str, directorio: Path = STATIC_DIR) -> str | None:
    """Hash corto del contenido de un estático; None si el archivo no existe."""
    try:
        contenido = (directorio / nombre).read_bytes()
    except OSError:
        return None
    return hashlib.sha256(contenido).hexdigest()[:10]


def estatico(nombre: str) -> str:
    """Ruta relativa de un estático con ?v=<hash> para invalidar la caché del navegador.

    El hash se calcula la primera vez que se pide cada archivo y se reutiliza (los
    estáticos no cambian mientras el proceso está en marcha; un despliegue lo reinicia).
    """
    if nombre not in _HUELLAS_ESTATICOS:
        _HUELLAS_ESTATICOS[nombre] = huella_estatico(nombre)
    huella = _HUELLAS_ESTATICOS[nombre]
    ruta = f"/static/{nombre}"
    return f"{ruta}?v={huella}" if huella else ruta


templates.env.globals["estatico"] = estatico


class NavItem(NamedTuple):
    label: str
    href: str
    descripcion: str = ""


class SeccionPendiente(NamedTuple):
    label: str
    descripcion: str


# Secciones de la navegación común; cada sprint agrega las suyas aquí (tupla inmutable).
NAV_ITEMS: tuple[NavItem, ...] = (
    NavItem(
        "Espacios",
        "/salas",
        "Consulta la disponibilidad de las salas y reserva con aforo y horario validados.",
    ),
    # Una línea por sección (Equipos, Incidencias...): evita conflictos de merge.
)

# Secciones previstas que todavía no tienen pantalla operativa; al implementarlas se
# mueven a NAV_ITEMS. Se muestran como "próximamente" para no aparentar funciones que no existen.
SECCIONES_PENDIENTES: tuple[SeccionPendiente, ...] = (
    SeccionPendiente(
        "Equipos",
        "Préstamo y devolución de equipos tecnológicos con seguimiento de su estado.",
    ),
    SeccionPendiente(
        "Incidencias",
        "Registro de incidencias en texto libre con clasificación asistida por IA.",
    ),
)

router = APIRouter(include_in_schema=False)


def render(request: Request, template: str, status_code: int = 200, **context) -> HTMLResponse:
    """Renderiza una plantilla con el contexto común (nombre del proyecto y navegación)."""
    context.setdefault("project_name", settings.PROJECT_NAME)
    context.setdefault("nav_items", NAV_ITEMS)
    context.setdefault("secciones_pendientes", SECCIONES_PENDIENTES)
    context.setdefault("mensaje_error_generico", ERROR_MESSAGES["ERROR_INTERNO"])
    return templates.TemplateResponse(request, template, context, status_code=status_code)


def _contexto_espacios(db: Session, ahora: datetime) -> dict:
    """Salas con su disponibilidad y reservas para pintar; lanza SQLAlchemyError si falla la BD."""
    salas = listar_salas(db)
    reservas = listar_reservas(db)
    vistas = construir_salas_vista(salas, reservas, ahora)
    return {
        "salas": salas,
        "salas_vista": vistas,
        "reservas": reservas,
        "reservas_vista": construir_reservas_vista(reservas, ahora),
        "resumen": construir_resumen(vistas),
    }


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    try:
        contexto = _contexto_espacios(db, datetime.now())
    except SQLAlchemyError:
        logger.exception("No se pudo leer el estado de los espacios para la portada")
        return render(request, "index.html", resumen=None, bd_error=True)
    return render(request, "index.html", resumen=contexto["resumen"], bd_error=False)


# Campos del formulario de reserva: etiqueta visible y qué debe hacer la persona.
_MENSAJE_FECHAS = 'Revisa "Inicio" y "Fin": indica fecha y hora completas.'
_MENSAJES_CAMPO = {
    "sala_id": 'Revisa "Sala": elige una sala de la lista.',
    "asistentes": 'Revisa "Número de asistentes": escribe un número entero de 1 o más.',
    "inicio": _MENSAJE_FECHAS,
    "fin": _MENSAJE_FECHAS,
    "responsable": 'Revisa "Responsable": escribe el nombre.',
}
_GRUPO_FECHAS = ("inicio", "fin")


def _campo_de(detalle: dict) -> str | None:
    loc = detalle.get("loc") or ()
    return loc[0] if loc and loc[0] in _MENSAJES_CAMPO else None


def _mensaje_validacion(error: ValidationError) -> str | None:
    """Mensaje para la persona de un error de esquema; None si no hay uno más específico.

    Las reglas del esquema (p. ej. rango horario) conservan su mensaje; los errores de un
    campo se explican con la etiqueta visible de ese campo en el formulario.
    """
    detalles = error.errors()
    for detalle in detalles:
        if detalle["type"] == "value_error":
            return str(detalle["ctx"]["error"])
    for detalle in detalles:
        campo = _campo_de(detalle)
        if campo is None:
            continue
        if campo == "responsable" and detalle["type"] == "string_too_long":
            maximo = detalle["ctx"]["max_length"]
            return f'Revisa "Responsable": usa {maximo} caracteres como máximo.'
        return _MENSAJES_CAMPO[campo]
    return None


def _campos_con_error(error: ValidationError) -> tuple[str, ...]:
    """Campos del formulario que la interfaz debe marcar y enfocar (orden del esquema)."""
    detalles = error.errors()
    if any(d["type"] == "value_error" for d in detalles):
        return _GRUPO_FECHAS
    campos = [c for c in dict.fromkeys(_campo_de(d) for d in detalles) if c]
    if not campos:
        return ()
    grupo = _GRUPO_FECHAS if campos[0] in _GRUPO_FECHAS else (campos[0],)
    return tuple(c for c in campos if c in grupo)


@router.get("/salas", response_class=HTMLResponse)
def salas(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    try:
        contexto = _contexto_espacios(db, datetime.now())
    except SQLAlchemyError:
        logger.exception("No se pudo leer salas y reservas")
        return render(
            request,
            "salas.html",
            status_code=503,
            salas=[],
            salas_vista=[],
            reservas=[],
            bd_error=True,
        )
    return render(request, "salas.html", bd_error=False, **contexto)


@router.post("/salas/reservar", response_class=HTMLResponse)
def reservar(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    sala_id: Annotated[str, Form()] = "",
    inicio: Annotated[str, Form()] = "",
    fin: Annotated[str, Form()] = "",
    asistentes: Annotated[str, Form()] = "",
    responsable: Annotated[str, Form()] = "",
) -> HTMLResponse:
    """Crea la reserva con el servicio; los errores de dominio llegan al manejador HTMX."""
    try:
        datos = ReservaCreate(
            sala_id=sala_id,
            inicio=inicio,
            fin=fin,
            asistentes=asistentes,
            responsable=responsable,
        )
    except ValidationError as exc:
        invalido = DatosInvalidos(mensaje=_mensaje_validacion(exc))
        # Solo lo usa el parcial HTML (marcar el campo); el JSON de la API no cambia.
        invalido.campos = _campos_con_error(exc)
        raise invalido from exc
    try:
        reserva = crear_reserva(db, datos)
        contexto = _contexto_espacios(db, datetime.now())
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Fallo de base de datos al crear la reserva")
        raise AppException(
            codigo="ERROR_INTERNO",
            mensaje=ERROR_MESSAGES["ERROR_INTERNO"],
            status_code=503,
        ) from exc
    return render(request, "partials/reserva_ok.html", reserva=reserva, **contexto)
