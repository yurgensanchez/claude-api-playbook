"""En vez de recuperar una vez, le doy una tool de búsqueda y decide él."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client
from shared.utils import console

client = get_client()

BUSCAR_EN_BASE = {
    "name": "buscar_en_base",
    "description": (
        "Busca fragmentos relevantes en la base de conocimiento interna. "
        "Úsala siempre que la respuesta dependa de documentación interna, "
        "políticas o datos de producto. Puedes llamarla varias veces con "
        "consultas distintas si la primera no devuelve lo que necesitas. "
        "Devuelve como máximo 5 fragmentos con su sección de origen."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "consulta": {
                "type": "string",
                "description": "Consulta de búsqueda. Sé específico.",
            },
            "k": {"type": "integer", "description": "Número de fragmentos (1-10)"},
        },
        "required": ["consulta"],
    },
}


def buscar_en_base(consulta: str, k: int = 5) -> list[dict]:
    # TODO conectar el pipeline de 05_
    raise NotImplementedError


SYSTEM = """
Eres un asistente que responde a partir de la base de conocimiento interna.

Antes de responder, busca. Si los primeros resultados no contienen la respuesta,
reformula la consulta y vuelve a buscar en vez de rendirte o improvisar.

Cita la sección de la que sale cada afirmación. Si tras varias búsquedas la
información no está, dilo claramente.
"""


def responder(pregunta: str) -> str:
    messages = [{"role": "user", "content": pregunta}]

    for _ in range(8):
        response = client.messages.create(
            model=MODEL, max_tokens=4096, system=SYSTEM,
            tools=[BUSCAR_EN_BASE], messages=messages,
        )

        if response.stop_reason == "end_turn":
            return extract_text(response)

        messages.append({"role": "assistant", "content": response.content})

        resultados = []
        for bloque in response.content:
            if bloque.type != "tool_use":
                continue
            console.print(f"  [dim]buscando: {bloque.input['consulta']}[/dim]")
            try:
                fragmentos = buscar_en_base(**bloque.input)
                contenido, es_error = json.dumps(fragmentos, ensure_ascii=False), False
            except Exception as e:  # noqa: BLE001
                contenido, es_error = str(e), True

            resultados.append({
                "type": "tool_result",
                "tool_use_id": bloque.id,
                "content": contenido,
                "is_error": es_error,
            })

        messages.append({"role": "user", "content": resultados})

    return "[límite de iteraciones alcanzado]"


if __name__ == "__main__":
    console.print(responder("¿Puedo devolver un monitor descatalogado?"))

# RAG clásico: 1 búsqueda fija, con la pregunta tal cual, barato y rápido.
# Agéntico: las búsquedas que decida, reformulando, más lento y más caro.
#
# Empiezo por el clásico. Paso al agéntico cuando mida que mis preguntas
# necesitan más de una recuperación para responderse.
