"""Cada dimensión que no fijo, la decide el modelo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client, print_block

client = get_client()

BASE = "Explica qué es el prompt caching."

VARIANTES = {
    "Sin especificar": BASE,

    "Audiencia fijada": (
        f"{BASE} La audiencia es un director financiero sin formación técnica "
        "que tiene que aprobar el presupuesto de infraestructura."
    ),

    "Formato fijado": (
        f"{BASE} Devuelve exactamente 4 bullets. Cada bullet empieza con un "
        "verbo en infinitivo y no supera las 20 palabras."
    ),

    "Todo fijado": (
        f"{BASE}\n\n"
        "Audiencia: un desarrollador backend que nunca ha usado la API de Claude.\n"
        "Formato: 3 párrafos cortos. El primero explica el qué, el segundo el "
        "cuándo conviene, el tercero el error más común.\n"
        "Excluye: precios concretos y comparativas con otros proveedores.\n"
        "Incluye: un ejemplo de una línea de código."
    ),
}

for titulo, prompt in VARIANTES.items():
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    print_block(titulo, extract_text(response))

# Dimensiones que merece la pena fijar: audiencia, formato, longitud,
# exclusiones y nivel de detalle asumido.
#
# Con la longitud, mejor cualitativa ("conciso") que numérica ("máx. 50
# palabras"): los topes numéricos ahogan el razonamiento en tareas difíciles.
# Y ojo, effort NO acorta de forma fiable el texto visible — eso se pide aquí.
