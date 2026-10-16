# Sprint 2 — Dev 2: API e IA

- [ ] `ai/base.py`: interfaz `AIClient`; `ai/providers/`: Gemini (principal) y Groq (respaldo); selección con `AI_PROVIDER`.
- [ ] `ai/prompts.py`: prompt de triaje que exige salida estructurada (categoría, prioridad, ruta).
- [ ] `ai/triage.py`: valida la salida con Pydantic contra valores permitidos.
- [ ] Timeout y respuestas inválidas: la incidencia queda "pendiente de revisión manual", sin inventar respuesta.
- [ ] Routers: `GET /api/equipos`, `POST /api/prestamos`, `POST /api/prestamos/{id}/devolucion`, `POST /api/incidencias`, `GET /api/incidencias`.
- [ ] (Opcional) `POST /api/recomendaciones/sala` según el tamaño del grupo.
- [ ] Pruebas en `tests/ai/` con un cliente de IA doble (salida válida, inválida y timeout) y en `tests/api/`.

**Listo cuando:** una incidencia en texto libre vuelve clasificada, o queda pendiente de revisión si la IA falla.
