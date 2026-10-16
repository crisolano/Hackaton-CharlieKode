import os
from enum import StrEnum
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def _numero_env(nombre: str, defecto: str, tipo: type[int] | type[float] = int) -> int | float:
    """Lee una variable numérica; si el valor no es un número, falla diciendo cuál variable es."""
    valor = os.getenv(nombre, defecto)
    try:
        return tipo(valor)
    except ValueError:
        raise ValueError(
            f"La variable de entorno {nombre} debe ser un número ({tipo.__name__})."
        ) from None


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
    AI_TIMEOUT_SECONDS: int = _numero_env("AI_TIMEOUT_SECONDS", "10")
    AI_MAX_RETRIES: int = _numero_env("AI_MAX_RETRIES", "1")
    # Proveedor de respaldo si el principal falla (vacío = sin respaldo).
    AI_FALLBACK_PROVIDER: str = os.getenv("AI_FALLBACK_PROVIDER", "")
    # Espera base entre reintentos (se duplica en cada intento); Retry-After del proveedor manda.
    AI_BACKOFF_SECONDS: float = _numero_env("AI_BACKOFF_SECONDS", "0.5", float)
    # Tope de tiempo total por proveedor, sumando peticiones y esperas.
    AI_TOTAL_TIMEOUT_SECONDS: float = _numero_env("AI_TOTAL_TIMEOUT_SECONDS", "20", float)
    # Si se define, todos los endpoints /api exigen esta clave en el header X-API-Key.
    API_KEY: str = os.getenv("API_KEY", "")
    # En "production" se ocultan /docs, /redoc y /openapi.json.
    APP_ENV: str = os.getenv("APP_ENV", "development")
    # Peticiones por minuto y por cliente para POST /api/incidencias (llaman a la IA).
    INCIDENCIAS_POR_MINUTO: int = _numero_env("INCIDENCIAS_POR_MINUTO", "20")


settings = Settings()
