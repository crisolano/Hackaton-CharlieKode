import json
import logging

import httpx
import pytest

from app.ai.base import AIClient, AIError
from app.ai.factory import ClienteIANoDisponible, get_ai_client_seguro
from app.ai.fallback import ClienteConRespaldo
from app.ai.providers.gemini import GeminiClient
from app.ai.providers.groq import GroqClient
from app.ai.triage import clasificar_incidencia
from app.core.config import IncidenciaEstado, settings


class Reloj:
    """Reloj y sleep falsos: dormir avanza el reloj sin esperar de verdad."""

    def __init__(self):
        self.ahora = 0.0
        self.esperas: list[float] = []

    def __call__(self) -> float:
        return self.ahora

    def dormir(self, segundos: float) -> None:
        self.esperas.append(segundos)
        self.ahora += segundos


def _ok(texto: str) -> dict:
    return {"choices": [{"message": {"content": texto}}]}


def _groq(handler, reloj: Reloj, max_retries=3, backoff=0.5, tiempo_total=None) -> GroqClient:
    return GroqClient(
        api_key="clave-de-prueba",
        model="modelo-de-prueba",
        base_url="https://groq.test/v1",
        timeout=1,
        max_retries=max_retries,
        transport=httpx.MockTransport(handler),
        backoff=backoff,
        tiempo_total=tiempo_total,
        dormir=reloj.dormir,
        reloj=reloj,
    )


# --- Espera entre reintentos ------------------------------------------------------------


def test_la_espera_entre_reintentos_crece_de_forma_exponencial():
    reloj = Reloj()
    respuestas = iter([httpx.Response(503)] * 3 + [httpx.Response(200, json=_ok("listo"))])

    resultado = _groq(lambda r: next(respuestas), reloj, max_retries=3).generate("hola")

    assert resultado == "listo"
    assert reloj.esperas == [0.5, 1.0, 2.0]


def test_respeta_retry_after_del_proveedor():
    reloj = Reloj()
    respuestas = iter(
        [httpx.Response(429, headers={"Retry-After": "3"}), httpx.Response(200, json=_ok("ok"))]
    )

    _groq(lambda r: next(respuestas), reloj, max_retries=1).generate("hola")

    assert reloj.esperas == [3.0]


def test_sin_backoff_no_espera():
    reloj = Reloj()
    respuestas = iter([httpx.Response(500), httpx.Response(200, json=_ok("ok"))])

    _groq(lambda r: next(respuestas), reloj, max_retries=1, backoff=0).generate("hola")

    assert reloj.esperas == []


def test_no_espera_despues_del_ultimo_intento():
    reloj = Reloj()

    with pytest.raises(AIError):
        _groq(lambda r: httpx.Response(503), reloj, max_retries=2).generate("hola")

    assert reloj.esperas == [0.5, 1.0]


def test_backoff_negativo_lanza_error_claro():
    with pytest.raises(AIError, match="AI_BACKOFF_SECONDS"):
        _groq(lambda r: httpx.Response(200), Reloj(), backoff=-1)


# --- Tope de tiempo total ---------------------------------------------------------------


def test_el_tope_de_tiempo_corta_los_reintentos():
    reloj = Reloj()
    llamadas = []

    def handler(request):
        llamadas.append(1)
        return httpx.Response(503, headers={"Retry-After": "10"})

    with pytest.raises(AIError, match="tope de tiempo"):
        _groq(handler, reloj, max_retries=5, tiempo_total=15).generate("hola")

    assert len(llamadas) == 2  # 1 intento + espera de 10 s + 1 intento; la siguiente espera no cabe
    assert reloj.esperas == [10.0]


def test_una_peticion_lenta_cuenta_para_el_tope_y_nunca_se_supera():
    """Simula una red real: cada petición tarda 9 s, o corta al agotar su timeout."""
    reloj = Reloj()
    llamadas = []

    def handler(request):
        llamadas.append(1)
        limite = request.extensions["timeout"]["read"]
        if limite < 9:
            reloj.ahora += limite
            raise httpx.ReadTimeout("lento", request=request)
        reloj.ahora += 9
        return httpx.Response(503)

    cliente = GroqClient(
        api_key="clave-de-prueba",
        model="modelo-de-prueba",
        base_url="https://groq.test/v1",
        timeout=10,
        max_retries=5,
        transport=httpx.MockTransport(handler),
        backoff=0.5,
        tiempo_total=10,
        dormir=reloj.dormir,
        reloj=reloj,
    )

    with pytest.raises(AIError, match="tope de tiempo"):
        cliente.generate("hola")

    # 9 s de la primera petición + 0.5 s de espera + 0.5 s que le quedaban a la segunda.
    assert len(llamadas) == 2
    assert reloj.ahora == pytest.approx(10)


def test_el_timeout_de_cada_peticion_se_recorta_a_lo_que_queda_del_tope():
    reloj = Reloj()
    timeouts = []

    def handler(request):
        timeouts.append(request.extensions["timeout"]["read"])
        reloj.ahora += 4
        return httpx.Response(503)

    with pytest.raises(AIError):
        _groq(handler, reloj, max_retries=1, backoff=1, tiempo_total=6).generate("hola")

    assert timeouts == [1, 1]  # el timeout por intento (1 s) ya es menor que lo que queda
    reloj2, timeouts2 = Reloj(), []

    def lento(request):
        timeouts2.append(request.extensions["timeout"]["read"])
        reloj2.ahora += 4
        return httpx.Response(503)

    cliente = GroqClient(
        api_key="clave-de-prueba",
        model="m",
        base_url="https://groq.test/v1",
        timeout=10,
        max_retries=1,
        transport=httpx.MockTransport(lento),
        backoff=1,
        tiempo_total=6,
        dormir=reloj2.dormir,
        reloj=reloj2,
    )
    with pytest.raises(AIError):
        cliente.generate("hola")
    assert timeouts2 == [6, 1]  # 6 - (4 s de petición + 1 s de espera) = 1 s para el segundo


@pytest.mark.parametrize("valor", ["0", "-1"])
def test_un_tope_no_positivo_lanza_error_claro(valor):
    with pytest.raises(AIError, match="AI_TOTAL_TIMEOUT_SECONDS"):
        _groq(lambda r: httpx.Response(200), Reloj(), tiempo_total=float(valor))


def test_retry_after_con_decimales_se_respeta():
    reloj = Reloj()
    respuestas = iter(
        [httpx.Response(429, headers={"Retry-After": "1.5"}), httpx.Response(200, json=_ok("ok"))]
    )

    _groq(lambda r: next(respuestas), reloj, max_retries=1).generate("hola")

    assert reloj.esperas == [1.5]


@pytest.mark.parametrize("valor", ["Wed, 21 Oct 2026 07:28:00 GMT", "pronto", "-3"])
def test_retry_after_en_fecha_o_invalido_usa_la_espera_propia(valor):
    reloj = Reloj()
    respuestas = iter(
        [httpx.Response(503, headers={"Retry-After": valor}), httpx.Response(200, json=_ok("ok"))]
    )

    _groq(lambda r: next(respuestas), reloj, max_retries=1, backoff=0.5).generate("hola")

    assert reloj.esperas == [0.5]


def test_sin_tope_un_retry_after_enorme_no_bloquea_el_proceso():
    reloj = Reloj()

    with pytest.raises(AIError, match="tope de tiempo"):
        _groq(
            lambda r: httpx.Response(503, headers={"Retry-After": "3600"}), reloj, max_retries=2
        ).generate("hola")

    assert reloj.esperas == []


# --- Errores claros ---------------------------------------------------------------------


def test_el_error_final_dice_el_motivo_y_el_codigo_http():
    with pytest.raises(AIError) as info:
        _groq(lambda r: httpx.Response(503), Reloj(), max_retries=0).generate("hola")

    assert "Groq" in str(info.value)
    assert "HTTP 503" in str(info.value)
    assert info.value.codigo_http == 503


def test_timeout_se_informa_como_timeout():
    def handler(request):
        raise httpx.ReadTimeout("lento", request=request)

    with pytest.raises(AIError, match="timeout") as info:
        _groq(handler, Reloj(), max_retries=0).generate("hola")

    assert info.value.codigo_http is None


def test_un_4xx_no_se_reintenta_y_guarda_el_codigo():
    llamadas = []

    def handler(request):
        llamadas.append(1)
        return httpx.Response(401)

    with pytest.raises(AIError) as info:
        _groq(handler, Reloj(), max_retries=3).generate("hola")

    assert info.value.codigo_http == 401
    assert len(llamadas) == 1


def test_cada_intento_fallido_queda_en_el_log_sin_la_clave_ni_el_prompt(caplog):
    with caplog.at_level(logging.WARNING, logger="app.ai.providers.http_base"):
        with pytest.raises(AIError):
            _groq(lambda r: httpx.Response(503), Reloj(), max_retries=1).generate("texto-privado")

    assert "intento 1 de 2" in caplog.text
    assert "intento 2 de 2" in caplog.text
    assert "HTTP 503" in caplog.text
    assert "clave-de-prueba" not in caplog.text
    assert "texto-privado" not in caplog.text


def test_gemini_tambien_acepta_backoff_y_tope():
    reloj = Reloj()
    respuestas = iter(
        [
            httpx.Response(503),
            httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}),
        ]
    )
    cliente = GeminiClient(
        api_key="clave-de-prueba",
        model="modelo-de-prueba",
        base_url="https://ia.test/v1",
        timeout=1,
        max_retries=1,
        transport=httpx.MockTransport(lambda r: next(respuestas)),
        backoff=0.25,
        tiempo_total=10,
        dormir=reloj.dormir,
        reloj=reloj,
    )

    assert cliente.generate("hola") == "ok"
    assert reloj.esperas == [0.25]


# --- Respaldo entre proveedores ---------------------------------------------------------


class Doble(AIClient):
    def __init__(self, nombre: str, respuesta: str | Exception):
        self.nombre = nombre
        self._respuesta = respuesta
        self.llamadas = 0
        self.cerrado = False

    def generate(self, prompt: str) -> str:
        self.llamadas += 1
        if isinstance(self._respuesta, Exception):
            raise self._respuesta
        return self._respuesta

    def close(self) -> None:
        self.cerrado = True


def test_si_el_principal_falla_usa_el_respaldo(caplog):
    principal = Doble("Gemini", AIError("saturado", codigo_http=503))
    respaldo = Doble("Groq", "respuesta del respaldo")

    with caplog.at_level(logging.WARNING, logger="app.ai.fallback"):
        texto = ClienteConRespaldo([principal, respaldo]).generate("hola")

    assert texto == "respuesta del respaldo"
    assert (principal.llamadas, respaldo.llamadas) == (1, 1)
    assert "se usa el respaldo Groq" in caplog.text


def test_si_el_principal_responde_no_se_llama_al_respaldo():
    principal = Doble("Gemini", "ok")
    respaldo = Doble("Groq", "no debería usarse")

    assert ClienteConRespaldo([principal, respaldo]).generate("hola") == "ok"
    assert respaldo.llamadas == 0


def test_si_todos_fallan_se_lanza_el_ultimo_error():
    principal = Doble("Gemini", AIError("uno"))
    respaldo = Doble("Groq", AIError("dos"))

    with pytest.raises(AIError, match="dos"):
        ClienteConRespaldo([principal, respaldo]).generate("hola")


def test_cerrar_el_respaldo_cierra_todos_los_proveedores():
    principal, respaldo = Doble("Gemini", "ok"), Doble("Groq", "ok")

    with ClienteConRespaldo([principal, respaldo]):
        pass

    assert principal.cerrado and respaldo.cerrado


def test_un_error_inesperado_del_principal_tambien_pasa_al_respaldo():
    principal = Doble("Gemini", ValueError("bug interno"))
    respaldo = Doble("Groq", "ok")

    assert ClienteConRespaldo([principal, respaldo]).generate("hola") == "ok"


def test_si_todos_fallan_con_error_inesperado_se_lanza_aierror():
    cliente = ClienteConRespaldo([Doble("Gemini", ValueError("x")), Doble("Groq", KeyError("y"))])

    with pytest.raises(AIError, match="Groq falló de forma inesperada"):
        cliente.generate("hola")


def test_el_log_del_respaldo_no_incluye_el_mensaje_del_error(caplog):
    principal = Doble("Gemini", AIError("mensaje-con-datos-del-proveedor", codigo_http=503))

    with caplog.at_level(logging.WARNING, logger="app.ai.fallback"):
        ClienteConRespaldo([principal, Doble("Groq", "ok")]).generate("hola")

    assert "HTTP 503" in caplog.text
    assert "mensaje-con-datos-del-proveedor" not in caplog.text


def test_si_cerrar_un_cliente_falla_se_cierran_los_demas():
    class FallaAlCerrar(Doble):
        def close(self):
            raise RuntimeError("no cierra")

    segundo = Doble("Groq", "ok")

    ClienteConRespaldo([FallaAlCerrar("Gemini", "ok"), segundo]).close()

    assert segundo.cerrado is True


def test_respaldo_sin_proveedores_lanza_error():
    with pytest.raises(AIError):
        ClienteConRespaldo([])


def test_el_triaje_clasifica_con_el_respaldo_si_el_principal_cae():
    clasificacion = json.dumps({"categoria": "red", "prioridad": "alta", "ruta": "soporte_tecnico"})
    cliente = ClienteConRespaldo([Doble("Gemini", AIError("503")), Doble("Groq", clasificacion)])

    resultado = clasificar_incidencia("No hay internet", cliente)

    assert resultado.estado == IncidenciaEstado.CLASIFICADA
    assert resultado.origen_ia is True


def test_el_triaje_queda_pendiente_si_caen_todos_los_proveedores():
    cliente = ClienteConRespaldo([Doble("Gemini", AIError("503")), Doble("Groq", AIError("429"))])

    resultado = clasificar_incidencia("No hay internet", cliente)

    assert resultado.estado == IncidenciaEstado.PENDIENTE_REVISION


# --- Fábrica: armado del respaldo desde la configuración --------------------------------


@pytest.fixture
def ambos_configurados(monkeypatch):
    for nombre, valor in {
        "GEMINI_API_KEY": "clave-de-prueba",
        "GEMINI_MODEL": "modelo-de-prueba",
        "GEMINI_BASE_URL": "https://ia.test/v1",
        "GROQ_API_KEY": "clave-de-prueba",
        "GROQ_MODEL": "modelo-de-prueba",
        "GROQ_BASE_URL": "https://groq.test/v1",
    }.items():
        monkeypatch.setattr(settings, nombre, valor)


def test_con_respaldo_configurado_la_fabrica_devuelve_cliente_con_respaldo(
    monkeypatch, ambos_configurados
):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "AI_FALLBACK_PROVIDER", "groq")

    with get_ai_client_seguro() as cliente:
        assert isinstance(cliente, ClienteConRespaldo)
        assert cliente.nombre == "Gemini -> Groq"


def test_sin_respaldo_la_fabrica_devuelve_solo_el_principal(monkeypatch, ambos_configurados):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "AI_FALLBACK_PROVIDER", "")

    with get_ai_client_seguro() as cliente:
        assert isinstance(cliente, GeminiClient)


def test_respaldo_igual_al_principal_no_se_duplica(monkeypatch, ambos_configurados):
    monkeypatch.setattr(settings, "AI_PROVIDER", "groq")
    monkeypatch.setattr(settings, "AI_FALLBACK_PROVIDER", "groq")

    with get_ai_client_seguro() as cliente:
        assert isinstance(cliente, GroqClient)


def test_si_el_principal_esta_mal_configurado_se_usa_solo_el_respaldo(
    monkeypatch, ambos_configurados
):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "AI_FALLBACK_PROVIDER", "groq")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

    with get_ai_client_seguro() as cliente:
        assert isinstance(cliente, GroqClient)


def test_si_ninguno_esta_configurado_devuelve_no_disponible_con_ambos_motivos(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "AI_FALLBACK_PROVIDER", "groq")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")

    cliente = get_ai_client_seguro()

    assert isinstance(cliente, ClienteIANoDisponible)
    assert "GEMINI_API_KEY" in cliente.motivo and "GROQ_API_KEY" in cliente.motivo


def test_un_proveedor_explicito_ignora_el_respaldo(monkeypatch, ambos_configurados):
    monkeypatch.setattr(settings, "AI_FALLBACK_PROVIDER", "groq")

    with get_ai_client_seguro("gemini") as cliente:
        assert isinstance(cliente, GeminiClient)
