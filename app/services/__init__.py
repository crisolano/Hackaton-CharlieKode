from app.services.prestamos import (
    crear_prestamo,
    listar_equipos,
    listar_prestamos,
    obtener_equipo,
    obtener_prestamo,
    registrar_devolucion,
)
from app.services.reservas import (
    crear_reserva,
    listar_reservas,
    listar_salas,
    obtener_sala,
)

__all__ = [
    "crear_reserva",
    "listar_reservas",
    "listar_salas",
    "obtener_sala",
    "obtener_equipo",
    "listar_equipos",
    "obtener_prestamo",
    "listar_prestamos",
    "crear_prestamo",
    "registrar_devolucion",
]
