import pytest

from app.core.config import settings


@pytest.fixture(autouse=True)
def _sin_respaldo_de_ia(monkeypatch):
    """Aísla las pruebas del .env local: el respaldo solo se activa en las que lo piden."""
    monkeypatch.setattr(settings, "AI_FALLBACK_PROVIDER", "")
