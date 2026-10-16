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
| _Pendiente_ | Dev 1 — Datos y reglas |
| _Pendiente_ | Dev 2 — API e IA |
| _Pendiente_ | Dev 3 — Interfaz y entrega |

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
_Se completa en el Sprint 2._ La IA clasifica las incidencias escritas en texto libre; su salida se valida contra valores permitidos y, si falla, la incidencia queda pendiente de revisión manual.

## Instalación y ejecución

### Con Docker (ruta recomendada)
```powershell
docker compose up --build
```
No hace falta crear `.env`; las claves de IA se leen de él solo si existe (`copy .env.example .env`).

- Aplicación: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Endpoint de salud: http://localhost:8000/health

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
3. **Variables de entorno:**
   ```powershell
   copy .env.example .env
   ```
4. **Ejecutar servidor local:**
   ```powershell
   uvicorn app.main:app --reload
   ```
5. **Pruebas y calidad de código:**
   ```powershell
   pytest
   ruff check .
   ruff format .
   ```

### En Vercel
_Se completa en el Sprint 3._
