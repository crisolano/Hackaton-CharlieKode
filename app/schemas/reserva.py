from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

MSG_ERROR_RANGO_HORARIO = "La fecha de inicio debe ser anterior a la fecha de fin."
MSG_ERROR_TIMEZONE = "Las fechas de reserva deben ser en hora local sin zona horaria (naive)."


class ReservaBase(BaseModel):
    sala_id: int = Field(..., gt=0)
    inicio: datetime
    fin: datetime
    asistentes: int = Field(..., ge=1)
    responsable: str = Field(..., min_length=1, max_length=150)

    @model_validator(mode="after")
    def validar_fechas(self) -> "ReservaBase":
        if self.inicio.tzinfo is not None or self.fin.tzinfo is not None:
            raise ValueError(MSG_ERROR_TIMEZONE)
        if self.inicio >= self.fin:
            raise ValueError(MSG_ERROR_RANGO_HORARIO)
        return self


class ReservaCreate(ReservaBase):
    pass


class ReservaRead(ReservaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
