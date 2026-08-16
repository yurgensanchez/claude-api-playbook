"""Pipeline RAG de punta a punta: indexar, recuperar, generar."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rag import Indice, proveedor_activo  # noqa: E402

from shared import MODEL, extract_text, get_client  # noqa: E402
from shared.utils import console  # noqa: E402

DATA = Path(__file__).parent / "data"
INDICE = DATA / "indice.json"

client = get_client()


def obtener_indice(reconstruir: bool = False) -> Indice:
    if INDICE.exists() and not reconstruir:
        return Indice.cargar(INDICE)

    console.print(f"[dim]Indexando con proveedor: {proveedor_activo()}[/dim]")
    indice = Indice.desde_directorio(DATA)
    indice.guardar(INDICE)
    console.print(f"[green]{len(indice)} chunks indexados[/green]")
    return indice


PROMPT_RAG = """
Responde la pregunta usando ÚNICAMENTE la información de <contexto>.
Si el contexto no contiene la respuesta, dilo explícitamente en vez de
recurrir a tu conocimiento general.
Cita la sección de la que sale cada afirmación.

<contexto>
{contexto}
</contexto>

<pregunta>
{pregunta}
</pregunta>
"""


def responder(indice: Indice, pregunta: str, k: int = 3) -> tuple[str, list[dict]]:
    chunks = indice.buscar(pregunta, k=k)

    contexto = "\n\n".join(
        f'<fragmento seccion="{c["titulo"]}">\n{c["texto"]}\n</fragmento>'
        for c in chunks
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[
            {"role": "user", "content": PROMPT_RAG.format(contexto=contexto, pregunta=pregunta)}
        ],
    )
    return extract_text(response), chunks


if __name__ == "__main__":
    indice = obtener_indice()

    PREGUNTAS = [
        "¿Qué política de devoluciones se aplica a un producto descatalogado?",
        "¿Qué significa el error ERR-4021?",
        "¿Cuál es la capital de Mongolia?",  # fuera del corpus: debe decir que no sabe
    ]

    for pregunta in PREGUNTAS:
        console.print(f"\n[bold green]P:[/bold green] {pregunta}")
        respuesta, chunks = responder(indice, pregunta)

        console.print("[dim]fragmentos recuperados:[/dim]")
        for c in chunks:
            console.print(f"  [dim]{c['score']:.4f}  [{c['titulo']}][/dim]")

        console.print(f"[cyan]R:[/cyan] {respuesta}")

# k bajo -> me dejo fuera el fragmento con la respuesta.
# k alto -> meto ruido. Empiezo por 3-5.
#
# La instrucción "si no está en el contexto, dilo" es lo que evita que rellene
# con conocimiento general. La tercera pregunta lo comprueba.
#
# La métrica que importa: ¿entró el fragmento correcto en el top-k? Si no entró,
# el problema es de RECUPERACIÓN, no del prompt. Por eso imprimo los fragmentos
# recuperados junto a la respuesta: sin eso no se puede diagnosticar cuál falló.
