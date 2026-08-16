# 06 — RAG y búsqueda agéntica

Construir un pipeline de recuperación desde cero: chunking, embeddings,
búsqueda léxica y combinación de índices.

## Lecciones y archivos

| Lección | Archivo |
|---|---|
| Introducción a RAG | este README |
| Estrategias de chunking | [`01_chunking.py`](01_chunking.py) |
| Embeddings de texto | [`02_embeddings.py`](02_embeddings.py) |
| El flujo completo de RAG / implementarlo | [`03_pipeline_rag.py`](03_pipeline_rag.py) |
| Búsqueda léxica BM25 | [`04_bm25.py`](04_bm25.py) |
| Pipeline RAG multi-índice | [`05_multi_indice.py`](05_multi_indice.py) |
| Extra: búsqueda agéntica | [`06_busqueda_agentica.py`](06_busqueda_agentica.py) |

## El flujo

```
INDEXACIÓN (una vez)
  documentos → chunks → embeddings → índice

CONSULTA (por pregunta)
  pregunta → embedding → top-k chunks → prompt con contexto → respuesta
```

## Decisiones que importan

**Chunking.** El tamaño del chunk es el parámetro que más afecta a la calidad.
Demasiado pequeño y pierdes contexto; demasiado grande y metes ruido y gastas
tokens. Estrategias, de menos a más sofisticada:

1. Tamaño fijo con solape — simple, rompe frases por la mitad
2. Por estructura (párrafos, secciones, headers markdown) — respeta el sentido
3. Semántico — corta donde cambia el tema, más caro de calcular

**Embeddings.** Anthropic no tiene endpoint de embeddings propio; el curso usa
Voyage AI (`voyageai`, recomendado por Anthropic). Alternativas: modelos locales
con `sentence-transformers`, u otros proveedores.

**Léxico vs semántico.** Los embeddings fallan con términos exactos: códigos de
error, SKUs, nombres propios raros. BM25 los borda. Por eso lo estándar hoy es
combinar los dos índices y fusionar los rankings (Reciprocal Rank Fusion).

**Búsqueda agéntica.** El giro moderno: en vez de recuperar una vez y responder,
le das al modelo una herramienta de búsqueda y deja que consulte varias veces,
refinando la query según lo que va encontrando. Suele ganar a un RAG de un solo
paso en preguntas complejas.

## Aviso de coste

Indexar genera embeddings de todos los chunks. Con el corpus de ejemplo de
`data/` es despreciable, pero ten cuidado si lo apuntas a tu propio corpus.

## Notas propias

<!-- Tus apuntes del módulo. -->
