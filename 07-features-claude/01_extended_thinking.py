"""Thinking adaptativo, que es lo que sustituye a budget_tokens."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anthropic

from shared import MODEL, extract_text, get_client, print_block, print_usage
from shared.utils import extract_thinking

client = get_client()

PROBLEMA = (
    "Una empresa tiene 3 almacenes. El A cubre el 45% de los pedidos con un "
    "coste de 4,20€ por envío; el B, el 35% a 3,80€; el C, el resto a 5,10€. "
    "Si cerramos el C y repartimos su volumen entre A y B a partes iguales, "
    "¿cómo cambia el coste medio por envío?"
)


# Lo que enseña el curso.
try:
    client.messages.create(
        model=MODEL,
        max_tokens=8000,
        thinking={"type": "enabled", "budget_tokens": 4000},
        messages=[{"role": "user", "content": PROBLEMA}],
    )
except anthropic.BadRequestError as e:
    print_block("budget_tokens en modelo actual", f"400: {e.message}", "red")


# Lo que uso.
response = client.messages.create(
    model=MODEL,
    max_tokens=8000,
    thinking={"type": "adaptive", "display": "summarized"},
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": PROBLEMA}],
)

razonamiento = extract_thinking(response)
if razonamiento:
    print_block("Razonamiento (resumen)", razonamiento[:1200], "magenta")

print_block("Respuesta", extract_text(response), "green")
print_usage(response)


print("\nMismo problema a distintos niveles de effort:\n")
for nivel in ("low", "high"):
    r = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        output_config={"effort": nivel},
        messages=[{"role": "user", "content": PROBLEMA}],
    )
    print(f"  effort={nivel:5} -> {r.usage.output_tokens} tokens de salida")

# En Opus 5 el thinking está activo por defecto: omitir el parámetro no lo
# desactiva. Ojo con max_tokens, que es tope de thinking + texto juntos.
#
# display por defecto es "omitted": los bloques llegan con el texto vacío. Si
# muestro razonamiento en una UI, tengo que pedir "summarized".
# La cadena de pensamiento cruda nunca se devuelve, solo el resumen.
#
# En multi-turno con el mismo modelo, devolver los bloques thinking TAL CUAL:
# modificarlos rompe la firma y da 400.
