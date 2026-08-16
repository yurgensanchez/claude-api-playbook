"""Pipeline RAG de punta a punta: indexar, recuperar, generar."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client
from shared.utils import console

DATA = Path(__file__).parent / "data"
INDICE = DATA / "indice.json"
MODELO_EMBEDDING = "voyage-3"

client = get_client()


def construir_indice() -> None:
    # TODO leer corpus -> chunkear (reutilizar chunk_por_secciones de 01_)
    #      -> embed(input_type="document")
    #      -> guardar [{"texto", "titulo", "vector"}] en INDICE
    raise NotImplementedError


def recuperar(pregunta: str, k: int = 3) -> list[dict]:
    # TODO embed(pregunta, input_type="query") -> coseno contra el índice
    #      -> devolver los k mejores
    raise NotImplementedError


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


def responder(pregunta: str, k: int = 3) -> str:
    chunks = recuperar(pregunta, k)

    contexto = "\n\n".join(
        f"<fragmento seccion=\"{c['titulo']}\">\n{c['texto']}\n</fragmento>"
        for c in chunks
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[
            {"role": "user", "content": PROMPT_RAG.format(contexto=contexto, pregunta=pregunta)}
        ],
    )
    return extract_text(response)


if __name__ == "__main__":
    if not INDICE.exists():
        console.print("Construyendo índice...")
        construir_indice()

    PREGUNTAS = [
        "¿Qué política de devoluciones se aplica?",
        "¿Cuál es la capital de Mongolia?",  # fuera del corpus: debe decir que no sabe
    ]

    for p in PREGUNTAS:
        console.print(f"\n[bold green]P:[/bold green] {p}")
        console.print(f"[cyan]R:[/cyan] {responder(p)}")

# k bajo -> me dejo fuera el fragmento con la respuesta.
# k alto -> meto ruido. Empiezo por 3-5.
#
# La instrucción "si no está en el contexto, dilo" es lo que evita que rellene
# con conocimiento general. Probar a quitarla y comparar.
#
# La métrica que importa: ¿entró el fragmento correcto en el top-k? Si no entró,
# el problema es de RECUPERACIÓN, no del prompt. Medir las dos fases por separado.
