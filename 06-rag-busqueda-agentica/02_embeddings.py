"""Texto a vectores y similitud coseno.

Anthropic no tiene endpoint de embeddings; el curso usa Voyage AI.
Requiere VOYAGE_API_KEY en el .env.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from shared.client import ROOT  # noqa: F401  (carga el .env)
from shared.utils import console

MODELO_EMBEDDING = "voyage-3"

FRASES = [
    "El teclado mecánico tiene switches táctiles.",
    "Este keyboard usa interruptores mecánicos con feedback.",
    "El monitor tiene una tasa de refresco de 165 Hz.",
    "La receta lleva tres huevos y harina.",
]


def similitud_coseno(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main() -> None:
    if not os.getenv("VOYAGE_API_KEY"):
        console.print(
            "[yellow]Falta VOYAGE_API_KEY en el .env.[/yellow]\n"
            "Alternativa local sin API key:\n"
            "  pip install sentence-transformers\n"
            "  modelo = SentenceTransformer('all-MiniLM-L6-v2')\n"
            "  vectores = modelo.encode(FRASES)"
        )
        return

    import voyageai

    cliente = voyageai.Client()
    resultado = cliente.embed(FRASES, model=MODELO_EMBEDDING, input_type="document")
    vectores = [np.array(v) for v in resultado.embeddings]

    console.print(f"Modelo: {MODELO_EMBEDDING}")
    console.print(f"Dimensiones por vector: {len(vectores[0])}\n")

    console.print("[bold]Similitud coseno entre pares[/bold]")
    for i in range(len(FRASES)):
        for j in range(i + 1, len(FRASES)):
            sim = similitud_coseno(vectores[i], vectores[j])
            color = "green" if sim > 0.7 else "yellow" if sim > 0.4 else "dim"
            console.print(
                f"  [{color}]{sim:.3f}[/{color}]  "
                f"{FRASES[i][:35]:38} <-> {FRASES[j][:35]}"
            )


if __name__ == "__main__":
    main()

# Las frases 0 y 1 dicen lo mismo con palabras distintas y aun así puntúan alto.
# Eso es justo lo que la búsqueda por palabras clave no puede hacer.
#
# input_type importa: "document" al indexar, "query" al buscar. Voyage aplica
# prefijos internos distintos y mezclarlos empeora los resultados.
