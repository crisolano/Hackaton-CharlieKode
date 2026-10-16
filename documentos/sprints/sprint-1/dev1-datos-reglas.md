# Sprint 1 — Dev 1: Datos y reglas

## Ramas de este sprint
Todas salen de `develop` y vuelven a `develop` por PR (ver [03-gitflow.md](../../03-gitflow.md)). Orden sugerido:

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev1-modelos-salas-reservas` | Modelos y esquemas de `Sala` y `Reserva` (mergear primero: Dev 2 y 3 dependen de ella) | `develop` |
| 2 | `feature/dev1-reglas-r1-r2` | R1, R2 y sus pruebas | `develop` |
| 3 | `feature/dev1-servicio-reservas` | `crear_reserva()` (publicar la firma temprano) | `develop` |
| 4 | `feature/dev1-seed-dataset` | Loader, seed de las 9 salas y reporte de rechazos | `develop` |

**Orden de merge:** fase 1 = `S1-PR3`, fase 2 = `S1-PR6`, fase 3 = `S1-PR7`, fase 4 = `S1-PR12`. Detalle, dependencias y zonas de choque en [05-orden-de-pull-requests.md](../../05-orden-de-pull-requests.md).

> **Aviso para el agente y para quien trabaja:** antes de crear una rama o abrir un PR, consulta ese documento. Si alguna dependencia (columna "Depende de") todavía no está mergeada en `develop`, no abras el PR: avisa al usuario de qué PR falta y quién lo tiene. Si ves que un PR salta el orden o apunta a `main`, avísalo también.

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

**Carpetas:** `app/models`, `app/schemas`, `app/rules`, `app/services`, `app/data`, `datos/`, `tests/rules`, `tests/services`.

- [ ] Modelos SQLAlchemy `Sala` y `Reserva` (`app/models/`) y esquemas Pydantic (`app/schemas/`).
- [ ] Loader del dataset oficial con pandas/csv/json: normaliza y tolera registros inconsistentes (`app/data/loader.py`).
- [ ] Script de seed: carga las 9 salas con su aforo **desde el dataset en `datos/`** (nunca desde listas en el código) solo si la base está vacía y registra las filas rechazadas (`app/data/seed.py`).
- [ ] R1 (aforo) y R2 (solapamiento) como funciones puras en `app/rules/`; el aforo se lee de la sala en la base de datos, y los mensajes y umbrales de `core/`.
- [ ] `services/reservas.py::crear_reserva()` aplicando R1 y R2 y lanzando excepciones de dominio.
- [ ] Pruebas de R1 y R2 en `tests/rules/` (caso válido e inválido de cada una).

**Listo cuando:** `pytest tests/rules` pasa y `crear_reserva()` rechaza aforo excedido y solapamiento.
