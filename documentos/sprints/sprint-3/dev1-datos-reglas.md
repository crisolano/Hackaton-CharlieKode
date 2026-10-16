# Sprint 3 — Dev 1: Datos y reglas

## Ramas de este sprint
Todas salen de `develop` y vuelven por PR. Sin funcionalidades nuevas: solo estabilizar.

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev1-casos-borde-dataset` | Casos borde, registros inconsistentes y seed contra Postgres | `develop` |
| 2 | `feature/dev1-pruebas-finales` | Pruebas finales de R1, R2 y R3 | `develop` |
| 3 | `feature/dev1-cambio-regla-vivo` | Centralizar umbrales/mensajes y documentar el cambio en vivo | `develop` |

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

- [ ] Casos borde del dataset y registros inconsistentes (reporte de filas rechazadas visible en el log del seed).
- [ ] Verificar el seed contra Postgres (Neon/Supabase) con `DATABASE_URL`.
- [ ] Pruebas finales de R1, R2 y R3 (límite exacto de aforo, reservas contiguas sin solape).
- [ ] Preparar el cambio de regla en vivo: archivo, línea y valor en `app/rules/` y `core/config.py` (menos de 3 min).
- [ ] Practicar el cambio con un compañero.

**Listo cuando:** `pytest` completo en verde y el cambio de regla ensayado.
