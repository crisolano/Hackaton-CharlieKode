# Plan de sprints — 3 desarrolladores

Tiempo total: 5 h = pre-sprint (15 min) + 3 sprints de 1 h 30 min + cierre (15 min).
Arquitectura y stack: ver [01-arquitectura.md](01-arquitectura.md).

Documentos de apoyo: [03-gitflow.md](03-gitflow.md) (ramas y PR) y [04-guia-desarrollo.md](04-guia-desarrollo.md) (puesta en marcha, valores permitidos, errores, ejemplos de contrato y Vercel).

## Roles
| Dev | Rol | Carpetas propias |
|---|---|---|
| **Dev 1** | Datos y reglas de negocio | `app/models`, `app/schemas`, `app/rules`, `app/services`, `app/data`, `datos/`, `tests/rules`, `tests/services` |
| **Dev 2** | API e IA | `app/api`, `app/ai`, `tests/api`, `tests/ai` |
| **Dev 3** | Interfaz y entrega | `app/web`, `Dockerfile`, `docker-compose.yml`, `vercel.json`, `README.md`, `documentos/` |

Compartido (se acuerda y va en commit aparte): `app/main.py`, `app/core/`, `requirements.txt`, `.env.example`.

## Índice (un documento por sprint y por dev)
| Fase | Horario | General | Dev 1 | Dev 2 | Dev 3 |
|---|---|---|---|---|---|
| Pre-sprint | 0:00-0:15 | [README](sprints/sprint-0-pre/README.md) | — | — | — |
| Sprint 1 | 0:15-1:45 | [README](sprints/sprint-1/README.md) | [dev1](sprints/sprint-1/dev1-datos-reglas.md) | [dev2](sprints/sprint-1/dev2-api-ia.md) | [dev3](sprints/sprint-1/dev3-interfaz-entrega.md) |
| Sprint 2 | 1:45-3:15 | [README](sprints/sprint-2/README.md) | [dev1](sprints/sprint-2/dev1-datos-reglas.md) | [dev2](sprints/sprint-2/dev2-api-ia.md) | [dev3](sprints/sprint-2/dev3-interfaz-entrega.md) |
| Sprint 3 | 3:15-4:45 | [README](sprints/sprint-3/README.md) | [dev1](sprints/sprint-3/dev1-datos-reglas.md) | [dev2](sprints/sprint-3/dev2-api-ia.md) | [dev3](sprints/sprint-3/dev3-interfaz-entrega.md) |
| Cierre | 4:45-5:00 | [README](sprints/cierre/README.md) | — | — | — |

## Reglas de trabajo
- Cada dev edita solo sus carpetas; los cambios al contrato se acuerdan y van en un commit aparte.
- Gitflow: ramas `feature/<dev>-<tema>` desde `develop`, PR a `develop`, y `develop` → `main` al final de cada sprint. Detalle en [03-gitflow.md](03-gitflow.md).
- Antes de cada PR, actualizar la feature con `develop` y resolver los choques en tu rama.
- Commits pequeños y frecuentes: el historial de Git se evalúa.
- `ruff check .` y `pytest` limpios antes de cada merge.

## Prioridad si el tiempo aprieta
1. Reglas de negocio y datos (25 pts).
2. Integración de IA (20 pts).
3. MVP funcional y UX (15 pts).
4. Lo primero que se recorta: la recomendación de sala con IA.

## Puntos a confirmar
- [ ] Proveedor de IA y modelos autorizados para la jornada.
- [ ] Si "Amarillas verdes" es una sala o dos.
- [ ] Formato de horarios de reserva (bloques fijos o libres).
- [ ] Postgres de Vercel Marketplace (Neon o Supabase) aprovisionado antes del Sprint 3.
