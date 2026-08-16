# Building with the Claude API — Curso de Anthropic

Repositorio de trabajo del curso oficial [**Building with the Claude API**](https://anthropic.skilljar.com/claude-with-the-anthropic-api) (Anthropic Academy).

Cada módulo del curso vive en su propia carpeta, con su README, sus ejercicios y sus proyectos independientes. La idea es que cada carpeta se pueda ejecutar y entender por separado.

---

## Índice de módulos

| # | Módulo | Carpeta | Tipo |
|---|--------|---------|------|
| 01 | Introducción | [`01-introduccion/`](01-introduccion/) | Teoría |
| 02 | Acceso a Claude vía API | [`02-acceso-api/`](02-acceso-api/) | Ejercicios |
| 03 | Evaluación de prompts (evals) | [`03-evaluacion-prompts/`](03-evaluacion-prompts/) | Proyecto |
| 04 | Ingeniería de prompts | [`04-ingenieria-prompts/`](04-ingenieria-prompts/) | Ejercicios |
| 05 | Tool use | [`05-tool-use/`](05-tool-use/) | Proyecto |
| 06 | RAG y búsqueda agéntica | [`06-rag-busqueda-agentica/`](06-rag-busqueda-agentica/) | Proyecto |
| 07 | Features de Claude | [`07-features-claude/`](07-features-claude/) | Ejercicios |
| 08 | Model Context Protocol (MCP) | [`08-mcp/`](08-mcp/) | Proyecto |
| 09 | Apps de Anthropic (Claude Code, Computer Use) | [`09-apps-anthropic/`](09-apps-anthropic/) | Teoría |
| 10 | Agentes y workflows | [`10-agentes-workflows/`](10-agentes-workflows/) | Proyecto |
| 11 | Proyecto final y evaluación | [`11-proyecto-final/`](11-proyecto-final/) | Proyecto |

Seguimiento del avance: [`docs/PROGRESO.md`](docs/PROGRESO.md)

---

## Puesta en marcha

```bash
# 1. Entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Dependencias
pip install -r requirements.txt

# 3. Credenciales
copy .env.example .env        # Windows  (cp en macOS/Linux)
# editar .env y pegar la ANTHROPIC_API_KEY

# 4. Verificar que todo funciona
python -m shared.check
```

Guía detallada en [`docs/SETUP.md`](docs/SETUP.md).

---

## Cómo está organizado cada módulo

```
NN-nombre-modulo/
├── README.md          Objetivos, checklist de lecciones y notas propias
├── 01_*.py            Un archivo por lección/concepto, ejecutable de forma aislada
├── ejercicio*.py      El ejercicio que plantea el curso
└── data/ | assets/    Recursos que necesita ese módulo
```

Todos los scripts se ejecutan desde la **raíz del repo** para que el paquete `shared/` resuelva:

```bash
python 02-acceso-api/01_primera_peticion.py
```

## Código compartido

`shared/` centraliza lo que se repite en todos los módulos, para que cada ejercicio se enfoque en el concepto que enseña y no en el boilerplate:

- `shared/client.py` — cliente de Anthropic ya configurado + modelo por defecto
- `shared/utils.py` — helpers de impresión, extracción de texto y conteo de tokens/coste
- `shared/check.py` — comprobación de entorno (`python -m shared.check`)

---

## Sobre los modelos

El curso original fue grabado con modelos anteriores. Este repositorio usa los modelos actuales, configurables desde `.env`:

| Variable | Por defecto | Uso |
|---|---|---|
| `CLAUDE_MODEL` | `claude-opus-5` | Modelo principal de los ejercicios |
| `CLAUDE_MODEL_FAST` | `claude-haiku-4-5` | Tareas simples, evals masivas, ahorro de coste |

Diferencias relevantes frente a lo que se ve en los vídeos del curso:

- `temperature` / `top_p` / `top_k` **ya no se aceptan** en Opus 5 y Sonnet 5. El control equivalente hoy es `output_config={"effort": ...}` y el prompting. El módulo 02 lo explica y demuestra ambas rutas.
- El *extended thinking* con `budget_tokens` está sustituido por `thinking={"type": "adaptive"}`.
- El prefill del turno `assistant` devuelve 400 en los modelos actuales; se sustituye por *structured outputs* (`output_config.format`).

Notas ampliadas en [`docs/DIFERENCIAS-CURSO.md`](docs/DIFERENCIAS-CURSO.md).

---

## Licencia y créditos

Código propio con fines de aprendizaje. El temario y los materiales originales pertenecen a Anthropic.
