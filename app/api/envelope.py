from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiOk(BaseModel, Generic[T]):
    """Formato estándar de éxito: { "ok": true, "data": ... }."""

    ok: bool = True
    data: T


def ok(data: Any) -> dict[str, Any]:
    """Envuelve la respuesta de un servicio; FastAPI la valida contra el response_model."""
    return {"ok": True, "data": data}
