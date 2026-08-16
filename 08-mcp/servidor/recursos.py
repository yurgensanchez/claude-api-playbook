"""Recursos MCP: datos de solo lectura que expone la APLICACIÓN, no el modelo."""

import json

from server import mcp

POLITICAS = {
    "devoluciones": (
        "30 días naturales desde la entrega, producto sin usar y en su embalaje "
        "original. Los descatalogados admiten devolución pero no cambio."
    ),
    "envios": (
        "Pedidos confirmados antes de las 14:00 salen el mismo día laborable. "
        "Plazo estándar 2-4 días hábiles en península."
    ),
    "garantia": "24 meses en todos los productos, 12 en consumibles.",
}


@mcp.resource("catalogo://politicas")
def listar_politicas() -> str:
    """Índice de las políticas comerciales disponibles."""
    return json.dumps(list(POLITICAS.keys()), ensure_ascii=False)


@mcp.resource("catalogo://politicas/{nombre}")
def leer_politica(nombre: str) -> str:
    """Texto completo de una política concreta.

    URI de ejemplo: catalogo://politicas/devoluciones
    """
    if nombre not in POLITICAS:
        raise ValueError(f"No existe la política '{nombre}'")
    return POLITICAS[nombre]


@mcp.resource("catalogo://inventario")
def inventario_completo() -> str:
    """Volcado completo del inventario en JSON."""
    from herramientas import INVENTARIO

    return json.dumps(INVENTARIO, ensure_ascii=False, indent=2)


# Cómo decido entre tool y resource:
#   RECURSO si solo lee, no tiene efectos secundarios y tiene sentido que la
#           aplicación lo cargue por su cuenta (config, política, esquema).
#   TOOL    si hace algo, o si el modelo tiene que decidir CUÁNDO usarla.
#
# El error típico es convertirlo todo en tool: un recurso no gasta una llamada
# ni depende de que el modelo se acuerde de pedirlo.
