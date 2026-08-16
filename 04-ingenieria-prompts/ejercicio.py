"""EJERCICIO — mejorar un prompt malo aplicando las cuatro técnicas.

Lo que tengo que sacar:
  1. Partir del PROMPT_INICIAL (deliberadamente malo).
  2. Aplicar las técnicas una a una, guardando cada versión.
  3. Ejecutar las cuatro versiones sobre los mismos casos.
  4. Anotar qué cambió en cada paso.
  5. Engancharlo a la eval del módulo 03 para tener números.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client, print_block

client = get_client()

CASOS = [
    "Necesito cancelar mi suscripción pero no encuentro el botón. Llevo pagando "
    "8 meses y me habéis cobrado dos veces este mes.",

    "hola",

    "Vuestro producto es una estafa, quiero hablar con un responsable AHORA. "
    "Además el chat de soporte tampoco funciona.",
]

PROMPT_INICIAL = "Responde al cliente."

# TODO claro y directo
PROMPT_V2 = ""

# TODO específico: formato, tono, longitud, exclusiones
PROMPT_V3 = ""

# TODO etiquetas XML, separando datos de instrucciones
PROMPT_V4 = ""

# TODO 2-3 ejemplos variados
PROMPT_V5 = ""


VERSIONES = {
    "v1 — inicial": PROMPT_INICIAL,
    # "v2 — claro y directo": PROMPT_V2,
    # "v3 — específico": PROMPT_V3,
    # "v4 — XML": PROMPT_V4,
    # "v5 — few-shot": PROMPT_V5,
}


def main() -> None:
    for nombre, prompt in VERSIONES.items():
        if not prompt:
            continue
        for i, caso in enumerate(CASOS, start=1):
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": f"{prompt}\n\n{caso}"}],
            )
            print_block(f"{nombre} — caso {i}", extract_text(response))


if __name__ == "__main__":
    main()

# Preguntas para el análisis:
# - ¿En qué versión el caso 2 ("hola") deja de recibir respuesta genérica?
# - ¿En qué versión el caso 3 deja de escalar el tono en vez de calmarlo?
# - ¿Alguna técnica empeoró algo? Los ejemplos pueden estrechar demasiado la
#   salida si son poco variados.
