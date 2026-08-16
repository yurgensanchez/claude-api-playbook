# 03 — Evaluación de prompts (evals)

Cómo medir objetivamente si un prompt funciona, en vez de mirarlo y decidir "va
bien". Es el módulo que separa el prototipo del sistema en producción.

## Lecciones y archivos

| Lección | Archivo |
|---|---|
| Qué es la evaluación de prompts / flujo típico | este README |
| Generar datasets de prueba | [`01_generar_dataset.py`](01_generar_dataset.py) |
| Ejecutar la eval | [`02_ejecutar_eval.py`](02_ejecutar_eval.py) |
| Grading basado en modelo | [`03_grading_por_modelo.py`](03_grading_por_modelo.py) |
| Grading basado en código | [`04_grading_por_codigo.py`](04_grading_por_codigo.py) |
| **Ejercicio: prompt evals** | [`ejercicio.py`](ejercicio.py) |

## El flujo de una eval

```
1. Dataset      →  casos de prueba (input + criterio de éxito)
2. Ejecución    →  correr el prompt sobre cada caso
3. Grading      →  puntuar cada salida
4. Análisis     →  agregar resultados, comparar versiones del prompt
```

Sin el paso 3 no hay eval: hay una demo.

## Los dos tipos de grading

**Basado en código** — determinista, gratis, instantáneo. Sirve cuando el
criterio es verificable programáticamente: ¿el JSON valida?, ¿contiene el campo
`precio` y es numérico?, ¿la respuesta está por debajo de N caracteres?, ¿el
código compila?

**Basado en modelo (LLM-as-judge)** — un modelo puntúa la salida contra una
rúbrica. Sirve para lo cualitativo: tono, exhaustividad, si la respuesta se
apoya en el contexto dado.

Regla práctica: **usa código siempre que puedas y modelo solo cuando no puedas.**
El grading por código no alucina y no cuesta.

## Escribir buenas rúbricas

Una rúbrica vaga produce evals ruidosas. Compara:

- Mal: "la respuesta es buena y completa"
- Bien: "la respuesta incluye una columna `precio` numérica por cada SKU
  mencionado en el input, y no inventa SKUs que no aparecen"

Cada criterio se puntúa de forma independiente. Si no puedes describir cómo
verificar un criterio, ese criterio no está listo.

## Detalles de implementación

- **Ejecuta en paralelo.** Una eval de 100 casos en serie tarda una eternidad.
  Usa `shared.client.get_async_client()` con `asyncio.gather` y un semáforo para
  no reventar el rate limit.
- **Usa un modelo barato para el dataset y las corridas masivas**
  (`CLAUDE_MODEL_FAST`), y el bueno para el juez si el criterio es sutil.
- **Guarda los resultados con la versión del prompt.** Sin eso no puedes
  comparar iteraciones.
- **La Batches API** procesa hasta 100.000 peticiones asíncronas al 50 % del
  precio: ideal para evals grandes que no son sensibles a latencia.

## Notas propias

<!-- Tus apuntes del módulo. -->
