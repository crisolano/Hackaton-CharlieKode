# Sprint 3 — Dev 2: API e IA

## Ramas de este sprint
Todas salen de `develop` y vuelven por PR. Sin funcionalidades nuevas: solo estabilizar.

| # | Rama | Cubre | PR a |
|---|---|---|---|
| 1 | `feature/dev2-robustez-ia` | Reintentos acotados, fallback a Groq y errores claros | `develop` |
| 2 | `feature/dev2-ajuste-prompts` | Ajuste final de prompts con casos reales | `develop` |
| 3 | `feature/dev2-revision-seguridad` | Revisión de claves, formato de errores y variables en Vercel | `develop` |

Antes de cada PR: `git merge origin/develop`, `pytest` y `ruff check .`.

- [ ] Robustez de la IA: reintentos acotados (`AI_MAX_RETRIES`), fallback a Groq y errores claros.
- [ ] Revisión de seguridad: sin claves en el repo, sin respuestas quemadas, `.env` ignorado.
- [ ] Ajuste final de prompts con casos reales de incidencias.
- [ ] Revisar que todo error devuelva el formato `{ "ok": false, "codigo", "mensaje" }`.
- [ ] Cargar variables en el panel de Vercel (`vercel env`) y probar la IA desde el despliegue.
- [ ] Preparar la explicación del rol de la IA para la defensa.

**Listo cuando:** la IA funciona en el despliegue y un fallo del proveedor no rompe la app.
