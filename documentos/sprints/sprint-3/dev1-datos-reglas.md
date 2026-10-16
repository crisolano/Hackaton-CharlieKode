# Sprint 3 — Dev 1: Datos y reglas

## Ramas de este sprint
Todas salen de `develop` y vuelven por PR. Sin funcionalidades nuevas: solo estabilizar.

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev1-casos-borde-dataset` | Casos borde, registros inconsistentes y seed contra Postgres | `develop` |
| 2 | `feature/dev1-pruebas-finales` | Pruebas finales de R1, R2 y R3 | `develop` |
| 3 | `feature/dev1-cambio-regla-vivo` | Centralizar umbrales/mensajes y documentar el cambio en vivo | `develop` |

**Orden de merge:** fase 1 = `S3-PR1`, fase 2 = `S3-PR4`, fase 3 = `S3-PR8`. Detalle, dependencias y zonas de choque en [05-orden-de-pull-requests.md](../../05-orden-de-pull-requests.md).

> **Aviso para el agente y para quien trabaja:** antes de crear una rama o abrir un PR, consulta ese documento. Si alguna dependencia (columna "Depende de") todavía no está mergeada en `develop`, no abras el PR: avisa al usuario de qué PR falta y quién lo tiene. Si ves que un PR salta el orden o apunta a `main`, avísalo también.

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

- [ ] Casos borde del dataset y registros inconsistentes (reporte de filas rechazadas visible en el log del seed).
- [ ] Verificar el seed contra Postgres (Neon/Supabase) con `DATABASE_URL`.
- [ ] Pruebas finales de R1, R2 y R3 (límite exacto de aforo, reservas contiguas sin solape).
- [ ] Preparar el cambio de regla en vivo: archivo, línea y valor en `app/rules/` y `core/config.py` (menos de 3 min).
- [ ] Practicar el cambio con un compañero.

**Listo cuando:** `pytest` completo en verde y el cambio de regla ensayado.
