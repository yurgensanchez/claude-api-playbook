# Proyecto del módulo 05 — Asistente de catálogo

Integra todo lo del módulo en un asistente conversacional que usa las tres
herramientas de `tools/` sobre el catálogo falso.

## Objetivo

Un chat de terminal donde el usuario puede:

- buscar productos por texto, categoría o precio
- consultar el estado de un pedido
- pedir el total de un carrito con IVA y descuentos

y donde el asistente encadena herramientas por su cuenta cuando hace falta.

## Requisitos

1. **`asistente.py`** — bucle agéntico manual (el patrón de `03_bucle_agentico.py`),
   con historial persistente entre turnos del usuario.
2. **`asistente_runner.py`** — la misma funcionalidad usando el tool runner del
   SDK (`@beta_tool` + `client.beta.messages.tool_runner`).
3. Un system prompt que fije rol, tono y cuándo NO usar herramientas.
4. Traza visible de qué herramienta se llamó y con qué argumentos.
5. Manejo correcto de: `end_turn`, `tool_use`, `pause_turn`, `refusal`,
   `max_tokens`.
6. Tope de iteraciones.

## Extras

- Confirmación humana antes de cualquier herramienta que modifique estado.
- Prompt caching sobre el system prompt y las definiciones de herramientas
  (módulo 07) — el bloque `tools` va al principio del prefijo, así que cachear
  ahí es lo que más ahorra.
- Contador de coste acumulado por sesión.

## Comparativa que hay que escribir al terminar

| | Bucle manual | Tool runner |
|---|---|---|
| Líneas de código | | |
| Control sobre cada turno | | |
| Manejo de `pause_turn` | | |
| Dependencia de beta | | |
| Cuándo lo elegirías | | |

Lo importante del módulo no es que el asistente funcione, sino entender qué
automatiza exactamente el runner y en qué casos sigue haciendo falta el bucle
manual.
