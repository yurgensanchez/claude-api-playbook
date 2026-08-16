"""EJERCICIO — chat de terminal con historial.

Lo que tengo que sacar:
  1. Bucle que lea input hasta "salir".
  2. Historial completo reenviado en cada petición.
  3. Comando "/reset" para limpiarlo.
  4. Consumo de tokens acumulado al salir.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client
from shared.utils import console

client = get_client()


def chat() -> None:
    messages: list[dict] = []
    tokens_entrada = 0
    tokens_salida = 0

    console.print("[dim]Escribe 'salir' para terminar, '/reset' para limpiar.[/dim]\n")

    while True:
        entrada = console.input("[bold green]Tú:[/bold green] ").strip()

        if entrada.lower() in {"salir", "exit", "quit"}:
            break
        if entrada == "/reset":
            messages.clear()
            console.print("[yellow]Historial limpiado.[/yellow]\n")
            continue
        if not entrada:
            continue

        # TODO añadir el mensaje del usuario a messages
        # TODO llamar a messages.create con el historial completo
        # TODO extraer el texto e imprimirlo
        # TODO añadir la respuesta del asistente a messages
        # TODO acumular usage.input_tokens / output_tokens

    console.print(
        f"\n[dim]Total — entrada: {tokens_entrada} | salida: {tokens_salida}[/dim]"
    )


if __name__ == "__main__":
    chat()

# Es el mismo bucle de 02_, solo que leyendo de stdin.
