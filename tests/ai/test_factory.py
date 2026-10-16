import pytest

from app.ai.base import AIError
from app.ai.factory import get_ai_client
from app.ai.providers.gemini import GeminiClient
from app.core.config import settings


def test_proveedor_desconocido_lanza_error(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "proveedor-inexistente")
    with pytest.raises(AIError, match="no soportado"):
        get_ai_client()


def test_gemini_sin_clave_lanza_error_claro(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    with pytest.raises(AIError, match="GEMINI_API_KEY"):
        get_ai_client()


def test_gemini_sin_modelo_lanza_error_claro(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "")
    with pytest.raises(AIError, match="GEMINI_MODEL"):
        get_ai_client()


def test_gemini_configurado_devuelve_cliente_gemini(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "modelo-de-prueba")
    monkeypatch.setattr(settings, "GEMINI_BASE_URL", "https://ia.test/v1")
    with get_ai_client() as cliente:
        assert isinstance(cliente, GeminiClient)
