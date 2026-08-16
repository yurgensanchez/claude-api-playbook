"""Troceado del corpus."""

from __future__ import annotations

import re


def chunk_por_secciones(texto: str, max_caracteres: int = 1200) -> list[dict]:
    """Corta por headers markdown y conserva el título como metadato.

    Si una sección se pasa de max_caracteres la parto por párrafos, para no
    acabar con un chunk gigante que se lleve todo el presupuesto del contexto.
    """
    partes = re.split(r"^(#{1,6} .+)$", texto, flags=re.MULTILINE)
    chunks: list[dict] = []
    titulo = "(sin título)"

    for parte in partes:
        parte = parte.strip()
        if not parte:
            continue

        if re.match(r"^#{1,6} ", parte):
            titulo = parte.lstrip("# ").strip()
            continue

        for trozo in _partir_si_largo(parte, max_caracteres):
            chunks.append({"titulo": titulo, "texto": trozo})

    return chunks


def _partir_si_largo(texto: str, maximo: int) -> list[str]:
    if len(texto) <= maximo:
        return [texto]

    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    trozos, actual = [], ""

    for parrafo in parrafos:
        if len(actual) + len(parrafo) > maximo and actual:
            trozos.append(actual.strip())
            actual = parrafo
        else:
            actual = f"{actual}\n\n{parrafo}" if actual else parrafo

    if actual:
        trozos.append(actual.strip())
    return trozos
