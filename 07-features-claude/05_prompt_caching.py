"""Prompt caching. Las lecturas salen a ~0,1x del precio de entrada."""

import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, get_client
from shared.utils import console

client = get_client()

# Necesito superar el mínimo cacheable (512 tokens en Opus 5). Esto lo consigue.
CONTEXTO_GRANDE = (
    "Eres un analista del catálogo de productos de una tienda de informática. "
    "Conoces al detalle el inventario, los precios, los plazos de envío y la "
    "política de devoluciones. Respondes siempre citando datos concretos.\n\n"
) + "\n".join(
    f"- SKU PRD-{i:04d}: producto de ejemplo número {i}, precio {19 + i * 3}€, "
    f"stock {i % 40}, categoría {'perifericos' if i % 2 else 'monitores'}."
    for i in range(1, 200)
)


def consultar(pregunta: str, con_cache: bool) -> None:
    if con_cache:
        system = [{
            "type": "text",
            "text": CONTEXTO_GRANDE,
            "cache_control": {"type": "ephemeral"},
        }]
    else:
        system = CONTEXTO_GRANDE

    inicio = time.perf_counter()
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": pregunta}],
    )
    duracion = time.perf_counter() - inicio

    u = response.usage
    console.print(
        f"  entrada sin cachear: {u.input_tokens:>6} | "
        f"escrita: {getattr(u, 'cache_creation_input_tokens', 0):>6} | "
        f"leída: {getattr(u, 'cache_read_input_tokens', 0):>6} | "
        f"{duracion:.2f}s"
    )


console.print("[bold]Sin caché — dos peticiones idénticas[/bold]")
consultar("¿Cuántos productos hay en la categoría monitores?", con_cache=False)
consultar("¿Cuántos productos hay en la categoría monitores?", con_cache=False)

console.print("\n[bold]Con caché — la segunda debería leer de caché[/bold]")
consultar("¿Cuántos productos hay en la categoría monitores?", con_cache=True)
consultar("¿Y en periféricos?", con_cache=True)
consultar("¿Cuál es el más caro?", con_cache=True)


console.print("\n[bold red]Invalidador silencioso[/bold red]")
console.print("[dim]Un timestamp al principio del system prompt: cero lecturas[/dim]")

for _ in range(2):
    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        system=[{
            # El timestamp cambia en cada petición -> cambia el prefijo ->
            # se invalida todo lo que viene detrás.
            "type": "text",
            "text": f"Fecha actual: {datetime.now().isoformat()}\n\n{CONTEXTO_GRANDE}",
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": "¿Cuántos productos hay?"}],
    )
    console.print(
        f"  leída de caché: {getattr(response.usage, 'cache_read_input_tokens', 0)}"
    )

console.print(
    "\n[green]Solución:[/green] el contenido volátil va DESPUÉS del último "
    "breakpoint, nunca antes."
)

# Orden de render: tools -> system -> messages. Un breakpoint en el último
# bloque de system cachea tools + system juntos. Máximo 4 breakpoints.
#
# Prefijo mínimo: 512 tokens (Opus 5), 1024 (Opus 4.8 / Sonnet 5),
# 4096 (Opus 4.6 / Haiku 4.5). Por debajo no cachea y no avisa.
#
# Escritura 1,25x (TTL 5 min) o 2x (TTL 1 h); lectura 0,1x.
# Break-even: 2 peticiones con TTL 5 min, 3 con 1 h.
#
# Invalidadores a buscar en el código: datetime.now(), uuid4(), json.dumps() sin
# sort_keys, iterar un set, tools construidas por usuario, cambiar de modelo.
#
# Verificación: si cache_read_input_tokens es 0 en peticiones repetidas con el
# mismo prefijo, hay un invalidador. Diffear los bytes renderizados.
