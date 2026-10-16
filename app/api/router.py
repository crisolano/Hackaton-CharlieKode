from fastapi import APIRouter, Depends

from app.api.deps import verificar_api_key
from app.api.routers import equipos, incidencias, prestamos, reservas, salas

api_router = APIRouter(dependencies=[Depends(verificar_api_key)])
api_router.include_router(salas.router)
api_router.include_router(reservas.router)
api_router.include_router(equipos.router)
api_router.include_router(prestamos.router)
api_router.include_router(incidencias.router)
