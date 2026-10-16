# Sprint 2 — Dev 1: Datos y reglas

## Ramas de este sprint
Todas salen de `develop` (ya actualizada con el Sprint 1) y vuelven por PR. Orden sugerido:

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev1-modelos-equipos-incidencias` | Modelos y esquemas de `Equipo`, `Prestamo` e `Incidencia` (mergear primero) | `develop` |
| 2 | `feature/dev1-regla-r3` | R3 y su integración en `crear_reserva()` | `develop` |
| 3 | `feature/dev1-servicio-prestamos` | Préstamo y devolución, seed de equipos | `develop` |
| 4 | `feature/dev1-servicio-incidencias` | Registro, estados y persistencia (publicar la firma temprano para Dev 2) | `develop` |

**Orden de merge:** fase 1 = `S2-PR1`, fase 2 = `S2-PR3`, fase 3 = `S2-PR4`, fase 4 = `S2-PR5`. Detalle, dependencias y zonas de choque en [05-orden-de-pull-requests.md](../../05-orden-de-pull-requests.md).

> **Aviso para el agente y para quien trabaja:** antes de crear una rama o abrir un PR, consulta ese documento. Si alguna dependencia (columna "Depende de") todavía no está mergeada en `develop`, no abras el PR: avisa al usuario de qué PR falta y quién lo tiene. Si ves que un PR salta el orden o apunta a `main`, avísalo también.

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

- [ ] Modelos `Equipo`, `Prestamo` e `Incidencia` y sus esquemas.
- [ ] Seed de equipos desde el dataset oficial.
- [ ] `services/prestamos.py`: préstamo y devolución con cambios de estado (disponible ↔ prestado).
- [ ] R3 en `app/rules/` (recurso inhabilitado o ya prestado), aplicada a salas y equipos; integrarla en `crear_reserva()`.
- [ ] `services/incidencias.py`: registro, estados (`pendiente_revision`, `clasificada`, ...) y persistencia.
- [ ] Pruebas de R3 y de integridad de datos en `tests/rules/` y `tests/services/`.

**Listo cuando:** no se puede prestar un equipo ya prestado ni reservar una sala inhabilitada.
