# Orden de Pull Requests por sprint

Orden en que deben mergearse los PR según las fases de cada sprint y sus dependencias. Cada fila enlaza con el documento del dev que define esa tarea. Reglas de ramas en [03-gitflow.md](03-gitflow.md); plan general en [02-sprints.md](02-sprints.md).

Repositorio: https://github.com/crisolano/Hackaton-CharlieKode — responsable de los merges: Santiago Becerra.

## Antes de empezar: ramas base incorrectas
Según [03-gitflow.md](03-gitflow.md), las features van a `develop` y `main` solo recibe `develop` al cerrar cada sprint. Hoy los PR #5, #8, #10 y #11 apuntan a `main`, y el #7 ya se mergeó en `main`. Consecuencias:
- `develop` **no tiene** los modelos de Dev 1, así que las ramas de Dev 2 y Dev 3 que los necesitan no pueden salir de `develop`.
- Esos PR traen decenas de archivos ajenos (documentos, `app/web`, etc.) porque salieron de una base vieja, y varios figuran como conflictivos.

Acción previa, antes de mergear nada más (Santiago con cada autor):
1. Sincronizar `develop` con `main` para que contenga el #7.
2. Cambiar la base de los PR #5, #8, #10 y #11 a `develop`.
3. Cada autor ejecuta `git merge origin/develop`, resuelve conflictos en su rama y vuelve a pasar `pytest` y `ruff check .`.

## Sprint 1 — Fundamentos (espacios de punta a punta, sin IA)
Documentos: [Dev 1](sprints/sprint-1/dev1-datos-reglas.md) · [Dev 2](sprints/sprint-1/dev2-api-ia.md) · [Dev 3](sprints/sprint-1/dev3-interfaz-entrega.md)

| Orden | PR | Dev | Rama | Documento del dev | Por qué en este lugar |
|---|---|---|---|---|---|
| 1 | [#1](https://github.com/crisolano/Hackaton-CharlieKode/pull/1) (mergeado) | Dev 3 | `feature/dev3-base-templates` | [dev3](sprints/sprint-1/dev3-interfaz-entrega.md) | Plantilla base y rutas web |
| 2 | [#2](https://github.com/crisolano/Hackaton-CharlieKode/pull/2) (mergeado) | Dev 3 | `feature/dev3-docker-readme` | [dev3](sprints/sprint-1/dev3-interfaz-entrega.md) | Compose sin `.env` obligatorio y README |
| 3 | [#7](https://github.com/crisolano/Hackaton-CharlieKode/pull/7) (mergeado) | Dev 1 | `feature/dev1-modelos-salas-reservas` | [dev1](sprints/sprint-1/dev1-datos-reglas.md) | Los modelos son la base de Dev 2 y Dev 3 |
| 4 | [#6](https://github.com/crisolano/Hackaton-CharlieKode/pull/6) | Dev 3 | `feature/dev3-python-deps` | [dev3](sprints/sprint-1/dev3-interfaz-entrega.md) | Toca `requirements.txt` (compartido): conviene antes de que otros añadan librerías |
| 5 | [#5](https://github.com/crisolano/Hackaton-CharlieKode/pull/5) | Dev 2 | `feature/dev2-errores-handler` | [dev2](sprints/sprint-1/dev2-api-ia.md) | Handler global de errores; lo consumen los routers y la web |
| 6 | [#10](https://github.com/crisolano/Hackaton-CharlieKode/pull/10) | Dev 1 | `feature/dev1-reglas-r1-r2` | [dev1](sprints/sprint-1/dev1-datos-reglas.md) | R1 y R2 son puras; las usa el servicio |
| 7 | [#11](https://github.com/crisolano/Hackaton-CharlieKode/pull/11) | Dev 1 | `feature/dev1-servicio-reservas` | [dev1](sprints/sprint-1/dev1-datos-reglas.md) | `crear_reserva()`: punto de integración de API y formulario |
| 8 | [#4](https://github.com/crisolano/Hackaton-CharlieKode/pull/4) | Dev 3 | `feature/dev3-web-hardening` | [dev3](sprints/sprint-1/dev3-interfaz-entrega.md) | `NAV_ITEMS` inmutable y SRI; antes de añadir páginas |
| 9 | [#9](https://github.com/crisolano/Hackaton-CharlieKode/pull/9) | Dev 3 | `feature/dev3-htmx-errores` | [dev3](sprints/sprint-1/dev3-interfaz-entrega.md) | Envuelve el handler de #5: va después de él |
| 10 | [#8](https://github.com/crisolano/Hackaton-CharlieKode/pull/8) | Dev 2 | `feature/dev2-conexion-gemini` | [dev2](sprints/sprint-1/dev2-api-ia.md) | Independiente del resto; solo prueba de conexión |
| 11 | [#3](https://github.com/crisolano/Hackaton-CharlieKode/pull/3) | Dev 3 | `feature/dev3-docker-hardening` | [dev3](sprints/sprint-1/dev3-interfaz-entrega.md) | Solo Docker; no bloquea a nadie |
| 12 | _por crear_ | Dev 1 | `feature/dev1-seed-dataset` | [dev1](sprints/sprint-1/dev1-datos-reglas.md) | Carga las salas desde `datos/`; hace falta para ver datos reales |
| 13 | _por crear_ | Dev 2 | `feature/dev2-router-salas-reservas` | [dev2](sprints/sprint-1/dev2-api-ia.md) | Requiere #7 y #11 |
| 14 | _por crear_ | Dev 3 | `feature/dev3-pagina-salas-reserva` | [dev3](sprints/sprint-1/dev3-interfaz-entrega.md) | Requiere #11, #5 y #9; es lo que cierra "reservar desde el navegador" |

**Cierre del sprint:** los tres revisan `develop` (`pytest`, app arrancando) y se hace el PR `develop` → `main`. Detalle: [README del sprint 1](sprints/sprint-1/README.md).

## Sprint 2 — Flujo con IA y módulos restantes
Documentos: [Dev 1](sprints/sprint-2/dev1-datos-reglas.md) · [Dev 2](sprints/sprint-2/dev2-api-ia.md) · [Dev 3](sprints/sprint-2/dev3-interfaz-entrega.md)

| Orden | Dev | Rama | Documento del dev | Depende de |
|---|---|---|---|---|
| 1 | Dev 1 | `feature/dev1-modelos-equipos-incidencias` | [dev1](sprints/sprint-2/dev1-datos-reglas.md) | Sprint 1 cerrado. Va primero: los demás dependen de estos modelos |
| 2 | Dev 2 | `feature/dev2-adaptador-ia` | [dev2](sprints/sprint-2/dev2-api-ia.md) | Independiente de Dev 1 |
| 3 | Dev 1 | `feature/dev1-regla-r3` | [dev1](sprints/sprint-2/dev1-datos-reglas.md) | Modelos del paso 1 |
| 4 | Dev 1 | `feature/dev1-servicio-prestamos` | [dev1](sprints/sprint-2/dev1-datos-reglas.md) | Pasos 1 y 3 |
| 5 | Dev 1 | `feature/dev1-servicio-incidencias` | [dev1](sprints/sprint-2/dev1-datos-reglas.md) | Paso 1; publicar la firma temprano para Dev 2 |
| 6 | Dev 2 | `feature/dev2-triaje-incidencias` | [dev2](sprints/sprint-2/dev2-api-ia.md) | Paso 2 |
| 7 | Dev 2 | `feature/dev2-routers-equipos-incidencias` | [dev2](sprints/sprint-2/dev2-api-ia.md) | Pasos 4, 5 y 6 |
| 8 | Dev 3 | `feature/dev3-pagina-equipos` | [dev3](sprints/sprint-2/dev3-interfaz-entrega.md) | Paso 4 |
| 9 | Dev 3 | `feature/dev3-pagina-incidencias` | [dev3](sprints/sprint-2/dev3-interfaz-entrega.md) | Pasos 5 y 6 (cliente de IA por `Depends`) |
| 10 | Dev 3 | `feature/dev3-vercel-preview` | [dev3](sprints/sprint-2/dev3-interfaz-entrega.md) | Páginas funcionando |
| 11 | Dev 2 | `feature/dev2-recomendacion-sala` | [dev2](sprints/sprint-2/dev2-api-ia.md) | Opcional; es lo primero que se recorta |

**Cierre del sprint:** `develop` → `main`. Detalle: [README del sprint 2](sprints/sprint-2/README.md).

## Sprint 3 — Robustez, pulido y defensa
Sin funcionalidades nuevas; se congela a las 4:00. Documentos: [Dev 1](sprints/sprint-3/dev1-datos-reglas.md) · [Dev 2](sprints/sprint-3/dev2-api-ia.md) · [Dev 3](sprints/sprint-3/dev3-interfaz-entrega.md)

| Orden | Dev | Rama | Documento del dev | Nota |
|---|---|---|---|---|
| 1 | Dev 1 | `feature/dev1-casos-borde-dataset` | [dev1](sprints/sprint-3/dev1-datos-reglas.md) | Incluye el seed contra Postgres; lo necesita el despliegue |
| 2 | Dev 2 | `feature/dev2-robustez-ia` | [dev2](sprints/sprint-3/dev2-api-ia.md) | Reintentos y fallback a Groq |
| 3 | Dev 3 | `feature/dev3-pulido-ui` | [dev3](sprints/sprint-3/dev3-interfaz-entrega.md) | UI y mensajes de validación |
| 4 | Dev 1 | `feature/dev1-pruebas-finales` | [dev1](sprints/sprint-3/dev1-datos-reglas.md) | Límites de R1, R2 y R3 |
| 5 | Dev 2 | `feature/dev2-ajuste-prompts` | [dev2](sprints/sprint-3/dev2-api-ia.md) | Con casos reales |
| 6 | Dev 3 | `feature/dev3-despliegue-vercel` | [dev3](sprints/sprint-3/dev3-interfaz-entrega.md) | Postgres y `/health`; requiere el paso 1 |
| 7 | Dev 2 | `feature/dev2-revision-seguridad` | [dev2](sprints/sprint-3/dev2-api-ia.md) | Revisa claves y variables en Vercel; después del despliegue |
| 8 | Dev 1 | `feature/dev1-cambio-regla-vivo` | [dev1](sprints/sprint-3/dev1-datos-reglas.md) | Centraliza umbrales; ensayo de la defensa |
| 9 | Dev 3 | `feature/dev3-readme-final` | [dev3](sprints/sprint-3/dev3-interfaz-entrega.md) | Va al final: documenta lo que ya existe |

**Cierre:** PR final `develop` → `main` y checklist de [cierre](sprints/cierre/README.md).

## Reglas para ordenar los merges
1. Primero lo compartido (`requirements.txt`, `app/main.py`, `app/core/`), en su propio PR y avisando al equipo.
2. Primero modelos, luego reglas, luego servicios, luego API y web: sigue la dependencia de capas de [01-arquitectura.md](01-arquitectura.md).
3. Un PR que envuelve o consume a otro va después de este (#9 después de #5).
4. Tras cada merge, quien mergea corre `pytest` y levanta la app; si `develop` se rompe, se arregla antes de seguir.
