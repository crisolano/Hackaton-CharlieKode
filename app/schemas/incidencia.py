from pydantic import BaseModel, ConfigDict, Field

from app.core.config import (
    IncidenciaCategoria,
    IncidenciaEstado,
    IncidenciaPrioridad,
    IncidenciaRuta,
)


class IncidenciaCreate(BaseModel):
    texto: str = Field(..., min_length=1)


class IncidenciaRead(BaseModel):
    id: int
    texto: str
    categoria: IncidenciaCategoria | None = None
    prioridad: IncidenciaPrioridad | None = None
    ruta: IncidenciaRuta | None = None
    estado: IncidenciaEstado
    origen_ia: bool

    model_config = ConfigDict(from_attributes=True)
