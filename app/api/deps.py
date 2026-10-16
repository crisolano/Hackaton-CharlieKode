from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.base import AIClient
from app.ai.factory import get_ai_client_seguro
from app.core.database import get_db

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
