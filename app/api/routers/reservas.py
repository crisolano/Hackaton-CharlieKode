from fastapi import APIRouter, Query, status

from app.api.deps import DbSession
from app.api.envelope import ApiOk, ok
from app.schemas import ReservaCreate, ReservaRead
from app.services import crear_reserva, listar_reservas

router = APIRouter(prefix="/api/reservas", tags=["Reservas"])


@router.post(
    "",
    response_model=ApiOk[ReservaRead],
    status_code=status.HTTP_201_CREATED,
    summary="Crea una reserva (aplica R1 de aforo y R2 de solapamiento)",
)
def post_reserva(datos: ReservaCreate, db: DbSession):
    return ok(crear_reserva(db, datos))


@router.get(
    "",
    response_model=ApiOk[list[ReservaRead]],
    summary="Lista las reservas, con filtro opcional por sala",
)
def get_reservas(db: DbSession, sala_id: int | None = Query(default=None, gt=0)):
    return ok(listar_reservas(db, sala_id))
