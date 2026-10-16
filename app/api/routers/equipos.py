from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.api.envelope import ApiOk, ok
from app.core.config import EquipoEstado
from app.schemas import EquipoRead
from app.services import listar_equipos

router = APIRouter(prefix="/api/equipos", tags=["Equipos"])


@router.get(
    "",
    response_model=ApiOk[list[EquipoRead]],
    summary="Lista los equipos y su estado, con filtro opcional por estado",
)
def get_equipos(
    db: DbSession,
    estado: Annotated[EquipoEstado | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return ok(listar_equipos(db, estado.value if estado else None, limit=limit, offset=offset))
