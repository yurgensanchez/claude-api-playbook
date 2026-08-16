"""Embeddings con dos proveedores.

Anthropic no tiene endpoint de embeddings, así que hay que traerlos de fuera.
Uso Voyage si hay clave y, si no, un modelo local: así el pipeline se puede
ejecutar sin dar de alta nada.
"""

from __future__ import annotations

import os
from functools import lru_cache

MODELO_VOYAGE = "voyage-3"
MODELO_LOCAL = "all-MiniLM-L6-v2"


def proveedor_activo() -> str:
    """voyage | local | ninguno"""
    if os.getenv("VOYAGE_API_KEY"):
        return "voyage"
    try:
        import sentence_transformers  # noqa: F401

        return "local"
    except ImportError:
        return "ninguno"


@lru_cache(maxsize=1)
def _cliente_voyage():
    import voyageai

    return voyageai.Client()


@lru_cache(maxsize=1)
def _modelo_local():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODELO_LOCAL)


def embed(textos: list[str], tipo: str = "document") -> list[list[float]]:
    """Vectoriza una lista de textos.

    `tipo` es "document" al indexar y "query" al buscar. Voyage aplica prefijos
    internos distintos según el caso y mezclarlos empeora los resultados; el
    modelo local no distingue, así que ahí el parámetro se ignora.
    """
    proveedor = proveedor_activo()

    if proveedor == "voyage":
        respuesta = _cliente_voyage().embed(textos, model=MODELO_VOYAGE, input_type=tipo)
        return respuesta.embeddings

    if proveedor == "local":
        return _modelo_local().encode(textos, show_progress_bar=False).tolist()

    raise RuntimeError(
        "No hay proveedor de embeddings.\n"
        "  Opción A: añade VOYAGE_API_KEY al .env (https://dash.voyageai.com)\n"
        "  Opción B: pip install sentence-transformers"
    )
