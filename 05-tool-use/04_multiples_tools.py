"""Cómo encadena y paraleliza herramientas, y cómo forzarlo con tool_choice.

Solo inspecciono el primer turno. El ciclo completo está en 03_.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, get_client
from shared.utils import console

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools import TODAS_LAS_TOOLS  # noqa: E402

client = get_client()


# Obliga a encadenar: primero buscar, luego calcular.
PREGUNTA_ENCADENADA = (
    "Quiero montar un puesto de trabajo: el monitor ultrawide y una silla "
    "ergonómica. ¿Cuánto sale en total con IVA?"
)

# Permite paralelizar: dos consultas independientes.
PREGUNTA_PARALELA = "¿Cómo van mis pedidos PED-5501 y PED-5503?"


def inspeccionar(pregunta: str) -> None:
    console.print(f"\n[bold green]Pregunta:[/bold green] {pregunta}")

    response = client.messages.create(
        model=MODEL, max_tokens=2048, tools=TODAS_LAS_TOOLS,
        messages=[{"role": "user", "content": pregunta}],
    )

    llamadas = [b for b in response.content if b.type == "tool_use"]
    console.print(f"  Herramientas pedidas en este turno: {len(llamadas)}")
    for b in llamadas:
        console.print(f"    - {b.name}: {b.input}")


inspeccionar(PREGUNTA_ENCADENADA)
inspeccionar(PREGUNTA_PARALELA)


console.print("\n[bold]tool_choice[/bold]")

OPCIONES = {
    '{"type": "auto"}': {"type": "auto"},
    '{"type": "any"}': {"type": "any"},
    '{"type": "tool", "name": ...}': {"type": "tool", "name": "buscar_productos"},
    '{"type": "none"}': {"type": "none"},
}

for etiqueta, opcion in OPCIONES.items():
    response = client.messages.create(
        model=MODEL, max_tokens=1024, tools=TODAS_LAS_TOOLS, tool_choice=opcion,
        messages=[{"role": "user", "content": "Hola, ¿qué tal?"}],
    )
    usadas = [b.name for b in response.content if b.type == "tool_use"]
    console.print(f"  {etiqueta:35} -> {usadas or 'ninguna'}")

# La paralelización viene activada. Para desactivarla:
#   tool_choice={"type": "auto", "disable_parallel_tool_use": True}
#
# Si pide N herramientas en un turno, los N tool_result van en UN solo mensaje.
