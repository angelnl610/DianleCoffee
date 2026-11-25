# Apify · Actor de entrega

El SDK local se probó con las mismas entradas reales y salidas de referencia de Analytics e Inference. Los comandos de preparación, recursos del Actor, procedimiento privado de build, API y prueba de adquisición están en [Integración paso a paso](../INTEGRACION_PASO_A_PASO.md).

## Contrato de registros

| Operación | Entrada | Registros de salida |
| --- | --- | --- |
| Analytics | `rows` con observaciones y `origen.fuente` | `OUTPUT`, `CAFE_CLEAN`, `QUALITY`, `ANALYTICS` con oportunidades e insights |
| Analytics con adquisición | `adquirir_sepa: true`; lote acotado en AMBA | Los anteriores más `CAFE_RAW` y `MANIFEST` |
| Inference | `rows` con formato, marca, canal y tamaño según formato; precio propuesto y supuestos del escenario opcionales | `OUTPUT` e `INFERENCE`, con referencias, evidencia, recomendaciones y escenario opcional, o errores por fila |

`OUTPUT` detalla estado, operación, lote, conteos, claves y versión para Inference. El contrato admite 2.500 filas y 1 MB de JSON; la primera prueba usa como máximo 50 filas. El CSV crudo y las consultas quedan fuera del contexto de build. El artefacto de scikit-learn se genera en el equipo, se verifica por hash y versión, y se empaqueta en un directorio privado antes del build. Inference usa ese modelo y el SDK sin descargar modelos ni volver a entrenar.

## Ficha para revisión de Store

Dianle Coffee analiza precios observados de café envasado. Analytics devuelve observaciones limpias, cobertura, métricas por segmento y calidad. Inference devuelve una referencia de precio de lista para presentaciones con soporte y advierte ante diferencias débiles. El lote demostrado cubre supermercados de AMBA y una única fecha. El precio de servicio, costo real, capacidad efectiva y autorización para publicar quedan pendientes.

## GET de documentación

Luego de una corrida privada autorizada, `GET /v2/key-value-stores/<defaultKeyValueStoreId>/records/DOCUMENTACION` devuelve el documento JSON con descripción, operaciones, parámetros, ejemplos, formatos, precio y límites. El enlace también aparece en el esquema de salida del Actor. El registro se genera localmente con el SDK y se incluye en las salidas de control. La comprobación HTTP sobre Apify queda para la integración.
