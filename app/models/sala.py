from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import SalaEstado
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.reserva import Reserva


class Sala(Base):
    __tablename__ = "salas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    aforo: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default=SalaEstado.ACTIVA.value, nullable=False)

    reservas: Mapped[list["Reserva"]] = relationship(
        "Reserva", back_populates="sala", cascade="all, delete-orphan"
    )
