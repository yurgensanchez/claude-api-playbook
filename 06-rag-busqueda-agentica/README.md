# 06 — RAG y búsqueda agéntica

Pipeline de recuperación completo: chunking, embeddings, búsqueda léxica,
fusión de índices y búsqueda agéntica.

**Antes de montar nada de esto, lee la sección siguiente.** La mitad de los RAG
que se construyen hoy no hacían falta.

---

## Antes de montar un RAG: ¿lo necesitas?

Con contextos de 1M de tokens, meter el documento entero y cachearlo suele
ganar. Los números, para un documento de 100 páginas (~75.000 tokens) sobre
Opus 5, con 20 consultas:

| Enfoque | Por consulta | 20 consultas |
|---|---|---|
| Mandar el documento sin cachear | $0,375 | **$7,50** |
| Documento entero + prompt caching | $0,0375 | **$1,18** |
| RAG (5 fragmentos ≈ 2.500 tokens) | $0,0125 | **$0,26** |

El RAG es más barato en tokens, sí. Pero ahorra **$0,90** a cambio de: montar
un índice, mantenerlo, y añadir un modo de fallo que no existía.

La diferencia se vuelve real con volumen. A 1.000 consultas diarias sobre el
mismo documento son ~$1.650/mes con caché contra ~$375 con RAG. **El RAG se
amortiza con volumen, no con tamaño.**

### El modo de fallo que se subestima

| | Qué pasa si falla |
|---|---|
| Caching | Nada. Si la caché expiró pagas completo y la respuesta es idéntica. |
| RAG | Si el fragmento correcto no entra en el top-k, la respuesta es incorrecta — y suena convincente. |

Con caching el modelo ve **todo** el documento en cada petición. Con RAG ve
solo los fragmentos que el recuperador eligió.

Por eso hay preguntas que el RAG no puede responder por diseño:

- *"¿Hay contradicciones entre la sección 2 y la 9?"*
- *"¿Cuántas veces se menciona el proveedor X en todo el contrato?"*
- *"Resume el documento"*

Ninguna se parece a un fragmento concreto, así que la recuperación por
similitud no sabe qué traer.

### ¿Y un grafo de conocimiento (GraphRAG, Cognee)?

Cierra parte del hueco, no todo:

| Pregunta | Grafo |
|---|---|
| Contradicciones entre secciones | Mejora — enlaza menciones de la misma entidad aunque estén lejos. Pero solo detecta lo que la extracción modeló como relación. |
| Contar menciones exactas | Sigue fallando, y peor: la extracción con LLM es *lossy* y te devuelve un número con apariencia de exacto. Para esto gana un `grep`. |
| Resumen global | Gana. La indexación ya genera resúmenes jerárquicos. |

El detalle económico: construir el grafo pasa un LLM por **todo** el corpus. Así
que el argumento "RAG es más barato porque no mando el documento entero" se cae
— lo mandas igual, solo que una vez y más caro que una escritura de caché.

Un grafo compensa para **memoria persistente entre sesiones** y **relaciones
que cruzan muchos documentos**, no para "un documento, muchas preguntas".

### La arquitectura que suele ganar hoy

Híbrida, y cambia el papel del recuperador:

```
Recuperación  →  ¿en QUÉ documento está esto?   (índice de resúmenes/metadatos)
Caching       →  cargar ESE documento entero    (y preguntar lo que haga falta)
```

La recuperación deja de ser *"tráeme los párrafos con los que voy a responder"*
y pasa a ser *"dime qué documento abrir"*. Es un trabajo más fácil y el fallo se
ablanda: si acierta el documento, el modelo lee las 100 páginas y encuentra el
párrafo él solo.

Consecuencia práctica: si el índice solo enruta, no necesitas trocear en
fragmentos de 500 caracteres. Indexas **un resumen y metadatos por documento**.

### Resumen de decisión

1. ¿Cabe el corpus en 1M de tokens y el volumen es bajo? → **caching**, y te ahorras el pipeline.
2. ¿Cabe pero son muchos documentos? → **router sobre metadatos + caching** del documento elegido.
3. ¿No cabe, o el volumen es alto? → **RAG**, y mide la calidad de la recuperación.
4. ¿Necesitas memoria entre sesiones o relaciones entre documentos? → **grafo**.

Lo que sigue implementa el 3, que es el caso que enseña el curso.

---

## Archivos

| Lección | Archivo |
|---|---|
| Estrategias de chunking | [`01_chunking.py`](01_chunking.py) |
| Embeddings de texto | [`02_embeddings.py`](02_embeddings.py) |
| Flujo RAG completo | [`03_pipeline_rag.py`](03_pipeline_rag.py) |
| Búsqueda léxica BM25 | [`04_bm25.py`](04_bm25.py) |
| Índice híbrido y fusión RRF | [`05_multi_indice.py`](05_multi_indice.py) |
| Búsqueda agéntica | [`06_busqueda_agentica.py`](06_busqueda_agentica.py) |
| Pipeline reutilizable | [`rag/`](rag/) |

`rag/` es el pipeline de verdad; los archivos numerados lo usan o explican una
pieza aislada.

```
rag/
├── chunking.py     troceo por secciones, con partición si se pasa de largo
├── embeddings.py   Voyage o modelo local, según lo que haya disponible
└── indice.py       índice híbrido (coseno + BM25), fusión RRF, persistencia
```

## Cómo ejecutarlo

```bash
python 06-rag-busqueda-agentica/03_pipeline_rag.py   # construye el índice y pregunta
python 06-rag-busqueda-agentica/05_multi_indice.py   # compara las tres búsquedas
python 06-rag-busqueda-agentica/06_busqueda_agentica.py
```

La primera ejecución indexa `data/` y guarda `data/indice.json`. Las siguientes
lo reutilizan.

**Embeddings.** Anthropic no tiene endpoint propio, así que hay dos opciones:

- `VOYAGE_API_KEY` en el `.env` — es lo que usa el curso
- `pip install sentence-transformers` — local, sin dar de alta nada

`rag/embeddings.py` detecta cuál hay y usa esa. `proveedor_activo()` te dice
cuál está en uso.

## Decisiones del pipeline

**Chunking por secciones**, conservando el título como metadato. Con eso el
modelo puede citar de dónde sale cada afirmación, y en la depuración ves qué
sección se recuperó.

**Recupero 10 de cada índice y fusiono**, en vez de quedarme con 5 de uno. Un
fragmento que sale décimo en semántico y segundo en léxico sube al combinar —
y ese es justo el caso que cada búsqueda por separado se pierde.

**RRF en vez de mezclar puntuaciones.** BM25 y coseno viven en escalas
distintas; normalizarlas bien es un problema en sí mismo. RRF solo usa el
orden, así que la escala da igual.

**Índice en JSON, en memoria.** Vale para miles de chunks. Por encima toca una
base vectorial de verdad (pgvector, Qdrant, Chroma): esto carga todos los
vectores en RAM y calcula el coseno contra todos en cada consulta.

## Lo que falta

- **Reranking.** Pasar los ~10 candidatos por un modelo de rerank o por Claude
  pidiéndole que los ordene por relevancia real. Suele ser la mejora individual
  más grande del pipeline.
- **Medición.** Conjunto de preguntas con el fragmento correcto conocido, y
  comparar recall@5 entre semántico, léxico e híbrido. Sin eso, "parece que va
  mejor" no significa nada. El módulo 03 tiene la maquinaria para montarlo.

## Notas propias

<!-- Tus apuntes del módulo. -->
