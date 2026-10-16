# Sprint 1 — Dev 3: Interfaz y entrega

## Ramas de este sprint
Todas salen de `develop` y vuelven a `develop` por PR (ver [03-gitflow.md](../../03-gitflow.md)). Orden sugerido:

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev3-base-templates` | `base.html` con Tailwind y HTMX, rutas HTML y `static/` | `develop` |
| 2 | `feature/dev3-pagina-salas-reserva` | Tabla de salas, formulario de reserva con HTMX y estados de carga (usa `crear_reserva()` de Dev 1) | `develop` |
| 3 | `feature/dev3-docker-readme` | Verificación de `docker compose` y esqueleto del README | `develop` |

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

**Carpetas:** `app/web`, `Dockerfile`, `docker-compose.yml`, `vercel.json`, `README.md`, `documentos/`.

- [ ] Plantilla base Jinja2 (`templates/base.html`) con Tailwind por CDN y HTMX cargado.
- [ ] Rutas HTML en `app/web/routes.py` y montaje de `static/`.
- [ ] Página de salas (nombre, aforo, estado) con tabla.
- [ ] Formulario de reserva con HTMX (`hx-post`) que llama al servicio y devuelve un parcial de éxito o error.
- [ ] Mensajes de éxito, error y estados de carga (`hx-indicator`).
- [ ] Verificar que `docker compose up --build` arranca la app.
- [ ] Esqueleto del README (problema, integrantes, stack, instalación).

**Listo cuando:** se puede reservar una sala desde el navegador y los errores se ven en pantalla.
