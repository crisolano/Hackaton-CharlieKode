# Sprint 2 — Dev 1: Datos y reglas

- [ ] Modelos `Equipo`, `Prestamo` e `Incidencia` y sus esquemas.
- [ ] Seed de equipos desde el dataset oficial.
- [ ] `services/prestamos.py`: préstamo y devolución con cambios de estado (disponible ↔ prestado).
- [ ] R3 en `app/rules/` (recurso inhabilitado o ya prestado), aplicada a salas y equipos; integrarla en `crear_reserva()`.
- [ ] `services/incidencias.py`: registro, estados (`pendiente_revision`, `clasificada`, ...) y persistencia.
- [ ] Pruebas de R3 y de integridad de datos en `tests/rules/` y `tests/services/`.

**Listo cuando:** no se puede prestar un equipo ya prestado ni reservar una sala inhabilitada.
