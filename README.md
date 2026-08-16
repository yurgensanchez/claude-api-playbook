# Claude API Playbook

Guía práctica de construcción con la API de Claude: tool use, evaluación de
prompts, RAG, MCP, prompt caching y arquitecturas de agente.

Cada patrón es un archivo ejecutable y aislado, con las trampas anotadas.
El código está actualizado a la API actual, no a la de hace dos años.

---

## Busca por lo que necesitas hacer

| Necesito... | Dónde |
|---|---|
| Que el modelo llame a mis funciones | [`05-tool-use/`](05-tool-use/) |
| Saber si mi prompt funciona, con números | [`03-evaluacion-prompts/`](03-evaluacion-prompts/) |
| Buscar sobre documentos propios | [`06-rag-busqueda-agentica/`](06-rag-busqueda-agentica/) |
| Bajar el coste de un prompt grande | [`07-features-claude/05_prompt_caching.py`](07-features-claude/05_prompt_caching.py) |
| JSON garantizado en la respuesta | [`02-acceso-api/08_datos_estructurados.py`](02-acceso-api/08_datos_estructurados.py) |
| Exponer capacidades a Claude Code u otro cliente | [`08-mcp/`](08-mcp/) |
| Decidir entre workflow y agente | [`10-agentes-workflows/`](10-agentes-workflows/) |
| Respuestas con citas verificables | [`07-features-claude/04_citations.py`](07-features-claude/04_citations.py) |
| Analizar imágenes o PDF | [`07-features-claude/`](07-features-claude/) |
| Que el modelo ejecute código | [`07-features-claude/06_code_execution.py`](07-features-claude/06_code_execution.py) |
| Escribir mejores prompts | [`04-ingenieria-prompts/`](04-ingenieria-prompts/) |
| Streaming de respuestas | [`02-acceso-api/07_streaming.py`](02-acceso-api/07_streaming.py) |

---

## Estado

| Módulo | Contenido | Estado |
|---|---|---|
| [01 — Introducción](01-introduccion/) | Modelos y conceptos base | Notas |
| [02 — Acceso a la API](02-acceso-api/) | Peticiones, multi-turno, system prompts, streaming, structured outputs | Ejecutable |
| [03 — Evaluación de prompts](03-evaluacion-prompts/) | Dataset, ejecución paralela, grading por modelo y por código | Ejecutable |
| [04 — Ingeniería de prompts](04-ingenieria-prompts/) | Claridad, especificidad, XML, few-shot | Ejecutable |
| [05 — Tool use](05-tool-use/) | Bucle agéntico, tools de servidor y de cliente, fine-grained | Ejecutable · proyecto pendiente |
| [06 — RAG y búsqueda agéntica](06-rag-busqueda-agentica/) | Chunking, embeddings, BM25, fusión RRF | Parcial — pipeline completo pendiente |
| [07 — Features de Claude](07-features-claude/) | Thinking, visión, PDF, citations, caching, code execution | Ejecutable |
| [08 — MCP](08-mcp/) | Servidor con tools, recursos y prompts + cliente | Ejecutable |
| [09 — Claude Code y Computer Use](09-apps-anthropic/) | Configuración y notas | Notas |
| [10 — Agentes y workflows](10-agentes-workflows/) | Paralelización, encadenamiento, enrutamiento, agentes | Ejecutable |
| [11 — Proyecto final](11-proyecto-final/) | Asistente documental con evals | Pendiente |

Los archivos `ejercicio*.py` están deliberadamente sin resolver: son el trabajo
del curso, no la referencia.

---

## Puesta en marcha

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt

copy .env.example .env        # y añade tu ANTHROPIC_API_KEY

python -m shared.check        # verifica clave, modelo y dependencias
```

Todo se ejecuta desde la raíz del repo:

```bash
python 02-acceso-api/01_primera_peticion.py
```

Guía detallada en [`docs/SETUP.md`](docs/SETUP.md).

---

## Lo que cambió respecto al material del curso

Este repositorio nace del curso [Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api)
de Anthropic Academy, grabado con una generación anterior de modelos. Varias
técnicas que enseña **hoy devuelven 400**:

| El curso enseña | Estado actual | Sustituto |
|---|---|---|
| `temperature` / `top_p` | Eliminados en Opus 5 y Opus 4.8/4.7 | `output_config.effort` + prompting |
| `thinking: {budget_tokens: N}` | Eliminado | `thinking: {"type": "adaptive"}` |
| Prefill del turno `assistant` para forzar JSON | Eliminado | `output_config.format` / `messages.parse()` |
| `text_editor_20250124` | Versión retirada | `text_editor_20250728` |
| Cabeceras beta `effort-*`, `interleaved-thinking-*` | Ya son GA | Quitarlas y volver a `client.messages` |

En vez de copiar el código obsoleto, las lecciones afectadas muestran **las dos
rutas**: la del curso (provocando el 400 a propósito, para que se vea) y la
actual. Detalle completo en [`docs/DIFERENCIAS-CURSO.md`](docs/DIFERENCIAS-CURSO.md).

---

## Modelos

Configurables desde `.env`:

| Variable | Por defecto | Uso |
|---|---|---|
| `CLAUDE_MODEL` | `claude-opus-5` | Ejercicios y razonamiento |
| `CLAUDE_MODEL_FAST` | `claude-haiku-4-5` | Evals masivas, clasificación, routing |
| `CLAUDE_MODEL_LEGACY` | `claude-haiku-4-5` | Lecciones que demuestran parámetros retirados |

---

## Estructura

```
shared/          cliente configurado, helpers, comprobación de entorno
docs/            setup, progreso del curso, diferencias con la API actual
NN-modulo/       README con conceptos + un archivo por patrón
```

`shared/` centraliza el boilerplate para que cada archivo se enfoque en el
concepto que enseña:

- `client.py` — cliente cacheado y modelos desde `.env`
- `utils.py` — `extract_text()`, `print_usage()`, `count_tokens()`
- `check.py` — `python -m shared.check`

---

## Créditos

Código propio escrito mientras seguía el curso. El temario y los materiales
originales pertenecen a Anthropic.
