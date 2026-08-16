"""La API no guarda estado: el historial lo mantengo yo y lo reenvío entero."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client, print_block

client = get_client()

messages = []


def enviar(texto_usuario: str) -> str:
    messages.append({"role": "user", "content": texto_usuario})

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=messages,
    )

    respuesta = extract_text(response)
    messages.append({"role": "assistant", "content": respuesta})
    return respuesta


print_block("Turno 1", enviar("Me llamo Yurgen y trabajo con sistemas de IA."))
print_block("Turno 2", enviar("¿Cómo me llamo?"))
print_block("Turno 3", enviar("¿Y a qué me dedico?"))

print(f"\nMensajes acumulados en el historial: {len(messages)}")

# El primer mensaje tiene que ser "user".
# El coste de entrada crece con el historial -> caché y compactación (módulo 07).
