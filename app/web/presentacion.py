"""Datos derivados solo para mostrar en pantalla (no contienen reglas de negocio).

La capa web consulta los servicios y aquí se calcula únicamente lo que la interfaz
necesita enseñar: si una sala está en uso en este momento, cuál es su próxima reserva
cuántas reservas pendientes tiene, en qué estado está cada reserva y cómo se escriben
las fechas en español. Quién puede reservar y cuándo lo deciden las
reglas de `app/rules`, no este módulo.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from app.core.config import SalaEstado
from app.models import Reserva, Sala


@dataclass(frozen=True)
class SalaVista:
    sala: Sala
    activa: bool
    ocupada_ahora: bool
    ocupada_hasta: datetime | None
    proxima: Reserva | None
    reservas_pendientes: int
    # Solo si la sala está libre y su próxima reserva es hoy: hasta qué hora sigue libre.
    libre_hasta: datetime | None = None


@dataclass(frozen=True)
class ResumenEspacios:
    total_salas: int
    salas_activas: int
    reservas_pendientes: int


def construir_salas_vista(
    salas: Sequence[Sala], reservas: Sequence[Reserva], ahora: datetime
) -> list[SalaVista]:
    """Resume la disponibilidad de cada sala en el instante `ahora` (hora local sin zona)."""
    vistas: list[SalaVista] = []
    for sala in salas:
        propias = sorted((r for r in reservas if r.sala_id == sala.id), key=lambda r: r.inicio)
        en_curso = next((r for r in propias if r.inicio <= ahora < r.fin), None)
        proxima = next((r for r in propias if r.inicio > ahora), None)
        vistas.append(
            SalaVista(
                sala=sala,
                activa=sala.estado == SalaEstado.ACTIVA.value,
                ocupada_ahora=en_curso is not None,
                ocupada_hasta=en_curso.fin if en_curso else None,
                proxima=proxima,
                reservas_pendientes=sum(1 for r in propias if r.fin > ahora),
                libre_hasta=(
                    proxima.inicio
                    if en_curso is None and proxima and proxima.inicio.date() == ahora.date()
                    else None
                ),
            )
        )
    return vistas


def construir_resumen(vistas: Sequence[SalaVista]) -> ResumenEspacios:
    return ResumenEspacios(
        total_salas=len(vistas),
        salas_activas=sum(1 for v in vistas if v.activa),
        reservas_pendientes=sum(v.reservas_pendientes for v in vistas),
    )


# Textos y clases de la insignia de estado de cada reserva (solo presentación).
_ESTADOS_RESERVA = {
    "en_curso": ("En curso", "badge-ok"),
    "proxima": ("Próxima", "badge-soon"),
    "finalizada": ("Finalizada", "badge-off"),
}


@dataclass(frozen=True)
class ReservaVista:
    reserva: Reserva
    estado: str
    etiqueta: str
    clase: str


def estado_reserva(reserva: Reserva, ahora: datetime) -> str:
    """'en_curso', 'proxima' o 'finalizada' según el instante `ahora`."""
    if reserva.inicio > ahora:
        return "proxima"
    if reserva.fin > ahora:
        return "en_curso"
    return "finalizada"


def construir_reservas_vista(reservas: Sequence[Reserva], ahora: datetime) -> list[ReservaVista]:
    vistas: list[ReservaVista] = []
    for reserva in reservas:
        estado = estado_reserva(reserva, ahora)
        etiqueta, clase = _ESTADOS_RESERVA[estado]
        vistas.append(ReservaVista(reserva, estado, etiqueta, clase))
    return vistas


# Nombres propios para no depender del idioma del servidor (locale).
DIAS_SEMANA = ("lun", "mar", "mié", "jue", "vie", "sáb", "dom")
MESES = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")


def formatear_fecha_hora(valor: datetime | None) -> str:
    """Fecha legible en español, p. ej. 'mar 20 oct, 10:00'."""
    if valor is None:
        return ""
    dia = DIAS_SEMANA[valor.weekday()]
    return f"{dia} {valor.day} {MESES[valor.month - 1]}, {valor:%H:%M}"


def formatear_hora(valor: datetime | None) -> str:
    return "" if valor is None else f"{valor:%H:%M}"
