"""EJERCICIO — escribir un system prompt y comprobar que se respeta.

Lo que tengo que sacar:
  1. Un asistente especializado (elijo yo el dominio).
  2. System prompt con rol, formato de salida y una restricción real.
  3. Los tres casos de abajo pasando.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client, print_block

client = get_client()

# TODO mi system prompt
SYSTEM = """
Eres ...
"""

# TODO casos que pongan a prueba las restricciones
CASOS = [
    "Un caso normal, dentro del dominio del asistente.",
    "Un caso ambiguo, donde debería pedir aclaración en vez de inventar.",
    "Un caso fuera de dominio, donde debería negarse educadamente.",
]

for i, caso in enumerate(CASOS, start=1):
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": caso}],
    )
    print_block(f"Caso {i}: {caso[:50]}", extract_text(response))

# Si falla, casi nunca es cosa de añadir mayúsculas: suele ser que la
# instrucción es ambigua o que le falta el porqué.
