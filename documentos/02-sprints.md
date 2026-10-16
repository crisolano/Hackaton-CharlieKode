# Plan de sprints — 3 desarrolladores

Tiempo total: 5 h = pre-sprint (15 min) + 3 sprints de 1 h 30 min + cierre (15 min).

## Roles
| Dev | Rol | Carpetas |
|---|---|---|
| **Dev 1** | Datos y reglas de negocio | `backend/src/data`, `rules`, `services`, `tests` |
| **Dev 2** | API e IA | `backend/src/api`, `backend/src/ai` |
| **Dev 3** | Interfaz y entrega | `frontend`, `README.md`, `.env.example`, `documento` |

---

## Pre-sprint (0:00-0:15) — Los tres juntos
- [ ] Crear el repo Git con `.gitignore` (incluye `.env`) y `.env.example`.
- [ ] Acordar el modelo de datos y los endpoints (ver `01-arquitectura.md`).
- [ ] Crear la estructura de carpetas y hacer el primer commit.
- [ ] Revisar el dataset oficial apenas llegue.

---

## Sprint 1 (0:15-1:45) — Fundamentos
**Meta:** módulo de espacios funcionando de punta a punta, sin IA.
**Entregable:** reservar una sala desde la UI; aforo excedido o solapamiento se rechazan con mensaje claro.

### Dev 1 — Datos y reglas
- [ ] Cargar y normalizar el dataset oficial, tolerando registros inconsistentes.
- [ ] Persistencia en SQLite y carga de las 9 salas con su aforo.
- [ ] Regla R1 (aforo) y R2 (solapamiento) como funciones puras.
- [ ] `crearReserva()` aplicando R1 y R2.
- [ ] Pruebas de R1 y R2 (caso válido e inválido).

### Dev 2 — API e IA
- [ ] Servidor Express y middleware global de errores.
- [ ] Endpoints `GET /api/salas`, `POST /api/reservas`, `GET /api/reservas`.
- [ ] Formato estándar de éxito y error.
- [ ] Configuración de `.env` y prueba de conexión con el proveedor de IA autorizado.

### Dev 3 — Interfaz y entrega
- [ ] Estructura del frontend y cliente de la API.
- [ ] Pantalla de salas (nombre, aforo, estado) y formulario de reserva.
- [ ] Mensajes de éxito, error y estados de carga.
- [ ] Esqueleto del README.

---

## Sprint 2 (1:45-3:15) — Flujo con IA y módulos restantes
**Meta:** flujo vertical con IA y las 3 reglas implementadas.
**Entregable:** incidencia → triaje con IA → guardada y visible; equipos con préstamo y devolución.

### Dev 1 — Datos y reglas
- [ ] Módulo de equipos: préstamo y devolución con estados.
- [ ] Regla R3 (recurso inhabilitado o ya prestado), aplicada a salas y equipos.
- [ ] Módulo de incidencias: registro, estados y persistencia.
- [ ] Pruebas de R3 y de integridad de datos.

### Dev 2 — API e IA
- [ ] Adaptador de IA intercambiable y prompt de triaje con salida estructurada.
- [ ] Validación de la salida de la IA (categoría, prioridad y ruta permitidas).
- [ ] Manejo de timeout y respuestas inválidas: la incidencia queda "pendiente de revisión manual".
- [ ] Endpoints de equipos, préstamos e incidencias.
- [ ] (Opcional) Recomendación de sala según el tamaño del grupo.

### Dev 3 — Interfaz y entrega
- [ ] Pantalla de equipos con préstamo y devolución.
- [ ] Pantalla de incidencias que muestra categoría, prioridad y ruta de la IA.
- [ ] Estados de carga durante la llamada a la IA.
- [ ] Avance del README (problema, stack, reglas).

---

## Sprint 3 (3:15-4:45) — Robustez, pulido y defensa
**Meta:** MVP estable, documentado y listo para defender.
**Entregable:** demo ensayada; las 3 reglas demostrables con casos válidos e inválidos.

### Dev 1 — Datos y reglas
- [ ] Casos borde del dataset y registros inconsistentes.
- [ ] Pruebas finales de R1, R2 y R3.
- [ ] Preparar el cambio de regla en vivo (qué archivo, qué línea, en menos de 3 min).

### Dev 2 — API e IA
- [ ] Robustez de la IA (reintentos acotados, errores claros).
- [ ] Revisión de seguridad: sin claves en el repo, sin respuestas quemadas.
- [ ] Ajuste final de prompts y explicación del rol de la IA.

### Dev 3 — Interfaz y entrega
- [ ] Pulido de la UI y de los mensajes de validación.
- [ ] README completo: problema, integrantes, stack, uso de IA, reglas e instalación.
- [ ] Verificar la instalación y ejecución desde cero.
- [ ] Guion de la demo y del pitch.

---

## Cierre (4:45-5:00) — Los tres juntos
- [ ] Revisar el historial de Git: sin secretos.
- [ ] Ensayo de la demo: cada regla con un caso válido y uno inválido, más el flujo con IA.
- [ ] Todos pueden explicar la arquitectura y modificar una regla.

---

## Reglas de trabajo
- Cada dev edita solo sus carpetas; los cambios al contrato se acuerdan y van en un commit aparte.
- Una rama por dev y merge a `main` al final de cada sprint.
- Commits pequeños y frecuentes: el historial de Git se evalúa.

## Prioridad si el tiempo aprieta
1. Reglas de negocio y datos (25 pts).
2. Integración de IA (20 pts).
3. MVP funcional y UX (15 pts).
4. Lo primero que se recorta: la recomendación de sala con IA.

## Puntos a confirmar
- [ ] Stack definitivo del equipo.
- [ ] Proveedor de IA y modelos autorizados para la jornada.
- [ ] Si "Amarillas verdes" es una sala o dos.
- [ ] Formato de horarios de reserva (bloques fijos o libres).
