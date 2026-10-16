# Sprint 2 — Dev 2: API e IA

## Ramas de este sprint
Todas salen de `develop` (ya actualizada con el Sprint 1) y vuelven por PR. Orden sugerido:

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev2-adaptador-ia` | `AIClient`, proveedores Gemini y Groq, selección con `AI_PROVIDER` | `develop` |
| 2 | `feature/dev2-triaje-incidencias` | Prompt, validación con Pydantic, timeout, "pendiente de revisión" y pruebas con IA doble | `develop` |
| 3 | `feature/dev2-routers-equipos-incidencias` | Routers de equipos, préstamos e incidencias (requiere las ramas 1 y 3-4 de Dev 1 mergeadas) | `develop` |
| 4 | `feature/dev2-recomendacion-sala` | Opcional; primera tarea que se recorta | `develop` |

**Orden de merge:** fase 1 = `S2-PR2`, fase 2 = `S2-PR6`, fase 3 = `S2-PR7`, fase 4 = `S2-PR11`. Detalle, dependencias y zonas de choque en [05-orden-de-pull-requests.md](../../05-orden-de-pull-requests.md).

> **Aviso para el agente y para quien trabaja:** antes de crear una rama o abrir un PR, consulta ese documento. Si alguna dependencia (columna "Depende de") todavía no está mergeada en `develop`, no abras el PR: avisa al usuario de qué PR falta y quién lo tiene. Si ves que un PR salta el orden o apunta a `main`, avísalo también.

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

- [ ] `ai/base.py`: interfaz `AIClient`; `ai/providers/`: Gemini (principal) y Groq (respaldo); selección con `AI_PROVIDER`.
- [ ] `ai/prompts.py`: prompt de triaje que exige salida estructurada (categoría, prioridad, ruta); las opciones del prompt se generan desde las enumeraciones, no se copian a mano.
- [ ] Prohibido clasificar con reglas fijas o texto predefinido: si la IA falla, queda `pendiente_revision`.
- [ ] Modelo, timeout, reintentos y claves solo desde configuración (`.env`).
- [ ] `ai/triage.py`: valida la salida con Pydantic contra valores permitidos.
- [ ] Timeout y respuestas inválidas: la incidencia queda "pendiente de revisión manual", sin inventar respuesta.
- [ ] Routers: `GET /api/equipos`, `POST /api/prestamos`, `POST /api/prestamos/{id}/devolucion`, `POST /api/incidencias`, `GET /api/incidencias`.
- [ ] (Opcional) `POST /api/recomendaciones/sala` según el tamaño del grupo.
- [ ] Pruebas en `tests/ai/` con un cliente de IA doble (salida válida, inválida y timeout) y en `tests/api/`.

**Listo cuando:** una incidencia en texto libre vuelve clasificada, o queda pendiente de revisión si la IA falla.
