# Sprint 1 (0:15-1:45) — Fundamentos

**Meta:** módulo de espacios funcionando de punta a punta, sin IA.
**Entregable:** reservar una sala desde la UI; aforo excedido o solapamiento se rechazan con mensaje claro.

| Dev | Documento |
|---|---|
| Dev 1 — Datos y reglas | [dev1-datos-reglas.md](dev1-datos-reglas.md) |
| Dev 2 — API e IA | [dev2-api-ia.md](dev2-api-ia.md) |
| Dev 3 — Interfaz y entrega | [dev3-interfaz-entrega.md](dev3-interfaz-entrega.md) |

**Ramas:** features `feature/dev1-*`, `feature/dev2-*` y `feature/dev3-*` → PR a `develop`. Al terminar el sprint, los tres revisan `develop` (`pytest`, app arrancando) y se hace PR `develop` → `main`.

**Punto de integración (al final del sprint):** `POST /api/reservas` y el formulario HTMX usan el mismo `services.reservas.crear_reserva()`.
