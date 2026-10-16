import logging

import pytest

from app.ai.base import AIClient, AIError
from app.ai.factory import ClienteIANoDisponible, get_ai_client_seguro
from app.ai.providers.gemini import GeminiClient
from app.ai.triage import clasificar_incidencia
from app.api import deps
from app.api.deps import get_cliente_ia
from app.core.config import IncidenciaEstado, IncidenciaRuta, settings


@pytest.fixture
def sin_clave(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")


def test_sin_clave_devuelve_un_cliente_no_disponible_en_vez_de_fallar(sin_clave):
    cliente = get_ai_client_seguro()

    assert isinstance(cliente, ClienteIANoDisponible)
    with pytest.raises(AIError, match="GEMINI_API_KEY"):
        cliente.generate("hola")


def test_proveedor_desconocido_devuelve_un_cliente_no_disponible(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "proveedor-inexistente")

    assert isinstance(get_ai_client_seguro(), ClienteIANoDisponible)


def test_con_configuracion_completa_devuelve_el_cliente_real(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "modelo-de-prueba")
    monkeypatch.setattr(settings, "GEMINI_BASE_URL", "https://ia.test/v1")

    with get_ai_client_seguro() as cliente:
        assert isinstance(cliente, GeminiClient)


def test_el_aviso_en_el_log_no_incluye_la_clave(monkeypatch, caplog):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "clave-secreta-de-prueba")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "")

    with caplog.at_level(logging.WARNING, logger="app.ai.factory"):
        get_ai_client_seguro()

    assert "GEMINI_MODEL" in caplog.text
    assert "clave-secreta-de-prueba" not in caplog.text


def test_el_triaje_con_la_ia_no_disponible_queda_pendiente(sin_clave):
    resultado = clasificar_incidencia("El proyector no enciende", get_ai_client_seguro())

    assert resultado.estado == IncidenciaEstado.PENDIENTE_REVISION
    assert resultado.ruta == IncidenciaRuta.REVISION_MANUAL
    assert resultado.origen_ia is False


def test_get_cliente_ia_cierra_el_cliente_al_terminar(monkeypatch):
    class ClienteEspia(AIClient):
        cerrado = False

        def generate(self, prompt: str) -> str:
            return "ok"

        def close(self) -> None:
            self.cerrado = True

    espia = ClienteEspia()
    monkeypatch.setattr(deps, "get_ai_client_seguro", lambda: espia)

    generador = get_cliente_ia()
    assert next(generador) is espia
    with pytest.raises(StopIteration):
        next(generador)
    assert espia.cerrado is True


# El caso "sin clave no da 500" se prueba contra la app real en
# tests/api/test_incidencias.py::test_sin_clave_de_ia_la_incidencia_queda_pendiente_y_no_da_500.
