import logging
from collections.abc import Callable

from app.ai.base import AIClient, AIError
from app.ai.fallback import ClienteConRespaldo
from app.ai.providers.gemini import GeminiClient
from app.ai.providers.groq import GroqClient
from app.core.config import settings

logger = logging.getLogger(__name__)


def _opciones_comunes() -> dict[str, float]:
    """Timeout, reintentos, espera y tope de tiempo: iguales para todos los proveedores."""
    return {
        "timeout": settings.AI_TIMEOUT_SECONDS,
        "max_retries": settings.AI_MAX_RETRIES,
        "backoff": settings.AI_BACKOFF_SECONDS,
        "tiempo_total": settings.AI_TOTAL_TIMEOUT_SECONDS,
    }


def _crear_gemini() -> AIClient:
    return GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
        base_url=settings.GEMINI_BASE_URL,
        **_opciones_comunes(),
    )


def _crear_groq() -> AIClient:
    return GroqClient(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        base_url=settings.GROQ_BASE_URL,
        **_opciones_comunes(),
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
    """Cliente listo para usar que nunca falla al crearse.

    Sin `proveedor` explícito usa AI_PROVIDER y, si AI_FALLBACK_PROVIDER está definido y es
    distinto, lo añade como respaldo. Los proveedores mal configurados se omiten; si no queda
    ninguno, devuelve un ClienteIANoDisponible (el triaje deja la incidencia en revisión).
    """
    principal = proveedor or settings.AI_PROVIDER
    nombres = [principal]
    respaldo = "" if proveedor else settings.AI_FALLBACK_PROVIDER
    if respaldo and respaldo != principal:
        nombres.append(respaldo)

    clientes: list[AIClient] = []
    motivos: list[str] = []
    for nombre in nombres:
        try:
            clientes.append(get_ai_client(nombre))
        except AIError as exc:
            logger.warning("IA no disponible (%s): %s", nombre, exc)
            motivos.append(str(exc))

    if not clientes:
        return ClienteIANoDisponible("; ".join(motivos))
    if len(clientes) == 1:
        return clientes[0]
    return ClienteConRespaldo(clientes)
