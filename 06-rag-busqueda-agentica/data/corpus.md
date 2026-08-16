# Base de conocimiento de ejemplo

Corpus mínimo para probar el pipeline del módulo 06. Sustitúyelo por tu propia
documentación cuando quieras probar con algo real.

## Política de devoluciones

Se admiten devoluciones dentro de los 30 días naturales siguientes a la entrega,
siempre que el producto esté sin usar y en su embalaje original. Los productos
descatalogados admiten devolución pero no cambio por otra unidad.

El reembolso se emite en el mismo método de pago original y tarda entre 5 y 10
días hábiles en reflejarse.

## Errores de autenticación

El error ERR-4021 se produce cuando el token de sesión ha caducado. Los tokens
de autenticación expiran a los 30 minutos de inactividad.

Para renovar una sesión sin volver a introducir credenciales, se llama al
endpoint `/auth/refresh` con el refresh token vigente.

El error ERR-4030 indica que el token es válido pero la cuenta no tiene permisos
sobre el recurso solicitado. No se resuelve renovando el token.

## Catálogo y disponibilidad

El SKU MON-011 (monitor ultrawide de 34 pulgadas) está descatalogado desde marzo
y no se repondrá. Los monitores ultrawide de 34 pulgadas ya no se fabrican en
esta gama.

Cuando un producto figura con stock 0 pero sigue en catálogo, se puede reservar;
si está descatalogado, no.

## Envíos

Los pedidos confirmados antes de las 14:00 salen el mismo día laborable. El
plazo estándar es de 2 a 4 días hábiles en península.

Un pedido en estado `en_transito` durante más de 7 días hábiles se considera
incidencia y se escala automáticamente al transportista.
