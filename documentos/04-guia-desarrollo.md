# Guía de desarrollo

Acuerdos técnicos que los tres devs necesitan para no bloquearse entre sí. Los valores marcados con **(confirmar)** son propuestas hasta contrastarlas con el dataset oficial y el enunciado.

## 1. Puesta en marcha local
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env          # completar las claves de IA (nunca subir .env)
uvicorn app.main:app --reload   # http://localhost:8000  ·  Swagger: /docs  ·  Salud: /health
pytest                          # pruebas
ruff check . ; ruff format .    # lint y formato
```
Docker (ruta del jurado): `docker compose up --build`.

## 1.1 Regla: nada hardcodeado
Prohibido escribir en el código valores que deban venir de otro lugar. Penaliza en la evaluación (respuestas de IA quemadas: 15 pts; claves en el repo: 10 pts).

| Qué | Dónde debe vivir | Prohibido |
|---|---|---|
| Claves de API, `DATABASE_URL`, proveedor de IA, timeouts, reintentos | `.env` → `core/config.py` | Literales en el código, en plantillas o en commits |
| Salas, aforos, equipos y cualquier dato de negocio | Dataset oficial en `datos/` → seed → base de datos | Listas de salas o aforos en el código, en reglas o en plantillas |
| Respuestas de la IA (categoría, prioridad, ruta) | Salida real del modelo, validada | Respuestas simuladas, "fallback" que invente una clasificación o `if "proyector" in texto` |
| Valores permitidos (estados, categorías, prioridades, rutas) | Enumeraciones únicas ([sección 3](#3-valores-permitidos-confirmar)) | Strings repetidos en reglas, esquemas, prompts y plantillas |
| Umbrales y mensajes de error (p. ej. mínimos de asistentes) | `core/config.py` y `core/errors.py` | Números o textos mágicos dentro de las reglas |
| URLs, puertos y nombres de modelo de IA | Configuración | Literales dispersos en el código |
| Datos de pruebas | Fixtures en `tests/` | Datos de prueba dentro de `app/` |

Cuando la IA falla, el sistema **no inventa** nada: la incidencia queda `pendiente_revision`. Las pruebas usan un cliente de IA doble solo dentro de `tests/`.

Verificación rápida antes de cada PR: buscar en el diff claves, literales de salas/aforos y respuestas de IA fijas (`git diff develop | grep -inE "api_key|aiza|sk-|auditorio|skilab"`); el resultado solo debe aparecer en `tests/`, `datos/` o la documentación.

## 2. Variables de entorno
| Variable | Ejemplo | Uso |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./campus.db` · `postgresql+psycopg://...` | Base de datos (SQLAlchemy) |
| `AI_PROVIDER` | `gemini` | Proveedor activo: `gemini`, `groq`, `openrouter`, `mistral` |
| `GEMINI_API_KEY` / `GROQ_API_KEY` / `OPENROUTER_API_KEY` / `MISTRAL_API_KEY` | (vacío en el repo) | Claves; solo en `.env` o en el panel de Vercel |
| `AI_TIMEOUT_SECONDS` | `10` | Timeout por llamada a la IA |
| `AI_MAX_RETRIES` | `1` | Reintentos acotados |

Toda variable nueva se agrega a `.env.example` (sin valor real) y a `core/config.py`.

## 3. Valores permitidos (confirmar)
Viven como enumeraciones en un solo lugar (`app/core/config.py` o `app/schemas/`) y las usan reglas, esquemas y validación de la IA.

| Campo | Valores |
|---|---|
| Sala.estado | `activa`, `inhabilitada` |
| Equipo.estado | `disponible`, `prestado`, `danado`, `inhabilitado` |
| Incidencia.categoria | `electrica`, `red`, `hardware`, `software`, `mobiliario`, `aseo`, `seguridad`, `otra` |
| Incidencia.prioridad | `baja`, `media`, `alta`, `critica` |
| Incidencia.ruta | `mantenimiento`, `soporte_tecnico`, `administracion`, `seguridad`, `revision_manual` |
| Incidencia.estado | `pendiente_revision`, `clasificada`, `en_proceso`, `resuelta` |

Si la IA devuelve un valor fuera de estas listas, la incidencia queda en `pendiente_revision` con ruta `revision_manual`.

## 4. Convenciones de datos
- Fechas y horas en **ISO 8601** (`2026-10-16T14:00:00`); una sola zona horaria en todo el sistema (confirmar: hora local del campus).
- Una reserva exige `inicio < fin` y `asistentes >= 1`; si no, error de validación.
- Reservas contiguas (el fin de una = el inicio de otra) **no** se solapan.
- Nombres de campos en `snake_case` en código y JSON.
- Formato de horarios (bloques fijos o libres): **(confirmar)**.

## 5. Códigos de error
| Código | HTTP | Origen |
|---|---|---|
| `AFORO_EXCEDIDO` | 422 | R1 |
| `SALA_OCUPADA` | 409 | R2 |
| `RECURSO_NO_DISPONIBLE` | 409 | R3 |
| `NO_ENCONTRADO` | 404 | Sala, equipo, préstamo o incidencia inexistente |
| `DATOS_INVALIDOS` | 422 | Falla de validación de Pydantic |
| `IA_NO_DISPONIBLE` | 200 con incidencia en `pendiente_revision` | Timeout o salida inválida de la IA (no es un error para el usuario) |
| `ERROR_INTERNO` | 500 | Cualquier excepción no controlada (sin exponer detalles) |

El texto de cada mensaje vive en un solo archivo (`core/errors.py`) para poder cambiarlo en la defensa.

## 6. Ejemplos de contrato
**Crear reserva** — `POST /api/reservas`
```json
{ "sala_id": 3, "inicio": "2026-10-16T14:00:00", "fin": "2026-10-16T16:00:00", "asistentes": 30, "responsable": "Ana Pérez" }
```
Éxito: `{ "ok": true, "data": { "id": 1, "sala_id": 3, ... } }`
Rechazo: `{ "ok": false, "codigo": "AFORO_EXCEDIDO", "mensaje": "La sala Skilab admite 20 personas y se pidieron 30." }`

**Prestar equipo** — `POST /api/prestamos`: `{ "equipo_id": 5, "solicitante": "Luis Gómez", "fecha_devolucion": "2026-10-17T10:00:00" }`

**Crear incidencia** — `POST /api/incidencias`: `{ "texto": "El proyector de Apolo no enciende" }`
Respuesta: `{ "ok": true, "data": { "id": 7, "categoria": "hardware", "prioridad": "media", "ruta": "soporte_tecnico", "estado": "clasificada", "origen_ia": true } }`

## 7. Despliegue en Vercel: puntos que no se pueden olvidar
- El sistema de archivos de Vercel es **de solo lectura**: SQLite no sirve allí. En Vercel `DATABASE_URL` apunta al Postgres del Marketplace (Neon o Supabase), con el prefijo `postgresql+psycopg://`.
- El seed corre al iniciar solo si la base está vacía y debe ser idempotente (varias instancias pueden arrancar a la vez).
- Las claves de IA se cargan en el panel de Vercel; `vercel env pull` las baja a un `.env` local (ya ignorado por Git).
- La app expone `app` en `app/main.py`; Vercel la detecta como FastAPI. Verificar `/health` tras cada despliegue.

## 8. Herramientas de apoyo
| Herramienta | Para qué |
|---|---|
| Swagger UI (`/docs`) / Postman | Probar los endpoints |
| DB Browser for SQLite | Inspeccionar `campus.db` y verificar el seed |
| ruff | Lint y formato antes de cada commit |

## 9. Definición de "terminado" para una tarea
- [ ] Hace lo que dice el sprint y está probada (caso válido e inválido si es una regla).
- [ ] `pytest` y `ruff check .` pasan.
- [ ] Sin claves, `.env` ni datos reales.
- [ ] Nada hardcodeado ([sección 1.1](#11-regla-nada-hardcodeado)): ni configuración, ni datos de negocio, ni respuestas de IA.
- [ ] Rama actualizada con `develop` y PR revisado por otro dev ([03-gitflow.md](03-gitflow.md)).
- [ ] Si cambia el contrato, `01-arquitectura.md` y esta guía están actualizados.
