# Sprint 2 (1:45-3:15) — Flujo con IA y módulos restantes

**Meta:** flujo vertical con IA y las 3 reglas implementadas.
**Entregable:** incidencia → triaje con IA → guardada y visible; equipos con préstamo y devolución.

| Dev | Documento |
|---|---|
| Dev 1 — Datos y reglas | [dev1-datos-reglas.md](dev1-datos-reglas.md) |
| Dev 2 — API e IA | [dev2-api-ia.md](dev2-api-ia.md) |
| Dev 3 — Interfaz y entrega | [dev3-interfaz-entrega.md](dev3-interfaz-entrega.md) |

**Punto de integración:** `services.incidencias.crear_incidencia()` recibe el cliente de IA por inyección (`Depends`) y guarda el resultado del triaje.
