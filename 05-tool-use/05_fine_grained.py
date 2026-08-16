"""Streaming del input de una herramienta según se genera."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, get_client
from shared.utils import console

client = get_client()

# eager_input_streaming se activa en la definición de la tool.
# Ya es GA: sin cabecera beta, con el stream normal.
REDACTAR_EMAIL = {
    "name": "redactar_email",
    "description": (
        "Guarda un borrador de email. Úsala cuando el usuario pida escribir o "
        "redactar un correo. Devuelve el id del borrador."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "destinatario": {"type": "string"},
            "asunto": {"type": "string"},
            "cuerpo": {"type": "string", "description": "Texto completo del email"},
        },
        "required": ["destinatario", "asunto", "cuerpo"],
    },
    "eager_input_streaming": True,
}

console.print("[bold]Streaming del input de la herramienta[/bold]\n")

with client.messages.stream(
    model=MODEL,
    max_tokens=4096,
    tools=[REDACTAR_EMAIL],
    messages=[
        {
            "role": "user",
            "content": (
                "Redacta un email a soporte@proveedor.com explicando que el "
                "pedido PED-5502 lleva dos semanas de retraso y pidiendo una "
                "fecha concreta de entrega."
            ),
        }
    ],
) as stream:
    for event in stream:
        if event.type == "content_block_start" and event.content_block.type == "tool_use":
            console.print(f"[cyan]-> herramienta: {event.content_block.name}[/cyan]")
        elif event.type == "content_block_delta":
            if event.delta.type == "input_json_delta":
                print(event.delta.partial_json, end="", flush=True)
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)

    final = stream.get_final_message()

print("\n")
for bloque in final.content:
    if bloque.type == "tool_use":
        console.print("[green]Input completo y ya parseado:[/green]")
        console.print(bloque.input)

# Merece la pena cuando el input es grande y el usuario está esperando: archivos,
# código, textos largos. Para un id o un filtro no aporta nada.
#
# Los partial_json NO son JSON válido por separado: solo se pueden mostrar en
# crudo o acumular. Para usar los datos, espero al bloque.input del mensaje final.
