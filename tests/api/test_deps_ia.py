import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.ai.base import AIClient, AIError
from app.ai.factory import ClienteIANoDisponible, get_ai_client_seguro
from app.ai.providers.gemini import GeminiClient
from app.ai.triage import clasificar_incidencia
from app.api import deps
from app.api.deps import ClienteIA, get_cliente_ia
from app.core.config import IncidenciaEstado, IncidenciaRuta, settings
from app.core.errors import setup_exception_handlers


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


def test_endpoint_sin_clave_responde_200_pendiente_y_no_500(sin_clave):
    """Reproduce el fallo crítico de la revisión del plan: sin clave no puede haber un 500."""
    app = FastAPI()
    setup_exception_handlers(app)

    @app.post("/triaje")
    def triaje(cliente: ClienteIA):
        resultado = clasificar_incidencia("La red del aula no funciona", cliente)
        return {"ok": True, "data": resultado.model_dump(mode="json")}

    response = TestClient(app, raise_server_exceptions=False).post("/triaje")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["estado"] == "pendiente_revision"
    assert data["ruta"] == "revision_manual"
    assert data["categoria"] is None
    assert data["origen_ia"] is False
