import re

import pytest

from app.web import routes

IDS_CRITICOS = (
    "form-reserva",
    "btn-reservar",
    "cargando",
    "resultado",
    "ayuda-aforo",
    "salas-disponibilidad",
    "reservas",
    "btn-movimiento",
)
CAMPOS = ("sala_id", "asistentes", "inicio", "fin", "responsable")


def _src_y_href(html: str) -> list[str]:
    return re.findall(r'(?:src|href)="([^"]+)"', html)


# ---------------------------------------------------------------- regresión funcional


def test_salas_conserva_ids_campos_y_atributos_htmx(client, salas_de_prueba):
    r = client.get("/salas")
    assert r.status_code == 200
    for ident in IDS_CRITICOS:
        assert f'id="{ident}"' in r.text, ident
    for campo in CAMPOS:
        assert f'name="{campo}"' in r.text, campo
    for atributo in (
        'hx-post="/salas/reservar"',
        'hx-target="#resultado"',
        'hx-indicator="#cargando"',
        'hx-disabled-elt="#btn-reservar"',
        "data-mensaje-carga=",
        "data-limpiar-al-exito",
        f'data-elegir-sala="{salas_de_prueba[0].id}"',
    ):
        assert atributo in r.text, atributo


def test_portada_enlaza_todos_los_modulos(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Equipos" in r.text and "Incidencias" in r.text and "Espacios" in r.text
    assert 'href="/incidencias"' in r.text


# ---------------------------------------------------------------- carga y versionado


@pytest.mark.parametrize("ruta", ["/", "/salas"])
def test_base_carga_visual_y_scroll_despues_de_app_con_version(client, ruta):
    html = client.get(ruta).text
    for nombre in ("app.css", "visual.css", "app.js", "scroll.js"):
        assert re.search(rf'"/static/{re.escape(nombre)}\?v=[0-9a-f]{{10}}"', html), nombre
    assert html.index("/static/app.css?v=") < html.index("/static/visual.css?v=")
    assert html.index("/static/app.js?v=") < html.index("/static/scroll.js?v=")
    for url in _src_y_href(html):
        if url.startswith("/static/"):
            assert "?v=" in url, url
        assert not url.startswith("http://testserver"), url


def test_huella_cambia_con_el_contenido(tmp_path):
    archivo = tmp_path / "x.css"
    archivo.write_text("a{}", encoding="utf-8")
    h1 = routes.huella_estatico("x.css", tmp_path)
    archivo.write_text("b{}", encoding="utf-8")
    h2 = routes.huella_estatico("x.css", tmp_path)
    assert h1 and h2 and h1 != h2
    assert len(h1) == 10
    assert routes.huella_estatico("no-existe.css", tmp_path) is None


def test_estatico_cachea_y_sin_archivo_no_pone_version(monkeypatch):
    monkeypatch.setattr(routes, "_HUELLAS_ESTATICOS", {})
    llamadas = []

    def falsa(nombre, directorio=routes.STATIC_DIR):
        llamadas.append(nombre)
        return "abc1234567"

    monkeypatch.setattr(routes, "huella_estatico", falsa)
    assert routes.estatico("app.css") == "/static/app.css?v=abc1234567"
    assert routes.estatico("app.css") == "/static/app.css?v=abc1234567"
    assert llamadas == ["app.css"]
    monkeypatch.setattr(routes, "_HUELLAS_ESTATICOS", {})
    monkeypatch.setattr(routes, "huella_estatico", lambda nombre, directorio=None: None)
    assert routes.estatico("falta.css") == "/static/falta.css"


@pytest.mark.parametrize(
    "nombre", ["app.css", "visual.css", "app.js", "scroll.js", "campuslands-casco.png"]
)
def test_estaticos_responden_con_y_sin_query(client, nombre):
    assert client.get(f"/static/{nombre}").status_code == 200
    assert client.get(routes.estatico(nombre)).status_code == 200
    assert client.get(f"/static/{nombre}?v=cualquiera").status_code == 200


# ---------------------------------------------------------------- visual.css y scroll.js


def test_visual_css_respeta_movimiento_y_anula_decoracion(client):
    css = client.get("/static/visual.css").text
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert '[data-movimiento="off"]' in css
    bloque_logo = css[css.index(".hero-logo {") :].split("}")[0]
    assert "animation: none" in bloque_logo
    bloque_orbita = css[css.index(".hero-orbita {") :].split("}")[0]
    assert "display: none" in bloque_orbita
    assert "@media (hover: hover)" in css
    assert "gsap" not in css.lower()
    assert "pointer-events: none" not in css
    for color in ("#24252B", "#303138", "#6B5CFF", "#00D5E8", "#F4F4FA"):
        assert color in css


def test_scroll_js_usa_intersection_observer_y_excluye_zonas_htmx(client):
    js = client.get("/static/scroll.js").text
    assert "IntersectionObserver" in js
    assert "unobserve" in js
    for zona in ("#resultado", "#salas-disponibilidad", "#reservas"):
        assert zona in js
    assert "prefers-reduced-motion" in js
    assert "data-movimiento" in js
    assert ".entra" in js or '"entra"' in js
    assert "gsap" not in js.lower()
