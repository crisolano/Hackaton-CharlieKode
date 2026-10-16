# Arquitectura — Sistema Central de Gestión Operativa del Campus

Hackatón Campuslands: "El campus bajo presión". MVP en 5 horas, equipo de 3 desarrolladores.

> Stack propuesto (ajustable si el equipo domina otro): **Node.js + Express**, **SQLite**, frontend **HTML/JS (o React con Vite)**, IA detrás de un adaptador intercambiable.

## 1. Objetivo del MVP
Un sistema que unifica en un solo flujo operativo:
1. **Espacios:** reserva de salas sin solapamientos ni excesos de aforo.
2. **Recursos tecnológicos:** préstamo y devolución de equipos con trazabilidad de estado.
3. **Incidencias:** triaje con IA (clasificación, prioridad y enrutamiento).

Regla central: nunca asignar espacios o recursos inhabilitados o con conflicto; la IA apoya la decisión.

## 2. Datos base: salas y aforo
| Sala | Aforo |
|---|---|
| Auditorio | 100 |
| Cosmos | 25 |
| Skilab | 20 |
| Spooki | 38 |
| Apolo | 34 |
| Blanca | 12 |
| Azul | 10 |
| Amarillas verdes | 6 |
| Artemis | 32 |

El dataset oficial (entregado al inicio del evento) es la fuente de verdad. Estos valores se contrastan con él al cargarlo.

## 3. Vista general

```
┌────────────────────┐      HTTP/JSON      ┌─────────────────────────┐
│  Frontend (UI)     │ ───────────────────▶│  API (Express)          │
│  Espacios          │ ◀───────────────────│  rutas + errores        │
│  Equipos           │                     └───────┬─────────┬───────┘
│  Incidencias       │                             │         │
└────────────────────┘                             ▼         ▼
                                       ┌──────────────┐  ┌──────────────┐
                                       │ Servicios +  │  │ Módulo IA    │
                                       │ Reglas       │  │ (adaptador)  │
                                       └──────┬───────┘  └──────┬───────┘
                                              ▼                 ▼
                                       ┌──────────────┐  ┌──────────────┐
                                       │ SQLite       │  │ API/modelo   │
                                       │ (datos)      │  │ autorizado   │
                                       └──────────────┘  └──────────────┘
```

Capas y dependencias: `UI → API → Servicios/Reglas → Datos`; `API → IA`. Las reglas no dependen de la API ni de la IA, por lo que se prueban solas y se modifican rápido en la defensa.

## 4. Estructura de carpetas
```
hackaton _2/
├── documento/          # arquitectura y sprints
├── backend/
│   ├── src/
│   │   ├── api/        # rutas, middleware de errores      (Dev 2)
│   │   ├── ai/         # adaptador, prompts, validación    (Dev 2)
│   │   ├── rules/      # reglas de negocio puras           (Dev 1)
│   │   ├── services/   # reservas, equipos, incidencias    (Dev 1)
│   │   └── data/       # carga del dataset, persistencia   (Dev 1)
│   └── tests/          # pruebas de reglas                 (Dev 1)
├── frontend/           # pantallas y cliente de la API     (Dev 3)
├── .env.example        # variables sin valores reales      (Dev 3)
├── .gitignore          # incluye .env desde el primer commit
└── README.md           # (Dev 3)
```
Cada desarrollador edita solo sus carpetas para evitar conflictos de merge.

## 5. Modelo de datos
| Entidad | Campos |
|---|---|
| Sala | id, nombre, aforo, estado (activa / inhabilitada) |
| Reserva | id, salaId, inicio, fin, asistentes, responsable |
| Equipo | id, nombre, estado (disponible / prestado / dañado / inhabilitado) |
| Prestamo | id, equipoId, solicitante, fechaInicio, fechaDevolucion |
| Incidencia | id, texto, categoria, prioridad, ruta, estado, origenIA |

## 6. Reglas de negocio (mínimo 3)
| # | Regla | Rechazo |
|---|---|---|
| R1 | `asistentes <= aforo` de la sala | `AFORO_EXCEDIDO` |
| R2 | Sin solapamiento de horario en la misma sala | `SALA_OCUPADA` |
| R3 | No asignar sala o equipo inhabilitado, o equipo ya prestado | `RECURSO_NO_DISPONIBLE` |

Cada regla es una función pura en `backend/src/rules/` con casos válidos e inválidos en `tests/`.

## 7. Contrato de API (borrador)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/salas` | Lista salas con aforo y estado |
| POST | `/api/reservas` | Crea reserva (aplica R1, R2, R3) |
| GET | `/api/reservas` | Lista reservas |
| GET | `/api/equipos` | Lista equipos y estado |
| POST | `/api/prestamos` | Presta un equipo (R3) |
| POST | `/api/prestamos/:id/devolucion` | Registra devolución |
| POST | `/api/incidencias` | Crea incidencia y ejecuta triaje con IA |
| GET | `/api/incidencias` | Lista incidencias |
| POST | `/api/recomendaciones/sala` | (opcional) La IA sugiere sala según el grupo |

Formato de error: `{ "ok": false, "codigo": "AFORO_EXCEDIDO", "mensaje": "..." }`.
Formato de éxito: `{ "ok": true, "data": ... }`.

## 8. Rol de la IA
**Flujo principal: triaje de incidencias.**
1. El usuario escribe la incidencia en texto libre.
2. El módulo IA envía el texto al modelo autorizado con un prompt que exige salida estructurada (categoría, prioridad, ruta).
3. La salida se **valida** contra valores permitidos; si es inválida o hay timeout, la incidencia se guarda como "pendiente de revisión manual" (nunca se inventa una respuesta).
4. Se guarda el resultado y se marca `origenIA = true`.

**Flujo opcional:** recomendar la sala más ajustada al tamaño del grupo, respetando R1 a R3.

Principios: sin respuestas simuladas ni quemadas (penaliza 15 pts), adaptador intercambiable de proveedor y clave leída solo desde `.env`.

## 9. Seguridad
- `.env` en `.gitignore` desde el primer commit; solo `.env.example` con valores falsos.
- Sin API keys ni contraseñas en el historial de Git (penaliza 10 pts).
- Solo datos ficticios o autorizados.

## 10. Manejo de errores y estados
- Middleware global de errores: ninguna excepción sin controlar.
- Registros inconsistentes del dataset: se descartan o corrigen y se reportan, sin romper la carga.
- La UI muestra estados de carga, éxito y error en cada operación.

## 11. Cómo se defiende
- Explicar el flujo `UI → API → reglas → datos` y el rol de la IA.
- Cambio de regla en vivo (menos de 3 min): todas las reglas viven en `rules/`, y los umbrales y mensajes están centralizados.
