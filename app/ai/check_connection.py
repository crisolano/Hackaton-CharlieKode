"""Prueba de conexión con el proveedor de IA activo: python -m app.ai.check_connection"""

import sys

from app.ai.base import AIError
from app.ai.factory import get_ai_client
from app.core.config import settings

PROMPT_PRUEBA = "Responde únicamente con la palabra: ok"


def main() -> int:
    try:
        respuesta = get_ai_client().generate(PROMPT_PRUEBA)
    except AIError as exc:
        print(f"[FALLO] {settings.AI_PROVIDER}: {exc}")
        return 1
    print(f"[OK] {settings.AI_PROVIDER} respondió: {respuesta.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
