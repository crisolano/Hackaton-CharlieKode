from collections.abc import Callable

from app.ai.base import AIClient, AIError
from app.ai.providers.gemini import GeminiClient
from app.ai.providers.groq import GroqClient
from app.core.config import settings


def _crear_gemini() -> AIClient:
    return GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
        base_url=settings.GEMINI_BASE_URL,
        timeout=settings.AI_TIMEOUT_SECONDS,
        max_retries=settings.AI_MAX_RETRIES,
    )


def _crear_groq() -> AIClient:
    return GroqClient(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        base_url=settings.GROQ_BASE_URL,
        timeout=settings.AI_TIMEOUT_SECONDS,
        max_retries=settings.AI_MAX_RETRIES,
    )


# Para añadir un proveedor: una función que lo construya desde la configuración y una entrada aquí.
PROVEEDORES: dict[str, Callable[[], AIClient]] = {
    "gemini": _crear_gemini,
    "groq": _crear_groq,
}


def get_ai_client(proveedor: str | None = None) -> AIClient:
    """Construye el cliente del proveedor pedido, o el de AI_PROVIDER si no se indica."""
    nombre = proveedor or settings.AI_PROVIDER
    crear = PROVEEDORES.get(nombre)
    if crear is None:
        raise AIError(f"Proveedor de IA no soportado: {nombre}")
    return crear()
