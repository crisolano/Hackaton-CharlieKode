from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import ClienteIA, DbSession
from app.api.envelope import ApiOk, ok
from app.core.config import IncidenciaCategoria, IncidenciaEstado
from app.schemas import IncidenciaCreate, IncidenciaRead
from app.services import crear_incidencia, listar_incidencias

router = APIRouter(prefix="/api/incidencias", tags=["Incidencias"])


@router.post(
    "",
    response_model=ApiOk[IncidenciaRead],
    status_code=status.HTTP_201_CREATED,
    summary="Registra una incidencia y la clasifica con IA (o la deja pendiente de revisión)",
)
def post_incidencia(datos: IncidenciaCreate, db: DbSession, cliente_ia: ClienteIA):
    return ok(crear_incidencia(db, datos, ai_client=cliente_ia))


@router.get(
    "",
    response_model=ApiOk[list[IncidenciaRead]],
    summary="Lista las incidencias, con filtros opcionales por estado y categoría",
)
def get_incidencias(
    db: DbSession,
    estado: Annotated[IncidenciaEstado | None, Query()] = None,
    categoria: Annotated[IncidenciaCategoria | None, Query()] = None,
):
    return ok(
        listar_incidencias(
            db,
            estado=estado.value if estado else None,
            categoria=categoria.value if categoria else None,
        )
    )
