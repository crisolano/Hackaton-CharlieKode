import logging
from collections.abc import Callable

from app.ai.base import AIClient, AIError
from app.ai.providers.gemini import GeminiClient
from app.ai.providers.groq import GroqClient
from app.core.config import settings

logger = logging.getLogger(__name__)


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


class ClienteIANoDisponible(AIClient):
    """Se usa cuando la IA no se pudo configurar: cada llamada falla con el motivo original.

    El triaje convierte ese fallo en `pendiente_revision`, así que la petición nunca da 500
    ni se inventa una clasificación.
    """

    def __init__(self, motivo: str):
        self.motivo = motivo

    def generate(self, prompt: str) -> str:
        raise AIError(self.motivo)


def get_ai_client(proveedor: str | None = None) -> AIClient:
    """Construye el cliente del proveedor pedido, o el de AI_PROVIDER si no se indica."""
    nombre = proveedor or settings.AI_PROVIDER
    crear = PROVEEDORES.get(nombre)
    if crear is None:
        raise AIError(f"Proveedor de IA no soportado: {nombre}")
    return crear()


def get_ai_client_seguro(proveedor: str | None = None) -> AIClient:
    """Como get_ai_client, pero si la configuración falla devuelve un ClienteIANoDisponible."""
    try:
        return get_ai_client(proveedor)
    except AIError as exc:
        logger.warning("IA no disponible: %s", exc)
        return ClienteIANoDisponible(str(exc))
