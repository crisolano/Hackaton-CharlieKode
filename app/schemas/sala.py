from pydantic import BaseModel, ConfigDict, Field

from app.core.config import SalaEstado


class SalaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    aforo: int = Field(..., gt=0)
    estado: SalaEstado = SalaEstado.ACTIVA


class SalaCreate(SalaBase):
    pass


class SalaRead(SalaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
