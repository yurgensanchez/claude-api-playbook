"""temperature (lo que enseña el curso) vs effort (lo que funciona hoy)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anthropic

from shared import MODEL, extract_text, get_client, print_block
from shared.client import MODEL_LEGACY

client = get_client()

PROMPT = "Dame un nombre para una cafetería de barrio. Solo el nombre."


# Ruta 1 — temperature, solo en modelos que aún lo aceptan.
print_block("Ruta 1 — temperature (modelo legacy)", f"modelo: {MODEL_LEGACY}", "yellow")

for temp in (0.0, 1.0):
    salidas = [
        extract_text(
            client.messages.create(
                model=MODEL_LEGACY,
                max_tokens=64,
                temperature=temp,
                messages=[{"role": "user", "content": PROMPT}],
            )
        ).strip()
        for _ in range(3)
    ]
    print(f"  temperature={temp}: {salidas}")


# Ruta 2 — el mismo parámetro en un modelo actual.
try:
    client.messages.create(
        model=MODEL,
        max_tokens=64,
        temperature=1.0,
        messages=[{"role": "user", "content": PROMPT}],
    )
except anthropic.BadRequestError as e:
    print_block("Ruta 2 — temperature en modelo actual", f"400: {e.message}", "red")


# Ruta 3 — effort. Va dentro de output_config, no top-level.
print_block("Ruta 3 — effort (modelo actual)", f"modelo: {MODEL}", "green")

for nivel in ("low", "high"):
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        output_config={"effort": nivel},
        messages=[
            {
                "role": "user",
                "content": "Diseña el esquema de una tabla de pedidos para un e-commerce.",
            }
        ],
    )
    print(f"  effort={nivel}: {len(extract_text(response))} caracteres, "
          f"{response.usage.output_tokens} tokens de salida")


# Ruta 4 — si lo que quería con temperature=1 era variedad, la pido.
response = client.messages.create(
    model=MODEL,
    max_tokens=512,
    messages=[
        {
            "role": "user",
            "content": (
                "Propón 4 nombres para una cafetería de barrio, cada uno con un "
                "registro distinto (clásico, moderno, local, juguetón). "
                "Una línea por nombre, sin explicaciones."
            ),
        }
    ],
)
print_block("Ruta 4 — variedad pedida en el prompt", extract_text(response), "green")

# Niveles de effort: low | medium | high | xhigh | max   (por defecto: high)
