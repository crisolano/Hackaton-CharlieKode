from datetime import datetime

import pytest

from app.core.errors import SalaOcupada
from app.rules import rango_se_solapa, validar_solapamiento


def test_rango_se_solapa_reservas_contiguas():
    # Reserva A: 08:00 - 10:00, Reserva B: 10:00 - 12:00
    r1_inicio = datetime(2026, 10, 16, 8, 0)
    r1_fin = datetime(2026, 10, 16, 10, 0)
    r2_inicio = datetime(2026, 10, 16, 10, 0)
    r2_fin = datetime(2026, 10, 16, 12, 0)

    # Contigua posterior: no se solapa
    assert rango_se_solapa(r1_inicio, r1_fin, r2_inicio, r2_fin) is False
    # Contigua anterior: no se solapa
    assert rango_se_solapa(r2_inicio, r2_fin, r1_inicio, r1_fin) is False


def test_solapamiento_horario_distinto():
    # Reservas en momentos totalmente separados
    reservas_existentes = [
        (datetime(2026, 10, 16, 8, 0), datetime(2026, 10, 16, 10, 0)),
        (datetime(2026, 10, 16, 14, 0), datetime(2026, 10, 16, 16, 0)),
    ]
    # Nueva reserva entre las 11:00 y las 13:00 (espacio libre)
    validar_solapamiento(
        inicio=datetime(2026, 10, 16, 11, 0),
        fin=datetime(2026, 10, 16, 13, 0),
        reservas_existentes=reservas_existentes,
        nombre_sala="Sala Apolo Test",
    )


def test_solapamiento_lista_vacia():
    # Sala sin ninguna reserva previa
    validar_solapamiento(
        inicio=datetime(2026, 10, 16, 8, 0),
        fin=datetime(2026, 10, 16, 10, 0),
        reservas_existentes=[],
        nombre_sala="Sala Vacia",
    )


def test_solapamiento_exacto():
    # Mismo horario que una reserva existente
    r_inicio = datetime(2026, 10, 16, 10, 0)
    r_fin = datetime(2026, 10, 16, 12, 0)
    reservas_existentes = [(r_inicio, r_fin)]

    with pytest.raises(SalaOcupada) as exc_info:
        validar_solapamiento(
            inicio=r_inicio,
            fin=r_fin,
            reservas_existentes=reservas_existentes,
            nombre_sala="Auditorio Test",
        )

    error = exc_info.value
    assert error.codigo == "SALA_OCUPADA"
    assert error.status_code == 409
    assert "Auditorio Test" in error.mensaje


def test_solapamiento_parcial_inicio():
    # Existente: 10:00 - 12:00. Nueva: 11:00 - 13:00 (se solapa de 11:00 a 12:00)
    reservas_existentes = [(datetime(2026, 10, 16, 10, 0), datetime(2026, 10, 16, 12, 0))]

    with pytest.raises(SalaOcupada):
        validar_solapamiento(
            inicio=datetime(2026, 10, 16, 11, 0),
            fin=datetime(2026, 10, 16, 13, 0),
            reservas_existentes=reservas_existentes,
            nombre_sala="Sala Alfa",
        )


def test_solapamiento_parcial_fin():
    # Existente: 10:00 - 12:00. Nueva: 09:00 - 11:00 (se solapa de 10:00 a 11:00)
    reservas_existentes = [(datetime(2026, 10, 16, 10, 0), datetime(2026, 10, 16, 12, 0))]

    with pytest.raises(SalaOcupada):
        validar_solapamiento(
            inicio=datetime(2026, 10, 16, 9, 0),
            fin=datetime(2026, 10, 16, 11, 0),
            reservas_existentes=reservas_existentes,
            nombre_sala="Sala Alfa",
        )


def test_solapamiento_nueva_engloba_existente():
    # Existente: 10:00 - 12:00. Nueva: 08:00 - 14:00 (engloba completamente a la existente)
    reservas_existentes = [(datetime(2026, 10, 16, 10, 0), datetime(2026, 10, 16, 12, 0))]

    with pytest.raises(SalaOcupada):
        validar_solapamiento(
            inicio=datetime(2026, 10, 16, 8, 0),
            fin=datetime(2026, 10, 16, 14, 0),
            reservas_existentes=reservas_existentes,
            nombre_sala="Sala Alfa",
        )


def test_solapamiento_nueva_contenida_en_existente():
    # Existente: 08:00 - 14:00. Nueva: 10:00 - 12:00 (está dentro de la existente)
    reservas_existentes = [(datetime(2026, 10, 16, 8, 0), datetime(2026, 10, 16, 14, 0))]

    with pytest.raises(SalaOcupada):
        validar_solapamiento(
            inicio=datetime(2026, 10, 16, 10, 0),
            fin=datetime(2026, 10, 16, 12, 0),
            reservas_existentes=reservas_existentes,
            nombre_sala="Sala Alfa",
        )
