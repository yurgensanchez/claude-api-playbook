"""Grading determinista. Lo que se pueda verificar con código, va aquí."""

import json
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.utils import console

DATA = Path(__file__).parent / "data"

PRIORIDADES_VALIDAS = {"baja", "media", "alta"}


def es_json_valido(salida: str) -> bool:
    try:
        json.loads(salida.strip())
        return True
    except json.JSONDecodeError:
        return False


def tiene_claves_requeridas(salida: str) -> bool:
    try:
        datos = json.loads(salida.strip())
    except json.JSONDecodeError:
        return False
    return {"categoria", "prioridad", "escalar"} <= datos.keys()


def prioridad_en_enum(salida: str) -> bool:
    try:
        datos = json.loads(salida.strip())
    except json.JSONDecodeError:
        return False
    return datos.get("prioridad") in PRIORIDADES_VALIDAS


def escalar_es_booleano(salida: str) -> bool:
    try:
        datos = json.loads(salida.strip())
    except json.JSONDecodeError:
        return False
    return isinstance(datos.get("escalar"), bool)


def sin_texto_extra(salida: str) -> bool:
    limpia = salida.strip()
    return limpia.startswith("{") and limpia.endswith("}")


CHECKS: dict[str, Callable[[str], bool]] = {
    "json_valido": es_json_valido,
    "claves_requeridas": tiene_claves_requeridas,
    "prioridad_valida": prioridad_en_enum,
    "escalar_booleano": escalar_es_booleano,
    "sin_texto_extra": sin_texto_extra,
}


def main() -> None:
    datos = json.loads((DATA / "salidas_v1.json").read_text(encoding="utf-8"))
    resultados = datos["resultados"]

    conteo = {nombre: 0 for nombre in CHECKS}
    fallos_por_caso = []

    for caso in resultados:
        fallos = [n for n, check in CHECKS.items() if not check(caso["salida"])]
        for nombre in CHECKS:
            if nombre not in fallos:
                conteo[nombre] += 1
        if fallos:
            fallos_por_caso.append((caso["id"], fallos))

    total = len(resultados)
    console.print(f"\n[bold]Grading por código — {total} casos[/bold]\n")
    for nombre, ok in conteo.items():
        pct = 100 * ok / total
        color = "green" if pct == 100 else "yellow" if pct >= 80 else "red"
        console.print(f"  [{color}]{ok:>3}/{total}[/{color}]  {nombre}  ({pct:.0f}%)")

    if fallos_por_caso:
        console.print("\n[bold]Casos con fallos[/bold]")
        for caso_id, fallos in fallos_por_caso:
            console.print(f"  {caso_id}: {', '.join(fallos)}")


if __name__ == "__main__":
    main()

# Casi todos estos checks desaparecen si uso output_config.format: el schema ya
# garantiza el JSON, las claves y el enum. Antes de escribir un validador, mirar
# si la API puede garantizarlo por mí.
# Los checks siguen valiendo para lo que el schema no cubre: relaciones entre
# campos y coherencia con el input.
