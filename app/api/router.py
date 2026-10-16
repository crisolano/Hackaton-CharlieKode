from fastapi import APIRouter

from app.api.routers import equipos, prestamos, reservas, salas

api_router = APIRouter()
api_router.include_router(salas.router)
api_router.include_router(reservas.router)
api_router.include_router(equipos.router)
api_router.include_router(prestamos.router)
