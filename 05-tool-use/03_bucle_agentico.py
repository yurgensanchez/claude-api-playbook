"""Bucle agéntico: repito el ciclo hasta que deje de pedir herramientas."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client
from shared.utils import console

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools import TODAS_LAS_TOOLS, ejecutar_tool  # noqa: E402

client = get_client()

MAX_ITERACIONES = 10  # nunca un while True sin tope


def responder(pregunta: str, verbose: bool = True) -> str:
    messages: list[dict] = [{"role": "user", "content": pregunta}]

    for iteracion in range(MAX_ITERACIONES):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            tools=TODAS_LAS_TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            return extract_text(response)

        # Herramienta de servidor que agotó sus iteraciones internas:
        # se reenvía tal cual y el servidor continúa donde lo dejó.
        if response.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": response.content})
            continue

        if response.stop_reason == "refusal":
            return f"[rechazado] {getattr(response.stop_details, 'explanation', '')}"

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for bloque in response.content:
            if bloque.type != "tool_use":
                continue

            if verbose:
                console.print(
                    f"  [dim]{iteracion + 1}. {bloque.name}"
                    f"({json.dumps(bloque.input, ensure_ascii=False)})[/dim]"
                )

            resultado, es_error = ejecutar_tool(bloque.name, bloque.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": bloque.id,
                "content": json.dumps(resultado, ensure_ascii=False, default=str),
                "is_error": es_error,
            })

        messages.append({"role": "user", "content": tool_results})

    return "[se alcanzó el límite de iteraciones]"


if __name__ == "__main__":
    PREGUNTAS = [
        "¿Cuánto me costarían 4 teclados mecánicos del 75%, con IVA?",
        "Mi pedido PED-9999 no llega, ¿qué pasa?",
    ]

    for pregunta in PREGUNTAS:
        console.print(f"\n[bold green]Usuario:[/bold green] {pregunta}")
        console.print("[bold]Herramientas usadas:[/bold]")
        respuesta = responder(pregunta)
        console.print(f"\n[bold cyan]Claude:[/bold cyan] {respuesta}\n")
        console.print("─" * 70)

# El tope convierte un cuelgue en un fallo visible.
# En el segundo caso el pedido no existe: la herramienta devuelve is_error y el
# modelo lo explica en vez de inventarse un estado. Eso se pierde si silencio errores.
