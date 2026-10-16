from collections.abc import Iterable
from datetime import datetime

from app.core.errors import AforoExcedido, SalaOcupada


def rango_se_solapa(
    inicio_a: datetime, fin_a: datetime, inicio_b: datetime, fin_b: datetime
) -> bool:
    """
    Determina si dos rangos horarios se solapan.
    Dos reservas contiguas (donde fin_a == inicio_b o fin_b == inicio_a) NO se solapan.
    """
    return inicio_a < fin_b and fin_a > inicio_b


def validar_aforo(asistentes: int, aforo_maximo: int, nombre_sala: str) -> None:
    """
    Regla R1: Los asistentes no deben superar el aforo máximo de la sala.
    Lanza AforoExcedido con mensaje formateado si se excede la capacidad.
    """
    if asistentes > aforo_maximo:
        raise AforoExcedido(sala=nombre_sala, aforo=aforo_maximo, asistentes=asistentes)


def validar_solapamiento(
    inicio: datetime,
    fin: datetime,
    reservas_existentes: Iterable[tuple[datetime, datetime]],
    nombre_sala: str,
) -> None:
    """
    Regla R2: No debe haber solapamiento de horario en la misma sala.
    Lanza SalaOcupada con el rango en conflicto al primer cruce encontrado.
    """
    for r_inicio, r_fin in reservas_existentes:
        if rango_se_solapa(inicio, fin, r_inicio, r_fin):
            raise SalaOcupada(sala=nombre_sala, inicio=r_inicio, fin=r_fin)
