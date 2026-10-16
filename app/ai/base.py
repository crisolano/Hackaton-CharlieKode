from abc import ABC, abstractmethod


class AIError(Exception):
    """Fallo al consultar al proveedor de IA (configuración, red, timeout o salida vacía)."""


class AIClient(ABC):
    """Interfaz única para cualquier proveedor de IA."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Envía el prompt al proveedor y devuelve el texto generado.

        Lanza AIError si no se puede obtener una respuesta.
        """
