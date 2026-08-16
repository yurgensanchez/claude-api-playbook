"""Citas verificables: la API me devuelve la localización exacta del texto."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, get_client
from shared.utils import console

client = get_client()

DOCUMENTO = """
Política de reembolsos, revisión 2026-01.

Se admiten devoluciones dentro de los 30 días naturales siguientes a la entrega,
siempre que el producto esté sin usar y en su embalaje original.

Los productos descatalogados admiten devolución pero no cambio por otra unidad.

El reembolso se emite en el mismo método de pago original y tarda entre 5 y 10
días hábiles en reflejarse.

Los gastos de envío de la devolución corren a cargo del cliente salvo que el
producto llegara defectuoso.
"""

response = client.messages.create(
    model=MODEL,
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {
                    "type": "text",
                    "media_type": "text/plain",
                    "data": DOCUMENTO,
                },
                "title": "Política de reembolsos",
                "citations": {"enabled": True},
            },
            {
                "type": "text",
                "text": "¿Quién paga el envío de una devolución, y en cuánto tiempo llega el dinero?",
            },
        ],
    }],
)

# Con citations la respuesta se parte en varios bloques text; los que se apoyan
# en el documento llevan un array `citations`.
for bloque in response.content:
    if bloque.type != "text":
        continue

    console.print(bloque.text, end="")

    if getattr(bloque, "citations", None):
        for cita in bloque.citations:
            console.print(
                f"\n  [dim]└─ cita: \"{cita.cited_text.strip()[:80]}...\" "
                f"(caracteres {cita.start_char_index}-{cita.end_char_index})[/dim]"
            )

print()

# citations va en CADA bloque document: o en todos o en ninguno.
# Localización según el tipo: char_location (texto), page_location (PDF, base 1),
# content_block_location (custom).
#
# INCOMPATIBLE con output_config.format: da 400. Si necesito JSON con citas,
# extraigo las citas del objeto de respuesta y monto el JSON yo.
#
# La ventaja sobre pedir citas en el prompt: aquí no puede inventárselas, los
# índices apuntan al documento real.
