"""Aquí el flujo lo decide el modelo, no mi código.

Comparar con 02_encadenamiento.py: la diferencia no es de código, es de quién decide.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from anthropic import beta_tool

from shared import get_client
from shared.client import MODEL
from shared.utils import console

client = get_client()

PROYECTOS = {
    "web": {"tests_pasan": False, "cobertura": 61, "lint_ok": True},
    "api": {"tests_pasan": True, "cobertura": 88, "lint_ok": False},
}


@beta_tool
def listar_proyectos() -> str:
    """Lista los proyectos disponibles en el repositorio.

    Úsala al principio si no sabes sobre qué proyecto trabajar.
    """
    return ", ".join(PROYECTOS)


@beta_tool
def estado_proyecto(proyecto: str) -> str:
    """Devuelve el estado de calidad de un proyecto.

    Incluye si los tests pasan, el porcentaje de cobertura y si el lint está
    limpio. Úsala antes de decidir qué hay que arreglar.

    Args:
        proyecto: Nombre del proyecto (usa listar_proyectos si no lo sabes).
    """
    if proyecto not in PROYECTOS:
        return f"Error: no existe el proyecto '{proyecto}'"
    return str(PROYECTOS[proyecto])


@beta_tool
def ejecutar_accion(proyecto: str, accion: str) -> str:
    """Ejecuta una acción de mantenimiento sobre un proyecto.

    Acciones válidas: "arreglar_tests", "subir_cobertura", "arreglar_lint".
    Modifica el estado del proyecto. Úsala solo cuando sepas qué está mal.

    Args:
        proyecto: Nombre del proyecto
        accion: Una de las tres acciones válidas
    """
    if proyecto not in PROYECTOS:
        return f"Error: no existe el proyecto '{proyecto}'"

    estado = PROYECTOS[proyecto]
    if accion == "arreglar_tests":
        estado["tests_pasan"] = True
    elif accion == "subir_cobertura":
        estado["cobertura"] = min(100, estado["cobertura"] + 20)
    elif accion == "arreglar_lint":
        estado["lint_ok"] = True
    else:
        return f"Error: acción desconocida '{accion}'"

    return f"Hecho. Estado ahora: {estado}"


SYSTEM = """
Eres un agente de mantenimiento de repositorios.

El listón de calidad es: tests pasando, cobertura >= 80 % y lint limpio.

Inspecciona el estado antes de actuar y verifica después de cada acción.
Cuando todos los proyectos cumplan el listón, resume qué hiciste y termina.
"""


def main() -> None:
    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM,
        tools=[listar_proyectos, estado_proyecto, ejecutar_accion],
        messages=[{
            "role": "user",
            "content": "Pon todos los proyectos del repo al día según el listón de calidad.",
        }],
    )

    for mensaje in runner:
        for bloque in mensaje.content:
            if bloque.type == "text" and bloque.text.strip():
                console.print(f"[cyan]{bloque.text}[/cyan]")
            elif bloque.type == "tool_use":
                console.print(f"  [dim]-> {bloque.name}({bloque.input})[/dim]")

    console.print(f"\n[bold]Estado final:[/bold] {PROYECTOS}")


if __name__ == "__main__":
    main()

# Nadie le dijo "primero lista, luego consulta, luego arregla": ese plan lo saca
# de las descripciones de las tools y del listón del system prompt. Por eso el
# orden puede variar entre ejecuciones.
#
# El tool runner ejecuta el bucle pero me deja intervenir en cada turno: aprobar
# o denegar antes de que se ejecute, inspeccionar el resultado, modificarlo o
# cortar. "Necesito control" casi nunca obliga al bucle manual.
#
# Para acciones destructivas, la puerta de aprobación va DENTRO de la función:
# devolver "el usuario ha denegado" en vez de ejecutar.
