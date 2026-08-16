# 02 — Acceso a Claude vía API

Primer módulo práctico: petición básica, conversación multi-turno, system
prompts, control de la generación, streaming y datos estructurados.

## Lecciones y archivos

| Lección | Archivo |
|---|---|
| Acceder a la API / API key / Hacer una petición | [`01_primera_peticion.py`](01_primera_peticion.py) |
| Conversaciones multi-turno | [`02_conversacion_multiturno.py`](02_conversacion_multiturno.py) |
| **Ejercicio: chat** | [`03_ejercicio_chat.py`](03_ejercicio_chat.py) |
| System prompts | [`04_system_prompts.py`](04_system_prompts.py) |
| **Ejercicio: system prompts** | [`05_ejercicio_system_prompt.py`](05_ejercicio_system_prompt.py) |
| Temperature (y su sustituto actual, `effort`) | [`06_temperatura_y_effort.py`](06_temperatura_y_effort.py) |
| Streaming de respuestas | [`07_streaming.py`](07_streaming.py) |
| Datos estructurados | [`08_datos_estructurados.py`](08_datos_estructurados.py) |
| **Ejercicio: datos estructurados** | [`09_ejercicio_estructurados.py`](09_ejercicio_estructurados.py) |

Ejecutar siempre desde la raíz del repo:

```bash
python 02-acceso-api/01_primera_peticion.py
```

## Ideas clave

**La API no recuerda nada.** Para que Claude "recuerde" el turno anterior,
tienes que reenviar la lista completa de `messages`. El historial lo mantienes tú.

**Reglas de `messages`:**
- El primer mensaje debe ser `user`.
- Se permiten mensajes consecutivos del mismo rol (se combinan en un turno).
- El contenido puede ser una cadena o una lista de bloques.

**System prompt ≠ mensaje de usuario.** El system prompt va en el parámetro
`system`, se procesa antes de todo el historial y define rol, tono y reglas.
Ponerlo como primer mensaje de usuario funciona peor y rompe el caché.

**Datos estructurados: usa el schema, no el prefill.** El curso enseña el
prefill del turno `assistant` para forzar JSON; hoy devuelve 400. La ruta
correcta es `client.messages.parse()` con un modelo Pydantic, o
`output_config={"format": {"type": "json_schema", ...}}`.

**Streaming.** Obligatorio si `max_tokens` supera ~16.000 (el SDK aborta por
timeout HTTP). `stream.get_final_message()` te devuelve el mensaje completo
aunque hayas ido consumiendo los deltas.

## Notas propias

<!-- Tus apuntes del módulo. -->
