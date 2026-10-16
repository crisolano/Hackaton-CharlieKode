# Sprint 1 — Dev 1: Datos y reglas

**Carpetas:** `app/models`, `app/schemas`, `app/rules`, `app/services`, `app/data`, `datos/`, `tests/rules`, `tests/services`.

- [ ] Modelos SQLAlchemy `Sala` y `Reserva` (`app/models/`) y esquemas Pydantic (`app/schemas/`).
- [ ] Loader del dataset oficial con pandas/csv/json: normaliza y tolera registros inconsistentes (`app/data/loader.py`).
- [ ] Script de seed: carga las 9 salas con su aforo solo si la base está vacía y registra las filas rechazadas (`app/data/seed.py`).
- [ ] R1 (aforo) y R2 (solapamiento) como funciones puras en `app/rules/`.
- [ ] `services/reservas.py::crear_reserva()` aplicando R1 y R2 y lanzando excepciones de dominio.
- [ ] Pruebas de R1 y R2 en `tests/rules/` (caso válido e inválido de cada una).

**Listo cuando:** `pytest tests/rules` pasa y `crear_reserva()` rechaza aforo excedido y solapamiento.
