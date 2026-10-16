from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import IncidenciaEstado
from app.core.database import Base


class Incidencia(Base):
    __tablename__ = "incidencias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    # Nulos mientras la incidencia esté pendiente de revisión (la IA no clasificó).
    categoria: Mapped[str | None] = mapped_column(String(20), nullable=True)
    prioridad: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ruta: Mapped[str | None] = mapped_column(String(30), nullable=True)
    estado: Mapped[str] = mapped_column(
        String(30), default=IncidenciaEstado.PENDIENTE_REVISION.value, index=True, nullable=False
    )
    origen_ia: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
