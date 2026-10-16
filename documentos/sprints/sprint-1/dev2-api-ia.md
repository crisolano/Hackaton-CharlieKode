# Sprint 1 — Dev 2: API e IA

**Carpetas:** `app/api`, `app/ai`, `tests/api`, `tests/ai`.

- [ ] Handler global de errores: convierte excepciones de dominio a `{ "ok": false, "codigo", "mensaje" }`.
- [ ] Dependencias en `app/api/deps.py` (sesión de BD).
- [ ] Routers: `GET /api/salas`, `POST /api/reservas`, `GET /api/reservas` con esquemas Pydantic.
- [ ] Formato estándar de éxito `{ "ok": true, "data": ... }`.
- [ ] `GET /health`.
- [ ] Carga de claves desde `.env` y prueba de conexión con Gemini (primer llamado real desde `app/ai/`).
- [ ] Pruebas de la API con `httpx`/`TestClient` en `tests/api/` (reserva válida, aforo excedido, sala ocupada).

**Listo cuando:** Swagger (`/docs`) permite crear una reserva y devuelve el error correcto en cada rechazo.
