# 07 — Features de Claude

Las capacidades que no son ni prompting ni tools: razonamiento extendido,
multimodalidad, citas, caché y ejecución de código.

## Lecciones y archivos

| Lección | Archivo |
|---|---|
| Extended thinking | [`01_extended_thinking.py`](01_extended_thinking.py) |
| Soporte de imágenes | [`02_imagenes.py`](02_imagenes.py) |
| Soporte de PDF | [`03_pdf.py`](03_pdf.py) |
| Citations | [`04_citations.py`](04_citations.py) |
| Prompt caching / reglas / en acción | [`05_prompt_caching.py`](05_prompt_caching.py) |
| Code execution y Files API | [`06_code_execution.py`](06_code_execution.py) |

## Resumen por feature

**Extended thinking.** El curso enseña `budget_tokens`; hoy se usa
`thinking={"type": "adaptive"}` y la profundidad se regula con `effort`. En
Opus 5 el thinking está **activo por defecto**, y el texto del razonamiento
llega vacío salvo que pidas `display="summarized"`.

**Imágenes.** Base64 o URL, en un bloque `image` dentro del contenido del
mensaje. Resolución máxima 2576 px en el lado largo. Más resolución cuesta más
tokens (hasta ~4784 por imagen).

**PDF.** Bloque `document` con `media_type: "application/pdf"`. Límites: 32 MB
por petición, 600 páginas. Para varias consultas sobre el mismo PDF, súbelo con
la Files API y referencia el `file_id` en vez de reenviar el base64.

**Citations.** `citations: {"enabled": true}` en cada bloque `document`. La
respuesta se parte en varios bloques `text` y los citados llevan un array
`citations` con `cited_text` y la localización exacta. Es la forma correcta de
hacer RAG verificable. Incompatible con `output_config.format`.

**Prompt caching.** La feature con más impacto en coste (lecturas a ~0,1× del
precio de entrada). Es un **match de prefijo**: cualquier byte que cambie
invalida todo lo que viene después.

**Code execution.** Herramienta de servidor: Claude escribe y ejecuta Python en
un contenedor aislado, sin internet, con pandas/matplotlib/etc. preinstalados.
Los archivos generados se descargan por la Files API.

## Las reglas del prompt caching (las que hay que memorizar)

1. El orden de render es `tools` → `system` → `messages`. Un breakpoint en el
   último bloque de `system` cachea tools + system juntos.
2. Máximo **4 breakpoints** por petición.
3. Prefijo mínimo cacheable: **512 tokens** en Opus 5, 1024 en Opus 4.8 y
   Sonnet 5. Por debajo, no cachea y no avisa.
4. Lo **estable va primero**, lo volátil al final. Un `datetime.now()` en el
   system prompt invalida absolutamente todo.
5. Verifica siempre con `usage.cache_read_input_tokens`. Si sale 0 en peticiones
   repetidas, hay un invalidador silencioso.
6. Escribir en caché cuesta 1,25× (TTL 5 min) o 2× (TTL 1 h). Con TTL de 5 min
   el punto de equilibrio son 2 peticiones; con 1 h, 3.

Invalidadores silenciosos típicos: `datetime.now()`, UUIDs, `json.dumps()` sin
`sort_keys=True`, iterar un `set`, herramientas que cambian por usuario.

## Notas propias

<!-- Tus apuntes del módulo. -->
