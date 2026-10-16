import re

from pydantic import BaseModel, ValidationError

from app.ai.base import AIClient, AIError
from app.ai.prompts import build_triage_prompt
from app.core.config import (
    IncidenciaCategoria,
    IncidenciaEstado,
    IncidenciaPrioridad,
    IncidenciaRuta,
)

_CERCAS_MARKDOWN = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


class SalidaTriaje(BaseModel):
    """Salida esperada del modelo; cualquier valor fuera de las enumeraciones se rechaza."""

    categoria: IncidenciaCategoria
    prioridad: IncidenciaPrioridad
    ruta: IncidenciaRuta


class ResultadoTriaje(BaseModel):
    categoria: IncidenciaCategoria | None
    prioridad: IncidenciaPrioridad | None
    ruta: IncidenciaRuta
    estado: IncidenciaEstado
    origen_ia: bool


def _pendiente_revision() -> ResultadoTriaje:
    """La IA falló o respondió algo inválido: no se inventa clasificación."""
    return ResultadoTriaje(
        categoria=None,
        prioridad=None,
        ruta=IncidenciaRuta.REVISION_MANUAL,
        estado=IncidenciaEstado.PENDIENTE_REVISION,
        origen_ia=False,
    )


def clasificar_incidencia(texto: str, client: AIClient) -> ResultadoTriaje:
    try:
        bruto = client.generate(build_triage_prompt(texto))
        salida = SalidaTriaje.model_validate_json(_CERCAS_MARKDOWN.sub("", bruto.strip()))
    except (AIError, ValidationError):
        return _pendiente_revision()
    return ResultadoTriaje(
        categoria=salida.categoria,
        prioridad=salida.prioridad,
        ruta=salida.ruta,
        estado=IncidenciaEstado.CLASIFICADA,
        origen_ia=True,
    )
