"""Helpers que acabo repitiendo en todos los ejercicios."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel

console = Console()


def extract_text(response: Any) -> str:
    """Concatena los bloques `text`.

    response.content[0].text se rompe en cuanto activo thinking o tools,
    así que filtro por tipo siempre.
    """
    return "".join(block.text for block in response.content if block.type == "text")


def extract_thinking(response: Any) -> str:
    return "\n".join(
        block.thinking for block in response.content if block.type == "thinking"
    )


def print_block(title: str, body: str, style: str = "cyan") -> None:
    console.print(Panel(body, title=title, border_style=style, expand=False))


def print_usage(response: Any) -> None:
    u = response.usage
    partes = [f"entrada: {u.input_tokens}", f"salida: {u.output_tokens}"]
    if getattr(u, "cache_creation_input_tokens", 0):
        partes.append(f"caché escrita: {u.cache_creation_input_tokens}")
    if getattr(u, "cache_read_input_tokens", 0):
        partes.append(f"caché leída: {u.cache_read_input_tokens}")
    console.print(f"[dim]tokens — {' | '.join(partes)}[/dim]")


def count_tokens(client: Any, model: str, messages: list, system: str | None = None) -> int:
    """Cuento con la API, no con tiktoken (ese es de OpenAI y da otras cifras)."""
    kwargs: dict[str, Any] = {"model": model, "messages": messages}
    if system:
        kwargs["system"] = system
    return client.messages.count_tokens(**kwargs).input_tokens
