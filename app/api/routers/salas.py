from fastapi import APIRouter

from app.api.deps import DbSession
from app.api.envelope import ApiOk, ok
from app.schemas import SalaRead
from app.services import listar_salas

router = APIRouter(prefix="/api/salas", tags=["Salas"])


@router.get("", response_model=ApiOk[list[SalaRead]], summary="Lista las salas con aforo y estado")
def get_salas(db: DbSession):
    return ok(listar_salas(db))
