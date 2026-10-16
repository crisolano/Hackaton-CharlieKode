from fastapi import APIRouter, Path, status

from app.api.deps import DbSession
from app.api.envelope import ApiOk, ok
from app.schemas import PrestamoCreate, PrestamoRead
from app.services import crear_prestamo, registrar_devolucion

router = APIRouter(prefix="/api/prestamos", tags=["Préstamos"])


@router.post(
    "",
    response_model=ApiOk[PrestamoRead],
    status_code=status.HTTP_201_CREATED,
    summary="Presta un equipo (aplica R3: solo equipos disponibles)",
)
def post_prestamo(datos: PrestamoCreate, db: DbSession):
    return ok(crear_prestamo(db, datos))


@router.post(
    "/{prestamo_id}/devolucion",
    response_model=ApiOk[PrestamoRead],
    summary="Registra la devolución de un préstamo y deja el equipo disponible",
)
def post_devolucion(db: DbSession, prestamo_id: int = Path(..., gt=0)):
    return ok(registrar_devolucion(db, prestamo_id))
