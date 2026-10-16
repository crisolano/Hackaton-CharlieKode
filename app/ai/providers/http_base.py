import logging
import time
from collections.abc import Callable
from typing import Any

import httpx

from app.ai.base import AIClient, AIError

logger = logging.getLogger(__name__)

# Códigos que vale la pena reintentar: saturación o límite de cuota del proveedor.
_REINTENTABLES = {429, 500, 502, 503, 504}


class HttpAIClient(AIClient):
    """Base de los proveedores HTTP+JSON: reintentos acotados con espera y tope de tiempo."""

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str],
        timeout: float,
        max_retries: int,
        transport: httpx.BaseTransport | None = None,
        backoff: float = 0.0,
        tiempo_total: float | None = None,
        dormir: Callable[[float], None] = time.sleep,
        reloj: Callable[[], float] = time.monotonic,
    ):
        if max_retries < 0:
            raise AIError("AI_MAX_RETRIES no puede ser negativo.")
        if backoff < 0:
            raise AIError("AI_BACKOFF_SECONDS no puede ser negativo.")
        self._max_retries = max_retries
        self._backoff = backoff
        self._tiempo_total = tiempo_total
        self._dormir = dormir
        self._reloj = reloj
        self._http = httpx.Client(
            base_url=base_url, timeout=timeout, headers=headers, transport=transport
        )

    def _espera(self, intento: int, response: httpx.Response | None) -> float:
        """Retry-After del proveedor si lo manda (en segundos); si no, espera exponencial."""
        if response is not None:
            retry_after = response.headers.get("retry-after", "")
            if retry_after.isdigit():
                return float(retry_after)
        return self._backoff * (2**intento)

    def _post(self, ruta: str, cuerpo: dict[str, Any]) -> Any:
        """POST con reintentos ante timeout, red, 5xx y 429; devuelve el JSON de la respuesta."""
        inicio = self._reloj()
        motivo = "sin respuesta"
        codigo: int | None = None
        for intento in range(self._max_retries + 1):
            response: httpx.Response | None = None
            try:
                response = self._http.post(ruta, json=cuerpo)
                response.raise_for_status()
                try:
                    return response.json()
                except ValueError as exc:
                    raise AIError(f"{self.nombre} devolvió una respuesta que no es JSON.") from exc
            except httpx.TimeoutException:
                motivo, codigo = "timeout", None
            except httpx.TransportError as exc:
                motivo, codigo = f"error de red ({type(exc).__name__})", None
            except httpx.HTTPStatusError as exc:
                codigo = exc.response.status_code
                if codigo not in _REINTENTABLES:
                    raise AIError(
                        f"{self.nombre} rechazó la petición ({codigo}).", codigo_http=codigo
                    ) from exc
                motivo = f"HTTP {codigo}"

            logger.warning(
                "%s falló (intento %d de %d): %s",
                self.nombre,
                intento + 1,
                self._max_retries + 1,
                motivo,
            )
            if intento == self._max_retries:
                break
            espera = self._espera(intento, response)
            if self._tiempo_total is not None:
                restante = self._tiempo_total - (self._reloj() - inicio)
                if espera >= restante:
                    motivo += ", tope de tiempo alcanzado"
                    break
            if espera > 0:
                self._dormir(espera)

        raise AIError(
            f"No se obtuvo respuesta de {self.nombre} ({motivo}).",
            reintentable=True,
            codigo_http=codigo,
        )

    def close(self) -> None:
        self._http.close()
