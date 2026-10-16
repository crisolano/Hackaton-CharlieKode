import httpx
import pytest

from app.ai.base import AIError
from app.ai.providers.gemini import GeminiClient


def _client(handler, max_retries: int = 1) -> GeminiClient:
    return GeminiClient(
        api_key="clave-de-prueba",
        model="modelo-de-prueba",
        base_url="https://ia.test/v1",
        timeout=1,
        max_retries=max_retries,
        transport=httpx.MockTransport(handler),
    )


def _ok(texto: str) -> dict:
    return {"candidates": [{"content": {"parts": [{"text": texto}]}}]}


def test_generate_devuelve_el_texto_y_envia_la_clave_por_header():
    vistas = []

    def handler(request: httpx.Request) -> httpx.Response:
        vistas.append(request)
        return httpx.Response(200, json=_ok("ok"))

    assert _client(handler).generate("hola") == "ok"
    assert vistas[0].headers["x-goog-api-key"] == "clave-de-prueba"
    assert "clave-de-prueba" not in str(vistas[0].url)
    assert str(vistas[0].url).endswith("/models/modelo-de-prueba:generateContent")


def test_falta_clave_o_modelo_lanza_error():
    with pytest.raises(AIError):
        GeminiClient("", "m", "https://ia.test", 1, 0)
    with pytest.raises(AIError):
        GeminiClient("k", "", "https://ia.test", 1, 0)


def test_timeout_reintenta_y_luego_falla():
    llamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas.append(1)
        raise httpx.ReadTimeout("lento", request=request)

    with pytest.raises(AIError):
        _client(handler, max_retries=1).generate("hola")
    assert len(llamadas) == 2


def test_error_500_reintenta_y_se_recupera():
    respuestas = iter([httpx.Response(500), httpx.Response(200, json=_ok("listo"))])

    def handler(request: httpx.Request) -> httpx.Response:
        return next(respuestas)

    assert _client(handler, max_retries=1).generate("hola") == "listo"


def test_error_4xx_no_reintenta():
    llamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas.append(1)
        return httpx.Response(403)

    with pytest.raises(AIError):
        _client(handler, max_retries=3).generate("hola")
    assert len(llamadas) == 1


def test_error_429_reintenta_y_se_recupera():
    respuestas = iter([httpx.Response(429), httpx.Response(200, json=_ok("listo"))])

    def handler(request: httpx.Request) -> httpx.Response:
        return next(respuestas)

    assert _client(handler, max_retries=1).generate("hola") == "listo"


def test_reintentos_agotados_hacen_max_retries_mas_uno_llamadas():
    llamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas.append(1)
        return httpx.Response(500)

    with pytest.raises(AIError):
        _client(handler, max_retries=2).generate("hola")
    assert len(llamadas) == 3


def test_sin_reintentos_hace_una_sola_llamada():
    llamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas.append(1)
        return httpx.Response(500)

    with pytest.raises(AIError):
        _client(handler, max_retries=0).generate("hola")
    assert len(llamadas) == 1


def test_respuesta_que_no_es_json_lanza_error_sin_reintentar():
    llamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas.append(1)
        return httpx.Response(200, content=b"<html>no es json</html>")

    with pytest.raises(AIError, match="no es JSON"):
        _client(handler, max_retries=3).generate("hola")
    assert len(llamadas) == 1


def test_peticion_bloqueada_por_seguridad_lanza_error():
    cuerpo = {"promptFeedback": {"blockReason": "SAFETY"}}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=cuerpo)

    with pytest.raises(AIError, match="bloqueó"):
        _client(handler, max_retries=0).generate("hola")


@pytest.mark.parametrize("feedback", ["texto suelto", ["lista"], 42, None])
def test_prompt_feedback_malformado_no_rompe_y_se_ignora(feedback):
    cuerpo = {**_ok("listo"), "promptFeedback": feedback}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=cuerpo)

    assert _client(handler, max_retries=0).generate("hola") == "listo"


def test_max_retries_negativo_lanza_error_claro():
    with pytest.raises(AIError, match="negativo"):
        GeminiClient("k", "m", "https://ia.test", 1, -1)


def test_candidato_sin_contenido_lanza_error_con_el_motivo():
    cuerpo = {"candidates": [{"finishReason": "MAX_TOKENS"}]}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=cuerpo)

    with pytest.raises(AIError, match="MAX_TOKENS"):
        _client(handler, max_retries=0).generate("hola")


@pytest.mark.parametrize(
    "respuesta",
    [httpx.Response(403), httpx.Response(500), httpx.Response(200, json={})],
)
def test_la_clave_no_aparece_en_los_mensajes_de_error(respuesta):
    def handler(request: httpx.Request) -> httpx.Response:
        return respuesta

    with pytest.raises(AIError) as info:
        _client(handler, max_retries=0).generate("hola")
    assert "clave-de-prueba" not in str(info.value)


def test_close_cierra_el_cliente_http_y_funciona_como_gestor_de_contexto():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_ok("ok"))

    with _client(handler) as cliente:
        assert cliente.generate("hola") == "ok"
    with pytest.raises(RuntimeError):
        cliente.generate("otra vez")


@pytest.mark.parametrize("cuerpo", [{}, {"candidates": []}, _ok("   ")])
def test_respuesta_invalida_o_vacia_lanza_error(cuerpo):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=cuerpo)

    with pytest.raises(AIError):
        _client(handler, max_retries=0).generate("hola")
