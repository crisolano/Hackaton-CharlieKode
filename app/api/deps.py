import secrets
import time
from collections import defaultdict, deque
from collections.abc import Generator
from threading import Lock
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from app.ai.base import AIClient
from app.ai.factory import get_ai_client_seguro
from app.core.config import settings
from app.core.database import get_db
from app.core.errors import (
    HTTP_TOO_MANY_REQUESTS,
    HTTP_UNAUTHORIZED,
    AppException,
)

# Sesión de base de datos inyectada en los routers; las pruebas la reemplazan
# con app.dependency_overrides[get_db].
DbSession = Annotated[Session, Depends(get_db)]


def get_cliente_ia() -> Generator[AIClient, None, None]:
    """Cliente de IA por petición: nunca falla al crearse y siempre se cierra al terminar."""
    cliente = get_ai_client_seguro()
    try:
        yield cliente
    finally:
        cliente.close()


# Cliente de IA inyectado en los routers; las pruebas lo reemplazan
# con app.dependency_overrides[get_cliente_ia].
ClienteIA = Annotated[AIClient, Depends(get_cliente_ia)]


def verificar_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    """Exige X-API-Key en la API cuando API_KEY está configurada; sin ella la API queda abierta."""
    esperada = settings.API_KEY
    if esperada and not secrets.compare_digest((x_api_key or "").encode(), esperada.encode()):
        raise AppException("NO_AUTORIZADO", status_code=HTTP_UNAUTHORIZED)


class _LimitadorPorCliente:
    """Ventana deslizante de 60 s en memoria (por proceso); basta para frenar abuso básico."""

    def __init__(self) -> None:
        self._golpes: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def permitir(self, cliente: str, maximo: int) -> bool:
        ahora = time.monotonic()
        with self._lock:
            golpes = self._golpes[cliente]
            while golpes and ahora - golpes[0] >= 60:
                golpes.popleft()
            if len(golpes) >= maximo:
                return False
            golpes.append(ahora)
            return True

    def reiniciar(self) -> None:
        with self._lock:
            self._golpes.clear()


limitador_incidencias = _LimitadorPorCliente()


def limitar_incidencias(request: Request) -> None:
    cliente = request.client.host if request.client else "desconocido"
    if not limitador_incidencias.permitir(cliente, settings.INCIDENCIAS_POR_MINUTO):
        raise AppException("DEMASIADAS_PETICIONES", status_code=HTTP_TOO_MANY_REQUESTS)
