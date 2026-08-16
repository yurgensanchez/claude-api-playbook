# 10 — Agentes y workflows

El módulo que da la perspectiva de arquitectura: cuándo hace falta un agente y
cuándo un workflow con la lógica en tu código.

## Lecciones y archivos

| Lección | Archivo |
|---|---|
| Agentes y workflows | este README |
| Workflows de paralelización | [`01_paralelizacion.py`](01_paralelizacion.py) |
| Workflows de encadenamiento | [`02_encadenamiento.py`](02_encadenamiento.py) |
| Workflows de enrutamiento | [`03_enrutamiento.py`](03_enrutamiento.py) |
| Agentes y herramientas | [`04_agente.py`](04_agente.py) |
| Inspección del entorno | [`05_inspeccion_entorno.py`](05_inspeccion_entorno.py) |
| Workflows vs. agentes | este README |

## La distinción

**Workflow**: tú controlas el flujo. El código decide qué llamada va después.
Predecible, depurable, barato.

**Agente**: el modelo controla el flujo. Decide qué herramientas usar y en qué
orden hasta terminar. Flexible, impredecible, más caro.

## Antes de construir un agente, comprueba las cuatro condiciones

1. **Complejidad** — ¿la tarea es multi-paso y difícil de especificar por
   adelantado? ("convierte este documento de diseño en un PR", no "extrae el
   título de este PDF")
2. **Valor** — ¿el resultado justifica más coste y más latencia?
3. **Viabilidad** — ¿Claude es realmente capaz en este tipo de tarea?
4. **Coste del error** — ¿los fallos se detectan y se pueden revertir? (tests,
   revisión, rollback)

Si alguna respuesta es "no", quédate en el nivel más simple.

## La escalera, de simple a complejo

| Caso | Nivel | Qué usar |
|---|---|---|
| Clasificar, resumir, extraer, responder | Una llamada | Claude API |
| Lote grande sin urgencia | Una llamada | Batches API (50 % más barata) |
| Pipeline multi-paso con lógica tuya | Workflow | API + tools, el bucle lo escribes tú |
| Agente con tus herramientas | Agente | API + tools (tool runner) |
| Agente con estado y sandbox gestionado | Agente | Managed Agents |

**Empieza siempre por el nivel más simple que resuelva el problema.** El error
caro es montar un agente para algo que un workflow de tres pasos resolvía.

## Los tres patrones de workflow

**Paralelización** — N tareas independientes a la vez. Ganancia: latencia.
Ej.: revisar el mismo texto desde cinco ángulos distintos.

**Encadenamiento** — la salida de un paso alimenta el siguiente. Ganancia:
cada paso hace una sola cosa y se puede evaluar por separado.
Ej.: extraer → validar → formatear.

**Enrutamiento** — un clasificador barato decide qué ruta especializada seguir.
Ganancia: coste (Haiku clasifica, Opus solo entra donde hace falta).

Se combinan: un router que lanza una cadena, con un paso paralelizado dentro.

## Un LLM no es un ejecutor de planes deterministas

Revisa cada llamada al modelo de tu pipeline y pregúntate: **¿los inputs
determinan por completo el output?** Si la respuesta es sí, eso es código.
Enrutar, contar, normalizar, filtrar y formatear van en Python. Deja para el
modelo el paso donde de verdad hay juicio.

## Notas propias

<!-- Tus apuntes del módulo. -->
