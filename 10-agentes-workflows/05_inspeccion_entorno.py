"""Acceso de solo lectura al repo, con las comprobaciones que no me salto."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from anthropic import beta_tool

from shared import get_client
from shared.client import MODEL
from shared.utils import console

client = get_client()

RAIZ = Path(__file__).resolve().parent.parent
EXTENSIONES_PERMITIDAS = {".py", ".md", ".txt", ".json", ".toml"}


def _ruta_segura(ruta_relativa: str) -> Path:
    """El path viene del modelo: entrada no confiable."""
    destino = (RAIZ / ruta_relativa).resolve()
    if not destino.is_relative_to(RAIZ):
        raise ValueError(f"Ruta fuera del directorio permitido: {ruta_relativa}")
    return destino


@beta_tool
def listar(directorio: str = ".") -> str:
    """Lista los archivos y subdirectorios de una ruta del repositorio.

    Las rutas son relativas a la raíz del repo. Úsala para orientarte antes de
    leer archivos concretos.

    Args:
        directorio: Ruta relativa, p. ej. "05-tool-use" o "." para la raíz.
    """
    try:
        ruta = _ruta_segura(directorio)
    except ValueError as e:
        return f"Error: {e}"

    if not ruta.is_dir():
        return f"Error: {directorio} no es un directorio"

    entradas = sorted(
        f"{'[dir] ' if p.is_dir() else '      '}{p.name}"
        for p in ruta.iterdir()
        if not p.name.startswith(".")
    )
    return "\n".join(entradas) or "(vacío)"


@beta_tool
def leer(archivo: str, max_lineas: int = 100) -> str:
    """Lee el contenido de un archivo de texto del repositorio.

    Solo admite archivos de código y documentación (.py, .md, .txt, .json, .toml).
    Trunca a max_lineas para no llenar el contexto.

    Args:
        archivo: Ruta relativa al archivo
        max_lineas: Número máximo de líneas a devolver
    """
    try:
        ruta = _ruta_segura(archivo)
    except ValueError as e:
        return f"Error: {e}"

    if not ruta.is_file():
        return f"Error: no existe el archivo {archivo}"
    if ruta.suffix not in EXTENSIONES_PERMITIDAS:
        return f"Error: extensión no permitida ({ruta.suffix})"

    lineas = ruta.read_text(encoding="utf-8", errors="replace").splitlines()
    contenido = "\n".join(lineas[:max_lineas])
    if len(lineas) > max_lineas:
        contenido += f"\n... ({len(lineas) - max_lineas} líneas más)"
    return contenido


@beta_tool
def buscar(patron: str, extension: str = ".py") -> str:
    """Busca un texto literal en todos los archivos de una extensión.

    Devuelve las rutas y los números de línea donde aparece. Úsala cuando no
    sepas en qué archivo está lo que buscas.

    Args:
        patron: Texto literal a buscar (no es una expresión regular)
        extension: Extensión de archivo, p. ej. ".py"
    """
    coincidencias = []
    for ruta in RAIZ.rglob(f"*{extension}"):
        if ".venv" in ruta.parts or "__pycache__" in ruta.parts:
            continue
        try:
            for n, linea in enumerate(
                ruta.read_text(encoding="utf-8", errors="replace").splitlines(), 1
            ):
                if patron in linea:
                    coincidencias.append(f"{ruta.relative_to(RAIZ)}:{n}: {linea.strip()[:90]}")
        except OSError:
            continue
        if len(coincidencias) >= 30:
            break

    return "\n".join(coincidencias) or f"Sin coincidencias para '{patron}'"


SYSTEM = f"""
Eres un agente que analiza este repositorio de curso.

Trabajas en modo solo lectura: puedes listar, leer y buscar, pero no modificar
nada. Orientate primero con `listar` antes de leer archivos concretos.

Raíz del repositorio: {RAIZ.name}
"""


def main() -> None:
    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM,
        tools=[listar, leer, buscar],
        messages=[{
            "role": "user",
            "content": (
                "¿Qué módulos tiene este repositorio y en cuáles se usa "
                "`messages.parse`? Responde de forma concisa."
            ),
        }],
    )

    for mensaje in runner:
        for bloque in mensaje.content:
            if bloque.type == "text" and bloque.text.strip():
                console.print(f"[cyan]{bloque.text}[/cyan]")
            elif bloque.type == "tool_use":
                console.print(f"  [dim]-> {bloque.name}({bloque.input})[/dim]")


if __name__ == "__main__":
    main()

# Tres tools estrechas y de solo lectura, en vez de un bash genérico:
#   bash   máximo alcance, pero mi harness solo ve una cadena opaca y no puede
#          distinguir un grep inofensivo de un rm -rf
#   tools  menos alcance, pero cada acción es interceptable, auditable y
#          paralelizable, y puedo pedir confirmación por separado
# Empiezo por bash para tener alcance y promuevo a tool lo que necesite limitar.
#
# Lo que no me salto cuando un agente toca el disco:
#   1. resolver la ruta y verificar que no se sale del directorio permitido
#   2. lista blanca de extensiones o de comandos
#   3. truncar la salida para no reventar el contexto
