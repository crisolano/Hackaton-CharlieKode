# Sprint 2 — Dev 3: Interfaz y entrega

## Ramas de este sprint
Todas salen de `develop` (ya actualizada con el Sprint 1) y vuelven por PR. Orden sugerido:

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev3-pagina-equipos` | Pantalla de equipos con préstamo y devolución | `develop` |
| 2 | `feature/dev3-pagina-incidencias` | Formulario, lista con categoría/prioridad/ruta, indicador de carga y navegación común | `develop` |
| 3 | `feature/dev3-vercel-preview` | `vercel.json` si hace falta, primer preview y avance del README | `develop` |

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

- [ ] Página de equipos con botones de préstamo y devolución (HTMX).
- [ ] Página de incidencias: formulario en texto libre y lista con categoría, prioridad y ruta de la IA.
- [ ] Indicador de carga durante la llamada a la IA y distintivo "pendiente de revisión manual".
- [ ] Navegación común entre Espacios, Equipos e Incidencias.
- [ ] Preparar `vercel.json` (si hace falta) y primer despliegue de prueba con `vercel`.
- [ ] Avance del README (problema, stack, reglas, uso de IA).

**Listo cuando:** las tres pantallas funcionan con los endpoints reales y hay un preview en Vercel.
