"""Índice híbrido: comparo semántico solo, léxico solo y la fusión."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rag import Indice, reciprocal_rank_fusion  # noqa: E402

from shared.utils import console  # noqa: E402

DATA = Path(__file__).parent / "data"
INDICE = DATA / "indice.json"


def demo_rrf() -> None:
    """RRF con rankings de juguete, para ver el mecanismo aislado."""
    semantico = [0, 2, 1, 4]
    lexico = [1, 0, 3]

    console.print("[bold]Cómo funciona RRF[/bold]")
    console.print(f"  ranking semántico: {semantico}")
    console.print(f"  ranking léxico   : {lexico}")

    for idx, score in reciprocal_rank_fusion([semantico, lexico]):
        console.print(f"    chunk {idx}  ->  {score:.5f}")

    console.print(
        "[dim]  El 0 sube porque aparece alto en los dos.\n"
        "  El 4 y el 3 bajan porque solo salen en uno y en mala posición.[/dim]\n"
    )


def comparar(indice: Indice, consultas: list[str]) -> None:
    """Lo que de verdad importa: en qué se diferencian sobre el corpus real."""
    for consulta in consultas:
        console.print(f"\n[bold green]{consulta}[/bold green]")

        sem = indice.buscar_semantico(consulta, k=3)
        lex = indice.buscar_lexico(consulta, k=3)
        hib = indice.buscar(consulta, k=3)

        console.print("  [cyan]semántico[/cyan]")
        for i in sem:
            console.print(f"    [{indice.chunks[i]['titulo']}] {indice.chunks[i]['texto'][:60]}...")

        console.print("  [yellow]léxico (BM25)[/yellow]")
        if not lex:
            console.print("    [dim](sin coincidencias léxicas)[/dim]")
        for i in lex:
            console.print(f"    [{indice.chunks[i]['titulo']}] {indice.chunks[i]['texto'][:60]}...")

        console.print("  [green]híbrido (RRF)[/green]")
        for c in hib:
            console.print(f"    [{c['titulo']}] {c['texto'][:60]}...")


if __name__ == "__main__":
    demo_rrf()

    if not INDICE.exists():
        console.print("[yellow]Falta el índice. Ejecuta antes 03_pipeline_rag.py[/yellow]")
        sys.exit(0)

    indice = Indice.cargar(INDICE)
    console.print(f"[dim]{len(indice)} chunks en el índice[/dim]")

    comparar(indice, [
        "ERR-4021",                          # código exacto: gana léxico
        "¿cuándo caduca una sesión?",        # paráfrasis: gana semántico
        "devolver un monitor descatalogado",  # mezcla: gana el híbrido
    ])

# Pendiente de probar: reranking. Pasar los ~10 candidatos por un modelo de
# rerank (voyageai tiene `rerank`) o por Claude pidiéndole que los ordene por
# relevancia real. Suele ser la mejora individual más grande del pipeline.
#
# Y medir de verdad: conjunto de preguntas con el fragmento correcto conocido,
# y comparar recall@5 de las tres estrategias. Sin esa medida, "parece que va
# mejor" no significa nada.
