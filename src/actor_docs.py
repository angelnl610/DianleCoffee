"""Documentación legible mediante GET del Key-Value Store privado de Apify."""
from config import LIMIT, MAX_BYTES

DOCUMENTATION = {
    "titulo": "Dianle Coffee",
    "descripcion": "Indicadores descriptivos de oferta y evaluación orientativa de precios de café.",
    "ejecucion": {"metodo": "POST", "ruta": "/v2/acts/{actorId}/runs", "formato": "application/json"},
    "documentacion": {"metodo": "GET",
                      "ruta": "/v2/key-value-stores/{defaultKeyValueStoreId}/records/DOCUMENTACION",
                      "formato": "application/json", "autenticacion": "Bearer del propietario autorizado"},
    "parametros": {
        "operation": "analytics o inference",
        "batch_id": "Identificador, 1 a 80 letras ASCII, números, guiones o guiones bajos",
        "origen": "Objeto con fuente del lote cuando se envía rows",
        "rows": "Registros con valores escalares",
        "fecha_referencia": "Fecha ISO opcional para evaluar antigüedad; por defecto, fecha UTC del run",
    },
    "operaciones": {
        "analytics": {
            "entrada": "Ofertas con fuente, fecha de observación, producto, comercio y precio de lista.",
            "adquisicion": "adquirir_sepa=true, sin rows: hasta 50 ofertas AMBA de 12 fragmentos.",
            "salidas": {"CAFE_CLEAN": "text/csv", "QUALITY": "application/json",
                        "ANALYTICS": "application/json", "CAFE_RAW": "text/csv (adquisición)",
                        "MANIFEST": "application/json (adquisición)"},
            "ejemplo": {"operation": "analytics", "batch_id": "consulta-sepa", "adquirir_sepa": True},
        },
        "inference": {
            "entrada": "formato, marca y canal cuando se conozcan, peso_g o cantidad_capsulas según formato.",
            "escenario": "precio_propuesto, costo_unitario_ars, unidades y costo_fijo_ars; margen_objetivo_pct opcional.",
            "salidas": {"INFERENCE": "application/json con referencia, evidencia, recomendaciones y escenario opcional"},
            "ejemplo": {"operation": "inference", "batch_id": "ejemplo-inference",
                        "origen": {"fuente": "Ejemplo de contrato"},
                        "rows": [{"formato": "molido", "peso_g": 250}]},
        },
    },
    "salidas_comunes": {"OUTPUT": "application/json con estado y claves", "DOCUMENTACION": "application/json"},
    "limites": {"filas": LIMIT, "bytes_input": MAX_BYTES, "memoria_inicial_mb": 512, "timeout_inicial_segundos": 120},
    "precio": "Sin precio comercial fijado. El costo real de Apify depende del plan y consumo. "
              "Registrar CU, memoria y tiempo antes de fijar precio.",
}
