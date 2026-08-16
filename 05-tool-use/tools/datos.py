"""Base de datos falsa en memoria."""

PRODUCTOS = [
    {"sku": "TCL-001", "nombre": "Teclado mecánico 75%", "categoria": "perifericos",
     "precio": 89.90, "stock": 34},
    {"sku": "TCL-002", "nombre": "Teclado inalámbrico compacto", "categoria": "perifericos",
     "precio": 45.00, "stock": 0},
    {"sku": "MON-010", "nombre": "Monitor 27\" 1440p 165Hz", "categoria": "monitores",
     "precio": 329.00, "stock": 7},
    {"sku": "MON-011", "nombre": "Monitor 34\" ultrawide", "categoria": "monitores",
     "precio": 549.00, "stock": 2},
    {"sku": "AUD-100", "nombre": "Auriculares con cancelación de ruido", "categoria": "audio",
     "precio": 199.00, "stock": 18},
    {"sku": "AUD-101", "nombre": "Micrófono USB cardioide", "categoria": "audio",
     "precio": 119.00, "stock": 5},
    {"sku": "SIL-200", "nombre": "Silla ergonómica con soporte lumbar", "categoria": "mobiliario",
     "precio": 429.00, "stock": 11},
]

PEDIDOS = [
    {"id": "PED-5501", "sku": "MON-010", "cantidad": 1, "estado": "entregado",
     "cliente": "ana@ejemplo.com"},
    {"id": "PED-5502", "sku": "TCL-001", "cantidad": 2, "estado": "en_transito",
     "cliente": "luis@ejemplo.com"},
    {"id": "PED-5503", "sku": "AUD-100", "cantidad": 1, "estado": "cancelado",
     "cliente": "ana@ejemplo.com"},
]
