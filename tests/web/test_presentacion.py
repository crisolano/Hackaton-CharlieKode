from datetime import datetime

from app.core.config import SalaEstado
from app.models import Reserva, Sala
from app.web.presentacion import (
    construir_reservas_vista,
    construir_resumen,
    construir_salas_vista,
    estado_reserva,
    formatear_fecha_hora,
    formatear_hora,
)

AHORA = datetime(2026, 10, 16, 15, 0)


def _sala(id_, nombre="Sala", estado=SalaEstado.ACTIVA.value):
    return Sala(id=id_, nombre=nombre, aforo=10, estado=estado)


def _reserva(sala_id, inicio_h, fin_h):
    return Reserva(
        sala_id=sala_id,
        inicio=datetime(2026, 10, 16, inicio_h),
        fin=datetime(2026, 10, 16, fin_h),
        asistentes=1,
        responsable="x",
    )


def test_sala_sin_reservas_esta_libre():
    (vista,) = construir_salas_vista([_sala(1)], [], AHORA)
    assert vista.activa and not vista.ocupada_ahora
    assert vista.proxima is None and vista.reservas_pendientes == 0


def test_reserva_en_curso_marca_ocupada_hasta_el_fin():
    (vista,) = construir_salas_vista([_sala(1)], [_reserva(1, 14, 16)], AHORA)
    assert vista.ocupada_ahora
    assert vista.ocupada_hasta == datetime(2026, 10, 16, 16)


def test_el_fin_de_una_reserva_ya_no_ocupa_la_sala():
    (vista,) = construir_salas_vista([_sala(1)], [_reserva(1, 13, 15)], AHORA)
    assert not vista.ocupada_ahora
    assert vista.reservas_pendientes == 0


def test_proxima_reserva_es_la_primera_futura_de_esa_sala():
    reservas = [_reserva(1, 18, 19), _reserva(1, 16, 17), _reserva(2, 15, 16)]
    vistas = construir_salas_vista([_sala(1), _sala(2)], reservas, AHORA)
    assert vistas[0].proxima.inicio.hour == 16
    assert vistas[0].reservas_pendientes == 2
    assert vistas[1].ocupada_ahora


def test_sala_inhabilitada_no_es_activa():
    (vista,) = construir_salas_vista([_sala(1, estado=SalaEstado.INHABILITADA.value)], [], AHORA)
    assert not vista.activa


def test_resumen_cuenta_salas_y_reservas_pendientes():
    salas = [_sala(1), _sala(2, estado=SalaEstado.INHABILITADA.value)]
    vistas = construir_salas_vista(salas, [_reserva(1, 16, 17), _reserva(1, 9, 10)], AHORA)
    resumen = construir_resumen(vistas)
    assert (resumen.total_salas, resumen.salas_activas, resumen.reservas_pendientes) == (2, 1, 1)


def test_fecha_hora_en_espanol_sin_depender_del_locale():
    assert formatear_fecha_hora(datetime(2026, 10, 20, 10, 0)) == "mar 20 oct, 10:00"
    assert formatear_fecha_hora(datetime(2026, 1, 4, 9, 5)) == "dom 4 ene, 09:05"
    assert formatear_fecha_hora(datetime(2026, 12, 31, 23, 59)) == "jue 31 dic, 23:59"
    assert formatear_fecha_hora(None) == ""


def test_hora_sola():
    assert formatear_hora(datetime(2026, 10, 20, 7, 3)) == "07:03"
    assert formatear_hora(None) == ""


def test_estado_de_reserva_finalizada_en_curso_y_proxima():
    assert estado_reserva(_reserva(1, 13, 15), AHORA) == "finalizada"  # termina justo ahora
    assert estado_reserva(_reserva(1, 14, 16), AHORA) == "en_curso"
    assert estado_reserva(_reserva(1, 15, 16), AHORA) == "en_curso"  # empieza justo ahora
    assert estado_reserva(_reserva(1, 16, 17), AHORA) == "proxima"


def test_reservas_vista_trae_etiqueta_y_clase_de_cada_estado():
    reservas = [_reserva(1, 9, 10), _reserva(1, 14, 16), _reserva(1, 18, 19)]
    vistas = construir_reservas_vista(reservas, AHORA)
    assert [v.etiqueta for v in vistas] == ["Finalizada", "En curso", "Próxima"]
    assert [v.clase for v in vistas] == ["badge-off", "badge-ok", "badge-soon"]


def test_libre_hasta_solo_si_la_proxima_reserva_es_hoy_y_la_sala_esta_libre():
    (hoy,) = construir_salas_vista([_sala(1)], [_reserva(1, 18, 19)], AHORA)
    assert hoy.libre_hasta == datetime(2026, 10, 16, 18)
    manana = Reserva(
        sala_id=1,
        inicio=datetime(2026, 10, 17, 9),
        fin=datetime(2026, 10, 17, 10),
        asistentes=1,
        responsable="x",
    )
    (otro_dia,) = construir_salas_vista([_sala(1)], [manana], AHORA)
    assert otro_dia.libre_hasta is None
    reservas = [_reserva(1, 14, 16), _reserva(1, 18, 19)]
    (ocupada,) = construir_salas_vista([_sala(1)], reservas, AHORA)
    assert ocupada.libre_hasta is None
