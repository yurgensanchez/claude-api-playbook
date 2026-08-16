# 05 — Tool use

El módulo más largo del curso y el primero que construye un proyecto completo:
un asistente que consulta una base de datos de productos mediante herramientas.

## Lecciones y archivos

| Lección | Archivo |
|---|---|
| Introducción a tool use / visión general del proyecto | este README |
| Funciones de las herramientas | [`tools/implementaciones.py`](tools/implementaciones.py) |
| Esquemas de herramientas | [`tools/definiciones.py`](tools/definiciones.py) |
| Manejo de bloques de mensaje | [`01_bloques_mensaje.py`](01_bloques_mensaje.py) |
| Enviar resultados de herramientas | [`02_enviar_resultados.py`](02_enviar_resultados.py) |
| Conversaciones multi-turno con tools | [`03_bucle_agentico.py`](03_bucle_agentico.py) |
| Usar múltiples herramientas | [`04_multiples_tools.py`](04_multiples_tools.py) |
| Fine-grained tool calling | [`05_fine_grained.py`](05_fine_grained.py) |
| La herramienta text edit | [`06_text_editor_tool.py`](06_text_editor_tool.py) |
| La herramienta web search | [`07_web_search_tool.py`](07_web_search_tool.py) |
| **Proyecto integrado** | [`proyecto/`](proyecto/) |

## Estructura

```
05-tool-use/
├── tools/
│   ├── definiciones.py      esquemas JSON de las herramientas
│   ├── implementaciones.py  las funciones Python que se ejecutan
│   └── datos.py             base de datos falsa en memoria
├── 01_..07_*.py             una lección por archivo
└── proyecto/                el asistente completo del curso
```

## Cómo funciona el ciclo

```
1. Envías messages + tools
2. Claude responde con stop_reason="tool_use" y uno o más bloques tool_use
3. TÚ ejecutas la función correspondiente
4. Devuelves los resultados como bloques tool_result en un mensaje "user"
5. Repites hasta stop_reason="end_turn"
```

Puntos donde todo el mundo se equivoca la primera vez:

- **Hay que añadir `response.content` completo** al historial como mensaje
  `assistant`, no solo el texto. Si pierdes los bloques `tool_use`, la API
  rechaza el `tool_result` siguiente.
- **Cada `tool_use` necesita su `tool_result`** con el `tool_use_id` que
  coincida. Si falta uno, la petición falla.
- **Las llamadas en paralelo van en un solo mensaje.** Si Claude pide tres
  herramientas a la vez, los tres `tool_result` van en el mismo mensaje `user`.
  Separarlos en tres mensajes le enseña a dejar de paralelizar.
- **Un error de herramienta también se devuelve**, con `is_error: True` y un
  mensaje útil. No lo silencies: Claude puede recuperarse.

## Dos formas de escribir el bucle

**Tool runner (recomendado, beta).** El SDK ejecuta el bucle por ti:
decoras las funciones con `@beta_tool` y llamas a
`client.beta.messages.tool_runner(...)`. Sigue permitiendo interceptar,
aprobar o modificar en cada turno.

**Bucle manual.** Lo escribes tú. Es lo que enseña el curso, y merece la pena
hacerlo al menos una vez para entender qué automatiza el runner.

Los archivos `01` a `04` usan el bucle manual (didáctico). El proyecto final
muestra las dos versiones.

## Herramientas definidas por Anthropic

No llevan `input_schema`: se declaran solo con `type` y `name`, y el esquema
está en el modelo.

| Herramienta | Declaración | Quién la ejecuta |
|---|---|---|
| Bash | `{"type": "bash_20250124", "name": "bash"}` | Tú (cliente) |
| Text editor | `{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}` | Tú (cliente) |
| Web search | `{"type": "web_search_20260209", "name": "web_search"}` | Anthropic (servidor) |
| Code execution | `{"type": "code_execution_20260521", "name": "code_execution"}` | Anthropic (servidor) |

`type` y `name` van emparejados. Cambiar solo uno devuelve 400.

## Seguridad

El `path` y el `command` que llegan en un `tool_use` son **salida del modelo, no
entrada de confianza**. Antes de ejecutar:

- Resuelve la ruta a su forma canónica y verifica que sigue dentro del
  directorio permitido (rechaza `..`, symlinks, rutas absolutas fuera).
- Para bash, usa una lista blanca de ejecutables y rechaza operadores de shell.
- Cualquier acción destructiva o difícil de revertir debería pasar por
  confirmación humana.

## Notas propias

<!-- Tus apuntes del módulo. -->
