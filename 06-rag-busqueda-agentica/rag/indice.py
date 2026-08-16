"""Índice híbrido: semántico (embeddings) + léxico (BM25), fusionado con RRF."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

from .chunking import chunk_por_secciones
from .embeddings import embed


def _tokenizar(texto: str) -> list[str]:
    return re.findall(r"\w+", texto.lower())


def reciprocal_rank_fusion(rankings: list[list[int]], k: int = 60) -> list[tuple[int, float]]:
    """Fusiona rankings por POSICIÓN, no por puntuación.

    BM25 y coseno viven en escalas distintas y normalizarlas bien es un problema
    en sí mismo. RRF solo mira el orden, así que da igual la escala.
    """
    puntuaciones: dict[int, float] = {}
    for ranking in rankings:
        for posicion, idx in enumerate(ranking, start=1):
            puntuaciones[idx] = puntuaciones.get(idx, 0.0) + 1.0 / (k + posicion)
    return sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True)


class Indice:
    """Índice en memoria, persistible a JSON.

    Suficiente para un corpus de miles de chunks. Por encima de eso toca una
    base vectorial de verdad (pgvector, Qdrant, Chroma): esto carga todos los
    vectores en RAM y calcula el coseno contra todos en cada consulta.
    """

    def __init__(self, chunks: list[dict], vectores: np.ndarray):
        self.chunks = chunks
        self.vectores = vectores
        self._normas = np.linalg.norm(vectores, axis=1)
        self._bm25 = BM25Okapi([_tokenizar(c["texto"]) for c in chunks])

    # --- construcción ---------------------------------------------------
    @classmethod
    def desde_texto(cls, texto: str) -> "Indice":
        chunks = chunk_por_secciones(texto)
        vectores = np.array(embed([c["texto"] for c in chunks], tipo="document"))
        return cls(chunks, vectores)

    @classmethod
    def desde_directorio(cls, directorio: Path, patron: str = "*.md") -> "Indice":
        chunks: list[dict] = []
        for archivo in sorted(directorio.glob(patron)):
            for chunk in chunk_por_secciones(archivo.read_text(encoding="utf-8")):
                chunks.append({**chunk, "fuente": archivo.name})

        if not chunks:
            raise ValueError(f"No encontré nada que indexar en {directorio}/{patron}")

        vectores = np.array(embed([c["texto"] for c in chunks], tipo="document"))
        return cls(chunks, vectores)

    # --- persistencia ---------------------------------------------------
    def guardar(self, destino: Path) -> None:
        destino.write_text(
            json.dumps(
                {"chunks": self.chunks, "vectores": self.vectores.tolist()},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    @classmethod
    def cargar(cls, origen: Path) -> "Indice":
        datos = json.loads(origen.read_text(encoding="utf-8"))
        return cls(datos["chunks"], np.array(datos["vectores"]))

    # --- búsqueda -------------------------------------------------------
    def buscar_semantico(self, consulta: str, k: int = 10) -> list[int]:
        vector = np.array(embed([consulta], tipo="query")[0])
        similitudes = (self.vectores @ vector) / (self._normas * np.linalg.norm(vector))
        return np.argsort(similitudes)[::-1][:k].tolist()

    def buscar_lexico(self, consulta: str, k: int = 10) -> list[int]:
        puntuaciones = self._bm25.get_scores(_tokenizar(consulta))
        orden = np.argsort(puntuaciones)[::-1]
        return [int(i) for i in orden[:k] if puntuaciones[i] > 0]

    def buscar(self, consulta: str, k: int = 5) -> list[dict]:
        """Búsqueda híbrida. Es la que se usa en producción.

        Recupero 10 de cada índice y fusiono, en vez de quedarme con k de uno:
        un fragmento que sale décimo en semántico y segundo en léxico sube al
        combinar, y ese es justo el caso que la búsqueda sola se pierde.
        """
        fusionado = reciprocal_rank_fusion([
            self.buscar_semantico(consulta, k=10),
            self.buscar_lexico(consulta, k=10),
        ])
        return [{**self.chunks[idx], "score": score} for idx, score in fusionado[:k]]

    def __len__(self) -> int:
        return len(self.chunks)
