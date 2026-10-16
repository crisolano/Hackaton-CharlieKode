from app.ai.base import AIClient, AIError
from app.ai.providers.gemini import GeminiClient
from app.core.config import settings


def get_ai_client() -> AIClient:
    """Construye el cliente del proveedor indicado en AI_PROVIDER."""
    if settings.AI_PROVIDER == "gemini":
        return GeminiClient(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
            base_url=settings.GEMINI_BASE_URL,
            timeout=settings.AI_TIMEOUT_SECONDS,
            max_retries=settings.AI_MAX_RETRIES,
        )
    raise AIError(f"Proveedor de IA no soportado: {settings.AI_PROVIDER}")
