"""Tools MCP: funciones que el MODELO decide llamar.

El esquema sale de las anotaciones de tipo y el docstring, no escribo JSON Schema.
"""

from server import mcp

INVENTARIO = {
    "TCL-001": {"nombre": "Teclado mecánico 75%", "stock": 34, "precio": 89.90},
    "MON-010": {"nombre": 'Monitor 27" 1440p', "stock": 7, "precio": 329.00},
    "AUD-100": {"nombre": "Auriculares ANC", "stock": 18, "precio": 199.00},
}


@mcp.tool()
def consultar_stock(sku: str) -> dict:
    """Consulta el stock disponible de un producto por su SKU.

    Úsala cuando el usuario pregunte por disponibilidad o quiera saber si puede
    pedir una cantidad concreta. Devuelve nombre, stock y precio.
    Devuelve error si el SKU no existe.

    Args:
        sku: Identificador del producto, p. ej. TCL-001
    """
    if sku not in INVENTARIO:
        raise ValueError(f"SKU desconocido: {sku}")
    return {"sku": sku, **INVENTARIO[sku]}


@mcp.tool()
def reservar_unidades(sku: str, cantidad: int) -> dict:
    """Reserva unidades de un producto, descontándolas del stock.

    Úsala solo cuando el usuario confirme explícitamente que quiere reservar.
    Modifica el estado del inventario.

    Args:
        sku: Identificador del producto
        cantidad: Número de unidades a reservar (debe ser positivo)
    """
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser positiva")
    if sku not in INVENTARIO:
        raise ValueError(f"SKU desconocido: {sku}")

    disponible = INVENTARIO[sku]["stock"]
    if cantidad > disponible:
        raise ValueError(f"Solo hay {disponible} unidades de {sku}")

    INVENTARIO[sku]["stock"] -= cantidad
    return {"sku": sku, "reservadas": cantidad, "stock_restante": INVENTARIO[sku]["stock"]}


# El docstring ES la descripción que ve el modelo: qué hace, cuándo usarla,
# qué devuelve, cuándo falla.
# Las excepciones con mensaje útil se convierten en resultados de error que el
# modelo puede leer y corregir.
# reservar_unidades modifica estado: en un cliente serio iría tras confirmación.
