from fastapi import APIRouter

from app.api.routers import reservas, salas

api_router = APIRouter()
api_router.include_router(salas.router)
api_router.include_router(reservas.router)
