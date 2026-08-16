"""Esquemas de las herramientas. Es lo único que el modelo ve de ellas."""

BUSCAR_PRODUCTOS = {
    "name": "buscar_productos",
    "description": (
        "Busca productos en el catálogo por texto libre, categoría o rango de "
        "precio. Úsala cuando el usuario pregunte qué productos hay disponibles, "
        "pida recomendaciones o mencione una categoría. Devuelve como máximo 10 "
        "resultados con sku, nombre, precio y stock. No devuelve historial de "
        "pedidos: para eso usa consultar_pedido."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "consulta": {
                "type": "string",
                "description": "Texto de búsqueda libre, p. ej. 'teclado mecánico'",
            },
            "categoria": {
                "type": "string",
                "enum": ["perifericos", "monitores", "audio", "mobiliario"],
                "description": "Filtra por categoría exacta",
            },
            "precio_max": {
                "type": "number",
                "description": "Precio máximo en euros",
            },
            "solo_con_stock": {
                "type": "boolean",
                "description": "Si es true, excluye productos con stock 0",
            },
        },
        "required": ["consulta"],
    },
}

CONSULTAR_PEDIDO = {
    "name": "consultar_pedido",
    "description": (
        "Consulta el estado de un pedido por su identificador (formato PED-XXXX). "
        "Úsala cuando el usuario mencione un número de pedido o pregunte por el "
        "estado de un envío. Devuelve el estado, el producto y la cantidad. "
        "Devuelve error si el pedido no existe."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "pedido_id": {
                "type": "string",
                "description": "Identificador del pedido, p. ej. PED-5501",
            },
        },
        "required": ["pedido_id"],
    },
}

CALCULAR_TOTAL = {
    "name": "calcular_total",
    "description": (
        "Calcula el total de un carrito aplicando IVA del 21 % y el descuento "
        "por volumen que corresponda. Úsala siempre que haya que dar un precio "
        "final: no calcules los totales tú mismo, los descuentos cambian."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "lineas": {
                "type": "array",
                "description": "Líneas del carrito",
                "items": {
                    "type": "object",
                    "properties": {
                        "sku": {"type": "string"},
                        "cantidad": {"type": "integer"},
                    },
                    "required": ["sku", "cantidad"],
                },
            },
        },
        "required": ["lineas"],
    },
}

TODAS_LAS_TOOLS = [BUSCAR_PRODUCTOS, CONSULTAR_PEDIDO, CALCULAR_TOTAL]


# Una descripción es una página de manual: qué hace, CUÁNDO usarla (esto es lo
# que más sube la tasa de acierto), cuándo no, qué devuelve y cuándo falla.
# El fallo típico es quedarse corto: una línea vaga y parámetros sin description.
#
# Lo que NO va aquí: ejemplos de diálogo completos, instrucciones de
# conversación, ni "SIEMPRE usa esta herramienta" (provoca sobre-disparo).
#
# strict: True + additionalProperties: False garantiza que el input valide exacto.
