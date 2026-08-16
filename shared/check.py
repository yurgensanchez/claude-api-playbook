"""Comprobación de entorno:  python -m shared.check"""

from __future__ import annotations

import importlib

from shared.client import MAX_TOKENS, MODEL, MODEL_FAST, get_client
from shared.utils import console, extract_text

DEPENDENCIAS_POR_MODULO = {
    "03 — evals": ["pydantic"],
    "06 — RAG": ["voyageai", "rank_bm25", "numpy"],
    "07 — features": ["PIL", "pypdf"],
    "08 — MCP": ["mcp"],
}


def main() -> None:
    console.print(f"[bold]Modelo principal:[/bold] {MODEL}")
    console.print(f"[bold]Modelo rápido:[/bold]    {MODEL_FAST}")
    console.print(f"[bold]max_tokens:[/bold]       {MAX_TOKENS}\n")

    client = get_client()

    console.print("Probando una petición real...")
    response = client.messages.create(
        model=MODEL,
        max_tokens=64,
        messages=[{"role": "user", "content": "Responde solo con: OK"}],
    )
    console.print(f"[green]Respuesta:[/green] {extract_text(response).strip()}")
    console.print(f"[dim]Modelo que respondió: {response.model}[/dim]\n")

    console.print("[bold]Dependencias por módulo[/bold]")
    for modulo, paquetes in DEPENDENCIAS_POR_MODULO.items():
        faltantes = []
        for paquete in paquetes:
            try:
                importlib.import_module(paquete)
            except ImportError:
                faltantes.append(paquete)
        if faltantes:
            console.print(f"  [yellow]○[/yellow] {modulo} — falta: {', '.join(faltantes)}")
        else:
            console.print(f"  [green]●[/green] {modulo}")

    console.print("\n[green bold]Entorno listo.[/green bold]")


if __name__ == "__main__":
    main()
