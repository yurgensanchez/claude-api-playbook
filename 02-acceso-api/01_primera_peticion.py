"""Petición mínima a la Messages API."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client, print_block, print_usage

client = get_client()

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,  # obligatorio; es tope de SALIDA
    messages=[
        {"role": "user", "content": "Explica qué es una API en dos frases."}
    ],
)

# content es una lista de bloques, no una cadena.
print_block("Respuesta", extract_text(response))

print(f"modelo que respondió : {response.model}")
print(f"stop_reason          : {response.stop_reason}")
print_usage(response)

# stop_reason == "max_tokens" -> la respuesta quedó cortada.
