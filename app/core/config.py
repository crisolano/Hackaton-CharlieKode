import os
from enum import StrEnum
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class SalaEstado(StrEnum):
    ACTIVA = "activa"
    INHABILITADA = "inhabilitada"


class EquipoEstado(StrEnum):
    DISPONIBLE = "disponible"
    PRESTADO = "prestado"
    DANADO = "danado"
    INHABILITADO = "inhabilitado"


class IncidenciaCategoria(StrEnum):
    ELECTRICA = "electrica"
    RED = "red"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    MOBILIARIO = "mobiliario"
    ASEO = "aseo"
    SEGURIDAD = "seguridad"
    OTRA = "otra"


class IncidenciaPrioridad(StrEnum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class IncidenciaRuta(StrEnum):
    MANTENIMIENTO = "mantenimiento"
    SOPORTE_TECNICO = "soporte_tecnico"
    ADMINISTRACION = "administracion"
    SEGURIDAD = "seguridad"
    REVISION_MANUAL = "revision_manual"


class IncidenciaEstado(StrEnum):
    PENDIENTE_REVISION = "pendiente_revision"
    CLASIFICADA = "clasificada"
    EN_PROCESO = "en_proceso"
    RESUELTA = "resuelta"


class Settings:
    PROJECT_NAME: str = "Sistema Central de Gestión Operativa del Campus"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./campus.db")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "")
    GEMINI_BASE_URL: str = os.getenv(
        "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"
    )
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "10"))
    AI_MAX_RETRIES: int = int(os.getenv("AI_MAX_RETRIES", "1"))
    # Si se define, todos los endpoints /api exigen esta clave en el header X-API-Key.
    API_KEY: str = os.getenv("API_KEY", "")
    # En "production" se ocultan /docs, /redoc y /openapi.json.
    APP_ENV: str = os.getenv("APP_ENV", "development")
    # Peticiones por minuto y por cliente para POST /api/incidencias (llaman a la IA).
    INCIDENCIAS_POR_MINUTO: int = int(os.getenv("INCIDENCIAS_POR_MINUTO", "20"))


settings = Settings()
