"""El system prompt va en su parámetro, no como primer mensaje de usuario."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client, print_block

client = get_client()

PREGUNTA = "¿Qué es la recursión?"

SIN_SYSTEM = None

CON_SYSTEM = (
    "Eres un instructor de programación para principiantes absolutos. "
    "Explicas con una analogía cotidiana antes de tocar código. "
    "Nunca superas los tres párrafos y no usas jerga sin definirla."
)


def preguntar(system: str | None) -> str:
    kwargs = {
        "model": MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": PREGUNTA}],
    }
    if system:
        kwargs["system"] = system
    return extract_text(client.messages.create(**kwargs))


print_block("Sin system prompt", preguntar(SIN_SYSTEM), style="yellow")
print_block("Con system prompt", preguntar(CON_SYSTEM), style="green")

# Aquí pongo rol, formato y restricciones reales — con su porqué.
# No pongo virtudes genéricas ("sé preciso") ni mayúsculas tipo "CRITICAL:":
# eso ya es comportamiento por defecto y encima provoca sobre-disparo.
#
# Para cachearlo (módulo 07) hay que pasarlo como lista de bloques:
#   system=[{"type": "text", "text": CON_SYSTEM,
#            "cache_control": {"type": "ephemeral"}}]
