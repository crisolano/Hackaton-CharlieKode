# Sprint 1 — Dev 3: Interfaz y entrega

## Ramas de este sprint
Todas salen de `develop` y vuelven a `develop` por PR (ver [03-gitflow.md](../../03-gitflow.md)). Orden sugerido:

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev3-base-templates` | `base.html` con Tailwind y HTMX, rutas HTML y `static/` | `develop` |
| 2 | `feature/dev3-pagina-salas-reserva` | Tabla de salas, formulario de reserva con HTMX y estados de carga (usa `crear_reserva()` de Dev 1) | `develop` |
| 3 | `feature/dev3-docker-readme` | Verificación de `docker compose` y esqueleto del README | `develop` |

**Orden de merge:** fase 1 = `S1-PR1`, fase 2 = `S1-PR14`, fase 3 = `S1-PR2`. Detalle, dependencias y zonas de choque en [05-orden-de-pull-requests.md](../../05-orden-de-pull-requests.md).

> **Aviso para el agente y para quien trabaja:** antes de crear una rama o abrir un PR, consulta ese documento. Si alguna dependencia (columna "Depende de") todavía no está mergeada en `develop`, no abras el PR: avisa al usuario de qué PR falta y quién lo tiene. Si ves que un PR salta el orden o apunta a `main`, avísalo también.

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

**Carpetas:** `app/web`, `Dockerfile`, `docker-compose.yml`, `vercel.json`, `README.md`, `documentos/`.

- [ ] Plantilla base Jinja2 (`templates/base.html`) con Tailwind por CDN y HTMX cargado.
- [ ] Rutas HTML en `app/web/routes.py` y montaje de `static/`.
- [ ] Página de salas (nombre, aforo, estado) con tabla, leída de la base de datos; el selector de salas del formulario se genera desde los datos, sin opciones escritas a mano en la plantilla.
- [ ] Formulario de reserva con HTMX (`hx-post`) que llama al servicio y devuelve un parcial de éxito o error.
- [ ] Mensajes de éxito, error y estados de carga (`hx-indicator`).
- [ ] Verificar que `docker compose up --build` arranca la app.
- [ ] Esqueleto del README (problema, integrantes, stack, instalación).

**Listo cuando:** se puede reservar una sala desde el navegador y los errores se ven en pantalla.
