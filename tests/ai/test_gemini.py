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


@pytest.mark.parametrize("cuerpo", [{}, {"candidates": []}, _ok("   ")])
def test_respuesta_invalida_o_vacia_lanza_error(cuerpo):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=cuerpo)

    with pytest.raises(AIError):
        _client(handler, max_retries=0).generate("hola")
