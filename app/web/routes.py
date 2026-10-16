from pathlib import Path
from typing import NamedTuple

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings

WEB_DIR = Path(__file__).resolve().parent
STATIC_DIR = WEB_DIR / "static"

templates = Jinja2Templates(directory=WEB_DIR / "templates")


class NavItem(NamedTuple):
    label: str
    href: str


# Secciones de la navegación común; cada sprint agrega las suyas aquí (tupla inmutable).
NAV_ITEMS: tuple[NavItem, ...] = ()

router = APIRouter(include_in_schema=False)


def render(request: Request, template: str, **context) -> HTMLResponse:
    """Renderiza una plantilla con el contexto común (nombre del proyecto y navegación)."""
    context.setdefault("project_name", settings.PROJECT_NAME)
    context.setdefault("nav_items", NAV_ITEMS)
    return templates.TemplateResponse(request, template, context)


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return render(request, "index.html")
