from pydantic import BaseModel, ConfigDict, Field

from app.core.config import EquipoEstado


class EquipoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    estado: EquipoEstado = EquipoEstado.DISPONIBLE


class EquipoCreate(EquipoBase):
    pass


class EquipoRead(EquipoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
