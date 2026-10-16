# Sprint 3 — Dev 3: Interfaz y entrega

## Ramas de este sprint
Todas salen de `develop` y vuelven por PR. Sin funcionalidades nuevas: solo estabilizar.

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev3-pulido-ui` | Pulido de la UI y mensajes de validación | `develop` |
| 2 | `feature/dev3-despliegue-vercel` | Despliegue con Postgres del Marketplace, link público y `/health` | `develop` |
| 3 | `feature/dev3-readme-final` | README completo, guion de demo y verificación desde cero | `develop` |

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

- [ ] Pulido de la UI y de los mensajes de validación.
- [ ] Despliegue en Vercel con Postgres del Marketplace; confirmar el link público y `/health`.
- [ ] README completo: problema, integrantes, stack, uso de IA, reglas e instalación (local, Docker y Vercel).
- [ ] Verificar la instalación y ejecución desde cero (`docker compose up --build` en una carpeta limpia).
- [ ] Guion de la demo y del pitch.

**Listo cuando:** un tercero puede instalar y correr el proyecto solo con el README.
