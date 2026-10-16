from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.errors import MSG_ERROR_TIMEZONE


class PrestamoCreate(BaseModel):
    equipo_id: int = Field(..., gt=0)
    solicitante: str = Field(..., min_length=1, max_length=150)
    fecha_devolucion: datetime

    @model_validator(mode="after")
    def validar_fecha(self) -> "PrestamoCreate":
        if self.fecha_devolucion.tzinfo is not None:
            raise ValueError(MSG_ERROR_TIMEZONE)
        return self


class PrestamoRead(BaseModel):
    id: int
    equipo_id: int
    solicitante: str
    fecha_inicio: datetime
    fecha_devolucion: datetime
    devuelto_en: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
