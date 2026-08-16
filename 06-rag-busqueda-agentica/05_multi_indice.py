"""Fusiono el ranking semántico y el léxico con RRF."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.utils import console


def reciprocal_rank_fusion(
    rankings: list[list[str]], k: int = 60
) -> list[tuple[str, float]]:
    """Fusiona rankings sin normalizar puntuaciones.

        score(d) = suma sobre rankings de  1 / (k + posicion(d))

    BM25 y coseno viven en escalas distintas y normalizarlas bien es un problema
    en sí mismo. RRF solo usa el orden, así que da igual la escala.
    """
    puntuaciones: dict[str, float] = {}
    for ranking in rankings:
        for posicion, doc_id in enumerate(ranking, start=1):
            puntuaciones[doc_id] = puntuaciones.get(doc_id, 0.0) + 1.0 / (k + posicion)
    return sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    ranking_semantico = ["doc_A", "doc_C", "doc_B", "doc_E"]
    ranking_lexico = ["doc_B", "doc_A", "doc_D"]

    console.print("[bold]Ranking semántico[/bold]:", ranking_semantico)
    console.print("[bold]Ranking léxico[/bold]   :", ranking_lexico)
    console.print()

    fusionado = reciprocal_rank_fusion([ranking_semantico, ranking_lexico])
    console.print("[bold]Fusionado (RRF)[/bold]")
    for doc_id, score in fusionado:
        console.print(f"  {doc_id}  {score:.5f}")

    console.print(
        "\n[dim]doc_A sube porque aparece alto en ambos.\n"
        "doc_E y doc_D bajan porque solo salen en uno y en mala posición.[/dim]"
    )


# TODO 1: pipeline real — indexar en ambos índices, recuperar top-10 de cada uno,
#         fusionar con RRF, quedarme con el top-5 para el prompt.
#
# TODO 2: reranking. Pasar los candidatos por un modelo de rerank (voyageai
#         tiene `rerank`) o por Claude. Suele ser la mejora individual más grande.
#
# TODO 3: medir. Conjunto de preguntas con el fragmento correcto conocido y
#         comparar recall@5 de: solo semántico / solo BM25 / fusionado.
#         Sin esa medida, "parece que va mejor" no significa nada.
