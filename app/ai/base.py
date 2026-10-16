from abc import ABC, abstractmethod
from typing import Self


class AIError(Exception):
    """Fallo al consultar al proveedor de IA (configuración, red, timeout o salida vacía).

    `codigo_http` guarda el estado devuelto por el proveedor, si lo hubo, para el log.
    Regla: el mensaje nunca incluye la clave, el prompt ni el cuerpo de la respuesta.
    """

    def __init__(self, mensaje: str, *, codigo_http: int | None = None):
        super().__init__(mensaje)
        self.codigo_http = codigo_http


class AIClient(ABC):
    """Interfaz única para cualquier proveedor de IA."""

    nombre: str = "El proveedor de IA"

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Envía el prompt al proveedor y devuelve el texto generado.

        Lanza AIError si no se puede obtener una respuesta.
        """

    def close(self) -> None:
        """Libera los recursos del cliente (conexiones); por defecto no hay nada que liberar."""
        return None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()
