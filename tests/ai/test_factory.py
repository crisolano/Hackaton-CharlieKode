import pytest

from app.ai.base import AIError
from app.ai.factory import PROVEEDORES, get_ai_client
from app.ai.providers.gemini import GeminiClient
from app.ai.providers.groq import GroqClient
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


def test_groq_sin_clave_o_modelo_lanza_error_claro(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "groq")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    with pytest.raises(AIError, match="GROQ_API_KEY"):
        get_ai_client()
    monkeypatch.setattr(settings, "GROQ_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(settings, "GROQ_MODEL", "")
    with pytest.raises(AIError, match="GROQ_MODEL"):
        get_ai_client()


def test_groq_configurado_devuelve_cliente_groq(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "groq")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(settings, "GROQ_MODEL", "modelo-de-prueba")
    monkeypatch.setattr(settings, "GROQ_BASE_URL", "https://groq.test/v1")
    with get_ai_client() as cliente:
        assert isinstance(cliente, GroqClient)


def test_se_puede_pedir_un_proveedor_distinto_al_configurado(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(settings, "GROQ_MODEL", "modelo-de-prueba")
    monkeypatch.setattr(settings, "GROQ_BASE_URL", "https://groq.test/v1")
    with get_ai_client("groq") as cliente:
        assert isinstance(cliente, GroqClient)


def test_los_proveedores_del_registro_son_los_documentados():
    assert set(PROVEEDORES) == {"gemini", "groq"}


def test_gemini_configurado_devuelve_cliente_gemini(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "modelo-de-prueba")
    monkeypatch.setattr(settings, "GEMINI_BASE_URL", "https://ia.test/v1")
    with get_ai_client() as cliente:
        assert isinstance(cliente, GeminiClient)
