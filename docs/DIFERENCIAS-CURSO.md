# Diferencias entre el curso grabado y la API actual

El curso se grabó con una generación anterior de modelos. Estas son las
diferencias que te vas a encontrar al escribir el código, con la versión que se
usa en este repositorio.

## 1. Parámetros de sampling: `temperature`, `top_p`, `top_k`

**En el curso:** `temperature=0` para determinismo, `temperature=1` para creatividad.

**Hoy:** eliminados en Opus 5, Opus 4.8/4.7 y Fable 5 — enviarlos devuelve **400**.
En Sonnet 5 solo se acepta el valor por defecto.

**Sustituto:** `output_config={"effort": "low" | "medium" | "high" | "xhigh" | "max"}`
más instrucciones explícitas en el prompt. Si necesitas variedad creativa, pide
al modelo que proponga varias direcciones distintas en vez de subir temperature.

El módulo 02 incluye la lección con `CLAUDE_MODEL_LEGACY` (un modelo que aún
acepta `temperature`) para que veas el comportamiento original, y al lado la
versión moderna con `effort`.

## 2. Extended thinking

**En el curso:** `thinking={"type": "enabled", "budget_tokens": 8000}`.

**Hoy:** `budget_tokens` devuelve 400 en Opus 5/4.8/4.7 y Sonnet 5. Se usa
`thinking={"type": "adaptive"}` y el modelo decide cuánto razonar; la
profundidad se controla con `effort`.

Además, en Opus 5 el thinking está **activo por defecto** aunque no pases el
parámetro, y el texto del razonamiento viene vacío salvo que pidas
`display="summarized"`.

## 3. Prefill del turno `assistant`

**En el curso:** terminar `messages` con `{"role": "assistant", "content": "{"}`
para forzar JSON.

**Hoy:** devuelve 400 en los modelos actuales.

**Sustituto:** *structured outputs* —
`output_config={"format": {"type": "json_schema", "schema": {...}}}`,
o `client.messages.parse()` con un modelo Pydantic. Es más fiable que el prefill
y elimina el parseo defensivo. Se cubre en el módulo 02.

## 4. `output_format` → `output_config.format`

El parámetro top-level `output_format` está deprecado en toda la API.

## 5. Versiones de herramientas

| En el curso | Hoy |
|---|---|
| `text_editor_20250124` + `str_replace_editor` | `text_editor_20250728` + `str_replace_based_edit_tool` |
| `web_search_20250305` | `web_search_20260209` (con filtrado dinámico) |
| `code_execution_*` antiguo | `code_execution_20260521` |

Los nombres `type` y `name` van emparejados: cambiar solo uno devuelve 400.

## 6. Cabeceras beta que ya son GA

Se pueden quitar y volver a `client.messages.create` (sin `.beta`):

- `effort-2025-11-24`
- `fine-grained-tool-streaming-2025-05-14`
- `interleaved-thinking-2025-05-14` (el thinking adaptativo lo activa solo)
- `token-efficient-tools-2025-02-19`
- `output-128k-2025-02-19`

## 7. Streaming obligatorio con `max_tokens` alto

Por encima de ~16.000 tokens de salida, una petición sin streaming se puede
quedar colgada por timeout HTTP del SDK. Usa `client.messages.stream(...)` y
`stream.get_final_message()`.

## 8. Modelos mencionados en el curso

| En los vídeos | Equivalente actual |
|---|---|
| `claude-3-5-sonnet-*` | `claude-sonnet-5` |
| `claude-3-opus-*` | `claude-opus-5` |
| `claude-3-5-haiku-*` | `claude-haiku-4-5` |

Los dos primeros están **retirados** y devuelven 404.
