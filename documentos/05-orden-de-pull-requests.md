# Orden de Pull Requests por sprint

Objetivo: que los PR no choquen. Cada PR tiene un identificador `S<sprint>-PR<n>`: el número es el **orden de merge dentro del sprint**. "Fase" es el número de la rama en el documento de cada dev (la tabla "Ramas de este sprint").

Ejemplo: **S2-PR1 = Dev 1, fase 1** (`feature/dev1-modelos-equipos-incidencias`).

Reglas de ramas en [03-gitflow.md](03-gitflow.md); plan general en [02-sprints.md](02-sprints.md). Repositorio: https://github.com/crisolano/Hackaton-CharlieKode. Responsable de los merges: Santiago Becerra.

## Reglas para no chocar
1. **Se mergea en el orden del identificador.** No se salta un PR; si uno se atrasa, los que dependen de él esperan.
2. **Antes de abrir el PR:** `git merge origin/develop`, resolver conflictos en la propia rama, `pytest` y `ruff check .`.
3. **Cada dev toca solo sus carpetas** ([02-sprints.md](02-sprints.md)). Los archivos compartidos (`app/main.py`, `app/core/`, `requirements.txt`, `.env.example`) van en su propio PR, pequeño, y se avisa al equipo.
4. **Tras cada merge:** quien mergea corre `pytest` y levanta la app. Si `develop` se rompe, se arregla antes del siguiente PR.
5. **Dependencias de capas:** modelos → reglas → servicios → API y web (ver [01-arquitectura.md](01-arquitectura.md)).
6. **Si cambia un contrato** (modelo, esquema, endpoint), se actualiza la documentación y se mergea antes de que otros lo consuman.

7. **Para los agentes (Claude Code u otros):** antes de crear una rama o abrir un PR, comprobar aquí su identificador y la columna "Depende de". Si una dependencia no está mergeada en `develop`, no abrir el PR y avisar al usuario de qué PR falta; avisar también si algún PR salta el orden o apunta a `main`. Cada documento de dev de los sprints repite este aviso.

## Antes de empezar: ramas base incorrectas
Hoy los PR #5, #8, #10 y #11 apuntan a `main` y el #7 se mergeó en `main`; las features deben ir a `develop`. Efectos: `develop` no tiene los modelos de Dev 1 y esos PR traen decenas de archivos ajenos (base vieja). Acción previa, antes de seguir mergeando (Santiago con cada autor):
1. Sincronizar `develop` con `main` para que contenga el #7.
2. Cambiar la base de #5, #8, #10 y #11 a `develop`.
3. Cada autor ejecuta `git merge origin/develop`, resuelve conflictos y vuelve a pasar `pytest` y `ruff check .`.

---

## Sprint 1 — Fundamentos
Documentos: [Dev 1](sprints/sprint-1/dev1-datos-reglas.md) · [Dev 2](sprints/sprint-1/dev2-api-ia.md) · [Dev 3](sprints/sprint-1/dev3-interfaz-entrega.md) · [README del sprint](sprints/sprint-1/README.md)

| ID | Dev y fase | Rama / PR | Depende de | Zona de posible choque |
|---|---|---|---|---|
| S1-PR1 | Dev 3 · fase 1 | `feature/dev3-base-templates` · [#1](https://github.com/crisolano/Hackaton-CharlieKode/pull/1) (mergeado) | — | `app/web`, `app/main.py` |
| S1-PR2 | Dev 3 · fase 3 | `feature/dev3-docker-readme` · [#2](https://github.com/crisolano/Hackaton-CharlieKode/pull/2) (mergeado) | — | `docker-compose.yml`, `README.md` |
| S1-PR3 | Dev 1 · fase 1 | `feature/dev1-modelos-salas-reservas` · [#7](https://github.com/crisolano/Hackaton-CharlieKode/pull/7) (mergeado) | — | `app/models`, `app/schemas` |
| S1-PR4 | Dev 3 · extra | `feature/dev3-python-deps` · [#6](https://github.com/crisolano/Hackaton-CharlieKode/pull/6) | — | `requirements.txt` (compartido): va antes de que otros añadan librerías |
| S1-PR5 | Dev 2 · fase 1 | `feature/dev2-errores-handler` · [#5](https://github.com/crisolano/Hackaton-CharlieKode/pull/5) | S1-PR3 | `app/core/errors.py`, `app/main.py` |
| S1-PR6 | Dev 1 · fase 2 | `feature/dev1-reglas-r1-r2` · [#10](https://github.com/crisolano/Hackaton-CharlieKode/pull/10) | S1-PR3 | `app/rules` |
| S1-PR7 | Dev 1 · fase 3 | `feature/dev1-servicio-reservas` · [#11](https://github.com/crisolano/Hackaton-CharlieKode/pull/11) | S1-PR3, S1-PR6 | `app/services` |
| S1-PR8 | Dev 3 · extra | `feature/dev3-web-hardening` · [#4](https://github.com/crisolano/Hackaton-CharlieKode/pull/4) | S1-PR1 | `app/web/routes.py`, `base.html` |
| S1-PR9 | Dev 3 · extra | `feature/dev3-htmx-errores` · [#9](https://github.com/crisolano/Hackaton-CharlieKode/pull/9) | S1-PR5, S1-PR8 | `app/main.py`, `base.html` |
| S1-PR10 | Dev 2 · fase 3 | `feature/dev2-conexion-gemini` · [#8](https://github.com/crisolano/Hackaton-CharlieKode/pull/8) | S1-PR5 | `app/ai`, `app/core/config.py` |
| S1-PR11 | Dev 3 · extra | `feature/dev3-docker-hardening` · [#3](https://github.com/crisolano/Hackaton-CharlieKode/pull/3) | S1-PR2 | `Dockerfile`, `docker-compose.yml` |
| S1-PR12 | Dev 1 · fase 4 | `feature/dev1-seed-dataset` · [#16](https://github.com/crisolano/Hackaton-CharlieKode/pull/16) | S1-PR3 | `app/data`, `datos/` |
| S1-PR13 | Dev 2 · fase 2 | `feature/dev2-router-salas-reservas` · [#14](https://github.com/crisolano/Hackaton-CharlieKode/pull/14) (mergeado) | S1-PR5, S1-PR7 | `app/api`, `app/main.py` |
| S1-PR14 | Dev 3 · fase 2 | `feature/dev3-pagina-salas-reserva` (por crear) | S1-PR7, S1-PR9, S1-PR12 | `app/web/routes.py` (`NAV_ITEMS`), `app/main.py` |

**Cierre del sprint:** los tres revisan `develop` y se hace el PR `develop` → `main`.

---

## Sprint 2 — Flujo con IA y módulos restantes
Documentos: [Dev 1](sprints/sprint-2/dev1-datos-reglas.md) · [Dev 2](sprints/sprint-2/dev2-api-ia.md) · [Dev 3](sprints/sprint-2/dev3-interfaz-entrega.md) · [README del sprint](sprints/sprint-2/README.md)

| ID | Dev y fase | Rama | Depende de | Zona de posible choque |
|---|---|---|---|---|
| S2-PR1 | Dev 1 · fase 1 | `feature/dev1-modelos-equipos-incidencias` | Sprint 1 cerrado | `app/models`, `app/schemas`: va primero, todos dependen de él |
| S2-PR2 | Dev 2 · fase 1 | `feature/dev2-adaptador-ia` | — | `app/ai`, `app/core/config.py` |
| S2-PR3 | Dev 1 · fase 2 | `feature/dev1-regla-r3` | S2-PR1 | `app/rules`, `services/reservas.py` |
| S2-PR4 | Dev 1 · fase 3 | `feature/dev1-servicio-prestamos` | S2-PR1, S2-PR3 | `app/services`, `app/data` |
| S2-PR5 | Dev 1 · fase 4 | `feature/dev1-servicio-incidencias` | S2-PR1 | `app/services` (publicar la firma temprano para Dev 2) |
| S2-PR6 | Dev 2 · fase 2 | `feature/dev2-triaje-incidencias` | S2-PR2 | `app/ai` |
| S2-PR7 | Dev 2 · fase 3 | `feature/dev2-routers-equipos-incidencias` | S2-PR4, S2-PR5, S2-PR6 | `app/api`, `app/main.py` |
| S2-PR8 | Dev 3 · fase 1 | `feature/dev3-pagina-equipos` | S2-PR4 | `app/web/routes.py` (`NAV_ITEMS`) |
| S2-PR9 | Dev 3 · fase 2 | `feature/dev3-pagina-incidencias` | S2-PR5, S2-PR6 | `app/web/routes.py` (`NAV_ITEMS`) |
| S2-PR10 | Dev 3 · fase 3 | `feature/dev3-vercel-preview` | S2-PR8, S2-PR9 | `vercel.json`, `README.md` |
| S2-PR11 | Dev 2 · fase 4 | `feature/dev2-recomendacion-sala` (opcional) | S2-PR7 | `app/ai`, `app/api`; es lo primero que se recorta |

**Cierre del sprint:** PR `develop` → `main`.

---

## Sprint 3 — Robustez, pulido y defensa
Sin funcionalidades nuevas; se congela a las 4:00. Documentos: [Dev 1](sprints/sprint-3/dev1-datos-reglas.md) · [Dev 2](sprints/sprint-3/dev2-api-ia.md) · [Dev 3](sprints/sprint-3/dev3-interfaz-entrega.md) · [README del sprint](sprints/sprint-3/README.md)

| ID | Dev y fase | Rama | Depende de | Zona de posible choque |
|---|---|---|---|---|
| S3-PR1 | Dev 1 · fase 1 | `feature/dev1-casos-borde-dataset` | Sprint 2 cerrado | `app/data`; incluye el seed contra Postgres que usa el despliegue |
| S3-PR2 | Dev 2 · fase 1 | `feature/dev2-robustez-ia` | — | `app/ai` |
| S3-PR3 | Dev 3 · fase 1 | `feature/dev3-pulido-ui` | — | `app/web` |
| S3-PR4 | Dev 1 · fase 2 | `feature/dev1-pruebas-finales` | S3-PR1 | `tests/rules`, `tests/services` |
| S3-PR5 | Dev 2 · fase 2 | `feature/dev2-ajuste-prompts` | S3-PR2 | `app/ai/prompts.py` |
| S3-PR6 | Dev 3 · fase 2 | `feature/dev3-despliegue-vercel` | S3-PR1, S3-PR3 | `vercel.json`, variables de entorno |
| S3-PR7 | Dev 2 · fase 3 | `feature/dev2-revision-seguridad` | S3-PR6 | `.env.example`, `app/core/errors.py`; después del despliegue |
| S3-PR8 | Dev 1 · fase 3 | `feature/dev1-cambio-regla-vivo` | S3-PR4 | `app/rules`, `app/core/config.py` |
| S3-PR9 | Dev 3 · fase 3 | `feature/dev3-readme-final` | todos los anteriores | `README.md`, `documentos/`; va al final: documenta lo que ya existe |

**Cierre:** PR final `develop` → `main` y checklist de [cierre](sprints/cierre/README.md).

---

## Cómo se mantiene este documento
- Al crear un PR, se sustituye "(por crear)" por su enlace y número.
- Si una dependencia cambia, se actualiza la columna "Depende de" y se avisa al equipo.
- Los identificadores no se reutilizan: si un PR se cierra sin mergear, su fila queda tachada y no se renumera.
