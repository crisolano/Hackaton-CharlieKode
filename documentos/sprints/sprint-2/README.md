# Sprint 2 (1:45-3:15) — Flujo con IA y módulos restantes

**Meta:** flujo vertical con IA y las 3 reglas implementadas.
**Entregable:** incidencia → triaje con IA → guardada y visible; equipos con préstamo y devolución.

| Dev | Documento |
|---|---|
| Dev 1 — Datos y reglas | [dev1-datos-reglas.md](dev1-datos-reglas.md) |
| Dev 2 — API e IA | [dev2-api-ia.md](dev2-api-ia.md) |
| Dev 3 — Interfaz y entrega | [dev3-interfaz-entrega.md](dev3-interfaz-entrega.md) |

**Ramas:** inicio del sprint con `git pull origin develop`; features `feature/dev1-*`, `feature/dev2-*` y `feature/dev3-*` → PR a `develop`. Al terminar, PR `develop` → `main`.

**Punto de integración:** `services.incidencias.crear_incidencia()` recibe el cliente de IA por inyección (`Depends`) y guarda el resultado del triaje.

**Orden de los PR de este sprint:** identificadores `S2-PR1`, `S2-PR2`... en [05-orden-de-pull-requests.md](../../05-orden-de-pull-requests.md).
