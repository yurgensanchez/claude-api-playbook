"""Streaming: recibo los tokens según se generan."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, get_client, print_usage
from shared.utils import console

client = get_client()

PROMPT = "Escribe un párrafo sobre por qué el streaming mejora la UX de un chat."


console.print("[bold cyan]Streaming de texto[/bold cyan]\n")

with client.messages.stream(
    model=MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": PROMPT}],
) as stream:
    for texto in stream.text_stream:
        print(texto, end="", flush=True)

    # Aunque haya consumido los deltas, aquí tengo el mensaje completo.
    final = stream.get_final_message()

print("\n")
print_usage(final)


# Eventos crudos: los necesito si quiero distinguir thinking de texto en una UI.
console.print("\n[bold cyan]Eventos del stream[/bold cyan]\n")

with client.messages.stream(
    model=MODEL,
    max_tokens=1024,
    thinking={"type": "adaptive", "display": "summarized"},
    messages=[{"role": "user", "content": "¿Cuánto es 27 * 453? Razona el cálculo."}],
) as stream:
    for event in stream:
        if event.type == "content_block_start":
            if event.content_block.type == "thinking":
                console.print("\n[dim][razonando...][/dim]")
            elif event.content_block.type == "text":
                console.print("\n[bold][respuesta][/bold]")
        elif event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print(event.delta.thinking, end="", flush=True)
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)

print()

# Por encima de ~16.000 max_tokens el streaming deja de ser opcional:
# sin él salta el timeout HTTP del SDK. Con él llego a 128.000.
