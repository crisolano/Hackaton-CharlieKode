from app.core.config import EquipoEstado, SalaEstado
from app.core.errors import RecursoNoDisponible


def validar_sala_disponible(sala_id: int, estado: str) -> None:
    """
    Regla R3 (salas): no se puede reservar una sala inhabilitada.
    Lanza RecursoNoDisponible si la sala no está activa.
    """
    if estado != SalaEstado.ACTIVA.value:
        raise RecursoNoDisponible(recurso="sala", id=sala_id, detalles={"estado": estado})


def validar_equipo_disponible(equipo_id: int, estado: str) -> None:
    """
    Regla R3 (equipos): solo se puede prestar un equipo disponible.
    Lanza RecursoNoDisponible si está prestado, dañado o inhabilitado.
    """
    if estado != EquipoEstado.DISPONIBLE.value:
        raise RecursoNoDisponible(recurso="equipo", id=equipo_id, detalles={"estado": estado})
