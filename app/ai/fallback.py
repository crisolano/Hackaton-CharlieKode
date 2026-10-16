import logging

from app.ai.base import AIClient, AIError

logger = logging.getLogger(__name__)


class ClienteConRespaldo(AIClient):
    """Prueba los proveedores en orden y pasa al siguiente si uno falla por cualquier motivo.

    También ante fallos de configuración (modelo inexistente, clave rechazada): el objetivo es
    no perder la clasificación. Si todos fallan se lanza AIError y el triaje deja la
    incidencia en revisión manual. Una incidencia puede costar como máximo
    (AI_MAX_RETRIES + 1) llamadas por proveedor configurado.
    """

    def __init__(self, clientes: list[AIClient]):
        if not clientes:
            raise AIError("ClienteConRespaldo necesita al menos un proveedor.")
        self._clientes = clientes
        self.nombre = " -> ".join(c.nombre for c in clientes)

    def generate(self, prompt: str) -> str:
        ultimo: AIError | None = None
        for posicion, cliente in enumerate(self._clientes):
            try:
                texto = cliente.generate(prompt)
            except Exception as exc:  # cualquier fallo de un proveedor pasa al siguiente
                ultimo = (
                    exc
                    if isinstance(exc, AIError)
                    else AIError(
                        f"{cliente.nombre} falló de forma inesperada ({type(exc).__name__})."
                    )
                )
                if posicion + 1 < len(self._clientes):
                    # Solo tipo y código HTTP: el mensaje podría traer datos del proveedor.
                    logger.warning(
                        "%s falló (%s, HTTP %s); se usa el respaldo %s",
                        cliente.nombre,
                        type(exc).__name__,
                        getattr(exc, "codigo_http", None),
                        self._clientes[posicion + 1].nombre,
                    )
                continue
            if posicion > 0:
                logger.info("Respuesta obtenida con el proveedor de respaldo %s", cliente.nombre)
            return texto
        assert ultimo is not None  # el bucle corre al menos una vez
        raise ultimo

    def close(self) -> None:
        for cliente in self._clientes:
            try:
                cliente.close()
            except Exception:  # cerrar uno no debe impedir cerrar los demás
                logger.warning("No se pudo cerrar el cliente %s", cliente.nombre)
