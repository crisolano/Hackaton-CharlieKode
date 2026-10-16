# Sprint 1 — Dev 2: API e IA

## Ramas de este sprint
Todas salen de `develop` y vuelven a `develop` por PR (ver [03-gitflow.md](../../03-gitflow.md)). Orden sugerido:

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev2-errores-handler` | Handler global de errores y formato `ok`/`codigo`/`mensaje` | `develop` |
| 2 | `feature/dev2-router-salas-reservas` | `deps.py`, `/health`, routers de salas y reservas y sus pruebas (requiere la rama 1 de Dev 1 ya mergeada) | `develop` |
| 3 | `feature/dev2-conexion-gemini` | Carga de claves desde `.env` y prueba de conexión con Gemini | `develop` |

**Orden de merge:** fase 1 = `S1-PR5`, fase 2 = `S1-PR13`, fase 3 = `S1-PR10`. Detalle, dependencias y zonas de choque en [05-orden-de-pull-requests.md](../../05-orden-de-pull-requests.md).

> **Aviso para el agente y para quien trabaja:** antes de crear una rama o abrir un PR, consulta ese documento. Si alguna dependencia (columna "Depende de") todavía no está mergeada en `develop`, no abras el PR: avisa al usuario de qué PR falta y quién lo tiene. Si ves que un PR salta el orden o apunta a `main`, avísalo también.

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

**Carpetas:** `app/api`, `app/ai`, `tests/api`, `tests/ai`.

- [ ] Handler global de errores: convierte excepciones de dominio a `{ "ok": false, "codigo", "mensaje" }`.
- [ ] Dependencias en `app/api/deps.py` (sesión de BD).
- [ ] Routers: `GET /api/salas`, `POST /api/reservas`, `GET /api/reservas` con esquemas Pydantic.
- [ ] Formato estándar de éxito `{ "ok": true, "data": ... }`.
- [ ] `GET /health`.
- [ ] Carga de claves desde `.env` y prueba de conexión con Gemini (primer llamado real desde `app/ai/`).
- [ ] Pruebas de la API con `httpx`/`TestClient` en `tests/api/` (reserva válida, aforo excedido, sala ocupada).

**Listo cuando:** Swagger (`/docs`) permite crear una reserva y devuelve el error correcto en cada rechazo.
