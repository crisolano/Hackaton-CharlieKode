from app.core.errors import ERROR_MESSAGES
from tests.web.conftest import HTMX


def test_portada_orienta_y_enlaza_a_reservar(client, salas_de_prueba):
    r = client.get("/")
    assert r.status_code == 200
    assert 'href="/salas#reservar"' in r.text
    assert "Cómo reservar una sala" in r.text


def test_portada_muestra_el_estado_real_de_la_base(client, salas_de_prueba):
    r = client.get("/")
    assert "Salas registradas" in r.text
    assert '<dd class="text-3xl font-bold">2</dd>' in r.text


def test_portada_sin_salas_explica_como_cargarlas(client):
    r = client.get("/")
    assert "Todavía no hay salas registradas." in r.text
    assert "Para el equipo técnico" in r.text
    assert "python -m app.data.seed" in r.text


def test_incidencias_se_anuncia_como_proximamente_sin_enlace(client):
    r = client.get("/")
    assert r.text.count("Próximamente") == 1
    assert 'href="/equipos"' in r.text
    assert 'href="/incidencias"' not in r.text


def test_navegacion_marca_la_pagina_actual_y_tiene_enlace_de_salto(client):
    r = client.get("/salas")
    assert 'class="skip-link"' in r.text
    assert 'aria-label="Secciones principales"' in r.text
    assert 'href="/salas" class="nav-link"\n           aria-current="page"' in r.text


def test_salas_inhabilitadas_no_ofrecen_reserva(client, db, salas_de_prueba):
    from app.core.config import SalaEstado

    salas_de_prueba[0].estado = SalaEstado.INHABILITADA.value
    db.commit()
    r = client.get("/salas")
    assert "Inhabilitada" in r.text
    assert "Esta sala no admite reservas por ahora." in r.text
    assert f'data-elegir-sala="{salas_de_prueba[0].id}"' not in r.text
    assert f'data-elegir-sala="{salas_de_prueba[1].id}"' in r.text


def test_formulario_tiene_etiquetas_visibles_y_estados_de_carga(client, salas_de_prueba):
    r = client.get("/salas")
    for campo in ("sala_id", "asistentes", "inicio", "fin", "responsable"):
        assert f'<label for="{campo}"' in r.text
    assert 'hx-indicator="#cargando"' in r.text
    assert 'hx-disabled-elt="#btn-reservar"' in r.text
    assert 'data-mensaje-carga="Reservando tu sala…"' in r.text
    assert "Reservando…" in r.text
    assert 'id="ayuda-aforo" class="hint" aria-live="polite"' in r.text


def test_pagina_salas_sin_tablas_responde_503_con_instrucciones(client_sin_tablas):
    r = client_sin_tablas.get("/salas")
    assert r.status_code == 503
    assert "No pudimos cargar la información del campus" in r.text
    assert "Para el equipo técnico" in r.text
    assert "python -m app.data.seed" in r.text


def test_portada_sin_tablas_no_rompe(client_sin_tablas):
    r = client_sin_tablas.get("/")
    assert r.status_code == 200
    assert "No pudimos cargar la información del campus" in r.text


def test_reservar_con_bd_caida_devuelve_parcial_de_error_503(client_sin_tablas):
    datos = {
        "sala_id": "1",
        "inicio": "2026-10-16T14:00",
        "fin": "2026-10-16T16:00",
        "asistentes": "5",
        "responsable": "Ana",
    }
    r = client_sin_tablas.post("/salas/reservar", data=datos, headers=HTMX)
    assert r.status_code == 503
    assert 'data-codigo="ERROR_INTERNO"' in r.text
    assert "Algo salió mal" in r.text
    assert ERROR_MESSAGES["ERROR_INTERNO"] in r.text
    assert "no such table" not in r.text


def test_error_de_dominio_incluye_titulo_por_codigo_sin_codigo_visible(client, salas_de_prueba):
    datos = {
        "sala_id": str(salas_de_prueba[0].id),
        "inicio": "2026-10-16T14:00",
        "fin": "2026-10-16T16:00",
        "asistentes": "99",
        "responsable": "Ana",
    }
    r = client.post("/salas/reservar", data=datos, headers=HTMX)
    assert r.status_code == 422
    assert "Demasiadas personas para esta sala" in r.text
    assert 'data-codigo="AFORO_EXCEDIDO"' in r.text
    assert "Código:" not in r.text


def test_logo_de_marca_se_carga_desde_estaticos_con_texto_alternativo(client):
    r = client.get("/")
    assert "/static/campuslands-casco.png" in r.text
    assert 'alt="Campuslands"' in r.text
    assert "/static/campuslands-logo-transparente.png" in r.text
    assert 'alt="Logo de Campuslands: casco de astronauta y el lema #HackeandoVidas"' in r.text
    import re

    rutas_img = re.findall(r'<img[^>]*\ssrc="([^"]+)"', r.text)
    assert rutas_img and all(ruta.startswith("/static/") for ruta in rutas_img)


def test_los_recursos_del_logo_se_sirven_como_png(client):
    for nombre in (
        "campuslands-casco.png",
        "campuslands-logo-transparente.png",
        "campuslands-logo.png",
    ):
        r = client.get(f"/static/{nombre}")
        assert r.status_code == 200
        assert r.headers["content-type"] == "image/png"


def test_el_logo_derivado_tiene_canal_alfa_y_conserva_proporcion(client):
    import struct

    for nombre, ancho, alto in (
        ("campuslands-casco.png", 45, 36),
        ("campuslands-logo-transparente.png", 166, 200),
    ):
        cabecera = client.get(f"/static/{nombre}").content[:26]
        w, h = struct.unpack(">II", cabecera[16:24])
        tipo_de_color = cabecera[25]
        assert tipo_de_color == 6  # RGBA: el fondo del logo es transparente
        assert abs(w / h - ancho / alto) < 0.02


def test_el_tema_oscuro_esta_declarado(client):
    r = client.get("/")
    assert '<meta name="color-scheme" content="dark">' in r.text
    css = client.get("/static/app.css").text
    for token in ("--bg: #24252b", "--primary: #6b5cff", "--cyan: #00d5e8", "--ink: #f4f4fa"):
        assert token in css


def test_opciones_de_salas_inhabilitadas_van_disabled(client, db, salas_de_prueba):
    from app.core.config import SalaEstado

    salas_de_prueba[0].estado = SalaEstado.INHABILITADA.value
    db.commit()
    html = client.get("/salas").text
    assert f'<option value="{salas_de_prueba[0].id}" data-aforo="10" disabled>' in html
    assert f'<option value="{salas_de_prueba[1].id}" data-aforo="40">' in html


def test_formulario_guia_asistentes_y_fechas(client, salas_de_prueba):
    html = client.get("/salas").text
    assert 'id="asistentes"' in html and 'min="1"' in html
    assert "De 1 hasta el aforo de la sala." in html
    js = client.get("/static/app.js").text
    assert "asistentes.max" in js
    assert "inicio.min" in js and "fin.min" in js


def test_botones_ocupan_todo_el_ancho_en_movil(client, salas_de_prueba):
    assert "btn btn-primary w-full sm:w-auto" in client.get("/salas").text
    assert "btn btn-primary w-full sm:w-auto" in client.get("/").text


def test_resultado_no_es_region_viva_y_la_ayuda_de_aforo_si(client, salas_de_prueba):
    import re

    html = client.get("/salas").text
    resultado = re.search(r'<div id="resultado"[^>]*>', html).group(0)
    assert "aria-live" not in resultado
    assert 'id="ayuda-aforo" class="hint" aria-live="polite"' in html


def test_boton_pausar_animaciones_con_aria_pressed(client):
    html = client.get("/").text
    assert 'id="btn-movimiento"' in html
    assert 'aria-pressed="false"' in html
    assert ">Pausar animaciones</button>" in html
    assert 'data-texto-reanudar="Reanudar animaciones"' in html
    js = client.get("/static/app.js").text
    assert 'setAttribute("aria-pressed"' in js
    assert "localStorage" in js


def test_css_declara_movimiento_reducido_y_apagado_manual(client):
    css = client.get("/static/app.css").text
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert '[data-movimiento="off"]' in css
    assert "animation: none !important" not in css  # ya no es un apagado global


def test_cabecera_sin_backdrop_filter_y_foco_sin_radio(client):
    css = client.get("/static/app.css").text
    assert "backdrop-filter" not in css
    bloque = css[css.index(":focus-visible {") :].split("}")[0]
    assert "border-radius" not in bloque


def test_terminologia_de_la_interfaz(client, salas_de_prueba):
    portada = client.get("/").text
    assert "Hoy puedes reservar salas. Equipos e incidencias llegan pronto." in portada
    assert "Reservas próximas" in portada and "Estado de las salas" in portada
    salas = client.get("/salas").text
    assert "<title>Reserva de salas · " in salas
    assert "Qué revisamos antes de confirmar" in salas
    assert "capacidad" not in (portada + salas).lower()


def test_tabla_de_reservas_muestra_estado_y_etiquetas_para_movil(client, db, salas_de_prueba):
    from datetime import datetime, timedelta

    from app.models import Reserva

    ahora = datetime.now()
    sala = salas_de_prueba[0]
    db.add_all(
        [
            Reserva(
                sala_id=sala.id,
                inicio=ahora - timedelta(days=2),
                fin=ahora - timedelta(days=2) + timedelta(hours=1),
                asistentes=2,
                responsable="Pasada",
            ),
            Reserva(
                sala_id=sala.id,
                inicio=ahora + timedelta(days=2),
                fin=ahora + timedelta(days=2, hours=1),
                asistentes=2,
                responsable="Futura",
            ),
        ]
    )
    db.commit()
    html = client.get("/salas").text
    assert '<th scope="col">Estado</th>' in html
    assert "Finalizada" in html and "Próxima" in html
    assert 'class="fila-finalizada"' in html
    assert 'data-label="Responsable"' in html
    assert '<th scope="row">Sala Uno</th>' in html


def test_css_incluye_respaldo_sin_tailwind(client):
    css = client.get("/static/app.css").text
    assert ":where(.grid)" in css and ":where(.sr-only)" in css
