import time
from collections.abc import Callable

import httpx

from app.ai.base import AIError
from app.ai.providers.http_base import HttpAIClient


class GeminiClient(HttpAIClient):
    nombre = "Gemini"

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
            raise AIError("Falta GEMINI_API_KEY en la configuración.")
        if not model:
            raise AIError("Falta GEMINI_MODEL en la configuración.")
        super().__init__(
            base_url=base_url,
            headers={"x-goog-api-key": api_key},
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
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        return self._extraer_texto(self._post(f"/models/{self._model}:generateContent", body))

    @staticmethod
    def _extraer_texto(data: dict) -> str:
        if not isinstance(data, dict):
            raise AIError("Respuesta de Gemini con formato inesperado.")
        feedback = data.get("promptFeedback")
        if isinstance(feedback, dict) and feedback.get("blockReason"):
            raise AIError("Gemini bloqueó la petición por sus filtros de seguridad.")
        try:
            candidato = data["candidates"][0]
            if "content" not in candidato:
                raise AIError(
                    f"Gemini no devolvió contenido (motivo: {candidato.get('finishReason', '?')})."
                )
            partes = candidato["content"]["parts"]
            texto = "".join(parte.get("text", "") for parte in partes)
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise AIError("Respuesta de Gemini con formato inesperado.") from exc
        if not texto.strip():
            raise AIError("Gemini devolvió una respuesta vacía.")
        return texto
