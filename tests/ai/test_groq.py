import json

import httpx
import pytest

from app.ai.base import AIError
from app.ai.providers.groq import GroqClient


def _client(handler, max_retries: int = 1) -> GroqClient:
    return GroqClient(
        api_key="clave-de-prueba",
        model="modelo-de-prueba",
        base_url="https://groq.test/v1",
        timeout=1,
        max_retries=max_retries,
        transport=httpx.MockTransport(handler),
    )


def _ok(texto: str) -> dict:
    return {"choices": [{"message": {"role": "assistant", "content": texto}}]}


def test_generate_devuelve_el_texto_y_envia_la_clave_por_header():
    vistas = []

    def handler(request: httpx.Request) -> httpx.Response:
        vistas.append(request)
        return httpx.Response(200, json=_ok("ok"))

    assert _client(handler).generate("hola") == "ok"
    peticion = vistas[0]
    assert peticion.headers["authorization"] == "Bearer clave-de-prueba"
    assert "clave-de-prueba" not in str(peticion.url)
    assert str(peticion.url) == "https://groq.test/v1/chat/completions"
    cuerpo = json.loads(peticion.content)
    assert cuerpo["model"] == "modelo-de-prueba"
    assert cuerpo["messages"] == [{"role": "user", "content": "hola"}]


def test_falta_clave_o_modelo_lanza_error_claro():
    with pytest.raises(AIError, match="GROQ_API_KEY"):
        GroqClient("", "m", "https://groq.test", 1, 0)
    with pytest.raises(AIError, match="GROQ_MODEL"):
        GroqClient("k", "", "https://groq.test", 1, 0)


def test_max_retries_negativo_lanza_error_claro():
    with pytest.raises(AIError, match="negativo"):
        GroqClient("k", "m", "https://groq.test", 1, -1)


def test_error_429_reintenta_y_se_recupera():
    respuestas = iter([httpx.Response(429), httpx.Response(200, json=_ok("listo"))])

    def handler(request: httpx.Request) -> httpx.Response:
        return next(respuestas)

    assert _client(handler, max_retries=1).generate("hola") == "listo"


def test_timeout_reintenta_y_luego_falla_con_el_nombre_del_proveedor():
    llamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas.append(1)
        raise httpx.ReadTimeout("lento", request=request)

    with pytest.raises(AIError, match="Groq"):
        _client(handler, max_retries=1).generate("hola")
    assert len(llamadas) == 2


def test_error_4xx_no_reintenta():
    llamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas.append(1)
        return httpx.Response(401)

    with pytest.raises(AIError, match="401"):
        _client(handler, max_retries=3).generate("hola")
    assert len(llamadas) == 1


def test_respuesta_que_no_es_json_lanza_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"<html>no es json</html>")

    with pytest.raises(AIError, match="no es JSON"):
        _client(handler, max_retries=0).generate("hola")


@pytest.mark.parametrize(
    "cuerpo",
    [
        {},
        {"choices": []},
        {"choices": [{}]},
        {"choices": [{"message": {}}]},
        {"choices": [{"message": {"content": None}}]},
        {"choices": [{"message": {"content": "   "}, "finish_reason": "length"}]},
        {"choices": "no-es-lista"},
        [],
    ],
)
def test_respuesta_invalida_o_vacia_lanza_error(cuerpo):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=cuerpo)

    with pytest.raises(AIError):
        _client(handler, max_retries=0).generate("hola")


@pytest.mark.parametrize("respuesta", [httpx.Response(401), httpx.Response(500)])
def test_la_clave_no_aparece_en_los_mensajes_de_error(respuesta):
    def handler(request: httpx.Request) -> httpx.Response:
        return respuesta

    with pytest.raises(AIError) as info:
        _client(handler, max_retries=0).generate("hola")
    assert "clave-de-prueba" not in str(info.value)


def test_close_cierra_el_cliente_http():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_ok("ok"))

    with _client(handler) as cliente:
        assert cliente.generate("hola") == "ok"
    with pytest.raises(RuntimeError):
        cliente.generate("otra vez")
