from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import setup_exception_handlers
from app.core.logging_config import setup_logging
from app.web.routes import STATIC_DIR
from app.web.routes import router as web_router

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sistema Central de Gestión Operativa del Campus - Hackatón Campuslands",
    version="0.1.0",
)

# Configuración global de excepciones de dominio
setup_exception_handlers(app)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(web_router)
app.include_router(api_router)


@app.get("/health", tags=["Salud"])
def health_check() -> dict:
    return {
        "ok": True,
        "status": "healthy",
    }
