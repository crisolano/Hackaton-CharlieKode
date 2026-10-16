from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.equipo import Equipo


class Prestamo(Base):
    __tablename__ = "prestamos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("equipos.id"), index=True, nullable=False
    )
    solicitante: Mapped[str] = mapped_column(String(150), nullable=False)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # Fecha prevista de devolución (la envía el solicitante al prestar).
    fecha_devolucion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # Se rellena al registrar la devolución; None mientras el préstamo siga activo.
    devuelto_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    equipo: Mapped["Equipo"] = relationship("Equipo", back_populates="prestamos")
