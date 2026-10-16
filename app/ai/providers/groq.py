import time
from collections.abc import Callable

import httpx

from app.ai.base import AIError
from app.ai.providers.http_base import HttpAIClient


class GroqClient(HttpAIClient):
    """Proveedor de respaldo: API de Groq, compatible con el formato de OpenAI."""

    nombre = "Groq"

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        timeout: float,
        max_retries: int,
        transport: httpx.BaseTransport | None = None,
        *,
        backoff: float = 0.0,
        tiempo_total: float | None = None,
        dormir: Callable[[float], None] = time.sleep,
        reloj: Callable[[], float] = time.monotonic,
    ):
        if not api_key:
            raise AIError("Falta GROQ_API_KEY en la configuración.")
        if not model:
            raise AIError("Falta GROQ_MODEL en la configuración.")
        super().__init__(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
            max_retries=max_retries,
            transport=transport,
            backoff=backoff,
            tiempo_total=tiempo_total,
            dormir=dormir,
            reloj=reloj,
        )
        self._model = model

    def generate(self, prompt: str) -> str:
        body = {"model": self._model, "messages": [{"role": "user", "content": prompt}]}
        return self._extraer_texto(self._post("/chat/completions", body))

    @staticmethod
    def _extraer_texto(data: dict) -> str:
        if not isinstance(data, dict):
            raise AIError("Respuesta de Groq con formato inesperado.")
        try:
            opcion = data["choices"][0]
            texto = opcion["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIError("Respuesta de Groq con formato inesperado.") from exc
        if not isinstance(texto, str) or not texto.strip():
            motivo = opcion.get("finish_reason", "?") if isinstance(opcion, dict) else "?"
            raise AIError(f"Groq devolvió una respuesta vacía (motivo: {motivo}).")
        return texto
