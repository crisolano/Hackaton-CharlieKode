import logging

from app.ai.base import AIClient, AIError

logger = logging.getLogger(__name__)


class ClienteConRespaldo(AIClient):
    """Prueba los proveedores en orden y pasa al siguiente si uno falla de forma reintentable.

    Un fallo no reintentable (clave inválida, petición rechazada, respuesta sin formato) se
    trata igual: también se prueba el siguiente, porque el objetivo es no perder la
    clasificación. Si todos fallan, se lanza el último error y el triaje deja la incidencia
    en revisión manual.
    """

    def __init__(self, clientes: list[AIClient]):
        if not clientes:
            raise AIError("ClienteConRespaldo necesita al menos un proveedor.")
        self._clientes = clientes
        self.nombre = " → ".join(c.nombre for c in clientes)

    def generate(self, prompt: str) -> str:
        ultimo: AIError | None = None
        for posicion, cliente in enumerate(self._clientes):
            try:
                texto = cliente.generate(prompt)
            except AIError as exc:
                ultimo = exc
                siguiente = (
                    self._clientes[posicion + 1].nombre
                    if posicion + 1 < len(self._clientes)
                    else None
                )
                if siguiente:
                    logger.warning(
                        "%s falló (%s); se usa el respaldo %s", cliente.nombre, exc, siguiente
                    )
                continue
            if posicion > 0:
                logger.info("Respuesta obtenida con el proveedor de respaldo %s", cliente.nombre)
            return texto
        raise ultimo  # type: ignore[misc]  # siempre hay al menos un cliente

    def close(self) -> None:
        for cliente in self._clientes:
            cliente.close()
