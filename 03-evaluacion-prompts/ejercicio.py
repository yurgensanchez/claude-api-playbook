"""EJERCICIO — eval completa comparando dos versiones de un prompt.

Lo que tengo que sacar:
  1. Tarea propia, distinta a la de las lecciones.
  2. Dataset de 15+ casos, con casos límite reales.
  3. Dos versiones del prompt: una ingenua (v1) y una trabajada (v2).
  4. Ambas ejecutadas sobre el dataset.
  5. Grading por código donde se pueda, por modelo donde no.
  6. Comparativa v1 vs v2 con números.

Terminado = puedo decir "v2 mejora v1 en X puntos en el criterio Y" con la
tabla que lo respalda.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.utils import console

# TODO mi tarea
TAREA = ""

# TODO las dos versiones
PROMPT_V1 = ""
PROMPT_V2 = ""


def main() -> None:
    # TODO generar/cargar dataset (reutilizar 01_)
    # TODO ejecutar ambas versiones (patrón async de 02_)
    # TODO graduar (03_ y 04_)
    # TODO imprimir comparativa
    console.print("Pendiente de implementar.")


if __name__ == "__main__":
    main()

# Si v2 gana en todo, sospechar: el dataset probablemente sea demasiado fácil.
# Un buen dataset tiene casos que fallan las dos versiones.
