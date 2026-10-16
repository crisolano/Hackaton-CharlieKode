from pathlib import Path
from typing import Annotated, NamedTuple

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.errors import DatosInvalidos
from app.schemas import ReservaCreate
from app.services.reservas import crear_reserva, listar_reservas, listar_salas

WEB_DIR = Path(__file__).resolve().parent
STATIC_DIR = WEB_DIR / "static"

FORMATO_FECHA_HORA = "%Y-%m-%d %H:%M"

templates = Jinja2Templates(directory=WEB_DIR / "templates")
templates.env.filters["fecha_hora"] = lambda valor: valor.strftime(FORMATO_FECHA_HORA)


class NavItem(NamedTuple):
    label: str
    href: str


# Secciones de la navegación común; cada sprint agrega las suyas aquí (tupla inmutable).
NAV_ITEMS: tuple[NavItem, ...] = (
    NavItem("Espacios", "/salas"),
    # Una línea por sección (Equipos, Incidencias...): evita conflictos de merge.
)

router = APIRouter(include_in_schema=False)


def render(request: Request, template: str, **context) -> HTMLResponse:
    """Renderiza una plantilla con el contexto común (nombre del proyecto y navegación)."""
    context.setdefault("project_name", settings.PROJECT_NAME)
    context.setdefault("nav_items", NAV_ITEMS)
    return templates.TemplateResponse(request, template, context)


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    """Muestra la vista de bienvenida e inicio de la aplicación web."""
    return render(request, "index.html")


def _mensaje_validacion(error: ValidationError) -> str | None:
    """Mensaje de una regla de esquema (p. ej. rango horario); None si es un error de tipo."""
    for detalle in error.errors():
        if detalle["type"] == "value_error":
            return str(detalle["ctx"]["error"])
    return None


@router.get("/salas", response_class=HTMLResponse)
def salas(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    return render(request, "salas.html", salas=listar_salas(db), reservas=listar_reservas(db))


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
        raise DatosInvalidos(mensaje=_mensaje_validacion(exc)) from exc
    reserva = crear_reserva(db, datos)
    return render(
        request, "partials/reserva_ok.html", reserva=reserva, reservas=listar_reservas(db)
    )
