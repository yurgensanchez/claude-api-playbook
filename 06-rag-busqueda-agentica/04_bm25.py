"""Búsqueda léxica: donde los embeddings fallan."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rank_bm25 import BM25Okapi

from shared.utils import console

DOCUMENTOS = [
    "El error ERR-4021 ocurre cuando el token de sesión ha caducado.",
    "Los tokens de autenticación expiran a los 30 minutos de inactividad.",
    "Para renovar la sesión, llama al endpoint /auth/refresh.",
    "El SKU MON-011 está descatalogado desde marzo.",
    "Los monitores ultrawide de 34 pulgadas ya no se fabrican.",
]


def tokenizar(texto: str) -> list[str]:
    """En producción: minúsculas, stopwords y stemming."""
    return re.findall(r"\w+", texto.lower())


bm25 = BM25Okapi([tokenizar(d) for d in DOCUMENTOS])


def buscar(consulta: str, k: int = 3) -> list[tuple[float, str]]:
    puntuaciones = bm25.get_scores(tokenizar(consulta))
    ranking = sorted(zip(puntuaciones, DOCUMENTOS), reverse=True)
    return [(s, d) for s, d in ranking[:k] if s > 0]


if __name__ == "__main__":
    CONSULTAS = [
        "ERR-4021",                    # término exacto: gana BM25
        "MON-011",                     # SKU: gana BM25
        "¿cuándo caduca la sesión?",   # semántica: aquí flojea
    ]

    for consulta in CONSULTAS:
        console.print(f"\n[bold green]Consulta:[/bold green] {consulta}")
        resultados = buscar(consulta)
        if not resultados:
            console.print("  [dim]sin coincidencias léxicas[/dim]")
        for score, doc in resultados:
            console.print(f"  [{score:.2f}] {doc}")

# BM25 gana en: códigos de error, SKUs, nombres propios raros, siglas.
# Embeddings ganan en: paráfrasis, sinónimos, preguntas en lenguaje natural.
#
# En la tercera consulta se ve: "caduca" no aparece en el doc 1, que dice
# "expiran". La respuesta no es elegir uno, es combinarlos (05_).
