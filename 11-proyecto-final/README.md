# 11 — Proyecto final y evaluación

## Lecciones

- [ ] Evaluación final del curso
- [ ] Cierre del curso
- [ ] Certificado descargado

## Repaso rápido antes de la evaluación final

Preguntas de autoevaluación. Si alguna no la respondes de carrerilla, vuelve al
módulo correspondiente.

**Módulo 02**
- ¿Por qué hay que reenviar todo el historial en cada petición?
- ¿Por qué `response.content[0].text` es frágil?
- ¿Qué sustituye hoy al prefill del turno assistant?

**Módulo 03**
- ¿Cuándo grading por código y cuándo por modelo?
- ¿Qué hace mala a una rúbrica?

**Módulo 04**
- ¿Para qué sirven las etiquetas XML, más allá de ordenar?
- ¿Por qué "CRITICAL: DEBES..." es contraproducente hoy?

**Módulo 05**
- ¿Qué pasa si guardas solo el texto de la respuesta y no `response.content`?
- ¿Por qué los `tool_result` de llamadas paralelas van en un solo mensaje?
- ¿Qué hace el tool runner y qué sigue estando en tus manos?

**Módulo 06**
- ¿En qué gana BM25 a los embeddings?
- ¿Por qué RRF en vez de mezclar scores directamente?

**Módulo 07**
- ¿En qué orden se renderiza el prompt, y por qué importa para el caché?
- Nombra tres invalidadores silenciosos de caché.

**Módulo 08**
- ¿Cuándo tool y cuándo resource?

**Módulo 10**
- Las cuatro condiciones antes de construir un agente.
- ¿Cuándo un paso de tu pipeline debería ser código y no una llamada al modelo?

---

## Proyecto final (propio, no del curso)

Para que el repositorio valga como muestra pública, conviene rematarlo con algo
que integre varios módulos en vez de dejar los ejercicios sueltos.

### Propuesta: asistente documental con evaluación

Un sistema que responde preguntas sobre un corpus propio, y que **se mide a sí
mismo**.

Piezas y de dónde salen:

| Pieza | Módulo |
|---|---|
| Ingesta y chunking del corpus | 06 |
| Índice híbrido (embeddings + BM25 + RRF) | 06 |
| Herramienta de búsqueda para el agente | 05 |
| Bucle agéntico con tool runner | 05, 10 |
| Router: pregunta simple → RAG directo; compleja → agéntica | 10 |
| Respuestas con citas verificables | 07 |
| Prompt caching sobre system + tools | 07 |
| Suite de evals con dataset propio | 03 |
| Servidor MCP que expone la búsqueda | 08 |

### Criterio de terminado

- [ ] Funciona de punta a punta con un corpus real tuyo
- [ ] Hay una suite de evals que se ejecuta con un comando
- [ ] Los números de la eval están en el README
- [ ] Se puede conectar a Claude Code vía MCP
- [ ] El README explica las decisiones de diseño, no solo cómo instalarlo

Ese último punto es el que convierte el repo en algo que se puede enseñar en una
entrevista: cualquiera puede seguir un curso, pocos documentan por qué eligieron
cada cosa.

---

## Cierre

Al terminar:

1. Descarga el certificado de Anthropic Academy.
2. Rellena el `docs/PROGRESO.md` completo.
3. Repasa el README raíz: es lo primero que verá quien entre desde GitHub.
4. Cursos que continúan de forma natural:
   - Claude Code in Action
   - MCP: Build Rich-Context AI Apps
   - Claude with Excel / Claude for Data Science
