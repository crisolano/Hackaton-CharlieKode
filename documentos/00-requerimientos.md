# Requerimientos y expectativas del producto

Hackatón Campuslands: "El campus bajo presión". Fuente: Guía Oficial de Competencia y Términos Técnicos del Desafío.

## 1. Contexto y objetivo
Campuslands crece rápido y sus procesos dependen de registros dispersos y revisiones manuales, lo que genera demoras, errores y fricción en la comunidad. Los problemas diarios son la disponibilidad de aulas, el préstamo de equipos, la gestión de incidentes y el bienestar estudiantil.

**Objetivo del desafío:** en **5 horas**, un equipo de **4 a 5 personas** (nosotros, 3 desarrolladores) construye el **Sistema Central de Gestión Operativa del Campus** como un **MVP funcional**, que fortalezca:
- el pensamiento computacional y el diseño de soluciones,
- la programación,
- la integración estratégica de IA,
- el trabajo en equipo.

## 2. Qué se espera del producto
Un sistema que unifique en **un único flujo operativo asistido por IA**:

| Módulo | Qué debe lograr |
|---|---|
| **1. Espacios** | Disponibilidad y asignación de aulas y cubículos, sin solapamientos ni conflictos de aforo |
| **2. Recursos tecnológicos** | Préstamo y control de equipos, con trazabilidad de estado y disponibilidad |
| **3. Incidencias y solicitudes** | Triaje inteligente: clasificación, priorización y enrutamiento automático con IA |

**Regla central:** el sistema opera de forma integrada, evita asignar espacios o recursos inhabilitados o con conflicto, y usa IA para optimizar decisiones, categorizar incidencias o recomendar asignaciones.

**Qué es un MVP aquí:** software ejecutable de extremo a extremo en su flujo principal. No bastan diseños ni prototipos estáticos. No hay framework obligatorio ni una única respuesta correcta.

## 3. Requerimientos funcionales (obligatorios)
| ID | Requerimiento |
|---|---|
| RF1 | Interfaz interactiva con al menos **un flujo vertical completo** que integre IA (análisis, recomendación, clasificación o asistencia contextual) |
| RF2 | Consultar los **datos oficiales** entregados por Campuslands y usarlos directamente en las operaciones |
| RF3 | Registrar, actualizar o modificar información de espacios, recursos e incidencias |
| RF4 | Implementar **al menos 3 validaciones de reglas de negocio** (lógica de dominio, no solo campos vacíos o tipos de dato) |
| RF5 | Mostrar confirmaciones y mensajes de error claros, y manejar excepciones sin fallos no controlados, incluidos registros inconsistentes en los datos de origen |
| RF6 | Mantener coherencia e integridad entre los datos originales y las operaciones realizadas |
| RF7 | Poder explicar el funcionamiento técnico: arquitectura y rol de la IA |

### Reglas de negocio definidas por el equipo
| # | Regla | Código de rechazo |
|---|---|---|
| R1 | `asistentes <= aforo` de la sala | `AFORO_EXCEDIDO` |
| R2 | Sin solapamiento de horario en la misma sala | `SALA_OCUPADA` |
| R3 | No asignar sala o equipo inhabilitado, ni equipo ya prestado | `RECURSO_NO_DISPONIBLE` |

### Salas y aforo
Auditorio 100 · Cosmos 25 · Skilab 20 · Spooki 38 · Apolo 34 · Blanca 12 · Azul 10 · Amarillas verdes 6 · Artemis 32.
El dataset oficial es la fuente de verdad y se contrasta con estos valores al cargarlo.

## 4. Requerimientos de calidad
- Código legible, modular y organizado.
- **Sin credenciales reales** (API keys, contraseñas) expuestas en el repositorio.
- Instalación y ejecución **reproducibles** en el entorno de evaluación.
- Uso exclusivo de datos ficticios o autorizados; no recopilar información personal real.
- Interfaz comprensible, con indicación clara de estados de carga, éxito y mensajes de validación.
- Capaz de ejecutarse con las **APIs o modelos locales autorizados** para la jornada.

## 5. Entregables
| Elemento | Requisito |
|---|---|
| Repositorio Git | Creado al inicio por el equipo; con el historial de commits del código hecho en las 5 horas |
| MVP | Funcional y ejecutable de extremo a extremo en su flujo principal |
| README | Problema, integrantes, stack, uso de IA, reglas de negocio implementadas y pasos de instalación y ejecución |
| Datos | Evidencia funcional de carga, lectura, validación y persistencia sobre la información oficial |
| Demostración | Ejecución en vivo del flujo principal y comprobación de las 3 reglas con casos válidos e inválidos |
| Defensa | Explicación de la arquitectura y **modificación en vivo de una regla** pedida por el jurado |

## 6. Criterios de evaluación (100 puntos)
| Bloque | Criterio | Pts | Enfoque |
|---|---|---|---|
| A. Técnico | Reglas de negocio y manejo de datos | 25 | Integridad del dataset, 3 validaciones de dominio y persistencia |
| A. Técnico | Integración estratégica de IA | 20 | Pertinencia de la IA en el flujo, control de respuestas y valor real |
| A. Técnico | Funcionalidad del MVP y UX/UI | 15 | Flujo completo ejecutable, manejo de estados y control de errores |
| A. Técnico | Calidad de código y repositorio | 10 | Modularidad, seguridad (`.env`), historial de Git y README |
| B. Sustentación | Reto de modificación en vivo | 15 | Alterar una regla o condición ante el jurado en **menos de 3 minutos** |
| B. Sustentación | Defensa arquitectónica y pitch | 15 | Claridad al explicar el flujo, justificación técnica y participación grupal |

### Penalizaciones directas
- **−10 puntos:** exponer credenciales, es decir subir API keys reales o contraseñas en texto plano al historial de Git.
- **−15 puntos:** datos quemados o *hardcoding*, es decir simular la respuesta de la IA o las validaciones con respuestas estáticas para aparentar que el flujo funciona.

## 7. Qué significa esto para el equipo
- **Prioridad de esfuerzo:** reglas y datos (25) → IA (20) → MVP y UX (15). La sustentación suma otros 30 puntos, así que todos deben entender y poder cambiar el código.
- **Las reglas viven en un solo lugar** (`app/rules/`) para poder modificarlas en vivo en menos de 3 minutos.
- **La IA debe ser real:** llamada a un proveedor, salida validada, fallo controlado (revisión manual) y nunca respuestas fijas.
- **El `.env` nunca entra a Git:** solo `.env.example` con valores falsos.
- **Los datos oficiales llegan al inicio del evento:** el diseño debe tolerar registros inconsistentes y casos borde.

## 8. Fuera de alcance
Dashboards avanzados, autenticación completa y notificaciones no suman puntos; solo se hacen si sobra tiempo.

## 9. Documentos relacionados
- [01-arquitectura.md](01-arquitectura.md): stack, capas, modelo de datos y API.
- [02-sprints.md](02-sprints.md): plan de sprints y tareas por desarrollador.
- [03-gitflow.md](03-gitflow.md): flujo de ramas y commits.
- [04-guia-desarrollo.md](04-guia-desarrollo.md): guía de desarrollo y regla de nada hardcodeado.
