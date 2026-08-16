"""Herramienta de servidor: la ejecuta Anthropic, yo solo leo los resultados."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, get_client, print_usage
from shared.utils import console

client = get_client()

WEB_SEARCH = {
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 5,
    # "allowed_domains": ["docs.anthropic.com"],
    # "blocked_domains": ["ejemplo.com"],
}

response = client.messages.create(
    model=MODEL,
    max_tokens=4096,
    tools=[WEB_SEARCH],
    messages=[{
        "role": "user",
        "content": "¿Qué novedades trae la última versión del SDK de Python de Anthropic?",
    }],
)

console.print(f"[bold]stop_reason:[/bold] {response.stop_reason}\n")

for bloque in response.content:
    if bloque.type == "text":
        console.print(bloque.text)

    elif bloque.type == "server_tool_use":
        console.print(f"\n[dim]buscando: {bloque.input}[/dim]")

    elif bloque.type == "web_search_tool_result":
        contenido = bloque.content
        # En éxito content es una LISTA; en error es un OBJETO.
        if isinstance(contenido, list):
            console.print(f"[green]{len(contenido)} resultados[/green]")
            for r in contenido[:3]:
                console.print(f"  - {r.title}\n    {r.url}")
        else:
            console.print(f"[red]error de búsqueda: {contenido.error_code}[/red]")

print()
print_usage(response)

# Los errores de herramientas de servidor no lanzan excepción: llegan como 200
# con un bloque de resultado cuyo content es un objeto de error.
#
# web_search_20260209 lleva filtrado dinámico y ejecuta código por debajo, así
# que NO hay que declarar además code_execution: dos entornos confunden al modelo.
#
# Si el turno tarda mucho puede volver con pause_turn: reenvío el historial tal
# cual y el servidor continúa. Nada de añadir un "continúa".
