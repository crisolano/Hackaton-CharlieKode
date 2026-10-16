import httpx

from app.ai.base import AIClient, AIError


class GeminiClient(AIClient):
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        timeout: float,
        max_retries: int,
        transport: httpx.BaseTransport | None = None,
    ):
        if not api_key:
            raise AIError("Falta GEMINI_API_KEY en la configuración.")
        if not model:
            raise AIError("Falta GEMINI_MODEL en la configuración.")
        self._model = model
        self._max_retries = max_retries
        self._http = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={"x-goog-api-key": api_key},
            transport=transport,
        )

    def generate(self, prompt: str) -> str:
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        ultimo_error: Exception | None = None
        for _ in range(self._max_retries + 1):
            try:
                response = self._http.post(f"/models/{self._model}:generateContent", json=body)
                response.raise_for_status()
                try:
                    data = response.json()
                except ValueError as exc:
                    raise AIError("Gemini devolvió una respuesta que no es JSON.") from exc
                return self._extraer_texto(data)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                ultimo_error = exc
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code < 500 and exc.response.status_code != 429:
                    raise AIError(
                        f"Gemini rechazó la petición ({exc.response.status_code})."
                    ) from exc
                ultimo_error = exc
        raise AIError("No se obtuvo respuesta de Gemini.") from ultimo_error

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "GeminiClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    @staticmethod
    def _extraer_texto(data: dict) -> str:
        if not isinstance(data, dict):
            raise AIError("Respuesta de Gemini con formato inesperado.")
        if (data.get("promptFeedback") or {}).get("blockReason"):
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
