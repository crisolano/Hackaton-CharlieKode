from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import EquipoEstado
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.prestamo import Prestamo


class Equipo(Base):
    __tablename__ = "equipos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), default=EquipoEstado.DISPONIBLE.value, nullable=False
    )

    prestamos: Mapped[list["Prestamo"]] = relationship(
        "Prestamo", back_populates="equipo", cascade="all, delete-orphan"
    )
