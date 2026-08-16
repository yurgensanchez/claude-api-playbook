# 04 — Ingeniería de prompts

Las cuatro técnicas centrales del curso, aplicadas sobre el mismo caso para que
la diferencia se vea.

## Lecciones y archivos

| Lección | Archivo |
|---|---|
| Introducción al prompt engineering | este README |
| Ser claro y directo | [`01_claro_y_directo.py`](01_claro_y_directo.py) |
| Ser específico | [`02_ser_especifico.py`](02_ser_especifico.py) |
| Estructurar con etiquetas XML | [`03_xml_tags.py`](03_xml_tags.py) |
| Dar ejemplos (few-shot) | [`04_ejemplos_fewshot.py`](04_ejemplos_fewshot.py) |
| **Ejercicio: prompting** | [`ejercicio.py`](ejercicio.py) |

## Las cuatro técnicas

**1. Claro y directo.** Di exactamente lo que quieres. La ambigüedad es la
primera causa de salidas malas: si un colega humano tendría que preguntarte a
qué te refieres, el modelo también.

**2. Específico.** Formato de salida, longitud, audiencia, qué excluir. "Resume
esto" y "resume esto en 3 bullets para un director financiero, sin jerga
técnica" producen cosas distintas.

**3. Etiquetas XML.** Separan instrucción de datos. Evitan que el contenido del
usuario se lea como instrucción, y te dan un punto de anclaje para referirte a
cada parte (`<documento>`, `<ejemplo>`, `<criterios>`).

**4. Ejemplos (few-shot).** La señal más fuerte de un prompt. El modelo imita
longitud, tono y estructura de los ejemplos, no solo su contenido — así que un
ejemplo mal elegido congela un comportamiento que no querías.

## Advertencia sobre el curso

El curso enseña algunos patrones que hoy son contraproducentes con los modelos
actuales, porque estos siguen las instrucciones mucho más de cerca:

| Patrón del curso | Hoy |
|---|---|
| `CRITICAL: DEBES usar esta herramienta cuando...` | `Usa esta herramienta cuando...` — el énfasis inflado provoca sobre-disparo |
| Listas largas de prohibiciones | Describe el éxito; una prohibición contra un fallo que el modelo no iba a cometer puede inducirlo |
| "Piensa paso a paso" / `<scratchpad>` | Redundante: usa `thinking={"type": "adaptive"}` y `effort` |
| Un único ejemplo "de oro" | Varios ejemplos variados, o el modelo copiará ese formato exacto siempre |

Lo que **sí** hay que dar y el modelo no puede saber: audiencia, producto,
entorno, listón de calidad, restricciones reales y **el porqué** de cada una.

## Notas propias

<!-- Tus apuntes del módulo. -->
