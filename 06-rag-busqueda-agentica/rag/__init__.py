"""Pipeline de recuperación reutilizable.

Lo saco del archivo de lección porque 03_, 05_ y 06_ necesitan lo mismo.
"""

from .chunking import chunk_por_secciones
from .embeddings import embed, proveedor_activo
from .indice import Indice, reciprocal_rank_fusion

__all__ = [
    "chunk_por_secciones",
    "embed",
    "proveedor_activo",
    "Indice",
    "reciprocal_rank_fusion",
]
