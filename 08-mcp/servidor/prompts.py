"""Prompts MCP: plantillas que invoca el USUARIO, no el modelo."""

from server import mcp


@mcp.prompt()
def revisar_disponibilidad(sku: str) -> str:
    """Genera un informe de disponibilidad de un producto."""
    return f"""
Consulta el stock del SKU {sku} y prepara un informe breve que incluya:

1. Disponibilidad actual y si permite pedidos grandes
2. Precio unitario
3. Recomendación: ¿conviene reservar ahora o esperar?

Si el SKU no existe, dilo directamente y no inventes datos.
"""


@mcp.prompt()
def responder_a_cliente(consulta: str, tono: str = "cercano") -> str:
    """Redacta una respuesta a un cliente aplicando las políticas vigentes."""
    return f"""
Un cliente escribe:

<consulta>
{consulta}
</consulta>

Consulta el recurso catalogo://politicas para saber qué aplica, y redacta la
respuesta en tono {tono}.

Requisitos:
- Cita la política concreta en la que te apoyas.
- Si la consulta cae fuera de las políticas, dilo y ofrece escalarlo.
- Máximo dos párrafos.
"""


# Un system prompt lo fijo yo y se aplica siempre; un prompt MCP lo invoca el
# usuario cuando lo necesita, con sus parámetros.
# Sirven para empaquetar flujos repetitivos: en vez de que cada persona
# reescriba el mismo encargo, vive en el servidor y se invoca por nombre.
