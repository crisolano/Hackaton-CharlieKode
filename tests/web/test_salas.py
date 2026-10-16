import html

from app.core.errors import MSG_ERROR_RANGO_HORARIO
from app.models import Reserva
from tests.web.conftest import HTMX


def _datos(sala, **cambios):
    datos = {
        "sala_id": str(sala.id),
        "inicio": "2026-10-16T14:00",
        "fin": "2026-10-16T16:00",
        "asistentes": "5",
        "responsable": "Ana Pérez",
    }
    datos.update(cambios)
    return datos


def test_pagina_salas_muestra_la_tabla_y_el_selector_desde_la_bd(client, salas_de_prueba):
    r = client.get("/salas")
    assert r.status_code == 200
    for sala in salas_de_prueba:
        assert f'<h3 class="text-lg font-semibold leading-tight">{sala.nombre}</h3>' in r.text
        assert f"Aforo: hasta <strong>{sala.aforo}</strong> personas" in r.text
        assert f'<option value="{sala.id}" data-aforo="{sala.aforo}">' in r.text
        assert f"{sala.nombre} — aforo {sala.aforo}" in r.text


def test_pagina_salas_sin_datos_no_inventa_salas(client):
    r = client.get("/salas")
    assert r.status_code == 200
    assert "Todavía no hay salas registradas." in r.text
    assert '<option value="1"' not in r.text


def test_navegacion_incluye_espacios(client):
    r = client.get("/")
    assert 'href="/salas"' in r.text


def test_reserva_valida_devuelve_parcial_de_exito_y_persiste(client, db, salas_de_prueba):
    r = client.post("/salas/reservar", data=_datos(salas_de_prueba[0]), headers=HTMX)
    assert r.status_code == 200
    assert "¡Reserva confirmada!" in r.text
    assert "Ya aparece en la lista de reservas." in r.text
    assert 'hx-swap-oob="true"' in r.text
    assert db.query(Reserva).count() == 1


def test_aforo_excedido_muestra_el_error_en_pantalla(client, db, salas_de_prueba):
    datos = _datos(salas_de_prueba[0], asistentes="30")
    r = client.post("/salas/reservar", data=datos, headers=HTMX)
    assert r.status_code == 422
    assert 'data-codigo="AFORO_EXCEDIDO"' in r.text
    assert "Sala Uno" in r.text
    assert db.query(Reserva).count() == 0


def test_solapamiento_muestra_sala_ocupada(client, db, salas_de_prueba):
    sala = salas_de_prueba[0]
    assert client.post("/salas/reservar", data=_datos(sala), headers=HTMX).status_code == 200
    r = client.post("/salas/reservar", data=_datos(sala, inicio="2026-10-16T15:00"), headers=HTMX)
    assert r.status_code == 409
    assert 'data-codigo="SALA_OCUPADA"' in r.text
    assert "Esa sala ya está reservada" in r.text
    assert db.query(Reserva).count() == 1


def test_reservas_contiguas_no_se_solapan(client, salas_de_prueba):
    sala = salas_de_prueba[0]
    client.post("/salas/reservar", data=_datos(sala), headers=HTMX)
    contigua = _datos(sala, inicio="2026-10-16T16:00", fin="2026-10-16T17:00")
    assert client.post("/salas/reservar", data=contigua, headers=HTMX).status_code == 200


def test_rango_horario_invalido_muestra_el_mensaje_del_esquema(client, salas_de_prueba):
    datos = _datos(salas_de_prueba[0], inicio="2026-10-16T16:00", fin="2026-10-16T14:00")
    r = client.post("/salas/reservar", data=datos, headers=HTMX)
    assert r.status_code == 422
    assert 'data-codigo="DATOS_INVALIDOS"' in r.text
    assert MSG_ERROR_RANGO_HORARIO in r.text
    assert 'data-campo="inicio fin"' in r.text


def test_formulario_vacio_devuelve_datos_invalidos_sin_eco_de_entrada(client):
    r = client.post("/salas/reservar", data={"responsable": "x-dato-enviado"}, headers=HTMX)
    assert r.status_code == 422
    assert 'data-codigo="DATOS_INVALIDOS"' in r.text
    assert 'Revisa "Sala": elige una sala de la lista.' in html.unescape(r.text)
    assert 'data-campo="sala_id"' in r.text
    assert "x-dato-enviado" not in r.text


def test_sala_inexistente_devuelve_no_encontrado(client, salas_de_prueba):
    r = client.post("/salas/reservar", data=_datos(salas_de_prueba[0], sala_id="999"), headers=HTMX)
    assert r.status_code == 404
    assert 'data-codigo="NO_ENCONTRADO"' in r.text


def test_responsable_se_escapa_en_la_respuesta(client, salas_de_prueba):
    datos = _datos(salas_de_prueba[0], responsable="<script>alert(1)</script>")
    r = client.post("/salas/reservar", data=datos, headers=HTMX)
    assert r.status_code == 200
    assert "<script>alert(1)</script>" not in r.text
    assert "&lt;script&gt;" in r.text


def test_formulario_declara_post_como_respaldo_sin_htmx(client, salas_de_prueba):
    html = client.get("/salas").text
    assert 'method="post"' in html
    assert 'action="/salas/reservar"' in html


def _errores_de(**cambios):
    from pydantic import ValidationError

    from app.schemas import ReservaCreate
    from app.web.routes import _campos_con_error, _mensaje_validacion

    datos = {
        "sala_id": "1",
        "inicio": "2026-10-16T14:00",
        "fin": "2026-10-16T16:00",
        "asistentes": "5",
        "responsable": "Ana",
    }
    datos.update(cambios)
    try:
        ReservaCreate(**datos)
    except ValidationError as exc:
        return _mensaje_validacion(exc), _campos_con_error(exc)
    raise AssertionError("se esperaba un error de validación")


def test_mapeo_de_campos_a_mensajes_con_la_etiqueta_visible():
    mensaje, campos = _errores_de(asistentes="")
    assert mensaje == 'Revisa "Número de asistentes": escribe un número entero de 1 o más.'
    assert campos == ("asistentes",)
    assert _errores_de(asistentes="0")[0] == mensaje
    assert _errores_de(sala_id="") == ('Revisa "Sala": elige una sala de la lista.', ("sala_id",))
    assert _errores_de(responsable="") == (
        'Revisa "Responsable": escribe el nombre.',
        ("responsable",),
    )
    mensaje, campos = _errores_de(inicio="", fin="")
    assert mensaje == 'Revisa "Inicio" y "Fin": indica fecha y hora completas.'
    assert campos == ("inicio", "fin")


def test_mapeo_conserva_el_mensaje_del_esquema_para_el_rango_horario():
    mensaje, campos = _errores_de(inicio="2026-10-16T16:00", fin="2026-10-16T14:00")
    assert mensaje == MSG_ERROR_RANGO_HORARIO
    assert campos == ("inicio", "fin")


def test_responsable_demasiado_largo_indica_el_maximo():
    mensaje, campos = _errores_de(responsable="x" * 151)
    assert mensaje == 'Revisa "Responsable": usa 150 caracteres como máximo.'
    assert campos == ("responsable",)


def test_la_api_json_no_cambia_con_el_mapeo_de_campos(client, salas_de_prueba):
    r = client.post("/salas/reservar", data={"sala_id": "x"})
    assert r.status_code == 422
    assert r.json()["codigo"] == "DATOS_INVALIDOS"
    assert "campos" not in r.json()
    assert "data-campo" not in r.text


def test_fechas_de_la_web_usan_el_formato_legible(client, db, salas_de_prueba):
    client.post("/salas/reservar", data=_datos(salas_de_prueba[0]), headers=HTMX)
    r = client.get("/salas")
    assert "vie 16 oct, 14:00" in r.text
    assert "2026-10-16 14:00" not in r.text
