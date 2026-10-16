# Flujo de trabajo con Git (Gitflow)

## Ramas
| Rama | Uso | Quién escribe |
|---|---|---|
| `main` | Versión estable y desplegable (Vercel producción). Solo recibe merges desde `develop` al cerrar cada sprint y al final. | Nadie directamente |
| `develop` | Integración: aquí se juntan todas las features. Siempre debe arrancar y pasar `pytest` y `ruff`. | Nadie directamente; solo vía Pull Request |
| `feature/<dev>-<tema>` | Una tarea concreta, creada desde `develop`. | El dev dueño |

Ejemplos: `feature/dev1-reglas-r1-r2`, `feature/dev2-router-reservas`, `feature/dev3-formulario-reserva`, `feature/dev2-adaptador-ia`.

Nombres en minúsculas, con guiones, una feature = una tarea del sprint. Features pequeñas (< 30 min) para que los merges sean fáciles.

## Ciclo de una feature
```bash
# 1. Partir de develop actualizado
git checkout develop
git pull origin develop
git checkout -b feature/dev1-reglas-r1-r2

# 2. Trabajar con commits pequeños
git add <archivos>
git commit -m "feat(rules): agrega R1 de aforo"

# 3. ANTES de abrir el PR: traer lo nuevo de develop y resolver choques en tu rama
git fetch origin
git merge origin/develop        # resolver conflictos aquí, no en develop
pytest && ruff check .          # deben pasar tras el merge

# 4. Subir y abrir Pull Request hacia develop
git push -u origin feature/dev1-reglas-r1-r2
```
5. Otro dev revisa el PR (no se aprueba el propio) y se hace merge a `develop`.
6. Borrar la rama de feature y volver a actualizar `develop` local (`git pull origin develop`).

## Actualizar `develop` (hacerlo seguido)
- Al empezar cada feature: `git pull origin develop` antes de crear la rama.
- Cada ~30 min y siempre antes del PR: `git merge origin/develop` dentro de tu feature.
- Cuando alguien avise que mergeó algo que te afecta (contrato, modelos, `core/`), actualiza de inmediato.

## Evitar que una cosa choque con otra
1. **Cada dev toca solo sus carpetas** (ver [02-sprints.md](02-sprints.md)). Es la principal defensa contra conflictos.
2. **Archivos compartidos** (`app/main.py`, `app/core/`, `requirements.txt`, `.env.example`): cambios pequeños, en su propia feature y mergeados a `develop` de inmediato; se avisa al equipo.
3. **Contrato primero:** si cambia un modelo, esquema o endpoint, se actualiza `01-arquitectura.md` y se mergea antes de que otros lo consuman.
4. **Dependencias entre devs:** Dev 2 y Dev 3 consumen funciones de `services/`. Dev 1 publica primero la firma (aunque sea con `NotImplementedError`) y la mergea temprano.
5. **Checklist de revisión del PR:**
   - [ ] La rama incluye el último `develop` (sin conflictos).
   - [ ] `pytest` y `ruff check .` pasan.
   - [ ] Solo toca carpetas del autor (o archivos compartidos justificados).
   - [ ] Sin `.env`, claves ni datos reales.
   - [ ] No rompe el contrato de API ni los formatos de error/éxito.
6. **Revisión de choques en `develop`:** tras cada merge, quien mergea corre `pytest` y levanta la app (`uvicorn app.main:app`). Si `develop` se rompe, se arregla antes de seguir.

## Integración con los sprints
- Durante el sprint: features → `develop` por PR.
- Al final de cada sprint (puntos de integración de cada `README.md` de sprint): los tres revisan juntos `develop`, y se hace PR `develop` → `main` con la demo del entregable funcionando.
- Hotfix urgente en `main`: rama `hotfix/<tema>` desde `main`, merge a `main` **y** a `develop`.

## Commits
- Formato: `tipo(ámbito): descripción` con tipos `feat`, `fix`, `test`, `docs`, `refactor`, `chore`.
- Commits pequeños y frecuentes; el historial se evalúa.
- Nunca commitear `.env` ni claves. Si pasa, rotar la clave: borrar el commit no basta.
- No usar `git push --force` en `develop` ni `main`.

## Protección recomendada en GitHub
En *Settings → Branches* para `main` y `develop`: exigir Pull Request y al menos 1 aprobación, y bloquear el push directo y el force push.
