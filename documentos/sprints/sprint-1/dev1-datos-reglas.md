# Sprint 1 — Dev 1: Datos y reglas

## Ramas de este sprint
Todas salen de `develop` y vuelven a `develop` por PR (ver [03-gitflow.md](../../03-gitflow.md)). Orden sugerido:

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev1-modelos-salas-reservas` | Modelos y esquemas de `Sala` y `Reserva` (mergear primero: Dev 2 y 3 dependen de ella) | `develop` |
| 2 | `feature/dev1-reglas-r1-r2` | R1, R2 y sus pruebas | `develop` |
| 3 | `feature/dev1-servicio-reservas` | `crear_reserva()` (publicar la firma temprano) | `develop` |
| 4 | `feature/dev1-seed-dataset` | Loader, seed de las 9 salas y reporte de rechazos | `develop` |

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

**Carpetas:** `app/models`, `app/schemas`, `app/rules`, `app/services`, `app/data`, `datos/`, `tests/rules`, `tests/services`.

- [ ] Modelos SQLAlchemy `Sala` y `Reserva` (`app/models/`) y esquemas Pydantic (`app/schemas/`).
- [ ] Loader del dataset oficial con pandas/csv/json: normaliza y tolera registros inconsistentes (`app/data/loader.py`).
- [ ] Script de seed: carga las 9 salas con su aforo solo si la base está vacía y registra las filas rechazadas (`app/data/seed.py`).
- [ ] R1 (aforo) y R2 (solapamiento) como funciones puras en `app/rules/`.
- [ ] `services/reservas.py::crear_reserva()` aplicando R1 y R2 y lanzando excepciones de dominio.
- [ ] Pruebas de R1 y R2 en `tests/rules/` (caso válido e inválido de cada una).

**Listo cuando:** `pytest tests/rules` pasa y `crear_reserva()` rechaza aforo excedido y solapamiento.
