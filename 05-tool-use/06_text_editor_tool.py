"""Herramienta definida por Anthropic: sin input_schema, pero la ejecuto yo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import MODEL, extract_text, get_client
from shared.utils import console

client = get_client()

SANDBOX = Path(__file__).parent / "sandbox"
SANDBOX.mkdir(exist_ok=True)

TEXT_EDITOR = {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}


def ruta_segura(path_str: str) -> Path:
    """El path viene del modelo: entrada no confiable.

    Sin esta comprobación, un ../../.env le da mi API key.
    """
    destino = (SANDBOX / Path(path_str).name).resolve()
    if not destino.is_relative_to(SANDBOX.resolve()):
        raise ValueError(f"Ruta fuera del sandbox: {path_str}")
    return destino


def ejecutar_editor(entrada: dict) -> tuple[str, bool]:
    comando = entrada["command"]

    try:
        ruta = ruta_segura(entrada["path"])

        if comando == "view":
            if not ruta.exists():
                return f"No existe: {ruta.name}", True
            contenido = ruta.read_text(encoding="utf-8")
            lineas = contenido.splitlines()
            if rango := entrada.get("view_range"):
                inicio, fin = rango
                lineas = lineas[inicio - 1 : (None if fin == -1 else fin)]
            return "\n".join(f"{i + 1}\t{l}" for i, l in enumerate(lineas)), False

        if comando == "create":
            ruta.write_text(entrada["file_text"], encoding="utf-8")
            return f"Creado {ruta.name}", False

        if comando == "str_replace":
            contenido = ruta.read_text(encoding="utf-8")
            viejo = entrada["old_str"]
            apariciones = contenido.count(viejo)
            if apariciones == 0:
                return "No se encontró old_str en el archivo", True
            if apariciones > 1:
                return f"old_str aparece {apariciones} veces; debe ser única", True
            ruta.write_text(contenido.replace(viejo, entrada["new_str"]), encoding="utf-8")
            return f"Reemplazo aplicado en {ruta.name}", False

        if comando == "insert":
            lineas = ruta.read_text(encoding="utf-8").splitlines(keepends=True)
            lineas.insert(entrada["insert_line"], entrada["insert_text"])
            ruta.write_text("".join(lineas), encoding="utf-8")
            return f"Insertado en línea {entrada['insert_line']}", False

        return f"Comando no soportado: {comando}", True

    except Exception as e:  # noqa: BLE001
        return f"Error: {e}", True


def main() -> None:
    messages = [{
        "role": "user",
        "content": (
            "Crea un archivo notas.md con tres puntos sobre tool use, y después "
            "cámbiale el título por 'Apuntes de tool use'."
        ),
    }]

    for _ in range(10):
        response = client.messages.create(
            model=MODEL, max_tokens=4096, tools=[TEXT_EDITOR], messages=messages
        )

        if response.stop_reason == "end_turn":
            console.print(f"\n[cyan]Claude:[/cyan] {extract_text(response)}")
            break

        messages.append({"role": "assistant", "content": response.content})

        resultados = []
        for bloque in response.content:
            if bloque.type != "tool_use":
                continue
            console.print(f"[dim]-> {bloque.input.get('command')} {bloque.input.get('path')}[/dim]")
            salida, es_error = ejecutar_editor(bloque.input)
            resultados.append({
                "type": "tool_result",
                "tool_use_id": bloque.id,
                "content": salida,
                "is_error": es_error,
            })

        messages.append({"role": "user", "content": resultados})

    console.print(f"\n[bold]Contenido del sandbox:[/bold] {SANDBOX}")
    for f in SANDBOX.iterdir():
        console.print(f"  {f.name} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

# type y name van emparejados: text_editor_20250728 exige
# str_replace_based_edit_tool. Mezclarlos con la versión antigua da 400.
# El comando undo_edit ya no existe en esta versión.
# str_replace debe encontrar exactamente una coincidencia; devolver 0 o >1 como
# error deja que el modelo reintente con más contexto.
