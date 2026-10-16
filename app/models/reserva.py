from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.sala import Sala


class Reserva(Base):
    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sala_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("salas.id"), index=True, nullable=False
    )
    inicio: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    fin: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    asistentes: Mapped[int] = mapped_column(Integer, nullable=False)
    responsable: Mapped[str] = mapped_column(String(150), nullable=False)

    sala: Mapped["Sala"] = relationship("Sala", back_populates="reservas")
