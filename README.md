# Sistema Central de Gestión Operativa del Campus

Hackatón Campuslands — "El campus bajo presión".

## Problema
Campuslands crece rápido y sus procesos dependen de registros dispersos y revisiones manuales: disponibilidad de aulas, préstamo de equipos y gestión de incidencias generan demoras, errores y fricción. Este MVP unifica los tres procesos en un solo flujo operativo asistido por IA:

1. **Espacios:** reserva de salas sin solapamientos ni excesos de aforo.
2. **Recursos tecnológicos:** préstamo y devolución de equipos con trazabilidad de estado.
3. **Incidencias:** triaje con IA (clasificación, prioridad y enrutamiento).

## Integrantes
| Nombre | Rol |
|---|---|
| Miguel Acevedo | Dev 1 — Datos y reglas |
| Juan Quintanilla | Dev 2 — API e IA |
| Cristian Solano | Dev 3 — Interfaz y entrega |
| Santiago Becerra | Responsable de los merges |

## Stack
- **Backend:** Python 3.11+, FastAPI, Pydantic, SQLAlchemy.
- **Frontend:** plantillas Jinja2 en el servidor, HTMX y Tailwind CSS (CDN), sin paso de build.
- **Datos:** SQLite en local y Docker; Postgres (Vercel Marketplace) en el despliegue.
- **IA:** adaptador `AIClient` con Gemini como proveedor principal y respaldo configurable.
- **Calidad:** pytest y ruff.
- **Despliegue:** Docker Compose (ruta oficial) y Vercel.

Detalle de capas y decisiones en [documentos/01-arquitectura.md](documentos/01-arquitectura.md).

## Reglas de negocio
| # | Regla | Código de rechazo |
|---|---|---|
| R1 | `asistentes <= aforo` de la sala | `AFORO_EXCEDIDO` |
| R2 | Sin solapamiento de horario en la misma sala | `SALA_OCUPADA` |
| R3 | No asignar sala o equipo inhabilitado, ni equipo ya prestado | `RECURSO_NO_DISPONIBLE` |

Viven en `app/rules/` como funciones puras.

## Uso de IA
El módulo de incidencias (`app/ai/`) implementa un triaje inteligente automatizado asistido por IA:
- **Adaptador desacoplado (`AIClient`):** Soporta Google Gemini (`gemini-2.5-flash-lite`) y Groq (`llama-3.1-8b-instant`) mediante un factory configurable por variable de entorno (`AI_PROVIDER`).
- **Triaje estructurado:** Analiza el texto libre de la incidencia y extrae:
  - `categoria`: electrica, red, hardware, software, mobiliario, aseo, seguridad, otra.
  - `prioridad`: baja, media, alta, critica.
  - `ruta`: mantenimiento, soporte_tecnico, administracion, seguridad, revision_manual.
- **Protección y validación:** Sanitiza inyecciones de prompt y valida la respuesta estructurada con esquemas Pydantic.
- **Tolerancia a fallos:** Si el proveedor de IA no está disponible o la respuesta es inválida, el sistema **no falla**: enruta automáticamente la incidencia a `revision_manual` con estado `pendiente_revision`.

## Instalación y ejecución

### Con Docker (ruta recomendada y reproducible)
```powershell
docker compose up --build
```
La aplicación inicializa automáticamente la base de datos con los datos oficiales de Campuslands (`datos/salas.csv` y `datos/equipos.csv`).

- **Aplicación web:** http://localhost:8000
- **Documentación interactiva (Swagger UI):** http://localhost:8000/docs
- **Endpoint de salud:** http://localhost:8000/health

### En local
1. **Crear y activar entorno virtual:**
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. **Instalar dependencias:**
   ```powershell
   pip install -r requirements-dev.txt
   ```
3. **Variables de entorno (opcional para IA real):**
   ```powershell
   copy .env.example .env
   ```
4. **Cargar dataset oficial (seed):**
   ```powershell
   python -m app.data.seed
   ```
5. **Ejecutar servidor local:**
   ```powershell
   uvicorn app.main:app --reload
   ```
6. **Pruebas y calidad de código:**
   ```powershell
   pytest
   ruff check .
   ```
