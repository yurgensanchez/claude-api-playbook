"""Las funciones que se ejecutan. Código normal: no saben nada de la API."""

from __future__ import annotations

from typing import Any

from .datos import PEDIDOS, PRODUCTOS

IVA = 0.21
DESCUENTOS_POR_VOLUMEN = [(10, 0.15), (5, 0.10), (3, 0.05)]


def buscar_productos(
    consulta: str,
    categoria: str | None = None,
    precio_max: float | None = None,
    solo_con_stock: bool = False,
) -> list[dict[str, Any]]:
    terminos = consulta.lower().split()
    resultados = []

    for p in PRODUCTOS:
        texto = f"{p['nombre']} {p['categoria']} {p['sku']}".lower()
        if not any(t in texto for t in terminos):
            continue
        if categoria and p["categoria"] != categoria:
            continue
        if precio_max is not None and p["precio"] > precio_max:
            continue
        if solo_con_stock and p["stock"] == 0:
            continue
        resultados.append(p)

    return resultados[:10]


def consultar_pedido(pedido_id: str) -> dict[str, Any]:
    for pedido in PEDIDOS:
        if pedido["id"].upper() == pedido_id.upper():
            producto = next(
                (p for p in PRODUCTOS if p["sku"] == pedido["sku"]), None
            )
            return {**pedido, "producto": producto["nombre"] if producto else None}
    raise ValueError(f"No existe el pedido {pedido_id}")


def calcular_total(lineas: list[dict[str, Any]]) -> dict[str, Any]:
    subtotal = 0.0
    unidades = 0
    detalle = []

    for linea in lineas:
        producto = next((p for p in PRODUCTOS if p["sku"] == linea["sku"]), None)
        if producto is None:
            raise ValueError(f"SKU desconocido: {linea['sku']}")
        importe = producto["precio"] * linea["cantidad"]
        subtotal += importe
        unidades += linea["cantidad"]
        detalle.append(
            {"sku": producto["sku"], "cantidad": linea["cantidad"], "importe": round(importe, 2)}
        )

    descuento_pct = next(
        (pct for minimo, pct in DESCUENTOS_POR_VOLUMEN if unidades >= minimo), 0.0
    )
    descuento = subtotal * descuento_pct
    base = subtotal - descuento

    return {
        "detalle": detalle,
        "subtotal": round(subtotal, 2),
        "descuento_pct": descuento_pct,
        "descuento": round(descuento, 2),
        "iva": round(base * IVA, 2),
        "total": round(base * (1 + IVA), 2),
    }


REGISTRO = {
    "buscar_productos": buscar_productos,
    "consultar_pedido": consultar_pedido,
    "calcular_total": calcular_total,
}


def ejecutar_tool(nombre: str, argumentos: dict[str, Any]) -> tuple[Any, bool]:
    """Devuelve (resultado, es_error).

    Un fallo no se propaga como excepción: se convierte en tool_result con
    is_error=True para que el modelo pueda corregir por su cuenta.
    """
    funcion = REGISTRO.get(nombre)
    if funcion is None:
        return f"Herramienta desconocida: {nombre}", True

    try:
        return funcion(**argumentos), False
    except Exception as e:  # noqa: BLE001
        return f"Error al ejecutar {nombre}: {e}", True
