# Diccionario de datos

| Campo | Procedencia o regla |
| --- | --- |
| id_oferta | Clave de observación. En SEPA derivado, EAN, ID de cadena y región. Se combina con fuente y fecha para deduplicar. |
| id_producto | Código observado, conservar como texto. En SEPA derivado es EAN. |
| nombre_original, marca | Identidad informada por origen. |
| nombre_normalizado, formato | Normalización de tildes y mayúsculas. Formato por término explícito en el nombre. |
| comercio, canal, fuente, region, granularidad | Identifican el comercio y alcance de observación. El derivador entrega agregados por cadena y región. |
| fecha_observacion, fecha_extraccion, url | Fecha del dato, día de adquisición y enlace de origen. |
| precio_lista_ars | Lista positiva en ARS. Para SEPA derivado es la mediana de sucursales de la cadena. |
| estado_promocion, condiciones_promocion | Presencia informada y condiciones disponibles. Campo vacío indica desconocido. |
| precio_promo_ars, descuento_pct | Precio promocional separado si consta y diferencia contra lista si corresponde. |
| precio_efectivo_ars | Lista salvo si existe promoción de alcance general verificado. |
| peso_g, cantidad_capsulas, cantidad_pack | Valores extraídos de la descripción. Peso total cuando el multipack por peso es interpretable. |
| tostado_torrado, descafeinado | Atributos extraídos solo ante mención explícita. |
| precio_unitario, unidad | Lista por kg para grano y molido, por 100 g para instantáneo, por cápsula para cápsulas. |
| grupo_producto | EAN para SEPA. Si falta, heurística de nombre, formato, marca y tamaño. |

Un lote externo autorizado debe adaptarse a los encabezados enumerados como FIELDS en src/etl.py y guardarse como `data/raw/cafe_raw.csv`. Precio y fecha deben conservar lo informado por la fuente. Completá el JSON adyacente `manifest.json` con `sha256` (minúsculas), `filas`, `fuente`, URLs, fechas, licencia y alcance verificables. Obtené el hash con `(Get-FileHash data/raw/cafe_raw.csv -Algorithm SHA256).Hash.ToLower()`. No incluyas secretos. El formato separado por coma debe estar en UTF-8.
