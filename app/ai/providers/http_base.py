from typing import Any

import httpx

from app.ai.base import AIClient, AIError


class HttpAIClient(AIClient):
    """Base de los proveedores que hablan HTTP+JSON: reintentos acotados y errores claros."""

    nombre: str = "El proveedor de IA"

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str],
        timeout: float,
        max_retries: int,
        transport: httpx.BaseTransport | None = None,
    ):
        if max_retries < 0:
            raise AIError("AI_MAX_RETRIES no puede ser negativo.")
        self._max_retries = max_retries
        self._http = httpx.Client(
            base_url=base_url, timeout=timeout, headers=headers, transport=transport
        )

    def _post(self, ruta: str, cuerpo: dict[str, Any]) -> Any:
        """POST con reintentos ante timeout, red, 5xx y 429; devuelve el JSON de la respuesta."""
        ultimo_error: Exception | None = None
        for _ in range(self._max_retries + 1):
            try:
                response = self._http.post(ruta, json=cuerpo)
                response.raise_for_status()
                try:
                    return response.json()
                except ValueError as exc:
                    raise AIError(f"{self.nombre} devolvió una respuesta que no es JSON.") from exc
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                ultimo_error = exc
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code < 500 and exc.response.status_code != 429:
                    raise AIError(
                        f"{self.nombre} rechazó la petición ({exc.response.status_code})."
                    ) from exc
                ultimo_error = exc
        raise AIError(f"No se obtuvo respuesta de {self.nombre}.") from ultimo_error

    def close(self) -> None:
        self._http.close()
