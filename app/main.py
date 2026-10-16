from fastapi import FastAPI

from app.core.config import settings
from app.core.errors import setup_exception_handlers

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sistema Central de Gestión Operativa del Campus - Hackatón Campuslands",
    version="0.1.0",
)

# Configuración global de excepciones de dominio
setup_exception_handlers(app)


@app.get("/health", tags=["Salud"])
def health_check() -> dict:
    return {
        "ok": True,
        "status": "healthy",
    }
