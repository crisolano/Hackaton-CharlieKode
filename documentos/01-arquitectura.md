# Arquitectura — Sistema Central de Gestión Operativa del Campus

Hackatón Campuslands: "El campus bajo presión". MVP en 5 horas, equipo de 3 desarrolladores.

## 1. Objetivo del MVP
Un sistema que unifica en un solo flujo operativo:
1. **Espacios:** reserva de salas sin solapamientos ni excesos de aforo.
2. **Recursos tecnológicos:** préstamo y devolución de equipos con trazabilidad de estado.
3. **Incidencias:** triaje con IA (clasificación, prioridad y enrutamiento).

Regla central: nunca asignar espacios o recursos inhabilitados o con conflicto; la IA apoya la decisión.

## 2. Stack tecnológico (definitivo)

### Backend
| Tecnología | Uso |
|---|---|
| Python 3.11+ | Lenguaje |
| FastAPI | API JSON y páginas |
| Uvicorn | Servidor local y en contenedor |
| Pydantic | Valida peticiones, datos importados y la salida de la IA |
| SQLAlchemy | ORM; cambia de base de datos con `DATABASE_URL` |
| python-dotenv | Carga el `.env` en local |

### Frontend (opción B: renderizado en servidor)
| Tecnología | Uso |
|---|---|
| Jinja2 | Plantillas HTML desde FastAPI |
| HTMX | Interacción sin JavaScript propio |
| Tailwind CSS (CDN o CSS propio) | Estilos sin paso de build |

### Base de datos y datos
| Tecnología | Uso |
|---|---|
| SQLite | Desarrollo local y modo `docker compose` |
| Postgres gratuito (Neon o Supabase vía Vercel Marketplace) | Persistencia real desplegado |
| pandas / csv / json | Importación y limpieza de los datos oficiales |
| Script de seed | Carga los datos si la base está vacía y registra las filas rechazadas |

### Inteligencia Artificial (API key con free tier)
| Proveedor | Rol |
|---|---|
| Google Gemini API | Principal |
| Groq API | Respaldo |
| OpenRouter (`:free`) o Mistral | Alternativas |
| Adaptador `AIClient` | Cambia de proveedor con `AI_PROVIDER` |

### Despliegue
| Tecnología | Uso |
|---|---|
| Vercel | Aloja la app FastAPI (Python en Fluid Compute) y da el link público; variables de entorno en su panel |
| Vercel CLI | `vercel` para desplegar; `vercel env pull` para sincronizar variables |
| Vercel Marketplace | Aprovisiona el Postgres gratuito |
| Docker y docker-compose | Ruta oficial reproducible para el jurado y respaldo si falla Vercel |
| Endpoint `/health` | Comprueba que la app está viva |

### Calidad, seguridad y herramientas
| Tecnología | Uso |
|---|---|
| pytest + httpx | Pruebas de las 3 reglas y de la API |
| ruff | Formato y linting |
| `.env`, `.env.example`, `.gitignore` | Las claves nunca entran al repo |
| `requirements.txt` | Instalación reproducible |
| Git y GitHub | Commits frecuentes de todo el equipo |
| README.md, Swagger UI (`/docs`) / Postman | Documentación y prueba de endpoints |
| DB Browser for SQLite, VS Code | Inspección de datos y editor |

## 3. Datos base: salas y aforo
| Sala | Aforo |
|---|---|
| Auditorio | 100 |
| Cosmos | 25 |
| Skilab | 20 |
| Spooki | 38 |
| Apolo | 34 |
| Blanca | 12 |
| Azul | 10 |
| Amarillas verdes | 6 |
| Artemis | 32 |

El dataset oficial (entregado al inicio del evento) es la fuente de verdad. Estos valores se contrastan con él al cargarlo.

## 4. Vista general

```
┌─────────────────────┐   HTMX / HTML    ┌──────────────────────────────┐
│ Navegador           │ ───────────────▶ │ FastAPI                      │
│ Jinja2 + HTMX       │ ◀─────────────── │  web/  (páginas y parciales) │
│ Espacios · Equipos  │                  │  api/  (JSON, Swagger)       │
│ Incidencias         │                  └───────┬──────────────┬───────┘
└─────────────────────┘                          │              │
                                                 ▼              ▼
                                        ┌──────────────┐  ┌──────────────┐
                                        │ services/    │  │ ai/          │
                                        │ + rules/     │  │ AIClient     │
                                        └──────┬───────┘  └──────┬───────┘
                                               ▼                 ▼
                                        ┌──────────────┐  ┌──────────────┐
                                        │ SQLAlchemy   │  │ Gemini/Groq/ │
                                        │ SQLite/PG    │  │ OpenRouter   │
                                        └──────────────┘  └──────────────┘
```

**Capas y dependencias (en un solo sentido):**
`web/` y `api/` → `services/` → `rules/` y `models/`; `services/` → `ai/` solo para el triaje.

- `rules/` son funciones puras: no importan FastAPI, SQLAlchemy ni la IA. Se prueban solas y se modifican rápido en la defensa.
- `web/` y `api/` son capas delgadas: validan entrada, llaman a un servicio y formatean la salida. Nunca contienen reglas de negocio.
- `services/` orquestan: cargan datos, llaman a las reglas, persisten.

## 5. Estructura de carpetas
```
Hackaton-CharlieKode/
├── app/
│   ├── main.py              # crea la app FastAPI, monta routers y estáticos      (Pre-sprint)
│   ├── core/                # config.py (.env), database.py (engine/sesión),
│   │                        # errors.py (excepciones de dominio y handler)        (Dev 1 / Dev 2)
│   ├── models/              # entidades SQLAlchemy                                 (Dev 1)
│   ├── schemas/             # esquemas Pydantic de entrada y salida                (Dev 1)
│   ├── rules/               # reglas de negocio puras (R1, R2, R3)                 (Dev 1)
│   ├── services/            # reservas, equipos, préstamos, incidencias            (Dev 1)
│   ├── data/                # loader del dataset, seed, reporte de rechazos        (Dev 1)
│   ├── ai/                  # base.py (AIClient), providers/, prompts.py,
│   │   └── providers/       # triage.py (validación de salida)                    (Dev 2)
│   ├── api/                 # deps.py y routers/ JSON + /health                    (Dev 2)
│   │   └── routers/
│   └── web/                 # rutas HTML, templates/ (+ partials/), static/        (Dev 3)
├── datos/                   # dataset oficial (solo datos ficticios/autorizados)   (Dev 1)
├── tests/                   # espeja app/: rules/, services/, api/, ai/            (cada dueño)
├── documentos/              # arquitectura y sprints por dev                       (Dev 3)
├── Dockerfile               # imagen de la app                                     (Dev 3)
├── docker-compose.yml       # ruta reproducible para el jurado                     (Dev 3)
├── vercel.json              # configuración de despliegue (si hace falta)          (Dev 3)
├── requirements.txt         # dependencias de ejecución (versiones fijadas)
├── requirements-dev.txt     # + pytest y ruff
├── pyproject.toml           # configuración de ruff y pytest
├── .env.example             # variables sin valores reales
├── .gitignore               # incluye .env desde el primer commit
└── README.md                                                                       (Dev 3)
```

### Buenas prácticas del código
- **Una responsabilidad por módulo** y dependencias en un solo sentido (nunca `rules` → `services`).
- **Configuración centralizada** en `core/config.py`: umbrales, estados permitidos y mensajes de error en un solo lugar, no dispersos.
- **Tipado y validación:** type hints en todo y Pydantic en cada frontera (HTTP, datos importados, salida de la IA).
- **Excepciones de dominio** (`AforoExcedido`, `SalaOcupada`, `RecursoNoDisponible`) lanzadas por las reglas y convertidas a respuesta por un handler global; sin `except` desnudos.
- **Inyección de dependencias** de FastAPI (`Depends`) para sesión de BD y cliente de IA: facilita las pruebas con dobles.
- **Nada hardcodeado:** configuración y claves vienen de `.env`; salas, aforos y equipos vienen del dataset y la base de datos; las respuestas de la IA, del modelo real. Reglas completas en [04-guia-desarrollo.md](04-guia-desarrollo.md#11-regla-nada-hardcodeado).
- **Sin estado global ni secretos en código.**
- **ruff** limpio antes de cada commit; commits pequeños con mensajes descriptivos.

## 6. Modelo de datos
| Entidad | Campos |
|---|---|
| Sala | id, nombre, aforo, estado (activa / inhabilitada) |
| Reserva | id, sala_id, inicio, fin, asistentes, responsable |
| Equipo | id, nombre, estado (disponible / prestado / dañado / inhabilitado) |
| Prestamo | id, equipo_id, solicitante, fecha_inicio, fecha_devolucion |
| Incidencia | id, texto, categoria, prioridad, ruta, estado, origen_ia |

## 7. Reglas de negocio (mínimo 3)
| # | Regla | Rechazo |
|---|---|---|
| R1 | `asistentes <= aforo` de la sala | `AFORO_EXCEDIDO` |
| R2 | Sin solapamiento de horario en la misma sala | `SALA_OCUPADA` |
| R3 | No asignar sala o equipo inhabilitado, o equipo ya prestado | `RECURSO_NO_DISPONIBLE` |

Cada regla es una función pura en `app/rules/` con casos válidos e inválidos en `tests/rules/`.

## 8. Contrato de API (borrador)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Comprueba que la app está viva |
| GET | `/api/salas` | Lista salas con aforo y estado |
| POST | `/api/reservas` | Crea reserva (aplica R1, R2, R3) |
| GET | `/api/reservas` | Lista reservas |
| GET | `/api/equipos` | Lista equipos y estado |
| POST | `/api/prestamos` | Presta un equipo (R3) |
| POST | `/api/prestamos/{id}/devolucion` | Registra devolución |
| POST | `/api/incidencias` | Crea incidencia y ejecuta triaje con IA |
| GET | `/api/incidencias` | Lista incidencias |
| POST | `/api/recomendaciones/sala` | (opcional) La IA sugiere sala según el grupo |

Formato de error: `{ "ok": false, "codigo": "AFORO_EXCEDIDO", "mensaje": "..." }`.
Formato de éxito: `{ "ok": true, "data": ... }`.

Las páginas HTML (`/`, `/salas`, `/equipos`, `/incidencias`) y los parciales HTMX viven en `app/web/` y reutilizan los mismos servicios, por lo que las reglas se aplican igual por JSON o por HTML.

## 9. Rol de la IA
**Flujo principal: triaje de incidencias.**
1. El usuario escribe la incidencia en texto libre.
2. `ai/triage.py` envía el texto al proveedor activo (`AI_PROVIDER`) con un prompt que exige salida estructurada (categoría, prioridad, ruta).
3. La salida se **valida con Pydantic** contra valores permitidos; si es inválida o hay timeout, la incidencia se guarda como "pendiente de revisión manual" (nunca se inventa una respuesta).
4. Se guarda el resultado y se marca `origen_ia = true`.

**Adaptador `AIClient`:** interfaz única con un método de generación; cada proveedor (Gemini, Groq, OpenRouter, Mistral) es una clase en `ai/providers/`. Si el principal falla, se usa el respaldo (Groq).

**Flujo opcional:** recomendar la sala más ajustada al tamaño del grupo, respetando R1 a R3.

Principios: sin respuestas simuladas ni quemadas (penaliza 15 pts), proveedor intercambiable y claves leídas solo desde `.env`.

## 10. Seguridad
- `.env` en `.gitignore` desde el primer commit; solo `.env.example` con valores falsos.
- Sin API keys ni contraseñas en el historial de Git (penaliza 10 pts).
- En Vercel, las claves se cargan en el panel de variables de entorno.
- Solo datos ficticios o autorizados.

## 11. Manejo de errores y estados
- Handler global de errores: ninguna excepción sin controlar.
- Registros inconsistentes del dataset: se descartan o corrigen, se reportan y no rompen la carga.
- La UI muestra estados de carga, éxito y error en cada operación (indicadores de HTMX).

## 12. Ejecución y despliegue
| Modo | Comando |
|---|---|
| Local | `pip install -r requirements-dev.txt` → `uvicorn app.main:app --reload` |
| Docker (jurado) | `docker compose up --build` |
| Vercel | `vercel` (preview) / `vercel --prod`; `vercel env pull` para sincronizar variables |
| Pruebas y lint | `pytest` · `ruff check .` · `ruff format .` |

En Vercel la base es Postgres (Neon/Supabase) vía `DATABASE_URL`; en local y Docker, SQLite. El seed corre al iniciar solo si la base está vacía.

## 13. Cómo se defiende
- Explicar el flujo `web/api → services → rules → datos` y el rol de la IA.
- Cambio de regla en vivo (menos de 3 min): todas las reglas viven en `app/rules/`, y los umbrales y mensajes están centralizados en `core/config.py`.
