"""Qué llega en la respuesta cuando el modelo decide usar una herramienta.

Aquí no ejecuto nada, solo inspecciono.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, get_client
from shared.utils import console

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools import TODAS_LAS_TOOLS  # noqa: E402

client = get_client()

response = client.messages.create(
    model=MODEL,
    max_tokens=2048,
    tools=TODAS_LAS_TOOLS,
    messages=[
        {"role": "user", "content": "¿Qué monitores tenéis por debajo de 400 euros?"}
    ],
)

console.print(f"[bold]stop_reason:[/bold] {response.stop_reason}\n")

for i, bloque in enumerate(response.content):
    console.print(f"[bold cyan]Bloque {i} — tipo: {bloque.type}[/bold cyan]")

    if bloque.type == "text":
        console.print(f"  {bloque.text}")

    elif bloque.type == "tool_use":
        console.print(f"  id     : {bloque.id}")
        console.print(f"  name   : {bloque.name}")
        console.print(f"  input  : {json.dumps(bloque.input, ensure_ascii=False)}")

    elif bloque.type == "thinking":
        console.print(f"  {bloque.thinking[:200]}...")

    console.print()

# stop_reason == "tool_use" es la señal de que quiere que ejecute algo.
# Una respuesta puede traer varios tool_use (llamadas paralelas) más un text.
# bloque.input ya viene parseado: nunca hacer match de cadenas sobre el JSON.
# bloque.id es el tool_use_id que tengo que devolver luego.
