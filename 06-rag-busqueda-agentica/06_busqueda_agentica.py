"""En vez de recuperar una vez, le doy una tool de búsqueda y decide él."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rag import Indice  # noqa: E402

from shared import MODEL, extract_text, get_client  # noqa: E402
from shared.utils import console  # noqa: E402

DATA = Path(__file__).parent / "data"
INDICE = DATA / "indice.json"

client = get_client()

BUSCAR_EN_BASE = {
    "name": "buscar_en_base",
    "description": (
        "Busca fragmentos relevantes en la base de conocimiento interna. "
        "Úsala siempre que la respuesta dependa de documentación interna, "
        "políticas o datos de producto. Puedes llamarla varias veces con "
        "consultas distintas si la primera no devuelve lo que necesitas. "
        "Devuelve como máximo 10 fragmentos con su sección de origen."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "consulta": {
                "type": "string",
                "description": "Consulta de búsqueda. Sé específico.",
            },
            "k": {
                "type": "integer",
                "description": "Número de fragmentos a devolver, entre 1 y 10",
            },
        },
        "required": ["consulta"],
    },
}


SYSTEM = """
Eres un asistente que responde a partir de la base de conocimiento interna.

Antes de responder, busca. Si los primeros resultados no contienen la respuesta,
reformula la consulta y vuelve a buscar en vez de rendirte o improvisar.

Cita la sección de la que sale cada afirmación. Si tras varias búsquedas la
información no está, dilo claramente.
"""


def responder(indice: Indice, pregunta: str, max_iteraciones: int = 8) -> str:
    messages: list[dict] = [{"role": "user", "content": pregunta}]

    for _ in range(max_iteraciones):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM,
            tools=[BUSCAR_EN_BASE],
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            return extract_text(response)

        messages.append({"role": "assistant", "content": response.content})

        resultados = []
        for bloque in response.content:
            if bloque.type != "tool_use":
                continue

            consulta = bloque.input["consulta"]
            k = min(max(bloque.input.get("k", 5), 1), 10)
            console.print(f"  [dim]buscando: \"{consulta}\" (k={k})[/dim]")

            try:
                fragmentos = [
                    {"seccion": c["titulo"], "texto": c["texto"]}
                    for c in indice.buscar(consulta, k=k)
                ]
                contenido = json.dumps(fragmentos, ensure_ascii=False)
                es_error = False
            except Exception as e:  # noqa: BLE001
                contenido, es_error = f"Error en la búsqueda: {e}", True

            resultados.append({
                "type": "tool_result",
                "tool_use_id": bloque.id,
                "content": contenido,
                "is_error": es_error,
            })

        messages.append({"role": "user", "content": resultados})

    return "[límite de iteraciones alcanzado]"


if __name__ == "__main__":
    if not INDICE.exists():
        console.print("[yellow]Falta el índice. Ejecuta antes 03_pipeline_rag.py[/yellow]")
        sys.exit(0)

    indice = Indice.cargar(INDICE)

    PREGUNTAS = [
        # Una recuperación basta: RAG clásico daría lo mismo.
        "¿Cuántos días tengo para devolver un producto?",
        # Cruza dos secciones: aquí es donde el agéntico se separa.
        "Compré un monitor ultrawide que ahora está descatalogado y quiero "
        "devolverlo. ¿Puedo, y quién paga el envío?",
    ]

    for pregunta in PREGUNTAS:
        console.print(f"\n[bold green]P:[/bold green] {pregunta}")
        console.print(f"[cyan]R:[/cyan] {responder(indice, pregunta)}")

# RAG clásico: 1 búsqueda fija, con la pregunta tal cual, barato y rápido.
# Agéntico: las búsquedas que decida, reformulando, más lento y más caro.
#
# La segunda pregunta es la que justifica el patrón: mezcla estado del producto
# (descatalogado), política de devolución y quién paga el envío. Eso vive en
# tres secciones distintas y una sola recuperación no las trae todas.
#
# Empiezo por el clásico. Paso al agéntico cuando mida que mis preguntas
# necesitan más de una recuperación para responderse.
