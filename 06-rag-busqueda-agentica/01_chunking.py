"""Tres estrategias de chunking sobre el mismo documento."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.utils import console

DATA = Path(__file__).parent / "data"


def chunk_tamano_fijo(texto: str, tamano: int = 500, solape: int = 50) -> list[str]:
    """Corta cada N caracteres. Simple, pero parte frases por la mitad."""
    chunks = []
    inicio = 0
    while inicio < len(texto):
        chunks.append(texto[inicio : inicio + tamano])
        inicio += tamano - solape
    return chunks


def chunk_por_parrafos(texto: str, max_caracteres: int = 800) -> list[str]:
    """Agrupa párrafos completos sin pasar del límite."""
    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    chunks, actual = [], ""

    for parrafo in parrafos:
        if len(actual) + len(parrafo) > max_caracteres and actual:
            chunks.append(actual.strip())
            actual = parrafo
        else:
            actual = f"{actual}\n\n{parrafo}" if actual else parrafo

    if actual:
        chunks.append(actual.strip())
    return chunks


def chunk_por_secciones(texto: str) -> list[dict]:
    """Corta por headers y conserva el título como metadato.

    El metadato es lo importante: me deja mostrar de qué sección viene cada
    fragmento y que el modelo lo cite.
    """
    partes = re.split(r"^(#{1,3} .+)$", texto, flags=re.MULTILINE)
    chunks = []
    titulo_actual = "(sin título)"

    for parte in partes:
        parte = parte.strip()
        if not parte:
            continue
        if re.match(r"^#{1,3} ", parte):
            titulo_actual = parte.lstrip("# ").strip()
        else:
            chunks.append({"titulo": titulo_actual, "texto": parte})

    return chunks


def main() -> None:
    archivo = DATA / "corpus.md"
    if not archivo.exists():
        console.print(f"[yellow]Falta {archivo}.[/yellow]")
        return

    texto = archivo.read_text(encoding="utf-8")
    console.print(f"Documento: {len(texto)} caracteres\n")

    for nombre, chunks in [
        ("Tamaño fijo (500/50)", chunk_tamano_fijo(texto)),
        ("Por párrafos (máx. 800)", chunk_por_parrafos(texto)),
    ]:
        longitudes = [len(c) for c in chunks]
        console.print(f"[bold]{nombre}[/bold]: {len(chunks)} chunks, "
                      f"media {sum(longitudes) // len(longitudes)} car.")
        console.print(f"  [dim]primero: {chunks[0][:100]}...[/dim]\n")

    secciones = chunk_por_secciones(texto)
    console.print(f"[bold]Por secciones[/bold]: {len(secciones)} chunks")
    for s in secciones[:3]:
        console.print(f"  [{s['titulo']}] {s['texto'][:80]}...")


if __name__ == "__main__":
    main()

# Cómo elijo:
#   documentación estructurada -> por secciones
#   prosa continua             -> por párrafos con límite
#   transcripciones, logs      -> tamaño fijo con solape generoso
#
# El solape existe para que una idea que cae justo en el corte siga entera en
# al menos un chunk.
